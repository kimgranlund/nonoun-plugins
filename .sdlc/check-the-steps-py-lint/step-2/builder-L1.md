<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/agents/planner.md`: rule 5 now lists two allowed `||` forms (the `test $# -eq 0` short circuit and a nonzero `exit` right operand), with the `for f in a b; do test -f "$f" || exit 1; done` example. `|| echo`, `|| true` and `|| exit 0` are named as still refused.
- `CLAUDE.md`: the `steps.py` bullet now says only a fallback `||` join is refused. It names both allowances and says `for`/`while`/`until`/`if`/`{` criteria are linted too.
- `.claude/agents/sdlc-lite-author.md`: line 18 now says a fallback `||` join is refused and names both allowed forms.
- `plugins/sdlc-lite/scripts/check.py`: added ``'nonzero `exit`': ('agents/planner.md', 'scripts/steps.py')`` to `PLAN_DEFECT_DOCS`.

## Checks
- All six acceptance greps passed, together with the `test $# -eq 0` guard grep: `! grep 'only allowed form'`, `! grep 'except after .test'`, `grep 'nonzero .exit'` in `planner.md` and `CLAUDE.md`, `grep nonzero` in `check.py`, `grep fallback` in the author agent file.
- `plugins/sdlc-lite/scripts/check.sh`: the first run exited 1 on `hook selftest: FAIL: block-pattern-kill without role: exit 141, want 0`. I ran `hook-selftest.sh` three more times and it passed each time. A second full `check.sh` run exited 0 with no FAIL lines.

## Notes
- The first-run hook selftest failure is flaky: exit 141 is SIGPIPE, in a hook this step did not touch. I did not run the base-worktree check because the rerun was green.
- The tree also holds changes from step 1 (`steps.py`, the ticket handoff) and untracked `.sdlc/` files. They are not from this step.
