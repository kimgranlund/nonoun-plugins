#!/bin/bash
# usage: lane-wait.sh <lane> <pr>
# Waits for the PR to merge on green (gh pr merge --auto, merge queue), then closes the lane.
. "$(dirname "$0")/env.sh"
lane=$1; pr=$2
gh pr merge "$pr" --repo "$REPO" --auto >/dev/null 2>&1
while :; do
  s=$(gh pr view "$pr" --repo "$REPO" --json state --jq .state 2>/dev/null || echo ERR)
  case $s in MERGED) echo "PR $pr MERGED"; "$(dirname "$0")/lane-close.sh" "$lane"; exit 0;; CLOSED) echo "PR $pr CLOSED, lane $lane left open"; exit 1;; esac
  sleep 45
done
