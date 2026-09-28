<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: `render()` now adds a blank line and a hint line when `<root>/.board-state.json` exists. The hint names the real path and says "safe to delete". The file is only checked for existence, never changed. `summary()` and `--summary` are untouched. The docstring has one new sentence about the hint. Selftest case 5c is new: no hint without the file, a hint with it, the file's bytes unchanged, and `summary()` identical either way.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: `board selftest: PASS`.
- Temp root with one task, run from the CLI (`SDLC_BOARD_STATE_DIR` pointed to a temp dir):
  - Without the legacy file, `board.py --root` printed 0 "safe to delete" lines.
  - With the file, it printed `Note: legacy <tmp>/.board-state.json is no longer used (the board cache moved to a per-user dir); safe to delete.`
  - `--summary` output was the same with and without the file.
  - The file's `shasum` was the same before and after the render.
  - `find` on the root showed no new files.
- Bite test: I replaced the `legacy.exists()` condition with `False` and the selftest failed with "legacy file gets the hint". I then restored the original file.
- `plugins/sdlc-lite/scripts/check.sh`: selftest, tickets selftest, board selftest, shellcheck and plugin validate all passed.

## Notes
- The step's Do covered only board.py. I did not update the records the task constraints name: the CLAUDE.md Feed entry, `.claude/agents/sdlc-lite-author.md` and `skills/board/SKILL.md`. Whether they now need a line about the hint is left to the planner or verifier.
- The hint sits after the footer, so no existing trailing-text assertion broke.
