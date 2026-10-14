<!-- role=builder level=L4 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/steps.py: added the helpers `task_of` and `records_of` (plus `_as_given`). `find_plan` now returns the plan through order and the task folder separately. split, `--supersede`, `earlier_widened`, `earlier_created`, `live_step_dirs`, `batch_verified`, `next_action`, `resume_action`, swap and widen now work on step dirs in the records dir (split uses `create=True`). `record_refusals` writes `<records>/refusals.jsonl`. `base_sha` reads `base-sha` from the records dir. `read_goal`, review, lane, `record_lane`, `verifier-level`, precheck, open, `held_items` and `full_gate_commands_for` read the task folder. Lint maps a task-side step path to its records twin. Updated the usage docstring and added 3 selftest cases.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/redck.py: `resolve` sends the dir through `order.records_dir`, with `create=True` for record and audit. `base_sha` and `dirty_paths` get `handoff.parent`. Selftest fixtures moved to records-side step dirs (`.sdlc/runtime/tasks/tN/step-1`). Added a `(records dir)` check: a task folder's checkpoint lands in `order.records_dir`. Docstring paths updated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/verify_scope.py: the lane check reads `order.task_dir(<handoff dir>)/skips.md`, and the tests gate reads `red-checkpoint.jsonl` through `order.records_dir`. Docstring paths updated. `RECORD_NAMES` unchanged.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/fanout.py:
  - `verifier_files` lists `order.records_dir(taskdir)`, and `price_solo_row` reads `order.records_dir(taskdir)/runs.jsonl`.
  - The T-0331 fixture now has a `.sdlc` parent and reads through `records_dir`.
  - Case 17 reads the `role solo` rows from `.git/sdlc-lane-archive/*/.sdlc/runtime/tasks/<slug>/runs.jsonl`, with the git-object read kept as the legacy fallback.
  - Case 22's allow-list now accepts `!! .sdlc/runtime/.gitignore`.
  - Transport code untouched.

## Checks
- `redck.py record <handoff>` before the first edit: exit 0, "recorded 2 retrospective control(s) red". The stderr said "14 source path(s) already differ from HEAD", meaning steps 1 and 2 were uncommitted in this tree before I edited anything.
- `fanout.py selftest` before any edit: exit 1, FileNotFoundError traceback at fanout.py:2812 (the T-0331 fixture). This is the red that step 2 caused.
- AC1 (red, split writes `runtime/tasks/0001-a/step-1`, only `handoff.md` untracked in the task folder): exit 0.
- AC2 (guard, legacy split in place, no `.sdlc/runtime`): exit 0.
- AC3 (guard, lane writes `skips.md` in the task folder, no runtime): exit 0.
- AC4 (red, `fanout.verifier_files` reads the records dir): exit 0.
- AC5 (`steps.py selftest` plus both `(records dir)` ok lines): exit 0, PASS. Also prints the legacy control line.
- AC6 (`redck.py selftest && verify_scope.py selftest`): exit 0, "redck selftest: PASS" and "verify_scope.py selftest: ok".
- AC7 (`fanout.py selftest`): exit 0, "fanout selftest: PASS".
- AC8 (guard, scope allow-list): exit 0.
- I made one last small change, to `base_sha`'s handoff lookup and redck's `base_sha` argument, after the fanout run. I re-ran AC5 and AC6 afterwards and both are green. AC7 was not re-run; fanout.py never calls `base_sha`.

## Notes
- The red checkpoint is stored as retrospective only because steps 1 and 2 were already uncommitted in this tree (14 dirty source paths) when `record` ran, before my first edit. The handoff's own red commands were red at that point (exit 0 from `record`). If `process-deviations.md` flags this, it reflects the shared tree, not an edit before the record.
- One deviation from the design: `steps.records_of` differs from `order.records_dir` in one case. Without `create`, an existing dir whose records dir does not exist is read in place, for example a hand-written task-side `step-<n>/` holding only `handoff.md`. Without this, a step dir in a temp fixture with no `.sdlc` parent and no legacy marker resolved to a missing `<parent>/runtime/tasks/...`. That turned about 40 existing steps selftest cases red (next, the T-0381 base cases, every widen case). It also keeps /fix-style hand-written step handoffs in the task folder readable. split always writes through `create=True` and never uses the fallback.
- `base_sha` reads the `base:` line from the handoff in the dir it is given, else from the records-side step handoff. It reads `base-sha` from the records dir. redck now passes `handoff.parent`, so a task-level (solo) handoff's `base:` line is still seen.
- Follow-up for the planner, out of this step's scope: `fanout.py planned_scope` (around :1023) still lists `step-*` under the ticket's task folder. With step dirs in runtime, a planned ticket in runtime layout now reads as "not planned" there. No selftest case covers it.
- System TMPDIR pollution: the pre-edit fanout run (T-0331 fixture with no `.sdlc` parent, in the step-2 state) left `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/runtime/tasks/tmp8wnbi2bv`. Older `tmp*` dirs there (21:14 to 22:06) come from earlier runs. The rm hook refuses paths outside my prefix, so I did not delete them. Runs after my edits added none.
- Scratch dir `.worktrees/tmp/0540-s3-builder-L4` has been removed. `d.json` and `last.py` in `.worktrees/tmp/` are not mine. No commits were made.
