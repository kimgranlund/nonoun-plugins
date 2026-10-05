#!/bin/bash
# usage: arm.sh <task> <solo|lean>
task=$1; arm=$2
B=/tmp/bench-sl; REPO=/Users/kimgranlund/Projects/nonoun/sdlc-lite
RUNNER=$REPO/.worktrees/bench-runner
base=$(awk '/^base:/{print $2}' $B/tasks/$task.md)
W=$B/wt/$task-$arm; O=$B/out/$task-$arm
mkdir -p $O
git -C $REPO worktree add -q --detach $W $base || exit 9
goal=$(awk '/^## Goal/{f=1} f' $B/tasks/$task.md)
t0=$(date +%s)
if [ $arm = solo ]; then
  printf '%s\n\nWork in this repository checkout (your current directory). Read the repository guidance first, implement the change, run the checks you think appropriate, and stop when it is done. Do not commit, push, or use the network.\n' "$goal" > $O/prompt.txt
  ( cd $W && python3 - "$O" <<'PY'
import subprocess,sys
o=sys.argv[1]
cmd=['claude','-p','--model','opus','--effort','high','--setting-sources','project','--disable-slash-commands','--dangerously-skip-permissions','--no-session-persistence','--output-format','json','--max-budget-usd','15']
try:
    p=subprocess.run(cmd,input=open(o+'/prompt.txt').read(),capture_output=True,text=True,timeout=2700)
    open(o+'/claude.json','w').write(p.stdout); open(o+'/claude.err','w').write(p.stderr)
except subprocess.TimeoutExpired as e:
    open(o+'/claude.json','w').write(''); open(o+'/claude.err','w').write('TIMEOUT 45 min')
PY
  )
else
  d=.sdlc/bench-$task
  mkdir -p $W/$d; printf '%s\n' "$goal" > $W/$d/handoff.md
  sed "s#^RUN=.*#RUN=$RUNNER/plugins/sdlc-lite/scripts/run.sh#; s#^S=.*#S=\"python3 $RUNNER/plugins/sdlc-lite/scripts/steps.py\"#" $B/drive.sh > $O/drive.sh
  ( cd $W && python3 - "$O" "$W" "bench-$task" <<'PY'
import subprocess,sys
o,w,task=sys.argv[1:4]
try:
    p=subprocess.run(['bash',o+'/drive.sh',w,task,'L2'],capture_output=True,text=True,timeout=4500)
    open(o+'/drive.log','w').write(p.stdout+p.stderr)
except subprocess.TimeoutExpired as e:
    open(o+'/drive.log','w').write((e.stdout or b'').decode()+'\nTIMEOUT 75 min')
PY
  )
fi
t1=$(date +%s)
# grade: hidden check, then the repository gate
bash $B/hidden.sh $task $W > $O/hidden.txt 2>&1; hrc=$?
( cd $W && bash plugins/sdlc-lite/scripts/check.sh > $O/check-sh.txt 2>&1; echo $? > $O/check-sh.rc )
git -C $W status --short | grep -v '^?? .sdlc/bench-' > $O/status.txt
git -C $W diff --stat > $O/diffstat.txt
echo "$task $arm wall=$((t1-t0))s hidden_rc=$hrc check_sh_rc=$(cat $O/check-sh.rc)" | tee $O/summary.txt
