# Hook live probe (conductor)

Dated live run for T-0166, made with `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --conductor --out docs/validation/agent-spawn-hook-live-run.md` from the repository root. It shows that a plugin session agent launched with `claude -p --plugin-dir <plugin> --agent sdlc-lite:conductor` sends `agent_type` `sdlc-lite:conductor` in the PreToolUse(Agent) payload, that `hooks/block-role-spawn.sh` denies an Agent spawn of `sdlc-lite:scout` from that session (exit 2), and that it lets a `general-purpose` spawn through (exit 0). It does not show the `agent_type` value for a conductor declared interactively through `"agent": "sdlc-lite:conductor"` in `.claude/settings.json`; that path was not observed. It says nothing about Codex, which has no equivalent enforcement.

- date: 2026-09-30T01:58:34Z
- model: haiku
- claude --version: 2.1.285 (Claude Code)

Captured PreToolUse(Agent) payload, deny run:

```json
{
  "session_id": "490cdf1a-3845-4a9b-9b0f-46906935b9c0",
  "transcript_path": "/Users/kimgranlund/.claude/projects/-private-var-folders-n0-b1pq09652mbd8kncmz8tgkvc0000gn-T-hook-live-probe-3IQqEC-deny/490cdf1a-3845-4a9b-9b0f-46906935b9c0.jsonl",
  "cwd": "/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/hook-live-probe.3IQqEC/deny",
  "prompt_id": "71833332-4664-4af4-89f6-1c355f31ab74",
  "permission_mode": "bypassPermissions",
  "agent_type": "sdlc-lite:conductor",
  "hook_event_name": "PreToolUse",
  "tool_name": "Agent",
  "tool_input": {
    "description": "hook probe",
    "prompt": "Say hello",
    "subagent_type": "sdlc-lite:scout",
    "run_in_background": false
  },
  "tool_use_id": "toolu_01DW6jx6fTwgycLQgyHLEyjY"
}
```

Captured PreToolUse(Agent) payload, allow run:

```json
{
  "session_id": "fb30208e-2deb-4abc-b12e-479999905ef1",
  "transcript_path": "/Users/kimgranlund/.claude/projects/-private-var-folders-n0-b1pq09652mbd8kncmz8tgkvc0000gn-T-hook-live-probe-3IQqEC-allow/fb30208e-2deb-4abc-b12e-479999905ef1.jsonl",
  "cwd": "/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/hook-live-probe.3IQqEC/allow",
  "prompt_id": "5a95e3d3-774a-4cad-82dd-ca97dd556414",
  "permission_mode": "bypassPermissions",
  "agent_type": "sdlc-lite:conductor",
  "hook_event_name": "PreToolUse",
  "tool_name": "Agent",
  "tool_input": {
    "description": "hook probe",
    "prompt": "Reply with the word ok and use no tools",
    "subagent_type": "general-purpose",
    "run_in_background": false
  },
  "tool_use_id": "toolu_01TxVvskYjUsgWF84USD5FPW"
}
```

conductor deny: agent_type sdlc-lite:conductor, subagent_type sdlc-lite:scout, hook exit code 2
conductor allow: agent_type sdlc-lite:conductor, subagent_type general-purpose, hook exit code 0

verdict: PASS
