# Global bound — the loop's caps are code, not the orchestrator's prose (v0.4.1 behavioral evidence)

The v0.4.0 council's **convergent Critical** (Andrej · Simon · Chip · David, independently): `/harness-run` was advertised "bounded by construction," but only the *per-cell* stop was wired in code — the **global** caps (max-cells · max-iterations · wall-clock) were prose the orchestrator *agent* "ticked" in its own context. A model counting and comparing to terminate an unattended loop is a computation routed to inference: the routing law violated at the point of maximum blast radius. Chip noted the eval that would prove the global bound "cannot be written — there is no code artifact to assert against."

0.4.1 builds the artifact. `check.py` (CI) proves it.

## The mechanism (`run-budget.py` + `gate-budget`)

```
run-budget.py start --max-iterations N --max-cells M --wall-clock-s S
   → persists .harness/run/budget.json {start_ts, deadline_ts, max_iterations, max_cells}

gate-budget (wired, PreToolUse Write|Edit), on every worker write, denies (exit 2) if the run is exhausted:
   • now ≥ deadline_ts                      ← wall-clock: an absolute deadline, enforced with NO counter
   • count(validate events since start) ≥ max_iterations   ← the LEDGER is the counter, not the agent
   • count(cells validated since start)  ≥ max_cells
```

Nothing is decremented by the orchestrator. The kernel (`lattice.run_budget_exhausted`) computes the verdict from the deadline and the ledger; the wired gate enforces it. The loop **physically cannot write past its budget**, whatever the orchestrator believes its counter says.

## What `check.py` proves (no model agent)

| Assertion | Shows |
| --- | --- |
| under-budget write allowed | the control — the gate isn't just denying everything |
| past-deadline → **every** write denied (exit 2) | wall-clock is a hard, counter-free ceiling |
| the deny covers an *unrelated* path (`src/main.py`) | it's the **global** stop, not the per-cell one |
| 2 ledgered validates vs cap 2 → denied | max-iterations counted from the ledger, not an agent |
| `clear` → writes allowed again | a fresh run is started deliberately, not automatically |

The deny fires from the **installed** `.harness/hooks/gate-budget` (the wired location), end to end, with no orchestrator in the loop — the same standard `evals/stop-gate/` meets for the per-cell breaker.

## The honest scope, now precise

After this: "bounded by construction" is **true** for what code reaches — the per-cell no-progress stop, and the global wall-clock / iteration / cell ceilings (all enforced by the wired `gate-budget`). What remains the orchestrator's *discipline* is only the **graceful** stop (notice the budget is spent, report, hand back) — and even if it ignores that, the gate denies its writes. The floor is code; the courtesy is the agent's.

## Replay

```bash
python3 harness-forge/evals/global-bound/check.py   # CI; exit 0 = the global bound is enforced in code
```
