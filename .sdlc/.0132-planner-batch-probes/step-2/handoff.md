## Task goal
Planner runs keep rule 1's criterion probing but use fewer requests and less context.

## Step 2: Gates green and live planner measurement
level: L2
### Do
Run `plugins/sdlc-lite/scripts/check.sh` from the worktree toplevel and fix any red that step 1 introduced (the check.py entry and the planner.md phrase must agree). It takes about two minutes here. A `hook selftest: FAIL: block-pattern-kill without role: exit 141` line is the known intermittent SIGPIPE flake tracked as T-0133, not a step 1 defect: rerun check.sh once and record both outcomes in Notes.

Then take one live measurement outside the repo:
1. `mkdir -p /tmp/t0132-probe`, then copy `.sdlc/.0137-the-steps-py-lint-accepts/handoff.md` (T-0137, an open ticket whose handoff is 865 bytes and whose change is one lint tweak in `steps.py`, so its criteria are red today) to `/tmp/t0132-probe/handoff.md`. Copy only that file, no plan or step artifacts.
2. From the worktree toplevel, run `plugins/sdlc-lite/scripts/run.sh planner L2 /tmp/t0132-probe/handoff.md` as a foreground Bash call with the Bash `timeout` at 900000 or more. run.sh loads this worktree's plugin through `--plugin-dir`, so the run uses the new rule 1, and it writes `planner-L2.md`, `planner-L2.log`, and a `runs.jsonl` line into `/tmp/t0132-probe/` only. Nested `claude -p` runs work here (fanout lanes launch role runs from a headless conductor the same way).
3. Record that run's `turns` and `cost_usd` from the last planner L2 line of `/tmp/t0132-probe/runs.jsonl` in the builder result's `## Notes`, for the filer, and count its Bash tool calls (`jq -R -c 'fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name' /tmp/t0132-probe/planner-L2.log | sort | uniq -c`) so the filer can compare with the 8 Bash calls of this ticket's own planner-L2 run.

Nothing from `/tmp/t0132-probe` goes into the repo, and nothing is committed. Leave `/tmp/t0132-probe` in place for the verifier. Change no model or effort.
### Acceptance criteria
- `test -s /tmp/t0132-probe/planner-L2.md`
- `jq -se 'map(select(.role=="planner" and .level=="L2")) | length > 0 and (last.turns < 11.5)' /tmp/t0132-probe/runs.jsonl`
- The builder result's Notes state the measured run's turns and cost_usd, and they match the last planner L2 line of `/tmp/t0132-probe/runs.jsonl`.
- (guard) `! git ls-files --cached --others --exclude-standard | grep -q t0132-probe`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
