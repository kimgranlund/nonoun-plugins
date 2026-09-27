## Task goal
When a role run leaves behind a git worktree or branch it created outside the Bash tool text the block-stray-worktree hook sees (from a python script, make target, or other program), run.sh reports it at run end, so the conductor and user learn about the stray instead of finding it later.

## Step 3: Gates green
level: L1
### Do
Run `plugins/sdlc-lite/scripts/check.sh` and fix any red the earlier steps introduced (shellcheck, the run selftest, check.py doc guards). The `claude plugin validate` warning about CLAUDE.md is expected. Do not change `hooks/block-stray-worktree.sh`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
