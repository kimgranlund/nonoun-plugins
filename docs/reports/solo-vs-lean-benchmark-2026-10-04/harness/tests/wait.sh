#!/bin/bash
# hidden check: run from the repo root of the worktree
M="$PWD/plugins/sdlc-lite/scripts/messages.py"
T=$(mktemp -d); cd "$T"; git init -q; mkdir -p .sdlc
fail() { echo "FAIL: $1"; cd /; rm -rf "$T"; exit 1; }
out=$(python3 "$M" wait --receiver codex --timeout 1 --interval 1 2>&1); rc=$?
[ $rc -eq 3 ] || fail "timeout rc=$rc"
echo "$out" | grep -Fq "no new messages" || fail "timeout text"
python3 "$M" send --receiver codex --sender claude --topic t --follow-up false "hello" >/dev/null || fail "send"
before=$(find .sdlc/messages -type f | sort | xargs shasum | shasum)
out=$(python3 "$M" wait --receiver codex --timeout 5 --interval 1 2>&1); rc=$?
[ $rc -eq 0 ] || fail "arrived rc=$rc"
f=$(ls .sdlc/messages/new/codex/*.md | head -1); id=$(basename "$f" .md)
echo "$out" | grep -Fq "$id" || fail "id missing from output"
echo "$out" | grep -Fq "$f" || fail "path missing from output"
after=$(find .sdlc/messages -type f | sort | xargs shasum | shasum)
[ "$before" = "$after" ] || fail "wait changed message state"
[ -f "$f" ] || fail "message claimed"
echo "$out" | grep -Fq "hello" && fail "body printed"
# other receiver still times out
python3 "$M" wait --receiver claude --timeout 1 --interval 1 >/dev/null 2>&1; [ $? -eq 3 ] || fail "wrong receiver woke"
# arrives mid-wait
rm -rf .sdlc/messages/new/codex/*.md
( python3 "$M" wait --receiver codex --timeout 20 --interval 1 > /tmp/bench-wait-mid.$$ 2>&1; echo $? > /tmp/bench-wait-mid-rc.$$ ) &
sleep 3
python3 "$M" send --receiver codex --sender claude --topic t2 --follow-up false "second" >/dev/null
wait
[ "$(cat /tmp/bench-wait-mid-rc.$$)" = "0" ] || fail "mid-wait rc"
grep -Fq "t2" /tmp/bench-wait-mid.$$ || fail "mid-wait output"
rm -f /tmp/bench-wait-mid*.$$
# bad arguments
for tmo in 0 601 abc; do python3 "$M" wait --receiver codex --timeout $tmo >/dev/null 2>&1; [ $? -ne 0 ] || fail "bad timeout $tmo accepted"; done
python3 "$M" wait --receiver "bad name" --timeout 1 >/dev/null 2>&1; [ $? -ne 0 ] || fail "bad receiver accepted"
cd /; rm -rf "$T"; echo PASS
