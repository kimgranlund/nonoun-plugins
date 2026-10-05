#!/bin/bash
# usage: hidden.sh <task> <worktree>   runs the hidden check from the worktree root; prints PASS/FAIL line, exit 0 only on pass
n=$1; w=$2
cd "$w" || exit 9
case $n in
  footprint) python3 /tmp/bench-sl/tests/footprint.py;;
  *) bash /tmp/bench-sl/tests/$n.sh;;
esac
