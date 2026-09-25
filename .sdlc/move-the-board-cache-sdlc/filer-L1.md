<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0019: Move the board cache out of the working tree

## PR body
### Summary
`/board` (board.py) no longer writes `.sdlc/.board-state.json` into the repo. The "· changed" cache now lives in a per-user cache dir outside the working tree, so a render never dirties a repo, including repos without the recommended ignore lines. Follow-up from T-0018.

### Changes
- `plugins/sdlc-lite/scripts/board.py`:
  - New `state_path(root)`. The path is `$SDLC_BOARD_STATE_DIR`, or else `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state/<key>.json`. `<key>` is the first 16 hex characters of the sha256 of the resolved root.
  - `render()` uses the new path and creates the dir on demand inside the existing write `try`. `OSError` is still ignored.
  - The legacy `<root>/.board-state.json` is never read, written, or deleted.
  - `summary()` is unchanged and still writes no state.
  - The docstring is updated.
  - Selftest:
    - It isolates state in a temp `SDLC_BOARD_STATE_DIR` and restores the env var afterwards.
    - It clears the state dir between compared runs.
    - New checks: a render creates no file under the root, "· changed" appears after a status change, and two roots get distinct state paths.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: drops `.sdlc/.board-state.json` from the recommended ignore block. A note now gives the new cache location and says the ignore line only matters for older versions.
- `CLAUDE.md`: the Feed line now says the cache lives in a per-user cache dir outside the repo, that `SDLC_BOARD_STATE_DIR` overrides it, and that `/board` writes nothing into the tree.
- `statusline.sh` and the root `.gitignore` are unchanged.

### Verification
- Step 1 (board.py): the verifier passed it.
  - `board.py selftest` prints PASS.
  - Fixture git repo, rendered twice: `git status --porcelain` was empty and no `.board-state.json` was found.
  - After `touch .sdlc/t/planner-L1.running`, the second render showed `🟡 running · planner-L1 · changed`.
  - The pre-change code, run in a throwaway worktree, did create `.sdlc/.board-state.json` on the same fixture. So the check can fail.
  - `--summary` left a fresh state dir empty.
  - No em dashes in board.py.
- Step 2 (docs): the verifier passed it.
  - At HEAD, the ignore block listed `.board-state.json`. It no longer does.
  - The CLAUDE.md clause is present.
  - `scripts/check.sh` exited 0: all selftests, shellcheck, and plugin validate passed.
  - The em-dash count in the diff is 0, and the verifier confirmed with a probe line that this count can come out nonzero.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Changed: `/board` keeps its "· changed" cache in `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state/` instead of `.sdlc/.board-state.json`, so rendering the board never writes into the repo. Set `SDLC_BOARD_STATE_DIR` to override the location. Old `.sdlc/.board-state.json` files are ignored and can be deleted by hand.

## Follow-ups
- Board "· changed" markers silently stop working when the per-user cache dir is unwritable, because write failures are ignored; consider a visible hint.
- Legacy `.sdlc/.board-state.json` files stay in existing projects after the T-0019 cache move; consider a one-line cleanup note or a /board hint when one is found.
