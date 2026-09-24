<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: `argument-hint` now has `[--numbered]` on `new`, `close` and `check`. Added one rule bullet under `Rules:`.
- `CLAUDE.md`: added one sentence to the `scripts/tickets.py` bullet in Layout.

## Checks
- `grep -n numbered plugins/sdlc-lite/skills/ticket/SKILL.md`: matches the `argument-hint` line and the rule bullet.
- `grep -c "ticket_folders: numbered" CLAUDE.md`: 1.
- `git diff --stat HEAD -- .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/scripts/board.py`: empty.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: exit 0.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0.

## Notes
None
