<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: adds `state_path(root)`. The state file now lives at `$SDLC_BOARD_STATE_DIR`, or else `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state`, and is named by a 16-hex-character sha256 of the resolved root.
  - `render()` uses the new path and creates the directory inside the existing write `try`, which still ignores `OSError`.
  - Updated the docstring and `import hashlib`.
  - Updated the selftest:
    - It sets a temp state dir and restores the env var afterwards.
    - `clear_state()` replaces the two legacy unlinks.
    - New checks: no file is created under the root, "· changed" appears after a `.running` is added, and two roots get different state paths.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: `board selftest: PASS`.
- Manual run in a fresh temp git repo with `SDLC_BOARD_STATE_DIR` set, rendered twice: `git status --porcelain` was empty and `find .sdlc -name .board-state.json` printed nothing. After `touch .sdlc/t/planner-L1.running`, the third render showed `🟡 running · planner-L1 · changed`.
- `grep -n "board-state.json" board.py`: the only hits are in the selftest's negative assertion (lines 490-491). There is no `root / '.board-state.json'`.
- `grep -c '—' board.py`: 0.
- `scripts/check.sh`: every check passed, including shellcheck and plugin validate.

## Notes
- `summary()` and `statusline.sh` are untouched.
- The legacy `<root>/.board-state.json` is never read, written, or deleted. Existing ones stay on disk until removed by hand.
- The "no new file under root" selftest check ignores only the `planner-L1.running` file that the test itself adds.
