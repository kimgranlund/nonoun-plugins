# Hook live probe

- date: 2026-09-26T01:02:02Z
- model: haiku
- claude --version: 2.1.281 (Claude Code)

Captured PreToolUse(Bash) payload:

```json
{
  "session_id": "d487df55-4ea5-49b3-a88a-34db2afca045",
  "transcript_path": "/Users/kimba/.claude/projects/-private-var-folders-0b-jf4lh4jd4sd9y2q7x271c9jm0000gn-T-hook-live-probe-9pymXw/d487df55-4ea5-49b3-a88a-34db2afca045.jsonl",
  "cwd": "/private/var/folders/0b/jf4lh4jd4sd9y2q7x271c9jm0000gn/T/hook-live-probe.9pymXw",
  "prompt_id": "e0388fbc-267c-4d50-96d4-2a87c59bb528",
  "permission_mode": "bypassPermissions",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "sleep 1",
    "run_in_background": true
  },
  "tool_use_id": "toolu_01SdcpmiuRBp9fG7XmLh3uY7"
}
```

hook exit code: 2

## Notes

No change to hooks/block-background.sh or to the fixtures in scripts/hook-selftest.sh. The live payload matches the fixture shape: tool_name is "Bash" and tool_input.run_in_background is the JSON boolean true, and the hook denied the call with exit code 2 under SDLC_HEADLESS=1.

verdict: PASS
