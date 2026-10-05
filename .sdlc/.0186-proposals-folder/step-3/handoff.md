## Task goal
Repeated failures in past runs become evidence-backed candidate proposals in a folder, and nothing is applied without an eval.

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 and 2. Run every gate the handoff's Common rules name. Fix any red the earlier steps introduced, inside the files those steps changed:
- `bash plugins/sdlc-lite/scripts/check.sh`, which now includes `proposals.py selftest`
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/proposals.py selftest`
- `git diff --check`
- no em dash and no trailing whitespace in added lines or new files
- no change to `run.sh` or `models.json`

A gate already red at the build-start HEAD is reported as Status `inherited red: <tests>`. Do not bump versions, tag, push, or publish.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/proposals.py selftest`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" && git diff --check "$SDLC_BASE_SHA" -- .sdlc/AGENTS.md`
- (guard) `! git diff "$SDLC_BASE_SHA" -- plugins docs .sdlc/AGENTS.md | grep '^+' | grep -q "$(printf '\342\200\224')"`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs .sdlc/proposals); do ! grep -q "$(printf '\342\200\224')" "$f" || exit 1; done`
- (guard) `for f in $(git ls-files --others --exclude-standard -- plugins docs .sdlc/proposals); do ! grep -qE '[[:space:]]$' "$f" || exit 1; done`
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/proposals.py -e plugins/sdlc-lite/scripts/check.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/skills/handoff-format/SKILL.md -e plugins/sdlc-lite/AGENTS.md -e docs/reports/proposals-live-run.md | { ! grep -q .; }`
