## Task goal
A repository that adopts SDLC Lite gets entry files that route into `docs/` and explain `.sdlc/`, plus a stated docs layout, without losing anything it already wrote.

## Step 5: Gates green
level: L2
### Do
Run every gate below and fix any red that the earlier steps introduced, in the files those steps own. A gate that was already red at the build-start HEAD is reported as Status `inherited red`. Also run any available skill validator on `plugins/sdlc-lite/skills/onboard` and on the Progressive Context skill, and report the validation as unverified when no validator is installed.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
