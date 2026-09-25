<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: added `lanes(root)` and the `--lanes` flag in `main()`, which returns before the summary and render paths. Added selftest case 8 for `--lanes`, and a Usage line plus a Lanes paragraph to the docstring.
- `plugins/sdlc-lite/skills/board/SKILL.md`: `[--lanes]` added to argument-hint. Step 2 now says to pass `--lanes` for a "lanes" or "worktrees" ask. Added a rule for `--lanes`.
- `CLAUDE.md`: one sentence in the `scripts/board.py` bullet saying what `--lanes` does, that it exits 1 outside git, and that the default board is unchanged.

## Checks
- AC1 `board.py --lanes --root .sdlc | grep -q '^| Lane | Branch | Board |$'`: rc=0
- AC2 row count equals `git worktree list` lines + 1: rc=0 (2 worktrees, 3 `| ` lines)
- AC3 current branch cell present: rc=0
- AC4 `--root` set to a plain mktemp dir: rc=1 with `git` in stderr, and the criterion passes (rc=0)
- AC5 `--lanes` found in both SKILL.md and CLAUDE.md: rc=0
- AC6 (read): selftest case 8 builds a temp repo with `alpha` and `beta` worktrees. It asserts the header, exactly 3 data rows in the order repo/alpha/beta with their branch names, alpha shows `t planning` while beta and repo show `t not planned`, and a plain dir exits 1 with `git` in stderr.
- AC7 `board.py selftest`: `board selftest: PASS`, rc=0
- AC8 default board diff against the HEAD versions of board, tickets and order: no diff, rc=0
- AC9 `bash plugins/sdlc-lite/scripts/check.sh`: rc=0
- Negative control: a temp copy where every row reads the local root (`summary(here)`) makes the selftest FAIL on "alpha's Board reads its own running marker". The case catches a lane reading the wrong worktree.

## Notes
- The error goes to stderr as exactly `<root>: not inside a git work tree`. A root that git accepts but that sits outside the toplevel also exits 1 with that message.
- A worktree with no branch line shows `(detached <7-char sha>)` in the Branch cell. A non-`refs/heads/` ref is shown in full.
- `.sdlc/fanout-command/handoff.md` was already modified and the untracked `.sdlc/fanout-command/*` files were already there before this step. I did not touch them.
