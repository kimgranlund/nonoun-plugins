## Task goal
Evidence from a real `claude -p` session, not a fixture, of the exact JSON shape Claude Code sends a PreToolUse(Bash) hook when the model calls Bash with `run_in_background: true` (field path `tool_input.run_in_background`, JSON type boolean), and proof that `hooks/block-background.sh` denies that live call when `SDLC_HEADLESS=1`. If the live shape differs from the fixtures, fix the hook and the fixtures in `scripts/hook-selftest.sh` to match.

Done when: a repeatable probe script exists (for example `scripts/hook-live-probe.sh`, opt-in, never run by `check.sh` because it spends a model call), it has been run once with its captured payload and verdict recorded in the task dir, and `scripts/check.sh` stays green. (Clarified by the conductor, unattended.)

## Step 2: Run the live probe once and record the result; fix the hook if the live shape differs
level: L3
### Do
1. Run `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --out .sdlc/confirm-with-a-live-claude/probe-result.md` once, in the foreground, with the Bash timeout at 600000.
2. If the verdict is PASS, stop here and change no code.
3. If the verdict is FAIL because the live payload shape differs (field path, JSON type, or `tool_name`):
   - Update `plugins/sdlc-lite/hooks/block-background.sh` to match the real shape.
   - Update the fixtures in `plugins/sdlc-lite/scripts/hook-selftest.sh` to use the captured shape (keep the negative cases).
   - Update the probe's selftest fixture (a) to the captured shape.
   - Rerun the probe with the same `--out` so the recorded file shows the final verdict.
4. If the FAIL means the model never made the call (no Bash call captured), rerun the probe at most twice. If there is still no call, stop with Status blocked and quote the probe output. Never edit the hook on an inconclusive run.
5. Append a short `## Notes` section to `probe-result.md`, above the verdict line, saying whether the hook or the fixtures changed and why. The verdict line stays last.
### Acceptance criteria
- `test -f .sdlc/confirm-with-a-live-claude/probe-result.md`
- `tail -n1 .sdlc/confirm-with-a-live-claude/probe-result.md | grep -qx "verdict: PASS"`
- `grep -Eq '"run_in_background": *true' .sdlc/confirm-with-a-live-claude/probe-result.md`
- `grep -Eq '"tool_name": *"Bash"' .sdlc/confirm-with-a-live-claude/probe-result.md`
- `grep -q "hook exit code: 2" .sdlc/confirm-with-a-live-claude/probe-result.md`
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- The verifier confirms that the recorded payload is a real capture, not a copied fixture. It must carry fields that only Claude Code sends, such as `session_id`, `transcript_path`, or `hook_event_name`. The verifier also confirms that any change to `block-background.sh` or the fixtures matches the recorded payload.
