<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Added `PREFIX_RE`, `CONFIG_RE`, `config_numbered(root)` (reads `<root>/config`, skips blank and `#` lines, returns False if the file is absent) and `folder_name(slug, tid, numbered)`.
  - `stamp()` takes `numbered=False`. It computes the new id once (`tid`), works out the folder name from it, and runs the existence and `problems()` checks against that final name.
  - `cmd_new()` takes `numbered=False`. The mode is on if the flag or the config says so. In numbered mode it refuses a slug that already starts with `NNNN-` (the error names the double prefix and writes nothing), then creates `NNNN-<slug>` from the stamped id.
  - `run()` passes keyword args through to `new`, and `main()` has a `--numbered` flag on `new`.
  - The module docstring usage now includes `--numbered`.
  - Added selftest cases and moved the `snap` helper earlier so they can use it.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, rc=0.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` (from repo root): `ok: 21 tickets, roadmap current`, rc=0.
- `plugins/sdlc-lite/scripts/check.sh`: rc=0. The selftest, tickets selftest, board selftest, shellcheck and plugin validate all passed.
- CLI smoke test in a temp root: `new feature foo "Foo" --numbered` made `0001-foo`, `new feature bar` made `bar`, and `new feature 0009-baz --numbered` exited 1 with the double-prefix message and wrote nothing.
- Mutation checks: I ran broken copies of the script (placed next to `tickets.py` so the plugin templates resolve, then deleted) and checked that the selftest goes red for each break:
  - Folder never numbered: fails the `new --numbered`, config, and existing-`0003-gamma` cases.
  - Double-prefix guard removed: fails both double-prefix cases (flag and config).
  - Config ignored: fails the config case and the config double-prefix case.
  - Comment lines counted, or any `ticket_folders:` value turning numbered on: fails the "plain mode (other config)" control.
  - Guard also applied in plain mode: fails "plain mode still takes a digit-led slug as-is".
  - Always numbered, or the final-name existence check removed: the selftest crashes with a traceback rather than reporting a labeled failure. It still goes red.

## Notes
- New selftest labels:
  - `new --numbered: folder 0003-gamma with id T-0003`
  - `new with config ticket_folders: numbered: ...`
  - `new 0007-gamma in numbered mode (flag|config) refuses on the double prefix`
  - `new --numbered onto an existing 0003-gamma refuses`
  - `plain mode (no config|other config) new gives bare folder gamma`
  - `plain mode still takes a digit-led slug as-is`
- The "other config" fixture is `# ticket_folders: numbered\nticket_folders: plain\n`. It covers comments and other values, and the "no config" case covers a missing file.
- Plain mode keeps its checks and error text. `stamp()` now computes the id before its existence check, but on the already-clean ticket list it gets, that order change has no visible effect.
- One guard is new and runs only in numbered mode. If a template has no `id: T-0000` line, `stamp()` refuses because the folder cannot be numbered.
- For step 2: `stamp()` already takes `numbered` and checks against the final folder name. `cmd_close` still calls it without that argument and unpacks `(text, meta)`. Its follow-up folders can get their names from `folder_name(s, m['id'], numbered)`.
- The double-prefix guard is only in `cmd_new`, not in `stamp()`. A follow-up whose generated slug starts with four digits won't be refused by it.
