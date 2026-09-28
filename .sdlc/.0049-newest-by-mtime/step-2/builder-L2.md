<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: imports `order`. `by_level(..., 'md')` now returns `order.ordered`, and `.running` files sort by (level number, name). The verifier-after-build test now uses `order.counts_after`. `plan_steps` gets the newest plan through `by_level`, so no code change was needed there. The docstring now states the runs.jsonl rule. Added selftest case 7 with three fixtures: equal mtimes giving pass, a rebuild after the pass giving awaiting verify, and mtimes inverse to record order.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: PASS, exit 0.
- `grep -n st_mtime plugins/sdlc-lite/scripts/board.py`: hits at lines 174 (`summary` task pick), 265 and 267 (`sort_tasks`), and 484 (the `--sort` selftest). None are in `by_level`, `step_row` or `plan_steps`.
- Copied the button-geometry-model results into a temp `results/` dir, touched every file to one time, and ran `board.py --root`. Step 2 shows `🟢 pass · builder L3 · verifier L2 · attempt 3`.
- Negative control: with line 93 reverted to the mtime comparison, the selftest fails on 2 cases (the rebuild after the pass, and the inverse mtimes) and exits 1. With the change restored it passes again.
- `plugins/sdlc-lite/scripts/check.sh`: the tail shows the order and run selftests passing, plus the shellcheck and plugin validate steps. I only read the last lines of output.

## Notes
- The step-2 row on the bench fixture has an ` · attempt 3` suffix after `verifier L2`. That suffix comes from the existing attempts counter, not from this change. The new selftest expectations include the suffix too.
- The worktree also has changes that are not from this step: `order.py`, `run.sh`, `check.sh` and `run-selftest.sh`, which look like step-1 work. I did not touch them.
