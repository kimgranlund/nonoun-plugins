#!/usr/bin/env bash
# Usage: bench.sh [task ...]   (default: every task in bench/tasks/)
# Runs /bench headless, one task per session, then prints the summary.
# Raises the Bash tool timeouts so long role runs can stay in the foreground.
set -uo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$root/bench/logs"
if [[ $# -eq 0 ]]; then
  tasks=()
  while IFS= read -r t; do tasks+=("$t"); done < <(find "$root/bench/tasks" -name '*.md' ! -name README.md -exec basename {} .md \; | sort)
  set -- "${tasks[@]}"
fi
for t in "$@"; do
  echo "== $t $(date +%H:%M)"
  BASH_DEFAULT_TIMEOUT_MS=3600000 BASH_MAX_TIMEOUT_MS=3600000 \
    claude -p --plugin-dir "$root" --model opus --effort medium --dangerously-skip-permissions \
    "/sdlc-lite:bench $t" </dev/null >"$root/bench/logs/$(date +%Y-%m-%d)-$t.txt" 2>&1
  echo "exit=$?"
done
"$root/scripts/bench-summary.sh"
