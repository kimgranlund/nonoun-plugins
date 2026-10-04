#!/usr/bin/env bash
# Live run for T-0202: does a planner given a scout result with a "## Carry forward" section
# read it, cite its path, and skip the scout's search, compared with a planner given no scout
# result? Run from the repository root.
#
# Full run: builds the fixture in a new temp dir, runs the three arms (one trial each), and
# writes scout.txt, with.txt, and without.txt next to this script:
#   bash docs/validation/carry-forward-live-run/probe.sh
# Evidence only: runs no role and builds nothing; recomputes the three arms' evidence from the
# logs and results already in <project dir>/with and <project dir>/without, and writes
# scout.txt, with.txt, and without.txt to <out dir>:
#   bash docs/validation/carry-forward-live-run/probe.sh --evidence-only <project dir> <out dir>
set -uo pipefail

R=$(git rev-parse --show-toplevel)
RUN=$R/plugins/sdlc-lite/scripts/run.sh
OUT=$R/docs/validation/carry-forward-live-run

EVIDENCE_ONLY=no
if (( $# > 0 )); then
  if [[ $1 == --evidence-only && $# -eq 3 ]]; then
    EVIDENCE_ONLY=yes
    P=$2
    OUT=$3
    mkdir -p "$OUT" || exit 1
  else
    echo "usage: probe.sh [--evidence-only <project dir> <out dir>]" >&2
    exit 2
  fi
fi

if [[ $EVIDENCE_ONLY == no ]]; then
  P=$(mktemp -d -t carry-forward-probe)
  echo "project dir: $P (kept after the run)"
fi

make_project() {
  local d=$1
  mkdir -p "$d" && cd "$d" || exit 1
  git init -q
  mkdir -p bin lib/text lib/table lib/io tests
  cat >README.md <<'EOF'
Tiny table printer.
EOF
  cat >bin/table.sh <<'EOF'
#!/usr/bin/env bash
. "$(dirname "$0")/../lib/table/render.sh"
render_row "$@"
EOF
  cat >lib/text/pad.sh <<'EOF'
# pad_cell <text> <width>: left-align text in a cell of width characters
pad_cell() { printf '%-*s' "$2" "$1"; }
EOF
  cat >lib/text/trim.sh <<'EOF'
trim() { printf '%s' "$1" | sed 's/^ *//; s/ *$//'; }
EOF
  cat >lib/table/render.sh <<'EOF'
. "$(dirname "${BASH_SOURCE[0]}")/../text/pad.sh"
render_row() { local out='' c; for c in "$@"; do out+="|$(pad_cell "$c" 8)"; done; printf '%s|\n' "$out"; }
EOF
  cat >lib/table/header.sh <<'EOF'
header_rule() { printf '+%s+\n' '--------'; }
EOF
  cat >lib/io/csv.sh <<'EOF'
split_csv() { local IFS=,; printf '%s\n' $1; }
EOF
  cat >tests/pad_test.sh <<'EOF'
. "$(dirname "$0")/../lib/text/pad.sh"
test "$(pad_cell ab 4)" = "ab  " && echo ok
EOF
  printf '.sdlc/\n.worktrees/\n' >.gitignore
  git add -A
  git -c user.name=probe -c user.email=probe@example.invalid commit -qm init
  mkdir -p .sdlc/cf
  cat >.sdlc/cf/handoff.md <<'EOF'
# Task: fill character for cell padding

## Goal
`pad_cell` takes an optional third argument, a fill character (default a space), and pads with it, so `pad_cell ab 4 .` prints `ab..`. Every existing caller keeps its output.

## Constraints
- Bash only.
- `bash tests/pad_test.sh` still prints `ok`.
EOF
}

# Run one role with no session or run state inherited from the caller.
role_run() {
  local proj=$1 role=$2 level=$3
  (
    unset CLAUDECODE
    for v in $(compgen -e | grep '^CLAUDE_CODE_'); do unset "$v"; done
    unset SDLC_ROLE SDLC_BASE_SHA SDLC_TMP_WORKTREES SDLC_HEADLESS SDLC_ATTEMPT_ID \
      SDLC_ATTEMPT_NAME SDLC_LIFECYCLE_CHILD SDLC_ROUTING_REASON SDLC_BACKEND
    cd "$proj" || exit 1
    bash "$RUN" "$role" "$level" .sdlc/cf/handoff.md
  )
  local rc=$?
  echo "run $role $level in $proj: exit $rc"
}

# Body lines of the "## Carry forward" section of a file (heading excluded), up to the next heading.
cf_body() {
  awk '/^#+ / { if (in_cf) exit; if ($0 == "## Carry forward") { in_cf = 1; next } } in_cf' "$1" 2>/dev/null
}

# One line per tool call, in log order, with the full compact JSON input.
tool_lines() {
  jq -R -r 'fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")
    | "tool=\(.name) input=\(.input | tojson | sub("\\s+$"; ""))"' "$1" 2>/dev/null
}

# Search lines, read from the log in log order. A Grep or Glob call counts whole. A Bash call's
# full .input.command (never .input.description) is split into command-list elements on newline,
# ;, &&, and ||, a pipeline staying whole, and each trimmed element matching the ERE counts.
search_lines() {
  jq -R -r 'fromjson? // empty | select(.type=="assistant") | .message.content[]? | select(.type=="tool_use")
    | if .name=="Grep" or .name=="Glob" then "search=\(.name) \(.input|tojson)"
      elif .name=="Bash" then ((.input.command // "") | [splits("\n|;|&&|\\|\\|")] | .[]
        | sub("^\\s+"; "") | sub("\\s+$"; "")
        | select(test("git grep|grep -[A-Za-z]*[rR]|rg |find ")) | "search=Bash \(tojson)")
      else empty end' "$1" 2>/dev/null
}

evidence() {
  local arm=$1 proj=$2 name=$3 out=$OUT/$1.txt
  local log=$proj/.sdlc/cf/$name.log res=$proj/.sdlc/cf/$name.md
  local tl sl
  tl=$(mktemp)
  sl=$(mktemp)
  tool_lines "$log" >"$tl"
  search_lines "$log" >"$sl"
  {
    echo "arm=$arm"
    echo "project=$proj"
    echo "plugin=$R/plugins/sdlc-lite"
    echo "result=$res"
    echo "header=$(head -n 1 "$res" 2>/dev/null)"
    echo "model=$(jq -R -r 'fromjson? // empty | .message.model? // empty' "$log" 2>/dev/null | awk 'NF && !seen[$0]++' | paste -sd, -)"
    cat "$tl"
    cat "$sl"
    echo "tool_calls=$(grep -c '^tool=' "$tl")"
    echo "tree_searches=$(grep -c '^search=' "$sl")"
    echo "symbol_searches=$(grep '^search=' "$sl" | grep -c 'pad_cell')"
    if [[ $arm == scout ]]; then
      if grep -qx '## Carry forward' "$res" 2>/dev/null; then echo "carry_forward_section=yes"; else echo "carry_forward_section=no"; fi
      echo "carry_forward_lines=$(cf_body "$res" | grep -c '[^[:space:]]')"
    else
      if grep -qF 'scout-L1.md' "$tl"; then echo "read_scout_result=yes"; else echo "read_scout_result=no"; fi
      if grep -qF 'scout-L1.md' "$res" 2>/dev/null; then echo "cites_result_path=yes"; else echo "cites_result_path=no"; fi
      local copies=no line
      grep -qx '## Carry forward' "$res" 2>/dev/null && copies=yes
      while IFS= read -r line; do
        line=$(printf '%s' "$line" | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//; s/^- //')
        (( ${#line} >= 20 )) || continue
        grep -qF -- "$line" "$res" 2>/dev/null && copies=yes
      done < <(cf_body "$P/with/.sdlc/cf/scout-L1.md")
      echo "copies_section=$copies"
    fi
  } >"$out"
  rm -f "$tl" "$sl"
  echo "wrote $out"
}

if [[ $EVIDENCE_ONLY == no ]]; then
  (make_project "$P/with")
  (make_project "$P/without")

  role_run "$P/with" scout L1
  role_run "$P/with" planner L2
  role_run "$P/without" planner L2
fi

evidence scout "$P/with" scout-L1
evidence with "$P/with" planner-L2
evidence without "$P/without" planner-L2
exit 0
