## Task goal
When a role run leaves behind a git worktree or branch it created outside the Bash tool text the block-stray-worktree hook sees (from a python script, make target, or other program), run.sh reports it at run end, so the conductor and user learn about the stray instead of finding it later.

## Step 2: Document the run-end stray report
level: L1
### Do
- **CLAUDE.md, `scripts/run.sh` bullet:** add one sentence about the run-end report. It covers the stderr line forms (quote `stray worktree appeared during this run`), the `stray_worktrees` and `stray_branches` runs.jsonl fields, that it is report only, that the exit code is unchanged, that this run's prefix is excluded, and that a dry run takes no snapshot.
- **CLAUDE.md, `hooks/block-stray-worktree.sh` bullet:** add that worktrees and branches made from inside a script or program a role runs bypass the hook, and that run.sh reports them at run end. Use the words `run end`.
- **`.claude/agents/sdlc-lite-author.md`:** make the same two notes. Extend the existing block-stray-worktree hazard line (the one containing `block-stray-worktree.sh`) with `run end`, and mention `stray worktree appeared during this run`.

Use no em dashes. Keep CLAUDE.md and the author agent in sync.
### Acceptance criteria
- `grep -qF 'stray worktree appeared during this run' CLAUDE.md`
- `grep -F 'hooks/block-stray-worktree.sh' CLAUDE.md | grep -qF 'run end'`
- `grep -qF 'stray worktree appeared during this run' .claude/agents/sdlc-lite-author.md`
- `grep -F 'block-stray-worktree.sh' .claude/agents/sdlc-lite-author.md | grep -qF 'run end'`
- `grep -qF 'stray_branches' CLAUDE.md`
