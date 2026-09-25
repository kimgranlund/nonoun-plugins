<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
- No planner, builder, or verifier ran. The conductor made this as a trivial edit, so there is no independent verifier verdict. The only evidence is the conductor's own record in `conductor-edit.md`.

## PR title
T-0053: Quote ${CLAUDE_PLUGIN_ROOT} in the block-publish hook command

## PR body
### Summary
In `plugins/sdlc-lite/hooks/hooks.json`, the PreToolUse command did not quote `${CLAUDE_PLUGIN_ROOT}`. If the plugin path contained a space, the shell split the command, so the block-publish hook never ran and publishing was not blocked. `claude plugin validate` also warned about the unquoted placeholder. This PR adds the quotes. The hook script and its matcher are unchanged.

### Changes
- `plugins/sdlc-lite/hooks/hooks.json`: `"command": "${CLAUDE_PLUGIN_ROOT}/hooks/block-publish.sh"` is now `"command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/block-publish.sh\""`.

### Verification
The conductor ran these checks. No independent verifier ran.
- Validator: before the change, `claude plugin validate plugins/sdlc-lite` printed `hooks.PreToolUse: Shell command uses ${CLAUDE_PLUGIN_ROOT} without quotes`. After it, the output was `✔ Validation passed` with no warnings.
- Spaced path test: the hook was copied into `/tmp/sp ace.XXXX/hooks/`. The command was expanded from hooks.json and run through `sh -c`, with `SDLC_ROLE=builder` and the input `{"tool_input":{"command":"git push"}}`.
  - With the quotes, the push was blocked (exit 2).
  - Negative control, the same command without the quotes: `sh: /tmp/sp: No such file or directory` (exit 127). The hook never ran and the push went through.
- `scripts/check.sh` exited 0 (all selftests, shellcheck, plugin validate).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: the block-publish PreToolUse hook now runs when the plugin path contains spaces (`${CLAUDE_PLUGIN_ROOT}` is quoted in `hooks/hooks.json`).

## Follow-ups
None
