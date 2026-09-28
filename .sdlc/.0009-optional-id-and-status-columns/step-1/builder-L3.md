<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: imports `tickets` and adds `ticket_of()`, which reads `id`/`status` with `tickets.parse` and treats any read or parse exception as no front matter. The table render moved from `main()` into `render()`. `ID`/`Ticket` columns appear only when a rendered task (after the `--task` filter) has front matter. Added a `selftest` subcommand and updated the docstring. `summary()` and the `.board-state.json` key format are unchanged.
- `plugins/sdlc-lite/scripts/check.sh`: added `python3 "$root/scripts/board.py" selftest || fail=1` after the tickets selftest, and updated the header comment to name it.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: prints `board selftest: PASS`, rc=0.
- Bite controls (each on a copy, original restored afterwards):
  - Gate forced to `with_ticket = True`: FAIL, rc=1. Both "4-column byte-for-byte" checks missed.
  - Gate forced to `with_ticket = False`: FAIL, rc=1. The 6-column header check and both row checks missed.
  - Exception guard narrowed to `except KeyError`: FAIL, rc=1. The mixed render crashed on the undecodable `handoff.md` fixture.
  - One multi-line sed mutation did not apply. My guard reported it, and the Python-applied mutation above replaced it.
- `python3 plugins/sdlc-lite/scripts/board.py` at the repo root: shows the 6-column header, and the rows include `| T-0009 | optional-id-and-status-columns | ready | ...`. rc=0.
- `python3 plugins/sdlc-lite/scripts/board.py --root plugins/sdlc-lite/bench/results`: `diff` and `cmp` against `baseline-bench-board.txt` are both identical.
- `python3 plugins/sdlc-lite/scripts/board.py --summary`: prints `optional-id-and-status-columns 5% (0/2)`. The baseline shows `... not planned`. Both are existing `summary()` formats. The task has been planned since the baseline was captured, and `summary()` was not changed.
- `plugins/sdlc-lite/scripts/check.sh`: every line ok (check.py, coverage selftest, tickets selftest, board selftest, shellcheck, plugin validate), rc=0.

## Notes
- Selftest fixtures:
  - A handoff with no front matter.
  - A ticket handoff.
  - An undecodable-bytes `handoff.md`, which covers the file IO exception path.
  - A run with `tickets.parse` monkeypatched to raise, which covers the parse exception path.
  - A `summary()` call on a ticketed task.
- A front matter block with no `id`/`status` still turns the 6-column layout on and shows empty cells, because the gate is "front matter present", not "has an id".
- `.sdlc/0009-optional-id-and-status-columns/handoff.md` already showed as modified in git before I started. I did not touch it.
- Updating the skill docs (`skills/board/SKILL.md`, `skills/handoff-format/SKILL.md` line 45) is step 2 and was not done here.
