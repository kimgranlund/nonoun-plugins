<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `.sdlc/confirm-with-a-live-claude/probe-result.md`: new file. The live probe wrote it, and I added a `## Notes` section above the last line, `verdict: PASS`.

## Checks
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --out .sdlc/confirm-with-a-live-claude/probe-result.md`: exit 0, `verdict: PASS`. It ran on haiku with Claude Code 2.1.281, the hook exit code was 2, and the captured payload has `tool_name: "Bash"` and `tool_input.run_in_background: true` (a JSON boolean). It ran once and no rerun was needed.
- `test -f .sdlc/confirm-with-a-live-claude/probe-result.md`: exit 0
- `tail -n1 ... | grep -qx "verdict: PASS"`: exit 0
- `grep -Eq '"run_in_background": *true' ...`: exit 0
- `grep -Eq '"tool_name": *"Bash"' ...`: exit 0
- `grep -q "hook exit code: 2" ...`: exit 0
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` (guard): exit 0, `hook selftest: PASS`
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Every selftest passed, including `hook live probe selftest: PASS`, and so did shellcheck and plugin validate.

## Notes
- The live payload has the same shape as the fixtures, so I left `hooks/block-background.sh`, `scripts/hook-selftest.sh` and the probe's selftest fixture unchanged.
- The recorded payload also carries fields that only Claude Code sends: `session_id`, `transcript_path`, `cwd`, `prompt_id`, `permission_mode`, `hook_event_name: "PreToolUse"` and `tool_use_id`. The verifier can use these to confirm it is a real capture and not a copied fixture.
- The other modified and untracked files in `git status` were already in the tree when this step started. This step did not touch them.
