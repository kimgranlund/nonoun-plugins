<!-- role=builder level=L1 model=sonnet effort=low -->
T-0008, T-0010, T-0011, T-0012, T-0005, T-0018 are correctly absent; T-0014 (done, has steps) still appears. All acceptance criteria satisfied.

## Status
done

## Changes
plugins/sdlc-lite/scripts/board.py: added subprocess-based selftest leg (5b) that exercises `main()`'s actual task selection through the gate fixture, per the previous attempt's feedback; added `subprocess` import.

## Checks
- `cd plugins/sdlc-lite && python3 scripts/board.py selftest` → `board selftest: PASS`
- `bash plugins/sdlc-lite/scripts/check.sh` → all ok (role levels, agents, tickets selftest, board selftest, shellcheck, plugin validate)
- Reverted-filter red check: temporarily deleted the `tasks = [t for t in tasks if belongs_on_board(t)]` line in `main()`, ran selftest → FAIL on the 3 new subprocess assertions (hides dropped-no-steps/dropped-with-plan/done-no-steps); restored the file, reran → PASS
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` (repo root) → no rows for T-0008, T-0010, T-0011, T-0012, T-0005, T-0018; T-0014 (done, has steps) still appears

## Notes
Docs (`skills/board/SKILL.md`, `skills/handoff-format/SKILL.md`, root `CLAUDE.md`) already stated the filtering rule from the prior attempt; no changes needed there. The `belongs_on_board()`-only assertions from the prior attempt (5) were kept alongside the new main()-through-subprocess leg (5b), since both are useful and the acceptance criteria ask for both a unit-level and an end-to-end proof.
