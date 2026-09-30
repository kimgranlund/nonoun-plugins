#!/usr/bin/env bash
# PreToolUse hook for Agent: when the session is the SDLC Lite conductor (agent_type
# sdlc-lite:conductor or conductor, or SDLC_ROLE=conductor), deny an Agent spawn of any
# sdlc-lite: role agent, or of another plugin's agent whose name holds a builder, verifier,
# reviewer, planner, or checker token. That work runs through scripts/run.sh. Read-only helpers
# (Explore, general-purpose, harness:fact-finder) and non-conductor sessions pass.
# Exit 2 blocks the call and shows stderr to the model.
set -uo pipefail
input="$(cat)"
tool="$(jq -r '.tool_name // ""' <<<"$input" 2>/dev/null)"
[[ "$tool" == "Agent" ]] || exit 0
atype="$(jq -r '.agent_type // ""' <<<"$input" 2>/dev/null)"
if [[ "$atype" != "sdlc-lite:conductor" && "$atype" != "conductor" && "${SDLC_ROLE:-}" != "conductor" ]]; then
  exit 0
fi
sub="$(jq -r '.tool_input.subagent_type // ""' <<<"$input" 2>/dev/null)"
deny=0
if [[ "$sub" == sdlc-lite:* ]]; then
  deny=1
elif [[ "$sub" == *:* ]]; then
  name="${sub#*:}"
  IFS='-_' read -r -a toks <<<"$name"
  for t in "${toks[@]}"; do
    case "$t" in builder|verifier|reviewer|planner|checker) deny=1 ;; esac
  done
fi
if [[ $deny -eq 1 ]]; then
  echo "conductor session: do not spawn '$sub' through the Agent tool; planner, builder, and verifier work runs through \${CLAUDE_PLUGIN_ROOT}/scripts/run.sh, never the Agent tool" >&2
  exit 2
fi
exit 0
