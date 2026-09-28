<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Close the three headless abandon routes found in T-0105 in `plugins/sdlc-lite`, each with a check that fails without its fix:
- Bash auto-backgrounding a call once it passes its timeout.
- A late task-notification turn replacing the real result.
- Monitor background gate runs.

## Step 1: run.sh raises the Bash timeouts for every role run
level: L2
### Do
In `plugins/sdlc-lite/scripts/run.sh`, before the real `claude` launch (the `SDLC_ROLE=... "${cmd[@]}"` line), set `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` to `3600000`, the value bench.sh uses.
- Keep an inherited value only when it is a plain integer and at least 3600000. Replace anything else (unset, lower, or not numeric) with 3600000.
- Export both, or pass them on the launch line like `SDLC_ROLE`.
- Add a comment in the header saying why: Claude Code moves a foreground Bash call to the background once it passes its timeout, and no PreToolUse hook sees that (T-0105).

In `plugins/sdlc-lite/scripts/run-selftest.sh`, make a stub `claude` record the `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` it sees. Assert three cases:
- Unset: the stub sees `3600000` for both.
- Inherited `120000`: the stub sees `3600000`.
- Inherited `7200000`: the stub sees `7200000`.

Also update the selftest's header comment.
### Acceptance criteria
- `grep -q 'BASH_DEFAULT_TIMEOUT_MS' plugins/sdlc-lite/scripts/run.sh`
- `grep -q 'BASH_MAX_TIMEOUT_MS' plugins/sdlc-lite/scripts/run.sh`
- `grep -q '7200000' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'BASH_DEFAULT_TIMEOUT_MS' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`

## Step 2: run.sh saves the real report, never a trailing task notification
level: L3
### Do
With `--output-format json`, the log holds only the session's last result. The peer logs (for example `gen-ui-system-svelte-lite/.sdlc/.0024-geometry-sample-set/step-3/verifier-L3-2.log`) show that last result carrying `"origin":{"kind":"task-notification"}`, so the earlier report cannot be recovered. Fix it in `plugins/sdlc-lite/scripts/run.sh`:
- Switch the launch to `--output-format stream-json --verbose`. The log becomes one JSON event per line; stderr stays mixed in.
- Parse the log leniently, skipping lines that are not JSON (for example `jq -R 'fromjson? // empty'`). Consider only events with `type == "result"`.
- Choose, in this order:
  1. The last result event whose `.result` holds a line that is exactly the role's required heading (`## Status`, `## Verdict`, `## Goal`, and the rest, taken from the existing case table, which moves above this point).
  2. Else the last result event whose `.origin.kind` is not `task-notification`.
  3. Else the last result event.
- Apply the `is_error == false` and non-empty checks to the chosen event, and write its `.result` to the result file.
- The `runs.jsonl` line takes `total_cost_usd`, `duration_ms`, and `num_turns` from the last result event, which holds the session totals.
- Keep exit codes 1 and 3 and every other behavior. Update the header comment to describe the selection.

In `plugins/sdlc-lite/scripts/run-selftest.sh`:
- Make every stub emit `"type":"result"` events.
- Add a stub case whose log holds two result events: first `## Verdict\npass` with no origin, then `stale monitor, no action needed` with `"origin":{"kind":"task-notification"}`. Assert that `verifier L1` exits 0 and that its result file holds `## Verdict` and not `stale monitor`.
- Add a case where both events lack the heading: the non-notification one is saved and run.sh exits 3.
- Add a non-JSON stderr line in one stub's output to prove it is skipped.
### Acceptance criteria
- `grep -q 'stream-json' plugins/sdlc-lite/scripts/run.sh`
- `grep -q 'task-notification' plugins/sdlc-lite/scripts/run.sh`
- `grep -q 'task-notification' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'stale monitor' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh planner L1 .sdlc/0105-find-out-why-the-t/handoff.md | grep -q -- '--agent sdlc-lite:planner'`
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`

## Step 3: fanout selftest proves lane drivers get the high Bash timeouts
level: L1
### Do
`plugins/sdlc-lite/scripts/fanout.py` already passes `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` (`TIMEOUT_MS = '3600000'`) to the driver. Nothing checks it yet. Add two lines to the selftest `STUB` driver, next to its `SDLC_HEADLESS` check:
- `[ "${BASH_DEFAULT_TIMEOUT_MS:-}" = 3600000 ] || { echo "BASH_DEFAULT_TIMEOUT_MS not 3600000" >&2; exit 1; }`
- The same line for `BASH_MAX_TIMEOUT_MS`.
### Acceptance criteria
- `grep -qF 'BASH_DEFAULT_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'BASH_MAX_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`

## Step 4: block-background.sh denies Monitor in headless sessions
level: L2
### Do
In `plugins/sdlc-lite/hooks/block-background.sh`:
- When `tool_name` is `Monitor` and the session is headless (`SDLC_ROLE` set or `SDLC_HEADLESS=1`), deny with exit 2.
- The stderr message says to run gates and tests with foreground Bash (timeout 600000 or more) instead, and never end the turn while background work runs.
- Update the header comment.

In `plugins/sdlc-lite/hooks/hooks.json`, add a `PreToolUse` entry with `"matcher": "Monitor"` running only `block-background.sh`.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, add Monitor fixtures:
- `SDLC_ROLE=verifier`: exit 2, and stderr mentions foreground.
- `SDLC_HEADLESS=1`: exit 2.
- Neither set: exit 0.
- `SDLC_HEADLESS=0`: exit 0.

Update the selftest's header comment.
### Acceptance criteria
- `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | SDLC_ROLE=verifier plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | SDLC_HEADLESS=1 plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- (guard) `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh`
- `jq -e '[.hooks.PreToolUse[] | select(.matcher == "Monitor") | .hooks[].command | select(test("block-background"))] | length == 1' plugins/sdlc-lite/hooks/hooks.json`
- `grep -qF '"tool_name":"Monitor"' plugins/sdlc-lite/scripts/hook-selftest.sh && bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-background.sh plugins/sdlc-lite/scripts/hook-selftest.sh`

## Step 5: builder and verifier prompts keep gates in the foreground, guarded by check.py
level: L2
### Do
In `plugins/sdlc-lite/agents/builder.md` and `plugins/sdlc-lite/agents/verifier.md`, add a rule containing the exact phrase `never end the turn while background work runs`. The rule says:
- Run gates, tests, and long commands as foreground Bash calls with the Bash `timeout` at 600000 or more.
- Never use `run_in_background` or Monitor.
- Never end the turn while background work runs, because a headless run ends with the turn and the report is lost.

In `plugins/sdlc-lite/scripts/check.py`, add a check that both files contain that exact phrase, with an error naming the file when it is missing.
### Acceptance criteria
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/builder.md`
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/verifier.md`
- `tmp=$(mktemp -d) && mkdir -p "$tmp/plugins" && cp -R plugins/sdlc-lite "$tmp/plugins/sdlc-lite" && cp CLAUDE.md "$tmp/" && sed -i '' 's/never end the turn while background work runs//' "$tmp/plugins/sdlc-lite/agents/verifier.md" && ! python3 "$tmp/plugins/sdlc-lite/scripts/check.py" "$tmp/plugins/sdlc-lite" >/dev/null 2>&1`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`

## Step 6: docs describe the three fixes; gates green
level: L2
### Do
Update every record that describes these routes in the same change:
- `CLAUDE.md`:
  - The block-background line becomes `PreToolUse(Bash, Agent, Monitor)` and says Monitor is denied headless.
  - The run.sh Layout line says run.sh sets `BASH_DEFAULT_TIMEOUT_MS`/`BASH_MAX_TIMEOUT_MS` to 3600000 unless already higher, logs `stream-json`, and saves the last result holding the required heading, else the last one without a `task-notification` origin.
  - The Commands check.sh line names the new fixtures.
- `.claude/agents/sdlc-lite-author.md`: the headless-foreground hazard names Monitor and the run.sh timeouts.
- `plugins/sdlc-lite/agents/conductor.md`: where it says bench.sh raises the Bash timeouts, say run.sh and fanout do too.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the `.log` is a stream-json role transcript.
- `plugins/sdlc-lite/scripts/check.sh`: header comment.
- The chain and fix skills, if they list what block-background denies.

Then run every gate below and fix any red that earlier steps introduced.
### Acceptance criteria
- `grep -qF 'PreToolUse(Bash, Agent, Monitor)' CLAUDE.md`
- `grep -q 'BASH_DEFAULT_TIMEOUT_MS' CLAUDE.md`
- `grep -q 'stream-json' CLAUDE.md`
- `grep -q 'task-notification' CLAUDE.md`
- `grep -q 'Monitor' .claude/agents/sdlc-lite-author.md`
- `grep -q 'stream-json' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- Step 2 assumes that `claude -p --output-format stream-json --verbose` emits one `type: "result"` event per turn, including the turns that task notifications trigger. The peer logs only prove that json mode keeps the last one. If stream-json also emits a single final result, the real report still cannot be recovered. The selftest uses stubs, so it cannot prove this on a live run. A live confirmation needs a real run that ends with a task notification.
- Step 2 assumes `total_cost_usd` and `duration_ms` on the last result event are session totals. If they are per turn, `runs.jsonl` costs undercount.
- The Monitor tool name in the PreToolUse payload is assumed to be `Monitor`. No live probe covers it (a non-goal).
- Step 1's criteria check the environment that run.sh passes, not a live auto-background.
- `scripts/check.sh` takes about 2.5 minutes and was green at plan time.
