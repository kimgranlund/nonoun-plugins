<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/maintenance/sdlc-internals.md: added a `migrate-layout [--dry-run] [--rewrite-refs]` passage to the `scripts/tickets.py` entry, placed before the T-0262 paragraph. It covers the preconditions, the moves, the cite scan and rewrite rule (managed blocks and `docs/reports/` are never rewritten), the two config lines, the regeneration and closing `check`, and the `nothing to migrate` rerun.
- plugins/sdlc-lite/skills/ticket/SKILL.md: added `| migrate-layout [--dry-run] [--rewrite-refs]` to the argument-hint, and added an upgrade-note bullet to Rules just before the "Never hand-edit" bullet.

## Checks
- AC1 grep on sdlc-internals.md: pass
- AC2 argument-hint and bullet greps (`onboard.py setup`, `layout: flat`): pass
- (guard) `git diff --check $SDLC_BASE_SHA -- plugins/sdlc-lite docs/maintenance`: pass
- (guard) changed-files allowlist test: pass
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: rc 0
- (guard) `python3 scripts/check-packaging.py`: rc 0
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: rc 0
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: rc 0. It prints `ok: 309 tickets, roadmap current` and the expected flat-layout warning.

## Notes
- I took SDLC_BASE_SHA from `step-2/base-sha` because the environment variable was not set.
- I did not run `migrate-layout` on this repository.
- I did not touch the `ticket_root` bullet or the `.sdlc/roadmap.md` and `.sdlc/notes.md` path text; those are left to T-0207.
