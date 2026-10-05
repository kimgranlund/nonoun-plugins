<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/reports/messages-wait-live-run/probe.py` (new): live probe for `messages.py wait` with `claude` and `codex` arms, one shared `judge` verdict function, and an offline `selftest` with the 12 named cases.

## Checks
- `python3 docs/reports/messages-wait-live-run/probe.py selftest` (Python 3.9.6, which is `/usr/bin/python3`): 12 `ok:` lines, then `probe selftest: PASS`, exit 0.
- AC1 (selftest PASS plus each labeled `ok:` line): exit 0.
- AC2 (`BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` appear in probe.py): exit 0.
- AC3 (file exists and contains no em dash): exit 0.
- AC4 (scope guard against `SDLC_BASE_SHA=bc21b53`: no tracked change outside the allowed list, and the only untracked file is probe.py): exit 0.
- Negative controls: I loaded the module, patched one value in memory, and ran `selftest()`. The file was not changed. Each mutation made the selftest fail on its own case:
  - `CLAUDE_POLL_TOOLS=()` failed `fail: a Monitor call`.
  - `CODEX_POLL_FUNCTIONS=('write_stdin',)` failed `fail: a Codex cell wait`.
  - Turning off sleep and count/list classification failed `fail: a count call`.
  - A constant `utc_now` failed `fail: the wait started after the send`.
- `git diff --check`: clean.
- `probe.py --help`: shows usage `{claude,codex,selftest} [--timeout SECONDS]`.

## Notes
- No live arm was run and no model was called, as the step says. The `run_arm` path (host launch, delayed send, Codex isolation controls, rollout lookup) is checked only by the shared code the selftest uses (`judge`, `measure`, the trace classes, `rollout_polls`, `host_missing`). Step 4 is the first live check.
- `judge` returns the output lines (`wait_calls=… poll_calls=…`, `wait_returned=`, `wait_before_send=`, then the stamps line) and the fail reasons. Each reason names its value:
  - `wait_calls=N`
  - `poll_calls=N`
  - `wait_returned=<x>, not <mid>`
  - `wait_before_send=no`
  - the T-0179 oracle reasons
  - `timeout after N s`
  - `no rollout file for thread <id>, so polls cannot be counted`
- Every unverified line reads `result=unverified reason=host cannot run: <detail>`. A Codex control call that leaves no rollout raises unverified, and its detail starts with `codex control call … left no rollout file`.
- Codex wait output comes only from an `item.completed` event for the first wait item. If Codex 0.159.2 shows code-mode shell calls in `exec --json` without `command_execution` items, the live arm will report `wait_calls=0`. Step 4 should check for this.
