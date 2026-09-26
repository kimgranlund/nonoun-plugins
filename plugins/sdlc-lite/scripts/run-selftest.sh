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
}
want_wt ok 0
want_wt fail 1
want_wt nosect 3

echo "run selftest: PASS"
