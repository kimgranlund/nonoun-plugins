## Task goal
A repeatable live probe proves, against the installed Claude Code version, that the subagent tool reaches PreToolUse as `tool_name` `Agent` (so the `"matcher": "Agent"` entry in plugins/sdlc-lite/hooks/hooks.json fires), that `hooks/block-background.sh` denies an Agent call with `run_in_background` missing or `true` under `SDLC_HEADLESS=1`, and that an Agent call with `run_in_background: false` is accepted by the tool schema and passes the hook. The probe is run once live and its result recorded in the task dir.

## Step 2: Run the Agent probe live once and record the result
level: L1
### Do
From the repo root, run the probe in the foreground with the Bash timeout at 600000 or more (never `run_in_background`):

`bash plugins/sdlc-lite/scripts/hook-live-probe.sh --agent --out .sdlc/0092-run-a-live-probe-to/agent-probe.md`

It uses the default model haiku.

- **Inconclusive** (the model made no Agent call, or claude timed out): rerun once with `--model sonnet` to the same `--out` path. Say in your Notes that you did.
- **FAIL on the tool name or on `run_in_background: false`:** record it as the finding in your Notes, quoting the verdict line. Do not edit `hooks.json`, `block-background.sh`, or the probe.
- **Any result:** put the verdict line and the `claude --version` in your Notes. Change no other file.
### Acceptance criteria
- `test -s .sdlc/0092-run-a-live-probe-to/agent-probe.md`
- `grep -qx '# Hook live probe (Agent)' .sdlc/0092-run-a-live-probe-to/agent-probe.md`
- `grep -qE '^- claude --version: [0-9]' .sdlc/0092-run-a-live-probe-to/agent-probe.md`
- `grep -q '^agent deny: tool_name ' .sdlc/0092-run-a-live-probe-to/agent-probe.md`
- `grep -q '^agent allow: tool_name ' .sdlc/0092-run-a-live-probe-to/agent-probe.md`
- `tail -n 1 .sdlc/0092-run-a-live-probe-to/agent-probe.md | grep -qE '^verdict: (PASS|FAIL)'`
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/hook-live-probe.sh` (the live run changes no code)
