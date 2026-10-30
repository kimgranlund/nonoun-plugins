# Plan review and plan refusals

Detail for /chain section 3.

## The `amend` action

`amend` → every finding of the newest review is `criterion-only` (a criterion the reviewer's replay on current main shows is a fact mismatch: a moved path, a deleted file, stale gate-log logic), with any `notes-fix` items: run `steps.py split .sdlc/<task>` as for `split`. It writes each replacement criterion into its step handoff in place of the old line and logs `- criterion-only amend: <review file>: step <n>: ...` under `## Plan review` itself. No planner run and no replan spent, even after the task's one design replan is used. A criterion-only item the script cannot apply makes `review` print `replan` (or `stop`) as a design finding.

## Rejected plans and overrides

`steps.py split` refuses a plan whose newest plan review says `replan` or `blocked`, so a rejected plan is never split. The count of `replan` reviews is per task dir: the second design one stops (a criterion-only review whose amends `## Plan review` logs is not counted). Only the user can lift a `replan` verdict (for example a review that faults a sound plan): on their say-so run `steps.py split .sdlc/<task> --override-review "<reason>"`, which records `review override: <review file>: <reason>` under `## Plan review` so later `split --only N` calls and `steps.py review` accept that review. A `blocked` verdict is never overridden, and a newer plan review ends the override. Unattended, a `replan` stays a stop.

## Caps

Caps (T-0553): a planner run is refused once the task holds two planner results (`replan cap:` from `dispatch.py prepare`, Codex `run.sh`), and `steps.py lint` and `split` refuse a plan with more steps than the ticket's `size:` allows (`step cap:`; L1 and L2 3, L3 6, L4 10, L5 15). Neither is a `plan defect` and neither is ever answered with a replan. Interactive: stop and ask the person with one AskUserQuestion (split the ticket, approve one more replan, or drop scope); on approval rerun with `--approved "<who: why>"` (`dispatch.py prepare` for the planner, `steps.py lint .sdlc/<task>` for the plan; Codex `run.sh`: `SDLC_REPLAN_APPROVED="<who: why>"`), which records the approval in the task's `skips.md`. Unattended: stop the task with status `blocked` naming the cap.

## Time budgets

Time budgets (T-0555, Claude `dispatch.py` only): a `time budget:` refusal from `prepare` (the ticket's agent time is past its `size:` budget) is handled like a cap: ask the person, rerun with `--approved "<who: why>"`, or stop `blocked` when unattended. An `over-budget` attempt in `dispatch.py status` is checked for a stdin wait or a stall, then brought to the person; it is never killed for them.

## Plan defect refusals

If `steps.py split` refuses with `plan defect`, the plan is wrong, not the build: append the refusal text to the task handoff under a `## Plan review` heading (create it if missing, keep earlier entries), rerun planner L3 on the task handoff, and run `steps.py review` again (a replan is reviewed only when it holds an L4 or L5 step) before splitting. After the second such refusal for this task, stop and ask the user. The full split here executes no criteria. The same handling applies to the split in 4.2, including a refusal from `--only N` for a red guard or a guard that changed the work tree.
