<!-- role=archaeologist level=L1 model=sonnet effort=medium -->
## Summary
The record does not name the tool call that backgrounded the work. The peer's `builder-L2.log` holds only the final result JSON, with no tool-call trace. The record does rule out the two routes the ticket suspected. Agent shows `subagent_stats.spawned: 0` in that JSON. Bash `run_in_background: true` was denied by the 0.9.0 hook if it ran, and the run still ended in "Waiting for the background job to notify." The best-fitting route is a Bash call that ran past its timeout and was auto-backgrounded by Claude Code. No hook sees that, and it still isn't covered at 0.11.1.

## Decisions
- T-0072 guards only an explicit Bash `run_in_background: true`. It exits 2 when `SDLC_ROLE` or `SDLC_HEADLESS=1` is set: commit 753993b, `hooks/block-background.sh:15-19`. The peer's 0.9.0 cache copy is the same, Bash only (`~/.claude/plugins/cache/*/sdlc-lite/0.9.0/hooks/`).
- T-0076 added the Agent route, denying unless `run_in_background` is exactly `false`, and a second `Agent` matcher in `hooks.json`: commit 12c0c9f, `block-background.sh:11-18`, `hooks/hooks.json`. It listed Workflow and Monitor as non-goals: `.sdlc/headless-conductors-can-still-abandon/handoff.md`, Intent section.
- The peer loaded 0.9.0, which has Bash-only hooks: T-0103 handoff, `hooks.json` in the 0.9.0 cache. 0.9.0 predates T-0076, so Agent was uncovered in that run.
- Run evidence in `sync-ports-2/step-1/runs.jsonl` and `builder-L2.log`:
  - 9 turns, 156.7 s, `terminal_reason: completed`, `permission_denials: []`.
  - `subagent_stats` shows 0 spawned and 0 requested in any mode.
  - The result text is "Waiting for the background job to notify."

## Landmines
- `permission_denials: []` does not prove no hook fired. A PreToolUse exit 2 may not be recorded there. I did not verify how it is recorded.
- `run.sh` does not raise the Bash timeout for role runs. `grep TIMEOUT run.sh` finds nothing, and only `bench.sh` raises it. A long foreground command can therefore be auto-backgrounded, and neither hook can see that.
- Monitor and Workflow are deliberately unguarded (T-0076 non-goals) and are still not in `hooks.json` at 0.11.1.
- The plugin cache holds several versions. The installed one is now 0.11.1 (`installed_plugins.json`, updated 2026-09-26T06:17Z). It was not necessarily 0.11.1 at run time (about 18:48 PDT on 2026-09-25).

## Inferred
- The route was most likely a Bash command that exceeded the default timeout (about 120 s, against a 156 s run) and was auto-backgrounded with a completion notification. No evidence in the log confirms it.
- Monitor is a second candidate. It is not in the 0.9.0 or 0.11.1 hooks, and the log cannot rule it out.
- Explicit Bash `run_in_background: true` in 0.9.0 is unlikely. If the hook had denied it, the model would have had no background job to wait for. The only other explanation would be `SDLC_ROLE` unset, but `run.sh:211` sets it.
- Gap for a follow-up ticket:
  - Timeout auto-backgrounding is unguarded.
  - Monitor and Workflow are unguarded.
  - The fix options are to set `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` in `run.sh`, and to add a Stop-hook or `run.sh` check for a result with no required section. The second option is already covered by T-0103's exit 3.
- To confirm the route, rerun a similar long merge step with tool tracing (`--output-format stream-json`), or capture the tool calls at run time.
