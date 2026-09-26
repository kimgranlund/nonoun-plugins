# Hook live probe (Agent)

- date: 2026-09-26T15:49:16Z
- model: haiku
- claude --version: 2.1.281 (Claude Code)

Captured PreToolUse(Agent) payload, deny run:

```json
{
  "session_id": "01cd4fed-b27b-4287-8524-9bd00d71af4d",
  "transcript_path": "/Users/kimba/.claude/projects/-private-var-folders-0b-jf4lh4jd4sd9y2q7x271c9jm0000gn-T-hook-live-probe-Y8xgYe-deny/01cd4fed-b27b-4287-8524-9bd00d71af4d.jsonl",
  "cwd": "/private/var/folders/0b/jf4lh4jd4sd9y2q7x271c9jm0000gn/T/hook-live-probe.Y8xgYe/deny",
  "prompt_id": "1f5505b9-803e-4f29-a0b7-1ffdf1041e41",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "PreToolUse",
  "tool_name": "Agent",
  "tool_input": {
    "description": "hook probe",
    "prompt": "Say hello",
    "subagent_type": "general-purpose"
  },
  "tool_use_id": "toolu_01Ve9D15vT1fiJbesxFsGy84"
}
```

Captured PreToolUse(Agent) payload, allow run:

```json
{
  "session_id": "5f61bf73-4a2e-4355-ba57-4dbaef1cf7f4",
  "transcript_path": "/Users/kimba/.claude/projects/-private-var-folders-0b-jf4lh4jd4sd9y2q7x271c9jm0000gn-T-hook-live-probe-Y8xgYe-allow/5f61bf73-4a2e-4355-ba57-4dbaef1cf7f4.jsonl",
  "cwd": "/private/var/folders/0b/jf4lh4jd4sd9y2q7x271c9jm0000gn/T/hook-live-probe.Y8xgYe/allow",
  "prompt_id": "c8631da1-4045-47f0-a0a0-a0f78a135151",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "PreToolUse",
  "tool_name": "Agent",
  "tool_input": {
    "description": "hook probe",
    "prompt": "Reply with the word ok and use no tools",
    "subagent_type": "general-purpose",
    "run_in_background": false
  },
  "tool_use_id": "toolu_012NMCxwYDSAJbFhY9ZhYq97"
}
```

agent deny: tool_name Agent, run_in_background (absent), hook exit code 2
agent allow: tool_name Agent, run_in_background false, hook exit code 0, posttooluse yes

verdict: PASS
