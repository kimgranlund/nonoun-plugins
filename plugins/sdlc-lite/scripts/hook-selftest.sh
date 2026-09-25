#!/usr/bin/env bash
# Selftest for the PreToolUse(Bash) hooks: block-background.sh denies run_in_background in a
# headless session (SDLC_ROLE set or SDLC_HEADLESS=1) and passes everything else; block-publish.sh
# still blocks a push inside a role run. Never inherits the caller's SDLC_ROLE/SDLC_HEADLESS.
# Prints "hook selftest: PASS" or "hook selftest: FAIL: <case>" and exits non-zero on failure.
set -uo pipefail

hooks="$(cd "$(dirname "$0")/../hooks" && pwd)"
bg="$hooks/block-background.sh"
pub="$hooks/block-publish.sh"

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

echo "hook selftest: PASS"
