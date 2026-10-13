#!/usr/bin/env bash
# Sourced by the role hooks (block-publish, block-pattern-kill, block-stray-worktree,
# block-repo-format, block-disk-scan, block-role-write); never run on its own.
#
#   sdlc_role <hook-input-json>   prints the caller's role, or nothing when the caller has none.
#
# The role is $SDLC_ROLE when it is set (run.sh and fanout set it per process). Otherwise it is
# the hook input's agent_type for an SDLC Lite sub-agent, with the sdlc-lite: prefix and the
# level suffix removed (sdlc-lite:builder-L3 -> builder, sdlc-lite:solo-L2 -> solo): a sub-agent
# inherits its parent's environment, so the per-process variable cannot tell it from the
# parent, and the hook input can. When both exist the variable wins, so a headless parent's
# role is what its sub-agents resolve to; the sub-agent's own type counts only in a session
# that has no SDLC_ROLE. The session agents conductor and messenger are not roles, so an
# interactive conductor that publishes after approval is never blocked. A bare agent_type
# counts only when it names a pipeline role; any other agent (Explore, general-purpose,
# another plugin's agent) has no role.
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
  at=$(jq -r '.agent_type // ""' <<<"$1" 2>/dev/null) || return 0
  [[ -n "$at" ]] || return 0
  name="${at#sdlc-lite:}"
  if [[ "$name" =~ $re_level ]]; then
    name="${BASH_REMATCH[1]}"
  elif [[ "$name" =~ $re_solo ]]; then
    name="${BASH_REMATCH[1]}"
  fi
  case "$name" in
    ''|conductor|messenger) return 0 ;;
  esac
  if [[ "$at" == sdlc-lite:* || "$SDLC_PIPELINE_ROLES" == *" $name "* ]]; then
    printf '%s' "$name"
  fi
  return 0
}
