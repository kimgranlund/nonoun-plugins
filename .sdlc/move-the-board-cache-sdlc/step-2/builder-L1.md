<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: dropped `.sdlc/.board-state.json` from the ignore block. Replaced its bullet with a note giving the new cache location and marking the ignore line as legacy-only.
- `CLAUDE.md`: added a clause to the Feed line saying the "· changed" cache lives in a per-user cache dir outside the repo, that `SDLC_BOARD_STATE_DIR` overrides it, and that `/board` writes nothing into the tree.

## Checks
- `grep -rn "board-state" plugins .claude CLAUDE.md`, run before editing. No mentions in `.claude` or `skills/board/SKILL.md`. The remaining hits are in `board.py` (step 1) and a bench result file.
- `git diff -U0 | grep '^+' | grep -c '—'` printed 0.
- `plugins/sdlc-lite/scripts/check.sh` exited 0. The selftests, shellcheck and plugin validate all passed.
- I did not re-run the `board-state` grep after editing. The one edited skill file was the only one that mentioned it, and both mentions there are now the new location or the legacy note.

## Notes
None
