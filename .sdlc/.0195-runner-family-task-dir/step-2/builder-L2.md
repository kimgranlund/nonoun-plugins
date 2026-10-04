<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/codex_roles.py`: in `resolve`, when the role is verifier and the directory holds no builder result, it now reads the newest builder result from the highest-numbered `step-<n>/` child that has one. Superseded dirs are skipped. A comment names run.sh's verifier family rule as the Claude twin.
- `plugins/sdlc-lite/scripts/codex-selftest.py`: added `CodexTests.test_verifier_task_dir_reads_newest_live_step_builder` with sub-cases 1 to 5, placed after `test_verifier_shares_builder_model_without_alternate`.
- `docs/codex-role-execution.md`: added the required sentence to line 46.

## Checks
- AC1, the task dir alternate and shared case, through the python one-liner: exit 0. It printed `('gpt-6.1-sol','low',False) ('gpt-6-luna','low',True)`.
- AC2, superseded dirs and numeric step order: exit 0.
- AC3 (guard), the task dir's own builder result wins: exit 0.
- AC4, the run.sh codex dry run grep for `--model gpt-6.1-sol --effort low`: exit 0.
- AC5, the new test against base `plugins/sdlc-lite` fails with `^AssertionError`: exit 0.
- AC6, the new test alone: 1 test, OK.
- AC7 (guard), the full `codex-selftest.py`: 23 tests, OK.
- AC8, the grep in the docs file: exit 0.
- AC9, the scope check: exit 0.
- `git diff --check`: clean.

## Notes
None
