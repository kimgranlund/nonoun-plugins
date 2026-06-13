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
| unmarked + no budget → allowed | manual editing / `/harness-advance` is free (not the loop) |
| **marked + no budget → every write denied (exit 2)** | **the I-9 arming-gap closure: a marked loop fails closed, not unbounded** |
| `stop` (clears marker + budget) → writes allowed again | a fresh run is marked + armed deliberately, not automatically |

The deny fires from the **installed** `.harness/hooks/gate-budget` (the wired location), end to end, with no orchestrator in the loop — the same standard `evals/stop-gate/` meets for the per-cell breaker.

## The arming gap, now closed (I-9, v0.5.0)

The v0.4.1 council named a real residual: the global bound was *enforced* in code but *armed* by the orchestrator's step 0, and the gate couldn't fail-closed without a budget because it couldn't tell a loop-write from a human's edit. **v0.5.0 closes it with a loop-active marker:**

- **Enforcement is code.** Once a run budget exists, `gate-budget` denies every write past it — wall-clock, iterations, cells — with no agent in the path. The eval proves this, including via the orchestrator's actual CLI (`run-budget.py start`).
- **Arming is now fail-closed.** `/harness-run` writes a loop-active marker as **step 0a** (`run-budget.py mark`) *before* arming the budget at **step 0b** (`run-budget.py start`). `gate-budget` denies every write while marked-but-un-budgeted — so skipping step 0b no longer produces a silent unbounded run; it produces a *denied* one. The eval asserts exactly this (`marked + no budget = denied`), plus the directionality control (`unmarked + no budget = free`, so manual editing and `/harness-advance` aren't bricked).

So "bounded by construction" now means **the autonomous loop cannot write un-budgeted.** The marker is what the gate previously lacked — the signal that distinguishes the running loop from a human. It is in the deny-on-write `.harness/run/*` perimeter (a worker can't clear its own marker to escape), `run-budget.py start` still refuses a *vacuous* budget, and `/harness-status` surfaces the arming-gap state explicitly. The residual shrank from "forget step 0" to "skip the entire run preamble" — a flagrant deviation, not a quiet one.

## Replay

```bash
python3 harness-forge/evals/global-bound/check.py   # CI; exit 0 = the global bound is enforced in code
```
