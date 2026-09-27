#!/usr/bin/env bash
# Usage: run.sh <role> <level> <handoff.md>
# Runs one role headless in the current directory with the level's model and effort.
# Writes <handoff dir>/<role>-<level>.md (the agent's report) and <role>-<level>.log
# (raw stream-json: one JSON event per line, stderr mixed in). A rerun of the same role and level (a replan, a rebuild) never overwrites: it
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
# does not create it; a role makes worktrees only under it (git worktree add "$SDLC_TMP_WORKTREES/<name>"
# HEAD makes the parents). On every exit, success or failure (exit 1, exit 3, INT, TERM, HUP), cleanup
# runs git worktree remove --force on each registered worktree under that prefix (paths compared by
# realpath, since macOS reports /private/var for /var), rm -rf of the prefix, git worktree prune, then
# rmdir of .worktrees/tmp and .worktrees only when empty. It touches only this run's prefix, never other
# worktrees that appeared during the run (concurrent fanout lanes run other role runs), and never
# changes the exit code; INT, TERM, and HUP exit 130, 143, and 129 after it.
# Exit codes: 0 ok, 1 run failed or returned no result, 2 usage or preflight, 3 result lacks its section.
# Result pick: the run uses --output-format stream-json --verbose, because plain json keeps only the
# session's last result, and a background task notification arriving after the report ends the session
# with its own result ("origin":{"kind":"task-notification"}), losing the report. The log is parsed
# leniently (lines that are not JSON are skipped) and only "type":"result" events count. The saved
# event is the last one whose .result holds a line exactly the role's required heading (trailing
# whitespace ignored), else the last one whose .origin.kind is not task-notification, else the last
# one. It must have is_error false and a non-empty .result (else exit 1); its .result is written to
# the result file. The runs.jsonl cost, duration, and turns come from the last result event, which
# holds the session totals.
# Env: SDLC_DRY_RUN=1 prints the command only (after the preflight and .nvmrc resolution).
# Bash timeouts: a real run passes BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS of 3600000 (as
# bench.sh does), keeping an inherited value only when it is a plain integer of at least 3600000.
# Claude Code moves a foreground Bash call to the background once it passes its timeout, and no
# PreToolUse hook sees that move, so hooks/block-background.sh cannot stop it (T-0105).
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
  --output-format stream-json --verbose
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
on_exit() {
  local rc=$?
  set +e
  rm -f "$running" ${skill_file:+"$skill_file"}
  cleanup_worktrees
  exit "$rc"
}
running="$dir/$role-$level.running"
date +%s >"$running"
trap on_exit EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
# Bash timeouts (see the header, T-0105): at least 3600000 ms, else replaced.
bash_timeout() { if [[ "${1:-}" =~ ^[0-9]+$ ]] && (( 10#$1 >= 3600000 )); then echo "$1"; else echo 3600000; fi; }
bash_default_ms=$(bash_timeout "${BASH_DEFAULT_TIMEOUT_MS:-}")
bash_max_ms=$(bash_timeout "${BASH_MAX_TIMEOUT_MS:-}")
SDLC_ROLE="$role" SDLC_TMP_WORKTREES="$wt_tmp" BASH_DEFAULT_TIMEOUT_MS="$bash_default_ms" BASH_MAX_TIMEOUT_MS="$bash_max_ms" "${cmd[@]}" </dev/null >"$log" 2>&1 || { echo "$role exited non-zero; see $log" >&2; exit 1; }
# Result pick (see the header): result events only, non-JSON lines skipped.
events=$(jq -R -c 'fromjson? // empty | select(type == "object" and .type == "result")' "$log" 2>/dev/null || true)
pick=$(jq -s -c --arg h "## $sect" '
  def has_head: (.result | strings | split("\n") | map(sub("[ \t\r]+$"; "")) | any(. == $h)) // false;
  (map(select(has_head)) | last)
  // (map(select((.origin.kind? // "") != "task-notification")) | last)
  // last // empty' <<<"$events" 2>/dev/null || true)
last_ev=$(jq -s -c 'last // empty' <<<"$events" 2>/dev/null || true)
if [[ -z "$pick" ]] || ! jq -e '.is_error == false and (.result | strings | length > 0)' <<<"$pick" >/dev/null 2>&1; then
  echo "$role returned no result; see $log" >&2; exit 1
fi
{ echo "<!-- role=$role level=$level model=$model effort=$effort -->"; jq -r '.result' <<<"$pick"; } >"$result"
jq -c --arg role "$role" --arg level "$level" --arg model "$model" --arg effort "$effort" \
  --arg file "$name.md" \
  '{ts: (now|todate), role: $role, level: $level, model: $model, effort: $effort, file: $file,
    cost_usd: .total_cost_usd, duration_ms: .duration_ms, turns: .num_turns}' <<<"$last_ev" >>"$dir/runs.jsonl"

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
