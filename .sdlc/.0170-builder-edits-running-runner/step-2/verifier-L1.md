<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -q "'test_exit_zero_without_result_fails'" plugins/sdlc-lite/scripts/lifecycle-selftest.py`: pass. Evidence: the grep matched. The name is in the `names` list at the end of `__main__`, and the method is defined in the diff.
- `grep -qF 'wrote no result' plugins/sdlc-lite/scripts/run_lifecycle.py`: pass. Evidence: the grep matched. The added lines in `run()` are guarded by `not interrupted and rc == 0 and not result.exists()`, print the stderr line naming the expected result and the `.log`, and set `rc = 1`.
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: pass. Evidence: "Ran 6 tests in 5.144s / OK".
- The new test fails on the base lifecycle: pass. I ran it by hand in a throwaway worktree at `$SDLC_BASE_SHA` (9d6ca64), because the hook blocked the compound `git worktree add` in the criterion's command line. I copied the new selftest over the base tree's and ran it. Output: "FAIL: test_exit_zero_without_result_fails ... AssertionError: 0 != 1 / FAILED (failures=1)". The base `run()` returns 0 for an exit 0 with no result, so the check can go red. The worktree was removed afterward.
- `grep -qF 'exits 0 without a result' docs/maintenance/sdlc-internals.md`: pass. Evidence: the grep matched. The diff shows the sentence in the run.sh entry: "When the runner exits 0 without a result file, `run_lifecycle.py` (the lifecycle owner) records the run as failed with exit 1...".
- `bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx "run selftest: PASS"`: pass. Evidence: the script's last output line was exactly "run selftest: PASS". I ran it without the grep and read its output.
- The `Exit codes` line in the run.sh header is updated (from the Do text): pass. Evidence: the diff shows the `# Exit codes:` line now notes that `run_lifecycle.py` also turns an exit 0 with no saved result into 1.

I drafted one possible fail reason: the new test patches the readiness module, so it might not exercise the real `run()` path. It does not hold. The test calls `run_lifecycle.run` directly, uses a real subprocess (`scripts/run.sh` containing `exit 0`), and asserts the return code, the attempt record status and `exit_code`, and the stderr text. The base run failing shows the assertion bites.

## Out of scope changes
- `plugins/sdlc-lite/scripts/run.sh` has a `{ ... }` group and a Self-edit header comment, and `plugins/sdlc-lite/scripts/run-selftest.sh` has 36 added lines. These look like step 1's uncommitted work. The `.sdlc/0170.../step-1/` directory exists and `git status` shows them as modified in the same tree.
- The `sdlc-internals.md` self-edit sentence also belongs to step 1.
- Only the Exit codes line and the `docs/maintenance/sdlc-internals.md` sentence about exit 0 without a result belong to this step.
- I did not check step 1's changes beyond the `run-selftest.sh` pass. I judged them out of this step's scope because the handoff's Do names only `run_lifecycle.py`, `lifecycle-selftest.py`, the Exit codes line and the docs sentence.

## For the next attempt
None
