#!/usr/bin/env bash
# Usage: bench.sh [--bench-dir DIR] [task ...]   (default: every task in <bench>/tasks/)
# The bench dir comes from bench-dir.sh: --bench-dir, $SDLC_BENCH_DIR, <project>/bench, else the plugin's bench/.
# Runs /bench headless, one task per session, then prints the summary.
# Each task's log ends with an `exit=<code> duration=<N>s` trailer.
# Raises the Bash tool timeouts so long role runs can stay in the foreground, and sets
# SDLC_HEADLESS=1 so hooks/block-background.sh denies run_in_background.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
dirargs=()
if [[ "${1:-}" == "--bench-dir" ]]; then
  [[ $# -ge 2 ]] || { echo "usage: bench.sh [--bench-dir DIR] [task ...]" >&2; exit 2; }
  dirargs=(--bench-dir "$2"); shift 2
fi
bench="$("$root/scripts/bench-dir.sh" ${dirargs[@]+"${dirargs[@]}"})" || exit 2
mkdir -p "$bench/logs"
if [[ $# -eq 0 ]]; then
  tasks=()
  while IFS= read -r t; do tasks+=("$t"); done < <(find "$bench/tasks" -name '*.md' ! -name README.md -exec basename {} .md \; | sort)
  set -- "${tasks[@]}"
fi
for t in "$@"; do
  echo "== $t $(date +%H:%M)"
  log="$bench/logs/$(date +%Y-%m-%d)-$t.txt"
  start=$SECONDS
  SDLC_BENCH_DIR="$bench" SDLC_HEADLESS=1 BASH_DEFAULT_TIMEOUT_MS=3600000 BASH_MAX_TIMEOUT_MS=3600000 \
    claude -p --plugin-dir "$root" --model opus --effort medium --dangerously-skip-permissions \
    "/sdlc-lite:bench $t" </dev/null >"$log" 2>&1
  rc=$?
  line="exit=$rc duration=$((SECONDS - start))s"
  echo "$line" >>"$log"
  echo "$line"
done
"$root/scripts/bench-summary.sh" --bench-dir "$bench"
