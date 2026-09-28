# Run readiness and recovery

Resolve the installed plugin root from the invoking skill. Run readiness before starting a workflow:

```sh
python3 "<plugin-root>/scripts/readiness.py" --backend claude --project "<project-root>"
python3 "<plugin-root>/scripts/readiness.py" --backend codex --transport subagent --project "<project-root>"
```

Use `--transport exec` for standalone Codex execution. These read-only checks inspect tools, Git baseline, plugin configuration, and Codex generated/project agents as applicable. They do not authenticate, spend a model call, or establish that an existing Codex chat loaded new agents. For native dispatch, confirm the exact named agent is available and that the host has delegation capacity. Fix reported setup issues before dispatch; do not widen permissions to pass a check. The shared role runner also performs local readiness checks.

Set `SDLC_ROUTING_REASON` per invocation to the reason for the selected role and level: user selection, task scope, or recorded escalation evidence. Keep the current model/effort mappings. Without a reason, the runner explicitly records that the caller supplied no task-specific rationale.

Every actual runner invocation reserves a unique `<role>-<level>[-N].attempt.json` before launching the backend. It captures the attempt ID, selected role/level/model/effort, backend/transport, reason, timestamps, and terminal exit status. Normal `runs.jsonl` rows carry the same ID and reason. A `completed` attempt means the runner accepted the report format and exited successfully; inspect the role's Status/Verdict for the actual work outcome. A failed or blocked verification is not task completion.

A handoff directory permits only one active pipeline run. Put roles that must run in parallel in separate handoff directories. A duplicate launch fails instead of overlapping a build and verification against the same handoff. Failed attempts and logs are never overwritten by retries.

```sh
python3 "<plugin-root>/scripts/run_lifecycle.py" status "<handoff-directory>"
python3 "<plugin-root>/scripts/run_lifecycle.py" recover "<handoff-directory>"
```

Status reads attempt records; `running` may be stale after a forced process kill. Recovery acquires the directory lock and refuses while a local runner still owns it. Once unlocked, it marks unfinished attempts interrupted and clears their stale display markers, preserving logs and reports. The Claude exec runner performs this recovery automatically after acquiring the lock, then starts a fresh attempt. Codex runs still refuse stale records until explicit recovery. Recovery never reruns work, publishes a result, rolls back edits, or interprets an old report as new evidence.

Before manually retrying, inspect the actual working tree, logs, and prior report. A headless Claude conductor can continue after automatic recovery; it should use the preserved attempt record to recognize the interruption. For Codex native transport, the parent must also stop or await the previously dispatched native agent using the host tools: cancelling a shell waiter cannot cancel a separately hosted subagent. Then rerun the original command as a fresh attempt. Do not replay a late report; native responses are bound to a unique request and its live owner. Recovery does not resume an LLM conversation or guarantee host-managed children have stopped.
