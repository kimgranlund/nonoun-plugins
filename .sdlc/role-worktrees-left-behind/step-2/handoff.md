## Task goal
No role run leaves a git worktree behind, on success or failure.

## Step 2: Point role prompts and docs at the prefix
level: L2
### Do
- In `plugins/sdlc-lite/agents/verifier.md` rule 3, replace `git worktree add <tmp dir> HEAD` with a worktree created only under `$SDLC_TMP_WORKTREES`, for example `git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`. State that run.sh removes everything under that prefix when the run exits, and that the verifier still removes its own worktree when done. The later paragraph's "throwaway worktree at HEAD" should refer to the same place.
- In `plugins/sdlc-lite/agents/builder.md`, add one rule: any throwaway worktree goes only under `$SDLC_TMP_WORKTREES`, never `/tmp` or a sibling dir.
- `skills/checks-that-bite` names no location, so leave it alone.
- Leave the `merge-step` template's `<tmp>` placeholder unchanged. check.py keeps its two copies identical, and the verifier prompt now resolves `<tmp>`.
- Repair the stale records:
  - Add one sentence to the `scripts/run.sh` Layout bullet in the repo-root `CLAUDE.md`: run.sh exports `SDLC_TMP_WORKTREES=<toplevel>/.worktrees/tmp/<role>-<pid>` and removes every worktree under it on any exit, then runs `git worktree prune`.
  - Add the matching line to `.claude/agents/sdlc-lite-author.md`, next to the "throwaway worktrees" invariant on line 36.
### Acceptance criteria
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/verifier.md`
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/agents/builder.md`
- `! grep -q 'git worktree add <tmp dir> HEAD' plugins/sdlc-lite/agents/verifier.md`
- `grep -q SDLC_TMP_WORKTREES CLAUDE.md`
- `grep -q SDLC_TMP_WORKTREES .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
