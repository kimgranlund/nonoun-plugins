<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. check.sh was green with step 1's changes, so no repo file needed a fix. The only new files are the probe files in `/tmp/t0132-probe/`, which is outside the repo.

## Checks
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. All selftests passed, including the hook selftest, and shellcheck and plugin validate are ok. The T-0133 flake did not show up, so I did not rerun it.
- `plugins/sdlc-lite/scripts/run.sh planner L2 /tmp/t0132-probe/handoff.md`: exit 0 and wrote `/tmp/t0132-probe/planner-L2.md`.
- `test -s /tmp/t0132-probe/planner-L2.md`: exit 0.
- `jq -se 'map(select(.role=="planner" and .level=="L2")) | length > 0 and (last.turns < 11.5)' /tmp/t0132-probe/runs.jsonl`: true.
- `! git ls-files --cached --others --exclude-standard | grep -q t0132-probe`: exit 0.
- The tool-call count command on `planner-L2.log` returned `7 "Bash"`.

## Notes
- For the filer, this is the last planner L2 line of `/tmp/t0132-probe/runs.jsonl`:
  - turns 8
  - cost_usd 0.6159388
  - duration_ms 180599
  - model opus, effort medium
- The measured run made 7 Bash tool calls. This ticket's own planner-L2 run made 8.
- `/tmp/t0132-probe` is still in place for the verifier. Nothing was committed.
