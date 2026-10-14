<!-- role=builder level=L2 model=sonnet effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/specgate.py`: `red_target` now finds the step dir through `steps.step_dirs(task_dir).get(step)`. It falls back to `task_dir` when no step dir exists.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/steps.py`: added the selftest case `(records dir) step_dirs lists a task-side step dir`. It builds a task with a runtime records dir and a hand-written task-side `step-1/` that has no records twin. It asserts `step_dirs(task)` returns that task-side dir for 1.

## Checks
- `redck.py record`: ran before the first edit. It recorded both `(red)` controls as red, but as retrospective because 49 source paths already differ from HEAD (the tree carries earlier steps' work).
- (red) `specgate.red_target` one-liner: exit 0 after the edit.
- (red) `steps.py selftest | grep -qF "ok: (records dir) step_dirs lists a task-side step dir"`: the line is present.
- `specgate.py selftest && steps.py selftest`: both PASS.
- (guard) every changed or untracked file outside `.sdlc` is under `plugins/sdlc-lite/`: exit 0, run with `SDLC_BASE_SHA=27a0cc9c`.
- Negative control: with a records-side-only `step_dirs`, the new case's layout returns no step 1 (False with the mutant, True with the real function). I ran this as a standalone snippet. The full selftest crashes in an earlier unrelated case under that mutation, so it never reaches the new case.

## Notes
None
