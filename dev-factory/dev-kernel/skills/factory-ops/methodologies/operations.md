# Operations — Running the Runtime, Arming the Loop, Tending the Substrate

`Cell: methodology.system.factory-ops · Status: defined · Register: established (event-sourced ops, single-writer discipline, bounded-loop arming); the dev-native binding to dev-server's heartbeat/store is house synthesis`

The dev-server is the operational tier (TDD §9): the process that polls, holds leases, serves a socket, supervises worker subprocesses, and pushes live views. It is **not a plugin** — it is a separately-distributed Python app that drives a `dev-kernel` substrate via `--dir`/env. The same kernel can also be driven by a CI trigger or by a human running one cell by hand; the server is just the heartbeat that automates it. This methodology is how you run it, arm its bounded loop, and tend the substrate under it — all deterministically.

## The harness surfaces you operate

Engineering the factory means mapping each system function onto a concrete harness surface, not an abstract box (`harness-and-storage.md`). The surfaces this skill touches:

| Function | Surface | Operated how |
| --- | --- | --- |
| substrate artifacts, worktrees, ledger, signals | filesystem + git | provision/teardown worktrees; the ledger is append-only (gate-ledger denies mutation) |
| deterministic computation (scan, rank, staleness, lease reconcile, reports) | bash / code execution | the heartbeat, `reconcile_leases`, `store.rebuild` — never inference |
| operational status + queryable history + CRUD + reports | database (SQLite, + DuckDB read-only for reports) | the single-writer server writes it; agents read it via MCP, never write |
| gates and feedback | hooks (PreToolUse deny on protected paths) | wired per-dispatch into the worker's worktree, never bundled |

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

## The two planes and the single-writer write path

The corpus splits into two planes with one typing rule: **artifact bodies → files; tensed status and queryable history → database** (`harness-and-storage.md`). You operate against four write-path invariants — never break them:

1. **Single-writer.** Operational-state writes happen in exactly one process (the server). No agent, worker, or UI writes the database or the lattice directly. The heartbeat calls the **same** `api.transition_ticket` a human drag does — the loop is the scheduler calling the API, not a separate code path.
2. **The DB is never ahead of the ledger.** Every operational write is preceded by a ledger append (`api.transition_ticket` ledgers *inside* `lifecycle.transition`, then writes the file-of-record, then re-materializes the index — in that order).
3. **Artifact bodies write on the filesystem, through a gated worker.** The DB row referencing the artifact is updated by the server *after* the gated write succeeds. The dispatcher records the authored asset on the cell with `seed_cell` (workers cannot write `lattice.json`).
4. **Reconstructible.** The operational store is rebuildable from ledger + filesystem at any time; losing it is a rebuild, not a loss (the crash-recovery runbook).

A UI drag is a transition **request**, not a direct write — the gate runs server-side (`gate-ticket-ready` / `gate-dispatch` / `gate-signal` via `lifecycle.transition`) and an illegal one is refused with a reason, never silently applied.

## Arming the bounded heartbeat

The 30s outer loop (`heartbeat.py`) is the dark factory's pulse, and it is **bounded by construction** — the I-9 arming discipline, dev-native over dev's ledger. One tick is deterministic end to end (`on_tick`):

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

An exhausted window **halts dispatch rather than burning through it** — the loop surfaces the ceiling. The budget file lives under the worker-protected `run/` perimeter, so a worker cannot lift its own ceiling. Whatever the orchestrator believes its counter says, the gate is the floor; `heartbeat.py selftest` proves both the fail-closed-when-unarmed path and the halt-past-deadline path with no model agent.

## Worktree lifecycle

`dispatch.provision_worktree(d, cell_id, worker_id)` provisions a **hermetic workspace** for one unit: a real `git worktree add --detach … HEAD` when the instance lives in a repo (so parallel workers on different cells never collide), a plain isolated dir as fallback. The worktree path is `run/worktrees/{cell-id}--{worker-id}`. `dispatch.teardown_worktree` removes it (`git worktree remove --force` + `rmtree`) on completion **and** on a worker failure — worktree GC is the dispatcher's, deterministic, never an agent's. Gates are wired **per dispatch, never bundled**: `dispatch.wire_gates` writes a `.claude/settings.json` into the worktree that runs the dev-kernel gates (`gate-verifier` / `gate-ledger` / `gate-naming`) as PreToolUse(Write|Edit) hooks, so a worker that tries to forge a signal or rewrite the lattice/ledger is denied **in-process** — the §9.2 "gates active inside the worktree" guarantee. The merge rule: **never co-dispatch two tickets targeting the same cell**; independent cells merge freely in isolated worktrees (TDD §15, OD-004).

## Graceful pause and stop

- **Pause** — `POST /api/control/pause` (and the `PAUSED` flag) is the human kill-switch: a paused tick returns immediately, reconciling and dispatching nothing. `/resume` clears it. Pausing freezes the loop; in-flight worker leases are recovered by reconciliation on resume if they expired.
- **Stop a run** — clear the window (`heartbeat.clear` removes `run/heartbeat.json`); the next tick is unarmed and fails closed. Re-arm to start a fresh bounded session.
- **Demote a family** — `POST /api/control/demote/{family}` drops its autonomy tier; demotion is mechanical and ledger-driven (REQ-SAFE-004) — the human investigates via the incident-responder *after* the demotion already happened.

## Operations Failure Modes

Running the loop **unarmed and assuming it dispatched** (it fails closed by design — read the `halted` reason). Claiming the loop is bounded **without an armed window** (arm first; an unarmed loop is not "running safely," it is not running). **Editing the index directly** or treating the DB as authoritative (it is a projection — mutate through the single-writer API, rebuild on corruption). **Hand-repairing a corrupted index** instead of `store.rebuild` (a DROP + replay is the property; manual surgery breaks the never-ahead-of-the-ledger invariant). **Co-dispatching two tickets on the same cell** (a scheduling failure dressed as a model failure — the dispatcher serializes per cell). **A worker writing operational state** (the single-writer discipline exists precisely to design out the claim race; a worker reads via MCP and never writes the DB, the lattice, the ledger, or its own budget).
