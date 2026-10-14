<!-- role=verifier level=L1 model=opus effort=low -->
## Verdict
pass

## Criteria
- #1 (red) specgate.red_target returns the records-side step-1 dir: pass. Evidence: ran the handoff span verbatim in the tree, exit 0 (C1=0). Bites: in a scratch copy of plugins/sdlc-lite/scripts with specgate.py:149 reverted to a task-side-only lookup (`d = task_dir / f'step-{step}'`), the same span raised `AssertionError: .../le.04TL0E/.sdlc/0001-a` (red, it fell back to task_dir). process-deviations.md records a retrospective red-checkpoint for this criterion; I ran the red control myself as above.
- #2 (red) steps selftest prints `ok: (records dir) step_dirs lists a task-side step dir`: pass. Evidence: span exit 0 in the tree (C2=0); case at plugins/sdlc-lite/scripts/steps.py:6433-6440. Bites: with steps.py:509 mutated to read only `records_of(task)`, the span exit 1 (M2=1). The red comes from an earlier selftest case crashing (FileNotFoundError on solo-a/handoff.md) before the new case runs, so the criterion goes red but not through the new case's own assertion; the builder reported the same. Same retrospective red-checkpoint deviation applies; red control run by me.
- #3 specgate and steps selftests: pass. Evidence: `specgate selftest: PASS`, `steps selftest: PASS`, both exit 0.
- #4 (guard) no changes outside plugins/sdlc-lite besides .sdlc: pass. Evidence: span with SDLC_BASE_SHA=27a0cc9c44ad6a5fd28d05ef72afaea618146b9d exit 0 (C4=0); git status shows only plugins/sdlc-lite/** and .sdlc/** changed or untracked.

## Out of scope changes
None. The step-5 edits are specgate.py:149-150 and the steps.py selftest case at :6433-6440; other modified plugins/sdlc-lite files are earlier steps' uncommitted work of this task (builder report notes 49 paths differ from HEAD), and all fall under the guard's allowed prefix.

## For the next attempt
None

## Notes
- plugins/sdlc-lite/scripts/steps.py:6439: the new case cannot be observed failing by itself under a records-only step_dirs mutation, because an earlier selftest case crashes first; the criterion still goes red.
- Pre-build worktree at the base sha could not be created: the block-stray-worktree hook refused because SDLC_TMP_WORKTREES is unset in this session; red controls used mutated scratch copies under the tmp prefix instead (removed afterward).
