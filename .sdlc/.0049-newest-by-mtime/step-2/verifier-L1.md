<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `board.py selftest` exits 0: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/board.py selftest`. It printed "board selftest: PASS" and exit=0.
- `st_mtime` appears only in `summary`, `sort_tasks`, and their selftest: pass. Evidence: `grep -n st_mtime` hits lines 174 (`summary` task pick), 265 and 267 (`sort_tasks`), and 484 (the `--sort` selftest). None fall in `by_level`, `step_row`, or `plan_steps`. The diff shows `by_level` now returns `order.ordered` for md files and sorts `.running` files by (level number, name). `plan_steps` needed no change because it goes through `by_level`. The docstring now states the runs.jsonl rule.
- Bench fixture copied to a temp dir, every file touched to one time, `board.py --root` run: pass. Evidence: step 2 shows `🟢 pass · builder L3 · verifier L2 · attempt 3`. The ` · attempt 3` suffix comes from the existing attempts counter, not from this change. The builder's notes say the same.
- Negative control (line 93 reverted to the mtime comparison makes the new case fail): pass. Evidence: I made a throwaway copy of the scripts and swapped `order.counts_after(...)` for `verifies[-1].stat().st_mtime >= last_build.stat().st_mtime`. The selftest then exited 1 on two cases. One was the rebuild-after-pass fixture, which gave 🟢 instead of awaiting verify. The other was the inverse-mtime fixture, which gave awaiting verify instead of 🟢. The equal-mtime pass fixture still passed under the revert, so it is not the case that bites. The other two fixtures carry that. The unmodified tree passes.
- Selftest fixtures match the spec: pass. Evidence: the diff shows an equal-mtime run (builder L1, verifier L1 fail, builder L2, verifier L2 pass) expecting a pass row. It also shows a rebuild fixture (a builder run after the pass) expecting awaiting verify, and an inverse-mtime fixture.

## Out of scope changes
None from this step. The worktree also modifies `check.sh`, `run-selftest.sh`, and `run.sh` and adds `order.py`. These look like step-1 work, and the builder said it did not touch them. I did not diff them.

## For the next attempt
None
