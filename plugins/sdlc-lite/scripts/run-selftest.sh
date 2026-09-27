#!/usr/bin/env bash
# Selftest for run.sh result numbering: three runs of the same role and level must keep every
# result. The first run writes <role>-<level>.md, later runs write <role>-<level>-2.md, -3.md, ...
# Each runs.jsonl line must name its result in a "file" field, in run order.
# Also checks the verifier model swap, and .nvmrc resolution against a fake NVM_DIR (exact,
# partial with numeric highest pick, whole-component matching, alias, missing, no .nvmrc), plus one
# real run proving the role run sees the matched node bin dir first on PATH, and the result
# check (exit 3 when a result lacks its role's required section; STUB_RESULT picks the result).
# Throwaway worktrees: with a stub that adds a worktree under $SDLC_TMP_WORKTREES, a successful run,
# a failing run (stub exits 1), and a run whose result lacks its section (exit 3) each leave only the
# main tree in `git worktree list` and no .worktrees/tmp, and the stub saw a non-empty
# SDLC_TMP_WORKTREES under <toplevel>/.worktrees/tmp/. A dry run creates no .worktrees, and a dry run
# of a role that declares skills leaves no mktemp skill file behind.
# Stray report: a stub that makes a worktree outside the prefix (detached and on a branch) and a
# branch from inside its own script gets one "stray worktree appeared during this run" line per
# worktree (" [<branch>]" only for the branched one) and one "stray branch appeared during this run"
# line per branch on stderr, and matching stray_worktrees and stray_branches arrays in runs.jsonl; a
# failing run (exit 1) that leaves strays still reports them and still exits 1; a run that creates
# nothing, or only a worktree under $SDLC_TMP_WORKTREES (also every worktree run above), prints no
# stray line and records empty arrays. The dry-run .nvmrc checks compare stderr exactly, so a dry run
# prints no stray line. Strays the cases make are removed inside the temp repo.
# Uses a stub `claude` on PATH (no model call) inside a throwaway git repo.
# Prints "run selftest: PASS" or "run selftest: FAIL: <reason>" and exits non-zero on failure.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() { echo "run selftest: FAIL: $*"; exit 1; }

# Stub claude: ignores its args, prints a run.sh-shaped JSON result numbered by a counter file.
mkdir -p "$tmp/bin"
cat >"$tmp/bin/claude" <<EOF
#!/usr/bin/env bash
n=\$(( \$(cat "$tmp/count" 2>/dev/null || echo 0) + 1 ))
echo "\$n" >"$tmp/count"
echo "\${PATH%%:*}" >"$tmp/pathhead"
if [[ -n "\${STUB_RESULT:-}" ]]; then cat "\$STUB_RESULT"; exit 0; fi
printf '{"is_error":false,"result":"## Goal\\\\nrun %s","total_cost_usd":0,"duration_ms":1,"num_turns":1}\n' "\$n"
EOF
chmod +x "$tmp/bin/claude"

repo="$tmp/repo"
mkdir -p "$repo/.sdlc/t"
echo '## Goal' >"$repo/.sdlc/t/handoff.md"
git -C "$repo" init -q
git -C "$repo" add -A
git -C "$repo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init

dir="$(cd "$repo/.sdlc/t" && pwd)"
names=(planner-L3 planner-L3-2 planner-L3-3)
outs=()
for i in 1 2 3; do
  out=$(cd "$repo" && PATH="$tmp/bin:$PATH" "$here/run.sh" planner L3 .sdlc/t/handoff.md) \
    || fail "run $i: run.sh exited non-zero"
  outs+=("$out")
done

# File contents first, so an overwrite is reported as such.
for i in 1 2 3; do
  name="${names[$((i - 1))]}"
  [[ -f "$dir/$name.md" ]] || fail "$name.md is missing"
  grep -qx "run $i" "$dir/$name.md" \
    || fail "$name.md does not hold 'run $i', it was overwritten: $(tr '\n' ' ' <"$dir/$name.md")"
  [[ -f "$dir/$name.log" ]] || fail "$name.log is missing"
done
for i in 1 2 3; do
  want="$dir/${names[$((i - 1))]}.md"
  [[ "${outs[$((i - 1))]}" == "$want" ]] || fail "run $i: run.sh printed '${outs[$((i - 1))]}', want '$want'"
done
lines=$(wc -l <"$dir/runs.jsonl" | tr -d ' ')
[[ "$lines" == 3 ]] || fail "runs.jsonl has $lines lines, want 3"
files=$(jq -r '.file // "MISSING"' "$dir/runs.jsonl" | tr '\n' ' ')
[[ "$files" == "planner-L3.md planner-L3-2.md planner-L3-3.md " ]] \
  || fail "runs.jsonl file fields are '$files', want 'planner-L3.md planner-L3-2.md planner-L3-3.md'"
leftover=$(find "$dir" -name '*.running')
[[ -z "$leftover" ]] || fail "a .running file is left over: $leftover"

# Verifier model swap reads the newest build from runs.jsonl order, not file times (dry run).
sw="$repo/.sdlc/t/step-1"
mkdir -p "$sw"
echo '## Goal' >"$sw/handoff.md"
echo '<!-- role=builder level=L5 model=fable effort=xhigh -->' >"$sw/builder-L5.md"
echo '<!-- role=builder level=L1 model=sonnet effort=low -->' >"$sw/builder-L1.md"
touch -t 202601010000 "$sw/builder-L5.md" "$sw/builder-L1.md"
dry() { (cd "$repo" && SDLC_DRY_RUN=1 PATH="$tmp/bin:$PATH" "$here/run.sh" verifier "$1" .sdlc/t/step-1/handoff.md); }
printf '%s\n' '{"role":"builder","level":"L1","file":"builder-L1.md"}' \
  '{"role":"builder","level":"L5","file":"builder-L5.md"}' >"$sw/runs.jsonl"
out=$(dry L2) || fail "dry run verifier L2 exited non-zero"
[[ "$out" == *"--model sonnet --effort high"* ]] \
  || fail "L5 newest: verifier L2 should stay '--model sonnet --effort high', got: $out"
printf '%s\n' '{"role":"builder","level":"L5","file":"builder-L5.md"}' \
  '{"role":"builder","level":"L1","file":"builder-L1.md"}' >"$sw/runs.jsonl"
out=$(dry L1) || fail "dry run verifier L1 exited non-zero"
[[ "$out" == *"--model opus --effort medium"* ]] \
  || fail "L1 newest: verifier L1 should swap sonnet to '--model opus --effort medium', got: $out"
out=$(dry L2) || fail "dry run verifier L2 exited non-zero"
[[ "$out" == *"--model opus --effort high"* ]] \
  || fail "L1 newest: verifier L2 should swap sonnet to '--model opus --effort high', got: $out"
# A dry run of a role that declares skills removes its mktemp skill file (T-0108).
out=$(dry L1) || fail "dry run verifier L1 exited non-zero"
sf=$(awk '{for (i = 1; i < NF; i++) if ($i == "--append-system-prompt-file") print $(i + 1)}' <<<"$out")
[[ -n "$sf" ]] || fail "dry run verifier L1 printed no --append-system-prompt-file: $out"
[[ ! -e "$sf" ]] || fail "dry run left its skill file behind: $sf"

# .nvmrc resolution against a fake NVM_DIR: dry runs assert the one stderr line, then one real
# run checks that the stub claude sees the matched bin dir first on PATH.
nvm="$tmp/nvm"
node="$nvm/versions/node"
for v in v18.19.1 v20.9.0 v20.11.0 v200.1.0; do mkdir -p "$node/$v/bin"; done
nrepo="$tmp/nrepo"
mkdir -p "$nrepo"
echo '## Goal' >"$nrepo/h.md"
git -C "$nrepo" init -q
git -C "$nrepo" add -A
git -C "$nrepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
# nvmrc_err <.nvmrc content | ""> [NVM_DIR]: stderr of a dry run ("" means no .nvmrc).
nvmrc_err() {
  if [[ -n "$1" ]]; then printf '%s\n' "$1" >"$nrepo/.nvmrc"; else rm -f "$nrepo/.nvmrc"; fi
  (cd "$nrepo" && { NVM_DIR="${2:-$nvm}" SDLC_DRY_RUN=1 PATH="$tmp/bin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null; } 2>&1)
}
want_err() { # want_err <.nvmrc> <expected stderr> [NVM_DIR]
  local got
  got=$(nvmrc_err "$1" "${3:-}") || fail ".nvmrc '$1': dry run exited non-zero: $got"
  [[ "$got" == "$2" ]] || fail ".nvmrc '$1': stderr is '$got', want '$2'"
}
pre() { echo "run.sh: .nvmrc $1: prepended $node/$2/bin to PATH"; }
nf() { echo "run.sh: .nvmrc $1: not found under ${2:-$node}, PATH unchanged"; }
want_err v20.11.0 "$(pre v20.11.0 v20.11.0)"
want_err 20.9.0 "$(pre 20.9.0 v20.9.0)"
want_err 20 "$(pre 20 v20.11.0)"
want_err v20 "$(pre v20 v20.11.0)"
want_err v20.9 "$(pre v20.9 v20.9.0)"
want_err 18 "$(pre 18 v18.19.1)"
want_err v20.1 "$(nf v20.1)"
want_err v2 "$(nf v2)"
want_err v22.1.0 "$(nf v22.1.0)"
want_err v20.11 "$(pre v20.11 v20.11.0)"
want_err 'lts/*' "run.sh: .nvmrc lts/*: alias not resolved, PATH unchanged"
want_err node "run.sh: .nvmrc node: alias not resolved, PATH unchanged"
want_err 20 "$(nf 20 "$tmp/no-nvm/versions/node")" "$tmp/no-nvm"
want_err "" ""
printf '  v20.11.0 \n\n' >"$nrepo/.nvmrc"
got=$(cd "$nrepo" && { NVM_DIR="$nvm" SDLC_DRY_RUN=1 "$here/run.sh" builder L1 h.md >/dev/null; } 2>&1) \
  || fail ".nvmrc with whitespace: dry run exited non-zero: $got"
[[ "$got" == "$(pre v20.11.0 v20.11.0)" ]] || fail ".nvmrc with whitespace: stderr is '$got'"

# Result check: a result lacking the role's required section exits 3 and keeps its files.
res() { jq -n --arg r "$1" '{is_error:false,result:$r,total_cost_usd:0,duration_ms:1,num_turns:1}' >"$tmp/res.json"; }
rrepo="$tmp/rrepo"
mkdir -p "$rrepo"
echo x >"$rrepo/h.md"
git -C "$rrepo" init -q
git -C "$rrepo" add -A
git -C "$rrepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
# want_rc <rc> <role> <level> <result text>: runs run.sh with that result, checks the exit code.
want_rc() {
  res "$4"; rm -f "$rrepo"/*-L*.md "$rrepo"/*.log "$rrepo/runs.jsonl"
  local rc=0
  (cd "$rrepo" && STUB_RESULT="$tmp/res.json" PATH="$tmp/bin:$PATH" "$here/run.sh" "$2" "$3" h.md \
    >/dev/null 2>"$tmp/rerr") || rc=$?
  [[ "$rc" == "$1" ]] || fail "$2 result '$4': exit $rc, want $1 ($(cat "$tmp/rerr"))"
}
want_rc 3 builder L2 $'## Changes\nNone'
grep -q '## Status' "$tmp/rerr" || fail "builder no Status: stderr does not name ## Status: $(cat "$tmp/rerr")"
[[ -f "$rrepo/builder-L2.md" ]] || fail "builder no Status: result file not kept"
grep -q '"file":"builder-L2.md"' "$rrepo/runs.jsonl" || fail "builder no Status: runs.jsonl line not kept"
want_rc 3 builder L2 $'## Status\nmaybe'
want_rc 0 builder L2 $'## Status\ninherited red: test_a'
want_rc 3 builder L2 $'## Status\ninherited red'
want_rc 3 verifier L1 $'## Verdict\nmaybe'
grep -q '## Verdict' "$tmp/rerr" || fail "verifier maybe: stderr does not name ## Verdict"
want_rc 3 planner L1 $'## Steps\nx'
grep -q '## Goal' "$tmp/rerr" || fail "planner no Goal: stderr does not name ## Goal"
want_rc 0 builder L2 $'## Status\n\nDone \n\n## Changes\nNone'
want_rc 0 verifier L1 $'## Verdict\npass'
want_rc 0 verifier L1 $'## Verdict\ninherited red: test_a'
want_rc 3 verifier L1 $'## Verdict\ninherited red'

# Real run: the stub claude records the first PATH entry it sees.
printf '20\n' >"$nrepo/.nvmrc"
res $'## Status\ndone'
(cd "$nrepo" && STUB_RESULT="$tmp/res.json" NVM_DIR="$nvm" PATH="$tmp/bin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null 2>&1) \
  || fail ".nvmrc real run: run.sh exited non-zero"
head_seen=$(cat "$tmp/pathhead" 2>/dev/null || echo MISSING)
[[ "$head_seen" == "$node/v20.11.0/bin" ]] \
  || fail ".nvmrc real run: claude saw PATH head '$head_seen', want '$node/v20.11.0/bin'"

# Throwaway worktrees: a second stub records SDLC_TMP_WORKTREES and adds a worktree under it
# (under .worktrees/tmp/unset when it is unset), then succeeds, fails, or returns a result
# lacking its section (STUB_MODE ok|fail|nosect). Every case must leave only the main tree.
mkdir -p "$tmp/wbin"
cat >"$tmp/wbin/claude" <<EOF
#!/usr/bin/env bash
printf '%s\n' "\${SDLC_TMP_WORKTREES:-}" >"$tmp/wtenv"
git worktree add -q --detach "\${SDLC_TMP_WORKTREES:-\$PWD/.worktrees/tmp/unset}/w" HEAD >/dev/null 2>&1 \\
  || { echo "stub: git worktree add failed" >&2; exit 9; }
case "\${STUB_MODE:-ok}" in
  fail) exit 1 ;;
  nosect) jq -n '{is_error:false,result:"## Changes\\nNone",total_cost_usd:0,duration_ms:1,num_turns:1}' ;;
  *) jq -n '{is_error:false,result:"## Status\\ndone",total_cost_usd:0,duration_ms:1,num_turns:1}' ;;
esac
EOF
chmod +x "$tmp/wbin/claude"
wrepo="$tmp/wrepo"
mkdir -p "$wrepo"
echo x >"$wrepo/h.md"
git -C "$wrepo" init -q
git -C "$wrepo" add -A
git -C "$wrepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
wtop=$(git -C "$wrepo" rev-parse --show-toplevel)
(cd "$wrepo" && SDLC_DRY_RUN=1 PATH="$tmp/wbin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null 2>&1) \
  || fail "worktree dry run: run.sh exited non-zero"
[[ ! -e "$wrepo/.worktrees" ]] || fail "worktree dry run: created $wrepo/.worktrees"
# want_wt <mode> <rc>: one real run with that stub mode, then the worktree assertions.
want_wt() {
  local rc=0 env_seen wts
  rm -f "$tmp/wtenv" "$wrepo"/*-L*.md "$wrepo"/*.log "$wrepo/runs.jsonl"
  (cd "$wrepo" && STUB_MODE="$1" PATH="$tmp/wbin:$PATH" "$here/run.sh" builder L1 h.md \
    >/dev/null 2>"$tmp/werr") || rc=$?
  [[ "$rc" == "$2" ]] || fail "worktree $1 run: exit $rc, want $2 ($(cat "$tmp/werr"))"
  wts=$(git -C "$wrepo" worktree list)
  [[ "$(printf '%s\n' "$wts" | wc -l | tr -d ' ')" == 1 ]] \
    || fail "worktree $1 run: leftover worktree: $(printf '%s\n' "$wts" | sed 1d | tr '\n' ' ')"
  [[ ! -e "$wrepo/.worktrees/tmp" ]] || fail "worktree $1 run: $wrepo/.worktrees/tmp is left over"
  env_seen=$(cat "$tmp/wtenv" 2>/dev/null || true)
  [[ -n "$env_seen" ]] || fail "worktree $1 run: claude saw no SDLC_TMP_WORKTREES (missing or empty)"
  [[ "$env_seen" == "$wtop/.worktrees/tmp/"?* ]] \
    || fail "worktree $1 run: SDLC_TMP_WORKTREES is '$env_seen', want it under $wtop/.worktrees/tmp/"
  ! grep -q stray "$tmp/werr" || fail "worktree $1 run: printed a stray line: $(cat "$tmp/werr")"
}
want_wt ok 0
want_wt fail 1
want_wt nosect 3

# Stray report: a third stub makes worktrees and a branch from inside its own script (STUB_MODE
# stray|strayfail|prefix|none), outside the Bash tool text the hooks see.
mkdir -p "$tmp/sbin"
cat >"$tmp/sbin/claude" <<'EOF'
#!/usr/bin/env bash
case "${STUB_MODE:-none}" in
  stray|strayfail)
    { git worktree add -q --detach "$SDLC_TMP_WORKTREES/w" HEAD
      git worktree add -q --detach "$PWD-stray-det" HEAD
      git worktree add -q -b stray-wt-br "$PWD-stray-br" HEAD
      git branch stray-br; } >/dev/null 2>&1 || { echo "stub: stray setup failed" >&2; exit 9; } ;;
  prefix) git worktree add -q --detach "$SDLC_TMP_WORKTREES/w" HEAD >/dev/null 2>&1 \
    || { echo "stub: git worktree add failed" >&2; exit 9; } ;;
esac
[[ "${STUB_MODE:-}" == strayfail ]] && exit 1
jq -n '{is_error:false,result:"## Status\ndone",total_cost_usd:0,duration_ms:1,num_turns:1}'
EOF
chmod +x "$tmp/sbin/claude"
srepo="$tmp/srepo"
mkdir -p "$srepo"
echo x >"$srepo/h.md"
git -C "$srepo" init -q
git -C "$srepo" add -A
git -C "$srepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
# stray_run <mode> <rc>: one real run with that stub mode; stderr lands in $tmp/serr.
stray_run() {
  local rc=0
  rm -f "$srepo"/*-L*.md "$srepo"/*.log "$srepo/runs.jsonl"
  (cd "$srepo" && STUB_MODE="$1" PATH="$tmp/sbin:$PATH" "$here/run.sh" builder L1 h.md \
    >/dev/null 2>"$tmp/serr") || rc=$?
  [[ "$rc" == "$2" ]] || fail "stray $1 run: exit $rc, want $2 ($(cat "$tmp/serr"))"
}
# stray_clean: removes the strays a stray run made (inside the temp repo only).
stray_clean() {
  git -C "$srepo" worktree remove --force "$srepo-stray-det" >/dev/null 2>&1 || true
  git -C "$srepo" worktree remove --force "$srepo-stray-br" >/dev/null 2>&1 || true
  git -C "$srepo" branch -D stray-br stray-wt-br >/dev/null 2>&1 || true
  [[ "$(git -C "$srepo" worktree list | wc -l | tr -d ' ')" == 1 ]] || fail "stray cleanup left a worktree"
}
# want_strays <label>: the stderr lines for the two worktrees and two branches the stub made.
want_strays() {
  local n
  n=$(grep -c '^run.sh: stray worktree appeared during this run: ' "$tmp/serr" || true)
  [[ "$n" == 2 ]] || fail "$1: $n stray worktree lines, want 2: $(cat "$tmp/serr")"
  grep -qx 'run.sh: stray worktree appeared during this run: .*/srepo-stray-det' "$tmp/serr" \
    || fail "$1: no detached stray worktree line (without a branch): $(cat "$tmp/serr")"
  grep -qx 'run.sh: stray worktree appeared during this run: .*/srepo-stray-br \[stray-wt-br\]' "$tmp/serr" \
    || fail "$1: no branched stray worktree line with ' [stray-wt-br]': $(cat "$tmp/serr")"
  n=$(grep -c '^run.sh: stray branch appeared during this run: ' "$tmp/serr" || true)
  [[ "$n" == 2 ]] || fail "$1: $n stray branch lines, want 2: $(cat "$tmp/serr")"
  grep -qx 'run.sh: stray branch appeared during this run: stray-br' "$tmp/serr" \
    || fail "$1: no stray branch line for stray-br: $(cat "$tmp/serr")"
  grep -qx 'run.sh: stray branch appeared during this run: stray-wt-br' "$tmp/serr" \
    || fail "$1: no stray branch line for stray-wt-br: $(cat "$tmp/serr")"
  ! grep -q '/.worktrees/tmp/' "$tmp/serr" || fail "$1: reported a worktree under the prefix: $(cat "$tmp/serr")"
}
stray_run stray 0
want_strays "stray ok run"
jq -e '(.stray_branches | sort) == ["stray-br", "stray-wt-br"]
  and (.stray_worktrees | length == 2)
  and (.stray_worktrees | map(test("/srepo-stray-(det|br)$")) | all)' "$srepo/runs.jsonl" >/dev/null \
  || fail "stray ok run: runs.jsonl stray fields wrong: $(cat "$srepo/runs.jsonl")"
stray_clean
stray_run strayfail 1
want_strays "stray failing run"
stray_clean
for m in none prefix; do
  stray_run "$m" 0
  ! grep -q stray "$tmp/serr" || fail "stray $m run: printed a stray line: $(cat "$tmp/serr")"
  jq -e '.stray_worktrees == [] and .stray_branches == []' "$srepo/runs.jsonl" >/dev/null \
    || fail "stray $m run: runs.jsonl stray fields not empty arrays: $(cat "$srepo/runs.jsonl")"
done

echo "run selftest: PASS"
