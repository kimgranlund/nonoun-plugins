## Task goal
When the SDLC Lite conductor is in force, an Agent-tool spawn of another plugin's builder, verifier, or planner agent is flagged before it runs, with a message pointing at `run.sh`.

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below and fix any red that the earlier steps introduced, in the files those steps changed. A gate that was already red at the build-start HEAD is reported as `inherited red`. A gate that goes red while other lanes or probes run on this host and green when rerun alone is load, not a regression (during planning, `check.sh` went red once under parallel probe runs and green twice alone): rerun it alone before changing anything.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`
