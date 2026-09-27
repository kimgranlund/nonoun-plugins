#!/usr/bin/env bash
# PreToolUse hook for Bash, Agent, and Monitor: in a headless session (SDLC_ROLE set by run.sh,
# or SDLC_HEADLESS=1), deny Bash run_in_background, deny Agent unless run_in_background is
# exactly false (Agent runs in the background by default), and deny Monitor always (it watches
# background work, which a headless session must not start). A headless session that backgrounds work and ends its turn ends the
# session and abandons the work. Exit 2 blocks the call and shows stderr to the model.
set -uo pipefail
input="$(cat)"
role="${SDLC_ROLE:-}"
if [[ -z "$role" && "${SDLC_HEADLESS:-}" != "1" ]]; then exit 0; fi
tool="$(jq -r '.tool_name // ""' <<<"$input" 2>/dev/null)"
if [[ "$tool" == "Monitor" ]]; then
  echo "headless session (sdlc role '$role' or SDLC_HEADLESS=1): do not use Monitor; run gates and tests with foreground Bash and the Bash timeout at 600000 or more, and never end the turn while background work runs, because ending the turn ends the session and abandons the work" >&2
  exit 2
fi
if [[ "$tool" == "Agent" ]]; then
  abg="$(jq -c '.tool_input.run_in_background' <<<"$input" 2>/dev/null)"
  if [[ "$abg" != "false" ]]; then
    echo "headless session (sdlc role '$role' or SDLC_HEADLESS=1): pass run_in_background: false to the Agent tool and wait for the subagent's result in this same turn; never end the turn while it runs, because ending the turn ends the session and abandons the work" >&2
    exit 2
  fi
  exit 0
fi
bg="$(jq -r '.tool_input.run_in_background // false' <<<"$input" 2>/dev/null)"
if [[ "$bg" == "true" ]]; then
  echo "headless session (sdlc role '$role' or SDLC_HEADLESS=1): run this in the foreground with the Bash timeout at 600000 or more; do not use run_in_background, and never end the turn while it runs, because that ends the session and abandons the work" >&2
  exit 2
fi
exit 0
