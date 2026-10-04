<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints the new `ok: (r) review_required ...` line: pass. Evidence: I ran `steps.py selftest` and it exited 0. The output ends `steps selftest: PASS` and includes `ok: (r) review_required returns the unresolved items and every reason review prints, in order`. To check the case can go red, I copied the built `steps.py` into a throwaway worktree and changed the `'the plan has a merge step'` string to `'...stepX'`. The selftest then failed with `- (r) review_required returns ...`, so the case bites on the reason text. The worktree is removed.
- `review_action` source contains `review_required(` and not `builder L4 or L5`: pass. The `inspect` one-liner exited 0.
- `lean_warnings` source contains `review_required(` and not `Merge `: pass. The `inspect` one-liner exited 0.
- (guard) full selftest: pass. It exited 0 and printed PASS. All existing `(r)` and `(lean)` cases are still `ok`, and the diff touches no existing case.
- (guard) no em dash in `steps.py`: pass. The command exited 0.
- (guard) scope check against `$SDLC_BASE_SHA`: pass. The command exited 0. `git status` shows only `steps.py` modified outside `.sdlc`.

I also read the diff against the Do:
- `review_required` returns `(unresolved, why)` with the five reason strings in the specified order.
- `review_action` keeps the structure check, the `plans` list, and the newest-plan pick, and then calls `review_required`.
- `review_action` still stops on `unresolved[0]` with the same reason text.
- `lean_warnings` keeps its `result_level` check and returns `[]` when `unresolved` or `why` is non-empty.
- `len(plans)` in `review_action` and `len(order.ordered(task_dir, 'planner'))` in `review_required` are the same computation. `plans` is `order.ordered(t, 'planner')`.
- The new selftest case asserts the exact reason line from the handoff on `review`'s second stdout line. I did not run a separate comparison of the `review` output at the base commit. The new case's exact-string assertion on that line, passing on the built tree, is the evidence.

## Out of scope changes
None. `git status` shows only `steps.py` modified. The other entries are untracked artifacts under `.sdlc/0197-lane/step-1`.

## For the next attempt
None
