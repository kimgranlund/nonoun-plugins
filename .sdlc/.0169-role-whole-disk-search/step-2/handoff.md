## Task goal
A role cannot stall its run on a search of the whole filesystem, and a test that failed before the fix passes after it.

## Step 2: Gates green
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root. Fix any red that step 1 introduced, in the files step 1 changed. A gate already red at the build-start HEAD comes back as Status `inherited red`. All of these gates were green at plan time.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
