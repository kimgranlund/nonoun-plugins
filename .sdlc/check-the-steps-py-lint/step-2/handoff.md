## Task goal
The `steps.py` `||` lint refuses only real fallbacks (a criterion that passes when either side passes) and stops refusing the fail-fast `||` forms that peer repos' plans actually use, so a valid plan is never sent to a replan as a plan defect.

## Step 2: Update every record of the `||` rule and guard the phrase
level: L1
### Do
Change these records to match step 1: `||` is allowed only in the `test $# -eq 0` short circuit or when its right operand is a nonzero `exit N` (bare, or as the last command of a `{ ...; }` group). `|| echo`, `|| true` and `|| exit 0` stay refused. Loop and `if` criteria are now linted too.

- `plugins/sdlc-lite/agents/planner.md`, rule 5: replace the bullet "The only allowed form is the empty-argument short circuit ..." with the two allowed forms. Use the literal phrase ``nonzero `exit` ``, keep `test $# -eq 0` named, and give one example: `for f in a b; do test -f "$f" || exit 1; done`.
- Repo `CLAUDE.md`, the `scripts/steps.py` bullet: replace "(an unquoted `||`, except after `test $# -eq 0`)" with a short parenthetical naming both allowances, using the phrase ``nonzero `exit` ``. Also state that `for`/`while`/`until`/`if`/`{` criteria are linted.
- `.claude/agents/sdlc-lite-author.md`, line 18: make the `||` wording say it refuses a real fallback join, not every `||`, and keep it in sync with CLAUDE.md.
- `plugins/sdlc-lite/scripts/check.py`: add ``'nonzero `exit`': ('agents/planner.md', 'scripts/steps.py')`` to `PLAN_DEFECT_DOCS`, so the phrase cannot drift out of either file.
### Acceptance criteria
- `! grep -n 'only allowed form' plugins/sdlc-lite/agents/planner.md`
- `! grep -n 'except after .test' CLAUDE.md`
- `grep -q 'nonzero .exit' plugins/sdlc-lite/agents/planner.md`
- `grep -q 'nonzero .exit' CLAUDE.md`
- `grep -q 'nonzero' plugins/sdlc-lite/scripts/check.py`
- `grep -q 'fallback' .claude/agents/sdlc-lite-author.md`
- (guard) `grep -qF 'test $# -eq 0' plugins/sdlc-lite/agents/planner.md`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
