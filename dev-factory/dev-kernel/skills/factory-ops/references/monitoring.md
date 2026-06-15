# Monitoring — What to Watch and What It Means

`Cell: methodology.system.monitoring · Status: defined · Register: established (flow metrics, trust-trajectory inputs, event-sourced reporting); the dev-native metric set is house synthesis`

The UI is a *window onto substrate*, not a separate database: every card and every grid cell is a rendering of a git-tracked file, and every metric below is a **derived view** over the operational store and the ledger — SQL/DuckDB over the SQLite index + the JSONL ledger, never a second source of truth (`harness-and-storage.md`, TDD §9). This is the dev-native equivalent of harness-forge's `/harness-status` dashboard: the handful of signals that tell you whether the factory is healthy, stuck, or quietly reward-hacking. Reports are read-only by construction — DuckDB attaches the SQLite store and the ledger and runs columnar SQL with no ETL.

## The metrics to watch

| Metric | Source | Healthy | Watch for |
| --- | --- | --- | --- |
| **Maturity distribution** | the lattice grid (`store.grid` / `/api/lattice`) — cells by maturity | a thin vertical slice climbing `absent → … → validated`, depth-first | a wide band of `defined` with nothing `validated` (grid-filling — everything specified, nothing real, §17) |
| **Frontier** | `compass.scan` over the grid — the open/stale gap set at the frontier scope | a short, dependency-ready frontier the loop is draining | a frontier blocked on an unvalidated dependency (the partial order is unmet) or a growing stale set |
| **Run-budget X/Y + alarm** | `heartbeat.load_budget` + the ledger (`dispatches_since`, `tokens_since`) | dispatches and tokens well under the armed ceiling; a live deadline ahead | approaching `max_dispatches`/`token_ceiling`, or **no window at all** (unarmed → fail-closed; the loop is *not running*, not "running safely") |
| **Gate-fires** | the ledger — `block`/denied-transition events; PreToolUse denies in the worker stream | rare, expected denials (an illegal drag, a worker probing a protected path) | a *spike* of gate-fires (a worker repeatedly trying to write `signals/`/the ledger — a reward-hack attempt) or zero fires on a wired gate that should have caught something |
| **False-pass rate** | the ledger — independent-check disagreements with the critic | `< ~5%` and trending down (the Tier-2 precondition) | any upward move — it **mechanically demotes** the family and flips its verifier cells `stale` (REQ-SAFE-004); read it from the ledger, never trust the green board |

## How to read them together

- **Maturity + frontier** answer *"is the factory making real progress?"* Real progress is a slice reaching `validated` with a critic-written signal on disk — not cells turning green at `defined`. A grid that fills breadth-first is the enterprise-architecture pathology; depth-first to `validated` along one thin slice, then widen, is the trajectory rule.
- **Run-budget** answers *"is the loop bounded right now?"* The honest answer is `X/Y` against an armed window. **If there is no window, the loop fails closed and dispatches nothing** — that is the design, not an outage; arm a fresh window to run. A loop reported as "bounded" without an armed window is mis-stated.
- **Gate-fires** answer *"is the immutable boundary holding?"* The gates are wired into each worker's worktree per dispatch (`dispatch.wire_gates`), so a worker that tries to forge a signal or rewrite the lattice/ledger is denied in-process — and that denial is a ledgered fire. Expected denials are healthy; a *spike* is an adversarial worker worth an exploit scan.
- **False-pass** answers *"has this family actually earned its autonomy?"* It is the one metric the artifact cannot self-report: autonomy is earned by a measured track record read from the ledger, never granted by an "autonomy already earned" claim. A clean scoreboard is exactly what a reward-hack produces — so the false-pass rate, not the board's color, gates promotion, and a spike *mechanically* demotes.

## The autonomy tiers these metrics gate

The loop's `tier_allows(t)` check (TDD §14.2) reads the ledger-measured track record. The metrics above are its inputs:

| Tier | Unattended dispatch | Precondition (from the ledger) |
| --- | --- | --- |
| 0 Attended | nothing unattended | default for a new family |
| 1 Gated | dispatch; human reviews at `in-review` | verifier validated; false-pass trending down |
| 2 Unattended-in-budget | full `active → done` within budget | false-pass `< ~5%`; zero reward-hack incidents; caps active |
| 3 Scheduled/long-running | the heartbeat runs the family lights-out | Tier 2 sustained across a window; hermetic sandbox; tamper-evident audit trail |

The watch discipline that falls out: **a structurally elegant factory that cannot evidence its tier from the ledger has not earned it.** Demotion is mechanical and needs no human in the path; promotion needs a measured window. Reports surface the evidence; they never grant the tier.

## Monitoring Failure Modes

**Reading the green board as health** (a clean scoreboard is what a hack produces — the false-pass rate is the real signal). **Reporting the loop as bounded with no armed window** (unarmed is fail-closed, not safe-running). **Treating a `defined`-heavy grid as progress** (grid-filling; real progress is `validated` with a signal on disk). **Building a second source of truth for metrics** (every metric is a derived view over the operational store + the ledger — never authored, never authoritative). **Ignoring a gate-fire spike** (the expected case is rare denials; a spike is a worker probing the immutable boundary and warrants an exploit scan of its passing runs).
