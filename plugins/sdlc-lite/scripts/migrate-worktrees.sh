#!/usr/bin/env bash
# Usage: migrate-worktrees.sh [--apply]   run once per consumer repo, from its main checkout root
#        migrate-worktrees.sh --selftest  prove it on a throwaway fixture repo
# T-0563: SDLC Lite puts every worktree in the sibling root outside the repo, <main checkout parent>/<name>.worktrees/
# (scripts/wtroot.py root; a worktree_root: line in .sdlc/config overrides it). Before it, lanes and role trees lived
# under <main checkout>/.claude/worktrees/ (0.23.0 and 0.23.1, T-0550) or <main checkout>/.worktrees/ (before 0.23.0).
# A dry run (the default) prints each planned step and changes nothing; --apply acts. Idempotent: a second run finds
# nothing to move and changes nothing.
#   1. Each registered worktree under .worktrees/ or .claude/worktrees/ moves to the same relative path under the root
#      with git worktree move (never mv): `move .claude/worktrees/<rel> -> <root>/<rel>`. It is skipped and reported
#      (`skip <legacy>/<rel>: <why>`) when it is Claude Code's own tree (.claude/worktrees/agent-*), locked (a running
#      lane), has uncommitted changes (git status --porcelain), has a live owner (a *.running marker under it, a
#      .owner.json whose pid runs, or a run.sh prefix tmp/<role>-<pid> whose pid runs), is a lane whose branch has not
#      landed on the main branch (lanes.py landed: ancestor or every changed file equal), or its destination exists.
#   2. tickets.py --root .sdlc tidy (T-0544) lists, or with --apply moves, loose .sdlc/ entries into .sdlc/archive/.
#   3. Unregistered folders under a legacy root stay where they are and are listed (`left in place: <path>`).
#   4. With --apply, empty folders under each legacy root go; .worktrees/ itself is removed only when it ends empty,
#      .claude/worktrees/ itself stays (Claude Code's own folder).
# The last line is `nothing to move` when no worktree is planned to move (skips included).
# Read paths keep accepting both legacy roots for one release, so a skipped lane still lands; rerun after it lands.
# A bare clone (core.bare, lanes beside the bare dir, T-0561) has no main checkout: run from the bare dir or any lane,
# it prints `bare clone: worktree root <path>` (wtroot.py root) and `nothing to move`, changes nothing, and exits 0.
# Exit 0 when the run finished (skips included), 2 on a usage error or when not run from the main checkout root.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

migrate() {
  local apply=0 top cwd main common line p b locked rel dest why moved=0 planned=0 root src
  [[ "${1:-}" == --apply ]] && apply=1
  if git rev-parse --git-dir >/dev/null 2>&1 && [[ "$(git config --bool core.bare 2>/dev/null)" == true ]]; then
    echo "bare clone: worktree root $(python3 "$here/wtroot.py" root)"
    echo "nothing to move"
    return 0
  fi
  top=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "migrate-worktrees.sh: not a git repository" >&2; return 2; }
  cwd=$(pwd -P)
  common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
  if [[ "$(cd "$top" && pwd -P)" != "$cwd" || "${common##*/}" != .git || "$(cd "${common%/.git}" && pwd -P)" != "$cwd" ]]; then
    echo "migrate-worktrees.sh: run it from the main checkout root (the folder holding .git), not $cwd" >&2
    return 2
  fi
  top=$cwd
  root=$(python3 "$here/wtroot.py" root --cwd "$top") || { echo "migrate-worktrees.sh: wtroot.py root failed" >&2; return 2; }
  root=$(phys "$root")
  say() { if (( apply )); then echo "$1"; else echo "would $1"; fi; }

  main=$(git worktree list --porcelain | sed -n '1,/^$/s/^branch refs\/heads\///p' | head -n1)
  # the legacy roots this run reads; one that is the root itself (a worktree_root: line naming it) has nothing to move
  local -a legacy=()
  for src in .claude/worktrees .worktrees; do
    [[ "$top/$src" == "$root" || "$root" == "$top/$src/"* ]] || legacy+=("$src")
  done
  local -a paths=() srcs=() branches=() locks=()
  p="" b="" locked=0
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) p="${line#worktree }"; b=""; locked=0 ;;
      "branch "*) b="${line#branch refs/heads/}" ;;
      locked*) locked=1 ;;
      "")
        if [[ -n "$p" ]]; then
          p=$(cd "$p" 2>/dev/null && pwd -P || printf '%s' "$p")
          for src in "${legacy[@]}"; do
            if [[ "$p" == "$top/$src/"* ]]; then paths+=("$p"); srcs+=("$src"); branches+=("$b"); locks+=("$locked"); fi
          done
        fi
        p="" ;;
    esac
  done < <(git worktree list --porcelain; echo)

  local i n=${#paths[@]}
  for (( i = 0; i < n; i++ )); do
    p=${paths[i]}; src=${srcs[i]}; b=${branches[i]}; rel=${p#"$top/$src/"}; dest="$root/$rel"; why=""
    if [[ "$src" == .claude/worktrees && "$rel" == agent-* ]]; then why="Claude Code's own worktree"
    elif [[ "${locks[i]}" == 1 ]]; then why="locked (a running lane)"
    elif [[ -n "$(git -C "$p" status --porcelain 2>/dev/null)" ]]; then why="uncommitted changes"
    elif why=$(live_owner "$p" "$rel"); [[ -n "$why" ]]; then :
    elif [[ -n "$b" && -n "$main" && "$b" != "$main" ]] && ! landed "$top" "$b" "$main"; then why="branch $b has not landed on $main"
    elif [[ -e "$dest" ]]; then why="destination $dest exists"
    fi
    if [[ -n "$why" ]]; then echo "skip $src/$rel: $why"; continue; fi
    say "move $src/$rel -> $dest"
    planned=1
    if (( apply )); then
      mkdir -p "$(dirname "$dest")"
      if git worktree move "$p" "$dest" 2>/dev/null; then moved=$((moved + 1)); else echo "skip $src/$rel: git worktree move failed"; fi
    fi
  done

  if [[ -d .sdlc ]]; then
    local tidy
    if (( apply )); then tidy=$(python3 "$here/tickets.py" --root .sdlc tidy --apply 2>&1); else tidy=$(python3 "$here/tickets.py" --root .sdlc tidy 2>&1); fi
    [[ "$tidy" == "nothing to tidy" ]] || printf 'tickets.py tidy:\n%s\n' "$tidy"
  fi

  local d d2 reg
  for src in "${legacy[@]}"; do
    [[ -d "$src" ]] || continue
    reg=$(git worktree list --porcelain | sed -n 's/^worktree //p' | grep -F "$top/$src/")
    # A depth-1 folder that holds registered worktrees (fanout/, tmp/) is listed through its children instead.
    for d in "$src"/*/; do
      [[ -d "$d" ]] || continue
      d=$(cd "$d" && pwd -P)
      case $(relation "$d" "$reg") in
        none) echo "left in place: ${d#"$top/"} (not a registered worktree)" ;;
        holds)
          for d2 in "$d"/*/; do
            [[ -d "$d2" ]] || continue
            d2=$(cd "$d2" && pwd -P)
            [[ "${d2##*/}" == logs || $(relation "$d2" "$reg") != none ]] || echo "left in place: ${d2#"$top/"} (not a registered worktree)"
          done ;;
      esac
    done
    if (( apply )); then
      find "$src" -mindepth 1 -depth -type d -empty -delete 2>/dev/null
      if [[ "$src" == .worktrees ]]; then
        rmdir .worktrees 2>/dev/null
        [[ -d .worktrees ]] && echo "kept .worktrees/: it is not empty"
      fi
    fi
  done
  (( planned )) || echo "nothing to move"
  (( apply )) && (( moved )) && git worktree prune
  return 0
}

# phys <path>: physical path, resolving the deepest existing ancestor, so a missing path still compares.
phys() {
  local p="$1" rest="" r
  while [[ "$p" == /?* && ! -d "$p" ]]; do rest="/${p##*/}$rest"; p="${p%/*}"; done
  r=$(cd "${p:-/}" 2>/dev/null && pwd -P) || { printf '%s\n' "$1"; return 0; }
  printf '%s%s\n' "${r%/}" "$rest"
}

# relation <dir> <registered paths>: is (a registered worktree), in (inside one), holds (one inside it), or none.
relation() {
  local w
  while IFS= read -r w; do
    [[ -n "$w" ]] || continue
    w=$(cd "$w" 2>/dev/null && pwd -P || printf '%s' "$w")
    [[ "$1" == "$w" ]] && { echo is; return; }
    [[ "$1" == "$w"/* ]] && { echo in; return; }
    [[ "$w" == "$1"/* ]] && { echo holds; return; }
  done <<<"$2"
  echo none
}

# live_owner <worktree path> <rel>: prints why the tree has a live owner, else nothing.
live_owner() {
  local p=$1 rel=$2 f pid
  f=$(find "$p" -path "$p/node_modules" -prune -o -name '*.running' -print -quit 2>/dev/null)
  [[ -n "$f" ]] && { echo "live owner (${f#"$p/"})"; return; }
  if [[ -f "$p/.owner.json" ]]; then
    pid=$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' "$p/.owner.json")
    [[ -n "$pid" ]] && ps -p "$pid" >/dev/null 2>&1 && { echo "live owner (pid $pid)"; return; }
  fi
  if [[ "$rel" =~ ^tmp/[a-z]+-([0-9]+)(/|$) ]] && ps -p "${BASH_REMATCH[1]}" >/dev/null 2>&1; then
    echo "live owner (pid ${BASH_REMATCH[1]})"
  fi
}

# landed <top> <branch> <main>: exit 0 when lanes.py's landed test says ancestor, pr merged or content.
landed() {
  python3 - "$here" "$1" "$2" "$3" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import lanes
how, _ = lanes.landed(sys.argv[2], 'refs/heads/' + sys.argv[3], 'refs/heads/' + sys.argv[4], branch=sys.argv[3], pr=False)
sys.exit(0 if how in ('ancestor', 'pr merged', 'content') else 1)
PY
}

selftest() {
  local t r s fails=0 out snap1 snap2 me rc name dead
  me="$here/migrate-worktrees.sh"
  t=$(mktemp -d "${TMPDIR:-/tmp}/migrate-selftest.XXXXXX") || return 1
  t=$(cd "$t" && pwd -P)
  r="$t/repo"; s="$t/repo.worktrees"
  # shellcheck disable=SC2329,SC2317  # invoked through the trap
  cleanup() { rm -rf "$t"; }
  trap cleanup RETURN
  ok() { echo "ok: $1"; }
  bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
  g() { git -C "$r" -c user.name=t -c user.email=t@t "$@" >/dev/null 2>&1; }
  listed() { git -C "$r" worktree list --porcelain | grep -qxF "worktree $1"; }
  state() {  # worktree list, files under both legacy roots, the sibling root and .sdlc, .gitignore, status
    git -C "$r" worktree list --porcelain
    (cd "$r" && find .worktrees .claude .sdlc -print 2>/dev/null | sort)
    (cd "$t" && find repo.worktrees -print 2>/dev/null | sort)
    cat "$r/.gitignore"; git -C "$r" status --porcelain
  }
  mkdir -p "$r" && git -C "$r" init -q -b main
  printf '.worktrees/\n.claude/worktrees/\n.sdlc/runtime/\n*.running\n' >"$r/.gitignore"
  mkdir -p "$r/.sdlc" && echo x >"$r/.sdlc/stray-notes.txt" && : >"$r/.sdlc/config"
  g add -A && g commit -q -m init
  # .worktrees/ (before 0.23.0): clean, dirty, live, ahead; .claude/worktrees/ (0.23): clean, locked, ahead, agent-x,
  # a run.sh tmp prefix, and a lane whose destination already exists
  for name in clean dirty live ahead; do g worktree add -q -b "lane/$name" "$r/.worktrees/$name"; done
  for name in c-clean c-locked c-ahead agent-x taken; do g worktree add -q -b "lane/$name" "$r/.claude/worktrees/$name"; done
  dead=$(bash -c 'echo $$')
  g worktree add -q --detach "$r/.claude/worktrees/tmp/builder-$dead/w" HEAD
  g worktree lock "$r/.claude/worktrees/c-locked"
  mkdir -p "$s/taken" && echo occupied >"$s/taken/f.txt"
  echo new >"$r/.worktrees/ahead/ahead.txt" && g -C "$r/.worktrees/ahead" add ahead.txt && g -C "$r/.worktrees/ahead" commit -q -m "not landed"
  echo new >"$r/.claude/worktrees/c-ahead/c.txt" && g -C "$r/.claude/worktrees/c-ahead" add c.txt && g -C "$r/.claude/worktrees/c-ahead" commit -q -m "not landed"
  echo scratch >"$r/.worktrees/dirty/untracked.txt"
  mkdir -p "$r/.worktrees/live/.sdlc/runtime/tasks/x" && echo 1 >"$r/.worktrees/live/.sdlc/runtime/tasks/x/builder-L1.running"
  mkdir -p "$r/.worktrees/handmade" && echo keep >"$r/.worktrees/handmade/notes.txt"
  mkdir -p "$r/.claude/worktrees/host" && echo '{}' >"$r/.claude/worktrees/host/h.lane.json"

  out=$(cd "$t" && bash "$me" 2>&1); rc=$?
  [[ $rc -eq 2 && "$out" == *'not a git repository'* ]] && ok "outside a repository it refuses with exit 2" || bad "outside a repository it refuses with exit 2"
  out=$(cd "$r/.worktrees/clean" && bash "$me" 2>&1); rc=$?
  [[ $rc -eq 2 && "$out" == *'main checkout root'* ]] && ok "from a lane it refuses with exit 2 naming the main checkout root" || bad "from a lane it refuses with exit 2 naming the main checkout root"

  snap1=$(state)
  out=$(cd "$r" && bash "$me" 2>&1); rc=$?
  snap2=$(state)
  [[ $rc -eq 0 && "$snap1" == "$snap2" ]] && ok "dry run exits 0 and changes nothing" || bad "dry run exits 0 and changes nothing"
  [[ "$out" == *"would move .worktrees/clean -> $s/clean"* && "$out" == *"would move .claude/worktrees/c-clean -> $s/c-clean"* ]] \
    && ok "dry run plans a move from each legacy root to the sibling root" || bad "dry run plans a move from each legacy root to the sibling root: $out"
  [[ "$out" == *'stray-notes.txt -> archive/stray-notes.txt'* ]] && ok "dry run lists the tidy move of a loose .sdlc file" || bad "dry run lists the tidy move of a loose .sdlc file"

  out=$(cd "$r" && bash "$me" --apply 2>&1); rc=$?
  [[ $rc -eq 0 ]] && ok "apply exits 0" || bad "apply exits 0: $out"
  listed "$s/clean" && [[ ! -e "$r/.worktrees/clean" ]] \
    && ok "a clean landed .worktrees/ lane moves with git worktree move and git worktree list shows the sibling path" \
    || bad "a clean landed .worktrees/ lane moves with git worktree move and git worktree list shows the sibling path"
  listed "$s/c-clean" && [[ ! -e "$r/.claude/worktrees/c-clean" ]] \
    && ok "a clean landed .claude/worktrees/ lane moves to the sibling root" || bad "a clean landed .claude/worktrees/ lane moves to the sibling root"
  listed "$s/tmp/builder-$dead/w" && ok "a dead run.sh prefix tree moves under the sibling tmp/" || bad "a dead run.sh prefix tree moves under the sibling tmp/"
  [[ "$out" == *"skip .claude/worktrees/agent-x: Claude Code's own worktree"* ]] && listed "$r/.claude/worktrees/agent-x" \
    && ok "a Claude-owned agent-* tree is skipped and reported (negative control)" || bad "a Claude-owned agent-* tree is skipped and reported (negative control)"
  [[ "$out" == *'skip .claude/worktrees/c-locked: locked (a running lane)'* ]] && listed "$r/.claude/worktrees/c-locked" \
    && ok "a locked tree is skipped and reported (negative control)" || bad "a locked tree is skipped and reported (negative control)"
  [[ "$out" == *'skip .worktrees/dirty: uncommitted changes'* && -d "$r/.worktrees/dirty" ]] \
    && ok "a dirty tree is skipped and reported (negative control)" || bad "a dirty tree is skipped and reported (negative control)"
  [[ "$out" == *'skip .worktrees/live: live owner'* && -d "$r/.worktrees/live" ]] \
    && ok "a live tree (a .running marker) is skipped and reported (negative control)" || bad "a live tree (a .running marker) is skipped and reported (negative control)"
  [[ "$out" == *'skip .worktrees/ahead: branch lane/ahead has not landed on main'* && "$out" == *'skip .claude/worktrees/c-ahead: branch lane/c-ahead has not landed on main'* ]] \
    && ok "an unlanded lane is skipped and reported, from each legacy root (negative control)" || bad "an unlanded lane is skipped and reported, from each legacy root (negative control)"
  [[ "$out" == *"skip .claude/worktrees/taken: destination $s/taken exists"* && -f "$s/taken/f.txt" ]] && listed "$r/.claude/worktrees/taken" \
    && ok "a lane whose destination exists is skipped and the destination kept" || bad "a lane whose destination exists is skipped and the destination kept"
  [[ "$out" == *'left in place: .worktrees/handmade (not a registered worktree)'* && "$out" == *'left in place: .claude/worktrees/host (not a registered worktree)'* ]] \
    && ok "unregistered folders under each legacy root are left in place and listed" || bad "unregistered folders under each legacy root are left in place and listed"
  [[ "$out" != *'left in place: .worktrees/dirty'* && "$out" != *'left in place: .worktrees/live/'* ]] \
    && ok "a registered worktree and the folders inside one are not listed as left in place" || bad "a registered worktree and the folders inside one are not listed as left in place"
  [[ -f "$r/.sdlc/archive/stray-notes.txt" ]] && ok "tickets.py tidy moved the loose .sdlc file into archive/" || bad "tickets.py tidy moved the loose .sdlc file into archive/"
  [[ -d "$r/.worktrees" && "$out" == *'kept .worktrees/'* && -d "$r/.claude/worktrees" ]] \
    && ok "the legacy roots are kept while they are not empty" || bad "the legacy roots are kept while they are not empty"

  snap1=$(state)
  out=$(cd "$r" && bash "$me" --apply 2>&1); rc=$?
  snap2=$(state)
  [[ $rc -eq 0 && "$snap1" == "$snap2" && "$out" != *'move '* && "$out" == *'nothing to move' ]] \
    && ok "a second apply moves nothing, changes nothing and says nothing to move (idempotent)" || bad "a second apply moves nothing, changes nothing and says nothing to move (idempotent): $out"

  rm "$r/.worktrees/dirty/untracked.txt" "$r/.worktrees/live/.sdlc/runtime/tasks/x/builder-L1.running"
  rm -r "$r/.worktrees/handmade" "$r/.claude/worktrees/host" "$s/taken"
  g worktree unlock "$r/.claude/worktrees/c-locked"
  g add -A && g commit -q -m tidy  # the tidy move, so the non-fast-forward merge below has a clean index
  g merge -q --no-edit lane/ahead; g merge -q --no-edit lane/c-ahead
  out=$(cd "$r" && bash "$me" --apply 2>&1); rc=$?
  [[ $rc -eq 0 && ! -e "$r/.worktrees" && $(git -C "$r" worktree list --porcelain | grep -c "^worktree $s/") -eq 9 ]] \
    && ok "with the blockers gone every SDLC tree moves and the empty .worktrees/ is removed" || bad "with the blockers gone every SDLC tree moves and the empty .worktrees/ is removed: $out"
  [[ -d "$r/.claude/worktrees" ]] && listed "$r/.claude/worktrees/agent-x" && [[ ! -e "$r/.claude/worktrees/tmp" ]] \
    && ok ".claude/worktrees/ keeps Claude's agent-x tree and loses its emptied tmp/" || bad ".claude/worktrees/ keeps Claude's agent-x tree and loses its emptied tmp/"
  out=$(cd "$r" && bash "$me" 2>&1)
  [[ "$out" == "skip .claude/worktrees/agent-x: Claude Code's own worktree"$'\n''nothing to move' ]] \
    && ok "a dry run of a migrated repo says nothing to move: $(tr '\n' '|' <<<"$out")" || bad "a dry run of a migrated repo says nothing to move: $out"
  out=$(cd "$r" && bash "$here/migrate-0.23.sh" 2>&1)
  [[ "$out" == *'nothing to move' ]] && ok "migrate-0.23.sh runs this script" || bad "migrate-0.23.sh runs this script: $out"

  # T-0561: a bare clone with a lane beside it reports the root and exits 0, from the lane and from the bare dir
  git clone -q --bare "$r" "$t/kit/.bare" && git -C "$t/kit/.bare" worktree add -q --detach "$t/kit/lanes/a" HEAD >/dev/null 2>&1
  snap1=$(git -C "$t/kit/.bare" worktree list --porcelain; find "$t/kit" -maxdepth 3 | sort)
  out=$(cd "$t/kit/lanes/a" && bash "$me" 2>&1); rc=$?
  [[ $rc -eq 0 && "$out" == *"bare clone: worktree root $t/kit/lanes"* && "$out" == *'nothing to move'* ]] \
    && ok "bare clone: from a lane it prints the root and nothing to move, exit 0" || bad "bare clone: from a lane it prints the root and nothing to move, exit 0: rc $rc $out"
  out=$(cd "$t/kit/.bare" && bash "$me" --apply 2>&1); rc=$?
  snap2=$(git -C "$t/kit/.bare" worktree list --porcelain; find "$t/kit" -maxdepth 3 | sort)
  [[ $rc -eq 0 && "$out" == *"bare clone: worktree root $t/kit/lanes"* && "$snap1" == "$snap2" ]] \
    && ok "bare clone: from the bare dir --apply prints the root and changes nothing" || bad "bare clone: from the bare dir --apply prints the root and changes nothing: rc $rc $out"
  if (( fails )); then echo "migrate-worktrees.sh selftest: FAIL ($fails)"; return 1; fi
  echo "migrate-worktrees.sh selftest: ok"
}

case "${1:-}" in
  --selftest) selftest ;;
  ""|--apply) migrate "${1:-}" ;;
  *) echo "usage: migrate-worktrees.sh [--apply | --selftest]" >&2; exit 2 ;;
esac
