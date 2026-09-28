<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
No verifier result exists for this task. No plan, builder, or verifier file is present either. The only artifact is one archaeologist L1 result, `archaeologist-L1.md`, and it is unverified. The tool call that backgrounded the work was not confirmed. The conclusion below is inferred from the peer repo's final result JSON, which has no tool-call trace.

## PR title
T-0105: Record why the T-0072 background hook did not stop the T-0103 run

## PR body
**Summary**

This is an investigation only, with no code changes. It asks why the abandoned builder L2 run in T-0103 ended its turn with "Waiting for the background job to notify." when the T-0072 hook should have blocked background work. The archaeologist could not confirm a single cause. It ruled out two suspected routes and named the most likely one.

**What the record shows**
- The peer run loaded plugin 0.9.0, whose hooks cover only an explicit Bash `run_in_background: true` (commit 753993b).
- The Agent guard came later, in T-0076 (commit 12c0c9f), so Agent was uncovered in that run.
- The run's result JSON shows `subagent_stats.spawned: 0`, so Agent did not start work.
- The same JSON shows `permission_denials: []`. The archaeologist did not verify whether a PreToolUse exit 2 is recorded there, so this does not prove that no hook fired.
- If Bash `run_in_background: true` had been denied, the model would have had no background job to wait for. `run.sh:211` sets `SDLC_ROLE`, so an unset variable is unlikely.
- The best-fitting route is a Bash call that outlived its timeout and was auto-backgrounded by Claude Code. The run lasted 156.7 s against a default timeout of about 120 s. No hook sees this route.
- `run.sh` does not raise the Bash timeout (`grep TIMEOUT run.sh` finds nothing). Only `bench.sh` raises it.
- Monitor is a second candidate. Monitor and Workflow are deliberate T-0076 non-goals and are still absent from `hooks.json` at 0.11.1.

**Changes**

The only change is the ticket's investigation artifact, `.sdlc/0105-find-out-why-the-t/archaeologist-L1.md`, plus its run log. No plugin files were edited.

**How each was verified**
- The archaeologist read the peer repo's `builder-L2.log`, `runs.jsonl`, the 0.9.0 plugin cache, the hook git history (753993b, 12c0c9f), and the T-0072 and T-0076 handoffs. All of it was read-only.
- Nothing was reproduced, and no tool trace was captured. The auto-background explanation is an inference.
- No verifier ran.

## Changelog entry
None. This is a read-only investigation with no shipped change.

## Follow-ups
- Set `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` in `run.sh` for role runs, because a Bash call that outlives the default timeout is auto-backgrounded and no hook sees it (the likely cause of the T-0103 abandon).
- Confirm the T-0103 abandon route by rerunning a similar long merge step with `--output-format stream-json` tool tracing, since the peer log has no tool-call trace and the auto-background cause is only inferred.
- Decide whether to guard Monitor and Workflow backgrounding in headless role runs (`hooks.json` and `block-background.sh` at 0.11.1 leave both uncovered, a T-0076 non-goal), since Monitor is still a candidate for the T-0103 route.
