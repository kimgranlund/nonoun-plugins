<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints `board selftest: PASS`: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/board.py selftest` and it printed `board selftest: PASS`.
- Manual run, two renders with `SDLC_BOARD_STATE_DIR` set: pass. Evidence: in a fresh git repo I rendered twice. `git status --porcelain` was empty and `find .sdlc -name .board-state.json` printed nothing. The state dir held `a4db56d867fa3b78.json`.
- The check can go red: pass. Evidence: a throwaway worktree at HEAD, the pre-change code, created `.sdlc/.board-state.json` in the same fixture. The new code does not.
- `touch .sdlc/t/planner-L1.running` between renders shows `· changed`: pass. Evidence: the second render printed `| t | task | 🟡 running · planner-L1 · changed | 0 |`.
- No use of `root / '.board-state.json'`: pass. Evidence: `grep -n "board-state.json"` matched only the selftest assertion at lines 490 and 491. `state_path()` is used in `render()`.
- No em dashes: pass. Evidence: `grep -c '—' board.py` printed 0.
- `--summary` writes no state: pass. Evidence: a run with a fresh state dir printed `t planning` and left the dir empty (`ls -A` showed nothing).
- Other Do items: pass. Evidence from the diff:
  - `state_path` uses the sha256 of `root.resolve()`, truncated to 16 characters.
  - The `mkdir` sits inside the write `try`, which still catches `OSError`.
  - The docstring is updated.
  - The selftest sets and restores `SDLC_BOARD_STATE_DIR`, clears the state dir between compared runs, and adds checks for no files created, `· changed` appearing, and distinct paths for different roots.
  - `statusline.sh` is untouched.

## Out of scope changes
None. The diff touches only `plugins/sdlc-lite/scripts/board.py`. The other changes are the task's own `.sdlc` bookkeeping.

## For the next attempt
None
