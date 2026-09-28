<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `cmd_close` saves `flag` and calls `ensure_numbered_config` only on the success path.
  - `cmd_check` appends a warning line to `out` when not in numbered mode and every ticket folder has an NNNN- prefix.
  - The usage docstring's `close` and `check` lines are updated.
  - New selftest cases:
    - check warns on all-numbered folders with no config.
    - No warning with the config line, with plain slugs, with mixed folders, or with an empty root.
    - (i) A plain close writes no config.
    - (j) `close --numbered` writes the config line.
    - (j) A refused `close --numbered` writes nothing.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- Red-then-green:
  - I disabled the check warning and the persist guard with sed. Selftest FAILed and named "all-numbered folders, no config: check warns" and "(j) close --numbered writes config".
  - The same sed line also disabled `cmd_new`'s `if flag:`, so the existing new --numbered cases failed too.
  - I restored the file from backup and selftest PASSed again.
- Temp root with `0001-a`, `0002-b`, a roadmap and no config: `check` exited 0 and printed a `warning:` line. After I added `ticket_folders: numbered` to the config, it printed only the `ok:` line and exited 0.
- Plain-slug fixture: `check` printed only `ok: 1 tickets, roadmap current` and exited 0.
- `close a --numbered` with a filer file: exited 0 and created follow-up `0002-do-a-thing`. `config` contains `ticket_folders: numbered`.
- `plugins/sdlc-lite/scripts/check.sh`: all green (role levels, selftests, shellcheck, plugin validate).

## Notes
- The warning goes on a second line of stdout, so `check`'s output is no longer a single line when it fires. Existing exact-match asserts still pass because none of their fixtures are all-numbered.
- The handoff did not ask for changes to the argparse `--numbered` help text for `close`, so I left it as it was.
