#!/usr/bin/env bash
# Selftest for the PreToolUse hooks (Bash, Agent, Monitor): block-background.sh denies Bash
# run_in_background, Agent unless run_in_background is false, and every Monitor call, in a headless session (SDLC_ROLE set or SDLC_HEADLESS=1) and passes everything else; block-publish.sh,
# inside a role run, allows commands that only mention a publish phrase (heredoc body, quoted
# argument, commit message) and blocks every real publish, including one fed to a shell or
# evaluator, one in a $(...) or backtick substitution, one behind an unterminated quote, and
# one in interpreter inline code (python -c, node -e/--eval, perl -e, ruby -e), while a plain
# python3 script run and an interpreter word inside a quoted mention pass;
# block-pattern-kill.sh, inside a role run, blocks killing by name pattern (pkill, killall,
# kill fed by pgrep or ps, ps ... | xargs kill, a kill word held in a variable, also one
# assigned through a $(...) or backtick substitution) with a stderr naming the role and PIDs, and allows kill <pid>, kill $pid, kill %1, kill $(cat pidfile),
# echo $! | xargs kill, a variable holding another command, a quoted mention, and anything
# outside a role run; block-stray-worktree.sh, inside a role run, denies a git worktree add
# that is not detached under $SDLC_TMP_WORKTREES (a path outside it or with a .. segment, -b,
# -B, --orphan, no commit-ish, git -C, a bash -c wrapper, SDLC_TMP_WORKTREES unset) with a
# stderr naming the role, and allows the detached form, git worktree remove, a quoted mention,
# and anything outside a role run. block-repo-format.sh, inside a builder run, blocks a
# repo-wide format script or formatter (npm run format, make fmt, prettier --write ., eslint
# --fix src, cargo fmt, go fmt ./..., one behind cd x && or inside bash -c) with a stderr
# naming the role and builder rule 6, and allows explicit file paths, npm test, a quoted
# mention, and every other role or no role. block-disk-scan.sh, inside a role run, blocks a
# search of the whole filesystem or a home folder (find, bfs, rg, grep -r on /, ~, "$HOME",
# /Users, also behind sudo or inside bash -c) with a stderr naming the role, and allows
# find ., a path below those roots, ls / without -R, a quoted mention, and no role.
# block-role-spawn.sh is the spawn gate. In a conductor session (agent_type sdlc-lite:conductor or
# conductor, or SDLC_ROLE=conductor) it allows an sdlc-lite:<role>-L<n> spawn only when the name is
# <ticket>-<role>-L<n>[-<k>], a dispatch record beside the prompt's Handoff names that agent, and the
# call's model equals the record's model; each of the four conditions has a deny case, built by
# changing one thing in a passing payload. It denies a fork named verifier- or plan-reviewer-, a
# fork with no "Fork reason:" line, and another plugin's builder, verifier, reviewer, planner, or
# checker agent (stderr naming run.sh), and allows Explore, general-purpose, harness:fact-finder,
# non-conductor sessions, a run.sh Bash call, and non-Agent tools.
# _role.sh resolves the role (SDLC_ROLE, else agent_type minus sdlc-lite: and -L<n>); the five role
# hooks above each block a sub-agent role input and pass an input with no role, an interactive
# conductor, or a non-SDLC agent. block-role-write.sh lets a read-only role sub-agent Write only
# its dispatch result path (Write elsewhere, Edit, and NotebookEdit denied) and leaves the
# builder, solo, the conductor, and no role unrestricted. block-role-rm.sh (T-0538) lets a read-only
# role remove files only under its throwaway prefix: rm, rmdir, or unlink of a path under it passes (and
# prints an allow decision when the command is only rm and cd), a path outside it, with .. or an expansion
# the hook cannot read, is denied with a stderr naming the role, and every other role or no role passes.
# warn-handoff-edit.sh, for an Edit, Write, or NotebookEdit whose file is named handoff.md with a
# <role>-<level>.running file beside it, allows the edit (exit 0), prints a freeze warning, and
# appends one line to stale-edits.log beside the handoff; with SDLC_HANDOFF_EDIT_MODE=deny the same
# case exits 2 with the same message. No .running file, another file name, and a .running file in a
# different directory pass silently with no log line. Prepared-attempt cases (T-0505) use no hand-made
# marker: after a real dispatch.py prepare scout L1 in a throwaway repo, warn mode warns and logs one line
# and deny mode exits 2; after dispatch.py record (completed, and failed on error text) and after
# dispatch.py recover of a dead-owner attempt the hook is silent; recover leaves an attempt whose owner
# is alive running, and its handoff stays frozen.
# Publish phrases, kill-pattern words, and root-search phrases are built with printf so this
# file never holds one as a command.
# Never inherits the caller's SDLC_ROLE/SDLC_HEADLESS/SDLC_TMP_WORKTREES.
# Prints "hook selftest: PASS" or "hook selftest: FAIL: <case>" and exits non-zero on failure.
set -uo pipefail

hooks="$(cd "$(dirname "$0")/../hooks" && pwd)"
bg="$hooks/block-background.sh"
pub="$hooks/block-publish.sh"
pk="$hooks/block-pattern-kill.sh"
sw="$hooks/block-stray-worktree.sh"
rf="$hooks/block-repo-format.sh"
ds="$hooks/block-disk-scan.sh"
rs="$hooks/block-role-spawn.sh"
wh="$hooks/warn-handoff-edit.sh"
wrh="$hooks/block-role-write.sh"
rmh="$hooks/block-role-rm.sh"

fail() { echo "hook selftest: FAIL: $*"; exit 1; }

# run <hook> <json> [VAR=value ...]: prints stderr, returns the hook's exit code.
run() {
  local hook="$1" json="$2"; shift 2
  # Stdin comes from process substitution, not a pipe stage: a hook that exits
  # before reading stdin would SIGPIPE a feeder and pipefail would report 141.
  env -u SDLC_ROLE -u SDLC_HEADLESS -u SDLC_TMP_WORKTREES "$@" "$hook" 3>&1 1>/dev/null 2>&3 < <(printf '%s' "$json")
}

on='{"tool_input":{"command":"sleep 1","run_in_background":true}}'
off='{"tool_input":{"command":"sleep 1","run_in_background":false}}'
absent='{"tool_input":{"command":"sleep 1"}}'

out=$(run "$bg" "$on" SDLC_ROLE=builder); rc=$?
[[ $rc -eq 2 ]] || fail "role + background true: exit $rc, want 2"
grep -qi foreground <<<"$out" || fail "role + background true: stderr lacks foreground"
grep -q 600000 <<<"$out" || fail "role + background true: stderr lacks 600000"

run "$bg" "$on" SDLC_HEADLESS=1 >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "SDLC_HEADLESS=1 + background true: exit $rc, want 2"

run "$bg" "$on" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "neither set + background true: exit $rc, want 0"

run "$bg" "$off" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "role + background false: exit $rc, want 0"

run "$bg" "$absent" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "role + background absent: exit $rc, want 0"

run "$bg" "$on" SDLC_HEADLESS=0 >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "SDLC_HEADLESS=0 + background true: exit $rc, want 0"

push_json=$(printf '{"tool_input":{"command":"git %s origin main"}}' push)
run "$pub" "$push_json" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish push with role: exit $rc, want 2"

run "$pub" '{"tool_input":{"command":"ls"}}' SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish ls with role: exit $rc, want 0"

# pj <command>: the hook's JSON for one Bash command.
pj() { jq -n --arg c "$1" '{tool_input:{command:$c}}'; }

# Only mentions a publish phrase: allowed.
c=$(printf 'cat > f <<%s\ngit %s origin main\nEOF\n' "'EOF'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows heredoc body: exit $rc, want 0"
c=$(printf "sed -i 's/x/git %s/' f" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows sed argument: exit $rc, want 0"
c=$(printf 'python3 scripts/check.py "git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows python3 script run: exit $rc, want 0"
c="python3 -c 'print(1)'"
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows interpreter without publish: exit $rc, want 0"
c=$(printf 'git commit -m "doc: python3 -c must never git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows interpreter word in quoted mention: exit $rc, want 0"
c=$(printf 'git commit -m "doc: never git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows commit message: exit $rc, want 0"
c=$(printf 'grep -n "npm %s" f' publish)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows grep argument: exit $rc, want 0"

# A real publish, direct, via a shell or evaluator, or in a substitution: blocked.
# Interpreter inline code is scanned raw: blocked.
c=$(printf "python3 -c 'print(\"gh %s create\")'" pr)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks python3 -c: exit $rc, want 2"
c=$(printf "/usr/bin/python3 -u -c 'import os; os.system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks /usr/bin/python3 -c: exit $rc, want 2"
c=$(printf "node -e 'require(\"child_process\").execSync(\"gh %s create\")'" pr)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks node -e: exit $rc, want 2"
c=$(printf "node --eval 'require(\"child_process\").execSync(\"gh %s create\")'" pr)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks node --eval: exit $rc, want 2"
c=$(printf "perl -e 'system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks perl -e: exit $rc, want 2"
c=$(printf "ruby -e 'system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks ruby -e: exit $rc, want 2"
c=$(printf "python3 -X dev -c 'import os; os.system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks python3 -X dev -c: exit $rc, want 2"
c=$(printf "python3 -W ignore -c 'import os; os.system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks python3 -W ignore -c: exit $rc, want 2"
c=$(printf "node --require x -e 'require(\"child_process\").execSync(\"gh %s create\")'" pr)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks node --require x -e: exit $rc, want 2"
c=$(printf "perl -I lib -e 'system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks perl -I lib -e: exit $rc, want 2"
c=$(printf "ruby -I lib -e 'system(\"git %s\")'" push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks ruby -I lib -e: exit $rc, want 2"
# A script path ends the option run: masked scan, allowed.
c=$(printf 'python3 -X dev scripts/check.py "git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows python3 -X dev script.py: exit $rc, want 0"
c=$(printf 'python3 scripts/check.py -c "git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-publish allows python3 script.py -c: exit $rc, want 0"
c=$(printf 'git %s origin main' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks plain push: exit $rc, want 2"
c=$(printf 'cd x && git %s' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks push after &&: exit $rc, want 2"
c=$(printf 'bash -c "git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks bash -c: exit $rc, want 2"
c=$(printf "sh -c 'gh %s create'" pr)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks sh -c: exit $rc, want 2"
c=$(printf 'bash <<EOF\ngit %s\nEOF\n' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks bash heredoc: exit $rc, want 2"
# shellcheck disable=SC2016
c=$(printf 'echo "$(git %s)"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks \$() in double quotes: exit $rc, want 2"
# shellcheck disable=SC2016
c=$(printf 'echo "`git %s`"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks backtick in double quotes: exit $rc, want 2"
c=$(printf 'eval "git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks eval: exit $rc, want 2"
c=$(printf 'gh api -X %s repos/o/r/issues' POST)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks gh api POST: exit $rc, want 2"
c=$(printf 'npm %s' publish)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks npm: exit $rc, want 2"
c=$(printf 'cat <<EOF | sh\ngh %s create\nEOF\n' pr)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks heredoc piped to sh: exit $rc, want 2"
c=$(printf 'ssh host "git %s"' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks ssh: exit $rc, want 2"
c=$(printf 'git log | xargs git %s' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks xargs: exit $rc, want 2"
c=$(printf 'ls | (git %s origin main)' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks subshell: exit $rc, want 2"
c=$(printf 'echo "x" ; git %s origin main "' push)
run "$pub" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-publish blocks unterminated quote: exit $rc, want 2"

# block-pattern-kill.sh: inside a role run, killing by name pattern is blocked; killing a PID,
# a mention inside a quoted argument, and anything outside a role run are allowed.
pkw=$(printf 'p%s' kill); kaw=$(printf 'kill%s' all); pgw=$(printf 'p%s' grep)
c="$pkw -f vite"
out=$(run "$pk" "$(pj "$c")" SDLC_ROLE=builder); rc=$?
[[ $rc -eq 2 ]] || fail "block-pattern-kill blocks $pkw: exit $rc, want 2"
grep -q PID <<<"$out" || fail "block-pattern-kill $pkw: stderr lacks PID"
grep -q builder <<<"$out" || fail "block-pattern-kill $pkw: stderr lacks the role"
psw=$(printf 'p%s' s); awk2="awk '{print \$2}'"
for c in "$kaw node" "kill \$($pgw -f vite)" "$pgw -f vite | xargs kill" "sudo $pkw -f vite" \
  "cd x && $pkw -f vite" "$psw aux | grep x | $awk2 | xargs kill" \
  "$psw -ef | grep x | $awk2 | xargs kill -9" "kill \$($psw aux | grep x | $awk2)" \
  "p=$pkw; \$p x" "k=$kaw; \${k} node" "p=\$(command -v $pkw); \$p x" \
  "k=\$(which $kaw); \${k} node" "p=\`command -v $pkw\`; \$p x" "p=\$(echo find $pkw); \$p x" \
  "k=\$(compgen -c | grep $kaw | head -1); \${k} node" "k=\$(command -v kill); \$k \$($pgw -f vite)"; do
  run "$pk" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "block-pattern-kill blocks '$c': exit $rc, want 2"
done
for c in "kill 12345" "kill \$pid" "grep -n \"$pkw\" f" "kill %1" "kill \$(cat pidfile)" \
  "echo \$! | xargs kill" "cmd=ls; \$cmd -la" "cmd=\$(command -v ls); \$cmd -la" \
  "cmd=\`command -v ls\`; \$cmd -la" "echo 'p=\$(command -v $pkw); \$p x'"; do
  run "$pk" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-pattern-kill allows '$c': exit $rc, want 0"
done
run "$pk" "$(pj "$pkw -f vite")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-pattern-kill without role: exit $rc, want 0"

# block-stray-worktree.sh: inside a role run, a git worktree add must be detached and under
# $SDLC_TMP_WORKTREES; anything else is denied, other worktree commands and mentions pass.
# shellcheck disable=SC2016
tw='$SDLC_TMP_WORKTREES'
swenv=(SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1)
out=$(run "$sw" "$(pj "git worktree add /tmp/x HEAD")" "${swenv[@]}"); rc=$?
[[ $rc -eq 2 ]] || fail "block-stray-worktree denies /tmp/x: exit $rc, want 2"
grep -q builder <<<"$out" || fail "block-stray-worktree /tmp/x: stderr lacks the role"
grep -q -- '--detach' <<<"$out" || fail "block-stray-worktree /tmp/x: stderr lacks the allowed form"
for c in "git worktree add -b tmpbr \"$tw/x\" HEAD" "git worktree add -B tmpbr \"$tw/x\" HEAD" \
  "git worktree add --orphan \"$tw/x\"" "git worktree add --orphan -b tmpbr \"$tw/x\"" \
  "git -C . worktree add /tmp/x HEAD" "git worktree add \"$tw/x\"" \
  "git worktree add \"$tw/../x\" HEAD" "bash -c \"git worktree add /tmp/x HEAD\"" \
  "git worktree add --detach \"$tw\" HEAD" "git worktree add \"$tw/x\" feature-x" \
  "git worktree add \"$tw/x\" HEAD" "git worktree add --no-detach \"$tw/x\" HEAD" \
  "git worktree add \"$tw/x\" -- feature-x" "git worktree add \"\${SDLC_TMP_WORKTREES}/base\" HEAD"; do
  run "$sw" "$(pj "$c")" "${swenv[@]}" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "block-stray-worktree denies '$c': exit $rc, want 2"
done
out=$(run "$sw" "$(pj "git worktree add --detach /r/x HEAD")" SDLC_ROLE=conductor); rc=$?
[[ $rc -eq 2 ]] || fail "block-stray-worktree denies with SDLC_TMP_WORKTREES unset: exit $rc, want 2"
grep -q conductor <<<"$out" || fail "block-stray-worktree prefix unset: stderr lacks the role"
for c in "git worktree add --detach \"$tw/x\" HEAD" "git worktree add --detach \"\${SDLC_TMP_WORKTREES}/base\" HEAD" \
  "git worktree add -d \"$tw/x\" HEAD" "git worktree add --detach \"$tw/x\" origin/feature-x" \
  "git worktree add --detach /r/.worktrees/tmp/builder-1/x HEAD" \
  "git worktree remove --force \"$tw/x\"" "git worktree list" "grep -n \"git worktree add\" f"; do
  run "$sw" "$(pj "$c")" "${swenv[@]}" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-stray-worktree allows '$c': exit $rc, want 0"
done
# C7 (lane lifecycle): the denial names the lane commands, and a lanes.py call is not a worktree add.
out=$(run "$sw" "$(pj "git worktree add -b lane-x /tmp/x HEAD")" "${swenv[@]}"); rc=$?
[[ $rc -eq 2 ]] || fail "C7 raw git worktree add -b: exit $rc, want 2"
grep -q 'lanes.py open' <<<"$out" && grep -q 'lanes.py close' <<<"$out" || fail "C7 stray-worktree message lacks lanes.py open and close"
run "$sw" "$(pj "python3 scripts/lanes.py open lane-x --kind solo")" SDLC_ROLE=conductor >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "C7 lanes.py open passes the stray-worktree hook: exit $rc, want 0"
run "$sw" "$(pj "git worktree add /tmp/x HEAD")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-stray-worktree without role: exit $rc, want 0"

# block-repo-format.sh: inside a builder run, a repo-wide format script or formatter is
# blocked; explicit file paths, other commands, a quoted mention, and other roles pass.
out=$(run "$rf" "$(pj "npm run format")" SDLC_ROLE=builder); rc=$?
[[ $rc -eq 2 ]] || fail "block-repo-format blocks npm run format: exit $rc, want 2"
grep -q builder <<<"$out" || fail "block-repo-format npm run format: stderr lacks the role"
grep -q 'rule 6' <<<"$out" || fail "block-repo-format npm run format: stderr lacks rule 6"
rfblock=("npm run format" "pnpm run format" "yarn run lint:fix" "make fmt" "prettier --write ." \
  "eslint --fix src" "cargo fmt" "go fmt ./..." "npx prettier -w src/" \
  "cd x && npm run format" "bash -c 'npm run format'")
for c in "${rfblock[@]}"; do
  out=$(run "$rf" "$(pj "$c")" SDLC_ROLE=builder); rc=$?
  [[ $rc -eq 2 ]] || fail "block-repo-format blocks '$c': exit $rc, want 2"
  grep -q builder <<<"$out" || fail "block-repo-format '$c': stderr lacks the role"
  grep -q 'rule 6' <<<"$out" || fail "block-repo-format '$c': stderr lacks rule 6"
done
for c in "prettier --write a.ts" "npm run format -- a.ts" "npm test" \
  "eslint --fix src/a.ts src/b.ts" "grep -n 'npm run format' f" "ls"; do
  run "$rf" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-repo-format allows '$c': exit $rc, want 0"
done
for c in "${rfblock[@]}"; do
  run "$rf" "$(pj "$c")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-repo-format without role allows '$c': exit $rc, want 0"
  run "$rf" "$(pj "$c")" SDLC_ROLE=verifier >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-repo-format verifier allows '$c': exit $rc, want 0"
done

# block-disk-scan.sh: inside a role run, a search of the whole filesystem or a home folder is
# blocked; a bounded path, ls without -R, a quoted mention, and no role pass.
fw=$(printf 'f%s' ind); bw=$(printf 'b%s' fs); rw=$(printf 'r%s' g); gw=$(printf 'g%s' rep)
# shellcheck disable=SC2016
hv='"$HOME"'
out=$(run "$ds" "$(pj "$fw / -name quick_validate.py -path \"*skill*\" 2>/dev/null | head -3")" SDLC_ROLE=planner); rc=$?
[[ $rc -eq 2 ]] || fail "block-disk-scan blocks the T-0160 repro: exit $rc, want 2"
grep -q planner <<<"$out" || fail "block-disk-scan T-0160 repro: stderr lacks the role"
for c in "$bw / -name x" "$fw ~ -name x" "$fw $hv -name x" "$fw /Users -name x" "$rw -l x /" \
  "$gw -r x ~" "sudo $fw / -name x" "bash -c \"$fw / -name x\""; do
  out=$(run "$ds" "$(pj "$c")" SDLC_ROLE=scout); rc=$?
  [[ $rc -eq 2 ]] || fail "block-disk-scan blocks '$c': exit $rc, want 2"
  grep -q scout <<<"$out" || fail "block-disk-scan '$c': stderr lacks the role"
done
for c in "$fw . -name x" "$fw /tmp/x -name y" "$fw ~/.claude/plugins -name x" "ls /" \
  "$gw -n \"$fw / -name x\" notes.md"; do
  run "$ds" "$(pj "$c")" SDLC_ROLE=planner >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-disk-scan allows '$c': exit $rc, want 0"
done
run "$ds" "$(pj "$fw / -name x")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-disk-scan without role: exit $rc, want 0"

a_absent='{"tool_name":"Agent","tool_input":{"prompt":"x"}}'
a_on='{"tool_name":"Agent","tool_input":{"prompt":"x","run_in_background":true}}'
a_off='{"tool_name":"Agent","tool_input":{"prompt":"x","run_in_background":false}}'

out=$(run "$bg" "$a_absent" SDLC_ROLE=conductor); rc=$?
[[ $rc -eq 2 ]] || fail "agent role + absent: exit $rc, want 2"
grep -q 'run_in_background: false' <<<"$out" || fail "agent role + absent: stderr lacks run_in_background: false"

run "$bg" "$a_absent" SDLC_HEADLESS=1 >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "agent SDLC_HEADLESS=1 + absent: exit $rc, want 2"

run "$bg" "$a_on" SDLC_ROLE=conductor >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "agent role + true: exit $rc, want 2"

run "$bg" "$a_off" SDLC_ROLE=conductor >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "agent role + false: exit $rc, want 0"

run "$bg" "$a_absent" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "agent neither set + absent: exit $rc, want 0"

run "$bg" "$a_on" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "agent neither set + true: exit $rc, want 0"

run "$bg" "$a_absent" SDLC_HEADLESS=0 >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "agent SDLC_HEADLESS=0 + absent: exit $rc, want 0"

run "$bg" '{"tool_name":"Bash","tool_input":{"command":"sleep 1"}}' SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "bash tool_name role + absent: exit $rc, want 0"

m_json='{"tool_name":"Monitor","tool_input":{"command":"x"}}'

out=$(run "$bg" "$m_json" SDLC_ROLE=verifier); rc=$?
[[ $rc -eq 2 ]] || fail "monitor role: exit $rc, want 2"
grep -qi foreground <<<"$out" || fail "monitor role: stderr lacks foreground"

run "$bg" "$m_json" SDLC_HEADLESS=1 >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "monitor SDLC_HEADLESS=1: exit $rc, want 2"

run "$bg" "$m_json" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "monitor neither set: exit $rc, want 0"

run "$bg" "$m_json" SDLC_HEADLESS=0 >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "monitor SDLC_HEADLESS=0: exit $rc, want 0"

# rsj <agent_type or empty> <subagent_type> [tool]: the hook's JSON for one Agent spawn.
rsj() {
  local at="" tool="${3:-Agent}"
  [[ -n "$1" ]] && at=$(printf ',"agent_type":"%s"' "$1")
  printf '{"tool_name":"%s"%s,"tool_input":{"subagent_type":"%s","prompt":"x"}}' "$tool" "$at" "$2"
}
out=$(run "$rs" "$(rsj sdlc-lite:conductor sdlc-lite:builder)"); rc=$?
[[ $rc -eq 2 ]] || fail "role-spawn conductor + sdlc-lite:builder: exit $rc, want 2"
grep -q "dispatch.py prepare" <<<"$out" || fail "role-spawn conductor + sdlc-lite:builder: stderr lacks dispatch.py prepare"
out=$(run "$rs" "$(rsj sdlc-lite:conductor other:code-builder)"); rc=$?
[[ $rc -eq 2 ]] || fail "role-spawn conductor + other:code-builder: exit $rc, want 2"
grep -q run.sh <<<"$out" || fail "role-spawn conductor + other:code-builder: stderr lacks run.sh"
while IFS='|' read -r at sub env want; do
  if [[ -n "$env" ]]; then run "$rs" "$(rsj "$at" "$sub")" "$env" >/dev/null; rc=$?
  else run "$rs" "$(rsj "$at" "$sub")" >/dev/null; rc=$?; fi
  [[ $rc -eq $want ]] || fail "role-spawn agent_type '$at' + $sub ${env}: exit $rc, want $want"
done <<'CASES'
sdlc-lite:conductor|sdlc-lite:scout||2
sdlc-lite:conductor|other:code-reviewer||2
sdlc-lite:conductor|harness:agent-checker||2
conductor|sdlc-lite:verifier||2
|sdlc-lite:planner|SDLC_ROLE=conductor|2
sdlc-lite:conductor|Explore||0
sdlc-lite:conductor|general-purpose||0
sdlc-lite:conductor|harness:fact-finder||0
|sdlc-lite:builder||0
probecond|sdlc-lite:builder||0
CASES
run "$rs" "$(rsj sdlc-lite:conductor sdlc-lite:builder Bash)" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "role-spawn tool Bash + conductor: exit $rc, want 0"

# A run.sh invocation is a Bash call, so the spawn gate never sees it.
runsh_json=$(jq -n '{tool_name:"Bash",agent_type:"sdlc-lite:conductor",tool_input:{command:"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh verifier L3 .sdlc/t/handoff.md"}}')
run "$rs" "$runsh_json" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "role-spawn leaves a run.sh Bash call alone: exit $rc, want 0"
hooks_json="$hooks/../adapters/claude/hooks.json"
[[ "$(jq -r '[.hooks.PreToolUse[] | select(.matcher == "Agent") | .hooks[].command | select(contains("block-role-spawn.sh"))] | length' "$hooks_json")" == 1 ]] ||
  fail "hooks.json does not register block-role-spawn.sh under the Agent matcher"
[[ "$(jq -r '[.hooks.PreToolUse[] | select(.matcher != "Agent") | .hooks[].command | select(contains("block-role-spawn.sh"))] | length' "$hooks_json")" == 0 ]] ||
  fail "hooks.json registers block-role-spawn.sh under a matcher other than Agent"
[[ "$(jq -r '[.hooks.PreToolUse[] | select(.matcher == "Edit|Write|NotebookEdit") | .hooks[].command | select(contains("block-role-write.sh"))] | length' "$hooks_json")" == 1 ]] ||
  fail "hooks.json does not register block-role-write.sh under the Edit|Write|NotebookEdit matcher"
[[ "$(jq -r '[.hooks.PreToolUse[].hooks[].command | select(contains("_role.sh"))] | length' "$hooks_json")" == 0 ]] ||
  fail "hooks.json registers _role.sh, which is sourced by the hooks and never run"

wtmp=$(mktemp -d); trap 'rm -rf "$wtmp"' EXIT

# Spawn gate. A prepared dispatch is allowed; each of its four conditions has a deny case, built by
# changing exactly one thing in a payload that passes. gate/ holds what dispatch.py prepare writes:
# <role>-L<n>.dispatch.json (keyed by the stem, with the Agent name inside it) beside the handoff.
gate="$wtmp/gate"; mkdir -p "$gate/other"
: >"$gate/handoff.md"
printf '%s' '{"subagent_type":"sdlc-lite:verifier-L3","name":"gate-task-verifier-L3","model":"opus","role":"verifier","level":"L3"}' >"$gate/verifier-L3.dispatch.json"
printf '%s' '{"subagent_type":"sdlc-lite:builder-L2","name":"gate-task-builder-L2-2","model":"sonnet","role":"builder","level":"L2"}' >"$gate/builder-L2-2.dispatch.json"
printf '%s' '{"model":"haiku"}' >"$gate/gate-task-scout-L1.dispatch.json"
# gj <subagent_type> <name> <model> <handoff> [agent_type]: the JSON of one conductor Agent spawn
# whose prompt carries the Handoff line dispatch.py prepare writes.
gj() {
  jq -n --arg sub "$1" --arg name "$2" --arg model "$3" --arg h "$4" --arg at "${5-sdlc-lite:conductor}" --arg cwd "$gate" \
    '{tool_name:"Agent",cwd:$cwd,tool_input:{subagent_type:$sub,description:"d",prompt:("Handoff: " + $h + "\nArtifacts dir: x\nYour final message is saved verbatim as y."),run_in_background:true}}
     | if $at != "" then .agent_type = $at else . end
     | if $name != "" then .tool_input.name = $name else . end
     | if $model != "" then .tool_input.model = $model else . end'
}
gh="$gate/handoff.md"
vt=sdlc-lite:verifier-L3; vn="gate-task-verifier-L3"
run "$rs" "$(gj $vt $vn opus "$gh")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a prepared dispatch (record keyed by stem): exit $rc, want 0"
run "$rs" "$(gj $vt $vn opus "$gh" conductor)" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a prepared dispatch (agent_type conductor): exit $rc, want 0"
run "$rs" "$(gj $vt $vn opus "$gh" "")" SDLC_ROLE=conductor >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a prepared dispatch (SDLC_ROLE=conductor): exit $rc, want 0"
run "$rs" "$(gj sdlc-lite:builder-L2 gate-task-builder-L2-2 sonnet "$gh")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a -k dispatch (gate-task-builder-L2-2): exit $rc, want 0"
run "$rs" "$(gj sdlc-lite:scout-L1 gate-task-scout-L1 haiku "$gh")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a record named <name>.dispatch.json: exit $rc, want 0"
# T-0337: the Agent tool takes only the alias haiku while a record may hold the pinned id; compare by alias.
printf '%s' '{"name":"alias-task-scout-L1","model":"claude-haiku-5-5"}' >"$gate/scout-L1-alias.dispatch.json"
run "$rs" "$(gj sdlc-lite:scout-L1 alias-task-scout-L1 haiku "$gh")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows model haiku against a claude-haiku-5-5 record (T-0337): exit $rc, want 0"
run "$rs" "$(gj sdlc-lite:scout-L1 scout-L1-alias-task sonnet "$gh")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate denies a scout spawn with model sonnet against a haiku record: exit $rc, want 2"
run "$rs" "$(gj sdlc-lite:scout-L1 scout-L1-gate-task sonnet "$gh")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate denies a scout spawn with model sonnet against a haiku alias record: exit $rc, want 2"
run "$rs" "$(gj $vt $vn opus "other/../handoff.md")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate resolves a relative Handoff path against the hook cwd: exit $rc, want 0"
# T-0344: the path is the first token after "Handoff:"; trailing text (even with a slash) is ignored.
run "$rs" "$(gj $vt $vn opus "$gh")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a plain Handoff line (T-0344): exit $rc, want 0"
run "$rs" "$(gj $vt $vn opus "$gh  (frozen, see docs/a/b.md)")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows trailing text on the Handoff line (T-0344): exit $rc, want 0"
# T-0504: a path with spaces travels as a double-quoted locator; the text after the closing quote is ignored.
sp="$gate/with spaces"; mkdir -p "$sp"; : >"$sp/handoff.md"
printf '%s' '{"model":"opus","name":"gate-task-verifier-L3"}' >"$sp/verifier-L3.dispatch.json"
run "$rs" "$(gj $vt $vn opus "\"$sp/handoff.md\"")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows a quoted Handoff path with spaces (T-0504): exit $rc, want 0"
run "$rs" "$(gj $vt $vn opus "\"$sp/handoff.md\" (frozen, see docs/a b.md)")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate ignores text after a quoted Handoff path (T-0504): exit $rc, want 0"
rm -f "$sp/verifier-L3.dispatch.json"
out=$(run "$rs" "$(gj $vt $vn opus "\"$sp/handoff.md\"")"); rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate denies a quoted spaced path with no record (T-0504): exit $rc, want 2"
grep -q "no dispatch record for '$vn' beside $sp/handoff.md" <<<"$out" || fail "spawn gate names the whole spaced path in the missing-record denial (T-0504)"
run "$rs" "$(jq -n --arg cwd "$gate" '{tool_name:"Agent",cwd:$cwd,agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"sdlc-lite:verifier-L3",name:"gate-task-verifier-L3",model:"opus",prompt:"no line here"}}')" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate denies a prompt with no Handoff line (T-0344): exit $rc, want 2"
# A solo dispatch (sdlc-lite:solo-L1|L2|L3, solo_run.py) is gated by its record and model only (T-0287 live defect).
# The 0.21.x names solo-S|M|L are deprecated aliases the gate still accepts for one release (T-0342).
for st in L1 L2 L3 S M L; do
  printf '%s' "{\"subagent_type\":\"sdlc-lite:solo-$st\",\"name\":\"solo-$st-gate-task\",\"model\":\"sonnet\",\"role\":\"solo\"}" >"$gate/solo-$st-gate-task.dispatch.json"
  run "$rs" "$(gj "sdlc-lite:solo-$st" "solo-$st-gate-task" sonnet "$gh")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "spawn gate allows a recorded solo-$st dispatch: exit $rc, want 0"
  run "$rs" "$(gj "sdlc-lite:solo-$st" "solo-$st-gate-task" opus "$gh")" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate denies a solo-$st dispatch with another model: exit $rc, want 2"
  run "$rs" "$(gj "sdlc-lite:solo-$st" "solo-$st-no-record" sonnet "$gh")" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate denies a solo-$st spawn with no dispatch record: exit $rc, want 2"
done
# Negative controls: no other solo name passes condition 1, even with a record.
for st in L4 L0 XL X; do
  printf '%s' "{\"name\":\"solo-$st-gate-task\",\"model\":\"sonnet\"}" >"$gate/solo-$st-gate-task.dispatch.json"
  run "$rs" "$(gj "sdlc-lite:solo-$st" "solo-$st-gate-task" sonnet "$gh")" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate denies sdlc-lite:solo-$st: exit $rc, want 2"
done
# T-0520: the bare role name ui-designer is a role spawn too, so a conductor session cannot start it outside a dispatch.
run "$rs" "$(rsj sdlc-lite:conductor ui-designer)" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate denies the bare role name ui-designer (T-0520): exit $rc, want 2"
# Condition 1: subagent_type is sdlc-lite:<role>-L<n>.
for sub in sdlc-lite:verifier sdlc-lite:verifier-L sdlc-lite:solo sdlc-lite:solo-X sdlc-lite:conductor verifier-L3 sdlc-lite:Verifier-L3; do
  out=$(run "$rs" "$(gj "$sub" $vn opus "$gh")"); rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate condition 1, subagent_type '$sub': exit $rc, want 2"
done
grep -q "sdlc-lite:<role>-L<n>" <<<"$out" || fail "spawn gate condition 1: stderr does not name the required form"
# T-0369: a conductor may spawn the session agent sdlc-lite:messenger (no dispatch record: it is not a pipeline role)
# under the legible name inbox-<repo>-<receiver>; every other name, and every other non-role agent, stays denied.
mj() { gj "$1" "$2" haiku "$gh" "${3-sdlc-lite:conductor}"; }
for nm in inbox-maison-claude inbox-sdlc-lite-codex; do
  run "$rs" "$(mj sdlc-lite:messenger "$nm")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "spawn gate allows sdlc-lite:messenger named '$nm' (T-0369): exit $rc, want 0"
done
run "$rs" "$(mj sdlc-lite:messenger inbox-maison-claude conductor)" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows the messenger for agent_type conductor (T-0369): exit $rc, want 0"
run "$rs" "$(mj sdlc-lite:messenger inbox-maison-claude "")" SDLC_ROLE=conductor >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate allows the messenger under SDLC_ROLE=conductor (T-0369): exit $rc, want 0"
for nm in "" messenger poller inbox inbox- Inbox-maison-claude "inbox-bad name" inbox-a/b verifier-L3; do
  out=$(run "$rs" "$(mj sdlc-lite:messenger "$nm")"); rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate denies the messenger named '$nm' (T-0369): exit $rc, want 2"
done
grep -q "inbox-<repo>-<receiver>" <<<"$out" || fail "spawn gate: the messenger name denial does not name inbox-<repo>-<receiver>"
for sub in sdlc-lite:conductor sdlc-lite:solo sdlc-lite:solo-L4 sdlc-lite:messenger-L1 sdlc-lite:verifier sdlc-lite:builder-L3; do
  run "$rs" "$(mj "$sub" inbox-maison-claude)" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate: '$sub' named inbox-maison-claude still denies beside the messenger allowance (T-0369): exit $rc, want 2"
done
run "$rs" "$(mj sdlc-lite:messenger "inbox-maison-claude" "")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate: a non-conductor session passes a messenger spawn (T-0369): exit $rc, want 0"
# Condition 2: name is <ticket>-<role>-L<n>[-<k>] for the same <role>-L<n> (T-0363); the old <role>-L<n>-<slug> form is refused.
for nm in "" verifier-L3 verifier-L3- -verifier-L3 builder-L3-gate-task verifier-L3-gate-task verifier-L2-gate-task verifier-gate-task gate-task-builder-L3 gate-task-verifier-L2 gate-task-verifier-L3-x "bad name-verifier-L3" "a/b-verifier-L3"; do
  out=$(run "$rs" "$(gj $vt "$nm" opus "$gh")"); rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate condition 2, name '$nm': exit $rc, want 2"
done
grep -q "does not match" <<<"$out" || fail "spawn gate condition 2: stderr lacks the name rule"
# Condition 3: a dispatch record beside the named handoff.
out=$(run "$rs" "$(gj $vt no-record-verifier-L3 opus "$gh")"); rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate condition 3, no record naming the agent: exit $rc, want 2"
grep -q "no dispatch record" <<<"$out" || fail "spawn gate condition 3: stderr lacks 'no dispatch record'"
run "$rs" "$(gj $vt $vn opus "$gate/other/handoff.md")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate condition 3, handoff in a directory with no record: exit $rc, want 2"
run "$rs" "$(gj $vt $vn opus "$wtmp/missing/handoff.md")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate condition 3, handoff directory missing: exit $rc, want 2"
no_handoff=$(jq -n --arg name $vn '{tool_name:"Agent",agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"sdlc-lite:verifier-L3",name:$name,model:"opus",prompt:"Artifacts dir: x"}}')
out=$(run "$rs" "$no_handoff"); rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate condition 3, prompt with no Handoff line: exit $rc, want 2"
grep -q "Handoff" <<<"$out" || fail "spawn gate condition 3: stderr lacks the Handoff line rule"
# Condition 4: the call's model equals the dispatch model.
for m in sonnet fable haiku OPUS ""; do
  out=$(run "$rs" "$(gj $vt $vn "$m" "$gh")"); rc=$?
  [[ $rc -eq 2 ]] || fail "spawn gate condition 4, model '${m:-unset}' against opus: exit $rc, want 2"
done
grep -q "dispatch model 'opus'" <<<"$out" || fail "spawn gate condition 4: stderr lacks the dispatch model"
printf '%s' '{"subagent_type":"sdlc-lite:planner-L1","name":"gate-task-planner-L1","role":"planner"}' >"$gate/planner-L1.dispatch.json"
run "$rs" "$(gj sdlc-lite:planner-L1 gate-task-planner-L1 opus "$gh")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate condition 4, a record with no model: exit $rc, want 2"
run "$rs" "$(gj sdlc-lite:planner-L1 gate-task-planner-L1 "" "$gh")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "spawn gate condition 4, no model on the call or in the record: exit $rc, want 2"
# The same denied calls pass outside a conductor session: the gate acts only for the conductor.
run "$rs" "$(gj $vt $vn sonnet "$gh" "")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate: a wrong-model spawn from a non-conductor session: exit $rc, want 0"
run "$rs" "$(gj sdlc-lite:verifier bad-name sonnet "$gh" sdlc-lite:builder-L3)" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "spawn gate: a spawn from a builder sub-agent session: exit $rc, want 0"
# Forks: verifier- and plan-reviewer- names are denied outright; any other fork needs a Fork reason line.
# fkj <name or empty> <prompt>: the JSON of one conductor fork.
fkj() {
  jq -n --arg name "$1" --arg prompt "$2" \
    '{tool_name:"Agent",agent_type:"sdlc-lite:conductor",tool_input:{subagent_type:"fork",description:"d",prompt:$prompt}}
     | if $name != "" then .tool_input.name = $name else . end'
}
for nm in verifier-L3-gate-task verifier-L1-x plan-reviewer-L1-gate-task plan-reviewer-L2-x 0153-verifier-L3 0153-s2-plan-reviewer-L1-2; do
  out=$(run "$rs" "$(fkj $nm $'Fork reason: need the whole thread\nrest')"); rc=$?
  [[ $rc -eq 2 ]] || fail "fork named '$nm' with a Fork reason: exit $rc, want 2"
  grep -q independent <<<"$out" || fail "fork named '$nm': stderr lacks the independence reason"
done
for nm in builder-L3-gate-task scout-L1-x planner-L3-x ""; do
  out=$(run "$rs" "$(fkj "$nm" "just do it")"); rc=$?
  [[ $rc -eq 2 ]] || fail "fork '$nm' with no Fork reason: exit $rc, want 2"
  grep -q "Fork reason" <<<"$out" || fail "fork '$nm' with no Fork reason: stderr lacks 'Fork reason'"
  run "$rs" "$(fkj "$nm" $'Fork reason:\nrest')" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "fork '$nm' with an empty Fork reason: exit $rc, want 2"
  run "$rs" "$(fkj "$nm" "the Fork reason: is inline, not a line start")" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "fork '$nm' with an inline Fork reason: exit $rc, want 2"
  run "$rs" "$(fkj "$nm" "Fork reason: needs this thread's context")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "fork '$nm' with a Fork reason first line: exit $rc, want 0"
  run "$rs" "$(fkj "$nm" $'Handoff: x\nFork reason: needs this thread\'s context')" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "fork '$nm' with a Fork reason line: exit $rc, want 0"
done
run "$rs" "$(fkj verifier-L3-x "no reason")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "fork verifier-: exit $rc, want 2"
jq -n '{tool_name:"Agent",tool_input:{subagent_type:"fork",name:"verifier-L3-x",prompt:"x"}}' >"$wtmp/fork-noconductor.json"
run "$rs" "$(cat "$wtmp/fork-noconductor.json")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "fork verifier- outside a conductor session: exit $rc, want 0"

# warn-handoff-edit.sh: warn mode allows and logs; deny mode blocks; everything else passes silently.
mkdir -p "$wtmp/live" "$wtmp/idle" "$wtmp/other"
: >"$wtmp/live/handoff.md"; : >"$wtmp/idle/handoff.md"; : >"$wtmp/live/notes.md"; : >"$wtmp/other/handoff.md"
: >"$wtmp/live/planner-L3.running"; : >"$wtmp/other/builder-L1.running"; mkdir -p "$wtmp/sep" && : >"$wtmp/sep/builder-L1.running"
wj() { printf '{"tool_name":"%s","tool_input":{"%s":"%s"}}' "${3:-Edit}" "${4:-file_path}" "$1"; }
out=$(run "$wh" "$(wj "$wtmp/live/handoff.md")"); rc=$?
[[ $rc -eq 0 ]] || fail "handoff-edit warn: exit $rc, want 0"
grep -q "handoff freeze" <<<"$out" || fail "handoff-edit warn: stderr lacks the freeze warning"
grep -q "planner-L3" <<<"$out" || fail "handoff-edit warn: stderr does not name the running role"
[[ "$(grep -c "edited while planner-L3 ran" "$wtmp/live/stale-edits.log")" == 1 ]] || fail "handoff-edit warn: log line missing or repeated"
run "$wh" "$(wj "$wtmp/live/handoff.md" x Write)" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "handoff-edit warn via Write: exit $rc, want 0"
run "$wh" "$(wj "$wtmp/live/handoff.md" x NotebookEdit notebook_path)" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "handoff-edit warn via NotebookEdit: exit $rc, want 0"
[[ "$(wc -l <"$wtmp/live/stale-edits.log" | tr -d ' ')" == 3 ]] || fail "handoff-edit: three warned edits did not log three lines"
out=$(run "$wh" "$(wj "$wtmp/live/handoff.md")" SDLC_HANDOFF_EDIT_MODE=deny); rc=$?
[[ $rc -eq 2 ]] || fail "handoff-edit deny: exit $rc, want 2 (negative control: deny turns the same case into a denial)"
grep -q "handoff freeze" <<<"$out" || fail "handoff-edit deny: stderr lacks the freeze message"
out=$(run "$wh" "$(wj "$wtmp/idle/handoff.md")"); rc=$?
[[ $rc -eq 0 && -z "$out" && ! -e "$wtmp/idle/stale-edits.log" ]] || fail "handoff-edit: no .running beside the handoff warned or logged (rc=$rc)"
before=$(wc -l <"$wtmp/live/stale-edits.log" | tr -d ' ')
[[ "$before" == 4 ]] || fail "handoff-edit: the denied attempt was not logged (log has $before lines, want 4)"
out=$(run "$wh" "$(wj "$wtmp/live/notes.md")"); rc=$?
[[ $rc -eq 0 && -z "$out" ]] || fail "handoff-edit: another file name warned (rc=$rc)"
[[ "$(wc -l <"$wtmp/live/stale-edits.log" | tr -d ' ')" == "$before" ]] || fail "handoff-edit: another file name changed the log"
out=$(run "$wh" "$(wj "$wtmp/other/handoff.md")" ); rc=$?
[[ $rc -eq 0 && "$out" == *builder-L1* ]] || fail "handoff-edit: a different handoff's own .running was not used (rc=$rc)"
out=$(run "$wh" '{"tool_name":"Edit","tool_input":{}}'); rc=$?
[[ $rc -eq 0 && -z "$out" ]] || fail "handoff-edit: missing file_path was not a silent pass (rc=$rc)"

# warn-handoff-edit.sh with a real prepared attempt (T-0505): dispatch.py prepare writes the running marker, so the freeze
# holds with no hand-made .running file; record (completed or failed) and recover (a dead owner) release it; recover leaves
# an attempt that another live run owns. One throwaway repo and task folder per case (a live attempt refuses a second
# prepare in its folder, and the hook logs a denied edit too).
scripts="$(cd "$(dirname "$0")" && pwd)"
pa="handoff-edit prepared attempt"
# pd <repo> <owner pid or ""> <dispatch.py arguments>: dispatch.py run inside <repo> with none of the caller's variables.
pd() {
  local repo="$1" owner="$2"; shift 2
  ( cd "$repo" && env -i PATH="$PATH" HOME="$HOME" ${owner:+SDLC_DISPATCH_PARENT_PID="$owner"} python3 "$scripts/dispatch.py" "$@" )
}
# prepared <case> [owner pid]: a fresh repo with one commit and one task folder, then a real prepare scout L1.
# Sets pr (the repo) and pt (the task folder).
prepared() {
  pr="$wtmp/prepared-$1"; pt="$pr/.sdlc/task"
  git init -q "$pr" && git -C "$pr" -c user.name=t -c user.email=t@example.invalid -c commit.gpgsign=false commit --allow-empty -qm seed \
    || fail "$pa $1: could not build the throwaway repo"
  mkdir -p "$pt" && printf '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n' >"$pt/handoff.md"
  pd "$pr" "${2:-}" prepare scout L1 .sdlc/task/handoff.md >/dev/null 2>"$pr.err" || fail "$pa $1: dispatch.py prepare failed: $(cat "$pr.err")"
}
# frozen: the hook's exit code for an edit of the prepared handoff in deny mode; its stderr is left in $out.
frozen() { out=$(run "$wh" "$(wj "$pt/handoff.md")" SDLC_HANDOFF_EDIT_MODE=deny); }

prepared warn
out=$(run "$wh" "$(wj "$pt/handoff.md")" -u SDLC_HANDOFF_EDIT_MODE); rc=$?
[[ $rc -eq 0 ]] || fail "$pa warn: exit $rc, want 0"
grep -qF "handoff freeze (warning)" <<<"$out" || fail "$pa warn: stderr lacks the freeze warning (prepare left no running marker)"
grep -q "scout-L1" <<<"$out" || fail "$pa warn: stderr does not name scout-L1"
[[ "$(grep -c "edited while scout-L1 ran" "$pt/stale-edits.log" 2>/dev/null)" == 1 ]] || fail "$pa warn: stale-edits.log does not hold exactly one line"

prepared deny
frozen; rc=$?
[[ $rc -eq 2 ]] || fail "$pa deny: exit $rc, want 2"

prepared completed
frozen; rc=$?
[[ $rc -eq 2 ]] || fail "$pa completed: exit $rc before record, want 2"
pd "$pr" "" record .sdlc/task/scout-L1.dispatch.json >/dev/null 2>&1 \
  < <(printf '## Map\nNone\n\n## Entry points\nNone\n\n## Not found\nNone\n\n## Carry forward\nNone\n'); rc=$?
[[ $rc -eq 0 && "$(jq -r .status "$pt/scout-L1.attempt.json")" == completed ]] || fail "$pa completed: dispatch.py record exit $rc, want 0 and a completed attempt"
frozen; rc=$?
[[ $rc -eq 0 && -z "$out" ]] || fail "$pa completed: the handoff stayed frozen after record (rc=$rc)"

prepared failed
frozen; rc=$?
[[ $rc -eq 2 ]] || fail "$pa failed: exit $rc before record, want 2"
pd "$pr" "" record .sdlc/task/scout-L1.dispatch.json >/dev/null 2>&1 < <(printf 'API Error: connection reset by peer\n'); rc=$?
[[ $rc -eq 1 && "$(jq -r .status "$pt/scout-L1.attempt.json")" == failed ]] || fail "$pa failed: dispatch.py record exit $rc, want 1 and a failed attempt"
frozen; rc=$?
[[ $rc -eq 0 && -z "$out" ]] || fail "$pa failed: the handoff stayed frozen after a failed record (rc=$rc)"

(exit 0) & gone=$!; wait "$gone"
prepared recovered "$gone"
frozen; rc=$?
[[ $rc -eq 2 ]] || fail "$pa recovered: exit $rc before recover, want 2"
rec=$(pd "$pr" "" recover "$pt" 2>&1)
grep -qF "marked interrupted" <<<"$rec" || fail "$pa recovered: dispatch.py recover did not mark the dead-owner attempt interrupted: $rec"
frozen; rc=$?
[[ $rc -eq 0 && -z "$out" ]] || fail "$pa recovered: the handoff stayed frozen after recover (rc=$rc)"

# Negative control for recovery: $$ is this suite, alive and older than the attempt, so the attempt belongs to a live run.
prepared live "$$"
rec=$(pd "$pr" "" recover "$pt" 2>&1)
grep -qF "no orphaned attempts" <<<"$rec" || fail "$pa live: dispatch.py recover touched an attempt whose owner is alive: $rec"
[[ "$(jq -r '"\(.status) \(.parent_pid)"' "$pt/scout-L1.attempt.json")" == "running $$" ]] || fail "$pa live: the attempt is no longer running under pid $$"
frozen; rc=$?
[[ $rc -eq 2 ]] || fail "$pa live: exit $rc after recover, want 2 (a live attempt keeps the freeze)"

# Role resolution (hooks/_role.sh): SDLC_ROLE, else the sub-agent's agent_type with the sdlc-lite:
# prefix and the -L<n> or solo tier suffix removed. Session agents and non-SDLC agents have no role.
rr() { ( unset SDLC_ROLE; . "$hooks/_role.sh"; sdlc_role "$1" ); }
# rj <agent_type or empty> <command>: the JSON of one Bash call, with agent_type only when given.
rj() {
  jq -n --arg at "$1" --arg c "$2" '{tool_name:"Bash",tool_input:{command:$c}} | if $at != "" then .agent_type = $at else . end'
}
while IFS='|' read -r at want; do
  got=$(rr "$(rj "$at" x)")
  [[ "$got" == "$want" ]] || fail "_role.sh: agent_type '$at' resolved '$got', want '$want'"
done <<'CASES'
sdlc-lite:builder-L3|builder
sdlc-lite:verifier-L1|verifier
sdlc-lite:plan-reviewer-L2|plan-reviewer
sdlc-lite:scout-L1|scout
sdlc-lite:ui-designer-L1|ui-designer
sdlc-lite:solo-L1|solo
sdlc-lite:solo-L2|solo
sdlc-lite:solo-L3|solo
sdlc-lite:solo-M|solo
sdlc-lite:solo-S|solo
sdlc-lite:solo-L|solo
sdlc-lite:solo|solo
sdlc-lite:planner|planner
builder|builder
verifier-L2|verifier
sdlc-lite:conductor|
conductor|
sdlc-lite:messenger|
general-purpose|
Explore|
harness:agent-checker|
other:builder-L3|
|
CASES
[[ "$(rr '{"tool_name":"Bash"}')" == "" ]] || fail "_role.sh: a payload with no agent_type resolved a role"
[[ "$(rr 'not json agent_type')" == "" ]] || fail "_role.sh: unparsable input resolved a role"
[[ "$( . "$hooks/_role.sh"; SDLC_ROLE=verifier sdlc_role "$(rj sdlc-lite:builder-L3 x)" )" == verifier ]] || fail "_role.sh: SDLC_ROLE must win over agent_type"
[[ "$( . "$hooks/_role.sh"; SDLC_ROLE=solo sdlc_role '{}' )" == solo ]] || fail "_role.sh: SDLC_ROLE alone must resolve"

# The five role hooks resolve the role through _role.sh. For each: a sub-agent role input still
# blocks the same defect SDLC_ROLE blocked (stderr names the role), and an input with no role,
# an interactive conductor, and a non-SDLC agent pass (negative controls).
pushc=$(printf 'git %s origin main' push)
pkc="$pkw -f vite"
dsc="$fw / -name x"
fmtc="npm run format"
while IFS='|' read -r at rname; do
  for spec in "$pub|$pushc" "$pk|$pkc" "$ds|$dsc"; do
    hook="${spec%%|*}"; c="${spec#*|}"
    out=$(run "$hook" "$(rj "$at" "$c")"); rc=$?
    [[ $rc -eq 2 ]] || fail "$(basename "$hook") blocks '$c' for sub-agent $at: exit $rc, want 2"
    grep -q "role '$rname'" <<<"$out" || fail "$(basename "$hook") for $at: stderr does not name role '$rname'"
  done
done <<'CASES'
sdlc-lite:builder-L3|builder
sdlc-lite:verifier-L2|verifier
sdlc-lite:plan-reviewer-L1|plan-reviewer
sdlc-lite:solo-L2|solo
sdlc-lite:solo-M|solo
CASES
out=$(run "$rf" "$(rj sdlc-lite:builder-L2 "$fmtc")"); rc=$?
[[ $rc -eq 2 ]] || fail "block-repo-format blocks '$fmtc' for sub-agent sdlc-lite:builder-L2: exit $rc, want 2"
grep -q "role 'builder'" <<<"$out" || fail "block-repo-format for sdlc-lite:builder-L2: stderr does not name the role"
for at in "" sdlc-lite:conductor conductor general-purpose Explore harness:agent-checker sdlc-lite:messenger; do
  for spec in "$pub|$pushc" "$pk|$pkc" "$ds|$dsc" "$rf|$fmtc"; do
    hook="${spec%%|*}"; c="${spec#*|}"
    run "$hook" "$(rj "$at" "$c")" >/dev/null; rc=$?
    [[ $rc -eq 0 ]] || fail "$(basename "$hook") passes '$c' with agent_type '${at:-none}': exit $rc, want 0"
  done
done
for at in sdlc-lite:verifier-L2 sdlc-lite:solo-L2 sdlc-lite:solo-M sdlc-lite:planner-L1; do
  run "$rf" "$(rj "$at" "$fmtc")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-repo-format passes '$fmtc' for non-builder sub-agent $at: exit $rc, want 0"
done
# SDLC_ROLE wins over agent_type: a verifier role with a builder agent_type is not a builder, and a builder role is.
run "$rf" "$(rj sdlc-lite:builder-L3 "$fmtc")" SDLC_ROLE=verifier >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-repo-format: SDLC_ROLE=verifier with a builder agent_type: exit $rc, want 0"
run "$rf" "$(rj sdlc-lite:verifier-L1 "$fmtc")" SDLC_ROLE=builder >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-repo-format: SDLC_ROLE=builder with a verifier agent_type: exit $rc, want 2"
# The sub-agent role also gets the stray-worktree rule. With no SDLC_TMP_WORKTREES a sub-agent may add
# a detached worktree only under <git toplevel>/.worktrees/tmp, the parent of its dispatch tmp prefix.
srepo="$wtmp/repo"; mkdir -p "$srepo" "$wtmp/nogit"; git -C "$srepo" init -q
stop=$(git -C "$srepo" rev-parse --show-toplevel)
# swj <agent_type or empty> <command> [cwd]: the JSON of one Bash call with a cwd.
swj() {
  jq -n --arg at "$1" --arg c "$2" --arg cwd "${3:-$stop}" \
    '{tool_name:"Bash",cwd:$cwd,tool_input:{command:$c}} | if $at != "" then .agent_type = $at else . end'
}
wtp="$stop/.worktrees/tmp/verifier-L1-t"
for c in "git worktree add -b x \"$wtp/w\" HEAD" "git worktree add --detach /tmp/y HEAD" \
  "git worktree add --detach \"$stop/.worktrees/other/w\" HEAD" "git worktree add --detach \"$stop/.worktrees/tmp/../w\" HEAD" \
  "git worktree add \"$wtp/w\" HEAD" "git worktree add --detach \"$stop/.worktrees/tmp\" HEAD" \
  "bash -c \"git worktree add /tmp/y HEAD\""; do
  out=$(run "$sw" "$(swj sdlc-lite:verifier-L1 "$c")"); rc=$?
  [[ $rc -eq 2 ]] || fail "block-stray-worktree denies '$c' for sub-agent sdlc-lite:verifier-L1: exit $rc, want 2"
  grep -q "role 'verifier'" <<<"$out" || fail "block-stray-worktree '$c' for sub-agent: stderr does not name the role"
done
for c in "git worktree add --detach \"$wtp/w\" HEAD" "git worktree add -d \"$wtp/w\" HEAD" \
  "git worktree add --detach .worktrees/tmp/verifier-L1-t/w HEAD" "git worktree list" "git worktree remove \"$wtp/w\""; do
  run "$sw" "$(swj sdlc-lite:verifier-L1 "$c")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-stray-worktree allows '$c' for sub-agent sdlc-lite:verifier-L1: exit $rc, want 0"
done
run "$sw" "$(swj sdlc-lite:verifier-L1 "git worktree add --detach \"$wtp/w\" HEAD" "$wtmp/nogit")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-stray-worktree denies a sub-agent outside a git work tree: exit $rc, want 2"
for at in "" sdlc-lite:conductor general-purpose; do
  run "$sw" "$(swj "$at" "git worktree add -b x /tmp/y HEAD")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-stray-worktree passes agent_type '${at:-none}' (negative control): exit $rc, want 0"
done

# block-role-write.sh: a read-only role sub-agent may Write only its dispatch result path (the
# "result" of a <stem>.dispatch.json beside it); Edit and NotebookEdit and any other Write are denied;
# the builder, solo, the conductor, and a session with no role are not restricted.
wd="$wtmp/write"; mkdir -p "$wd/sub"
printf '%s' "$(jq -n --arg r "$wd/verifier-L3.md" '{subagent_type:"sdlc-lite:verifier-L3",role:"verifier",result:$r}')" >"$wd/verifier-L3.dispatch.json"
printf '%s' "$(jq -n --arg r "$wd/planner-L1.md" '{subagent_type:"sdlc-lite:planner-L1",role:"planner",result:$r}')" >"$wd/planner-L1.dispatch.json"
# wrj <agent_type or empty> <tool> <path>: the JSON of one file-edit call.
wrj() {
  jq -n --arg at "$1" --arg t "$2" --arg p "$3" \
    '{tool_name:$t,tool_input:{file_path:$p,content:"x"}} | if $at != "" then .agent_type = $at else . end'
}
run "$wrh" "$(wrj sdlc-lite:verifier-L3 Write "$wd/verifier-L3.md")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-role-write allows a verifier Write to its result path: exit $rc, want 0"
run "$wrh" "$(wrj sdlc-lite:planner-L1 Write "$wd/planner-L1.md")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-role-write allows a planner Write to its result path: exit $rc, want 0"
run "$wrh" "$(wrj "" Write "$wd/verifier-L3.md")" SDLC_ROLE=verifier >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-role-write allows a SDLC_ROLE=verifier Write to its result path: exit $rc, want 0"
for spec in "sdlc-lite:verifier-L3|Write|$wd/notes.md" "sdlc-lite:verifier-L3|Write|$wd/other.md" \
  "sdlc-lite:verifier-L3|Write|$wd/sub/verifier-L3.md" "sdlc-lite:verifier-L3|Write|/tmp/x.md" \
  "sdlc-lite:verifier-L3|Write|$wd/handoff.md" "sdlc-lite:verifier-L3|Write|verifier-L3.md" \
  "sdlc-lite:verifier-L3|Write|$wd/sub/../verifier-L3.md" "sdlc-lite:verifier-L3|Write|$wd/verifier-L3.dispatch.json" \
  "sdlc-lite:verifier-L3|Write|" "sdlc-lite:planner-L1|Write|$wd/verifier-L3.md" \
  "sdlc-lite:verifier-L3|Edit|$wd/verifier-L3.md" "sdlc-lite:verifier-L3|Edit|$wd/notes.md" \
  "sdlc-lite:scout-L1|NotebookEdit|$wd/n.ipynb" "sdlc-lite:plan-reviewer-L1|Write|$wd/plan-review.md" \
  "sdlc-lite:researcher-L2|Write|/etc/x" "sdlc-lite:architect-L1|Write|$wd/decompose/m.json" \
  "sdlc-lite:archaeologist-L1|Write|$wd/x.md" "sdlc-lite:filer-L1|Write|$wd/x.md"; do
  IFS='|' read -r at tool path <<<"$spec"
  out=$(run "$wrh" "$(wrj "$at" "$tool" "$path")"); rc=$?
  [[ $rc -eq 2 ]] || fail "block-role-write denies $at $tool '$path': exit $rc, want 2"
  rn=${at#sdlc-lite:}; rn=${rn%-L*}
  grep -q "role '$rn'" <<<"$out" || fail "block-role-write $at $tool '$path': stderr does not name the role"
done
run "$wrh" "$(wrj "" Write "$wd/notes.md")" SDLC_ROLE=planner >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-role-write denies a SDLC_ROLE=planner Write elsewhere: exit $rc, want 2"
# Not restricted (negative controls): the builder, solo, ui-designer, the conductor, other agents, no role, other tools.
for spec in "sdlc-lite:builder-L3|Write|$wd/notes.md" "sdlc-lite:builder-L3|Edit|$wd/notes.md" \
  "sdlc-lite:builder-L3|NotebookEdit|$wd/n.ipynb" "sdlc-lite:builder-L3|Write|/tmp/x.md" \
  "sdlc-lite:solo-L2|Write|$wd/notes.md" "sdlc-lite:solo-L2|Edit|$wd/notes.md" "sdlc-lite:solo-M|Write|$wd/notes.md" \
  "sdlc-lite:ui-designer-L1|Edit|$wd/notes.md" "sdlc-lite:ui-designer-L1|Write|$wd/notes.md" \
  "sdlc-lite:conductor|Write|$wd/notes.md" "general-purpose|Write|$wd/notes.md" \
  "|Write|$wd/notes.md" "|Edit|$wd/notes.md" "sdlc-lite:verifier-L3|Read|$wd/notes.md" "sdlc-lite:verifier-L3|Bash|$wd/notes.md"; do
  IFS='|' read -r at tool path <<<"$spec"
  run "$wrh" "$(wrj "$at" "$tool" "$path")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-role-write passes ${at:-no role} $tool '$path': exit $rc, want 0"
done
# A record whose result is another path does not unlock this one.
printf '%s' "$(jq -n --arg r "$wd/elsewhere.md" '{subagent_type:"sdlc-lite:verifier-L3",role:"verifier",result:$r}')" >"$wd/stale-L3.dispatch.json"
run "$wrh" "$(wrj sdlc-lite:verifier-L3 Write "$wd/stale-L3.md")" >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-role-write: a record whose result is another path unlocked this path: exit $rc, want 2"

# block-role-rm.sh (T-0538): a read-only role removes files only under its throwaway prefix. Allowed under it
# (and the allow decision is printed when the command is only rm and cd), refused outside it, and every
# other role or no role passes untouched.
rmp=/r/.worktrees/tmp/verifier-L1-x
rmj() { jq -n --arg c "$1" --arg a "$2" '{tool_name:"Bash",tool_input:{command:$c},agent_type:$a,cwd:"/nonexistent"}'; }
rmenv=(SDLC_ROLE=verifier SDLC_TMP_WORKTREES="$rmp")
for c in "rm $rmp/out.txt" "rm -rf $rmp/scratch" "rm -f -- $rmp/a.txt $rmp/b.txt" "rm -rf \"$rmp/scratch dir\"" \
  "rm -rf \$SDLC_TMP_WORKTREES/scratch" "rm -rf \${SDLC_TMP_WORKTREES}/scratch" "cd /r && rm -rf $rmp/scratch" \
  "cd $rmp && rm -f out.txt" "/bin/rm -f $rmp/out.txt" "sudo rm $rmp/out.txt" "rmdir $rmp/empty" "unlink $rmp/out.txt" \
  "rm $rmp/a.txt; rm $rmp/b.txt" "ls $rmp && rm $rmp/out.txt" "echo rm /etc/passwd" "git status" "ls -la /tmp"; do
  out=$(run "$rmh" "$(rmj "$c" "")" "${rmenv[@]}"); rc=$?
  [[ $rc -eq 0 ]] || fail "block-role-rm allows '$c': exit $rc, want 0 (stderr: $out)"
done
for c in "rm /etc/passwd" "rm -rf /tmp/x" "rm $rmp/../other/x" "rm $rmp" "rm $rmp/" "rm -rf $rmp/ok /tmp/bad" "rm out.txt" \
  "rm -rf \$HOME/x" "rm -rf ~/x" "rm -rf \$TMPDIR/x" "cd /tmp && rm -f out.txt" "cd x && rm -f $rmp/ok /etc/y" \
  "rm -rf /r/.worktrees/tmp/verifier-L1-xx/a" "rm -rf /r/.worktrees/other/a" "ls && rm /etc/x" "rm $rmp/a.txt; rm /etc/x"; do
  out=$(run "$rmh" "$(rmj "$c" "")" "${rmenv[@]}"); rc=$?
  [[ $rc -eq 2 ]] || fail "block-role-rm denies '$c': exit $rc, want 2"
  grep -q verifier <<<"$out" || fail "block-role-rm '$c': stderr lacks the role"
done
# The allow decision (stdout) is printed only when the whole command is rm and cd.
rma=$(env -u SDLC_ROLE -u SDLC_TMP_WORKTREES "${rmenv[@]}" "$rmh" < <(rmj "rm -rf $rmp/scratch" ""))
jq -e '.hookSpecificOutput.permissionDecision == "allow"' <<<"$rma" >/dev/null 2>&1 || fail "block-role-rm: rm under the prefix printed no allow decision: '$rma'"
rma=$(env -u SDLC_ROLE -u SDLC_TMP_WORKTREES "${rmenv[@]}" "$rmh" < <(rmj "rm -rf $rmp/scratch && curl x" ""))
[[ -z "$rma" ]] || fail "block-role-rm: a command with more than rm and cd printed a decision: '$rma'"
# A sub-agent has no prefix variable: the prefix is the git toplevel of its cwd plus /.worktrees/tmp.
rmrepo="$wtmp/rmrepo"; mkdir -p "$rmrepo"; git -C "$rmrepo" init -q
rmtop=$(git -C "$rmrepo" rev-parse --show-toplevel)
rmsub() { jq -n --arg c "$1" --arg cwd "$rmrepo" '{tool_name:"Bash",tool_input:{command:$c},agent_type:"sdlc-lite:verifier-L1",cwd:$cwd}'; }
run "$rmh" "$(rmsub "rm -rf $rmtop/.worktrees/tmp/verifier-L1-x/scratch")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-role-rm allows a verifier sub-agent rm under the repo tmp prefix: exit $rc, want 0"
for c in "rm -rf $rmtop/src" "rm -rf $rmtop/.worktrees/other/x" "rm -rf /tmp/x"; do
  run "$rmh" "$(rmsub "$c")" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "block-role-rm denies a verifier sub-agent '$c': exit $rc, want 2"
done
# No prefix at all: every rm is denied. Other roles and no role pass.
run "$rmh" "$(rmj "rm -rf /r/.worktrees/tmp/x/y" "")" SDLC_ROLE=verifier >/dev/null; rc=$?
[[ $rc -eq 2 ]] || fail "block-role-rm with no prefix: exit $rc, want 2"
for env1 in SDLC_ROLE=builder SDLC_ROLE=solo SDLC_ROLE=conductor SDLC_ROLE=; do
  run "$rmh" "$(rmj "rm -rf /etc/x" "")" "$env1" SDLC_TMP_WORKTREES="$rmp" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-role-rm passes '$env1': exit $rc, want 0"
done
for at in sdlc-lite:solo-L2 sdlc-lite:builder-L2 sdlc-lite:conductor general-purpose ""; do
  run "$rmh" "$(rmj "rm -rf /etc/x" "$at")" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-role-rm passes agent '${at:-no role}': exit $rc, want 0"
done
for at in sdlc-lite:verifier-L1 sdlc-lite:scout-L1 sdlc-lite:planner-L2; do
  run "$rmh" "$(rmj "rm -rf /etc/x" "$at")" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "block-role-rm denies agent '$at' with no prefix: exit $rc, want 2"
done

# Large commands: each Bash hook must finish a 20 KB heredoc command in under 2 seconds and
# keep blocking. Bash 3.2 made ${cmd//[class]/} quadratic (40+ s at 8 KB). One positive and one
# negative control per hook: the denied tail still exits 2, the harmless tail exits 0.
perf=$(python3 - "$hooks" <<'PYEOF'
import json, os, subprocess, sys, time
hooks = sys.argv[1]
body = "\n".join(f"echo line {i} 'quoted text' \"dq\" done C:\\tmp\\row{i}" for i in range(600))
cases = [  # hook, role, tail, wanted exit
    ("block-pattern-kill.sh", "solo", "git status", 0), ("block-pattern-kill.sh", "solo", "pkill -f x", 2),
    ("block-disk-scan.sh", "solo", "ls -la", 0), ("block-disk-scan.sh", "solo", "find / -name x", 2),
    ("block-stray-worktree.sh", "solo", "git status", 0), ("block-stray-worktree.sh", "solo", "git worktree add -b x /tmp/y", 2),
    ("block-publish.sh", "solo", "git status", 0), ("block-publish.sh", "solo", "git push origin x", 2),
    ("block-repo-format.sh", "builder", "ls", 0), ("block-repo-format.sh", "builder", "npm run format", 2),
]
bad = []
for hook, role, tail, want in cases:
    cmd = "cat > /tmp/x.txt <<'EOF2'\n" + body + "\nEOF2\n" + tail
    env = {k: v for k, v in os.environ.items() if k not in ("SDLC_ROLE", "SDLC_HEADLESS", "SDLC_TMP_WORKTREES")}
    env["SDLC_ROLE"] = role
    try:
        rc = subprocess.run(["bash", os.path.join(hooks, hook)],
                            input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
                            text=True, capture_output=True, timeout=2, env=env).returncode
    except subprocess.TimeoutExpired:
        rc = "timeout>2s"
    if rc != want:
        bad.append(f"{hook} [{tail}] exit {rc}, want {want}")
print("; ".join(bad))
PYEOF
)
[[ -z "$perf" ]] || fail "large 20 KB command: $perf"

echo "hook selftest: PASS"
