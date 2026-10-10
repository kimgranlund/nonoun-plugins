#!/bin/bash
# usage: lane-open.sh <lane>
# Opens lane/<lane> as a worktree at $LANES/<lane> off origin/main, bootstraps it,
# and assigns a port in 7400-7699. Refuses a name already in use.
. "$(dirname "$0")/env.sh"
lane=$1; [ -n "$lane" ] || { echo "usage: lane-open.sh <lane>"; exit 2; }
[ -e "$LANES/$lane" ] && { echo "lane exists: $LANES/$lane"; exit 1; }
git -C "$BARE" show-ref -q "refs/heads/lane/$lane" && { echo "branch lane/$lane exists"; exit 1; }
git -C "$BARE" fetch -q origin || exit 1
git -C "$BARE" worktree add "$LANES/$lane" -b "lane/$lane" origin/main >/dev/null 2>&1 || { echo "worktree add failed"; exit 1; }
used=$(cat "$LANES"/*/.lane.json 2>/dev/null | grep -o '"port": *[0-9]*' | grep -o '[0-9]*$')
for p in $(seq 7400 7699); do echo "$used" | grep -qx $p && continue; lsof -nP -iTCP:$p -sTCP:LISTEN >/dev/null 2>&1 && continue; port=$p; break; done
printf '{"lane":"%s","branch":"lane/%s","port":%s,"opened":"%s"}\n' "$lane" "$lane" "${port:-0}" "$(date -u +%FT%TZ)" > "$LANES/$lane/.lane.json"
grep -q '^.lane.json' "$BARE/info/exclude" 2>/dev/null || echo '.lane.json' >> "$BARE/info/exclude"
# a sibling lane has no parent node_modules to borrow, so install first, then bootstrap
( cd "$LANES/$lane" && pnpm install >/dev/null 2>&1 && node scripts/dev/bootstrap-worktree.mjs >/dev/null 2>&1 ) || echo "warn: install or bootstrap failed, run both by hand in $LANES/$lane"
echo "opened $LANES/$lane port=$port"
