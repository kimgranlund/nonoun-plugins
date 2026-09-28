<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `board.py selftest` passes and includes the new superseded cases: pass. Evidence: `python3 board.py selftest` printed `board selftest: PASS`. Case 5e is in the diff (board.py, added after case 5d). It asserts `plan_steps` returns exactly two steps, exactly two board step rows, no `⚠ L5` in `--summary`, `cost()` at 1.25 including the superseded dir, and `has_step_work` true for a superseded-only task.
- Negative control (new case fails when the `plan_steps` helper is reverted): pass. Evidence: I ran a copy of board.py with the `live_step_dirs` regex filter removed and the sort key loosened to `d.name`. The selftest went red at case 5e with `ValueError: invalid literal for int() with base 10: '2.superseded'` at `n = int(d.name.split('-')[1])`, in `plan_steps` at board.py line 125. The same run with the real helper passes.
  - This red is a crash, not an `expect` message. The crash sits in the line the handoff says stays valid for live dirs, so it does bite the helper.
  - I did not separately isolate the `expect` for the step-row count or the L5 summary.
- Manual check with a temp root holding `x/step-1`, `x/step-2` and `x/step-2.superseded-1`, each with a `handoff.md`: pass. Evidence: `board.py --root <tmp>` printed rows `x | 1. t` and `x | 2. t` and the footer `0% across 2 steps`. There is no third or second "2." row.
- Existing board and tickets selftests still pass: pass. Evidence: `board selftest: PASS` and `tickets selftest: PASS`.
- Design points from the Do list: pass. Evidence from the diff:
  - `live_step_dirs` is defined with `re.fullmatch(r'step-\d+')` and an `is_dir()` check.
  - `plan_steps` uses it and sorts by `int(d.name[5:])`.
  - The `--summary` L5 check goes over live dirs.
  - `cost()` and `has_step_work` keep the `step-*` glob, each with a comment saying so.
  - The module docstring mentions superseded dirs.

## Out of scope changes
None. The only file changed by the step is `plugins/sdlc-lite/scripts/board.py`. The other modified or untracked files are `.sdlc/0039-superseded-step-dirs/` task bookkeeping (`handoff.md`, `planner-L1.md`, `runs.jsonl`, `step-*` dirs).

## For the next attempt
None
