#!/usr/bin/env bash
# Summarize benchmark runs: one row per bench/results/<date>-<task> dir.
# Columns: run, hidden check (the real score), steps, steps the verifier passed, builder attempts, total cost.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
printf '%-40s %7s %6s %7s %9s %9s\n' run hidden steps passed attempts cost_usd
for d in "$root"/bench/results/*/; do
  [[ -d "$d" ]] || continue
  steps=0; passed=0; attempts=0
  for s in "$d"step-*/; do
    [[ -d "$s" ]] || continue
    steps=$((steps+1))
    attempts=$((attempts + $(jq -s '[.[] | select(.role=="builder")] | length' "$s/runs.jsonl" 2>/dev/null || echo 0)))
    v=$(ls -t "$s"verifier-*.md 2>/dev/null | head -1 || true)
    [[ -n "$v" ]] && grep -A1 '^## Verdict' "$v" | grep -qx 'pass' && passed=$((passed+1))
  done
  cost=$(cat "$d"runs.jsonl "$d"step-*/runs.jsonl 2>/dev/null | jq -s 'map(.cost_usd // 0) | add // 0 | . * 100 | round / 100')
  hidden=$(grep -o 'hidden_check: [a-z]*' "$d"grade.md 2>/dev/null | cut -d' ' -f2 || true)
  printf '%-40s %7s %6s %7s %9s %9s\n' "$(basename "$d")" "${hidden:-none}" "$steps" "$passed" "$attempts" "$cost"
done
