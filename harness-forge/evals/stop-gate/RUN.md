# Stop-gate — the wired circuit breaker halts a runaway loop (v0.4 behavioral evidence)

`/harness-run` is the autonomous loop, so its safety is the whole point: a cell stuck repeating a failure must be **halted mechanically**, not by the worker (or the orchestrator) remembering to stop. `check.py` (CI) replays that mechanic with only the public machinery — no model agent — so the circuit breaker is *proven*, not asserted.

## What it proves

```
seed + wire a project → a capability cell (parse.py) with budget{no_progress_n: 3}
control (before):  the cell IS rankable · gate-budget ALLOWS a write to its asset
→ validate.py runs a real FAILING verifier 3× (each ledgers a fail)
→ ledger.py no-progress  DETECTS the stuck cell (exit 1)              ← the detector, in code (CV4)
→ lattice.py block       flips it (the orchestrator's protected write)
after:  the cell is OUT of rank · the wired gate-budget DENIES the next write (exit 2)
        · advance-validity refuses it · the loop has no ready cell → it halts
```

The before/after is the directionality control: the same cell that was rankable-and-writable becomes unrankable-and-denied the moment it's blocked. The enforcement is two independent mechanisms — the selector (`rank` drops it) **and** the worker's own gate (`gate-budget` denies the write from its installed location) — so neither the orchestrator's loop logic nor the worker's restraint is the single point the safety rests on.

## The division of labor (the v0.4 wired stop-gate)

| Piece | Role | Where |
| --- | --- | --- |
| `ledger.py no-progress` | **detect** — a cell whose last N validates all failed (a pass resets the run) | code (CV4, 0.3.1) |
| `harness-builder` | **decide + block** — between passes, block detected cells; honor the hard caps; stop and report | the orchestrator (`/harness-run`) |
| `lattice.py block` · `rank` | **drop** — a blocked cell leaves the ready set | kernel |
| `gate-budget` (wired) | **enforce** — deny a Write/Edit to a blocked cell's asset, even a runaway worker | PreToolUse hook |

Autonomy stays **earned, not declared**: the loop is bounded (max-cells · max-iterations · wall-clock), attended (reports at every stop, never silently re-enters), and never raises its own caps or unblocks automatically. A blocked cell is a signal to *change the approach*, then `lattice.py unblock` deliberately.

## Replay

```bash
python3 harness-forge/evals/stop-gate/check.py   # CI runs this; exit 0 = the stop-gate halts the loop
```
