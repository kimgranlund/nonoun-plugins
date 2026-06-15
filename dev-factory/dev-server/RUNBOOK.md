# dev-server — operations runbook

How to run the dev-factory runtime, arm its bounded loop, watch its health, and recover from a crash. This is the **operational seat** — what is *running*, not what is *known* (that grid is the kernel's `lattice-management` skill). It ships **with the runtime it documents** (the same line drawn for the system-evals in `evals/`): the heartbeat, lease reconciliation, worktree GC, and rebuild-by-replay are this server's code (`heartbeat.py` · `dispatch.py` · `store.py`), so the runbook that drives them lives here, not in the invariant kernel.

> **The one law — computation routes to code, never to inference.** The heartbeat poll, lease reconciliation, worktree GC, the compass scan/rank, and the rebuild-by-replay are deterministic dev-server code (TDD §10.4 lists them as explicitly NOT agents) — a model-predicted computation is a hallucination surface. Your role operating the factory is to *read the metrics, decide what to do, and invoke the right code* — never to count budgets, reconcile leases, or rebuild an index by reasoning. The single-writer server is the only process that writes operational state; a worker, an agent, or a UI never writes the database or the lattice directly.

## The two planes and the single writer

dev-factory is two planes (kernel ref `harness-and-storage.md`): **artifact bodies on the filesystem + git** (the substrate plane the outer loop rewrites and diffs) and **tensed status + queryable history in a database** (the operational plane — ticket lifecycle state, cell maturity, leases, metrics, the grid, all a *materialized projection* of the ledger).

| Plane | Holds | Authority | Operated by |
| --- | --- | --- | --- |
| **Substrate** (files + git) | spec/rubric/policy/pattern **content**, signal files, cell artifacts, worktrees, the ledger | files-of-record, git-versioned; the ledger is the source of truth for every transition | worktree lifecycle, ledger append (under gates) |
| **Operational** (SQLite `index.db`, + DuckDB read-only for reports) | ticket lifecycle **state**, cell maturity **status**, leases, timestamps, metrics, the grid | a **materialized projection** — derived, rebuildable by ledger replay | the single-writer server (`store.py`, `api.py`) |

Four write-path invariants — never break them:

1. **Single-writer.** Operational-state writes happen in exactly one process (the server). No agent, worker, or UI writes the database or the lattice directly. The heartbeat calls the **same** `api.transition_ticket` a human drag does — the loop is the scheduler calling the API, not a separate code path.
2. **The DB is never ahead of the ledger.** Every operational write is preceded by a ledger append (`api.transition_ticket` ledgers *inside* `lifecycle.transition`, then writes the file-of-record, then re-materializes the index — in that order).
3. **Artifact bodies write on the filesystem, through a gated worker.** The DB row referencing the artifact is updated by the server *after* the gated write succeeds; the dispatcher records the authored asset with `seed_cell` (workers cannot write `lattice.json`).
4. **Reconstructible.** The operational store is rebuildable from ledger + filesystem at any time; losing it is a `rebuild`, not a loss. A UI drag is a transition **request**, not a direct write — the gate runs server-side and an illegal one is refused with a reason, never silently applied.

## Boot

The coordination core (`store.py`, `api.py`) is stdlib + `sqlite3` — zero runtime deps, CI-tested. FastAPI/uvicorn are only the HTTP transport.

```bash
# 1. headless verification of the whole coordination path — no deps, run this first
python3 store.py selftest && python3 api.py selftest

# 2. the live server (Crawl: heartbeat OFF; Walk: scheduler enabled)
pip install fastapi uvicorn
DEV_FACTORY_DIR=/path/to/project/.agents/dev-factory uvicorn app:app --port 8731

# point the server at a different kernel checkout
DEV_KERNEL_BIN=/path/to/dev-kernel/bin uvicorn app:app
```

On boot the server calls `api.init_instance(d)` — it scaffolds the substrate tree (the nine layer dirs + `signals/` + `ledger/` via the vendored `lattice.scaffold`), writes an empty canonical `lattice.json` if absent, and lays the `coordination/{tickets,roadmap,issues}/` dirs. It is **idempotent**: re-booting against an existing instance re-scaffolds nothing and re-materializes the index from the ledger + files. The env contract is one variable — the instance dir (`DEV_FACTORY_DIR`) — and one optional override (`DEV_KERNEL_BIN`, the vendored kernel `bin/`).

## The bounded heartbeat — arm before you run (it fails closed)

The 30s outer loop (`heartbeat.py`) is the dark factory's pulse, **bounded by construction** — the same discipline harness-forge's I-9 run budget enforces, here dev-native over dev's ledger. One tick is deterministic end to end:

```
on_tick():
  if PAUSED: return {halted, "paused (human kill-switch)"}
  reconcile_leases()                 # expire dead workers (dispatch.py)
  if budget_exhausted(): return      # SURFACE the ceiling — never burn through it
  slots = max_concurrency - count_running()
  for t in compass.next_batch(tier, slots):   # ready + ranked (compass.py)
      dispatch_unit(t)                          # provision, claim, run, validate (dispatch.py)
  emit_metrics()
```

**Arm before you run.** A window must exist before the loop dispatches:

```bash
heartbeat.py arm --dir DIR --deadline-s 3600 --max-dispatches 20 --token-ceiling 2000000
```

`heartbeat.arm` writes `run/heartbeat.json` with `start_ts`, an absolute `deadline_ts` (not a counter), `max_dispatches`, and `token_ceiling`. Then **`budget_exhausted` is the gate**, computed from code + the ledger, never an agent's counting:

- **Unarmed → `(True, "loop not armed — arm the heartbeat window before dispatching (fail-closed)")`.** An unarmed `on_tick` halts and dispatches nothing. This is the arming discipline: you cannot skip the preamble into a silent unbounded run.
- **Wall-clock** — halts when `now ≥ deadline_ts`. The deadline is absolute, so you *re-arm a fresh window* to extend a run; you never edit a counter mid-flight.
- **Max-dispatches** — halts when `dispatches_since(start_ts) ≥ max_dispatches` (counted from the ledger's `dispatch` events).
- **Token ceiling** — halts when `tokens_since(start_ts) ≥ token_ceiling` (summed from ledger `metrics.tokens`).

An exhausted window **halts dispatch rather than burning through it** — the loop surfaces the ceiling (Failure 4, the canonical token-burn incident). The budget file lives under the worker-protected `run/` perimeter, so a worker cannot lift its own ceiling. `heartbeat.py selftest` proves both the fail-closed-when-unarmed path and the halt-past-deadline path with no model agent.

> Operating rule: **never `tick`/`run` before `arm`.** An unarmed `on_tick` returns `{halted: True, reason: "loop not armed…"}` and dispatches nothing — that is the design, not a bug.

## Worktree lifecycle

`dispatch.provision_worktree(d, cell_id, worker_id)` provisions a **hermetic workspace** for one unit: a real `git worktree add --detach … HEAD` when the instance lives in a repo (so parallel workers on different cells never collide), a plain isolated dir as fallback. The path is `run/worktrees/{cell-id}--{worker-id}`. `dispatch.teardown_worktree` removes it (`git worktree remove --force` + `rmtree`) on completion **and** on a worker failure — worktree GC is the dispatcher's, deterministic, never an agent's. Gates are wired **per dispatch, never bundled**: `dispatch.wire_gates` writes a `.claude/settings.json` into the worktree that runs the dev-kernel gates (`gate-verifier` / `gate-ledger` / `gate-naming`) as PreToolUse(Write|Edit) hooks, so a worker that tries to forge a signal or rewrite the lattice/ledger is denied **in-process**. The merge rule: **never co-dispatch two tickets targeting the same cell**; independent cells merge freely in isolated worktrees (TDD §15, OD-004).

## Graceful pause and stop

- **Pause** — `POST /api/control/pause` (and the `PAUSED` flag) is the human kill-switch: a paused tick returns immediately, reconciling and dispatching nothing. `/resume` clears it; in-flight leases are recovered by reconciliation on resume if they expired.
- **Stop a run** — clear the window (`heartbeat.clear` removes `run/heartbeat.json`); the next tick is unarmed and fails closed. Re-arm to start a fresh bounded session.
- **Demote a family** — `POST /api/control/demote/{family}` drops its autonomy tier; demotion is mechanical and ledger-driven (REQ-SAFE-004) — the human investigates via the `incident-responder` *after* the demotion already happened.

## Health you watch

Every metric is a **derived view** over the operational store + the ledger — SQL/DuckDB over the SQLite index + the JSONL ledger, never a second source of truth. This is the dev-native equivalent of harness-forge's `/harness-status` dashboard.

| Metric | Source | Healthy | Watch for |
| --- | --- | --- | --- |
| **Maturity distribution** | the lattice grid (`store.grid` / `/api/lattice`) | a thin vertical slice climbing `absent → … → validated`, depth-first | a wide band of `defined` with nothing `validated` (grid-filling — everything specified, nothing real, §17) |
| **Frontier** | `compass.scan` over the grid | a short, dependency-ready frontier the loop is draining | a frontier blocked on an unvalidated dependency, or a growing stale set |
| **Run-budget X/Y + alarm** | `heartbeat.load_budget` + the ledger | dispatches and tokens well under the armed ceiling; a live deadline ahead | approaching `max_dispatches`/`token_ceiling`, or **no window at all** (unarmed → fail-closed; the loop is *not running*, not "running safely") |
| **Gate-fires** | the ledger — `block`/denied-transition events; PreToolUse denies | rare, expected denials | a *spike* (a worker repeatedly trying to write `signals/`/the ledger — a reward-hack attempt), or zero fires on a wired gate that should have caught something |
| **False-pass rate** | the ledger — independent-check disagreements with the critic | `< ~5%` and trending down (the Tier-2 precondition) | any upward move — it **mechanically demotes** the family and flips its verifier cells `stale` (REQ-SAFE-004); read it from the ledger, never trust the green board |

The discipline: **a structurally elegant factory that cannot evidence its tier from the ledger has not earned it.** A clean scoreboard is exactly what a reward-hack produces — so the false-pass rate, not the board's color, gates promotion. The autonomy tiers these inputs gate (TDD §14.2): **0 Attended** (default), **1 Gated** (dispatch; human reviews at `in-review`; verifier validated + false-pass trending down), **2 Unattended-in-budget** (false-pass `< ~5%`, zero reward-hack incidents, caps active), **3 Scheduled** (Tier 2 sustained across a window, hermetic sandbox, tamper-evident audit trail).

## Crash & recovery

Long-running autonomy needs explicit crash semantics, not hope (TDD §15). The spine under all of it is event sourcing: **the append-only ledger is the source of truth for every transition; current state is a materialized view**, so the operational store is rebuildable by replay.

| Failure | Detection | Recovery |
| --- | --- | --- |
| **Worker crash / hang** | the lease heartbeat stops (`lease_expiry` passes) | `reconcile_leases()` next tick expires the lease; ticket → `active` (retry, `attempts++`) or `blocked` if attempts exhausted; the worktree is GC'd |
| **Server crash mid-tick** | restart | **idempotent dispatch** (REQ-LOOP-006) — existing leases/worktrees are adopted, not duplicated; the SQLite index is rebuilt from files; the ledger is replayed for in-memory state |
| **Budget exhaustion** | counters vs. caps (`budget_exhausted`, from the ledger) | ticket → `blocked` with a reason; the cell is **not** advanced; surfaced to the compass and the UI |
| **No-progress (same failure signature ×N)** | attempt diff | ticket → `blocked`; flagged for triage/regeneration; a blocked cell drops out of `rank` |
| **Reward-hack / false-pass** | an exploit scan or an independent check disagreeing with the critic | the incident is logged; the **family is auto-demoted** (§14.2, mechanical); its verifier cells flip `stale` |
| **Upstream cell changed** | `propagate-staleness` (deterministic) | every dependent flips to `stale`; tickets targeting them are gated until re-validated |
| **Merge collision (parallel worktrees)** | an integration check | a *scheduling* failure, not a model failure — the dispatcher serializes merges to one cell; concurrent tickets on the **same** cell are never co-dispatched |
| **Corrupted index** | a read anomaly / a failed selftest | `store.rebuild(d)` — a DROP + replay; **a corrupted index is a rebuild, not a loss** (below) |

**Worker crash → lease reconciliation.** A dispatched worker holds a **lease** (`claim.lease_expiry`, default `LEASE_TTL_S = 900s`). If it crashes or hangs, the lease stops being renewed and passes its expiry; `dispatch.reconcile_leases(d)` (run every tick) clears the claim and returns the ticket to `active` with `attempts++`. It is **idempotent** — a ticket already reconciled is skipped. A dead worker is recovered by **lease expiry**, not by reconciling competing claims, because the single-writer server is the only writer of `claimed` — the classic distributed-claim race is designed out, not mitigated.

**Server crash mid-tick → idempotent re-dispatch + rebuild.** A restart adopts existing leases/worktrees (idempotent dispatch, REQ-LOOP-006) so it cannot double-launch; reconciliation then expires any whose worker actually died, and `store.rebuild` re-materializes the index from the ledger + files. Posture: **boot, let `store.rebuild` re-materialize, let the first tick reconcile.** Do not hand-repair tickets or rows; the machinery converges.

**The rebuild-by-replay property — "a corrupted index is a DROP and a replay."** The operational store (`.agents/dev-factory/index.db`) is a **materialized projection** of the ledger + on-disk files — derived, never authoritative (OD-001). When it is corrupted, deleted, or stale:

```bash
python3 store.py rebuild --dir /path/to/.agents/dev-factory
```

`store.rebuild(d)` is a **DROP + replay**: it deletes every projected table, replays the ledger into the `ledger` table and the `activities` fold, re-scans `coordination/tickets/*.json`, and re-projects the canonical `lattice.json` cells into the grid. `store.py selftest` proves the property directly — it nukes `index.db`, rebuilds, and asserts the view is identical. **Never hand-edit rows to "fix" the index**: a manual write makes the DB disagree with the ledger and breaks the never-ahead-of-the-ledger invariant. The correct repair is always to rebuild from the authoritative substrate.

## Operations failure modes

Running the loop **unarmed and assuming it dispatched** (it fails closed — read the `halted` reason). Claiming the loop is bounded **without an armed window** (arm first; an unarmed loop is not "running safely," it is not running). **Editing the index directly** or treating the DB as authoritative (it is a projection — mutate through the single-writer API, rebuild on corruption). **Hand-repairing a corrupted index** instead of `store.rebuild`. **Co-dispatching two tickets on the same cell** (a scheduling failure dressed as a model failure). **A worker writing operational state** (the single-writer discipline designs out the claim race; a worker reads via MCP and never writes the DB, the lattice, the ledger, or its own budget). **Reading the green board as health** (the false-pass rate, read from the ledger, is the real signal — a clean scoreboard is what a hack produces).
