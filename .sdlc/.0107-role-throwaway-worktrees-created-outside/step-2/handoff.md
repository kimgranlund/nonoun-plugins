## Task goal
Inside a role run, a throwaway git worktree created outside `$SDLC_TMP_WORKTREES` (for example under `/tmp`) or created with a new branch (`git worktree add -b`/`-B`) can no longer leave a worktree or branch behind unnoticed: it is blocked before it is created, or detected and reported when the run ends.

Done when: an automated selftest (wired into `scripts/check.sh`) proves that, with `SDLC_ROLE` set, `git worktree add /tmp/x HEAD` and `git worktree add -b tmpbr <path under $SDLC_TMP_WORKTREES> HEAD` are caught (denied or reported), that `git worktree add --detach "$SDLC_TMP_WORKTREES/x" HEAD` still passes, and that nothing changes when `SDLC_ROLE` is unset.

## Step 2: Update the records that describe the hooks
level: L1
### Do
Make the records name the new hook and state its rule the way `block-pattern-kill.sh` is described:
- In the repo-root `CLAUDE.md`, add a `hooks/block-stray-worktree.sh` bullet in Layout after the `hooks/block-pattern-kill.sh` bullet. State what it denies and allows and that it fails closed. Note that fanout.py's own worktrees are untouched because they are not Bash tool calls, and that run.sh's EXIT cleanup stays. Add the hook to the hook-selftest list in the Commands "Check everything" line.
- In `.claude/agents/sdlc-lite-author.md`, add it to the check.sh hook-selftest list and to the learned hazards next to the pattern-kill entry.
- Add one clause to `plugins/sdlc-lite/agents/builder.md` rule 5 and `plugins/sdlc-lite/agents/verifier.md` rule 3: a hook denies `-b`/`-B`/`--orphan` and any path outside the prefix.

Keep each file's existing wording otherwise. No em dashes.
### Acceptance criteria
- `grep -q 'hooks/block-stray-worktree.sh' CLAUDE.md`
- `grep -q block-stray-worktree .claude/agents/sdlc-lite-author.md`
- `grep -q -- '--orphan' plugins/sdlc-lite/agents/builder.md`
- `grep -q -- '--orphan' plugins/sdlc-lite/agents/verifier.md`
- `! git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md | grep -q '^+.*—'`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
