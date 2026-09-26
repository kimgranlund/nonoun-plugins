<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None needed. The 2-line `build L3 done, no verifier -> verify L2` case from the superseded attempt was already in `plugins/sdlc-lite/scripts/steps.py`, at the specified position inside `selftest()`. I left it as is.

## Checks
- `grep -q "build L3 done, no verifier -> verify L2" plugins/sdlc-lite/scripts/steps.py`: exit 0, case present.
- Mutant check: exit 0. The copy differs from the tree, its selftest fails, and its FAIL list names the L3 case.
- (guard) selftest on the tree: exit 0, last line `steps selftest: PASS`.
- (guard) no deleted lines in the steps.py diff: exit 0.
- (guard) every hunk sits inside `def selftest`: exit 0.
- (guard) nothing outside `.sdlc/` other than steps.py is modified: exit 0.
- `check.sh`: exit 0 on the tree and exit 0 on a `git worktree add HEAD` copy. The FAIL, error, and warn lines match between the two, so no new findings. I removed the temp worktree afterward.

## Notes
None
