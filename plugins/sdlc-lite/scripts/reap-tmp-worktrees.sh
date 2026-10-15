#!/usr/bin/env bash
# Usage: reap-tmp-worktrees.sh <main checkout> [<own prefix>]
# Reaps throwaway worktree prefixes left by run.sh runs that died without their exit cleanup (a
# SIGKILL, or a role that outlived run_lifecycle.py's grace period). run.sh calls it at the start
# and at the end of every real run; fanout calls it for a lane after each driver.
# A prefix is a directory directly under <wtroot.py root>/tmp/ (the sibling <main checkout>.worktrees/tmp, T-0563, or
# under a worktree_root: line or a bare clone's <bare parent>/lanes, T-0561), or for one release the legacy
# <main checkout>/.claude/worktrees/tmp/ (T-0550) and <main checkout>/.worktrees/tmp/, named <role>-<pid> (matching
# ^[a-z]+-[0-9]+$), the SDLC_TMP_WORKTREES of the run.sh whose pid it names. A prefix is skipped when
# that pid names a live process (ps -p, so a process owned by another user counts as alive) or when
# it is <own prefix> (compared by physical path). Every other prefix has a dead owner: each
# registered worktree under it (paths compared by physical path, since macOS reports /private/var
# for /var) gets git worktree remove --force --force, then the prefix is removed with rm -rf.
# Finally git worktree prune runs, then each tmp dir, and the legacy .worktrees, are removed only when empty
# (.claude/worktrees itself is Claude Code's and stays).
# Without ps on PATH liveness cannot be told, so it reaps nothing and exits 0.
# Contract: it always exits 0. It deletes files only under the tmp dirs (plus the empty tmp dirs and the
# empty legacy .worktrees dir themselves); git worktree remove and prune also drop the matching
# entries in git's own worktree records. It never removes a worktree outside a dead owner's prefix,
# never deletes a branch, and never changes the caller's exit code (callers ignore its status).
set -u

top="${1:-}"
own="${2:-}"
[[ -n "$top" && -d "$top" ]] || exit 0
command -v ps >/dev/null 2>&1 || exit 0

# phys <path>: physical path, resolving the deepest existing ancestor, so a missing path still compares.
phys() {
  local p="$1" rest="" r
  while [[ "$p" == /?* && ! -d "$p" ]]; do rest="/${p##*/}$rest"; p="${p%/*}"; done
  r=$(cd "${p:-/}" 2>/dev/null && pwd -P) || { printf '%s\n' "$1"; return 0; }
  printf '%s%s\n' "${r%/}" "$rest"
}

wt_tmp=$(python3 "$(dirname "$0")/wtroot.py" root --cwd "$top" 2>/dev/null) && wt_tmp="$wt_tmp/tmp" || wt_tmp="$top.worktrees/tmp"
[[ "$wt_tmp" == "$top/.claude/worktrees/tmp" ]] && wt_tmp=""
for base in "$top/.claude/worktrees/tmp" "$top/.worktrees/tmp" ${wt_tmp:+"$wt_tmp"}; do
  [[ -d "$base" ]] || continue
  own_real=""
  [[ -n "$own" ]] && own_real=$(phys "$own")
  wts=$(git -C "$top" worktree list --porcelain 2>/dev/null | sed -n 's/^worktree //p') || wts=""
  for d in "$base"/*; do
    [[ -d "$d" && ! -L "$d" ]] || continue
    n="${d##*/}"
    [[ "$n" =~ ^[a-z]+-([0-9]+)$ ]] || continue
    pid="${BASH_REMATCH[1]}"
    d_real=$(phys "$d")
    if [[ -n "$own" ]] && [[ "$d" == "$own" || "$d_real" == "$own_real" ]]; then continue; fi
    ps -p "$pid" >/dev/null 2>&1 && continue
    while IFS= read -r p; do
      [[ -n "$p" ]] || continue
      pr=$(phys "$p")
      if [[ "$pr" == "$d_real"/* || "$p" == "$d"/* ]]; then
        git -C "$top" worktree remove --force --force "$p" >/dev/null 2>&1
      fi
    done <<<"$wts"
    rm -rf "$d"
  done
done
git -C "$top" worktree prune >/dev/null 2>&1
rmdir "$top/.claude/worktrees/tmp" "$top/.worktrees/tmp" ${wt_tmp:+"$wt_tmp"} >/dev/null 2>&1
rmdir "$top/.worktrees" >/dev/null 2>&1
exit 0
