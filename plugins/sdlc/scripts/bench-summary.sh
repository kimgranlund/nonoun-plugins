#!/usr/bin/env bash
# Usage: bench-summary.sh [--bench-dir DIR]
# Summarize benchmark runs: one row per <bench>/results/<date>-<task> dir.
# The bench dir comes from bench-dir.sh: --bench-dir, $SDLC_BENCH_DIR, <project>/bench, else the plugin's bench/.
# Columns: run, hidden check (the real score), steps, steps the verifier passed, builder attempts, total cost.
# Step dirs and runs.jsonl come from the run's records dir (order.py records-dir: results/runtime/tasks/<run>/,
# or the results dir itself when it already holds records); grade.md stays in the results dir.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
bench="$("$root/scripts/bench-dir.sh" "$@")"
printf '%-40s %7s %6s %7s %9s %9s\n' run hidden steps passed attempts cost_usd
for d in "$bench"/results/*/; do
  [[ -d "$d" ]] || continue
  [[ "$(basename "$d")" == runtime ]] && continue
  rd="$(python3 "$root/scripts/order.py" records-dir "$d")"
  steps=0; passed=0; attempts=0
  for s in "$rd"/step-*/; do
    [[ -d "$s" ]] || continue
    # Superseded dirs (step-N.superseded-K) count for cost only (line below the loop), not as steps.
    [[ "$(basename "$s")" =~ ^step-[0-9]+$ ]] || continue
    steps=$((steps+1))
    attempts=$((attempts + $(jq -s '[.[] | select(.role=="builder")] | length' "$s/runs.jsonl" 2>/dev/null || echo 0)))
    v=$(python3 "$root/scripts/order.py" newest "$s" verifier)
    [[ -n "$v" ]] && grep -A1 '^## Verdict' "$v" | grep -qx 'pass' && passed=$((passed+1))
  done
  cost=$({ cat "$rd"/runs.jsonl "$rd"/step-*/runs.jsonl 2>/dev/null || true; } | jq -r -s 'if any(.[]; .backend == "codex" and .cost_usd == null) then "unknown" else (map(.cost_usd // 0) | add // 0 | . * 100 | round / 100) end')
  hidden=$(grep -o 'hidden_check: [a-z]*' "$d"grade.md 2>/dev/null | cut -d' ' -f2 || true)
  printf '%-40s %7s %6s %7s %9s %9s\n' "$(basename "$d")" "${hidden:-none}" "$steps" "$passed" "$attempts" "$cost"
done
