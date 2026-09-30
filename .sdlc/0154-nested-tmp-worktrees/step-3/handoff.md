## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 3: gates green
level: L2
### Do
Run every gate below and fix any red that Steps 1 and 2 introduced. A gate that is already red at `$SDLC_BASE_SHA` is reported as Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
