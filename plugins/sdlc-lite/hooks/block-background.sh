#!/usr/bin/env bash
# PreToolUse(Bash) hook: in a headless session (SDLC_ROLE set by run.sh, or SDLC_HEADLESS=1),
# deny run_in_background. A headless session that backgrounds work and ends its turn ends the
# session and abandons the work. Exit 2 blocks the call and shows stderr to the model.
set -uo pipefail
input="$(cat)"
role="${SDLC_ROLE:-}"
if [[ -z "$role" && "${SDLC_HEADLESS:-}" != "1" ]]; then exit 0; fi
bg="$(jq -r '.tool_input.run_in_background // false' <<<"$input" 2>/dev/null)"
if [[ "$bg" == "true" ]]; then
  echo "headless session (sdlc role '$role' or SDLC_HEADLESS=1): run this in the foreground with the Bash timeout at 600000 or more; do not use run_in_background, and never end the turn while it runs, because that ends the session and abandons the work" >&2
  exit 2
fi
exit 0
