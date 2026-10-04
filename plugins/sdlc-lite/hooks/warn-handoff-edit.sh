#!/usr/bin/env bash
# PreToolUse hook for Edit, Write, and NotebookEdit (Claude Code only; Codex has no hooks, so there the
# runner's stale_input flag on the run line is the only signal). Acts in any session. When the edited
# file is named handoff.md and a <role>-<level>.running file sits beside it, a role is reading that
# handoff right now. Warn mode (default): allow the edit, print one stderr warning, and append one
# line to stale-edits.log beside the handoff. Deny mode (SDLC_HANDOFF_EDIT_MODE=deny): exit 2 with the
# same message. Any other file name, or a handoff with no .running file beside it, passes silently
# and logs nothing. Exit 0 allows, exit 2 blocks.
set -uo pipefail
input="$(cat)"
file="$(jq -r '.tool_input.file_path // .tool_input.notebook_path // ""' <<<"$input" 2>/dev/null)"
[[ -n "$file" && "$(basename "$file")" == "handoff.md" ]] || exit 0
dir="$(dirname "$file")"
running=()
for r in "$dir"/*.running; do [[ -e "$r" ]] && running+=("$(basename "$r" .running)"); done
(( ${#running[@]} > 0 )) || exit 0
msg="handoff $file is being read by ${running[*]}; an edit now makes that result stale input (run.sh flags it on the run line). Scope changes belong in a new ticket."
printf '%s %s edited while %s ran\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$file" "${running[*]}" >>"$dir/stale-edits.log" 2>/dev/null || true
if [[ "${SDLC_HANDOFF_EDIT_MODE:-warn}" == "deny" ]]; then
  echo "handoff freeze: $msg" >&2
  exit 2
fi
echo "handoff freeze (warning): $msg" >&2
exit 0
