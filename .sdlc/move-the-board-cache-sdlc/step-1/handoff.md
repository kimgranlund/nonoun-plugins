## Task goal
Rendering `/board` (board.py) never creates or modifies any file inside the repo's working tree, in any project, whether or not it ignores `.sdlc/.board-state.json`, while the "· changed" markers keep working between renders.

Constraints: board table output unchanged; `--summary` still writes no state; stdlib only; no em dashes in edited files.

## Step 1: Move the board state file out of the tree
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Add `state_path(root)`. It returns `<dir>/<key>.json`.
  - `<dir>` is `$SDLC_BOARD_STATE_DIR` if set, else `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state`.
  - `<key>` is the sha256 hex of `str(root.resolve())`, truncated. Import `hashlib`.
- In `render()`, use `state_path(root)` instead of `root / '.board-state.json'`.
- Create the state dir on demand with `mkdir(parents=True, exist_ok=True)` inside the existing write `try`. Widen that `except` so it still ignores `OSError`.
- Never read, write, or delete the legacy `<root>/.board-state.json`.
- Leave `--summary` and `statusline.sh` untouched. `summary()` must not call `state_path`.
- Update the module docstring line about "· changed" to name the new location and `SDLC_BOARD_STATE_DIR`.
- Update the selftest:
  - At the start of `selftest()`, inside the tmp block, set `os.environ['SDLC_BOARD_STATE_DIR']` to a temp dir outside every fixture root. Subprocess runs inherit it.
  - Replace the two `(plain / '.board-state.json').unlink(...)` calls with removing the files in that state dir.
  - Add a check that renders a fixture root twice and then asserts no `.board-state.json`, and no new file at all, exists under the root.
  - Add a check that a row whose status changed between two renders shows "· changed" on the second render. Do this by adding a `builder-L1.md` or `.running` file between the renders.
  - Add a check that two different roots get different state paths.
- No em dashes in edited files.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS`.
- Manual run:
  - `d=$(mktemp -d); cd $d; git init -q; mkdir -p .sdlc/t; printf '## Goal\nx\n' > .sdlc/t/handoff.md; git add -A; git -c user.name=a -c user.email=a@a commit -qm i`
  - Run `SDLC_BOARD_STATE_DIR=$(mktemp -d) python3 <repo>/plugins/sdlc-lite/scripts/board.py --root .sdlc` twice.
  - `git status --porcelain` is empty, and `find .sdlc -name '.board-state.json'` prints nothing.
- Add a status change between the two renders, for example `touch .sdlc/t/planner-L1.running`. The second render then shows `· changed` on that row.
- `grep -n "board-state.json" plugins/sdlc-lite/scripts/board.py` shows no use of `root / '.board-state.json'`.
- `grep -c '—' plugins/sdlc-lite/scripts/board.py` is 0.

## Planner risks
- `statusline.sh` may write state somewhere. The read shows only `board.py --summary`, which writes none, so no edit is planned. Step 1's acceptance check on `git status` covers renders but not the statusline path.
- A selftest subprocess that inherits a stale `SDLC_BOARD_STATE_DIR` could leak "· changed" markers into output comparisons. The selftest must clear the state dir between the compared runs.
- `~/.cache` may be unwritable. The write failure is ignored, so "· changed" silently stops working.
