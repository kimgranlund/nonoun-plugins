#!/bin/bash
# usage: idle-drive.sh <worktree> <task-slug> <planner-level>   (a minimal /chain driver: planner, review, split, build and verify each step)
wt="$1"; task="$2"; plv="${3:-L2}"
RUN=/Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/run.sh
S="python3 $wt/plugins/sdlc-lite/scripts/steps.py"
cd "$wt" || exit 9
d=".sdlc/$task"
log() { echo "$(date +%H:%M:%S) $*"; }
role() {
  local n=0
  while :; do
    SDLC_ROUTING_REASON="$task: $4" bash "$RUN" "$1" "$2" "$3" >/tmp/idle-role-$$.out 2>&1; rc=$?
    log "rc $rc $1 $2 $3 -> $(tail -1 /tmp/idle-role-$$.out)"
    [ $rc -eq 0 ] && return 0
    lf=$(tail -1 /tmp/idle-role-$$.out | grep -o '/[^ ]*\.log' | head -1)
    if [ -n "$lf" ] && grep -q "session limit" "$lf" 2>/dev/null; then log "STOP session limit"; exit 75; fi
    if [ -n "$lf" ] && grep -q "529" "$lf" 2>/dev/null && [ $n -lt 2 ]; then n=$((n+1)); log "529 overloaded, retry $n after 150s"; sleep 150; continue; fi
    return $rc
  done
}
if ! ls $d/planner-L*.md >/dev/null 2>&1; then
  role planner "$plv" "$d/handoff.md" "task plan at $plv per ticket size" || { log STOP planner failed; exit 1; }
fi
for i in 1 2 3 4; do
  act=$($S review "$d" | head -1); log "review: $act"
  case "$act" in
    split*) break;;
    "review L1") role plan-reviewer L1 "$d/handoff.md" "plan review required" || { log STOP reviewer failed; exit 1; };;
    replan*) log "STOP replan needed: $($S review "$d" | head -4 | tr '\n' ' ')"; exit 2;;
    *) log "STOP review action: $act"; exit 2;;
  esac
done
[ "$act" = "split" ] || { log STOP no split; exit 2; }
[ -d "$d/step-1" ] || $S split "$d" || { log "STOP split refused"; exit 2; }
for sd in $(ls -d $d/step-[0-9]* 2>/dev/null | grep -v superseded | sort -t- -k2 -n); do
  while :; do
    out=$($S next "$sd"); act=$(echo "$out" | head -1); log "$sd next: $act"
    case "$act" in
      done) break;;
      build*|rebuild*|bump*)
        lv=$(echo "$act" | awk '{print $2}')
        if [[ "$act" == rebuild* || "$act" == bump* ]]; then
          vf=$(ls -t $sd/verifier-L*.md 2>/dev/null | head -1)
          if [ -n "$vf" ] && ! grep -q "^## Previous attempt" "$sd/handoff.md"; then
            { printf '\n## Previous attempt\n'; awk '/^## For the next attempt/{f=1;next} /^## /{f=0} f' "$vf"; } >> "$sd/handoff.md"
          fi
        fi
        role builder "$lv" "$sd/handoff.md" "$act" || { log "STOP builder rc"; exit 1; };;
      verify*|reverify*)
        lv=$(echo "$act" | awk '{print $2}')
        role verifier "$lv" "$sd/handoff.md" "$act" || { log "STOP verifier rc"; exit 1; };;
      *) log "STOP action: $act ($(echo "$out" | sed -n 2,4p | tr '\n' ' '))"; exit 2;;
    esac
  done
done
log "ALL STEPS DONE $task"
