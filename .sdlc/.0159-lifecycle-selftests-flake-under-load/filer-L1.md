<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0159: Make lifecycle and codex selftests tolerate host load

## PR body
### Summary
On a loaded host (load average about 45, a 1305 s `check.sh` run), `lifecycle-selftest.py` and `codex-selftest.py` failed even though the code was correct. Both pass standalone. The cause was fixed short timeouts and immediate existence asserts. This PR replaces them with polling up to a 120 s deadline. When a wait times out, the failure message shows the state the test saw. The change is tests only. No runtime script changed.

### Changes
- `plugins/sdlc-lite/scripts/codex-selftest.py`:
  - Adds `DEADLINE = 120` and a `CodexTests.wait_for(predicate, describe, deadline, directory, owner)` helper.
  - On timeout, the helper's failure message lists the sorted contents of the watched directory and includes `describe()`. If an owner process is given, it also includes that process's returncode and stderr.
  - If the owner exits before the condition holds, the helper checks once more and then fails at once instead of waiting for the deadline.
  - The `scout-L1.request.json` wait and the conductor request wait now use `wait_for`.
  - `SDLC_CODEX_TIMEOUT_SECONDS` in the native and conductor exchange tests is now `str(DEADLINE)`. `role('timeout')` still sets it to `'1'`, because that test exercises the timeout on purpose.
  - Fixed `timeout=10/20` values are now `DEADLINE`.
  - The `MODE=timeout` stub sleep goes from 30 s to 600 s.
- `plugins/sdlc-lite/scripts/lifecycle-selftest.py`:
  - The `scout-L1.running` wait, the attempt.json `process_pid` plus `.running` wait, and the lock-release loop now use `self.wait_for`.
  - Fixed `timeout=5/10/15/20` values are now `fixture.DEADLINE`.
  - The `MODE=timeout` stub sleep goes from 60 s to 600 s.
- Assertions keep their meaning. A duplicate launch still returns 2 with `still owns`. The recovery, `interrupted`/143 and native-refusal checks are unchanged.

### Verification
The verifier passed step 1.
- Load simulation: a wrapper delays every child `python3` start by 11 s. The three named race tests (`test_both_hosts_cancel_lock_retry_and_routing`, `test_sigkill_recovers_claude_but_codex_native_refuses`, `test_native_exchange_preserves_runner_artifacts`) pass, "Ran 3 tests in 273.407s, OK". The same command at base SHA 7334f49 fails with 2 failures and 1 error, so the check discriminates.
- The grep for remaining one- or two-digit `timeout=` or `monotonic()+N` values exits 0 with no matches.
- `lifecycle-selftest.py` passes standalone: 6 tests, OK. `codex-selftest.py` passes standalone: 20 tests, OK.
- Negative control: with `run_lifecycle.py` from before c78e9b5, the lifecycle selftest still fails ("AssertionError: 0 != 1", failures=2).
- Only the two selftest files changed. No untracked files exist outside `.sdlc`. `git diff --check` is clean.
- A `pgrep` after the runs found no leftover stub processes.

### Limitations
- The load check only simulates load by delaying `python3` starts. It does not reproduce real contention at load average about 45, so it does not show that `check.sh` stays green at that load.
- The full `check.sh` was not re-run under real load. The artifacts show only the two selftests and the guards.

## Changelog entry
- Fixed: `lifecycle-selftest.py` and `codex-selftest.py` no longer time out on a loaded host. Fixed short timeouts and immediate existence asserts are now polls with a 120 s deadline. A timeout failure reports the watched directory and child process state. Tests only; no runtime behavior changed.

## Follow-ups
- note: The verifier did not independently re-check the builder's claim that `codex_exec.py` kills the stub on timeout (the stub sleep is now 600 s). A `pgrep` after the runs found no orphans.
- note: The negative-control guard fails as a whole only if every test passes against the old `run_lifecycle.py`. It already fails through `test_sigkill_recovers_claude_but_codex_native_refuses` and `test_exit_zero_without_result_fails`, so loosening one of those tests would go unnoticed while the other still fails.
