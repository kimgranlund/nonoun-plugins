# Control Model Reference

## Horizons

| Horizon | Purpose | Typical scope | Authority | Verification |
|---|---|---|---|---|
| H0 Action | Produce one observable signal | one action | minimal | V0 |
| H1 Repair Window | bounded local search | one local issue | local | V0–V2 |
| H2 Episode | resolve one causal cluster | failure cluster | scoped | V0–V3 |
| H3 Verification Cycle | govern correctness of a run | system/task | broad | V0–V5 |
| H4 Learning Cycle | improve future runs | cross-run | systemic | trend/pattern |

## Control flow

```text
H4 Learning
  └─ H3 Cycle
      ├─ Frame / Baseline / Verify
      ├─ H2 Episode
      │   └─ H1 Repair Window
      │       ├─ H0 Action
      │       ├─ H0 Action
      │       └─ H0 Action
      ├─ H2 Episode
      └─ Integrate / Regress / Learn / Report
```

The parent horizon owns the child horizon's budget and may terminate it. A child horizon may request escalation but may not silently expand its own authority.

When H4 is a series of cycles against a live or paid system, it also owns the fixed comparison set, the alternation of targeted and full cycles, and the approval gate before each paid cycle ([experiment-series.md](experiment-series.md)).

## Recommended run protocol

When invoked, follow this concise protocol:

```text
FRAME
  Define intent, expected outcomes, invariants, budgets, stop rules.

BASELINE
  Establish checkpoint and capture initial evidence.

VERIFY
  Run broad verification once.

TRIAGE
  Deduplicate and cluster failures into episodes.

FOR EACH EPISODE
  Diagnose → open bounded repair window → progressively verify → terminate with explicit state.

INTEGRATE
  Combine validated changes at checkpoint.

REGRESS
  Run wider regression and outside-in/inside-out evaluation.

LEARN
  Capture root causes and durable hardening only where justified.

REPORT
  Emit the cycle report and stop.
```

## Checkpoints and transactional change

Use checkpoints to keep experimentation reversible.

At minimum preserve:

- starting baseline;
- episode start state;
- last validated state;
- integrated candidate state before full regression.

When the environment supports branches, worktrees, snapshots, transactions, versioned artifacts, or reversible patches, use them. Otherwise record enough state to revert safely.

Commit or retain changes only after their required progressive verification passes.

## Concurrency

Episodes may run in parallel when all are true:

- causal boundaries are independent enough to avoid misleading diagnosis;
- change scopes do not conflict;
- shared state can be isolated;
- integration order is known or unimportant;
- each episode maintains its own evidence and budget.

Serialize episodes when one is upstream of another or when they modify shared contracts, architecture, evaluators, or common state.

## Cost-aware strategy

Optimize for **evidence gained per unit cost**, not for the number of actions completed.

Prefer:

- focused tests before full suites;
- dependency-aware invalidation before global reruns;
- representative scenarios before exhaustive scenarios;
- probes before rewrites;
- reversible changes before structural changes;
- upstream causal fixes before repeated downstream patches;
- cached valid evidence before recomputation;
- batching independent episodes where isolation is preserved.

Do not optimize cost by weakening acceptance criteria or skipping the final verification required to make a trustworthy claim. When each run costs money, the cap, ordering and preflight rules in [live-evaluation.md](live-evaluation.md) apply on top of this list.

## Universal adaptation

Map the generic concepts to the current domain:

```text
intent       → requirement / goal / desired state
artifact     → code / UI / document / dataset / workflow / configuration / plan
execution    → run / render / query / simulate / inspect / publish / operate
evidence     → tests / measurements / logs / screenshots / outputs / observations
contract     → schema / interface / rubric / policy / invariant / acceptance rule
repair       → edit / regenerate / configure / restructure / retry / replace
checkpoint   → commit / snapshot / version / saved state / transaction
regression   → re-evaluation of previously valid behavior
learning     → durable test / rule / knowledge / contract / system improvement
```

Do not assume software-specific tools unless the current task is software.
