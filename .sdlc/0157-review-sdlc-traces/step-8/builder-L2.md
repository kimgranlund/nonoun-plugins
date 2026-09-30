<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/tickets.py` (new): `read(root)` returns `by_slug`, `problems`, `external` and `notes`, all taken from `scripts/tickets.py`.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added two `tickets` family cases. The first covers slug to id and status plus the duplicate-id problem, and also checks the notes flag. The second checks that a root with no config gives `external` empty, and has a positive control where a config does set it.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets`: 2 ok, PASS.
- `... selftest -k tickets | grep -q '^ok: tickets: '`: exit 0.
- The grep for `tickets.load` and `tickets.problems` in `sources/tickets.py`: exit 0.
- The scope guard, with `SDLC_BASE_SHA` read from `step-8/base-sha`: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (full): PASS.

## Notes
- `read(root)` accepts either a string or a Path; it converts the root to a Path because `tickets.load` needs one.
- The fixture has no config file, so `tickets.problems` runs with numbered mode off. That is why `0003-c` produces only the duplicate-id line and no folder-prefix mismatch.
