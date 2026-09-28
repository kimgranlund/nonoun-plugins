<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added one selftest case, `worktree dry-run with follow-ups:`, right after the existing `worktree dry-run:` expect. It adds 10 lines and removes none.

## Checks
- `grep -c "worktree dry-run with follow-ups" plugins/sdlc-lite/scripts/tickets.py`: prints 1.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: exit 0, prints `tickets selftest: PASS`.
- Mutant check: I copied the whole plugin dir to `$SDLC_TMP_WORKTREES/mutp` and replaced `[f'expect {digest}']` with `[f'expect {follow_digest(items + opens + other_opens)}']`. `selftest` on the copy exits 1, and stderr lists `worktree dry-run with follow-ups: ...` among the misses.
- `git diff HEAD --stat -- plugins/sdlc-lite/scripts`: only `tickets.py` is listed (10 insertions). `git diff HEAD -U0` shows no removed lines.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check`: exit 0 (`ok: 126 tickets, roadmap current`).
- `plugins/sdlc-lite/scripts/check.sh`: exit 0 on the current tree, and exit 0 in a detached HEAD worktree at `$SDLC_TMP_WORKTREES/base`, which I removed afterwards. No new failures.

## Notes
- The mutant check does not work if you copy `tickets.py` alone to a temp dir. It needs `order.py` next to it and the plugin's `skills/ticket/templates`, so without them it crashes before any case runs. Copy the whole `plugins/sdlc-lite` dir, as I did.
- The new case matches the fixture's exact line `open T-0004 Gamma [gamma] (worktree wtdr)`, the same id the existing case already expects.
