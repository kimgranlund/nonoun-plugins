## Task goal
Inherited red never blocks a step whose own work is green.

## Step 2: Gates green
level: L1
### Do
Run the repo's full gate, `bash plugins/sdlc-lite/scripts/check.sh`, on the tree with step 1's changes. Fix any red that step 1 introduced, and change only the files step 1 touched. If the gate is already red at the build-start HEAD (check it in a `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD` copy), report Status `inherited red: <tests>`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
