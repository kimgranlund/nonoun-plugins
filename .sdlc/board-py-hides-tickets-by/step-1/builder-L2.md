<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: added three visibility sets: `ALWAYS_HIDDEN`, `HIDDEN_WITHOUT_STEP_WORK` and `ALWAYS_SHOWN`, with a comment saying every new status must go in one of them.
- `plugins/sdlc-lite/scripts/board.py`: `belongs_on_board` now checks status against the sets instead of literal strings, so an unknown status stays visible.
- `plugins/sdlc-lite/scripts/board.py`: new `unclassified_statuses(known, sets=None)` reports three problems: a known status in no set, a status in two sets, and a set entry that is not a known status.
- `plugins/sdlc-lite/scripts/board.py`: new selftest section 6, placed just before `if misses:`, runs a consistency check, a negative control with `zz-new-status`, and a check that catches a status placed in two sets.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: printed `board selftest: PASS`, exit 0.
- `grep -n "'dropped'\|'done'" plugins/sdlc-lite/scripts/board.py`: the literals appear only on the set lines (190-191), the existing gate fixtures (371-377) and the new overlap fixture (469-471). None are in `belongs_on_board`.
- Negative control, run through the `python3 -c` helper call: returned `["status 'zz' is not classified in any board visibility set"]`.
- Negative control, run through the full selftest with `'zz'` added to `tickets.ENUMS['status']` in memory: printed FAIL naming `'zz'`, exit 1.
- `git diff --stat`: no edits to `tickets.py`, and the existing selftest expectations are untouched.
- `scripts/check.sh`, run from `plugins/sdlc-lite`: exit 0. The selftest, tickets selftest, board selftest, shellcheck and plugin validate all passed.

## Notes
- `git diff` also lists `.sdlc/board-py-hides-tickets-by/handoff.md` as changed. That edit was already there before this build started; I did not touch it.
- I did not edit `CLAUDE.md` or `skills/board/SKILL.md`, because what the board shows is unchanged.
- The selftest also fails if a set lists a status that is not in `tickets.ENUMS`. The handoff asked the helper to report that, and it passes today.
