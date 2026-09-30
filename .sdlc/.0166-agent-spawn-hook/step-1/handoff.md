## Task goal
When the SDLC Lite conductor is in force, an Agent-tool spawn of another plugin's builder, verifier, or planner agent is flagged before it runs, with a message pointing at `run.sh`.

## Step 1: Add hooks/block-role-spawn.sh, register it, add selftest fixtures
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/hooks/block-role-spawn.sh` (executable, bash, `set -uo pipefail`, reads the PreToolUse JSON from stdin with jq, in the style of `hooks/block-background.sh`). Behavior:
- Exit 0 unless `.tool_name` is `Agent`.
- The session counts as the conductor when `.agent_type` is `sdlc-lite:conductor` or bare `conductor`, or when the env var `SDLC_ROLE` is `conductor` (fanout lane drivers set this). Otherwise exit 0. A session with no `agent_type` and no `SDLC_ROLE=conductor` is never blocked. The hook must not block non-conductor sessions (handoff constraint).
- Read `.tool_input.subagent_type`. Deny (exit 2) when either of these holds:
  - (a) It starts with `sdlc-lite:`. Any SDLC Lite role agent has a run.sh role.
  - (b) It is plugin-qualified (`<plugin>:<name>`), and `<name>`, split on `-` and `_`, contains a token `builder`, `verifier`, `reviewer`, `planner`, or `checker`, matching the rule text in `agents/conductor.md` line 24.
- Everything else exits 0: `Explore`, `general-purpose`, `Plan`, `claude`, a missing subagent_type, and `harness:fact-finder`. Read-only helpers are a non-goal to block.
- On deny, stderr names the subagent_type and says that planner, builder, and verifier work runs through `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh`, never the Agent tool. The text must contain the literal `run.sh`.
- The hook denies with exit 2 rather than only warning. The handoff allows either, and the conductor contract already forbids these spawns.

Register it in `plugins/sdlc-lite/adapters/claude/hooks.json` as a second command in the existing `"matcher": "Agent"` entry, after block-background.sh. Do not create `hooks/hooks.json`.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, add a `rs="$hooks/block-role-spawn.sh"` variable, a header-comment sentence, and fixtures run through the existing `run` helper:
- Exit 2 cases:
  - conductor agent_type + `sdlc-lite:builder`, with stderr containing `run.sh`
  - conductor + `sdlc-lite:scout`
  - conductor + `other:code-reviewer`
  - conductor + `harness:agent-checker`
  - bare `conductor` agent_type + `sdlc-lite:verifier`
  - no agent_type with `SDLC_ROLE=conductor` + `sdlc-lite:planner`
- Exit 0 cases:
  - conductor + `Explore`
  - conductor + `general-purpose`
  - conductor + `harness:fact-finder`
  - no agent_type + `sdlc-lite:builder`
  - agent_type `probecond` + `sdlc-lite:builder`
  - `tool_name` Bash with conductor

Add `block-role-spawn.sh` to the hook list in the header comment of `plugins/sdlc-lite/scripts/check.sh`.
### Acceptance criteria
- `test -x plugins/sdlc-lite/hooks/block-role-spawn.sh`
- `printf "%s" "{\"tool_name\":\"Agent\",\"agent_type\":\"sdlc-lite:conductor\",\"tool_input\":{\"subagent_type\":\"sdlc-lite:builder\",\"prompt\":\"x\"}}" | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-role-spawn.sh; test $? -eq 2`
- `printf "%s" "{\"tool_name\":\"Agent\",\"agent_type\":\"sdlc-lite:conductor\",\"tool_input\":{\"subagent_type\":\"sdlc-lite:builder\",\"prompt\":\"x\"}}" | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-role-spawn.sh 2>&1 >/dev/null | grep -q run.sh`
- `printf "%s" "{\"tool_name\":\"Agent\",\"agent_type\":\"sdlc-lite:conductor\",\"tool_input\":{\"subagent_type\":\"Explore\",\"prompt\":\"x\"}}" | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-role-spawn.sh`
- `printf "%s" "{\"tool_name\":\"Agent\",\"tool_input\":{\"subagent_type\":\"sdlc-lite:builder\",\"prompt\":\"x\"}}" | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-role-spawn.sh`
- `jq -e ".hooks.PreToolUse[] | select(.matcher==\"Agent\") | .hooks[].command | select(contains(\"block-role-spawn.sh\"))" plugins/sdlc-lite/adapters/claude/hooks.json`
- `d=$(mktemp -d) && cp -R plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts "$d"/ && printf "#!/bin/sh\nexit 0\n" > "$d/hooks/block-role-spawn.sh" && chmod +x "$d/hooks/block-role-spawn.sh" && ! bash "$d/scripts/hook-selftest.sh"` (negative control: the selftest fails when the hook allows everything)
- `grep -q block-role-spawn plugins/sdlc-lite/scripts/check.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
