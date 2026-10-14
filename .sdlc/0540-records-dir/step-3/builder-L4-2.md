<!-- role=builder level=L4 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/steps.py: try 2 adds two helpers.
  - `step_handoff(d)` returns a step dir's own `handoff.md`, else the one in its twin on the other side, found through `order.task_dir` and `order.records_dir`.
  - `step_dirs(task)` returns the step dirs of the task folder and the records dir together, preferring the records-side dir when both exist.
  - These handoff readers now go through `step_handoff`: `step_handoff_of` (used by lint), `handoff_level` (used by next), the title read in `batch_verified`, `step_criterion_lines`, `earlier_created`, `earlier_widened`, swap and widen.
  - `live_step_dirs`, `resume_action`, `earlier_created` and `earlier_widened` now list step dirs through `step_dirs`.
  - New selftest case `(records dir) a task-side step handoff with an empty records twin: lint, next and resume read it`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/fanout.py: `planned_scope` now lists step dirs through `steps.step_dirs` and reads each handoff through `steps.step_handoff`, so both the records-dir layout and in-place step dirs are read. Case 14 gets a records-dir variant, with the in-place case as its legacy control.
- Try 1's changes to redck.py and verify_scope.py, and its other fanout.py and steps.py changes, are still in the tree and were not touched.

## Checks
- `redck.py record <handoff>` before the first edit of this attempt: refused both (red) spans as "green now". It said "retrospective: 18 source path(s) already differ from HEAD". This is expected on a resume: try 1's edits are already in the tree.
- AC1 (red: split writes `runtime/tasks/0001-a/step-1`, and only `handoff.md` is untracked in the task folder): rc 0.
- AC2 (guard: a legacy task splits in place, no runtime dir): rc 0.
- AC3 (guard: lane writes `skips.md` in the task folder, no runtime dir): rc 0.
- AC4 (red: `fanout.verifier_files` reads the records dir): rc 0.
- AC5 (`steps.py selftest` plus both `(records dir)` ok lines): rc 0, PASS. I ran it once after the lint, next and resume fix, and again after the last edit (swap and widen); both green. All four `(records dir)` lines print, including the new one.
- Negative control for the new steps case: with `step_handoff` patched to `d/handoff.md`, the selftest fails on exactly that one case.
- AC6 (`redck.py selftest && verify_scope.py selftest`): rc 0.
- AC7 (`fanout.py selftest`, system TMPDIR): rc 0, "fanout selftest: PASS".
- Negative control for the case-14 variant: on a records-side step handoff, `planned_scope` returns `{'a.txt', 'shared.txt'}`. With `steps.step_dirs` patched to look only in the task folder, it returns `None`, the defect the verifier reported.
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` (system TMPDIR), the dependent the verifier named: rc 0, "dispatch selftest: PASS". It ran before the swap and widen edit; neither dispatch.py nor fanout.py calls swap or widen.
- AC8 (guard: scope allow-list against 27a0cc9c): rc 0.
- `git diff --check` on steps.py and fanout.py: clean.

## Notes
- The red checkpoint for this attempt is a retrospective base control. The tree already held try 1's edits, so both (red) spans were green before this attempt's first edit. That is not a plan defect: the verifier ran both spans at base and saw rc 1. Try 1's own control was also retrospective, because the uncommitted step 1 and 2 paths were in the tree.
- I also routed swap and widen through `step_handoff`, which the verifier did not ask for. Both had the same defect: a hand-written task-side step whose records twin has no handoff would be refused with "no step handoff". Edits now go to the handoff wherever it sits; results stay in the records twin.
- `step_handoff` returns an absolute path when it falls back to the twin, so a message that names a twin's handoff shows it as absolute.
- The scratch dir `.worktrees/tmp/0540-s3-builder-L4-2` has been removed. `.worktrees/tmp/d.json` and `last.py` are not mine. No commits were made.
