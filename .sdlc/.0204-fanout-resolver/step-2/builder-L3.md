<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: `planned_scope` now builds the ticket folder path from `tickets.ticket_dir(pathlib.Path(root)) / slug`, and its docstring says so. The `ticket_root lane` selftest fixture gained tickets `y` (T-0002) and `z` (T-0003) under `.sdlc/tickets/`, each with a step-1 scope criterion that allow-lists `shared.txt`. A new dry run `a=T-0002 b=T-0003` must print `overlap (planned scope): a T-0002 and b T-0003: shared.txt` and no `not planned` line.
- docs/maintenance/sdlc-internals.md: the fanout "Regular lanes follow `ticket_root`" sentence now also says the dry run's planned-scope overlap check reads step handoffs from that dir.

## Checks
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: `fanout selftest: PASS`, rc=0.
- Negative control: I put back the old line `tdir = pathlib.Path(root) / slug` (nothing else changed) and ran the selftest. rc=1, and the only miss was the new case `ticket_root lane: planned scopes under .sdlc/tickets print the a/b shared.txt pair line`. I then restored the fix and grep confirmed the line at fanout.py:487.
- `grep -q "ticket_dir" plugins/sdlc-lite/scripts/fanout.py`: rc=0.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 19 role levels, 9 agents checked`, rc=0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: `Codex agent definitions verified`, rc=0.
- `python3 scripts/check-packaging.py`: `PASS: catalog parity, identity, skill routes, hook isolation and context links`, rc=0.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. It printed `skip: shellcheck not installed`, so the shellcheck leg did not run on this host.
- `git diff --check main -- plugins docs`: rc=0, no output.

## Notes
- The negative control replaced only the routing line, not the whole pre-change file. The new selftest assertions stayed in place.
- During the control, the backup copy of fanout.py and the check.sh log went to plain files in `/tmp`, not worktrees. Both were removed.
- Untracked `.sdlc/0204-fanout-resolver/step-2/base-sha` and `builder-L3.attempt.json` are run records written by run.sh. Nothing was committed.
