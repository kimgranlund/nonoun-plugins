<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `lint_steps` finds `while ... done < f` with `|| echo` fallback: pass. Evidence: `python3 -c '...steps.lint_steps(...)'` on the built tree exits 0; the same command in a throwaway worktree at pre-build HEAD (`cc6c797`, via `git worktree add --detach "$SDLC_TMP_WORKTREES/base" cc6c797`) exits 1, confirming the check bites.
- `lint_steps` finds `for ... done | cat` with a fallback: pass. Evidence: same command exits 0 on built tree, exits 1 at pre-build HEAD in the throwaway worktree.
- `is_command` true and lint stays clean for `done 2>/dev/null` with fail-fast `|| exit 1`: pass. Evidence: same command exits 0 on built tree, exits 1 at pre-build HEAD.
- (guard) `is_command("for each file done < f")` is False: pass. Evidence: `python3 -c '...steps.is_command(...)'` exits 0 on built tree.
- selftest passes and prints `trailing redirect`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/steps.py selftest` rc=0 on built tree, output contains `ok: (k2) ... trailing redirect ...` lines (4 new cases); at pre-build HEAD the same selftest passes but its output has no `trailing redirect` match (`grep -qF` rc=1), so criterion 5's grep half bites.
- `grep -qF 'trailing redirect or pipe' plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: exits 0 on built tree (steps.py:47, 261); exits 1 at pre-build HEAD.
- `grep -qF 'trailing redirect or pipe' CLAUDE.md`: pass. Evidence: exits 0 on built tree (CLAUDE.md:33); exits 1 at pre-build HEAD.

Gate: `plugins/sdlc-lite/scripts/check.sh` run from git toplevel on the built tree: exits 0, all suites `PASS`, including the four new `(k2) ... trailing redirect` selftest lines inside `steps selftest: PASS`.

Note on a Do-prose deviation (not a criterion, so not a fail): the Do section's literal spec ("closing keyword preceded by start, whitespace, `;`, `&`, or `|`") would make `for each file done < f` a command (whitespace precedes `done`, and `< f` starts a redirect), directly contradicting criterion 4's guard that it must stay a non-command. The builder instead required `;`, `&`, or newline before the keyword (see `builder-L2.md` Notes and `steps.py:277-279`), which resolves the contradiction and is the only choice under which all seven acceptance criteria (including the guard) can hold. Checked by reading `steps.py` diff directly, not by the builder's summary. Since every stated acceptance criterion passes and the Do's own prose is internally inconsistent on this point, this is not filed as a fail; it doesn't rise to a plan defect against a specific criterion since no criterion contradicts another.

## Out of scope changes
- `.sdlc/the-steps-py-lint-does/handoff.md`, `planner-L2.md`, `runs.jsonl`, `step-2/` (untracked): normal `/chain` planning-phase artifacts (task Goal/Constraints filled in, second step split out), not code the step-1 Do named. Checked via `git diff .sdlc/the-steps-py-lint-does/handoff.md`: only the task-level Goal/Constraints prose changed, no code. Dismissing as expected SDLC scaffolding, not a step-1 builder change.
- None beyond that.

## For the next attempt
None.
