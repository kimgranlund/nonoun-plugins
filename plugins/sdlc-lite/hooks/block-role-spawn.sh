#!/usr/bin/env bash
# PreToolUse hook for Agent: the spawn gate for a conductor session (agent_type sdlc-lite:conductor
# or conductor, or SDLC_ROLE=conductor); every other session passes. In a conductor session:
#
#  - subagent_type sdlc-lite:<role>-L<n> is allowed only as a prepared dispatch, that is only when
#    all four hold, and each failed condition is its own denial:
#      1. subagent_type is sdlc-lite:<role>-L<n> (a level definition, or sdlc-lite:solo-L1|L2|L3 on
#         its dispatch record and model alone; not sdlc-lite:conductor or a bare role name); the
#         0.21.x solo names solo-S, solo-M, solo-L pass as deprecated aliases for one release (ALIAS_OK);
#      2. name is <role>-L<n>-<slug>[-<k>], the same <role>-L<n> as the subagent_type;
#      3. a dispatch record exists beside the handoff named by the prompt's "Handoff:" line (its path is the first token, or the whole text of a leading "double-quoted" locator; trailing text is ignored): the
#         file <name>.dispatch.json, or any *.dispatch.json whose "name" is this name (dispatch.py
#         prepare writes <role>-L<n>[-<k>].dispatch.json and puts the Agent name inside it);
#      4. the call's model equals that record's model, so a verifier or plan-reviewer cannot be
#         moved onto the builder's family after prepare chose its model.
#  - sdlc-lite:messenger is the one session agent a conductor may spawn without a dispatch record (it is
#    not a pipeline role): its name must be inbox-<repo>-<receiver> (T-0369). Any other name is denied.
#  - subagent_type fork is denied when the name starts with verifier- or plan-reviewer- (a fork
#    inherits the parent's context and model, so it cannot be independent), and any other fork
#    needs a "Fork reason:" line in the prompt.
#  - another plugin's agent whose name after the colon holds a builder, verifier, reviewer,
#    planner, or checker token (split on - and _) is denied, as before.
# Read-only helpers (Explore, general-purpose, Plan, harness:fact-finder), a call with no
# subagent_type, and every non-Agent tool pass. A run.sh call is a Bash call and never reaches
# this hook.
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
name="$(jq -r '.tool_input.name // ""' <<<"$input" 2>/dev/null)"

deny() {
  echo "conductor session: $1" >&2
  exit 2
}
prepare_hint="prepare the dispatch with dispatch.py prepare <role> <level> <handoff.md> and spawn with exactly the JSON it prints (subagent_type, name, model, prompt)"

if [[ "$sub" == "fork" ]]; then
  if [[ "$name" == verifier-* || "$name" == plan-reviewer-* || "$name" =~ -(verifier|plan-reviewer)-L[0-9]+(-[0-9]+)?$ ]]; then
    deny "do not fork '$name': a fork inherits this session's context and model, so a verifier or plan-reviewer fork cannot be independent. $prepare_hint"
  fi
  prompt="$(jq -r '.tool_input.prompt // ""' <<<"$input" 2>/dev/null)"
  has_reason=0
  while IFS= read -r line; do
    if [[ "$line" =~ ^Fork\ reason:[[:space:]]*[^[:space:]] ]]; then has_reason=1; break; fi
  done <<<"$prompt"
  [[ $has_reason -eq 1 ]] || deny "a fork needs a line 'Fork reason: <why a fork and not a fresh brief>' in its prompt"
  exit 0
fi

if [[ "$sub" == "sdlc-lite:messenger" ]]; then
  [[ "$name" =~ ^inbox-[a-z0-9]+(-[a-z0-9]+)+$ ]] ||
    deny "name '$name' does not match inbox-<repo>-<receiver> (lowercase letters, digits and dashes) for subagent_type 'sdlc-lite:messenger'; spawn it as the mailbox poller, for example inbox-maison-claude"
  exit 0
fi

re_bare='^(scout|researcher|architect|archaeologist|planner|plan-reviewer|builder|verifier|filer|solo|ui-designer|conductor|messenger)(-L[0-9]+|-[SML])?$'  # ALIAS_OK
if [[ "$sub" == sdlc-lite:* || "$sub" =~ $re_bare ]]; then
  # A bare role name is never a prepared dispatch (prepare prints the sdlc-lite: form), so it
  # fails condition 1 like any other malformed type.
  stem="${sub#sdlc-lite:}"
  re_type='^[a-z]+(-[a-z]+)*-L[0-9]+$'
  # solo-L1|L2|L3, and the deprecated 0.21.x aliases solo-S|M|L for one release. ALIAS_OK
  re_solo='^solo-(L[1-3]|[SML])$'
  [[ "$sub" == sdlc-lite:* && ( "$stem" =~ $re_type || "$stem" =~ $re_solo ) && ( "$stem" != solo-* || "$stem" =~ $re_solo ) ]] ||
    deny "do not spawn '$sub': only sdlc-lite:<role>-L<n> agents are dispatched, and only after dispatch.py prepare. $prepare_hint"
  re_name='^[A-Za-z0-9][A-Za-z0-9_-]*$'
  # A solo dispatch (solo_run.py, fanout prep) names its own agent: the record check below is its gate.
  if [[ "$stem" =~ $re_solo ]]; then
    [[ "$name" =~ $re_name ]] || deny "name '$name' is not a valid agent name. $prepare_hint"
  elif [[ ! "$name" =~ ^.+-${stem}(-[0-9]+)?$ || ! "$name" =~ $re_name ]]; then
    deny "name '$name' does not match <ticket>-${stem}[-<k>] for subagent_type '$sub'. $prepare_hint"
  fi

  prompt="$(jq -r '.tool_input.prompt // ""' <<<"$input" 2>/dev/null)"
  cwd="$(jq -r '.cwd // ""' <<<"$input" 2>/dev/null)"
  # locator <prefix>: the value of the first prompt line starting with <prefix>, quoted or its first token,
  # made absolute against .cwd; empty when no such line.
  locator() {
    local line v=""
    while IFS= read -r line; do
      if [[ "$line" == "$1"* ]]; then
        v="${line#"$1"}"; v="${v#"${v%%[![:space:]]*}"}"
        if [[ "$v" == \"*\"* ]]; then
          v="${v#\"}"; v="${v%%\"*}"  # a quoted locator ("<path>") holds spaces; text after the closing quote is ignored
        else
          v="${v%%[[:space:]]*}"  # a bare locator is its first token: trailing text is ignored
        fi
        break
      fi
    done <<<"$prompt"
    [[ -z "$v" || "$v" == /* ]] || v="${cwd:-$PWD}/$v"
    printf '%s' "$v"
  }
  handoff="$(locator 'Handoff: ')"
  [[ -n "$handoff" ]] || deny "the prompt of '$name' has no 'Handoff: <path>' line, so no dispatch record can be found. $prepare_hint"
  # The record sits in the Artifacts dir (the records dir dispatch.py prepare names), else beside the handoff
  # (a legacy task dir). A missing or nonexistent Artifacts dir falls back to the handoff dir silently.
  artifacts="$(locator 'Artifacts dir: ')"
  hdir="${handoff%/*}"
  record=""
  for dir in "$artifacts" "$hdir"; do
    [[ -n "$dir" && -d "$dir" ]] || continue
    if [[ -f "$dir/$name.dispatch.json" ]]; then
      record="$dir/$name.dispatch.json"
    else
      for f in "$dir"/*.dispatch.json; do
        [[ -f "$f" ]] || continue
        if jq -e --arg n "$name" '.name == $n' "$f" >/dev/null 2>&1; then record="$f"; break; fi
      done
    fi
    [[ -z "$record" ]] || break
  done
  where="beside $handoff"
  [[ -z "$artifacts" || ! -d "$artifacts" ]] || where="in the Artifacts dir $artifacts or beside $handoff"
  [[ -n "$record" ]] ||
    deny "no dispatch record for '$name' $where (looked for $name.dispatch.json and a *.dispatch.json naming it). $prepare_hint"

  want="$(jq -r '.model // ""' "$record" 2>/dev/null)"
  model="$(jq -r '.tool_input.model // ""' <<<"$input" 2>/dev/null)"
  [[ -n "$want" ]] || deny "the dispatch record $record holds no model. $prepare_hint"
  # Compare by Agent alias: the Agent tool takes sonnet|opus|haiku|fable, a record may pin an id.
  alias_of() { local m="${1#claude-}"; m="${m%%-*}"; case "$m" in sonnet|opus|haiku|fable) echo "$m" ;; *) echo "$1" ;; esac; }
  [[ "$(alias_of "$model")" == "$(alias_of "$want")" ]] ||
    deny "model '${model:-unset}' is not the dispatch model '$want' in $record: the model is chosen by dispatch.py prepare, which keeps a verifier off the build's model family. Pass model '$want'."
  exit 0
fi

if [[ "$sub" == *:* ]]; then
  pname="${sub#*:}"
  IFS='-_' read -r -a toks <<<"$pname"
  for t in "${toks[@]}"; do
    case "$t" in
      builder|verifier|reviewer|planner|checker)
        deny "do not spawn '$sub' through the Agent tool; planner, builder, and verifier work runs through \${CLAUDE_PLUGIN_ROOT}/scripts/run.sh or a prepared sdlc-lite dispatch, never another plugin's agent" ;;
    esac
  done
fi
exit 0
