#!/usr/bin/env bash
# Selftest for run.sh result numbering: three runs of the same role and level must keep every
# result. The first run writes <role>-<level>.md, later runs write <role>-<level>-2.md, -3.md, ...
# Each runs.jsonl line must name its result in a "file" field, in run order.
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

echo "run selftest: PASS"
