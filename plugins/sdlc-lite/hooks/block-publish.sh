#!/usr/bin/env bash
# PreToolUse(Bash): inside a role run (SDLC_ROLE set by scripts/run.sh), block commands that
# publish outside the machine. Publishing happens only from the user's session after approval.
[[ -n "${SDLC_ROLE:-}" ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""')
pattern='(^|[^[:alnum:]_-])(git[[:space:]]+push|gh[[:space:]]+(pr|issue)[[:space:]]+(create|merge|comment|edit|close|reopen|review|ready|delete)|gh[[:space:]]+release|gh[[:space:]]+api[^|;&]*(-X|--method)[[:space:]]*(POST|PATCH|PUT|DELETE)|(npm|pnpm|yarn)[[:space:]]+publish)'
if grep -Eq "$pattern" <<<"$cmd"; then
  echo "Blocked for sdlc role '$SDLC_ROLE': publishing is the user's call. Draft it in your final message instead." >&2
  exit 2
fi
exit 0
