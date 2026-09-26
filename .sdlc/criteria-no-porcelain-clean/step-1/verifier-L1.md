<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, the three bad spans each get a "clean porcelain status" finding: pass. Evidence: I ran the command and it exited 0 (`c1=0`). The printed findings show all three spans flagged. In a throwaway worktree at HEAD the same check exits 1 (`base_c1=1`), so it can go red.
- (guard) Criterion 2, the four allowed spans (`git diff --quiet HEAD -- src`, the untracked `ls-files -- src` test, a path-scoped `git status --porcelain -- src`, and `! git rev-parse -q --verify MERGE_HEAD`) get no finding: pass. Evidence: exit 0 (`c2=0`). It can go red because the new predicate fires on the three bad spans in criterion 1.
- `grep -q "(k6)" plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: exit 0. At HEAD, `grep -c "(k6)"` gives 0, so it bites.
- `grep -qF "clean porcelain status" plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: it printed `steps selftest: PASS`. `(k6)` is present in the diff at steps.py, after `(k5)`.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0 (`ck=0`).

Spot checks beyond the criteria, all matching the Do:
- `! git status --short | grep -q .` is flagged.
- `test "$(git status --porcelain)" = ""` is flagged.
- A bare `git status --porcelain` and `test -n ...` are not flagged.
- The docstring `lint` paragraph is extended.
- The two-line finding text matches the handoff.

## Out of scope changes
None. `git diff --stat` shows only `plugins/sdlc-lite/scripts/steps.py`. The untracked files are all under `.sdlc/`: the planner and runs artifacts, this step's own files, and `step-2/`.

## For the next attempt
None
