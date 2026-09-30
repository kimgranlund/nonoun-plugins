## Task goal
A role working on a plan step reads the entry files that govern the files it changes, on Claude Code and on Codex alike.

## Step 6: Gates green
level: L2
### Do
Read `plugins/sdlc-lite/AGENTS.md` first.

Run every gate below and fix any red that steps 1 to 5 introduced. If a gate was already red at `$SDLC_BASE_SHA`, report Status `inherited red`. If a shared role or skill body changed after step 2, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` again.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --check`
