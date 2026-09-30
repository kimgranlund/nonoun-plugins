## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 2: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below. Fix any red that step 1 introduced, for example:
- a `scripts/check.py` contract that pins the chain skill's `allowed-tools` line or its wording;
- Codex generated-agent drift (regenerate with `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`, never edit the TOML by hand);
- trailing whitespace.

Keep fixes inside the files step 1 changed, plus any generated files the regeneration rewrites. A gate that was already red at the build-start HEAD is reported as Status `inherited red: <tests>`. The resume rule in the chain skill is conductor prose; these gates prove the script and the contracts, not a live resumed /chain run.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -q '^ok: resume'`
