<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
Record the live Agent probe result that step 1's `--agent` mode already produced, then run the repo gates, without any criterion that compares step 1's uncommitted probe script against HEAD.

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

## Step 3: Gates green
level: L1
### Do
Run `bash plugins/sdlc-lite/scripts/check.sh` from the repo root in the foreground with the Bash timeout at 1800000. It took more than 15 minutes on this host, so do not background it. Fix any red that steps 1 and 2 introduced, for example shellcheck warnings, the probe selftest, or check.py doc guards. Keep the Bash probe behavior and the docs accurate. If a gate was already red at the build-start HEAD, report Status `inherited red: <tests>`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`

## Risks
- Step 3's `check.sh` guard takes about 15 minutes on this host (906s at load 40 to 90, green, tree unchanged). `steps.py split --only 3` with the default 300s guard timeout refuses on a timeout as a plan defect, so pass `--guard-timeout 1800`. Step 3 is unchanged from planner-L2.md, so the existing `step-3/handoff.md` is already correct and only `split --only 2` is needed.
- Step 2 has only guard criteria because its work already exists in the tree; if `agent-probe.md` were removed before the split, `split --only 2` would refuse as a red guard, and the right answer then is to run the probe again once, not to replan.
