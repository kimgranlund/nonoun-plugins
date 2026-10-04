<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/tickets.py: adds the `skip_section`, `skip_missing`, `skip_line` and `skip_problems` helpers. `cmd_check` runs the guard after the router-problems check. `cmd_close` refuses right after the existing `status == 'done'` refusal, on every close path. Adds the `check` and `close` docstring sentences and the `(skips)` selftest block with all 11 cases from the handoff.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: the Layout `skips.md` line now also covers `## Skipped` and gives the entry format.
- docs/maintenance/sdlc-internals.md: one sentence in the `scripts/tickets.py` section on the `## Skipped` guard and the no-lane-record exemption.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS (rc 0).
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: `ok: 214 tickets, roadmap current` (rc 0). Tickets closed before the guard stay exempt.
- I ran the 3 fixture `check` criteria (fix lane missing planner and filer, both guards, lean lane missing the step 1 verifier): rc 0 each.
- I ran the 3 fixture `close` criteria (`--reason` refusal, filer-path refusal, `--reason` success guard): rc 0 each.
- The 3 grep criteria (`(skips)` in tickets.py, `## Skipped` in handoff-format SKILL.md and in sdlc-internals.md): rc 0 each.
- The scope criterion, with `SDLC_BASE_SHA` taken from step-1/base-sha: rc 0.
- `git diff --check`: clean.

## Notes
None
