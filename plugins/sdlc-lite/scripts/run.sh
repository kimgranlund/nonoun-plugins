#!/usr/bin/env bash
# Usage: run.sh <role> <level> <handoff.md>
# Runs one role headless in the current directory with the level's model and effort.
# Writes <handoff dir>/<role>-<level>.md (the agent's final message) and <role>-<level>.log
# (raw JSON), keeps <role>-<level>.running while the run is live (for /board and the
# status line), and appends one line to <handoff dir>/runs.jsonl for /bench.
# Runs with --dangerously-skip-permissions; hooks/block-publish.sh still blocks publishing (via SDLC_ROLE). Every role except builder gets Edit/Write/NotebookEdit disallowed.
# Preflight: exits 2 unless the current directory is in a git work tree with at least one commit.
# Env: SDLC_DRY_RUN=1 prints the command only (after the preflight).
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
  verifier:L2)      model=fable;  effort=medium ;;
  verifier:L3)      model=fable;  effort=xhigh ;;
  researcher:L1)    model=sonnet; effort=medium ;;
  researcher:L2)    model=opus;   effort=medium ;;
  researcher:L3)    model=opus;   effort=high ;;
  architect:L1)     model=fable;  effort=high ;;
  scout:L1)         model=haiku;  effort=low ;;
  archaeologist:L1) model=sonnet; effort=medium ;;
  filer:L1)         model=opus;   effort=low ;;
  *) usage ;;
esac
[[ -f "$handoff" ]] || { echo "handoff not found: $handoff" >&2; exit 2; }
# Git preflight: roles need a repo with a commit (diffs, worktrees). Never init git here.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo: run git init and commit first" >&2; exit 2; }
git rev-parse --verify -q HEAD >/dev/null || { echo "git repo has no commit: commit first" >&2; exit 2; }

plugin_root="$(cd "$(dirname "$0")/.." && pwd)"
handoff="$(cd "$(dirname "$handoff")" && pwd)/$(basename "$handoff")"
dir="$(dirname "$handoff")"
result="$dir/$role-$level.md"
log="$dir/$role-$level.log"

# Fable never verifies a Fable build: fall back to Opus at the same effort.
if [[ "$role" == verifier ]]; then
  built=$(ls -t "$dir"/builder-L*.md 2>/dev/null | head -1 || true)
  if [[ -n "$built" ]]; then
    bmodel=$(grep -o 'model=[a-z]*' "$built" | head -1 | cut -d= -f2 || true)
    [[ "$model" == fable && "$bmodel" == fable ]] && model=opus
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
  '{ts: (now|todate), role: $role, level: $level, model: $model, effort: $effort,
    cost_usd: .total_cost_usd, duration_ms: .duration_ms, turns: .num_turns}' "$log" >>"$dir/runs.jsonl"
echo "$result"
