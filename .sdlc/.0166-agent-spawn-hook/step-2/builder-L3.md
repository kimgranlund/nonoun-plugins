<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/hook-live-probe.sh`: added a `--conductor` mode.
  - The usage line, `--help` and the header comment now list it. The header's "never passes --plugin-dir" statement now applies only to the Bash and Agent modes.
  - `--agent` and `--conductor` together is a usage error.
  - `write_capture` takes an optional hook to wrap. `run_claude` gets an optional `claude_extra` array, written to be safe under bash 3.2 `set -u`.
  - The conductor block runs two sessions with `--plugin-dir <plugin root> --agent sdlc-lite:conductor`. Its capture hook, set through `--settings`, wraps `hooks/block-role-spawn.sh`. The deny run spawns `sdlc-lite:scout` and the allow run spawns `general-purpose`, both with `run_in_background` false.
  - It prints the two `conductor deny/allow:` lines and a final verdict line. `--out` writes the markdown report, with the verdict as the last line.
  - The stub can now log the arguments it was called with (`STUB_ARGS_LOG`).
  - New selftest cases:
    - (k) deny plus allow passes. It also checks the stdout lines, the `--out` report, and that both claude runs got `--agent sdlc-lite:conductor` and `--plugin-dir <plugin root>`.
    - (l) the short `agent_type` value `conductor` passes.
    - (m) a hook that allows everything fails with "conductor deny: hook exit code 0, not 2".
    - (n) a payload with no `agent_type` fails, and the line records `(absent)`.
    - (o) no Agent call captured fails.

## Checks
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --help 2>&1 | grep -q -- --conductor`: exit 0 (pass).
- Negative control (copy of the plugin with an allow-all `block-role-spawn.sh`, then `! ... --selftest`): the selftest failed with "(k) conductor: exit 1, want 0 (verdict: FAIL: conductor deny: hook exit code 0, not 2)", so the criterion exits 0 (pass).
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: "hook live probe selftest: PASS", exit 0.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: "hook selftest: PASS", exit 0.
- Extra mutation checks, run on throwaway copies:
  - Removing `--agent sdlc-lite:conductor` from the claude arguments makes the selftest fail at (k).
  - Disabling the missing-`agent_type` check makes it fail at (n).
- `--agent --conductor` together: usage error, exit 2.
- `bash -n` on the script: clean.
- `git diff --check`: clean.
- shellcheck: not installed, so not run.

## Notes
- No live model call was made in this step. The first real `claude --agent sdlc-lite:conductor` run comes in step 3.
- The deny and allow prompts tell the conductor not to use `scripts/run.sh` instead. If the live conductor still refuses to make the call, step 3 can make the prompt stronger.
- The probe does not fail when the model spawns a different agent than the one it was told to. The `subagent_type` it actually saw is written on each line.
- Pass conditions are exactly the four the handoff names. An `agent_type` counts as a conductor only if it is `sdlc-lite:conductor` or `conductor`. Any other value fails and the reason names what was seen.
- Nothing was committed. Uncommitted changes from step 1 (`hooks.json`, `check.sh`, `hook-selftest.sh`, `block-role-spawn.sh`) were already in the tree and were not touched.
