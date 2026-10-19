<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 (red) `git grep -q 'show-toplevel' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`: pass. Evidence: rc=0 on the built tree (HEAD ccc3d023); rc=1 in a throwaway worktree at a9d42334 (parent of build commit 10075c99), so the check goes red before the build. The text is Preflight item 5 in run-rules.md (`git rev-parse --show-toplevel`, stop with state written when it is not the repository holding the plan doc), matching the Do.
- #2 (red) `git grep -qi 'already passes' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`: pass. Evidence: rc=0 on the built tree; rc=1 at a9d42334. The added sentence ends The loop step 4 and names the plan defect stop, the commit that built it, and that the driver never closes that ticket itself.
- #3 (guard) `python3 plugins/sdlc-lite/scripts/check.py >/dev/null`: pass. Evidence: rc=0 on the built tree. Negative control in the throwaway worktree with the built run-rules.md: rc=0 as is, then with `fanout.py prep` rewritten it printed `FAIL check.py: plan-doc skills: rules missing "fanout.py prep"`, so the guard covers this file and can go red.
- #4 (guard) `git grep -q 'plan_done.py' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`: pass. Evidence: rc=0 on the built tree and at a9d42334. A scratch copy of the file with the `plan_done.py` lines deleted gives `grep -q` rc=1, so the predicate can go red.

## Out of scope changes
None. The build commit 10075c99 changes only plugins/sdlc-lite/skills/run-plan/references/run-rules.md (+2/-1: Preflight item 5 and one sentence at the end of loop step 4). `git diff --check` on that commit is clean. The base sha ccc3d023 is the current HEAD, so `git diff ccc3d023` shows only the uncommitted verifier-*.attempt.json record churn from the run tooling, not build work. The later commits 0e0cfb96 (close records) and 4df56850 (notes) are run bookkeeping.

## For the next attempt
None
