## Goal
The maintainer plans a goal once in a plan doc, then a smaller model runs `/goal complete build and verify <plan-doc.md>` to done unattended, with the verifier still independent.

## Intent
Literal ask: plan-doc contract, plan_done.py and a run-plan executor any builder tier can drive with /goal, so I can plan in one session and have a smaller, faster model finish unattended, with the verifier still independent.
Level: L4 (lane: full; cost: high, three tickets across scripts and skills; reversible: no, a plan may name a push)
Deltas:
- hidden-scope: the ask bundles three parts -> defaulted: three parts in order, the plan-doc lint, the done condition script, then the run-plan skill, each its own ticket [U] (source: T-0410)
- assumption: the ask leaves self-grading and publishing open -> defaulted: the executor never grades itself, and push, tag and publish happen only when the plan names them [U] (source: root AGENTS.md)
Do:
1. Write a plan doc with three steps, one ticket each.
2. Build `plan_check.py plan` and its parser.
3. Build `plan_done.py <plan-doc>`, which exits 0 only when every step ticket is closed with a verifier pass.
4. Write the run-plan skill that loops on `plan_done.py`.
Non-goals:
- model or effort changes
- a long-lived orchestrator agent
Done when:
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_check.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py selftest` exits 0
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py` exits 0

## Outcome
Outcome: a planned goal runs to done with no maintainer hand step. Why: the maintainer's planning session is the scarce resource, not model time.
Measured by: hand steps per plan run (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/plan_done.py <plan-doc>` exits 0 with no hand edit in the run record), before: unmeasured, target: 0.
Rubric:
1. Done condition | pass: plan_done.py exits 0 only when every step is closed with an independent verifier pass.
2. Lint | pass: plan_check.py plan flags each rule's mutant and passes the good plan.
3. No self-grading | pass: no step is verified by the driver that built it.
Negative control: a plan with one step left open makes plan_done.py exit 1.

## Constraints
The driver MUST NOT verify a step it built.
