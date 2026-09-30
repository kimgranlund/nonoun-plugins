## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 5: Transcript reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/transcripts.py`: `read(log_path)` parses a stream-json `.log` leniently (lines that are not JSON objects are skipped): `tool_calls` = the count of `tool_use` blocks in `assistant` events, `bash_calls` = a list of (event `timestamp`, `input.command`) for `Bash` tool_use blocks, `tool_errors` = the count of `tool_result` blocks with `is_error` true, `denials` = a list of {hook_name, stderr} from `system` events with subtype `hook_response` and `exit_code` 2, `rate_limits` = the count of `rate_limit_event` events, `result` = {total_cost_usd, duration_ms, num_turns} from the last `result` event. A missing path returns a record with every field None and raises nothing. Register the `transcripts` cases: a fixture log with 5 Bash tool_use blocks, one `hook_response` with exit_code 2 whose stderr names run_in_background, one `rate_limit_event`, and prose lines mixed in yields tool_calls 5, one denial, rate_limits 1; a missing path yields None fields.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k transcripts`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k transcripts | grep -q '^ok: transcripts: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/transcripts.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
