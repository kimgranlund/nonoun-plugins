#!/usr/bin/env bash
# PreToolUse(Bash): in a role run (a role from hooks/_role.sh, or SDLC_HEADLESS=1), give the
# command a closed stdin. The Bash tool's child inherits an stdin pipe that never closes, so a
# command that reads stdin (a bare `cat > file`, `python3 -`, `read`) waits with no output until
# the Bash timeout, which run.sh raises to an hour (T-0548: a builder sat 39 minutes on
# `cat > /tmp/x`). The hook returns updatedInput with the command wrapped as
#   {
#   <command>
#   } </dev/null
# a brace group, so a cd still changes the session's directory, with the closing brace on its own
# line, so a trailing comment or a heredoc terminator cannot swallow it. A heredoc, a pipe, or an
# input redirect inside the command still feeds its own command. The other tool_input fields
# (timeout, description) are kept, because a partial input fails validation (probe P2).
# No permissionDecision is printed, so the permission check and the other Bash hooks still decide.
# Not a role, an empty command, or no jq: exit 0 with no output, the command unchanged.
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
input=$(cat)
role=$(sdlc_role "$input")
[[ -n "$role" || "${SDLC_HEADLESS:-}" == "1" ]] || exit 0
command -v jq >/dev/null 2>&1 || exit 0
cmd=$(jq -r '.tool_input.command // ""' <<<"$input" 2>/dev/null) || exit 0
[[ -n "${cmd//[[:space:]]/}" ]] || exit 0
jq -c '{hookSpecificOutput: {hookEventName: "PreToolUse",
         updatedInput: (.tool_input + {command: ("{\n" + .tool_input.command + "\n} </dev/null")})}}' \
  <<<"$input" 2>/dev/null || true
exit 0
