## Task goal
Model and effort choices are backed by recorded experiments, and a change to the model table cannot land without citing one.

## Step 6: Gates green
level: L2
### Do
Depends on: steps 1 to 5. Run every gate the handoff's Common rules name, and fix any red the earlier steps introduced, inside the files those steps changed:
- `bash plugins/sdlc-lite/scripts/check.sh`, which now includes `evals.py selftest` and check.py's evals guard
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- `git diff --check`
- no em dash and no trailing whitespace in added lines or new files
- no change to the model rows of run.sh or to models.json

A gate already red at the build-start HEAD is reported as Status `inherited red: <tests>`. Do not bump versions, tag, push, or publish.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/evals.py check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `! git diff "$SDLC_BASE_SHA" -- plugins docs .sdlc/AGENTS.md | grep '^+' | grep -q "$(printf '\342\200\224')"`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs .sdlc/evals); do ! grep -q "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs .sdlc/evals); do ! grep -qE '[[:space:]]$' "$f" || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
