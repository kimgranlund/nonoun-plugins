#!/usr/bin/env bash
# Selftest for the PreToolUse hooks (Bash and Agent): block-background.sh denies Bash
# run_in_background, and Agent unless run_in_background is false, in a headless session (SDLC_ROLE set or SDLC_HEADLESS=1) and passes everything else; block-publish.sh,
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
# mention, and every other role or no role.
# Publish phrases and kill-pattern words are built with printf so this file never holds one
# as a command.
# Never inherits the caller's SDLC_ROLE/SDLC_HEADLESS/SDLC_TMP_WORKTREES.
# Prints "hook selftest: PASS" or "hook selftest: FAIL: <case>" and exits non-zero on failure.
set -uo pipefail

hooks="$(cd "$(dirname "$0")/../hooks" && pwd)"
bg="$hooks/block-background.sh"
pub="$hooks/block-publish.sh"
pk="$hooks/block-pattern-kill.sh"
sw="$hooks/block-stray-worktree.sh"
rf="$hooks/block-repo-format.sh"

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
  "git worktree add --detach \"$tw\" HEAD"; do
  run "$sw" "$(pj "$c")" "${swenv[@]}" >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "block-stray-worktree denies '$c': exit $rc, want 2"
done
out=$(run "$sw" "$(pj "git worktree add --detach /r/x HEAD")" SDLC_ROLE=conductor); rc=$?
[[ $rc -eq 2 ]] || fail "block-stray-worktree denies with SDLC_TMP_WORKTREES unset: exit $rc, want 2"
grep -q conductor <<<"$out" || fail "block-stray-worktree prefix unset: stderr lacks the role"
for c in "git worktree add --detach \"$tw/x\" HEAD" "git worktree add \"\${SDLC_TMP_WORKTREES}/base\" HEAD" \
  "git worktree add --detach /r/.worktrees/tmp/builder-1/x HEAD" \
  "git worktree remove --force \"$tw/x\"" "git worktree list" "grep -n \"git worktree add\" f"; do
  run "$sw" "$(pj "$c")" "${swenv[@]}" >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-stray-worktree allows '$c': exit $rc, want 0"
done
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

echo "hook selftest: PASS"
