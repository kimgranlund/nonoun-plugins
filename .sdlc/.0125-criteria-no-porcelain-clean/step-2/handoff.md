## Task goal
Criteria never require a clean porcelain status, which a no-commit builder can't meet.

## Step 2: Planner rule and doc sync for the clean-status lint
level: L1
### Do
- In `plugins/sdlc-lite/agents/planner.md`, add rule 13 after rule 12 under "Criteria that can pass". It says:
  - Never require a clean `git status --porcelain` or `git status -s` as a criterion. Builders never commit, so the step's own changes keep the status dirty and the criterion can never pass.
  - Check the step's changes with `git diff` (`git diff --quiet HEAD -- <path>`) plus untracked files (`git ls-files --others --exclude-standard -- <path>`).
  - `steps.py split` refuses an emptiness test on an unscoped porcelain or short status as a `plan defect`. The rule must use the exact phrase "clean porcelain status".
- In `plugins/sdlc-lite/scripts/check.py`, add `'clean porcelain status': ('agents/planner.md', 'scripts/steps.py'),` to `PLAN_DEFECT_DOCS`.
- In the repo-root `CLAUDE.md` `scripts/steps.py` bullet, add a clause after the fixed-number clause. It names the new refusal: a criterion that requires a clean porcelain status, meaning an emptiness test on `git status --porcelain` or `-s` with no `--` pathspec, and says to use `git diff` plus untracked files instead.
- In `.claude/agents/sdlc-lite-author.md`, add "one that requires a clean porcelain status" to the list of `steps.py split` lint checks in the plan-defect-route bullet.
### Acceptance criteria
- `grep -qE "^13\. .*clean porcelain status" plugins/sdlc-lite/agents/planner.md`
- `grep -qF "git ls-files --others --exclude-standard" plugins/sdlc-lite/agents/planner.md`
- `grep -qF "clean porcelain status" plugins/sdlc-lite/scripts/check.py`
- `grep -qF "clean porcelain status" CLAUDE.md`
- `grep -qF "clean porcelain status" .claude/agents/sdlc-lite-author.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
