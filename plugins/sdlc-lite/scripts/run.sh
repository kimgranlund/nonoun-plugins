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
# hold the role's required section (a line exactly "## <Name>"): builder ## Status (done|blocked|inherited red: <tests>),
# verifier ## Verdict (pass|fail|inherited red: <tests>), planner ## Goal, researcher ## Answer, scout ## Map,
# archaeologist ## Summary, architect ## Approach, filer ## Warnings. Otherwise one stderr line, exit 3.
# Throwaway worktrees: a real run (never a dry run) passes the role
# SDLC_TMP_WORKTREES=<toplevel>/.worktrees/tmp/<role>-<pid of run.sh>, a prefix this run owns. run.sh
# does not create it; a role makes worktrees only under it (git worktree add --detach "$SDLC_TMP_WORKTREES/<name>"
# HEAD makes the parents). On every exit, success or failure (exit 1, exit 3, INT, TERM, HUP), cleanup
# runs git worktree remove --force on each registered worktree under that prefix (paths compared by
# realpath, since macOS reports /private/var for /var), rm -rf of the prefix, git worktree prune, then
# rmdir of .worktrees/tmp and .worktrees only when empty. It touches only this run's prefix, never other
# worktrees that appeared during the run (concurrent fanout lanes run other role runs), and never
# changes the exit code; INT, TERM, and HUP exit 130, 143, and 129 after it.
# Stray report: a real run (never a dry run) snapshots `git worktree list --porcelain` and the local
# branches (refs/heads) before the role starts. Worktrees and branches that appeared during this run
# (from a script, make target, or other program the hooks cannot see) are reported, leaving out this
# run's own prefix (compared by realpath). This run's runs.jsonl line always holds stray_worktrees
# (array of worktree paths) and stray_branches (array of branch names), empty arrays when none
# appeared. At exit, on success or failure (exit 1, exit 3, INT, TERM, HUP), after the cleanup, stderr
# gets one line per item, once per run: "run.sh: stray worktree appeared during this run: <path>
# [<branch>]" (no " [<branch>]" for a detached worktree) and "run.sh: stray branch appeared during
# this run: <branch>". It says "appeared during this run", not that this role made them, because
# concurrent fanout lanes and other role runs can add worktrees and branches too. It only reports:
# it never removes or deletes anything and never changes the exit code.
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
  # Removes it on a dry run or an early exit; on_exit replaces this trap and removes it too.
  trap 'rm -f "$skill_file"' EXIT
  while IFS= read -r sk; do
    src="$plugin_root/skills/$sk/SKILL.md"
    [[ -f "$src" ]] || { echo "agent $role declares missing skill: $sk" >&2; exit 2; }
    { echo "# Skill: $sk (loaded for this role; its relative paths are under $plugin_root/skills/$sk/)"
      # shellcheck disable=SC2016 # ${CLAUDE_PLUGIN_ROOT} is the literal text to replace.
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

# Throwaway worktree prefix owned by this run (see the header). Not created here.
toplevel="$(git rev-parse --show-toplevel)"
wt_tmp="$toplevel/.worktrees/tmp/$role-$$"
# phys <path>: physical path, resolving the deepest existing ancestor, so a missing path still compares.
phys() {
  local p="$1" rest="" r
  while [[ "$p" == /?* && ! -d "$p" ]]; do rest="/${p##*/}$rest"; p="${p%/*}"; done
  r=$(cd "${p:-/}" 2>/dev/null && pwd -P) || { printf '%s\n' "$1"; return 0; }
  printf '%s%s\n' "${r%/}" "$rest"
}
# Removes every worktree under this run's prefix only. Runs without errexit; never fails.
cleanup_worktrees() {
  local wt_real line p pr
  wt_real=$(phys "$wt_tmp")
  while IFS= read -r line; do
    case "$line" in "worktree "*) p="${line#worktree }" ;; *) continue ;; esac
    pr=$(phys "$p")
    if [[ "$pr" == "$wt_real" || "$pr" == "$wt_real"/* || "$p" == "$wt_tmp" || "$p" == "$wt_tmp"/* ]]; then
      git -C "$toplevel" worktree remove --force --force "$p" >/dev/null 2>&1
    fi
  done < <(git -C "$toplevel" worktree list --porcelain 2>/dev/null)
  rm -rf "$wt_tmp"
  git -C "$toplevel" worktree prune >/dev/null 2>&1
  rmdir "$toplevel/.worktrees/tmp" >/dev/null 2>&1
  rmdir "$toplevel/.worktrees" >/dev/null 2>&1
  return 0
}
# Stray report baseline (see the header): worktree paths and local branches before the role runs.
snap_wt=$(git -C "$toplevel" worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p') || snap_wt=""
snap_br=$(git -C "$toplevel" for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null) || snap_br=""
stray_done=0; stray_reported=0
stray_wt=(); stray_wt_br=(); stray_br=()
# in_list <item> <newline-separated list>: exact line match.
in_list() {
  local x
  while IFS= read -r x; do [[ "$x" == "$1" ]] && return 0; done <<<"$2"
  return 1
}
# Fills stray_wt (paths), stray_wt_br (branch or "" per path), and stray_br once per run.
# Called in an || list, so it runs without errexit; never fails.
detect_strays() {
  (( stray_done )) && return 0
  stray_done=1
  local wt_real line p="" b="" pr br now_wt now_br
  wt_real=$(phys "$wt_tmp")
  now_wt=$(git -C "$toplevel" worktree list --porcelain 2>/dev/null)
  # Porcelain records end at a blank line; $(...) strips the last one, so the input adds it back.
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) p="${line#worktree }"; b="" ;;
      "branch "*) b="${line#branch }"; b="${b#refs/heads/}" ;;
      "")
        if [[ -n "$p" ]] && ! in_list "$p" "$snap_wt"; then
          pr=$(phys "$p")
          if ! [[ "$pr" == "$wt_real" || "$pr" == "$wt_real"/* || "$p" == "$wt_tmp" || "$p" == "$wt_tmp"/* ]]; then
            stray_wt+=("$p"); stray_wt_br+=("$b")
          fi
        fi
        p=""; b="" ;;
    esac
  done <<<"$now_wt"$'\n'
  now_br=$(git -C "$toplevel" for-each-ref --format='%(refname:short)' refs/heads 2>/dev/null)
  while IFS= read -r br; do
    [[ -n "$br" ]] && ! in_list "$br" "$snap_br" && stray_br+=("$br")
  done <<<"$now_br"
  return 0
}
# json_array <item>...: a compact JSON array of strings.
json_array() {
  if (( $# == 0 )); then echo '[]'; return 0; fi
  printf '%s\n' "$@" | jq -Rsc 'split("\n") | .[:-1]'
}
# Prints the stray lines on stderr, once per run.
report_strays() {
  (( stray_reported )) && return 0
  stray_reported=1
  local i
  for (( i = 0; i < ${#stray_wt[@]}; i++ )); do
    echo "run.sh: stray worktree appeared during this run: ${stray_wt[$i]}${stray_wt_br[$i]:+ [${stray_wt_br[$i]}]}" >&2
  done
  for (( i = 0; i < ${#stray_br[@]}; i++ )); do
    echo "run.sh: stray branch appeared during this run: ${stray_br[$i]}" >&2
  done
  return 0
}
on_exit() {
  local rc=$?
  set +e
  rm -f "$running" ${skill_file:+"$skill_file"}
  cleanup_worktrees
  detect_strays || :
  report_strays
  exit "$rc"
}
running="$dir/$role-$level.running"
date +%s >"$running"
trap on_exit EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
SDLC_ROLE="$role" SDLC_TMP_WORKTREES="$wt_tmp" "${cmd[@]}" </dev/null >"$log" 2>&1 || { echo "$role exited non-zero; see $log" >&2; exit 1; }
if ! jq -e '.is_error == false and (.result | length > 0)' "$log" >/dev/null 2>&1; then
  echo "$role returned no result; see $log" >&2; exit 1
fi
{ echo "<!-- role=$role level=$level model=$model effort=$effort -->"; jq -r '.result' "$log"; } >"$result"
detect_strays || :
stray_wt_json=$(json_array ${stray_wt[@]+"${stray_wt[@]}"}) || stray_wt_json='[]'
stray_br_json=$(json_array ${stray_br[@]+"${stray_br[@]}"}) || stray_br_json='[]'
jq -c --arg role "$role" --arg level "$level" --arg model "$model" --arg effort "$effort" \
  --arg file "$name.md" --argjson stray_wt "$stray_wt_json" --argjson stray_br "$stray_br_json" \
  '{ts: (now|todate), role: $role, level: $level, model: $model, effort: $effort, file: $file,
    cost_usd: .total_cost_usd, duration_ms: .duration_ms, turns: .num_turns,
    stray_worktrees: $stray_wt, stray_branches: $stray_br}' "$log" >>"$dir/runs.jsonl"

# Required section per role; builder and verifier also need an allowed first value under it.
case "$role" in
  builder) sect=Status; allowed='done|blocked|inherited red: .+' ;;
  verifier) sect=Verdict; allowed='pass|fail|inherited red: .+' ;;
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
