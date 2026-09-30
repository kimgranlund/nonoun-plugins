## Task goal
A role that changes `scripts/run.sh` during its own run still gets its result saved, or is stopped before it can change the running file. A test that failed before the fix passes after it.

## Step 2: run_lifecycle.py fails an exit 0 that wrote no result
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Defense in depth for the stated exit code contract ("1 run failed or returned no result"). In `plugins/sdlc-lite/scripts/run_lifecycle.py` `run()`, after the child exits: if it was not interrupted, `rc == 0`, and `directory / (name + '.md')` does not exist, print one stderr line containing `wrote no result` (naming the expected result path and the `.log`), set `rc = 1`, and let the attempt record become `failed` with `exit_code` 1. Leave interrupted, failed, and normal completed paths unchanged.

In `plugins/sdlc-lite/scripts/lifecycle-selftest.py`, add `test_exit_zero_without_result_fails` and append it to the `names` list in `__main__`. It drives `run_lifecycle.run` with a runner that exits 0 without writing a result. For example, point `readiness.ROOT` (as seen by `run_lifecycle`) at a temp root whose `scripts/run.sh` is just `exit 0`, with readiness patched to ready. It asserts return code 1, attempt status `failed`, and the stderr line.

Update the `Exit codes` line in the `run.sh` header, and add a sentence to the run.sh entry in `docs/maintenance/sdlc-internals.md` containing the exact phrase `exits 0 without a result`: the lifecycle owner records such a run as failed with exit 1.
### Acceptance criteria
- `grep -q "'test_exit_zero_without_result_fails'" plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `grep -qF 'wrote no result' plugins/sdlc-lite/scripts/run_lifecycle.py`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- The new test fails on the base lifecycle: `w="${SDLC_TMP_WORKTREES:?}/base-s2"; git worktree add -q --detach "$w" "$SDLC_BASE_SHA" && cp plugins/sdlc-lite/scripts/lifecycle-selftest.py "$w/plugins/sdlc-lite/scripts/lifecycle-selftest.py" && out=$(python3 "$w/plugins/sdlc-lite/scripts/lifecycle-selftest.py" 2>&1); rc=$?; git worktree remove --force "$w"; test "$rc" -ne 0 && printf '%s\n' "$out" | grep -q "test_exit_zero_without_result_fails"`
- `grep -qF 'exits 0 without a result' docs/maintenance/sdlc-internals.md`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx "run selftest: PASS"`
