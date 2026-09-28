<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'clean whole-tree diff' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: ran the command, rc=0 (rule 13 extended with the exact phrase).
- `grep -qF 'script the span calls' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: ran the command, rc=0 (rule 13: "a clean check hidden inside a script the span calls is not caught").
- `grep -qF 'clean whole-tree diff' CLAUDE.md`: pass. Evidence: ran the command, rc=0; `git diff CLAUDE.md` shows the `scripts/steps.py` bullet extended next to the porcelain clause exactly as specified.
- `grep -qF 'clean whole-tree diff' .claude/agents/sdlc-lite-author.md`: pass. Evidence: ran the command, rc=0; diff shows line 18's plan-defect list now reads "a clean porcelain status or a clean whole-tree diff".
- `grep -qF "'clean whole-tree diff': ('agents/planner.md', 'scripts/steps.py')" plugins/sdlc-lite/scripts/check.py`: pass. Evidence: ran the command, rc=0; `git diff check.py` shows the exact `PLAN_DEFECT_DOCS` entry added.
- (guard) `grep -qF 'clean porcelain status' plugins/sdlc-lite/agents/planner.md`: pass. Evidence: ran the command, rc=0; wording preserved verbatim per diff.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: ran it, rc=0, output ends `steps selftest: PASS`, including the k8 fixtures for whole-tree-diff detection added in step 1's code (not this step's scope, but the guard exercises it and it's green).
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: ran the full script, rc=0; scanned full output for fail/error markers, none found; every listed selftest, shellcheck, and plugin validate line reads `ok`/`PASS`.

## Out of scope changes
`plugins/sdlc-lite/scripts/steps.py` and `.sdlc/0135-extend-the-clean-status-lint/handoff.md` also show as modified in `git status`, but neither was touched by this step's builder run: the steps.py detector code (`requires_clean_diff`, k8 selftest fixtures) is step 1's uncommitted work still sitting in the tree (builders never commit), and the handoff.md diff is the task's own `## Goal`/`## Plan review` bookkeeping from `/chain`'s planning flow, not step 2's Do. Checked via `git diff` on each file: step 2's builder-L2.md `## Changes` section lists only the four files the Do named, and the diff content for planner.md/CLAUDE.md/check.py/sdlc-lite-author.md matches the Do's instructions exactly with no extra edits. Not out of scope for step 2's verdict.

## For the next attempt
None.
