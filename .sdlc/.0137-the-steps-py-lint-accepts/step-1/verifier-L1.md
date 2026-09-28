<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `test -f a || exit 1 | cat` lint criterion: pass. Evidence: I ran the exact span on the built tree and got `rc=0`, so `plan defect` was emitted. The same span in a throwaway worktree at HEAD gave `base rc=1`, so the check fails before the change.
- `test -f a || { echo x; exit 1; } | cat` lint criterion: pass. Evidence: the exact span gave `rc=0` on the built tree and `base rc=1` at HEAD, so this check also fails before the change.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: on the built tree it printed `steps selftest: PASS` with `rc=0`. Negative control: in the throwaway worktree I copied in the built steps.py and put `'|'` back into the `ends_command` tuple (line 454). The selftest then printed `steps selftest: FAIL, these did not hold:`, so the two new refuse controls do catch the old behavior. At HEAD the selftest also exits 0, as a guard should. The existing pass controls are still in place (`'test -f a || exit 1'` and the loop form at steps.py:1264) and pass within the green run. The builder's Checks lines are confirmed by these runs, not taken from its summary.

## Out of scope changes
`.sdlc/0137-the-steps-py-lint-accepts/handoff.md` (the task handoff, not the step's code file) was modified. I read the diff: it fills in the template placeholders for Goal and Constraints with text about this task. That is task bookkeeping from the planning stage, not a code change, and it does not affect any criterion. Dismissed as harmless. `plugins/sdlc-lite/scripts/steps.py` is the only project file changed, and its diff covers exactly the Do: the `ends_command` tuple, the two docstrings, and the two selftest refuse forms.

## For the next attempt
None
