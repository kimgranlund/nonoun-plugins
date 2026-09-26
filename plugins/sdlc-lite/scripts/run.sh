#!/usr/bin/env bash
# Usage: run.sh <role> <level> <handoff.md>
# Runs one role headless in the current directory with the level's model and effort.
# Writes <handoff dir>/<role>-<level>.md (the agent's final message) and <role>-<level>.log
# (raw JSON). A rerun of the same role and level (a replan, a rebuild) never overwrites: it
# writes <role>-<level>-<k>.md and .log with the lowest free k >= 2, and prints the path it
# wrote; readers take the newest file. Keeps <role>-<level>.running while the run is live
# (for /board and the status line), and appends one line to <handoff dir>/runs.jsonl for /bench;
# its "file" field names the result, and scripts/order.py orders results by those lines.
# Runs with --dangerously-skip-permissions; hooks/block-publish.sh still blocks publishing (via SDLC_ROLE). Every role except builder gets Edit/Write/NotebookEdit disallowed.
# Preflight: exits 2 unless the current directory is in a git work tree with at least one commit.
# Node: a .nvmrc at the git toplevel is resolved against ${NVM_DIR:-$HOME/.nvm}/versions/node
# (nvm is never sourced or run). An exact version (v20.11.0) matches that dir only; a partial one
# (20, v20.11) matches whole components and takes the highest installed. A match prepends its bin
# dir to PATH, so the role run inherits it; no match or an alias (lts/*, node) leaves PATH alone.
# Each outcome prints one "run.sh: .nvmrc ..." line on stderr; none changes the exit code.
# Result check: after the result and its runs.jsonl line are written (both kept), the result must
# hold the role's required section (a line exactly "## <Name>"): builder ## Status (done|blocked),
# verifier ## Verdict (pass|fail), planner ## Goal, researcher ## Answer, scout ## Map,
# archaeologist ## Summary, architect ## Approach, filer ## Warnings. Otherwise one stderr line, exit 3.
# Exit codes: 0 ok, 1 run failed or returned no result, 2 usage or preflight, 3 result lacks its section.
# Env: SDLC_DRY_RUN=1 prints the command only (after the preflight and .nvmrc resolution).
set -euo pipefail

role="${1:-}"; level="${2:-}"; handoff="${3:-}"
usage() { echo "usage: run.sh <role> <level> <handoff.md>  (see levels in this file)" >&2; exit 2; }

# role:level -> model effort. Keep in sync with skills/level-rubric/SKILL.md and CLAUDE.md.
case "$role:$level" in
  builder:L1)       model=sonnet; effort=low ;;
  builder:L2)       model=opus;   effort=low ;;
  builder:L3)       model=opus;   effort=high ;;
  builder:L4)       model=opus;   effort=xhigh ;;
  builder:L5)       model=fable;  effort=xhigh ;;
  planner:L1)       model=sonnet; effort=medium ;;
  planner:L2)       model=opus;   effort=medium ;;
  planner:L3)       model=fable;  effort=xhigh ;;
  verifier:L1)      model=sonnet; effort=medium ;;
  verifier:L2)      model=sonnet; effort=high ;;
  verifier:L3)      model=fable;  effort=xhigh ;;
  researcher:L1)    model=sonnet; effort=medium ;;
  researcher:L2)    model=opus;   effort=medium ;;
  researcher:L3)    model=opus;   effort=high ;;
  architect:L1)     model=fable;  effort=high ;;
  scout:L1)         model=haiku;  effort=low ;;
  archaeologist:L1) model=sonnet; effort=medium ;;
  filer:L1)         model=sonnet; effort=medium ;;
  *) usage ;;
esac
[[ -f "$handoff" ]] || { echo "handoff not found: $handoff" >&2; exit 2; }
# Git preflight: roles need a repo with a commit (diffs, worktrees). Never init git here.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo: run git init and commit first" >&2; exit 2; }
git rev-parse --verify -q HEAD >/dev/null || { echo "git repo has no commit: commit first" >&2; exit 2; }

# Node version: honor the repo's .nvmrc without sourcing or running nvm. Resolve it against
# installed dirs under ${NVM_DIR:-$HOME/.nvm}/versions/node and prepend that bin dir to PATH.
# One stderr line per outcome; never changes the exit code. No .nvmrc: nothing.
nvmrc="$(git rev-parse --show-toplevel)/.nvmrc"
if [[ -f "$nvmrc" ]]; then
  nvmrc_raw=$(tr -d '[:space:]' <"$nvmrc" || true)
  nvm_node="${NVM_DIR:-$HOME/.nvm}/versions/node"
  nvm_pick=""
  if [[ -z "$nvmrc_raw" ]]; then
    :
  elif [[ "$nvmrc_raw" =~ ^v?[0-9]+(\.[0-9]+)?(\.[0-9]+)?$ ]]; then
    nvm_want="${nvmrc_raw#v}"
    if [[ "$nvm_want" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      # Exact version: that dir only.
      [[ -d "$nvm_node/v$nvm_want" ]] && nvm_pick="v$nvm_want"
    else
      # Partial version: whole-component prefix match, highest by numeric compare.
      IFS=. read -r nw1 nw2 _ <<<"$nvm_want"
      best1=-1; best2=-1; best3=-1
      for d in "$nvm_node"/v*; do
        [[ -d "$d" ]] || continue
        [[ "${d##*/}" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]] || continue
        c1=$((10#${BASH_REMATCH[1]})); c2=$((10#${BASH_REMATCH[2]})); c3=$((10#${BASH_REMATCH[3]}))
        [[ "$c1" == "$((10#$nw1))" ]] || continue
        [[ -z "${nw2:-}" || "$c2" == "$((10#$nw2))" ]] || continue
        if (( c1 > best1 || (c1 == best1 && (c2 > best2 || (c2 == best2 && c3 > best3))) )); then
          best1=$c1; best2=$c2; best3=$c3; nvm_pick="${d##*/}"
        fi
      done
    fi
    if [[ -n "$nvm_pick" ]]; then
      nvm_bin="$nvm_node/$nvm_pick/bin"
      echo "run.sh: .nvmrc $nvmrc_raw: prepended $nvm_bin to PATH" >&2
      export PATH="$nvm_bin:$PATH"
    else
      echo "run.sh: .nvmrc $nvmrc_raw: not found under $nvm_node, PATH unchanged" >&2
    fi
  else
    echo "run.sh: .nvmrc $nvmrc_raw: alias not resolved, PATH unchanged" >&2
  fi
fi

plugin_root="$(cd "$(dirname "$0")/.." && pwd)"
handoff="$(cd "$(dirname "$handoff")" && pwd)/$(basename "$handoff")"
dir="$(dirname "$handoff")"
# Never overwrite an earlier result: the first run is <role>-<level>, later ones <role>-<level>-<k>.
name="$role-$level"
if [[ -e "$dir/$name.md" ]]; then
  k=2
  while [[ -e "$dir/$role-$level-$k.md" ]]; do k=$((k + 1)); done
  name="$role-$level-$k"
fi
result="$dir/$name.md"
log="$dir/$name.log"

# A verifier never runs on the build's model family (T-0005, user decision 2026-09-24):
# Fable or Sonnet build -> Opus at the same effort.
if [[ "$role" == verifier ]]; then
  built=$(python3 "$plugin_root/scripts/order.py" newest "$dir" builder 2>/dev/null || true)
  if [[ -n "$built" ]]; then
    bmodel=$(grep -o 'model=[a-z]*' "$built" | head -1 | cut -d= -f2 || true)
    if [[ "$model" == "$bmodel" ]]; then
      case "$model" in
        fable|sonnet) model=opus ;;
      esac
    fi
  fi
fi

# Skills declared in the agent's frontmatter (skills: list). `claude --agent` does not preload
# them (probed 2026-09-24), so append each skill body to the system prompt here.
agent_file="$plugin_root/agents/$role.md"
skills=$(awk '/^---$/{n++; next} n==1 && /^skills:/{f=1; next} n==1 && f && /^  - /{sub(/^  - /,""); print; next} n==1 && f{f=0}' "$agent_file")
skill_prompt=()
if [[ -n "$skills" ]]; then
  skill_file=$(mktemp)
  while IFS= read -r sk; do
    src="$plugin_root/skills/$sk/SKILL.md"
    [[ -f "$src" ]] || { echo "agent $role declares missing skill: $sk" >&2; exit 2; }
    { echo "# Skill: $sk (loaded for this role; its relative paths are under $plugin_root/skills/$sk/)"
      awk '/^---$/{n++; next} n>=2' "$src" | sed 's|${CLAUDE_PLUGIN_ROOT}|'"$plugin_root"'|g'
      echo; } >>"$skill_file"
  done <<<"$skills"
  skill_prompt=(--append-system-prompt-file "$skill_file")
fi

read_only=()
case "$role" in
  planner|verifier|researcher|architect|scout|archaeologist|filer)
    read_only=(--disallowedTools Edit Write NotebookEdit) ;;
esac

cmd=(claude -p
  --plugin-dir "$plugin_root"
  --agent "sdlc-lite:$role"
  --model "$model" --effort "$effort"
  --dangerously-skip-permissions
  --output-format json
  ${read_only[@]+"${read_only[@]}"}
  ${skill_prompt[@]+"${skill_prompt[@]}"}
  --
  "Handoff: $handoff
Artifacts dir: $dir
Your final message is saved verbatim as $result. Make it exactly the output format your instructions define: start with its first heading, with nothing before it and nothing after the last section.")

if [[ "${SDLC_DRY_RUN:-}" == 1 ]]; then printf '%q ' "${cmd[@]}"; echo; exit 0; fi

running="$dir/$role-$level.running"
date +%s >"$running"; trap 'rm -f "$running" ${skill_file:+"$skill_file"}' EXIT
SDLC_ROLE="$role" "${cmd[@]}" </dev/null >"$log" 2>&1 || { echo "$role exited non-zero; see $log" >&2; exit 1; }
if ! jq -e '.is_error == false and (.result | length > 0)' "$log" >/dev/null 2>&1; then
  echo "$role returned no result; see $log" >&2; exit 1
fi
{ echo "<!-- role=$role level=$level model=$model effort=$effort -->"; jq -r '.result' "$log"; } >"$result"
jq -c --arg role "$role" --arg level "$level" --arg model "$model" --arg effort "$effort" \
  --arg file "$name.md" \
  '{ts: (now|todate), role: $role, level: $level, model: $model, effort: $effort, file: $file,
    cost_usd: .total_cost_usd, duration_ms: .duration_ms, turns: .num_turns}' "$log" >>"$dir/runs.jsonl"

# Required section per role; builder and verifier also need an allowed first value under it.
case "$role" in
  builder) sect=Status; allowed='done|blocked' ;;
  verifier) sect=Verdict; allowed='pass|fail' ;;
  planner) sect=Goal; allowed='' ;;
  researcher) sect=Answer; allowed='' ;;
  scout) sect=Map; allowed='' ;;
  archaeologist) sect=Summary; allowed='' ;;
  architect) sect=Approach; allowed='' ;;
  filer) sect=Warnings; allowed='' ;;
esac
# Prints "missing", or the first non-blank line under the section (empty if none).
val=$(awk -v h="## $sect" '
  !f { l=$0; sub(/[ \t\r]+$/, "", l); if (l == h) { f=1 }; next }
  { l=$0; gsub(/^[ \t]+|[ \t\r]+$/, "", l); if (l != "") { print l; found=1; exit } }
  END { if (!f) print "missing"; else if (!found) print "" }' "$result")
bad=0
if [[ "$val" == missing && -z "$allowed" ]]; then bad=1
elif [[ -n "$allowed" ]]; then
  lc=$(printf '%s' "$val" | tr '[:upper:]' '[:lower:]')
  [[ "$lc" =~ ^($allowed)$ ]] || bad=1
fi
if (( bad )); then
  echo "run.sh: $role result lacks ## $sect${allowed:+ ($allowed)}; see $result" >&2
  exit 3
fi
echo "$result"
