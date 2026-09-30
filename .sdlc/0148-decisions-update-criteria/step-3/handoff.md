## Task goal
A conductor decision that widens a step's scope edits the scope guard the criteria read, so the next builder does not block on the old guard.

## Step 3: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root. Fix any red that steps 1 and 2 introduced, in the files those steps changed. The shellcheck part of `check.sh` is skipped on this host because shellcheck is not installed. That is not a failure.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check`
