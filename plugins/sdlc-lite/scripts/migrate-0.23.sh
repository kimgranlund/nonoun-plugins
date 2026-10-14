#!/usr/bin/env bash
# Usage: migrate-0.23.sh [--apply]   run once per consumer repo, from its main checkout root, when installing 0.23.0
#        migrate-0.23.sh --selftest  prove it on a throwaway fixture repo
# T-0550: SDLC Lite 0.23.0 puts every worktree under <main checkout>/.claude/worktrees/ (Claude Code's own default);
# before it, lanes and role trees lived under .worktrees/. A dry run (the default) prints each planned step and
# changes nothing; --apply acts. Idempotent: a second run finds nothing to move and changes nothing.
#   1. .claude/worktrees/ must be gitignored: `would add .claude/worktrees/ to .gitignore`, appended with --apply.
#   2. Each registered worktree under .worktrees/ moves to the same relative path under .claude/worktrees/ with
#      git worktree move (never mv): `move .worktrees/<rel> -> .claude/worktrees/<rel>`. It is skipped and reported
#      (`skip .worktrees/<rel>: <why>`) when it is locked (a running lane), has uncommitted changes (git status
#      --porcelain), has a live owner (a *.running marker under it, a .owner.json whose pid runs, or a run.sh prefix
#      tmp/<role>-<pid> whose pid runs), is a lane whose branch has not landed on the main branch (lanes.py landed:
#      ancestor or every changed file equal), or its destination exists.
#   3. tickets.py --root .sdlc tidy (T-0544) lists, or with --apply moves, loose .sdlc/ entries into .sdlc/archive/.
#   4. Unregistered folders under .worktrees/ stay where they are and are listed (`left in place: <path>`).
#   5. With --apply, empty folders under .worktrees/ go and .worktrees/ itself is removed only when it ends empty.
# Read paths keep accepting .worktrees/ for one release, so a skipped lane still lands; rerun after it lands.
# Exit 0 when the run finished (skips included), 2 on a usage error or when not run from the main checkout root.
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

migrate() {
  local apply=0 top cwd main common line p b locked rel dest why moved=0 planned=0
  [[ "${1:-}" == --apply ]] && apply=1
  top=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "migrate-0.23.sh: not a git repository" >&2; return 2; }
  cwd=$(pwd -P)
  common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
  if [[ "$(cd "$top" && pwd -P)" != "$cwd" || "${common##*/}" != .git || "$(cd "${common%/.git}" && pwd -P)" != "$cwd" ]]; then
    echo "migrate-0.23.sh: run it from the main checkout root (the folder holding .git), not $cwd" >&2
    return 2
  fi
  top=$cwd
  say() { if (( apply )); then echo "$1"; else echo "would $1"; fi; }

  if ! git check-ignore -q .claude/worktrees/x 2>/dev/null; then
    say "add .claude/worktrees/ to .gitignore"
    planned=1
    if (( apply )); then
      [[ ! -s .gitignore || "$(tail -c1 .gitignore)" == "" ]] || echo >>.gitignore
      echo ".claude/worktrees/" >>.gitignore
    fi
  fi

  main=$(git worktree list --porcelain | sed -n '1,/^$/s/^branch refs\/heads\///p' | head -n1)
  local -a paths=() branches=() locks=()
  p="" b="" locked=0
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) p="${line#worktree }"; b=""; locked=0 ;;
      "branch "*) b="${line#branch refs/heads/}" ;;
      locked*) locked=1 ;;
      "")
        if [[ -n "$p" ]]; then
          p=$(cd "$p" 2>/dev/null && pwd -P || printf '%s' "$p")
          if [[ "$p" == "$top/.worktrees/"* ]]; then paths+=("$p"); branches+=("$b"); locks+=("$locked"); fi
        fi
        p="" ;;
    esac
  done < <(git worktree list --porcelain; echo)

  local i n=${#paths[@]}
  for (( i = 0; i < n; i++ )); do
    p=${paths[i]}; b=${branches[i]}; rel=${p#"$top/.worktrees/"}; dest="$top/.claude/worktrees/$rel"; why=""
    if [[ "${locks[i]}" == 1 ]]; then why="locked (a running lane)"
    elif [[ -n "$(git -C "$p" status --porcelain 2>/dev/null)" ]]; then why="uncommitted changes"
    elif why=$(live_owner "$p" "$rel"); [[ -n "$why" ]]; then :
    elif [[ -n "$b" && -n "$main" && "$b" != "$main" ]] && ! landed "$top" "$b" "$main"; then why="branch $b has not landed on $main"
    elif [[ -e "$dest" ]]; then why="destination .claude/worktrees/$rel exists"
    fi
    if [[ -n "$why" ]]; then echo "skip .worktrees/$rel: $why"; continue; fi
    say "move .worktrees/$rel -> .claude/worktrees/$rel"
    planned=1
    if (( apply )); then
      mkdir -p "$(dirname "$dest")"
      if git worktree move "$p" "$dest" 2>/dev/null; then moved=$((moved + 1)); else echo "skip .worktrees/$rel: git worktree move failed"; fi
    fi
  done

  if [[ -d .sdlc ]]; then
    local tidy
    if (( apply )); then tidy=$(python3 "$here/tickets.py" --root .sdlc tidy --apply 2>&1); else tidy=$(python3 "$here/tickets.py" --root .sdlc tidy 2>&1); fi
    [[ "$tidy" == "nothing to tidy" ]] || { printf 'tickets.py tidy:\n%s\n' "$tidy"; planned=1; }
  fi

  if [[ -d .worktrees ]]; then
    local d d2 reg
    reg=$(git worktree list --porcelain | sed -n 's/^worktree //p' | grep -F "$top/.worktrees/")
    # A depth-1 folder that holds registered worktrees (fanout/, tmp/) is listed through its children instead.
    for d in .worktrees/*/; do
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
      find .worktrees -depth -type d -empty -delete 2>/dev/null
      [[ -d .worktrees ]] && echo "kept .worktrees/: it is not empty"
    elif [[ -z "$(find .worktrees -type f -print -quit 2>/dev/null)" ]] && (( n == 0 )); then
      echo "would remove the empty .worktrees/"
    fi
  fi
  (( planned )) || echo "nothing to migrate"
  (( apply )) && (( moved )) && git worktree prune
  return 0
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
  local t r fails=0 out snap1 snap2 me rc
  me="$here/migrate-0.23.sh"
  t=$(mktemp -d "${TMPDIR:-/tmp}/migrate-selftest.XXXXXX") || return 1
  t=$(cd "$t" && pwd -P)
  r="$t/repo"
  # shellcheck disable=SC2329,SC2317  # invoked through the trap
  cleanup() { rm -rf "$t"; }
  trap cleanup RETURN
  ok() { echo "ok: $1"; }
  bad() { echo "FAIL: $1"; fails=$((fails + 1)); }
  g() { git -C "$r" -c user.name=t -c user.email=t@t "$@" >/dev/null 2>&1; }
  state() {  # worktree list, files under .worktrees and .claude, .gitignore and .sdlc, status
    git -C "$r" worktree list --porcelain
    (cd "$r" && find .worktrees .claude .sdlc -print 2>/dev/null | sort)
    cat "$r/.gitignore"; git -C "$r" status --porcelain
  }
  mkdir -p "$r" && git -C "$r" init -q -b main
  printf '.worktrees/\n.sdlc/runtime/\n*.running\n' >"$r/.gitignore"
  mkdir -p "$r/.sdlc" && echo x >"$r/.sdlc/stray-notes.txt" && : >"$r/.sdlc/config"
  g add -A && g commit -q -m init
  for name in clean dirty live ahead; do g worktree add -q -b "lane/$name" "$r/.worktrees/$name"; done
  echo new >"$r/.worktrees/ahead/ahead.txt" && g -C "$r/.worktrees/ahead" add ahead.txt && g -C "$r/.worktrees/ahead" commit -q -m "not landed"
  echo scratch >"$r/.worktrees/dirty/untracked.txt"
  mkdir -p "$r/.worktrees/live/.sdlc/runtime/tasks/x" && echo 1 >"$r/.worktrees/live/.sdlc/runtime/tasks/x/builder-L1.running"
  mkdir -p "$r/.worktrees/handmade" && echo keep >"$r/.worktrees/handmade/notes.txt"

  out=$(cd "$t" && bash "$me" 2>&1); rc=$?
  [[ $rc -eq 2 && "$out" == *'not a git repository'* ]] && ok "outside a repository it refuses with exit 2" || bad "outside a repository it refuses with exit 2"
  out=$(cd "$r/.worktrees/clean" && bash "$me" 2>&1); rc=$?
  [[ $rc -eq 2 && "$out" == *'main checkout root'* ]] && ok "from a lane it refuses with exit 2 naming the main checkout root" || bad "from a lane it refuses with exit 2 naming the main checkout root"

  snap1=$(state)
  out=$(cd "$r" && bash "$me" 2>&1); rc=$?
  snap2=$(state)
  [[ $rc -eq 0 && "$snap1" == "$snap2" ]] && ok "dry run exits 0 and changes nothing" || bad "dry run exits 0 and changes nothing"
  [[ "$out" == *'would move .worktrees/clean -> .claude/worktrees/clean'* && "$out" == *'would add .claude/worktrees/ to .gitignore'* ]] \
    && ok "dry run plans the clean move and the .gitignore line" || bad "dry run plans the clean move and the .gitignore line"
  [[ "$out" == *'stray-notes.txt -> archive/stray-notes.txt'* ]] && ok "dry run lists the tidy move of a loose .sdlc file" || bad "dry run lists the tidy move of a loose .sdlc file"

  out=$(cd "$r" && bash "$me" --apply 2>&1); rc=$?
  [[ $rc -eq 0 ]] && ok "apply exits 0" || bad "apply exits 0"
  git -C "$r" worktree list --porcelain | grep -qxF "worktree $r/.claude/worktrees/clean" && [[ ! -e "$r/.worktrees/clean" ]] \
    && ok "a clean landed worktree moves with git worktree move and git worktree list shows the new path" || bad "a clean landed worktree moves with git worktree move and git worktree list shows the new path"
  [[ "$out" == *'skip .worktrees/dirty: uncommitted changes'* && -d "$r/.worktrees/dirty" ]] \
    && ok "a dirty worktree is skipped and reported (negative control)" || bad "a dirty worktree is skipped and reported (negative control)"
  [[ "$out" == *'skip .worktrees/live: live owner'* && -d "$r/.worktrees/live" ]] \
    && ok "a live worktree (a .running marker) is skipped and reported (negative control)" || bad "a live worktree (a .running marker) is skipped and reported (negative control)"
  [[ "$out" == *'skip .worktrees/ahead: branch lane/ahead has not landed on main'* && -d "$r/.worktrees/ahead" ]] \
    && ok "a lane not landed is skipped and reported (negative control)" || bad "a lane not landed is skipped and reported (negative control)"
  [[ "$out" == *'left in place: .worktrees/handmade (not a registered worktree)'* && -f "$r/.worktrees/handmade/notes.txt" ]] \
    && ok "an unregistered folder is left in place and listed" || bad "an unregistered folder is left in place and listed"
  [[ "$out" != *'left in place: .worktrees/dirty'* && "$out" != *'left in place: .worktrees/live/'* ]] \
    && ok "a registered worktree and the folders inside one are not listed as left in place" || bad "a registered worktree and the folders inside one are not listed as left in place"
  git -C "$r" check-ignore -q .claude/worktrees/x && ok ".claude/worktrees/ is now gitignored" || bad ".claude/worktrees/ is now gitignored"
  [[ -f "$r/.sdlc/archive/stray-notes.txt" ]] && ok "tickets.py tidy moved the loose .sdlc file into archive/" || bad "tickets.py tidy moved the loose .sdlc file into archive/"
  [[ -d "$r/.worktrees" && "$out" == *'kept .worktrees/'* ]] && ok ".worktrees/ is kept while it is not empty" || bad ".worktrees/ is kept while it is not empty"

  snap1=$(state)
  out=$(cd "$r" && bash "$me" --apply 2>&1); rc=$?
  snap2=$(state)
  [[ $rc -eq 0 && "$snap1" == "$snap2" && "$out" != *'move .worktrees/'* ]] && ok "a second apply changes nothing (idempotent)" || bad "a second apply changes nothing (idempotent)"

  rm "$r/.worktrees/dirty/untracked.txt" "$r/.worktrees/live/.sdlc/runtime/tasks/x/builder-L1.running"
  rm -r "$r/.worktrees/handmade"
  g merge -q --no-edit lane/ahead
  out=$(cd "$r" && bash "$me" --apply 2>&1); rc=$?
  [[ $rc -eq 0 && ! -e "$r/.worktrees" && $(git -C "$r" worktree list --porcelain | grep -c "^worktree $r/.claude/worktrees/") -eq 4 ]] \
    && ok "with the blockers gone every worktree moves and the empty .worktrees/ is removed" || bad "with the blockers gone every worktree moves and the empty .worktrees/ is removed"
  out=$(cd "$r" && bash "$me" 2>&1)
  [[ "$out" == 'nothing to migrate' ]] && ok "a dry run of a migrated repo says nothing to migrate: $out" || bad "a dry run of a migrated repo says nothing to migrate: $out"
  if (( fails )); then echo "migrate-0.23.sh selftest: FAIL ($fails)"; return 1; fi
  echo "migrate-0.23.sh selftest: ok"
}

case "${1:-}" in
  --selftest) selftest ;;
  ""|--apply) migrate "${1:-}" ;;
  *) echo "usage: migrate-0.23.sh [--apply | --selftest]" >&2; exit 2 ;;
esac
