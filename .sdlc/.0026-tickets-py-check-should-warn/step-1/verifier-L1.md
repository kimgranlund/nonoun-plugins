<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest prints PASS: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS`.
- Red-then-green, revert the `cmd_check` warning and the `cmd_close` persist: pass. Evidence: I ran two copies of the script with one revert each. Without the close persist, selftest FAILed with `(j) close --numbered writes config with the numbered line`. Without the check warning, it FAILed with `all-numbered folders, no config: check warns and exits 0`. The working-tree file was untouched and its selftest is green.
- Temp root with `0001-a`, `0002-b`, roadmap, no config: pass. Evidence: I built it with `new --numbered` and removed the config. `check` printed `ok: 2 tickets, roadmap current` and then a `warning: every ticket folder has an NNNN- prefix but .../config lacks 'ticket_folders: numbered'...` line, with rc=0. After I added `ticket_folders: numbered` to the config, it printed only the `ok:` line with rc=0.
- Plain-slug fixture: pass. Evidence: two tickets created with plain `new`. `check` printed only `ok: 2 tickets, roadmap current`, rc=0. The selftest also covers the mixed and empty-root cases with no warning.
- `close <slug> --numbered` persists the config: pass. Evidence: selftest case `(j)` checks that rc=0, `<root>/config` is a file, and `config_numbered(root)` holds, using a filer fixture. The `cmd_close` diff puts `ensure_numbered_config` after `write_roadmap`, on the success path only. Selftest `(j)` also passes for a refused close (rc 1, no config, snapshot unchanged), and a plain close writes no config. Follow-up files are unchanged. The builder's run showed rc=0 and follow-up `0002-do-a-thing`; I did not re-run that.
- Usage docstring updated: pass. Evidence: the diff shows both the `check` and `close` lines changed.

## Out of scope changes
None. `plugins/sdlc-lite/scripts/tickets.py` is the only plugin file modified. The other changes are `.sdlc` task artifacts.

## For the next attempt
None
