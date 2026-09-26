## Task goal
A repeatable live probe proves, against the installed Claude Code version, that the subagent tool reaches PreToolUse as `tool_name` `Agent` (so the `"matcher": "Agent"` entry in plugins/sdlc-lite/hooks/hooks.json fires), that `hooks/block-background.sh` denies an Agent call with `run_in_background` missing or `true` under `SDLC_HEADLESS=1`, and that an Agent call with `run_in_background: false` is accepted by the tool schema and passes the hook. The probe is run once live and its result recorded in the task dir.

## Step 2: Keep the recorded live Agent probe result
level: L1
### Do
The probe already ran once live, during the first attempt at this step, and its report is `.sdlc/run-a-live-probe-to/agent-probe.md` (model haiku, Claude Code 2.1.281, deny run denied with the field absent, allow run passed with PostToolUse, `verdict: PASS`). Keep that file as the record. Do not run the probe, `claude`, or any model call again, and do not edit the report. Read it, then put its `verdict:` line and its `- claude --version:` line in your Notes. A FAIL on the tool name or on `run_in_background: false` would have been the finding to quote there; the recorded verdict is PASS, so state that there is none. Change no file: not `plugins/sdlc-lite/hooks/`, not `plugins/sdlc-lite/scripts/hook-live-probe.sh`, not the docs. Every criterion below is a guard because the record exists before this step runs. Step 1 left `hook-live-probe.sh` modified and uncommitted (builders never commit), so no criterion of this step compares that file against HEAD; the hooks dir is compared because no step of this task changes it.
### Acceptance criteria
- (guard) `test -s .sdlc/run-a-live-probe-to/agent-probe.md`
- (guard) `grep -qx '# Hook live probe (Agent)' .sdlc/run-a-live-probe-to/agent-probe.md`
- (guard) `grep -qE '^- claude --version: [0-9]' .sdlc/run-a-live-probe-to/agent-probe.md`
- (guard) `grep -q '^agent deny: tool_name ' .sdlc/run-a-live-probe-to/agent-probe.md`
- (guard) `grep -q '^agent allow: tool_name ' .sdlc/run-a-live-probe-to/agent-probe.md`
- (guard) `tail -n 1 .sdlc/run-a-live-probe-to/agent-probe.md | grep -qE '^verdict: (PASS|FAIL)'`
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/hooks` (no step of this task changes a hook)
- (guard) `test -z "$(git ls-files --others --exclude-standard -- plugins)"` (the probe leaves nothing new under the plugin)
