<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0075: Add an opt-in live claude -p probe for the Bash PreToolUse background hook

## PR body
### Summary
Until now, `hooks/block-background.sh` had only been tested against fixtures. If Claude Code sent a different payload shape, the hook would stop working without any error. This PR adds a probe that runs one real `claude -p` session and captures the PreToolUse(Bash) payload for a `run_in_background: true` call. The probe then checks that the hook denies that call when `SDLC_HEADLESS=1`. We ran it once. The live payload matches the fixtures (`tool_input.run_in_background` is a JSON boolean `true`) and the hook exited 2, so the hook and fixtures did not need changes.

### Changes
- `plugins/sdlc-lite/scripts/hook-live-probe.sh` (new): `[--out FILE] [--model M] [--timeout SEC] [--selftest]`, default model haiku. Exit codes: 0 PASS, 1 FAIL, 2 setup error.
  - It unsets `SDLC_ROLE`, sets `SDLC_HEADLESS=1`, and registers a capture wrapper only through `--settings` in a `mktemp -d` dir, with no `--plugin-dir`.
  - A python3 process-group watchdog enforces the timeout, and a trap removes the temp dir on EXIT, INT and TERM.
  - `--selftest` runs offline against a stub claude. It covers four cases: a boolean PASS, a string-typed FAIL that names the type, no hook call, and a timeout. It also checks that no temp dirs are left behind.
- `plugins/sdlc-lite/scripts/check.sh`: runs `hook-live-probe.sh --selftest` only. The live probe never runs from check.sh.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: new Commands bullet for the probe, and it is added to the check.sh list and the `block-background.sh` notes.
- `.sdlc/confirm-with-a-live-claude/probe-result.md`: the recorded live run (haiku, Claude Code 2.1.281). It holds the payload, `hook exit code: 2` and `verdict: PASS`.

### Verification
- Step 1 (verifier L2: pass):
  - All criteria passed: the selftest, the `/usr/bin/true` stub exiting 1, the check.sh wiring greps, shellcheck, `check.sh` exit 0, and the hook-selftest guard.
  - The verifier broke the probe in throwaway copies to see if the selftest catches it. Removing the string-type check, the `SDLC_HEADLESS` setting, the cleanup, or the timeout each turned the selftest red.
- Step 2 (verifier L2: pass):
  - All grep criteria on `probe-result.md` passed, and so did `check.sh` and the hook-selftest guard.
  - The payload is a real capture, not a copied fixture. It carries `session_id`, `transcript_path`, `prompt_id` and `tool_use_id`, none of which appear in any fixture. The matching session transcript also exists on disk.
  - `git diff` confirms the hook and fixtures are unchanged.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Added `scripts/hook-live-probe.sh`, an opt-in probe that makes one real `claude -p` call (haiku by default). It confirms that the live PreToolUse(Bash) payload carries `tool_input.run_in_background` as a JSON boolean and that `block-background.sh` denies the call when `SDLC_HEADLESS=1`. `check.sh` runs only its offline `--selftest`.

## Follow-ups
- Add a hook-live-probe.sh selftest case where the hook exits with a code other than 2; the step 1 verifier found that removing the rc==2 check leaves the selftest green.
