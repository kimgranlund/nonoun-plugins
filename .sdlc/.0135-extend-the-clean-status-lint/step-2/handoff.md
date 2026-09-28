## Task goal
`steps.py lint` and `split` also refuse, as a plan defect, a criterion that requires a clean whole work tree through `git diff` (for example `git diff --quiet` or `git diff --exit-code` with no `-- <pathspec>` and no two-commit range), not only through an empty `git status --porcelain`/`-s`, while scoped and commit-to-commit diffs still pass. A clean check hidden inside a script the span calls stays out of reach, since the detector only reads span text; the docs say so.

## Step 2: Sync the docs and check.py guard, then gates green
level: L2
### Do
Update the rule in these places:
- `plugins/sdlc-lite/agents/planner.md` rule 13: extend it so a clean whole-tree diff is also forbidden. That means `git diff --quiet` or `git diff --exit-code` with no `-- <pathspec>` and no two-commit range, or an empty `git diff` output. Say that `steps.py split` refuses it as a `plan defect`, using the exact phrase `clean whole-tree diff`. Add that the detector reads only span text, so a clean check hidden inside a script the span calls is not caught and must not be written (exact words `script the span calls`). Keep the existing `clean porcelain status` wording.
- Root `CLAUDE.md`, the `scripts/steps.py` bullet: next to the porcelain clause, add that it also refuses a criterion that requires a clean whole-tree diff (a `--quiet`/`--exit-code` diff or an emptiness test on diff output, with no `--` pathspec and no two-commit range), and that a clean check inside a script the span calls stays out of reach.
- `.claude/agents/sdlc-lite-author.md` line 18: after "one that requires a clean porcelain status", add "or a clean whole-tree diff".
- `plugins/sdlc-lite/scripts/check.py` `PLAN_DEFECT_DOCS`: add the entry `'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py'),` in exactly that form.

Then run `bash plugins/sdlc-lite/scripts/check.sh` and fix any red that step 1 or this step introduced. No em dashes.
### Acceptance criteria
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'script the span calls' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'clean whole-tree diff' CLAUDE.md`
- `grep -qF 'clean whole-tree diff' .claude/agents/sdlc-lite-author.md`
- `grep -qF "'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py')" plugins/sdlc-lite/scripts/check.py`
- (guard) `grep -qF 'clean porcelain status' plugins/sdlc-lite/agents/planner.md`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest >/dev/null 2>&1`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
