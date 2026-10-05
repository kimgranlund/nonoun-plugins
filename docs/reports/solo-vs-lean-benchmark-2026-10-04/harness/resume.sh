#!/bin/bash
# resume a lean arm after a replan: run the driver again (planner exists), then grade
task=$1
B=/tmp/bench-sl; REPO=/Users/kimgranlund/Projects/nonoun/sdlc-lite
W=$B/wt/$task-lean; O=$B/out/$task-lean
t0=$(date +%s)
( cd $W && python3 - "$O" "$W" "bench-$task" <<'PY'
import subprocess,sys
o,w,task=sys.argv[1:4]
try:
    p=subprocess.run(['bash',o+'/drive.sh',w,task,'L2'],capture_output=True,text=True,timeout=4500)
    open(o+'/drive2.log','w').write(p.stdout+p.stderr)
except subprocess.TimeoutExpired as e:
    open(o+'/drive2.log','w').write('TIMEOUT 75 min')
PY
)
t1=$(date +%s)
bash $B/hidden.sh $task $W > $O/hidden.txt 2>&1; hrc=$?
( cd $W && bash plugins/sdlc-lite/scripts/check.sh > $O/check-sh.txt 2>&1; echo $? > $O/check-sh.rc )
echo "$task lean-resume wall=$((t1-t0))s hidden_rc=$hrc check_sh_rc=$(cat $O/check-sh.rc)" | tee -a $O/summary.txt >> $B/all.log
