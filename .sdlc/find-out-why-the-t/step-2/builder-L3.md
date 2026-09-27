<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: the launch now uses `--output-format stream-json --verbose`. The role section case table moved above the handoff check. The log is parsed leniently (`jq -R 'fromjson? // empty'`), and only `type == "result"` events count. The saved event is picked in this order: the last event with a line that is exactly the role's heading (trailing whitespace ignored), else the last event whose origin is not `task-notification`, else the last event. The `is_error == false` and non-empty checks run on the picked event. The `runs.jsonl` cost, duration and turns come from the last result event. The header comment now describes the selection. Exit codes 1, 2 and 3 are unchanged.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: every stub now emits compact `"type":"result"` events. The main stub also writes a non-JSON stderr line into the log. New `res2`/`pick_rc` cases:
  - Case 1: `## Verdict\npass` (cost 1), then `stale monitor, no action needed` with `origin.kind` `task-notification` (cost 3), plus a system event and a non-JSON line. `verifier L1` must exit 0, the result must hold `## Verdict` and not `stale monitor`, and `runs.jsonl` `cost_usd` must be 3.
  - Case 2: no event has the heading. Exit 3, and the non-notification result (`working on it`) is the one saved.
  - The header comment is updated.

## Checks
- `grep -q 'stream-json' plugins/sdlc-lite/scripts/run.sh`: exit 0
- `grep -q 'task-notification' plugins/sdlc-lite/scripts/run.sh`: exit 0
- `grep -q 'task-notification' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'stale monitor' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, exit 0
- (guard) `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh planner L1 .sdlc/find-out-why-the-t/handoff.md | grep -q -- '--agent sdlc-lite:planner'`: exit 0
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, no output
- Negative controls, each a temporary edit of run.sh that was then restored:
  - Pick only the last event: the selftest fails (`exit 3, want 0`).
  - Remove the non-notification fallback: the selftest fails (`no heading: the non-notification result was not saved`).
- `scripts/check.sh` (run from `plugins/sdlc-lite`): exit 0. The order, fanout, run, hook and live-probe selftests passed, as did shellcheck and plugin validate.

## Notes
- The step 1 changes to both files (the Bash timeout settings) were already uncommitted in the tree, and I kept them. Nothing was committed.
- Neither of the handoff's two required cases tests the heading rule on its own. Removing it from run.sh leaves the selftest green, because the non-notification fallback still picks the Verdict event. A case that would catch this: an earlier event with the heading, then a later non-notification event without it. I did not add it, because the handoff did not ask for it.
- The stubs now use `jq -nc` because the log is parsed one line at a time. Pretty-printed multi-line JSON would not parse.
