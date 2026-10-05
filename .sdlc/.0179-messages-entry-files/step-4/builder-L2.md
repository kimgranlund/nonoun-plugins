<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/maintenance/sdlc-internals.md: added the given text to the end of the `scripts/messages.py` entry and to the end of the `scripts/tickets.py` entry.
- docs/ticket-stages/design.md: replaced line 3 (the version line) and the pending sentence in the Message bus Status paragraph.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: extended the `.sdlc/messages/` layout row on line 36.

## Checks
- c1, the sdlc-internals grep chain: exit 0
- c2, design.md has the link and the pending sentence is gone: exit 0
- c3, the handoff-format messages row contains AGENTS.md: exit 0
- c4 (guard), no em dash in added lines: exit 0
- c5 (guard), git diff --check: exit 0
- c6 (guard), scope allow-list: exit 0

## Notes
`SDLC_BASE_SHA` was taken from the env, or from step-4/base-sha if the env had none. The link target docs/reports/messages-live-run.md exists.
