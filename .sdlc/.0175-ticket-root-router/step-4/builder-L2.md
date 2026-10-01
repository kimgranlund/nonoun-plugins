<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: added `task_dirs(root)`, which lists the dirs holding a `handoff.md` directly under `root`. When `tickets.ticket_dir(root)` differs from `root`, it also lists those directly under the ticket dir. On `tickets.Fail` it lists `root` only. `main` and `summary` now use it, and `lanes` gets it through `summary`. The docstring gains the `ticket_root: tickets` case. Selftest gains case 9: a ticket under `tickets/` and a plain root task both render, `--task` finds the ticket, and `--summary` names it. Its negative controls cover no config line and an unsupported `ticket_root: work`.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: PASS
- Criterion 1 (ticket and root task render, `--task 0001-a`): PASS
- Criterion 2 (`--summary` = `0001-a 0% (0/1)`): PASS
- Criterion 3 (copied scripts: selftest passes in the unmodified copy and fails when `ticket_dir` is stubbed to return `root`): PASS
- Guard (no config: `tickets/0001-a` not listed): PASS
- Guard (`ticket_root: work`: root task still listed): PASS
- Guard (board selftest): PASS
- Guard (diff scope limited to `tickets.py` and `board.py`): PASS
- `git diff --check`: clean

## Notes
The new selftest case gives its board subprocesses their own `SDLC_BOARD_STATE_DIR` under the case's temp dir. This is needed because the case runs after the selftest restores the original environment, so without it the case would write board state into the user's cache.
