<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add a Claude Code `PreToolUse(Agent)` hook. When the session runs as the SDLC Lite conductor, it denies an Agent-tool spawn of an SDLC Lite role agent or another plugin's builder, verifier, reviewer, planner, or checker agent, and its message points at `run.sh`. The step also adds an offline selftest with a negative control, a live conductor probe with recorded evidence, and docs that say Codex is not covered.

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

## Step 3: Live conductor run, evidence, and docs
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --conductor --out docs/validation/agent-spawn-hook-live-run.md` from the repository root in the foreground. This spends model calls; the handoff's done-condition asks for live evidence.
- If the recorded `agent_type` is neither `sdlc-lite:conductor` nor `conductor`, change the match in `hooks/block-role-spawn.sh` and its selftest fixtures to the observed value, then rerun.
- If the conductor model refuses the call, strengthen the probe prompt rather than weakening the checks.
- Add a short note under the report's heading on what it proves: the observed `agent_type` for a plugin session agent. It does not prove the interactive `.claude/settings.json` agent path, unless you also observe that path and record it there.

Add a `## \`hooks/block-role-spawn.sh\`` section to `docs/maintenance/claude-hooks.md` covering:
- the event and matcher
- conductor detection
- the deny rule and the allowed helpers
- the fixtures' location and the `--conductor` probe
- the statement that this is a Claude hook only and Codex conductor sessions are not enforced

In `plugins/sdlc-lite/agents/conductor.md` line 24, add one sentence: in Claude Code, `hooks/block-role-spawn.sh` denies such spawns, and Codex has no equivalent enforcement. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`.
### Acceptance criteria
- `test -f docs/validation/agent-spawn-hook-live-run.md`
- `test "$(tail -n 1 docs/validation/agent-spawn-hook-live-run.md)" = "verdict: PASS"`
- `grep -qE "^conductor deny: agent_type [^ ]*conductor, .*hook exit code 2$" docs/validation/agent-spawn-hook-live-run.md`
- `grep -qE "^conductor allow: agent_type [^ ]*conductor, .*hook exit code 0$" docs/validation/agent-spawn-hook-live-run.md`
- `grep -qF "## \`hooks/block-role-spawn.sh\`" docs/maintenance/claude-hooks.md`
- `awk "/^## \`hooks\/block-role-spawn.sh\`/{f=1;next} /^## /{f=0} f" docs/maintenance/claude-hooks.md | grep -q Codex`
- `grep -q block-role-spawn.sh plugins/sdlc-lite/agents/conductor.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below and fix any red that the earlier steps introduced, in the files those steps changed. A gate that was already red at the build-start HEAD is reported as `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`

## Risks
- The `agent_type` value for a plugin session agent is unverified. It may be `sdlc-lite:conductor`, `conductor`, or something else. Step 3 pins it live and adjusts the hook. The interactive `.claude/settings.json` path may still differ and is not proven by the `claude -p --agent` probe.
- The conductor's own contract forbids spawning SDLC Lite role agents, so the conductor model may refuse the probe's deny-run call, and the probe prompt may need several tries.
- `--plugin-dir` may duplicate hooks if the plugin is also installed in the user's plugin cache, which could make capture or exit codes noisy.
- The token rule (builder, verifier, reviewer, planner, checker) can over-match a plugin agent named, for example, `docs-checker` that is harmless. The conductor rule text treats checkers as off-limits too, so this is accepted.
- shellcheck is not installed on this host, so check.sh skips it and shell lint of the new hook is not proven here.
