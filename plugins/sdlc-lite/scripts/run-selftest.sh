#!/usr/bin/env bash
# Selftest for run.sh result numbering: three runs of the same role and level must keep every
# result. The first run writes <role>-<level>.md, later runs write <role>-<level>-2.md, -3.md, ...
# Each runs.jsonl line must name its result in a "file" field, in run order.
# Also checks the verifier model swap, the plan-reviewer family rule (dry run: newest planner opus ->
# --model fable --effort high; newest planner fable, planner sonnet, or no planner -> --model opus
# --effort high), and .nvmrc resolution against a fake NVM_DIR (exact,
# partial with numeric highest pick, whole-component matching, alias, missing, no .nvmrc), plus one
# real run proving the role run sees the matched node bin dir first on PATH, and the result
# check (exit 3 when a result lacks its role's required section; STUB_RESULT picks the result; a
# plan-reviewer ## Verdict of pass, replan, or blocked exits 0, maybe or no ## Verdict exits 3).
# Result pick: stubs emit stream-json lines ("type":"result" events, plus a non-JSON stderr line that
# must be skipped). A log holding a "## Verdict" result and then a trailing task-notification result
# ("stale monitor") saves the Verdict and exits 0; when neither holds the heading, the
# non-notification one is saved and run.sh exits 3. runs.jsonl takes cost from the last event.
# Task dir: dry runs of run.sh verifier <level> .sdlc/td/handoff.md, a task dir holding no builder
# result, read the newest build of the highest-numbered live step-<n>/ under it: a sonnet step-1
# build moves verifier L1 and L2 to opus (medium, high); a fable build moves verifier L3 to opus
# xhigh; step-<n>.superseded-<k>/ dirs are ignored either way; step-10 outranks step-2 (numeric
# order); inside one step runs.jsonl order picks the build; a builder result in the task dir itself
# wins over its step dirs; no build anywhere keeps sonnet medium (L1) and fable xhigh (L3); and a
# verifier at a live step-3/ with no build ignores a sonnet step-1/. Its failures read
# "task dir: <reason>".
# Throwaway worktrees: with a stub that adds a worktree under $SDLC_TMP_WORKTREES, a successful run,
# a failing run (stub exits 1), and a run whose result lacks its section (exit 3) each leave only the
# main tree in `git worktree list` and no .worktrees/tmp, and the stub saw a non-empty
# SDLC_TMP_WORKTREES under <toplevel>/.worktrees/tmp/. A dry run creates no .worktrees, and a dry run
# of a role that declares skills leaves no mktemp skill file behind.
# Stale prefix: before a real run, detached worktrees are registered under .worktrees/tmp/builder-<pid
# of an exited subshell>/w and .worktrees/tmp/builder-<pid of this selftest>/w; after the run the dead
# owner's prefix is gone from disk and from git worktree list, and the live owner's worktree is still
# on disk and listed (then removed by the case). Its failures read "stale prefix: <reason>".
# Term cleanup: a stub claude adds a worktree under $SDLC_TMP_WORKTREES, ignores TERM (trap ''), writes
# a ready marker holding its pid, and execs sleep 30 (which inherits the ignore). run.sh runs in the
# background; once the marker appears, the run.sh pid (the run_lifecycle.py process) gets TERM and
# must exit 143 with no worktree under .worktrees/tmp registered, no .worktrees/tmp, and the stub no
# longer alive. Its failures read "term cleanup: <reason>". Both cases drive run.sh only.
# Bash timeouts: the stub records BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS; unset or an
# inherited 120000 must reach it as 3600000, an inherited 7200000 as 7200000 (T-0105).
# Build base: a stub records ${SDLC_BASE_SHA:-unset}. The first builder run writes base-sha equal
# to HEAD and the stub sees it; after a plain commit a verifier still sees the old base; after a
# git merge --no-ff of a side branch the next run sees the merge commit and base-sha is rewritten
# to it; a base-sha holding junk or a commit that is not an ancestor is replaced by HEAD; a planner
# run sees unset and writes no base-sha even with SDLC_BASE_SHA exported by the caller; a builder
# dry run writes no base-sha.
# Stray report: a stub that makes a worktree outside the prefix (detached and on a branch) and a
# branch from inside its own script gets one "stray worktree appeared during this run" line per
# worktree (" [<branch>]" only for the branched one) and one "stray branch appeared during this run"
# line per branch on stderr, and matching stray_worktrees and stray_branches arrays in runs.jsonl; a
# failing run (exit 1) that leaves strays still reports them and still exits 1; a run that creates
# nothing, or only a worktree under $SDLC_TMP_WORKTREES (also every worktree run above), prints no
# stray line and records empty arrays. The dry-run .nvmrc checks compare stderr exactly, so a dry run
# prints no stray line. Strays the cases make are removed inside the temp repo.
# Temporary worktree recipe: a source repo with a tracked file and a .gitignore holding .sdlc/ is
# cloned with git clone --bare to proj.git, which gets a primary worktree on the default branch and
# an unrelated user worktree on its own branch. The primary is made dirty (a modified tracked file,
# an untracked file) and holds the task handoff .sdlc/t/handoff.md. The run-operations recipe then
# runs: a mktemp path, a detached worktree added from the bare repo, run.sh scout L1 <absolute
# handoff> from inside it, and a worktree remove without --force. run.sh exits 0 from the temporary
# worktree (the stub records its cwd); scout-L1.md and runs.jsonl land beside the handoff in the
# primary's .sdlc/t and no result file appears under the temporary worktree; after removal its path
# is gone from git worktree list and from disk, the user worktree is still listed, refs/heads is
# unchanged, the primary's porcelain status and tracked-file bytes are byte-identical to the
# snapshot, and the primary has no .worktrees dir.
# Self-edit: a copy of the plugin runs a real planner run whose stub claude truncates the copy's
# scripts/run.sh in place (same inode) before printing its result; the run must still exit 0, print
# the result path, save the stub's text, write its runs.jsonl line, and mark the attempt completed.
# The real run.sh is never touched. Its failures read "run selftest: FAIL: self-edit: <reason>".
# Mailbox notice: in a fresh repo a planner dry run with no mailbox prints no stderr and creates no
# .sdlc; after one message to planner the dry run's stderr is exactly "run.sh: 1 new message(s) for
# planner; read with messages.py"; after one more to claude it says 2, and a builder dry run says 1;
# a real planner run prints the line exactly once and no message body. Its failures read "notice: <reason>".
# Spec gate: a plan-reviewer dry run on a plan whose (guard) runs check.sh with no "guard timeout:"
# line exits 2 and prints "slow guard"; a real run on it exits 2, the stub is never called, and no
# runs.jsonl or *.running exists; the same plan with a "guard timeout:" line dry-runs to exit 0; with
# SDLC_SPECGATE=off a real run exits 0 and its runs.jsonl line has "specgate":"off". The no-planner
# and header-only plan-reviewer cases above keep exit 0. Its failures read "spec gate: <reason>".
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
pwd -P >"$tmp/cwd"
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

# Task dir: a verifier whose handoff dir holds no builder result reads the newest build of the
# highest-numbered live step-<n>/ under it (dry run). Fixtures live under .sdlc/td.
td="$repo/.sdlc/td"
tdreset() { rm -rf "$td"; mkdir -p "$td"; echo '## Goal' >"$td/handoff.md"; }
tdbuild() { mkdir -p "$td/$1"; echo "<!-- role=builder level=$2 model=$3 effort=x -->" >"$td/$1/builder-$2.md"; }
tddry() { (cd "$repo" && SDLC_DRY_RUN=1 PATH="$tmp/bin:$PATH" "$here/run.sh" verifier "$1" "${2:-.sdlc/td/handoff.md}") \
  || fail "task dir: dry run verifier $1 exited non-zero"; }
tdwant() { [[ "$3" == *"--agent sdlc-lite:verifier --model $2"* ]] || fail "task dir: $1: want '--model $2', got: $3"; }
# 1. No build in the task dir; step-1 holds a sonnet build.
tdreset; tdbuild step-1 L1 sonnet
tdwant "sonnet step build, verifier L1" "opus --effort medium" "$(tddry L1)"
tdwant "sonnet step build, verifier L2" "opus --effort high" "$(tddry L2)"
# 2. Newest live build is fable.
tdreset; tdbuild step-1 L5 fable
tdwant "fable step build, verifier L3" "opus --effort xhigh" "$(tddry L3)"
# 3. Superseded step dirs are ignored.
tdreset; tdbuild step-1 L1 sonnet; mkdir -p "$td/step-2"; echo '## Step 2' >"$td/step-2/handoff.md"
tdbuild step-2.superseded-1 L3 opus
tdwant "superseded opus ignored" "opus --effort medium" "$(tddry L1)"
tdreset; tdbuild step-1 L3 opus; tdbuild step-2.superseded-1 L1 sonnet
tdwant "superseded sonnet ignored" "sonnet --effort medium" "$(tddry L1)"
# 4. Step order is numeric, not lexical.
tdreset; tdbuild step-2 L3 opus; tdbuild step-10 L1 sonnet
tdwant "step-10 sonnet beats step-2 opus" "opus" "$(tddry L1)"
tdreset; tdbuild step-2 L1 sonnet; tdbuild step-10 L3 opus
tdwant "step-10 opus beats step-2 sonnet" "sonnet" "$(tddry L1)"
# 5. Within one step the newest build comes from order.py (runs.jsonl order).
tdreset; tdbuild step-1 L5 fable; tdbuild step-1 L1 sonnet
touch -t 202601010000 "$td/step-1/builder-L5.md" "$td/step-1/builder-L1.md"
printf '%s\n' '{"role":"builder","level":"L5","file":"builder-L5.md"}' \
  '{"role":"builder","level":"L1","file":"builder-L1.md"}' >"$td/step-1/runs.jsonl"
tdwant "runs.jsonl newest sonnet" "opus" "$(tddry L1)"
# 6. The handoff dir's own build wins over its step dirs.
tdreset; echo '<!-- role=builder level=L3 model=opus effort=high -->' >"$td/builder-L3.md"; tdbuild step-1 L1 sonnet
tdwant "task dir opus build wins" "sonnet --effort medium" "$(tddry L1)"
# 7. No builder result anywhere.
tdreset; mkdir -p "$td/step-1"; echo '## Step 1' >"$td/step-1/handoff.md"
tdwant "no build, verifier L1" "sonnet --effort medium" "$(tddry L1)"
tdwant "no build, verifier L3" "fable --effort xhigh" "$(tddry L3)"
# 8. A live step with no build reads only under itself, not its siblings.
tdreset; tdbuild step-1 L1 sonnet; mkdir -p "$td/step-3"; echo '## Step 3' >"$td/step-3/handoff.md"
tdwant "step-3 verifier ignores step-1" "sonnet --effort medium" "$(tddry L1 .sdlc/td/step-3/handoff.md)"
rm -rf "$td"

# Plan-reviewer family rule reads the newest planner result by runs.jsonl order (dry run).
pr="$repo/.sdlc/t/review"
mkdir -p "$pr"
echo '## Goal' >"$pr/handoff.md"
prdry() { (cd "$repo" && SDLC_DRY_RUN=1 PATH="$tmp/bin:$PATH" "$here/run.sh" plan-reviewer L1 .sdlc/t/review/handoff.md); }
out=$(prdry) || fail "dry run plan-reviewer L1 (no planner) exited non-zero"
[[ "$out" == *"--agent sdlc-lite:plan-reviewer --model opus --effort high"* ]] \
  || fail "no planner: plan-reviewer should stay '--model opus --effort high', got: $out"
[[ "$out" == *"--disallowedTools Edit Write NotebookEdit"* ]] \
  || fail "plan-reviewer is not read-only, got: $out"
echo '<!-- role=planner level=L1 model=sonnet effort=medium -->' >"$pr/planner-L1.md"
echo '{"role":"planner","level":"L1","file":"planner-L1.md"}' >"$pr/runs.jsonl"
out=$(prdry) || fail "dry run plan-reviewer L1 (sonnet planner) exited non-zero"
[[ "$out" == *"--model opus --effort high"* ]] \
  || fail "sonnet planner: plan-reviewer should stay '--model opus --effort high', got: $out"
echo '<!-- role=planner level=L2 model=opus effort=medium -->' >"$pr/planner-L2.md"
echo '<!-- role=planner level=L3 model=fable effort=xhigh -->' >"$pr/planner-L3.md"
touch -t 202601010000 "$pr/planner-L2.md" "$pr/planner-L3.md"
printf '%s\n' '{"role":"planner","level":"L3","file":"planner-L3.md"}' \
  '{"role":"planner","level":"L2","file":"planner-L2.md"}' >"$pr/runs.jsonl"
out=$(prdry) || fail "dry run plan-reviewer L1 (opus planner) exited non-zero"
[[ "$out" == *"--model fable --effort high"* ]] \
  || fail "opus planner newest: plan-reviewer should swap to '--model fable --effort high', got: $out"
printf '%s\n' '{"role":"planner","level":"L2","file":"planner-L2.md"}' \
  '{"role":"planner","level":"L3","file":"planner-L3.md"}' >"$pr/runs.jsonl"
out=$(prdry) || fail "dry run plan-reviewer L1 (fable planner) exited non-zero"
[[ "$out" == *"--model opus --effort high"* ]] \
  || fail "fable planner newest: plan-reviewer should stay '--model opus --effort high', got: $out"
# Planner L3 runs on Opus xhigh, so a review after an Opus L3 plan moves to Fable high.
out=$(cd "$repo" && SDLC_DRY_RUN=1 PATH="$tmp/bin:$PATH" "$here/run.sh" planner L3 .sdlc/t/review/handoff.md) \
  || fail "dry run planner L3 exited non-zero"
[[ "$out" == *"--model opus --effort xhigh"* ]] \
  || fail "planner L3 should run '--model opus --effort xhigh', got: $out"
echo '<!-- role=planner level=L3 model=opus effort=xhigh -->' >"$pr/planner-L3.md"
printf '%s\n' '{"role":"planner","level":"L2","file":"planner-L2.md"}' \
  '{"role":"planner","level":"L3","file":"planner-L3.md"}' >"$pr/runs.jsonl"
out=$(prdry) || fail "dry run plan-reviewer L1 (opus L3 planner) exited non-zero"
[[ "$out" == *"--model fable --effort high"* ]] \
  || fail "opus L3 planner newest: plan-reviewer should swap to '--model fable --effort high', got: $out"

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

# Independent fixture resets remove attempt records as well as reports/logs.
# Retry preservation and interrupted attempts are exercised by lifecycle-selftest.py.
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
  res "$4"; rm -f "$rrepo"/*-L*.md "$rrepo"/*.log "$rrepo"/*.attempt.json "$rrepo/runs.jsonl"
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
want_rc 0 plan-reviewer L1 $'## Verdict\npass'
want_rc 0 plan-reviewer L1 $'## Verdict\nreplan\n\n## Findings\n- step 1: scope: x. Evidence: a:1'
want_rc 0 plan-reviewer L1 $'## Verdict\nblocked'
want_rc 3 plan-reviewer L1 $'## Verdict\nmaybe'
grep -q '## Verdict' "$tmp/rerr" || fail "plan-reviewer maybe: stderr does not name ## Verdict"
want_rc 3 plan-reviewer L1 $'## Findings\nNone'
want_rc 3 verifier L1 $'## Criteria\n1. ok\n\n## Verdict\npass'
grep -q 'comes before' "$tmp/rerr" || fail "verifier Criteria before Verdict: stderr does not name the order: $(cat "$tmp/rerr")"

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
  rm -f "$rrepo"/*-L*.md "$rrepo"/*.log "$rrepo"/*.attempt.json "$rrepo/runs.jsonl"
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
  rm -f "$tmp/timeouts" "$nrepo"/*-L*.md "$nrepo"/*.log "$nrepo"/*.attempt.json
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
  rm -f "$tmp/wtenv" "$wrepo"/*-L*.md "$wrepo"/*.log "$wrepo"/*.attempt.json "$wrepo/runs.jsonl"
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

# Stale prefix: a prefix whose owner pid is dead is reaped by the next real run; a live owner's stays.
dead=$(bash -c 'echo $$')
! ps -p "$dead" >/dev/null 2>&1 || fail "stale prefix: fixture pid $dead is still alive"
git -C "$wrepo" worktree add -q --detach "$wrepo/.worktrees/tmp/builder-$dead/w" HEAD >/dev/null 2>&1 \
  || fail "stale prefix: could not add the dead-owner worktree"
git -C "$wrepo" worktree add -q --detach "$wrepo/.worktrees/tmp/builder-$$/w" HEAD >/dev/null 2>&1 \
  || fail "stale prefix: could not add the live-owner worktree"
rm -f "$wrepo"/*-L*.md "$wrepo"/*.log "$wrepo"/*.attempt.json "$wrepo/runs.jsonl"
src=0
(cd "$wrepo" && STUB_MODE=ok PATH="$tmp/wbin:$PATH" "$here/run.sh" builder L1 h.md >/dev/null 2>"$tmp/werr") || src=$?
[[ "$src" == 0 ]] || fail "stale prefix: run.sh exited $src, want 0 ($(cat "$tmp/werr"))"
[[ ! -e "$wrepo/.worktrees/tmp/builder-$dead" ]] || fail "stale prefix: dead-owner prefix builder-$dead is still on disk"
swl=$(git -C "$wrepo" worktree list --porcelain)
! grep -qF "/builder-$dead/w" <<<"$swl" \
  || fail "stale prefix: dead-owner worktree builder-$dead/w is still in git worktree list"
[[ -d "$wrepo/.worktrees/tmp/builder-$$/w" ]] || fail "stale prefix: live-owner worktree builder-$$/w was removed from disk"
grep -qF "/builder-$$/w" <<<"$swl" \
  || fail "stale prefix: live-owner worktree builder-$$/w is no longer in git worktree list"
git -C "$wrepo" worktree remove --force --force "$wrepo/.worktrees/tmp/builder-$$/w" >/dev/null 2>&1 || true
rm -rf "$wrepo/.worktrees"
git -C "$wrepo" worktree prune >/dev/null 2>&1 || true
[[ "$(git -C "$wrepo" worktree list | wc -l | tr -d ' ')" == 1 ]] || fail "stale prefix: cleanup left a worktree"

# Term cleanup: a stub that adds a worktree under its prefix and ignores TERM (sleep inherits the
# ignore through exec) must still leave nothing behind when the run gets TERM: run.sh stops the
# stub and cleans up inside run_lifecycle.py's 5 s grace, before its SIGKILL.
mkdir -p "$tmp/tbin"
cat >"$tmp/tbin/claude" <<'EOF'
#!/usr/bin/env bash
trap '' TERM
git worktree add -q --detach "$SDLC_TMP_WORKTREES/w" HEAD >/dev/null 2>&1 \
  || { echo "stub: git worktree add failed" >&2; exit 9; }
echo "$$" >"$STUB_READY.tmp" && mv "$STUB_READY.tmp" "$STUB_READY"
exec sleep 30
EOF
chmod +x "$tmp/tbin/claude"
rm -f "$tmp/term.ready" "$wrepo"/*-L*.md "$wrepo"/*.log "$wrepo"/*.attempt.json "$wrepo/runs.jsonl"
(cd "$wrepo" || exit 1; export STUB_READY="$tmp/term.ready" PATH="$tmp/tbin:$PATH"
  exec "$here/run.sh" builder L1 h.md) >/dev/null 2>"$tmp/terr" &
tpid=$!
for (( i = 0; i < 300; i++ )); do
  [[ -s "$tmp/term.ready" ]] && break
  kill -0 "$tpid" 2>/dev/null || break
  sleep 0.1
done
if [[ ! -s "$tmp/term.ready" ]]; then
  kill -KILL "$tpid" 2>/dev/null || true
  fail "term cleanup: the stub never wrote its ready marker ($(cat "$tmp/terr"))"
fi
stub_pid=$(cat "$tmp/term.ready")
kill -TERM "$tpid"
trc=0
wait "$tpid" || trc=$?
[[ "$trc" == 143 ]] || fail "term cleanup: run.sh exited $trc after TERM, want 143 ($(cat "$tmp/terr"))"
left=$(git -C "$wrepo" worktree list --porcelain | sed -n 's/^worktree //p' | grep -F '/.worktrees/tmp/' || true)
[[ -z "$left" ]] || fail "term cleanup: a worktree under .worktrees/tmp is still registered: $(tr '\n' ' ' <<<"$left")"
[[ ! -e "$wrepo/.worktrees/tmp" ]] || fail "term cleanup: $wrepo/.worktrees/tmp is left over"
if ps -p "$stub_pid" >/dev/null 2>&1; then
  kill -KILL "$stub_pid" 2>/dev/null || true
  fail "term cleanup: the stub claude (pid $stub_pid) is still alive"
fi

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
jq -nc '{type:"result",is_error:false,result:"## Status\ndone",total_cost_usd:0,duration_ms:1,num_turns:1}'
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
  rm -f "$srepo"/*-L*.md "$srepo"/*.log "$srepo"/*.attempt.json "$srepo/runs.jsonl"
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

# Temporary worktree recipe (run-operations): a bare clone with a dirty primary worktree. The role
# runs from a detached mktemp worktree; its result lands beside the absolute handoff in the primary.
rtmp=$(cd "$tmp" && pwd -P)
tg() { git -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false "$@"; }
tsrc="$rtmp/tsrc"
mkdir -p "$tsrc"
echo tracked >"$tsrc/file.txt"
echo '.sdlc/' >"$tsrc/.gitignore"
tg -C "$tsrc" init -q
tg -C "$tsrc" add -A
tg -C "$tsrc" commit -q -m init
tbranch=$(git -C "$tsrc" symbolic-ref --short HEAD)
bare="$rtmp/proj.git"
git clone -q --bare "$tsrc" "$bare" || fail "temporary worktree recipe: clone --bare failed"
primary="$rtmp/proj/$tbranch"
userwt="$rtmp/proj/user"
git -C "$bare" worktree add -q "$primary" "$tbranch" >/dev/null 2>&1 || fail "temporary worktree recipe: primary worktree add failed"
git -C "$bare" worktree add -q -b user-work "$userwt" HEAD >/dev/null 2>&1 || fail "temporary worktree recipe: user worktree add failed"
echo 'uncommitted edit' >>"$primary/file.txt"
echo untracked >"$primary/scratch.txt"
mkdir -p "$primary/.sdlc/t"
echo '## Goal' >"$primary/.sdlc/t/handoff.md"
# Snapshots, taken before the recipe path exists.
snap_status=$(git -C "$primary" status --porcelain)
cp "$primary/file.txt" "$rtmp/file.snap"
snap_wts=$(git -C "$bare" worktree list --porcelain)
snap_refs=$(git -C "$bare" for-each-ref refs/heads)
[[ -n "$snap_status" ]] || fail "temporary worktree recipe: fixture primary is not dirty"
# The recipe, in the doc's command shapes.
wt="$(mktemp -d "$rtmp/recipe.XXXXXX")/wt"
git -C "$bare" worktree add -q --detach "$wt" HEAD >/dev/null 2>&1 || fail "temporary worktree recipe: detached worktree add failed"
res $'## Map\nfile.txt'
rm -f "$tmp/cwd"
rc=0
(cd "$wt" && STUB_RESULT="$tmp/res.json" PATH="$tmp/bin:$PATH" "$here/run.sh" scout L1 "$primary/.sdlc/t/handoff.md" \
  >/dev/null 2>"$tmp/terr") || rc=$?
[[ "$rc" == 0 ]] || fail "temporary worktree recipe: run.sh exited $rc, want 0 ($(cat "$tmp/terr"))"
cwd_seen=$(cat "$tmp/cwd" 2>/dev/null || echo MISSING)
[[ "$cwd_seen" == "$wt" ]] || fail "temporary worktree recipe: the role ran in '$cwd_seen', want the temporary worktree $wt"
[[ -f "$primary/.sdlc/t/scout-L1.md" ]] || fail "temporary worktree recipe: $primary/.sdlc/t/scout-L1.md is missing"
[[ -f "$primary/.sdlc/t/runs.jsonl" ]] || fail "temporary worktree recipe: $primary/.sdlc/t/runs.jsonl is missing"
inwt=$(find "$wt" \( -name 'scout-L1*' -o -name runs.jsonl -o -name '*.attempt.json' -o -name handoff.md \) -print)
[[ -z "$inwt" ]] || fail "temporary worktree recipe: result files appeared under the temporary worktree: $(tr '\n' ' ' <<<"$inwt")"
wtstat=$(git -C "$wt" status --porcelain --ignored)
[[ -z "$wtstat" ]] || fail "temporary worktree recipe: the temporary worktree is not clean before removal: $(tr '\n' ' ' <<<"$wtstat")"
git -C "$bare" worktree remove "$wt" >/dev/null 2>"$tmp/terr" \
  || fail "temporary worktree recipe: worktree remove without --force failed: $(cat "$tmp/terr")"
rmdir "$(dirname "$wt")" || fail "temporary worktree recipe: could not remove the mktemp parent of $wt"
now_wts=$(git -C "$bare" worktree list --porcelain)
! grep -qF "$wt" <<<"$now_wts" || fail "temporary worktree recipe: $wt is still in git worktree list"
[[ ! -e "$wt" && ! -e "$(dirname "$wt")" ]] || fail "temporary worktree recipe: $wt is still on disk"
[[ "$now_wts" == "$snap_wts" ]] || fail "temporary worktree recipe: git worktree list changed: $(tr '\n' ' ' <<<"$now_wts")"
grep -qx "worktree $userwt" <<<"$now_wts" || fail "temporary worktree recipe: the user worktree $userwt is no longer listed"
[[ "$(git -C "$bare" for-each-ref refs/heads)" == "$snap_refs" ]] || fail "temporary worktree recipe: refs/heads changed"
[[ "$(git -C "$primary" status --porcelain)" == "$snap_status" ]] \
  || fail "temporary worktree recipe: the primary's porcelain status changed: $(git -C "$primary" status --porcelain | tr '\n' ' ')"
cmp -s "$primary/file.txt" "$rtmp/file.snap" || fail "temporary worktree recipe: the primary's tracked file bytes changed"
[[ ! -e "$primary/.worktrees" ]] || fail "temporary worktree recipe: the primary has a .worktrees dir"

# Self-edit: a role that rewrites run.sh in place while it runs must still get its result saved.
# Runs a copy of the plugin, so the real run.sh is never touched.
copy="$tmp/plugin-copy"
cp -R "$here/.." "$copy"
mkdir -p "$tmp/ebin"
cat >"$tmp/ebin/claude" <<EOF
#!/usr/bin/env bash
: >"$copy/scripts/run.sh"
jq -nc '{type:"result",is_error:false,result:"## Goal\\nself-edit survived",total_cost_usd:0,duration_ms:1,num_turns:1}'
EOF
chmod +x "$tmp/ebin/claude"
erepo="$tmp/erepo"
mkdir -p "$erepo"
echo '## Goal' >"$erepo/h.md"
git -C "$erepo" init -q
git -C "$erepo" add -A
git -C "$erepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
edir="$(cd "$erepo" && pwd)"
erc=0
eout=$(cd "$erepo" && PATH="$tmp/ebin:$PATH" "$copy/scripts/run.sh" planner L3 h.md 2>"$tmp/eerr") || erc=$?
[[ ! -s "$copy/scripts/run.sh" ]] || fail "self-edit: the stub did not truncate the copy's run.sh"
[[ "$erc" == 0 ]] || fail "self-edit: run.sh exited $erc, want 0 ($(cat "$tmp/eerr"))"
[[ "$eout" == "$edir/planner-L3.md" ]] || fail "self-edit: stdout is '$eout', want '$edir/planner-L3.md'"
[[ -f "$edir/planner-L3.md" ]] || fail "self-edit: result file planner-L3.md is missing"
grep -qx 'self-edit survived' "$edir/planner-L3.md" \
  || fail "self-edit: planner-L3.md lacks the stub's text: $(tr '\n' ' ' <"$edir/planner-L3.md")"
jq -e 'select(.file == "planner-L3.md")' "$edir/runs.jsonl" >/dev/null 2>&1 \
  || fail "self-edit: runs.jsonl has no line with file planner-L3.md"
est=$(jq -r '.status' "$edir/planner-L3.attempt.json" 2>/dev/null || echo MISSING)
[[ "$est" == completed ]] || fail "self-edit: planner-L3.attempt.json status is '$est', want completed"

# Mailbox notice.
mrepo="$tmp/mrepo"
mkdir -p "$mrepo"
echo x >"$mrepo/h.md"
git -C "$mrepo" init -q
git -C "$mrepo" add -A
git -C "$mrepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
nline() { echo "run.sh: $1 new message(s) for $2; read with messages.py"; }
(cd "$mrepo" && SDLC_DRY_RUN=1 "$here/run.sh" planner L2 h.md >/dev/null 2>"$tmp/n0") \
  || fail "notice: dry run with no mailbox exited non-zero"
[[ ! -s "$tmp/n0" ]] || fail "notice: dry run with no mailbox printed stderr: $(cat "$tmp/n0")"
[[ ! -e "$mrepo/.sdlc" ]] || fail "notice: dry run with no mailbox created .sdlc"
(cd "$mrepo" && python3 "$here/messages.py" send --receiver planner --sender alice --topic t \
  --follow-up false notice-body-1 >/dev/null) || fail "notice: send to planner failed"
(cd "$mrepo" && SDLC_DRY_RUN=1 "$here/run.sh" planner L2 h.md >/dev/null 2>"$tmp/n1") \
  || fail "notice: planner dry run exited non-zero"
[[ "$(cat "$tmp/n1")" == "$(nline 1 planner)" ]] || fail "notice: one message: stderr is '$(cat "$tmp/n1")'"
(cd "$mrepo" && python3 "$here/messages.py" send --receiver claude --sender codex --topic t \
  --follow-up false notice-body-2 >/dev/null) || fail "notice: send to claude failed"
(cd "$mrepo" && SDLC_DRY_RUN=1 "$here/run.sh" planner L2 h.md >/dev/null 2>"$tmp/n2") \
  || fail "notice: planner dry run exited non-zero"
[[ "$(cat "$tmp/n2")" == "$(nline 2 planner)" ]] || fail "notice: role plus backend: stderr is '$(cat "$tmp/n2")'"
(cd "$mrepo" && SDLC_DRY_RUN=1 "$here/run.sh" builder L2 h.md >/dev/null 2>"$tmp/n3") \
  || fail "notice: builder dry run exited non-zero"
[[ "$(cat "$tmp/n3")" == "$(nline 1 builder)" ]] || fail "notice: builder: stderr is '$(cat "$tmp/n3")'"
nrc=0
(cd "$mrepo" && PATH="$tmp/bin:$PATH" "$here/run.sh" planner L2 h.md >"$tmp/n4o" 2>"$tmp/n4e") || nrc=$?
[[ "$nrc" == 0 ]] || fail "notice: real run exited $nrc ($(cat "$tmp/n4e"))"
[[ "$(grep -cF "new message(s)" "$tmp/n4e")" == 1 ]] || fail "notice: real run did not print the notice exactly once: $(cat "$tmp/n4e")"
grep -qxF "$(nline 2 planner)" "$tmp/n4e" || fail "notice: real run notice line is wrong: $(cat "$tmp/n4e")"
! grep -qF notice-body "$tmp/n4o" "$tmp/n4e" || fail "notice: real run printed a message body"

# Spec gate (see the header).
sgrepo="$tmp/sgrepo"
mkdir -p "$sgrepo/.sdlc/t"
echo '## Goal' >"$sgrepo/.sdlc/t/handoff.md"
git -C "$sgrepo" init -q
git -C "$sgrepo" add -A
git -C "$sgrepo" -c user.name=selftest -c user.email=selftest@example.invalid -c commit.gpgsign=false \
  commit -q -m init
sgd="$sgrepo/.sdlc/t"
sgplan() { # sgplan <goal extra line>: a planner result whose step 1 guard runs check.sh
  printf '%s\n' '<!-- role=planner level=L1 model=sonnet effort=medium -->' '## Goal' x "$1" '' \
    '## Step 1: Gates' 'level: L1' '### Do' x '### Acceptance criteria' \
    '- (guard) `bash plugins/sdlc-lite/scripts/check.sh`' '' '## Assumptions' None '' '## Risks' None >"$sgd/planner-L1.md"
}
# sgrun <out file> [env assignments...]: plan-reviewer run in sgrepo; prints the exit code.
sgrun() {
  local o="$1" rc=0; shift
  (cd "$sgrepo" && env -u SDLC_SPECGATE -u SDLC_DRY_RUN "$@" STUB_RESULT="$tmp/res.json" PATH="$tmp/bin:$PATH" \
    "$here/run.sh" plan-reviewer L1 .sdlc/t/handoff.md >"$o" 2>&1) || rc=$?
  echo "$rc"
}
res $'## Verdict\npass'
sgplan ''
rm -f "$tmp/count"
rc=$(sgrun "$tmp/sg1" SDLC_DRY_RUN=1)
[[ "$rc" == 2 ]] || fail "spec gate: dry run on a check.sh guard with no guard timeout line exited $rc, want 2: $(cat "$tmp/sg1")"
grep -qF "step 1: slow guard:" "$tmp/sg1" || fail "spec gate: dry run did not print slow guard: $(cat "$tmp/sg1")"
grep -qF "run.sh: specgate.py check refused the plan in $sgd; replan, or set SDLC_SPECGATE=off" "$tmp/sg1" \
  || fail "spec gate: dry run did not print the run.sh refusal line: $(cat "$tmp/sg1")"
rc=$(sgrun "$tmp/sg2")
[[ "$rc" == 2 ]] || fail "spec gate: real run on a refused plan exited $rc, want 2: $(cat "$tmp/sg2")"
[[ ! -e "$tmp/count" ]] || fail "spec gate: real run on a refused plan called the stub claude"
[[ ! -e "$sgd/runs.jsonl" ]] || fail "spec gate: real run on a refused plan wrote runs.jsonl"
[[ -z "$(find "$sgd" -name '*.running')" ]] || fail "spec gate: real run on a refused plan left a .running file"
[[ -z "$(find "$sgd" -name '*.attempt.json')" ]] || fail "spec gate: real run on a refused plan left an attempt record"
sgplan 'guard timeout: 900'
rc=$(sgrun "$tmp/sg3" SDLC_DRY_RUN=1)
[[ "$rc" == 0 ]] || fail "spec gate: dry run on a plan with a guard timeout line exited $rc, want 0: $(cat "$tmp/sg3")"
! grep -qF specgate "$tmp/sg3" || fail "spec gate: a passing gate printed a line: $(cat "$tmp/sg3")"
sgplan ''
rc=$(sgrun "$tmp/sg4" SDLC_SPECGATE=off)
[[ "$rc" == 0 ]] || fail "spec gate: SDLC_SPECGATE=off real run exited $rc, want 0: $(cat "$tmp/sg4")"
grep -qxF "run.sh: SDLC_SPECGATE=off: spec gate skipped" "$tmp/sg4" || fail "spec gate: off did not print its skip line: $(cat "$tmp/sg4")"
[[ -e "$tmp/count" ]] || fail "spec gate: SDLC_SPECGATE=off real run never called the stub claude"
tail -n 1 "$sgd/runs.jsonl" | jq -e '.specgate == "off"' >/dev/null 2>&1 \
  || fail "spec gate: SDLC_SPECGATE=off run line lacks \"specgate\":\"off\": $(tail -n 1 "$sgd/runs.jsonl" 2>/dev/null)"
res $'## Goal\nx'
(cd "$sgrepo" && env -u SDLC_SPECGATE SDLC_SPECGATE=off STUB_RESULT="$tmp/res.json" PATH="$tmp/bin:$PATH" \
  "$here/run.sh" planner L1 .sdlc/t/handoff.md >/dev/null 2>&1) || fail "spec gate: planner run with SDLC_SPECGATE=off failed"
! tail -n 1 "$sgd/runs.jsonl" | jq -e 'has("specgate")' >/dev/null 2>&1 \
  || fail "spec gate: a planner run line carries a specgate key: $(tail -n 1 "$sgd/runs.jsonl")"

echo "run selftest: PASS"
