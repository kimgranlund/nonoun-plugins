<!-- role=verifier level=L1 model=sonnet effort=medium -->
No unaccounted changes outside the expected set.

## Verdict
pass

## Criteria
- New behavior (non-zero exit + inherited step → `inherited red: step-1: test_a (driver rc=7)`): pass. Evidence: ran the exact handoff command against the built tree; `.sdlc/.../report.md` row was `| alpha | T-0001 | inherited red: step-1: test_a (driver rc=7) | wip 44cc066 |`. Confirmed the check bites: same command run in a throwaway worktree (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`) at pre-build HEAD produced `| alpha | T-0001 | driver failed rc=7 |` (red), so the criterion discriminates.
- (guard) Unchanged existing behavior (non-zero exit, no inherited step → `driver failed rc=<n>`): pass. Evidence: ran the exact handoff command; report row was `| alpha | T-0001 | driver failed rc=7 |`. Also ran the same command in the pre-build worktree and got the identical passing row, confirming this is a true guard (unchanged behavior, not silently vacuous).
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: ran it in the built tree, full output ends `EXIT=0`, including `fanout selftest: PASS` (which now runs the new case 5b and its negative control).

## Out of scope changes
None. Working tree changes are exactly: `plugins/sdlc-lite/scripts/fanout.py` (the Do's code, docstring, and selftest case), `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` (the Do's required doc sync), and `.sdlc/0119-fanout-py-still-reports-only/handoff.md` plus the untracked `planner-L1.md`/`planner-L1.log`/`runs.jsonl` — these are the pre-existing planner-stage artifacts that produced this step's own handoff, not builder output, and predate the builder's diff (`git diff HEAD` for fanout.py/CLAUDE.md/sdlc-lite-author.md shows only the step's own scoped changes, checked above).

## For the next attempt
None.
