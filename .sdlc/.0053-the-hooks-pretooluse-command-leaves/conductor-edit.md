# Conductor trivial edit (T-0053)

The conductor made this one-line change itself (trivial-edit rule: a quoting fix whose effect the validator and a direct run check). No planner, builder, or verifier ran.

## Change
`plugins/sdlc-lite/hooks/hooks.json`: `"command": "${CLAUDE_PLUGIN_ROOT}/hooks/block-publish.sh"` became `"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/block-publish.sh\""`.

## Evidence
- Before: `claude plugin validate plugins/sdlc-lite` printed `hooks.PreToolUse: Shell command uses ${CLAUDE_PLUGIN_ROOT} without quotes`. After: `✔ Validation passed`, no warnings.
- Behavior with a spaced path: copied the hook into `/tmp/sp ace.XXXX/hooks/`, expanded the command from hooks.json, fed `{"tool_input":{"command":"git push"}}` with `SDLC_ROLE=builder` through `sh -c`. Quoted command: blocked, exit 2. Negative control, same command with the quotes stripped: `sh: /tmp/sp: No such file or directory`, exit 127 (hook never runs, push not blocked).
- `scripts/check.sh`: exit 0 (all selftests, shellcheck, plugin validate).
