#!/usr/bin/env bash
# Usage: bench-dir.sh [--bench-dir DIR]
# Prints the absolute bench dir. First match wins:
#   1. --bench-dir DIR   2. $SDLC_BENCH_DIR   3. <git toplevel>/bench if it exists
#   4. the plugin's own bench/ dir.
set -euo pipefail
usage() { echo "usage: bench-dir.sh [--bench-dir DIR]" >&2; exit 2; }
abs() { case "$1" in /*) printf '%s\n' "$1" ;; *) printf '%s\n' "$PWD/$1" ;; esac; }
flag=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --bench-dir) [[ $# -ge 2 && -n "$2" ]] || usage; flag="$2"; shift 2 ;;
    *) usage ;;
  esac
done
if [[ -n "$flag" ]]; then abs "$flag"; exit 0; fi
if [[ -n "${SDLC_BENCH_DIR:-}" ]]; then abs "$SDLC_BENCH_DIR"; exit 0; fi
if top=$(git rev-parse --show-toplevel 2>/dev/null) && [[ -d "$top/bench" ]]; then
  printf '%s\n' "$top/bench"; exit 0
fi
printf '%s\n' "$(cd "$(dirname "$0")/.." && pwd)/bench"
