<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add an opt-in live `claude -p` probe that captures the real PreToolUse(Bash) payload for a `run_in_background: true` call and proves `hooks/block-background.sh` denies it under `SDLC_HEADLESS=1`. Run it once, record the payload and verdict in the task dir, and keep `scripts/check.sh` green and free of live model calls.

## Step 1: Add the opt-in hook live probe script with an offline selftest
level: L3
### Do
1. Create `plugins/sdlc-lite/scripts/hook-live-probe.sh`, executable, with `set -uo pipefail`.
   - Usage: `hook-live-probe.sh [--out FILE] [--model M] [--timeout SEC] [--selftest]`.
   - Defaults: model `haiku`, timeout 120 seconds.
   - Exit contract: 0 = PASS, 1 = FAIL or inconclusive, 2 = usage or setup error (such as `jq` or the claude binary missing).
   - The claude binary is `${SDLC_PROBE_CLAUDE:-claude}`, so tests can substitute a stub.
2. Live mode:
   - Make a temp dir with `mktemp -d`. A `trap` removes it on EXIT, INT, and TERM, whatever the outcome. The probe writes nothing else apart from the `--out` file.
   - In the temp dir, write a capture wrapper hook script. It saves its stdin to `<tmp>/payload.json`, pipes that same stdin into `plugins/sdlc-lite/hooks/block-background.sh` (resolve the path from `$(dirname "$0")/../hooks`), writes the hook's exit code to `<tmp>/rc`, forwards the hook's stderr, and exits with the hook's code.
   - In the temp dir, write a settings JSON that registers the wrapper as a `PreToolUse` hook with matcher `Bash`.
   - Run the binary as `env -u SDLC_ROLE SDLC_HEADLESS=1 "$claude" -p --model "$model" --settings <tmp>/settings.json --dangerously-skip-permissions` with a short prompt. The prompt tells the model to call the Bash tool exactly once, with command `sleep 1` and `run_in_background` set to true, and then stop.
   - Bound the run by `--timeout`. macOS has no `timeout` binary, so use a bash watchdog (background `sleep` plus `kill`) or `python3` `subprocess` with a timeout. Never leave a child running.
   - Never touch user or project settings files, and never pass `--plugin-dir`.
3. Verdict:
   - PASS only when all of these hold:
     - `payload.json` exists.
     - `.tool_name == "Bash"`.
     - `(.tool_input.run_in_background | type) == "boolean"` and it is `true`.
     - The recorded hook rc is 2.
   - Otherwise FAIL, with a one-line reason: no Bash call captured, field missing, wrong JSON type (name the type), or hook exit code not 2.
   - Print the pretty-printed payload (`jq .`), the hook rc, and a final line `verdict: PASS` or `verdict: FAIL: <reason>` to stdout.
   - With `--out FILE`, write the same content as markdown to FILE:
     - a `# Hook live probe` heading;
     - the date, the model, and `claude --version` output;
     - the payload in a fenced `json` block;
     - a `hook exit code: <n>` line;
     - the verdict line as the file's last line.
4. `--selftest` runs offline and makes no model call.
   - It writes a stub claude into its own temp dir. The stub finds the `--settings` path in its args, reads the hook command from that JSON with `jq`, and pipes a fixture payload into it.
   - It runs the probe with `SDLC_PROBE_CLAUDE` pointing at the stub for these cases:
     - (a) `{"tool_name":"Bash","tool_input":{"command":"sleep 1","run_in_background":true}}` must give exit 0 and `verdict: PASS`.
     - (b) the same payload with `"run_in_background":"true"` (a string) must give exit 1 and a FAIL line that names the type.
     - (c) a stub that calls no hook must give exit 1.
     - (d) a run whose stub sleeps past a `--timeout 2` must give exit 1 within a few seconds.
   - It also checks that the probe's temp dirs are gone afterwards.
   - It prints `hook live probe selftest: PASS`, or `hook live probe selftest: FAIL: <case>` with a non-zero exit.
5. `plugins/sdlc-lite/scripts/check.sh`:
   - Add `bash "$root/scripts/hook-live-probe.sh" --selftest || fail=1` after the hook-selftest line.
   - Update the header comment to say that the probe's selftest runs offline and the live probe never runs here.
6. Docs sync:
   - In the repo-root `CLAUDE.md`, add a Commands bullet for the opt-in live probe: what it proves, that it spends one small model call, and that `check.sh` runs only its `--selftest`. Also mention the probe in the `hooks/block-background.sh` Layout bullet.
   - In `.claude/agents/sdlc-lite-author.md`, add the probe to the check.sh list on line 24, and mention it where `block-background.sh` is described.
### Acceptance criteria
- `test -x plugins/sdlc-lite/scripts/hook-live-probe.sh`
- `out=$(bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest) && grep -q "hook live probe selftest: PASS" <<<"$out"`
- `SDLC_PROBE_CLAUDE=/usr/bin/true bash plugins/sdlc-lite/scripts/hook-live-probe.sh --timeout 20; test $? -eq 1`
- `grep -q "hook-live-probe.sh\" --selftest" plugins/sdlc-lite/scripts/check.sh`
- `! grep hook-live-probe plugins/sdlc-lite/scripts/check.sh | grep -v "^#" | grep -qv -- --selftest`
- `grep -q hook-live-probe CLAUDE.md`
- `grep -q hook-live-probe .claude/agents/sdlc-lite-author.md`
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/hook-live-probe.sh`
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. It exits 0 on the current tree too.
- The verifier reads the script and confirms that live mode unsets `SDLC_ROLE` and sets `SDLC_HEADLESS=1`, passes only `--settings` (never `--plugin-dir`, never writing a settings file outside its temp dir), bounds the run with the timeout, and removes its temp dir by trap. The verifier also confirms that selftest cases (a) through (d) exist and assert the stated exit codes.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`

## Step 2: Run the live probe once and record the result; fix the hook if the live shape differs
level: L3
### Do
1. Run `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --out .sdlc/0075-confirm-with-a-live-claude/probe-result.md` once, in the foreground, with the Bash timeout at 600000.
2. If the verdict is PASS, stop here and change no code.
3. If the verdict is FAIL because the live payload shape differs (field path, JSON type, or `tool_name`):
   - Update `plugins/sdlc-lite/hooks/block-background.sh` to match the real shape.
   - Update the fixtures in `plugins/sdlc-lite/scripts/hook-selftest.sh` to use the captured shape (keep the negative cases).
   - Update the probe's selftest fixture (a) to the captured shape.
   - Rerun the probe with the same `--out` so the recorded file shows the final verdict.
4. If the FAIL means the model never made the call (no Bash call captured), rerun the probe at most twice. If there is still no call, stop with Status blocked and quote the probe output. Never edit the hook on an inconclusive run.
5. Append a short `## Notes` section to `probe-result.md`, above the verdict line, saying whether the hook or the fixtures changed and why. The verdict line stays last.
### Acceptance criteria
- `test -f .sdlc/0075-confirm-with-a-live-claude/probe-result.md`
- `tail -n1 .sdlc/0075-confirm-with-a-live-claude/probe-result.md | grep -qx "verdict: PASS"`
- `grep -Eq '"run_in_background": *true' .sdlc/0075-confirm-with-a-live-claude/probe-result.md`
- `grep -Eq '"tool_name": *"Bash"' .sdlc/0075-confirm-with-a-live-claude/probe-result.md`
- `grep -q "hook exit code: 2" .sdlc/0075-confirm-with-a-live-claude/probe-result.md`
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- The verifier confirms that the recorded payload is a real capture, not a copied fixture. It must carry fields that only Claude Code sends, such as `session_id`, `transcript_path`, or `hook_event_name`. The verifier also confirms that any change to `block-background.sh` or the fixtures matches the recorded payload.

## Risks
- If the user's global settings enable the sdlc-lite plugin, its own `block-background.sh` also fires on the probe call under `SDLC_HEADLESS=1`. It denies the same call, so this is harmless, but the capture wrapper must still run. The builder should confirm that the payload is captured.
- The model (Haiku) may refuse or skip the `run_in_background` parameter. Step 2 allows two reruns, then blocks. A larger `--model` is the fallback.
- The builder runs as a role with `SDLC_ROLE=builder`, so a nested `claude -p` inherits the hooks context. The probe unsets `SDLC_ROLE` on purpose, so the verdict proves the `SDLC_HEADLESS` path specifically.
- The `--settings` hook merging and the PreToolUse ordering relative to `--dangerously-skip-permissions` are assumed from the docs. If the hook does not fire in `-p` mode with that flag, step 2 reports FAIL with no call captured. That calls for a plan review, not a hook change.
- `check.sh` takes a few minutes, so it is a plain criterion, not a guard, to stay under the 300-second guard timeout.
