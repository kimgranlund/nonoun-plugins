<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qE "^13\. .*clean porcelain status" plugins/sdlc-lite/agents/planner.md`: pass. Evidence: exit 0 on the built tree and exit 1 in a throwaway worktree at HEAD, so the check can go red. Rule 13 is at planner.md:29 and states the three points the Do asks for: no clean porcelain or `-s` status, since builders never commit; `git diff --quiet HEAD -- <path>` plus `git ls-files --others --exclude-standard -- <path>` instead; and the `steps.py split` plan defect refusal.
- `grep -qF "git ls-files --others --exclude-standard" plugins/sdlc-lite/agents/planner.md`: pass. Evidence: exit 0 built, exit 1 at HEAD.
- `grep -qF "clean porcelain status" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0 built, exit 1 at HEAD. The diff adds `'clean porcelain status': ('agents/planner.md', 'scripts/steps.py'),` to `PLAN_DEFECT_DOCS`, which is the exact line the Do names.
- `grep -qF "clean porcelain status" CLAUDE.md`: pass. Evidence: exit 0 built, exit 1 at HEAD. The diff adds the clause right after the fixed-number clause in the `scripts/steps.py` bullet. It names the emptiness test on `git status --porcelain` or `-s` with no `--` pathspec, and says to use `git diff` plus untracked files.
- `grep -qF "clean porcelain status" .claude/agents/sdlc-lite-author.md`: pass. Evidence: exit 0 built, exit 1 at HEAD. The diff adds "and one that requires a clean porcelain status" to the list of split lint checks in the plan-defect-route bullet.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: on the built tree it exits 0 and prints `ok: 18 role levels, 8 agents checked`. To see it go red, I copied the built check.py and steps.py into the HEAD worktree, where planner.md lacks rule 13. It then printed `FAIL agents/planner.md: plan-defect route missing "clean porcelain status"`. The phrase entry in `PLAN_DEFECT_DOCS` is the part that bites.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: exit 0 with `steps selftest: PASS` on the built tree, and also exit 0 at HEAD. It is a guard that no existing selftest broke. Step 1 owns the lint behavior this selftest covers.

## Out of scope changes
`plugins/sdlc-lite/scripts/steps.py` has 48 added lines. Step 2's Do does not ask for this change. The step-1 dir holds its own builder-L2 and verifier-L1 results, so this is step 1's lint work carried in the same uncommitted tree. It is not a step 2 change, so I am not filing it.

The other four files match the Do, checked against `git diff`.

Steelman: I drafted a finding on the author-file wording. The list now reads "..., and one that compares ..., and one that requires ...", with two "and"s. The builder's likely rebuttal is that the Do only asked for the phrase to be added to the list, and that the doubled "and" is a style nit, not a defect. That rebuttal holds, so I dropped the finding.

## For the next attempt
None
