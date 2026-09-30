<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/transcripts.py`: new file. `read(log_path)` reads a stream-json log leniently and returns tool_calls, bash_calls, tool_errors, denials, rate_limits and result. A missing path returns every field as None.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: registered two `transcripts` cases, the mixed fixture log and the missing path.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k transcripts`: exit 0, both cases ok, PASS.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k transcripts | grep -q '^ok: transcripts: '`: matched.
- `test -f plugins/sdlc-lite/scripts/traces/sources/transcripts.py`: true.
- (guard) scope check against the SHA in `step-5/base-sha`: passed (empty output).
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): exit 0.
- `git diff --check`: clean.

## Notes
- The fixture includes a non-object JSON line (`[1, 2]`), a truncated line, a second `hook_response` with exit_code 0 that is not counted, and two `result` events. The test asserts the last `result` event wins.
- `tool_errors` counts only `tool_result` blocks inside `user` events, because that is where the stream-json format puts them.
