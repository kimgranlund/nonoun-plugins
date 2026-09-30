<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/codex-selftest.py: added `import time`, `DEADLINE = 120`, and the `CodexTests.wait_for(predicate, describe, deadline, directory, owner)` helper. The native-exchange and conductor-exchange polls now use `wait_for`. `SDLC_CODEX_TIMEOUT_SECONDS` in those two tests is now `str(DEADLINE)`. All `timeout=10/20` values are now `DEADLINE`. The `STUB` timeout sleep went from 30 to 600.
- plugins/sdlc-lite/scripts/lifecycle-selftest.py: the running-marker wait, the attempt.json `process_pid` and `.running` wait, and the lock-release loop now use `self.wait_for`. All `timeout=5/10/15/20` values are now `fixture.DEADLINE`. The `CLAUDE` stub timeout sleep went from 60 to 600.

## Checks
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: OK
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: Ran 20 tests, OK
- Simulated-load command (every child python3 start delayed 11 s): all 3 named tests ok, 270 s, exit 0
- `! grep -nE "(timeout=|monotonic\(\) ?\+ ?)[0-9]{1,2}\b" ...`: no matches, exit 0
- Negative control using the `run_lifecycle.py` from before c78e9b5: the selftest fails as required, exit 0
- Scope guard (only the two selftest files changed): exit 0
- Untracked-files guard: exit 0
- `git diff --check "$SDLC_BASE_SHA" -- <two files>`: clean
- `ps` scan for leftover `sdlc native test` processes after the suites: none found

## Notes
- The failure message comes from `state()` inside `wait_for` in codex-selftest.py. It includes the reason, the sorted listing of the watched directory, and `describe()`. When an owner process is passed, it also includes the owner's returncode and stderr.
- If the owner exits before the condition holds, `wait_for` checks the predicate once more and then fails at once, without waiting for the deadline.
- `codex_exec.py` sends `killpg` SIGTERM, then SIGKILL, on timeout (lines 55 and 61). So the longer stub sleep leaves no orphans, and the process scan above found none.
- `role('timeout')` still sets `SDLC_CODEX_TIMEOUT_SECONDS='1'`.
- The load run printed one extra path line to stdout, `.../scout-L1.request.response.json`. It is output from `codex_exchange.respond`, not a failure.
