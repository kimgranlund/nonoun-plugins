<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints `board selftest: PASS`: pass. Evidence: `python3 plugins/sdlc-lite/scripts/board.py selftest` printed `board selftest: PASS`.
- Temp root with a task and the legacy file prints the hint, and prints none without the file: pass. Evidence: I diffed the render with and without the file. The only added lines are a blank line and `Note: legacy <tmp>/.board-state.json is no longer used (the board cache moved to a per-user dir); safe to delete.`
- `--summary` output is identical with and without the legacy file: pass. Evidence: `cmp` of the two summary outputs printed `summary-same`.
- Legacy file checksum unchanged and no new file created under the root: pass. Evidence: `shasum` before and after the render matched (`sum-same`). `find` on the root listed only `.board-state.json` and `t1/handoff.md`. `SDLC_BOARD_STATE_DIR` pointed to a separate temp dir, so the cache write did not land in the tree.
- Removing the hint code makes the selftest fail: pass. Evidence: in a throwaway worktree at HEAD with the changed `board.py` copied in, I replaced `legacy.exists()` with `False`. The selftest then printed `board selftest: FAIL ... legacy file gets the hint`. I removed the worktree afterwards.
- Docstring has one sentence about the hint: pass. Evidence: the diff adds it at `board.py` lines 26-27.
- `summary()` and the `--summary` path are untouched: pass. Evidence: the diff hunks are only in the docstring, `render()`, and the selftest.
- New selftest case covers the hint, unchanged bytes, and summary equality: pass. Evidence: case 5c in the diff has all three checks.

## Out of scope changes
None. `.sdlc/0031-legacy-sdlc-board-state-json/handoff.md` shows as modified and the task folder holds untracked artifacts, but those are task bookkeeping. The records the task constraints name (CLAUDE.md Feed entry, `sdlc-lite-author.md`, `skills/board/SKILL.md`) are not yet updated. The step's Do did not cover them, and a `step-2` folder exists, so I treated that as later work.

## For the next attempt
None
