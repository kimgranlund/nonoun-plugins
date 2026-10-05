#!/bin/bash
task=$1; B=/tmp/bench-sl; W=$B/wt/$task-lean; O=$B/out/$task-lean
R=/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/bench-runner/plugins/sdlc-lite/scripts
cd $W
{ printf '\n## Plan defect (replan 1)\nThe previous plan failed steps lint: a criterion command did not parse under bash -n, or compared a count over a changing set with a fixed number. Write criteria whose commands parse (no nested or escaped quotes) and derive sets at run time.\n'; } >> .sdlc/bench-$task/handoff.md
t0=$(date +%s)
SDLC_ROUTING_REASON="bench replan after lint plan defect" bash $R/run.sh planner L3 $PWD/.sdlc/bench-$task/handoff.md > $O/replan.out 2>&1
echo "rc=$? wall=$(( $(date +%s)-t0 ))" > $O/replan.txt
bash $B/resume.sh $task
