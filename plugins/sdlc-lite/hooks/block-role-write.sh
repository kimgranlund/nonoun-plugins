#!/usr/bin/env bash
# PreToolUse(Edit|Write|NotebookEdit): a read-only role (hooks/_role.sh resolves the role: SDLC_ROLE,
# else the sub-agent's agent_type; the set is SDLC_READONLY_ROLES, the roles run.sh disallows these
# tools for) may Write only its dispatch result path. Edit and NotebookEdit are denied (the
# generated definitions already disallow them; this holds when the definition is not honored). A
# Write passes when the file_path is exactly the "result" of a <stem>.dispatch.json beside it whose
# subagent_type is this agent's type (or whose role is this role); any other path is denied (exit 2).
# The builder, solo, the conductor, a session with no role, and every other tool pass untouched.
set -uo pipefail
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
input=$(cat)
role=$(sdlc_role "$input")
[[ -n "$role" && "$SDLC_READONLY_ROLES" == *" $role "* ]] || exit 0
tool=$(jq -r '.tool_name // ""' <<<"$input" 2>/dev/null)
case "$tool" in
  Edit|Write|NotebookEdit) ;;
  *) exit 0 ;;
esac

block() {
  echo "Blocked for sdlc role '$role': $1. A read-only role writes no file except its dispatch result path, the one its brief names ('Report file: <path>'); put everything else in your final message." >&2
  exit 2
}

[[ "$tool" == Write ]] || block "$tool is not allowed"
fp=$(jq -r '.tool_input.file_path // ""' <<<"$input" 2>/dev/null)
[[ -n "$fp" && "$fp" == /* && "$fp" == *.md ]] || block "'${fp:-no path}' is not a dispatch result path"
atype=$(jq -r '.agent_type // ""' <<<"$input" 2>/dev/null)
record="${fp%.md}.dispatch.json"
if [[ -f "$record" ]] &&
  jq -e --arg p "$fp" --arg t "$atype" --arg r "$role" \
    '.result == $p and (.subagent_type == $t or .role == $r)' "$record" >/dev/null 2>&1; then
  exit 0
fi
block "'$fp' is not the result path of a dispatch for this role"
