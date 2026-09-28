## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

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
