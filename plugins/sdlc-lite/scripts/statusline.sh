#!/usr/bin/env bash
# Claude Code status line. Reads the status JSON on stdin (https://code.claude.com/docs/en/statusline).
# Line 1: model · dir · git (branch, * dirty, ↑ahead ↓behind, wt:<worktree>) · ctx % · $cost · duration
# Line 2 (only when <cwd>/.sdlc has tasks): live role run, then board.py --summary
#         ("<task> <pct>% (<passed>/<steps>) · 🔴<n> · ⚠ L5").
input=$(cat)
j() { jq -r "$1 // empty" <<<"$input"; }
root="$(cd "$(dirname "$0")/.." && pwd)"
cwd=$(j '.workspace.current_dir'); cwd=${cwd:-$(j '.cwd')}; cwd=${cwd:-.}

parts=("$(j '.model.display_name')" "${cwd##*/}")

if branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short -q HEAD 2>/dev/null || git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null); then
  g="$branch"
  [[ -n $(git -C "$cwd" --no-optional-locks status --porcelain -uno 2>/dev/null | head -1) ]] && g="$g*"
  if ab=$(git -C "$cwd" --no-optional-locks rev-list --left-right --count '@{u}...HEAD' 2>/dev/null); then
    read -r behind ahead <<<"$ab"
    (( ahead > 0 )) && g="$g ↑$ahead"
    (( behind > 0 )) && g="$g ↓$behind"
  fi
  wt=$(j '.workspace.git_worktree'); [[ -n $wt ]] && g="$g wt:$wt"
  parts+=("$g")
fi

ctx=$(j '.context_window.used_percentage')
if [[ -n $ctx ]]; then
  ctx=${ctx%.*}
  if (( ctx >= 85 )); then parts+=("🔴 ctx $ctx%"); elif (( ctx >= 70 )); then parts+=("🟡 ctx $ctx%"); else parts+=("ctx $ctx%"); fi
fi

cost=$(j '.cost.total_cost_usd'); ms=$(j '.cost.total_duration_ms')
if [[ -n $cost ]]; then
  c=$(printf '$%.2f' "$cost")
  [[ -n $ms ]] && c="$c · $(( ms / 60000 ))m"
  parts+=("$c")
fi

line1=$(IFS='|'; echo "${parts[*]}"); line1=${line1//|/ · }
printf '%s' "$line1"

sdlc="$cwd/.sdlc"
[[ -d "$sdlc" ]] || exit 0
second=()
run=$(find "$sdlc" -name '*.running' 2>/dev/null | head -1)
if [[ -n "$run" ]]; then
  rel=${run#"$sdlc"/}; step=$(grep -o 'step-[0-9]*' <<<"$rel" | head -1)
  mins=$(( ($(date +%s) - $(cat "$run" 2>/dev/null || date +%s)) / 60 ))
  second+=("🟡 ${step:+$step }$(basename "$run" .running) ${mins}m")
fi
summary=$(python3 "$root/scripts/board.py" --root "$sdlc" --summary 2>/dev/null)
[[ -n $summary ]] && second+=("$summary")
if (( ${#second[@]} )); then
  line2=$(IFS='|'; echo "${second[*]}"); printf '\n%s' "${line2//|/ · }"
fi
