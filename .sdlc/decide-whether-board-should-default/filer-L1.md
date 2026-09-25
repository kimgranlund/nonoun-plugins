<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0021: Default /board to ticket-id order when tasks have tickets

## PR body
### Summary
When you run `/board` with no `--sort` flag, it now orders by ticket id if any rendered task has ticket front matter. Unticketed tasks follow in recency (mtime) order. With no ticketed tasks the default is still recency. An explicit `--sort recent|id|name` works exactly as before. This carries out the user's decision on the T-0017 follow-up.

### Changes
- `plugins/sdlc-lite/scripts/board.py`:
  - `--sort` now defaults to None.
  - `main()` filters with `belongs_on_board` before sorting, so the default depends only on the tasks that are rendered.
  - With no flag it uses a new `auto` mode when any rendered task has a ticket, and `recent` when none does.
  - `auto` sorts ticketed tasks by id, then unticketed tasks by mtime. Explicit `id` still sorts unticketed tasks by folder name.
  - The `sort_tasks` docstring is updated.
  - Selftest section 6 is rewritten and gets a new fixture with no tickets.
- `plugins/sdlc-lite/skills/board/SKILL.md`: states the new default and that `recent`, `id` and `name` override it.
- `CLAUDE.md` Feed bullet: states the new default and that `--sort recent` restores recency.
- `.claude/agents/sdlc-lite-author.md`: unchanged. A grep found no mention of a sort default.

### Verification
- Step 1 (board.py and selftest), verifier L1: pass.
  - `board.py selftest` prints PASS.
  - Temp root with T-0003 (older), T-0002 (newer) and one unticketed task, no flag: order is T-0002, T-0003, then the unticketed task. A negative control confirms the check can fail: HEAD's board.py puts T-0003 first on the same fixture.
  - Fixture with no tickets: the no-flag output is byte-identical to the `--sort recent` output.
  - Explicit `--sort id|name|recent` order is unchanged.
  - `summary()` does not call `sort_tasks`, so the statusline is unaffected.
  - `--task <slug>` still renders only that task.
- Step 2 (docs), verifier L1: pass on the second attempt.
  - The first attempt failed. The new wording was correct but avoided the word "default", so the acceptance grep could not see it. `SKILL.md` also had a doubled period. Both were fixed.
  - The final grep shows the new default wording in both files, and neither file still says recency is the unconditional default.
  - `check.sh` exits 0: selftest, tickets selftest, board selftest, shellcheck and plugin validate all pass.
  - Negative control: in a throwaway worktree, forcing `mode = a.sort or 'recent'` makes `check.sh` fail with a board selftest FAIL.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `/board` with no `--sort` now orders by ticket id when any rendered task has a ticket, with unticketed tasks after it by recency. Without tickets it still orders by recency. `--sort recent` restores the old order. (T-0021)

## Follow-ups
None
