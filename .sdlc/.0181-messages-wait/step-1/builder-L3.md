<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/messages.py`: added the `wait` subcommand (`cmd_wait` plus a `wait_ready` helper that skips invalid files), registered it in `COMMANDS`, and added a `wait` subparser right after `count`. Also added the seven selftest cases with the exact labels, appended to `SELFTEST_CASES`, and updated the module docstring (usage, exit 3, a commands entry, the layout sentence, the schema paragraph) and the subparser metavar.

## Checks
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: printed `messages selftest: PASS`, with `ok:` for all seven new `wait` cases and every existing case.
- All 10 acceptance-criteria commands, run verbatim under bash from the repo root with `SDLC_BASE_SHA=bc21b53c` (the same as HEAD): all PASS.
- `git diff --check`: clean.
- `python3 --version`: 3.9.6, which is the interpreter that ran all the above.

## Notes
- Validation runs in the order the handoff gives: receiver, then timeout, then interval. Timeout and interval are parsed as strings and must fullmatch `[0-9]{1,9}` (a module constant `WAIT_NUM_RE`).
- `wait_ready` catches `Refuse` for each file, so a malformed file in `new/<receiver>/` neither wakes a waiter nor makes `wait` exit 1. `count` is unchanged.
- The literal `ready = wait_ready(mbox, receiver)` appears exactly once in the source, inside `cmd_wait`. The control case builds the anchor from two pieces and asserts it occurs once.
- The control case (`wait: a claiming wait is caught`) passes, so the patched copy that claims the message failed at check (d) (`wait changed the mailbox`) and not at any earlier check.
- The layout sentence in the docstring now reads "list, count, wait, and expire on a missing mailbox create nothing; list, count, and expire exit 0". It no longer says all four exit 0, because `wait` on a missing mailbox exits 3 at its timeout.
- `ENTRY_TEMPLATE` is unchanged, as the handoff requires, so `case_entry_parses` still expects the old set of subcommands. Step 2 changes both.
