## Task goal
A ticket can depend on the specific fix it needs (a capability or file) instead of a serial integration ticket, so parallel work is not blocked until a human overrides the dependency.

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root. Fix any red that steps 1 and 2 introduced, keeping their behavior. If a skill body change makes generated Codex agents drift, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. A gate already red at the build-start HEAD is reported as `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`
