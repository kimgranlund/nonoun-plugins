<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `lifecycle-selftest.py` and `codex-selftest.py` pass on a slow, heavily loaded host when the code is correct, by changing the tests only. Fixed short timeouts and 10-second existence waits become polling up to a generous deadline, and a timeout failure reports the state it saw. The tests must still fail against the run_lifecycle.py from before c78e9b5.

## Step 1: Load-tolerant waits in the lifecycle and codex selftests
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Edit only `plugins/sdlc-lite/scripts/lifecycle-selftest.py` and `plugins/sdlc-lite/scripts/codex-selftest.py`. Runtime scripts (`run.sh`, `run_lifecycle.py`, `codex_exec.py`, `codex_exchange.py`) stay unchanged.

1. Add one shared deadline constant in `codex-selftest.py`, for example `DEADLINE = 120` seconds. `lifecycle-selftest.py` already imports that module as `fixture`, so it reuses the same constant. Next to it, add a small helper `wait_for(predicate, describe, deadline=DEADLINE)`. It polls every 0.05 s. On timeout it calls `self.fail(...)` with a message that shows the observed state: a sorted listing of the watched directory, plus whatever `describe()` returns (for example the child's returncode). A method on `CodexTests` is fine, because `LifecycleTests` subclasses it.
2. Replace every "poll for a file up to `monotonic()+10`, then assert" with `wait_for`:
   - `test_both_hosts_cancel_lock_retry_and_routing`: the `scout-L1.running` wait.
   - `test_sigkill_recovers_claude_but_codex_native_refuses`: the attempt.json `process_pid` plus `.running` wait, and the lock-release loop.
   - `test_native_exchange_preserves_runner_artifacts`: the `scout-L1.request.json` wait.
   - `test_conductor_exchange_needs_no_nested_cli`: the conductor request glob wait.
   If the owner process exits before the condition holds, fail at once with its returncode and stderr. Do not spin until the deadline.
3. Replace every fixed short subprocess timeout in both files (`timeout=5/10/15/20` on `subprocess.run`, `communicate`, `wait`) with `DEADLINE`.
   - The native exchange test and the conductor exchange test set `SDLC_CODEX_TIMEOUT_SECONDS='10'`. Raise it to `str(DEADLINE)` so the runner does not give up while a loaded test is still polling.
   - Leave `SDLC_CODEX_TIMEOUT_SECONDS='1'` in `role('timeout')` alone. That test exercises the timeout on purpose.
4. The `MODE=timeout` stubs (the `CLAUDE` stub in lifecycle-selftest sleeps 60, the codex `STUB` sleeps 30) must outlive the whole duplicate-launch phase under load. Raise both sleeps well past `DEADLINE`, for example 600. The tests always stop these children (SIGTERM, killpg, or codex_exec's own timeout kill). Before relying on that, confirm in `codex_exec.py` that a timeout kills the stub, so a longer sleep leaves no orphan.
5. Keep every assertion's meaning. The duplicate launch must still return 2 with `still owns`. Recovery, `interrupted`/143, and the native refusal checks stay as they are.

This is the gates green step. Run both selftests plus the load-simulation and negative-control criteria below, and fix any red this change introduces.

### Acceptance criteria
- Under a simulated load, where every child `python3` start is delayed 11 s, the three named race tests pass. This is red now: the 10 s waits expire. `set -u; py=$(command -v python3); d=$(mktemp -d); printf '#!/bin/sh\nsleep 11\nexec %s "$@"\n' "$py" > "$d/python3"; chmod +x "$d/python3"; cd plugins/sdlc-lite/scripts && PATH="$d:$PATH" "$py" -c 'import sys,unittest,importlib.util;sys.path.insert(0,".");s=importlib.util.spec_from_file_location("lst","lifecycle-selftest.py");m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=importlib.util.spec_from_file_location("cst","codex-selftest.py");n=importlib.util.module_from_spec(c);c.loader.exec_module(n);t=unittest.TestSuite([m.LifecycleTests("test_both_hosts_cancel_lock_retry_and_routing"),m.LifecycleTests("test_sigkill_recovers_claude_but_codex_native_refuses"),n.CodexTests("test_native_exchange_preserves_runner_artifacts")]);sys.exit(not unittest.TextTestRunner(verbosity=2).run(t).wasSuccessful())'`
- No fixed one- or two-digit timeout or poll deadline remains in either selftest: `! grep -nE "(timeout=|monotonic\(\) ?\+ ?)[0-9]{1,2}\b" plugins/sdlc-lite/scripts/lifecycle-selftest.py plugins/sdlc-lite/scripts/codex-selftest.py`
- Observable: when a wait times out, the helper's failure message includes the watched directory's listing, and the child's returncode or stderr when a child exists. A verifier can see this in the helper source.
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) Negative control: the lifecycle selftest still fails against the run_lifecycle.py from before c78e9b5. `set -u; sha=$(git log --format=%H -1 --grep='Recover stale Claude runs under lifecycle lock'); test -n "$sha" || exit 1; d=$(mktemp -d); cp -R plugins/sdlc-lite "$d/p"; git show "$sha^:plugins/sdlc-lite/scripts/run_lifecycle.py" > "$d/p/scripts/run_lifecycle.py"; ! python3 "$d/p/scripts/lifecycle-selftest.py"`
- (guard) Only the two selftest files change: `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxE 'plugins/sdlc-lite/scripts/(lifecycle|codex)-selftest\.py')"`
- (guard) No new untracked files outside `.sdlc`: `test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/lifecycle-selftest.py plugins/sdlc-lite/scripts/codex-selftest.py`

## Risks
- The load criterion only simulates load, by delaying each `python3` start 11 s. Real contention at load average ~45 is not reproduced, so this step does not prove check.sh stays green at that load.
- After the fix, the load criterion takes several minutes. Its margin rests on at most about 4 delayed spawns (~44 s) per wait against a 120 s deadline.
- The negative control fails today through `test_sigkill_recovers_claude_but_codex_native_refuses` (returns 2) and `test_exit_zero_without_result_fails`. Suppose the builder's changes made either test pass against the old run_lifecycle.py, for example by loosening the recovery assertion. The guard catches that only if every other test also passes; one remaining failure keeps it green.
- Longer stub sleeps rely on the tests always stopping their children. If a path exists where codex_exec does not kill the stub on timeout, an orphan could live up to 600 s.
