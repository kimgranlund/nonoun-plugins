#!/usr/bin/env bash
# PreToolUse hook for Edit, Write, and NotebookEdit (Claude Code only; Codex has no hooks, so there the
# runner's stale_input flag on the run line is the only signal). Acts in any session. When the edited
# file is named handoff.md and a <role>-<level>.running file sits in its records dir (scripts/records.sh)
# or beside it, a role is reading that handoff right now. Warn mode (default): allow the edit, print one
# stderr warning, and append one line to stale-edits.log in the records dir when a marker sits there, else
# beside the handoff. Deny mode (SDLC_HANDOFF_EDIT_MODE=deny): exit 2 with the same message. Any other
# file name, or a handoff with no .running file in either place, passes silently and logs nothing.
# Exit 0 allows, exit 2 blocks.
set -uo pipefail
# shellcheck source=../scripts/records.sh
. "$(dirname "${BASH_SOURCE[0]}")/../scripts/records.sh"
input="$(cat)"
file="$(jq -r '.tool_input.file_path // .tool_input.notebook_path // ""' <<<"$input" 2>/dev/null)"
[[ -n "$file" && "$(basename "$file")" == "handoff.md" ]] || exit 0
hdir="$(dirname "$file")"
rdir="$(records_dir "$hdir" 2>/dev/null || true)"
running=()
log=""
dirs=("$hdir")
[[ -z "$rdir" || "$rdir" == "$hdir" ]] || dirs=("$rdir" "$hdir")  # the same dir is read once
for d in "${dirs[@]}"; do
  for r in "$d"/*.running; do
    [[ -e "$r" ]] || continue
    n="$(basename "$r" .running)"
    [[ " ${running[*]-} " == *" $n "* ]] || running+=("$n")
    [[ -n "$log" ]] || log="$d/stale-edits.log"
  done
done
(( ${#running[@]} > 0 )) || exit 0
msg="handoff $file is being read by ${running[*]}; an edit now makes that result stale input (run.sh flags it on the run line). Scope changes belong in a new ticket."
printf '%s %s edited while %s ran\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$file" "${running[*]}" >>"$log" 2>/dev/null || true
if [[ "${SDLC_HANDOFF_EDIT_MODE:-warn}" == "deny" ]]; then
  echo "handoff freeze: $msg" >&2
  exit 2
fi
echo "handoff freeze (warning): $msg" >&2
exit 0
