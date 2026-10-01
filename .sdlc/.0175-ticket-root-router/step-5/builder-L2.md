<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/traces/ingest.py: split the old listing out into `_names(d)`. `task_dirs` now leaves `tickets` out and appends `tickets/<name>` entries when `tickets.ticket_dir` returns a dir other than the root. On `tickets.Fail` it lists the root only. Added the `pathlib` import and updated the "handoff dirs" docstring.
- plugins/sdlc-lite/scripts/traces/sources/tickets.py: `read()` now loads tickets from `tickets.ticket_dir(root)`, falling back to `root` on `Fail`. `problems`, `external` and `notes` still read from `root`. Updated the `by_slug` docstring line.
- plugins/sdlc-lite/scripts/traces/selftest.py: added three `tickets:` cases: task_dirs under the ticket root, the reader's by_slug read from `tickets/`, and the negative control where `tickets` stays a plain dir name when config has no `ticket_root` line.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets`: PASS, including the 3 new cases.
- AC1 (task_dirs and by_slug fixture one-liner): exit 0.
- AC2 (the selftest passes on the real copy and fails on the copy where `ticket_dir` is mutated to return the root): exit 0.
- Guard: with no config, task_dirs returns `['0001-a', 'tickets']`: exit 0.
- Guard: full `python3 plugins/sdlc-lite/scripts/traces.py selftest`: PASS.
- Guard: no files changed outside the allowed list: exit 0.
- `git diff --check`: clean.

## Notes
None
