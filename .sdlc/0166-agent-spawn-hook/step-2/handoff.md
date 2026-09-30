## Task goal
When the SDLC Lite conductor is in force, an Agent-tool spawn of another plugin's builder, verifier, or planner agent is flagged before it runs, with a message pointing at `run.sh`.

## Step 2: Add a --conductor mode to hook-live-probe.sh
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
In `plugins/sdlc-lite/scripts/hook-live-probe.sh`, add a `--conductor` mode next to `--agent`, and add it to the usage line and header comment. The mode runs two small `claude -p` sessions as the plugin's conductor: `--plugin-dir <plugin root>` and `--agent sdlc-lite:conductor`. This mode deliberately loads the plugin, so the header's statement that the probe never passes `--plugin-dir` needs amending for this mode only. The capture hook comes from `--settings` as in the other modes, and it wraps `hooks/block-role-spawn.sh` rather than block-background.sh.
- The deny run tells the model to call the Agent tool once with `subagent_type` `sdlc-lite:scout` and `run_in_background` false. Because run_claude sets `SDLC_HEADLESS=1`, block-background.sh must also pass it.
- The allow run tells the model to call the Agent tool once with `general-purpose` and `run_in_background` false.

Print these lines:
- `conductor deny: agent_type <value>, subagent_type <value>, hook exit code <n>`
- `conductor allow: agent_type <value>, subagent_type <value>, hook exit code <n>`
- a final `verdict: PASS` or `verdict: FAIL: <reason>`

It passes only when both runs capture a PreToolUse(Agent) payload, both have a conductor `agent_type` (record the exact value), the deny run's hook exits 2, and the allow run's hook exits 0. `--out FILE` writes a markdown report with the date, model, `claude --version`, both captured payloads, both lines, and the verdict as the last line.

Extend the offline `--selftest` stub with at least these cases:
- conductor deny + allow passes
- the hook exits 0 on the deny run: FAIL naming the hook exit code
- no `agent_type` in the payload: FAIL
- no Agent call captured: FAIL

This step makes no live model call.
### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --help 2>&1 | grep -q -- --conductor`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts "$d"/ && printf "#!/bin/sh\nexit 0\n" > "$d/hooks/block-role-spawn.sh" && chmod +x "$d/hooks/block-role-spawn.sh" && ! bash "$d/scripts/hook-live-probe.sh" --selftest` (negative control: the probe selftest fails when the hook allows everything)
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
