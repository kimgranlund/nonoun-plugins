<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - New `--rewrite-refs` flag, added to argparse, the usage line and the docstring.
  - ctx now carries `rewrite_refs` and `numbered`.
  - The dry-run plan prints one `close:` line, picked for the mode.
  - The flag is passed through to `tickets.py close`. Without it, a refusal that names the flag gets the added hint.
  - The `close <id>` commit stages `rel` plus every path outside it whose `git status --porcelain` entry changed during the close. A new `porcelain()` helper takes the snapshot.
  - New selftest case 4 covers numbered mode, and the selftest docstring is updated to match.

## Checks
Each acceptance criterion command was run from the worktree root. All exited 0:
- `fanout.py run --help | grep -q -- --rewrite-refs`: 0
- Close with the flag (the rewrite lands in the close commit, worktree clean): 0
- Close without the flag (refused, names the flag, nothing rewritten): 0
- Dry run with the flag: 0
- Dry run without the flag in numbered mode: 0
- `grep -q "ticket_folders: numbered" fanout.py`: 0
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/tickets.py`: 0
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: 0

## Notes
- The step is scoped to `fanout.py`, so I did not change `skills/fanout/SKILL.md`, `CLAUDE.md`, or `sdlc-lite-author.md`. The task-level done-conditions for those files belong to a later step.
- The staging diff compares (status, path) pairs. A file that was already dirty before the close and whose status code stays the same afterwards would not be staged. That cannot happen in the integration worktree, which is clean after the gates pass.
