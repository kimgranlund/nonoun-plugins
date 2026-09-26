## Task goal
A criterion with an `||` fallback between checks is refused before any build.

## Step 2: Ban `||` fallbacks in the planner rules and sync the docs
level: L1
### Do
In `plugins/sdlc-lite/agents/planner.md`, under `## Criteria that can pass`, add one numbered rule after rule 4. It says:
- Never join two checks with `||` in one criterion, because a fallback passes when either side matches, so the criterion can hold at HEAD and never fail. State each check as its own criterion.
- `steps.py split` refuses a `||` join as a `plan defect`.
- The only allowed form is the empty-argument short circuit `test $# -eq 0 || ...`.

Renumber the later rules and keep their text. In `CLAUDE.md` (repo root), in the `scripts/steps.py` Layout bullet, change "refuses, with `plan defect` on stderr, a plan whose acceptance criterion command spans do not parse under `bash -n`" so it also says "or join two checks with `||` (an unquoted `||`, except after `test $# -eq 0`)". Use the literal phrase `join two checks with`. In `.claude/agents/sdlc-lite-author.md`, add the same phrase to the plan-defect route bullet (line 18), naming the split lint's `||` check, so the author agent stays in sync with CLAUDE.md.
### Acceptance criteria
- `grep -qE '[|]{2}' plugins/sdlc-lite/agents/planner.md`
- `grep -q 'join two checks with' CLAUDE.md`
- `grep -q 'join two checks with' .claude/agents/sdlc-lite-author.md`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
