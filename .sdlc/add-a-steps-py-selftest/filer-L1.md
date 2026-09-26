<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0081: Add a steps.py selftest case for a done L3 build mapping to verify L2

## PR body
### Summary
`steps.py selftest` now fails when a done L3 build stops mapping to `verify L2`. Before this change, a mutant that mapped L3 to verifier L3 left the selftest green. This is a follow-up from T-0061.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`: adds one `check(...)` case in `selftest()`, right after the L4 → `verify L3` case. It is `next verify: build L3 done, no verifier -> verify L2`, two added lines and no deletions.
- No behavior change to `steps.py next`. `verifier_level` and `next_action` are untouched.

### How each step was verified
The task ran as one step. The first attempt failed verification on two plan defects, not on the build. The mutant criterion copied `steps.py` alone, which dies on `import order`. The `git diff --name-only` guard also caught the task handoff, which was edited before the plan. A planner L3 replan fixed both criteria, and the build was accepted unchanged. The rerun verifier (L1) verdict is pass.
- The case is present in the tree. The same grep exits 1 in a throwaway `git worktree add HEAD` copy, so the check can fail.
- Mutant check, run in a copy of the whole `scripts/` dir. With `verifier_level` mapping L3 to 3, the selftest exits 1 and its FAIL list names only the new case. The same mutant on HEAD's `steps.py` ends at `steps selftest: PASS`, which was the gap.
- The tree's selftest exits 0 and ends with `steps selftest: PASS`.
- The `steps.py` diff deletes no line, and its only hunk is inside `def selftest()`.
- Nothing outside `.sdlc/` other than `steps.py` is modified or untracked.
- `plugins/sdlc-lite/scripts/check.sh` exits 0 on the tree and in a HEAD worktree. The fail, error, and warn lines are identical, so there are no new findings.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `steps.py selftest` now covers a done L3 build mapping to `verify L2`, so a wrong build-level to verifier-level mapping for L3 turns the selftest red. Test coverage only; no change to `steps.py next` behavior.

## Follow-ups
None
