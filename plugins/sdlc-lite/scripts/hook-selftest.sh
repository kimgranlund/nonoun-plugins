#!/usr/bin/env bash
# Selftest for the PreToolUse hooks (Bash and Agent): block-background.sh denies Bash
# run_in_background, and Agent unless run_in_background is false, in a headless session (SDLC_ROLE set or SDLC_HEADLESS=1) and passes everything else; block-publish.sh,
# inside a role run, allows commands that only mention a publish phrase (heredoc body, quoted
# argument, commit message) and blocks every real publish, including one fed to a shell or
# evaluator, one in a $(...) or backtick substitution, one behind an unterminated quote, and
# one in interpreter inline code (python -c, node -e/--eval, perl -e, ruby -e), while a plain
# python3 script run and an interpreter word inside a quoted mention pass;
# block-pattern-kill.sh, inside a role run, blocks killing by name pattern (pkill, killall,
# kill fed by pgrep) with a stderr naming the role and PIDs, and allows kill <pid>, kill $pid,
# a quoted mention, and anything outside a role run.
# Publish phrases and kill-pattern words are built with printf so this file never holds one
# as a command.
# Never inherits the caller's SDLC_ROLE/SDLC_HEADLESS.
# Prints "hook selftest: PASS" or "hook selftest: FAIL: <case>" and exits non-zero on failure.
set -uo pipefail

hooks="$(cd "$(dirname "$0")/../hooks" && pwd)"
bg="$hooks/block-background.sh"
pub="$hooks/block-publish.sh"
pk="$hooks/block-pattern-kill.sh"

fail() { echo "hook selftest: FAIL: $*"; exit 1; }

# run <hook> <json> [VAR=value ...]: prints stderr, returns the hook's exit code.
run() {
  local hook="$1" json="$2"; shift 2
  printf '%s' "$json" | env -u SDLC_ROLE -u SDLC_HEADLESS "$@" "$hook" 3>&1 1>/dev/null 2>&3
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
for c in "$kaw node" "kill \$($pgw -f vite)" "$pgw -f vite | xargs kill" "sudo $pkw -f vite" \
  "cd x && $pkw -f vite"; do
  run "$pk" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
  [[ $rc -eq 2 ]] || fail "block-pattern-kill blocks '$c': exit $rc, want 2"
done
for c in "kill 12345" "kill \$pid" "grep -n \"$pkw\" f"; do
  run "$pk" "$(pj "$c")" SDLC_ROLE=builder >/dev/null; rc=$?
  [[ $rc -eq 0 ]] || fail "block-pattern-kill allows '$c': exit $rc, want 0"
done
run "$pk" "$(pj "$pkw -f vite")" >/dev/null; rc=$?
[[ $rc -eq 0 ]] || fail "block-pattern-kill without role: exit $rc, want 0"

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
