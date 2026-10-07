<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- docs/maintenance/sdlc-internals.md: in the `scripts/fanout.py` entry, added the merge-time overlap wait and its `waiting for lane <name> (overlap: <files>)` event, the report's `- Overlap:` lines (`- Overlap: none` when no lanes overlap), the dry run's `overlap (planned scope)` lines read from the scope allow-lists in the forms `steps.py widen` recognizes, and the remaining limit.
- plugins/sdlc-lite/scripts/fanout.py: added one docstring sentence on the same limit (an overlap first visible after a later lane has started its merge is not reordered), so the docstring and the doc entry agree.

## Checks
- `grep -qF -- '- Overlap:' docs/references/sdlc-internals.md`: exit 0
- `grep -qF 'overlap (planned scope)' docs/references/sdlc-internals.md`: exit 0
- `grep -qF 'waiting for lane' docs/references/sdlc-internals.md`: exit 0
- Scope guard, with `SDLC_BASE_SHA` read from the step's base-sha file: exit 0
- `git diff --check "$SDLC_BASE_SHA" -- <both files>`: exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. It printed "skip: shellcheck not installed", so shellcheck did not run.
- `python3 scripts/check-packaging.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: exit 0

## Notes
No gate was red, so the steps 1 and 2 code needed no fixes. `skills/fanout/SKILL.md` is unchanged.
