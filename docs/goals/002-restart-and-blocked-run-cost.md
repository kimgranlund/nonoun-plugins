---
id: G-002
title: A host restart or a blocked run costs minutes, not hours
status: proposed
owner: maintainer
created: 2026-10-09
horizon: 2026-Q4
kpis: [K-002, K-003, K-004]
---
## Outcome
When the host restarts or a run blocks, the factory finds every lost or blocked run with one command and re-dispatches it, so the work thrown away per interrupted run is minutes, and builders stop blocking on plan or dispatch defects that a check could have caught before the build.

## Why
The [fleet retro of 2026-10-09](../reports/2026-10-09-fleet-retro-00.md) and the 12 hour retro answers of the same day (ui-kit-maison, agent-ui and ultimate-tokens, each in that repository's `.sdlc/fleet-retro-2026-10-09-12.md`) report three host restarts that cost maison about 2 hours of repeated verification, four crashed planner and reviewer runs in agent-ui, three builders blocked on a stale checkout, and builders blocked on scope lists and guards that could not pass. The attempt records of that day show 8 interrupted runs whose replacement started a median 34.3 minutes after the lost run began (K-002, unverified probe). The cost lands on wall time and on the user's attention, not only on spend.

## Scope
In: the seven 0.22.3 candidates in [the restart and blocked run plan](../specs/sdlc/restart-and-blocked-run-plan.md): orphan recovery after a restart, `dispatch.py record` before the result exists, the stale Tree and Base sha in dispatch prompts, circular criteria, scope lists and guards checked before build, prune safety, and the delta verifier measurement. The collector fields that make K-002 to K-004 readable are in scope.

Out: the host load itself and the gate admission design (T-0386), model and effort rows, the held criteria verdicts already built in T-0408, and checkpointing a role's partial work so a restarted run resumes it (a separate design if K-002 stays above target after this scope lands).

## Done when
- [K-002](../kpi/002-restart-recovery-minutes.md) reads 15 or below in the first fleet retro after the plan's tickets land.
- [K-003](../kpi/003-blocked-builders-per-wave.md) reads 5 or below in the same retro.
- [K-004](../kpi/004-unsatisfiable-criteria-caught.md) reads 50 or above once its early count is recorded; until then this line is open and the goal cannot be achieved.

## History
- 2026-10-09: proposed with K-002 to K-004 from the 2026-10-09 fleet retro and its 12 hour answers (planner-L3 of task plan-reliability-docs).
