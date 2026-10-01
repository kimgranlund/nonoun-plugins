<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/maintenance/sdlc-internals.md: the `tickets.py` entry now covers the `ticket_root: tickets` root, the router block, the `.sdlc/CLAUDE.md` import, the `router:` stamp, and the `check` failures. The board paragraph now names the `.sdlc/tickets/` task dirs. The fanout entry gains the regular-lane follow-up, and the traces entry gains the ingest and reader facts.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: four Layout lines added (`.sdlc/AGENTS.md`, `.sdlc/CLAUDE.md`, `.sdlc/config`, `.sdlc/tickets/`), plus the `claimed_by:` and `router:` front matter lines.
- plugins/sdlc-lite/skills/ticket/SKILL.md: one new Rules bullet covering `ticket_root`, the router, the `check` failures, the upgrade step, and `claimed_by`.
- docs/ticket-stages/design.md: line 3 updated to version 0.2, Built: Option A and the opt-in root.
- docs/ticket-stages/README.md: line 3 updated.
- docs/README.md: the Ticket stages line updated.

## Checks
- All seven content grep criteria: exit 0 (the handoff-format loop printed no FAIL).
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0
- `python3 scripts/check-packaging.py`: exit 0
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0
- Scope guard (changed and untracked files against the allow-list): exit 0
- `git diff | grep '^+' | grep -c '—'`: 0 em dashes added.

## Notes
- The step introduced no em dash, but the check covered only the uncommitted diff, not text from earlier steps.
- In `docs/maintenance/sdlc-internals.md` the new `tickets.py` text is appended after the Templates sentence at the end of that entry.
