#!/usr/bin/env bash
# Sourced by the role hooks (block-background, block-publish, block-pattern-kill, block-stray-worktree,
# block-repo-format, block-disk-scan, block-role-write, block-role-rm, close-role-stdin); never run on its own.
#
#   sdlc_role <hook-input-json>   prints the caller's role, or nothing when the caller has none.
#
# The role is $SDLC_ROLE when it is set (run.sh and fanout set it per process). Otherwise it is
# the hook input's agent_type for an SDLC Lite sub-agent, with the sdlc-lite: prefix and the
# level suffix removed (sdlc-lite:builder-L3 -> builder, sdlc-lite:solo-L2 -> solo): a sub-agent
# inherits its parent's environment, so the per-process variable cannot tell it from the
# parent, and the hook input can. When both exist the variable wins, so a headless parent's
# role is what its sub-agents resolve to; the sub-agent's own type counts only in a session
# that has no SDLC_ROLE. The session agents conductor, direct, hybrid and messenger are not roles, so an
# interactive conductor that publishes after approval is never blocked. A bare agent_type
# counts only when it names a pipeline role; any other agent (Explore, general-purpose,
# another plugin's agent) has no role.
# An in-process teammate (an Agent spawn with a name in a session with agent teams on) reports
# its name as agent_type, not its sdlc-lite type (T-0702: solo-0702 ran find / unblocked), so a
# name with no colon resolves too when it holds <role>-L<n> as whole hyphen-separated parts
# (0702-solo-L2, 0697-verifier-L2-2, the dispatch.py and solo_run.py names) or starts or ends
# with solo as a part (solo-0702, the fanout name T-0702-solo).
# That name inference is the fallback (T-0704): the teammate's real type is not in the payload,
# but its transcript sidecar <transcript_path minus .jsonl>/subagents/agent-<agent_id>.meta.json
# holds it as customAgentType (sdlc-lite:builder-L2 for a teammate named reviewer-x), and it is
# there by the teammate's first tool call. When that file names a type, the type decides and the
# name is not read; a missing file or field falls back to the name.
#
# A payload without an agent_type costs no jq call.
SDLC_PIPELINE_ROLES=" scout researcher architect archaeologist planner plan-reviewer builder verifier filer solo ui-designer "
# The roles that never edit the project: run.sh disallows Edit, Write, and NotebookEdit for exactly
# these, and claude_roles.py gives exactly these definitions disallowedTools (builder, solo, and ui-designer write;
# ui-designer edits only in its generate mode, a rule its role contract holds, not a hook).
# shellcheck disable=SC2034 # read by block-role-write.sh, which sources this file
SDLC_READONLY_ROLES=" scout researcher architect archaeologist planner plan-reviewer verifier filer "

sdlc_role() {
  # re_solo: the deprecated 0.21.x solo names solo-S|M|L, kept for one release. ALIAS_OK
  local at name re_level='^(.+)-L[0-9]+$' re_solo='^(solo)-[SML]$'
  if [[ -n "${SDLC_ROLE:-}" ]]; then
    printf '%s' "$SDLC_ROLE"
    return 0
  fi
  [[ "$1" == *'"agent_type"'* ]] || return 0
  local tp aid meta ct
  # \x1f, not a tab: whitespace IFS would merge an empty transcript_path into the next field.
  IFS=$'\x1f' read -r at tp aid < <(jq -r '[.agent_type, .transcript_path, .agent_id] | map(. // "" | tostring) | join("\u001f")' <<<"$1" 2>/dev/null) || true
  [[ -n "$at" ]] || return 0
  if [[ "$at" != *:* && "$tp" == *.jsonl && "$aid" =~ ^[A-Za-z0-9_-]+$ ]]; then
    meta="${tp%.jsonl}/subagents/agent-$aid.meta.json"
    if [[ -f "$meta" ]]; then
      ct=$(jq -r '.customAgentType // ""' "$meta" 2>/dev/null) || ct=
      [[ -n "$ct" ]] && at="$ct"
    fi
  fi
  name="${at#sdlc-lite:}"
  if [[ "$name" =~ $re_level ]]; then
    name="${BASH_REMATCH[1]}"
  elif [[ "$name" =~ $re_solo ]]; then
    name="${BASH_REMATCH[1]}"
  fi
  case "$name" in
    ''|conductor|direct|hybrid|messenger) return 0 ;;
  esac
  if [[ "$at" == sdlc-lite:* || "$SDLC_PIPELINE_ROLES" == *" $name "* ]]; then
    printf '%s' "$name"
    return 0
  fi
  [[ "$at" == *:* || -n "${ct:-}" ]] && return 0
  local r re_mate re_solo_part='^solo-|-solo$'
  for r in $SDLC_PIPELINE_ROLES; do
    re_mate="(^|-)$r-L[0-9]+(-|\$)"
    if [[ "$at" =~ $re_mate ]]; then
      printf '%s' "$r"
      return 0
    fi
  done
  [[ "$at" =~ $re_solo_part ]] && printf solo
  return 0
}
