#!/usr/bin/env bash
# Selftest for run.sh result numbering: three runs of the same role and level must keep every
# result. The first run writes <role>-<level>.md, later runs write <role>-<level>-2.md, -3.md, ...
# Each runs.jsonl line must name its result in a "file" field, in run order.
# Also checks the verifier model swap, and .nvmrc resolution against a fake NVM_DIR (exact,
# partial with numeric highest pick, whole-component matching, alias, missing, no .nvmrc), plus one
# real run proving the role run sees the matched node bin dir first on PATH, and the result
# check (exit 3 when a result lacks its role's required section; STUB_RESULT picks the result).
# Result pick: stubs emit stream-json lines ("type":"result" events, plus a non-JSON stderr line that
# must be skipped). A log holding a "## Verdict" result and then a trailing task-notification result
# ("stale monitor") saves the Verdict and exits 0; when neither holds the heading, the
# non-notification one is saved and run.sh exits 3. runs.jsonl takes cost from the last event.
# Throwaway worktrees: with a stub that adds a worktree under $SDLC_TMP_WORKTREES, a successful run,
# a failing run (stub exits 1), and a run whose result lacks its section (exit 3) each leave only the
# main tree in `git worktree list` and no .worktrees/tmp, and the stub saw a non-empty
# SDLC_TMP_WORKTREES under <toplevel>/.worktrees/tmp/. A dry run creates no .worktrees, and a dry run
# of a role that declares skills leaves no mktemp skill file behind.
# Bash timeouts: the stub records BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS; unset or an
# inherited 120000 must reach it as 3600000, an inherited 7200000 as 7200000 (T-0105).
# Build base: a stub records ${SDLC_BASE_SHA:-unset}. The first builder run writes base-sha equal
# to HEAD and the stub sees it; after a plain commit a verifier still sees the old base; after a
# git merge --no-ff of a side branch the next run sees the merge commit and base-sha is rewritten
# to it; a base-sha holding junk or a commit that is not an ancestor is replaced by HEAD; a planner
# run sees unset and writes no base-sha even with SDLC_BASE_SHA exported by the caller; a builder
# dry run writes no base-sha.
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
echo "\${BASH_DEFAULT_TIMEOUT_MS:-unset} \${BASH_MAX_TIMEOUT_MS:-unset}" >"$tmp/timeouts"
echo "stub: stderr noise, not JSON" >&2
if [[ -n "\${STUB_RESULT:-}" ]]; then cat "\$STUB_RESULT"; exit 0; fi
printf '{"type":"result","is_error":false,"result":"## Goal\\\\nrun %s","total_cost_usd":0,"duration_ms":1,"num_turns":1}\n' "\$n"
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
res() { jq -nc --arg r "$1" '{type:"result",is_error:false,result:$r,total_cost_usd:0,duration_ms:1,num_turns:1}' >"$tmp/res.json"; }
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

# Result pick: a trailing task-notification result must not replace the report. The stub output
# holds a system event and a non-JSON line (from the stub's stderr), then two result events.
# res2 <first result> <cost>: writes that log shape, the second result a task notification (cost 3).
res2() {
  { echo '{"type":"system","subtype":"init"}'
    jq -nc --arg r "$1" --argjson c "$2" '{type:"result",is_error:false,result:$r,total_cost_usd:$c,duration_ms:1,num_turns:1}'
    echo 'not json: stderr line'
    jq -nc '{type:"result",is_error:false,result:"stale monitor, no action needed",origin:{kind:"task-notification"},total_cost_usd:3,duration_ms:9,num_turns:4}'
  } >"$tmp/res.json"
}
# pick_rc <rc> <role> <level>: runs run.sh on the current res.json, checks the exit code.
pick_rc() {
  rm -f "$rrepo"/*-L*.md "$rrepo"/*.log "$rrepo/runs.jsonl"
  local rc=0
  (cd "$rrepo" && STUB_RESULT="$tmp/res.json" PATH="$tmp/bin:$PATH" "$here/run.sh" "$2" "$3" h.md \
    >/dev/null 2>"$tmp/rerr") || rc=$?
  [[ "$rc" == "$1" ]] || fail "result pick $2 $3: exit $rc, want $1 ($(cat "$tmp/rerr"))"
}
res2 $'## Verdict\npass' 1
pick_rc 0 verifier L1
grep -qx '## Verdict' "$rrepo/verifier-L1.md" || fail "result pick: verifier-L1.md lacks ## Verdict: $(tr '\n' ' ' <"$rrepo/verifier-L1.md")"
! grep -q 'stale monitor' "$rrepo/verifier-L1.md" || fail "result pick: verifier-L1.md holds the task-notification result"
grep -q 'stderr noise' "$rrepo/verifier-L1.log" || fail "result pick: the log holds no non-JSON stderr line"
cost=$(jq -r '.cost_usd' "$rrepo/runs.jsonl")
[[ "$cost" == 3 ]] || fail "result pick: runs.jsonl cost_usd is '$cost', want 3 (the last result event)"
res2 'working on it' 1
pick_rc 3 verifier L1
grep -q 'working on it' "$rrepo/verifier-L1.md" || fail "no heading: the non-notification result was not saved"
! grep -q 'stale monitor' "$rrepo/verifier-L1.md" || fail "no heading: verifier-L1.md holds the task-notification result"
# heading rule: two results, neither a task notification; the earlier one holds the heading, the
# later one does not. Only the heading rule saves the earlier one (the fallback picks the last).
{ jq -nc '{type:"result",is_error:false,result:"## Verdict\npass",total_cost_usd:1,duration_ms:1,num_turns:1}'
  jq -nc '{type:"result",is_error:false,result:"done, see above",total_cost_usd:2,duration_ms:1,num_turns:2}'
} >"$tmp/res.json"
pick_rc 0 verifier L1
grep -qx '## Verdict' "$rrepo/verifier-L1.md" || fail "heading rule: verifier-L1.md lacks ## Verdict: $(tr '\n' ' ' <"$rrepo/verifier-L1.md")"
! grep -q 'done, see above' "$rrepo/verifier-L1.md" || fail "heading rule: verifier-L1.md holds the later headingless result"

# Real run: the stub claude records the first PATH entry it sees.
printf '20\n' >"$nrepo/.nvmrc"
res $'## Status\ndone'
(cd "$nrepo" && STUB_RESULT="$tmp/res.json" NVM_DIR="$nvm" PATH="$tmp/bin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null 2>&1) \
  || fail ".nvmrc real run: run.sh exited non-zero"
head_seen=$(cat "$tmp/pathhead" 2>/dev/null || echo MISSING)
[[ "$head_seen" == "$node/v20.11.0/bin" ]] \
  || fail ".nvmrc real run: claude saw PATH head '$head_seen', want '$node/v20.11.0/bin'"

# Bash timeouts: the stub claude records both values it sees.
want_to() { # want_to <inherited value or ""> <expected>
  rm -f "$tmp/timeouts" "$nrepo"/*-L*.md "$nrepo"/*.log
  if [[ -n "$1" ]]; then
    (cd "$nrepo" && STUB_RESULT="$tmp/res.json" BASH_DEFAULT_TIMEOUT_MS="$1" BASH_MAX_TIMEOUT_MS="$1" \
      PATH="$tmp/bin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null 2>&1) || fail "timeouts '$1': run.sh exited non-zero"
  else
    (cd "$nrepo" && unset BASH_DEFAULT_TIMEOUT_MS BASH_MAX_TIMEOUT_MS && STUB_RESULT="$tmp/res.json" \
      PATH="$tmp/bin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null 2>&1) || fail "timeouts unset: run.sh exited non-zero"
  fi
  local seen; seen=$(cat "$tmp/timeouts" 2>/dev/null || echo MISSING)
  [[ "$seen" == "$2 $2" ]] || fail "timeouts '${1:-unset}': claude saw '$seen', want '$2 $2'"
}
want_to "" 3600000
want_to 120000 3600000
want_to 7200000 7200000

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
  nosect) jq -nc '{type:"result",is_error:false,result:"## Changes\\nNone",total_cost_usd:0,duration_ms:1,num_turns:1}' ;;
  *) jq -nc '{type:"result",is_error:false,result:"## Status\\ndone",total_cost_usd:0,duration_ms:1,num_turns:1}' ;;
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

# Build base: a third stub records ${SDLC_BASE_SHA:-unset}. Builder and verifier runs resolve and
# store <step dir>/base-sha; other roles see unset and write none; a dry run writes none.
mkdir -p "$tmp/bbin"
cat >"$tmp/bbin/claude" <<EOF
#!/usr/bin/env bash
echo "\${SDLC_BASE_SHA:-unset}" >"$tmp/baseseen"
jq -nc '{type:"result",is_error:false,result:"## Status\\ndone\\n## Verdict\\npass\\n## Goal\\nx",total_cost_usd:0,duration_ms:1,num_turns:1}'
EOF
chmod +x "$tmp/bbin/claude"
brepo="$tmp/brepo"
mkdir -p "$brepo/s"
echo '## Goal' >"$brepo/s/handoff.md"
bg() { git -C "$brepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false "$@"; }
bg init -q
bg add -A
bg commit -q -m init
b0=$(bg rev-parse HEAD)
# brun <role>: one real run in brepo; stub output lands in $tmp/baseseen.
brun() {
  rm -f "$tmp/baseseen"
  (cd "$brepo" && PATH="$tmp/bbin:$PATH" "$here/run.sh" "$1" L1 s/handoff.md >/dev/null 2>"$tmp/berr") \
    || fail "base $1 run: run.sh exited non-zero ($(cat "$tmp/berr"))"
  cat "$tmp/baseseen" 2>/dev/null || echo MISSING
}
bfile() { head -1 "$brepo/s/base-sha" 2>/dev/null || echo MISSING; }
(cd "$brepo" && SDLC_DRY_RUN=1 PATH="$tmp/bbin:$PATH" "$here/run.sh" builder L1 s/handoff.md >/dev/null 2>&1) \
  || fail "base dry run: run.sh exited non-zero"
[[ ! -e "$brepo/s/base-sha" ]] || fail "base dry run: builder dry run wrote base-sha"
seen=$(SDLC_BASE_SHA=leak brun planner)
[[ "$seen" == unset ]] || fail "base planner: SDLC_BASE_SHA is '$seen', want unset (caller exported 'leak')"
[[ ! -e "$brepo/s/base-sha" ]] || fail "base planner: planner run wrote base-sha"
seen=$(brun builder)
[[ "$seen" == "$b0" ]] || fail "base first builder: SDLC_BASE_SHA is '$seen', want HEAD $b0"
[[ "$(bfile)" == "$b0" ]] || fail "base first builder: base-sha is '$(bfile)', want HEAD $b0"
echo w >"$brepo/w.txt"
bg add w.txt
bg commit -q -m work
seen=$(brun verifier)
[[ "$seen" == "$b0" ]] || fail "base after plain commit: SDLC_BASE_SHA is '$seen', want old base $b0"
[[ "$(bfile)" == "$b0" ]] || fail "base after plain commit: base-sha is '$(bfile)', want $b0"
bg branch -q side "$b0"
bg checkout -q side
bg commit -q --allow-empty -m main
bg checkout -q -
bg merge -q --no-ff -m sync side
bm=$(bg rev-parse HEAD)
seen=$(brun verifier)
[[ "$seen" == "$bm" ]] || fail "base after resync merge: SDLC_BASE_SHA is '$seen', want merge $bm"
[[ "$(bfile)" == "$bm" ]] || fail "base after resync merge: base-sha is '$(bfile)', want $bm"
echo junk >"$brepo/s/base-sha"
seen=$(brun builder)
head_now=$(bg rev-parse HEAD)
[[ "$seen" == "$head_now" ]] || fail "base junk: SDLC_BASE_SHA is '$seen', want HEAD $head_now"
[[ "$(bfile)" == "$head_now" ]] || fail "base junk: base-sha is '$(bfile)', want HEAD $head_now"
bg branch -q other "$b0"
bg checkout -q other
bg commit -q --allow-empty -m other
na=$(bg rev-parse HEAD)
bg checkout -q -
bg merge-base --is-ancestor "$na" HEAD && fail "base non-ancestor: fixture commit $na is an ancestor of HEAD"
echo "$na" >"$brepo/s/base-sha"
seen=$(brun verifier)
[[ "$seen" == "$head_now" ]] || fail "base non-ancestor: SDLC_BASE_SHA is '$seen', want HEAD $head_now"
[[ "$(bfile)" == "$head_now" ]] || fail "base non-ancestor: base-sha is '$(bfile)', want HEAD $head_now"

echo "run selftest: PASS"
