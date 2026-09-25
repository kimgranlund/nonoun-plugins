#!/usr/bin/env bash
# Usage: bench-summary.sh [--bench-dir DIR]
# Summarize benchmark runs: one row per <bench>/results/<date>-<task> dir.
# The bench dir comes from bench-dir.sh: --bench-dir, $SDLC_BENCH_DIR, <project>/bench, else the plugin's bench/.
# Columns: run, hidden check (the real score), steps, steps the verifier passed, builder attempts, total cost.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
bench="$("$root/scripts/bench-dir.sh" "$@")"
printf '%-40s %7s %6s %7s %9s %9s\n' run hidden steps passed attempts cost_usd
for d in "$bench"/results/*/; do
  [[ -d "$d" ]] || continue
  steps=0; passed=0; attempts=0
  for s in "$d"step-*/; do
    [[ -d "$s" ]] || continue
    # Superseded dirs (step-N.superseded-K) count for cost only (line below the loop), not as steps.
    [[ "$(basename "$s")" =~ ^step-[0-9]+$ ]] || continue
    steps=$((steps+1))
    attempts=$((attempts + $(jq -s '[.[] | select(.role=="builder")] | length' "$s/runs.jsonl" 2>/dev/null || echo 0)))
    v=""
    for f in "$s"verifier-*.md; do
      [[ -f "$f" ]] || continue
      if [[ -z "$v" || "$f" -nt "$v" ]]; then v="$f"; fi
    done
    [[ -n "$v" ]] && grep -A1 '^## Verdict' "$v" | grep -qx 'pass' && passed=$((passed+1))
  done
  cost=$({ cat "$d"runs.jsonl "$d"step-*/runs.jsonl 2>/dev/null || true; } | jq -s 'map(.cost_usd // 0) | add // 0 | . * 100 | round / 100')
  hidden=$(grep -o 'hidden_check: [a-z]*' "$d"grade.md 2>/dev/null | cut -d' ' -f2 || true)
  printf '%-40s %7s %6s %7s %9s %9s\n' "$(basename "$d")" "${hidden:-none}" "$steps" "$passed" "$attempts" "$cost"
done
