## Task goal
Evidence from a real `claude -p` session, not a fixture, of the exact JSON shape Claude Code sends a PreToolUse(Bash) hook when the model calls Bash with `run_in_background: true` (field path `tool_input.run_in_background`, JSON type boolean), and proof that `hooks/block-background.sh` denies that live call when `SDLC_HEADLESS=1`. If the live shape differs from the fixtures, fix the hook and the fixtures in `scripts/hook-selftest.sh` to match.

Done when: a repeatable probe script exists (for example `scripts/hook-live-probe.sh`, opt-in, never run by `check.sh` because it spends a model call), it has been run once with its captured payload and verdict recorded in the task dir, and `scripts/check.sh` stays green. (Clarified by the conductor, unattended.)

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
