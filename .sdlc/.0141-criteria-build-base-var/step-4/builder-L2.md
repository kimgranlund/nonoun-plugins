<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. Every gate was already green, so there was nothing to fix.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0
- `python3 plugins/sdlc-lite/skills/decompose/scripts/coverage_check.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/order.py selftest`: exit 0
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: exit 0
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: exit 0
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/check.sh`: exit 0
- `claude plugin validate plugins/sdlc-lite`: exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, run twice, passed both times
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0, run on its own once and again inside each check.sh run

## Notes
- hook-selftest.sh: no exit 141 (SIGPIPE) in any run this session. It passed on its own once, and inside both check.sh runs. The flake seen at plan time did not show up.
- My first loop over the gates exited 127 on every command. That was my harness's fault, not the gates: zsh does not split an unquoted variable into words, so each command string was run as one program name. I reran every gate with `eval` and all passed. Only those `eval` results are counted above.
