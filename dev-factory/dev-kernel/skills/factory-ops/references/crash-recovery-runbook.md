# Crash & Recovery Runbook

`Cell: methodology.system.crash-recovery · Status: defined · Register: established (lease expiry, idempotent re-dispatch, event-sourcing replay); the dev-native binding to dev-server is house synthesis`

Long-running autonomy needs explicit crash semantics, not hope (TDD §15). This is that table as a runbook: the failure, how it is **detected** (always a mechanism, never a guess), and the **recovery** — code you invoke, not surgery you perform. The spine under all of it is event sourcing: **the append-only ledger is the source of truth for every state transition; current state is a materialized view of the ledger**, so the operational store is rebuildable by replay.

## The failure → recovery table

| Failure | Detection | Recovery |
| --- | --- | --- |
| **Worker crash / hang** | the lease heartbeat stops (`lease_expiry` passes) | `reconcile_leases()` next tick expires the lease; ticket → `active` (retry, `attempts++`) or `blocked` if attempts exhausted; the worktree is GC'd |
| **Server crash mid-tick** | restart | **idempotent dispatch** (REQ-LOOP-006) — existing leases/worktrees are adopted, not duplicated; the SQLite index is rebuilt from files; the ledger is replayed for in-memory state |
| **Budget exhaustion** | counters vs. caps (`budget_exhausted`, from the ledger) | ticket → `blocked` with a reason; the cell is **not** advanced; surfaced to the compass and the UI |
| **No-progress (same failure signature ×N)** | attempt diff | ticket → `blocked`; flagged for triage/regeneration |
| **Reward-hack / false-pass** | an exploit scan or an independent check disagreeing with the critic | the incident is logged; the **family is auto-demoted** (§14.2, mechanical); its verifier cells flip `stale` |
| **Upstream cell changed** | `propagate-staleness` (a hook, deterministic) | every dependent flips to `stale`; tickets targeting them are gated until re-validated |
| **Merge collision (parallel worktrees)** | an integration check | a *scheduling* failure, not a model failure — the dispatcher serializes merges to one cell; concurrent tickets on the **same** cell are never co-dispatched |
| **Corrupted index** | a read anomaly / a failed selftest | `store.rebuild(d)` — a DROP + replay; **a corrupted index is a rebuild, not a loss** (below) |

## Worker crash → lease reconciliation

A dispatched worker holds a **lease** (`claim.lease_expiry`, default `LEASE_TTL_S = 900s`). If the worker crashes, hangs, or its host dies, the lease simply stops being renewed and passes its expiry. Detection is the passing timestamp; recovery is `dispatch.reconcile_leases(d)`, which the heartbeat runs **every tick** (`on_tick` calls it before anything else):

- It walks `claimed`/`in-progress` tickets, reads each `claim.lease_expiry`, and for any that is past `now`, clears the claim and transitions the ticket back to `active` — **a retry, with `attempts++`** — ledgering "lease expired (…); worker presumed dead — returned to active".
- It is **idempotent**: a ticket already reconciled is skipped (its state is no longer `claimed`/`in-progress`). Running it twice is a no-op.

This is the single-writer principle doing safety work: a dead worker is recovered by **lease expiry**, not by reconciling competing claims, because no two workers ever claimed the same ticket (the server is the only writer of `claimed`; the classic distributed-claim race is designed out, not mitigated — §7.2).

## Server crash mid-tick → idempotent re-dispatch + rebuild

A server that dies in the middle of a tick is recovered by restart, leaning on two properties:

1. **Idempotent dispatch (REQ-LOOP-006).** Re-dispatching a ticket whose worktree/lease already exists is a no-op, so a restart mid-tick cannot double-launch. Existing leases and worktrees are **adopted, not duplicated**; reconciliation then expires any whose worker actually died.
2. **Rebuild on boot.** The SQLite index is rebuilt from the files; the ledger is replayed for in-memory state. The DB is downstream of the ledger, so nothing authoritative is lost in the crash — only the *projection*, which is reconstructed.

The operating posture: after an unclean shutdown, **boot, let `store.rebuild` re-materialize, let the first tick reconcile leases.** Do not hand-repair tickets or rows; the machinery converges the state.

## Budget exhaustion → blocked (surface, never burn)

When a window's counters meet its caps, `budget_exhausted` returns `(True, reason)` and `on_tick` halts — it **surfaces the ceiling, it does not burn through it** (Failure 4, the canonical token-burn incident). A ticket that cannot finish within budget goes to `blocked` with a reason; the cell is **not** advanced; both are surfaced to the compass and the UI. Recovery is a deliberate human act: extend the window by **re-arming** (`heartbeat.py arm` writes a fresh absolute deadline — you do not edit the counter) or `unblock` the ticket once its dependency is ready. The budget file is under the worker-protected `run/` perimeter, so a worker can neither lift its own ceiling nor unblock itself.

## No-progress → blocked

A cell whose last N attempts all failed with the **same failure signature** is detected by an attempt diff, not by the worker's self-assessment. The ticket goes to `blocked` and is flagged for triage or regeneration — the loop stops throwing iterations at a stuck cell. A blocked cell drops out of `rank`, so the compass routes work elsewhere while a human (or the regeneration loop) decides whether the spec, the rubric, or the approach was wrong.

## Reward-hack / false-pass → mechanical demotion

The canonical reward-hack is a clean scoreboard a worker produced by editing its own verifier — which is **designed out**: workers are mechanically deny-on-write to the immutable side (`rubric/`, `signals/`, `ledger/`, the hooks, `naming.schema.json`, the kernel schemas), enforced by the gates wired into the worktree (`dispatch.wire_gates`). When an exploit scan or an independent check *disagrees with the critic* on a passing run, the incident is logged and the **family is auto-demoted a tier with no human in the demotion path** (REQ-SAFE-004); its verifier cells flip `stale`. The human investigates via `incident-responder` *after* the demotion already happened. Autonomy is earned by a measured false-pass rate read from the ledger, never granted by the artifact's own claim.

## The rebuild-by-replay property — "a corrupted index is a DROP and a replay"

This is the load-bearing recovery property and the reason the database is never the source of truth. The operational store (`.agents/dev-factory/index.db`) is a **materialized projection** of the ledger + the on-disk files — *derived, never authoritative* (`harness-and-storage.md`, OD-001). So when it is corrupted, deleted, or simply stale:

```bash
python3 store.py rebuild --dir /path/to/.agents/dev-factory
```

`store.rebuild(d)` is a **DROP + replay**: it `DELETE`s every projected table, replays the ledger (the source of truth for history) into the `ledger` table and the `activities` fold, re-scans `coordination/tickets/*.json` (files are the source of truth for entity bodies), and re-projects the canonical `lattice.json` cells into the grid. The `store.py selftest` proves the property directly — it nukes `index.db`, rebuilds from ledger + files, and asserts the view is identical. **A corrupted index is not a disaster; it is a `DROP` and a replay.** Never hand-edit rows to "fix" the index: a manual write makes the DB disagree with the ledger and breaks the never-ahead-of-the-ledger invariant. The correct repair is always to rebuild from the authoritative substrate.

## Recovery Failure Modes

**Hand-repairing the index** instead of `store.rebuild` (breaks the never-ahead-of-the-ledger invariant; the projection must be derived, not authored). **Reconciling competing claims** that cannot exist (the single-writer server means a dead worker is a lease expiry, not a claim race). **Editing a counter to extend a budget** instead of re-arming a fresh window (the deadline is absolute; a mid-flight counter edit is the kind of un-audited state the design forbids). **Unblocking a ticket without resolving why it blocked** (no-progress and budget blocks have a cause; clearing the flag without the fix just re-burns the budget). **Trusting a passing run because the board is green** (a clean scoreboard is exactly what a reward-hack produces — the false-pass rate, read from the ledger, is the real signal).
