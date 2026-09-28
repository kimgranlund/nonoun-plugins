<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: added the `live_step_dirs(task)` helper and used it in `plan_steps` (now sorted by `int(d.name[5:])`) and in the `--summary` L5 check. Added comments on `cost()` and `has_step_work` saying they keep the `step-*` glob on purpose. Added a docstring line about superseded dirs, and selftest case 5e.

## Checks
- `python3 board.py selftest`: PASS, and case 5e (the new superseded cases) is included.
- `python3 tickets.py selftest`: PASS.
- Negative control: I put the old `task.glob('step-*')` filter and sort key back in `plan_steps`, and the selftest failed with exit 1. I restored the helper and it passed again.
- Manual check: a temp root with `x/step-1`, `step-2` and `step-2.superseded-1`, each holding a `handoff.md`. `board.py --root <tmp>` shows exactly two step rows ("1. t" and "2. t") and no second "2." row.

## Notes
- The negative control fails because the old code crashes, not because an `expect` message fires. The old line `int(d.name.split('-')[1])` raises `ValueError` on `2.superseded` inside `plan_steps`. Either way the selftest fails, and after the revert is undone every step-count `expect` in 5e passes.
- I did not run `scripts/check.sh`. The acceptance criteria don't call for it.
