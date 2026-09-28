<!-- role=builder level=L1 model=sonnet effort=low -->
All three acceptance criteria pass.

## Status
done

## Changes
- plugins/sdlc-lite/skills/board/SKILL.md: description and rules now describe the optional ID/Ticket columns and when they appear
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: rewrote the front-matter line to state board.py reads id/status for display only via tickets.py, without validating or writing front matter

## Checks
- `grep -n "does not parse" plugins/sdlc-lite/skills/handoff-format/SKILL.md` — no match (exit 1), unqualified claim removed
- `grep -n "Task, Step, Status" plugins/sdlc-lite/skills/board/SKILL.md` — matches, surrounding text now documents ID/Ticket columns
- `plugins/sdlc-lite/scripts/check.sh` — exit 0 (role levels, selftest, tickets selftest, board selftest, shellcheck, plugin validate all ok)

## Notes
None
