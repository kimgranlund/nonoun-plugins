#!/bin/bash
# usage: lane-close.sh <lane> [--discard]
# Closes a lane: refuses if the tree is dirty or the work is not in origin/main
# (unless --discard), archives .sdlc/, removes the worktree, deletes the branch, prunes.
. "$(dirname "$0")/env.sh"
lane=$1; flag=$2; [ -n "$lane" ] || { echo "usage: lane-close.sh <lane> [--discard]"; exit 2; }
wt=$LANES/$lane; br=lane/$lane
[ -d "$wt" ] || { echo "no lane at $wt"; exit 1; }
git -C "$BARE" fetch -q origin
dirty=$(git -C "$wt" status --porcelain | grep -v '^?? .sdlc/' | grep -v '.lane.json')
[ -n "$dirty" ] && [ "$flag" != "--discard" ] && { echo "REFUSE: uncommitted changes in $lane"; echo "$dirty" | head -5; exit 1; }
if [ "$flag" != "--discard" ]; then
  if ! git -C "$BARE" merge-base --is-ancestor "$br" origin/main 2>/dev/null; then
    files=$(git -C "$wt" diff --name-only "$(git -C "$wt" merge-base origin/main "$br")" "$br")
    for f in $files; do [ "$(git -C "$BARE" rev-parse -q --verify "$br:$f")" = "$(git -C "$BARE" rev-parse -q --verify "origin/main:$f")" ] || { echo "REFUSE: $br has changes not in origin/main (first: $f); push and merge, or --discard"; exit 1; }; done
  fi
fi
mkdir -p "$ARCHIVE/sdlc"; [ -d "$wt/.sdlc" ] && cp -R "$wt/.sdlc" "$ARCHIVE/sdlc/$lane"
sha=$(git -C "$BARE" rev-parse "$br"); echo "$br $sha" >> "$ARCHIVE/closed-lanes.txt"
git -C "$BARE" worktree remove --force "$wt" && git -C "$BARE" branch -D "$br" >/dev/null && git -C "$BARE" worktree prune
echo "closed $lane (branch sha $sha saved in closed-lanes.txt)"
