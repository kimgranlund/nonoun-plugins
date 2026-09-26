## Task goal
A repeatable live probe proves, against the installed Claude Code version, that the subagent tool reaches PreToolUse as `tool_name` `Agent` (so the `"matcher": "Agent"` entry in plugins/sdlc-lite/hooks/hooks.json fires), that `hooks/block-background.sh` denies an Agent call with `run_in_background` missing or `true` under `SDLC_HEADLESS=1`, and that an Agent call with `run_in_background: false` is accepted by the tool schema and passes the hook. The probe is run once live and its result recorded in the task dir.

## Step 1: Add the Agent mode and its offline selftest to hook-live-probe.sh
level: L3
### Do
Edit `plugins/sdlc-lite/scripts/hook-live-probe.sh`. Keep the existing Bash probe, its flags, its report and its selftest cases (a) to (e) unchanged.

1. Add the `--agent` flag and list it in `usage` so `--help` prints it. With `--agent`, live mode runs the Agent probe instead of the Bash probe. `--model`, `--timeout` (per claude run) and `--out` work the same way. Exit codes stay 0 PASS, 1 FAIL or inconclusive, 2 usage or setup error.

2. The Agent probe makes two small `claude -p` runs, each through the existing python3 process-group runner with `env -u SDLC_ROLE SDLC_HEADLESS=1`. It never uses `--plugin-dir` and never touches user or project settings. Everything goes in the mktemp dir except the `--out` file.
   - **Deny run.** The prompt tells the model to call the Agent tool once, as a general-purpose subagent with a trivial prompt, and not to set `run_in_background`.
   - **Allow run.** The prompt tells the model to call the Agent tool once with `run_in_background: false` and the subagent prompt "Reply with the word ok and use no tools".

3. Each run's `--settings <tmp>/settings.json` registers three hooks:
   - A PreToolUse capture under `"matcher": "Agent"`. It saves the first call's payload and the real `hooks/block-background.sh` exit code for that run, then pipes the payload through the hook and returns its exit code, as `capture.sh` does now.
   - A PreToolUse logger under a match-all matcher. It appends every `tool_name` it sees to a tools log. If the Agent matcher never fires, the report can then name the tool that was called instead, for example `Task`.
   - A PostToolUse recorder under `"matcher": "Agent"`. It proves the allowed call actually ran.

4. The verdict is PASS only when all of these hold. Otherwise it is FAIL with a reason that names what was wrong: no Agent call captured (list the tool names seen, e.g. `tool_name is Task`), the wrong JSON type, the wrong hook exit code, or no PostToolUse.
   - The deny run captured `tool_name` `Agent` with `run_in_background` absent or `true`, and hook exit code 2.
   - The allow run captured `tool_name` `Agent` with `run_in_background` as the JSON boolean `false`, and hook exit code 0.
   - A PostToolUse(Agent) record exists for the allow run.

5. Stdout and the `--out` report print these lines. The `--out` report starts with `# Hook live probe (Agent)`, has the same `- date:`, `- model:` and `- claude --version:` bullets as the Bash report plus both captured payloads, and ends with the verdict line.
   - `agent deny: tool_name <name>, run_in_background <json>, hook exit code <n>`
   - `agent allow: tool_name <name>, run_in_background <json>, hook exit code <n>, posttooluse <yes|no>`
   - `verdict: ...`

6. Extend the `--selftest` stub claude and cases so the selftest covers the Agent path offline (no model call):
   - Pick the payload per run from the prompt text.
   - Find hooks by matcher, not by index `[0]`.
   - Call the PostToolUse hook only when the PreToolUse hook exits 0.
   - Add cases:
     - (f) missing field plus `false`, with the real hook: PASS, exit 0. The `--out` report heading, the two `agent ...` lines, and the last line `verdict: PASS` are all present.
     - (g) payloads with `"tool_name":"Task"` (that literal JSON text appears in the script): FAIL naming `Task`.
     - (h) `run_in_background` given as the string `"false"`: FAIL.
     - (i) the allow payload denied by the hook: FAIL naming the hook exit code.
     - (j) deny payload `true` and the hook exits 0 (hook env without `SDLC_HEADLESS`): FAIL.
   - The final "no temp dir left behind" check covers the Agent runs too.

7. Update `CLAUDE.md` (the "Live hook probe" command bullet and the `hooks/block-background.sh` layout bullet) and `.claude/agents/sdlc-lite-author.md` (the hook-live-probe sentence) in the same change. Each must use the literal phrase `hook-live-probe.sh --agent` and state that the selftest covers the Agent path. Update the header comment of `hook-live-probe.sh` to match.
### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --help 2>&1 | grep -qF -- '--agent'`
- Selftest bites on an Agent-blind hook: `t=$(mktemp -d); mkdir -p "$t/scripts" "$t/hooks"; cp plugins/sdlc-lite/scripts/hook-live-probe.sh "$t/scripts/"; sed 's/"\$tool" == "Agent"/"$tool" == "NoAgent"/' plugins/sdlc-lite/hooks/block-background.sh > "$t/hooks/block-background.sh"; chmod +x "$t/hooks/block-background.sh"; bash "$t/scripts/hook-live-probe.sh" --selftest >/dev/null 2>&1; rc=$?; rm -rf "$t"; test "$rc" -ne 0`
- Selftest bites on a hook that denies `false`: `t=$(mktemp -d); mkdir -p "$t/scripts" "$t/hooks"; cp plugins/sdlc-lite/scripts/hook-live-probe.sh "$t/scripts/"; sed 's/"\$abg" != "false"/"$abg" != "nope"/' plugins/sdlc-lite/hooks/block-background.sh > "$t/hooks/block-background.sh"; chmod +x "$t/hooks/block-background.sh"; bash "$t/scripts/hook-live-probe.sh" --selftest >/dev/null 2>&1; rc=$?; rm -rf "$t"; test "$rc" -ne 0`
- `grep -qF '"tool_name":"Task"' plugins/sdlc-lite/scripts/hook-live-probe.sh`
- `grep -qF 'hook-live-probe.sh --agent' CLAUDE.md`
- `grep -qF 'hook-live-probe.sh --agent' .claude/agents/sdlc-lite-author.md`
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-live-probe.sh`
- `git diff --quiet HEAD -- plugins/sdlc-lite/hooks/hooks.json plugins/sdlc-lite/hooks/block-background.sh` (this step never changes the hooks)
