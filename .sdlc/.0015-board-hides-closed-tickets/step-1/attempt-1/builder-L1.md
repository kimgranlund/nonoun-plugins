<!-- role=builder level=L1 model=sonnet effort=low -->
All checks pass. Temp files are in /tmp, harmless to leave.

## Status
done

## Changes
plugins/sdlc-lite/scripts/board.py: added `has_step_work`/`belongs_on_board` helpers, applied filter in `main()`, added selftest gate cases
plugins/sdlc-lite/skills/board/SKILL.md: documented the dropped/done-no-steps exclusion rule
plugins/sdlc-lite/skills/handoff-format/SKILL.md: documented that board.py uses ticket status to exclude tasks
CLAUDE.md: updated the board.py Layout line with the new exclusion rule

## Checks
`cd plugins/sdlc-lite && python3 scripts/board.py selftest` → `board selftest: PASS`
`plugins/sdlc-lite/scripts/check.sh` → all ok, board selftest PASS
Manual temp-root test: dropped (no steps) and done (no steps) tasks produced no row; done-with-step task still appeared as a row
`python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` (repo backlog): T-0008, T-0010, T-0011, T-0012, T-0005, T-0018 no longer listed; T-0014 (done with steps) still appears
Revert check: patched a copy of board.py with `belongs_on_board` forced to always return `True` (simulating a reverted filter) and ran its selftest → failed on the 3 new dropped/done-hidden assertions, confirming the gate bites

## Notes
None
