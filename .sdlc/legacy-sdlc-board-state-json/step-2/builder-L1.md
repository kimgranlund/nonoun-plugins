<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/board/SKILL.md`: added a Rules bullet about the legacy `.board-state.json` hint line.
- `CLAUDE.md`: Feed entry now says `/board` prints a one-line hint when a legacy `.sdlc/.board-state.json` exists, and that the file is never deleted automatically and never appears in `--summary`.
- `.claude/agents/sdlc-lite-author.md`: no change, since it does not describe board output.

## Checks
- `grep -n "board-state" plugins/sdlc-lite/skills/board/SKILL.md CLAUDE.md` shows the new notes in both files.
- `plugins/sdlc-lite/scripts/check.sh` printed all `ok`/`PASS` lines: level tables, selftest, tickets selftest, board selftest, shellcheck, plugin validate. I did not see its exit code, because `PIPESTATUS` is empty under zsh, so I judged it from the output alone.

## Notes
None
