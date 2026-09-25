<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `cmd_archive`, its `run()` dispatch, the `archive [--dry-run] [--numbered]` subparser, `archive` in the `main` kw tuple, the Usage and docstring lines, and six selftest `expect`s (done and dropped move while ready stays, dry run writes nothing, collision refuses, plain mode refuses, a second run reports nothing to archive, check passes after archive).

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: printed `tickets selftest: PASS`.
- Temp numbered root with `0001-a` (done), `0002-b` (dropped) and `0003-c` (ready), roadmap regenerated and `check` ok before starting:
  - `archive --dry-run`: exit 0, printed `0001-a -> .0001-a` and `0002-b -> .0002-b`, and `ls -A` was the same before and after.
  - `archive`: exit 0, left `.0001-a`, `.0002-b`, `0003-c`, `config` and `roadmap.md`.
  - `check`: exit 0 (`ok: 3 tickets, roadmap current`).
  - Second `archive`: printed `nothing to archive`.
- Plain root (no config, no flag), `archive`: exit 1, and the message names numbered mode.
- `tickets.py archive --help`: lists `--dry-run` and `--numbered`.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
- The collision refusal lists the dot folders that already exist and ends with `nothing written`.
- Problems found by `problems()` are reported with the suffix `nothing written: fix the problems above first`.
- I left the `tickets.py` line in CLAUDE.md and the `/ticket` skill docs alone because the handoff scoped this step to `tickets.py`. If no later step updates them, they now leave out `archive`.
