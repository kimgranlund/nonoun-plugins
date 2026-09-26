<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Added `worktree_pairs(root)`, which returns (worktree dir, root) pairs. `worktree_roots` now wraps it, and its callers behave the same.
  - In the `cmd_close` dry run, added `other_opens` lines of the form `open T-NNNN <title> [<slug>] (worktree <name>)`. They come after the local open lines and before the rename and ack lines. The digest is unchanged.
  - Updated the module docstring and the `--dry-run` help.
  - Added two selftest cases: a fresh sub-repo worktree case (fixture worktree `wtdr`) and an outside-git case on `solo`.

## Checks
- AC1, the scratch repo with worktrees wt and wt2: exit 0.
- AC2 (guard), outside git: exit 0.
- `grep -qF '(worktree <name>)'`: exit 0.
- `grep -q "(worktree wt"`: exit 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- Observable check, on a scratch copy inside the scripts dir with `+ other_opens` removed: `selftest` exited 1 and named the case "worktree dry-run: other-worktree gamma listed once…". The copy is deleted.
- `scripts/check.sh`: the tail shows run selftest PASS, hook selftest PASS, shellcheck ok, plugin validate ok.

## Notes
- The selftest's other-worktree fixture is named `wtdr`, not `drwt`, so that the literal `(worktree wt` required by AC4 appears in the file.
- A scratch copy placed in `/tmp` cannot import `order`, so the Observable check has to run on a copy placed next to `tickets.py`.
