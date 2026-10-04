<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest label `(lean) lint warns on a lean-eligible plan with 3 steps`: pass. Evidence: ran `steps.py selftest` and grepped for `ok: <label>`. It matched. The full selftest ends `steps selftest: PASS`.
- Selftest label `(lean) lint warns on a one-criterion step`: pass. Evidence: the same selftest run matched this label.
- Selftest label `(lean) no warning for a planner L3 plan, a step at L4, a merge step, a replan, a ## Plan review line, or an unresolved: assumption`: pass. Evidence: the same selftest run matched this label.
- Selftest label `(lean) no warning for a two-step plan with two criteria per step`: pass. Evidence: the same selftest run matched this label.
- Warning appears on stderr for a one-criterion `planner-L2.md`: pass. Evidence: the command exited 0. A manual run printed the `steps lint: warning: ... step 1: one acceptance criterion; ...` line on stderr.
- (guard) Stdout is exactly `steps lint: ok`: pass. Evidence: the check passed, and the manual run shows exit code 0.
- `steps.py -h` contains `steps lint: warning:`: pass. Evidence: the grep matched. The text comes from the new argparse epilog.
- `sdlc-internals.md` contains `steps lint: warning:`: pass. Evidence: the grep matched. The diff adds one parenthetical to the lint sentence, covering the eligibility conditions and both triggers.
- (guard) Only `steps.py` and `sdlc-internals.md` changed outside `.sdlc`: pass. Evidence: the check exited 0. `git status` shows only those two files modified outside `.sdlc`.

The warning check can go red. I ran the same lint command from a throwaway worktree at `$SDLC_BASE_SHA`, and it printed no warning there.

I linted a `handoff.md` with one criterion. It printed `steps lint: ok` and exit 0 with no warning. This covers the `/fix` contract dependent.

## Out of scope changes
None. The `-h` epilog and the `RawDescriptionHelpFormatter` change in `main` are in `steps.py`, a targeted file, and they serve the `-h` criterion.

## For the next attempt
None
