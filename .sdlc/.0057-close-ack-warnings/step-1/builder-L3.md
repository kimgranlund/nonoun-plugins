<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - `cmd_close(..., ack_warnings=None)` now has three early refusals: with `force`, with `reason`, and on empty or whitespace-only text.
  - At the warnings gate, it refuses when Warnings is None, and the open-warnings refusal names `--ack-warnings "<why>"` before `--force`.
  - The dry run prints an `ack warnings: <why>` line; `expect <digest>` stays the last line.
  - On a real close, the handoff gets a `## Closed` section: the date, `warnings acknowledged: <why>`, then each warnings line quoted with `> `. This is written before the numbered archive rename.
  - The success message ends with `; warnings acknowledged: <why>`.
  - Added the argparse `--ack-warnings TEXT` flag, `kw['ack_warnings']` in `main()`, and updated the `close` subparser help, the module docstring's Usage line, and its close paragraph.
  - Selftest: added a `--ack-warnings`-before-`--force` assert to case (b), and new cases (w1) to (w9) after the (u) negative controls.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: printed `tickets selftest: PASS`, rc 0.
- `grep -n "ack_warnings\|ack-warnings" plugins/sdlc-lite/scripts/tickets.py`: 46 lines. They cover the Usage line (5), the `cmd_close` parameter (524), the argparse flag, the case (b) assert, and the (w1) to (w9) cases.
- Negative control on a temp copy of the whole plugin dir (not the build tree), with the gate changed to `if not is_none(warnings) and not force:`: the selftest printed FAIL on (w1), (w2), (w7), (w8), (w9), rc 1. My first attempt copied only `scripts/` and crashed because the ticket templates were missing; that crash was not a check result.
- Manual temp-dir run of `close demo --ack-warnings "committed later"` (Warnings `nothing committed yet`, Follow-ups `- Add retry`):
  - exit 0 and front matter `status: done`
  - one new ticket `add-retry` with type idea, status proposed
  - handoff ends with `## Closed`, `2026-09-25: warnings acknowledged: committed later`, `> nothing committed yet`
- `close demo` with no flags: rc 1, and stderr names `--ack-warnings "<why>"` before `--force`.
- `close demo --ack-warnings x --force`: rc 1, file tree checksum unchanged.
- `close demo --ack-warnings "  "`: rc 1, file tree checksum unchanged.
- `python3 plugins/sdlc-lite/scripts/tickets.py close --help`: lists `--ack-warnings TEXT`.
- `plugins/sdlc-lite/scripts/check.sh`: rc 0, including shellcheck and plugin validate.

## Notes
- The quoted warnings come from the `section()` output, which is stripped, so blank lines before or after the section are left out. Blank lines inside the section become a bare `>`.
- The CLAUDE.md and `sdlc-lite-author` entries describing `tickets.py close` do not mention `--ack-warnings` yet. That was outside this step; step 2 probably covers it.
