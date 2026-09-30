## Task goal
A role that changes `scripts/run.sh` during its own run still gets its result saved, or is stopped before it can change the running file. A test that failed before the fix passes after it.

## Step 3: Gates green
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 and 2 introduced, keeping their behavior. If a gate was already red at the build-start HEAD, report builder Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check`
