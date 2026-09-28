## Task goal
Rendering `/board` (board.py) never creates or modifies any file inside the repo's working tree, in any project, whether or not it ignores `.sdlc/.board-state.json`, while the "· changed" markers keep working between renders.

Constraints: board table output unchanged; `--summary` still writes no state; stdlib only; no em dashes in edited files.

## Step 2: Update docs and run the full check
level: L1
### Do
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, lines 27 to 39:
  - Drop `.sdlc/.board-state.json` from the recommended ignore block.
  - Replace the bullet with a note that the board cache now lives in `${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state/`, outside the repo, and that the ignore line only matters for older versions that wrote it in `.sdlc/`.
- Repo root `CLAUDE.md`, Feed line (line 23): add a short clause that the "· changed" cache lives in a per-user cache dir outside the repo (`SDLC_BOARD_STATE_DIR` overrides it), so `/board` writes nothing into the tree.
- Leave the root `.gitignore` line as is.
- If `.claude/agents/sdlc-lite-author.md` or `skills/board/SKILL.md` mentions the cache, update it too: `grep -rn "board-state" plugins .claude CLAUDE.md`.
- No em dashes in edited text.
### Acceptance criteria
- `grep -rn "board-state" plugins/sdlc-lite/skills CLAUDE.md` shows only text describing the new location or the legacy note.
- The ignore code block in `handoff-format/SKILL.md` no longer lists `.sdlc/.board-state.json`.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The validate warning about CLAUDE.md is expected.
- `git diff -U0 | grep '^+' | grep -c '—'` prints 0.

## Planner risks
- `statusline.sh` may write state somewhere. The read shows only `board.py --summary`, which writes none, so no edit is planned. Step 1's acceptance check on `git status` covers renders but not the statusline path.
- A selftest subprocess that inherits a stale `SDLC_BOARD_STATE_DIR` could leak "· changed" markers into output comparisons. The selftest must clear the state dir between the compared runs.
- `~/.cache` may be unwritable. The write failure is ignored, so "· changed" silently stops working.
