#!/usr/bin/env bash
# T-0552 live probe: plant an idle stdin reader under this shell (a Claude Bash tool call, so a role descendant),
# check that detect reports it, that resolve refuses a sibling pid, and that resolve kills only the planted reader.
# Run from the repo root. Exit 0 means all three held.
set -u
S=$(mktemp -d)
D=plugins/sdlc-lite/scripts/fleet_doctor.py
mkfifo "$S/f"
sleep 300 > "$S/f" &
writer=$!
cat < "$S/f" > "$S/x" &
reader=$!
sleep 2
python3 "$D" collect --state-dir "$S" > /dev/null
python3 "$D" detect --state-dir "$S" --stdin-wait-min 0 > "$S/out.txt"
grep "stdin-wait  pid $reader " "$S/out.txt"; found=$?
python3 "$D" resolve --state-dir "$S" --kill "$writer"; refused=$?
python3 "$D" resolve --state-dir "$S" --kill "$reader"
sleep 1
ps -p "$reader" > /dev/null; reader_alive=$?
ps -p "$writer" > /dev/null; writer_alive=$?
echo "found=$found refused_sibling=$refused reader_gone=$reader_alive writer_alive=$((1 - writer_alive))"
kill "$writer" 2> /dev/null
[ "$found" = 0 ] && [ "$refused" = 2 ] && [ "$reader_alive" != 0 ] && [ "$writer_alive" = 0 ]
