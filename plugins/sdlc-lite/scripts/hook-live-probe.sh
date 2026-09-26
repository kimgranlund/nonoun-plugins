#!/usr/bin/env bash
# Opt-in live probe for hooks/block-background.sh: runs one real, small `claude -p` session that
# is told to call Bash once with run_in_background: true, captures the exact PreToolUse(Bash)
# payload Claude Code sends, and checks that tool_input.run_in_background arrives as a JSON
# boolean true and that block-background.sh denies the call (exit 2) with SDLC_HEADLESS=1.
# It spends one model call, so check.sh never runs live mode; check.sh runs only --selftest,
# which is offline (a stub claude, no model call).
#
# Usage: hook-live-probe.sh [--out FILE] [--model M] [--timeout SEC] [--selftest]
#   --out FILE     also write the report as markdown to FILE
#   --model M      model for the probe session (default: haiku)
#   --timeout SEC  bound the claude run (default: 120)
#   --selftest     offline selftest with a stub claude; makes no model call
# The claude binary is ${SDLC_PROBE_CLAUDE:-claude}.
# Everything is written into a mktemp -d dir removed by trap, apart from the --out file. It never
# touches user or project settings files and never passes --plugin-dir: the hook is registered
# only through --settings <tmp>/settings.json.
# Exit: 0 PASS, 1 FAIL or inconclusive, 2 usage or setup error.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
hook="$(cd "$here/../hooks" && pwd)/block-background.sh"
self="$here/$(basename "$0")"

usage() { echo "usage: hook-live-probe.sh [--out FILE] [--model M] [--timeout SEC] [--selftest]" >&2; exit 2; }

out="" model="haiku" timeout=120 selftest=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) [[ $# -ge 2 ]] || usage; out="$2"; shift 2 ;;
    --model) [[ $# -ge 2 ]] || usage; model="$2"; shift 2 ;;
    --timeout) [[ $# -ge 2 ]] || usage; timeout="$2"; shift 2 ;;
    --selftest) selftest=1; shift ;;
    -h|--help) usage ;;
    *) echo "hook-live-probe: unknown argument: $1" >&2; usage ;;
  esac
done
[[ "$timeout" =~ ^[0-9]+$ && "$timeout" -gt 0 ]] || { echo "hook-live-probe: --timeout must be a positive integer" >&2; exit 2; }
command -v jq >/dev/null || { echo "hook-live-probe: jq not found" >&2; exit 2; }
command -v python3 >/dev/null || { echo "hook-live-probe: python3 not found" >&2; exit 2; }
[[ -x "$hook" ]] || { echo "hook-live-probe: hook not found or not executable: $hook" >&2; exit 2; }

# ---------------------------------------------------------------------------------------------
# Selftest: offline, stub claude, cases (a) to (d), and no probe temp dir left behind.
# ---------------------------------------------------------------------------------------------
if [[ $selftest -eq 1 ]]; then
  st="$(mktemp -d "${TMPDIR:-/tmp}/hook-live-probe-selftest.XXXXXX")"
  trap 'rm -rf "$st"' EXIT
  trap 'rm -rf "$st"; exit 130' INT
  trap 'rm -rf "$st"; exit 143' TERM
  sfail() { echo "hook live probe selftest: FAIL: $*"; exit 1; }
  mkdir -p "$st/tmp"
  # Stub claude. STUB_MODE: hook (pipe STUB_PAYLOAD into the registered hook), none (call no
  # hook), sleep (outlive the timeout). --version prints a fake version.
  cat >"$st/claude" <<'EOF'
#!/usr/bin/env bash
settings=""
while [[ $# -gt 0 ]]; do
  [[ "$1" == "--version" ]] && { echo "0.0.0 (stub)"; exit 0; }
  [[ "$1" == "--settings" && $# -ge 2 ]] && settings="$2"
  shift
done
case "${STUB_MODE:-hook}" in
  none) exit 0 ;;
  sleep) sleep 47; exit 0 ;;
esac
cmd="$(jq -r '.hooks.PreToolUse[0].hooks[0].command' "$settings")"
printf '%s' "$STUB_PAYLOAD" | "$cmd" 2>/dev/null
exit 0
EOF
  chmod +x "$st/claude"
  # probe <mode> <payload> [args...]: runs the probe against the stub; sets pout and prc.
  probe() {
    local mode="$1" payload="$2"; shift 2
    pout="$(TMPDIR="$st/tmp" SDLC_PROBE_CLAUDE="$st/claude" STUB_MODE="$mode" STUB_PAYLOAD="$payload" \
      bash "$self" "$@" 2>/dev/null)"
    prc=$?
  }
  good='{"tool_name":"Bash","tool_input":{"command":"sleep 1","run_in_background":true}}'
  strtype='{"tool_name":"Bash","tool_input":{"command":"sleep 1","run_in_background":"true"}}'

  # (a) boolean true, hook denies: PASS, exit 0; the --out report ends with the verdict line.
  probe hook "$good" --out "$st/report.md"
  [[ $prc -eq 0 ]] || sfail "(a) boolean true: exit $prc, want 0"
  grep -qx "verdict: PASS" <<<"$pout" || sfail "(a) boolean true: no 'verdict: PASS' line"
  grep -qx "# Hook live probe" "$st/report.md" || sfail "(a) --out report lacks heading"
  grep -qx "hook exit code: 2" "$st/report.md" || sfail "(a) --out report lacks hook exit code line"
  [[ "$(tail -n 1 "$st/report.md")" == "verdict: PASS" ]] || sfail "(a) --out report last line is not the verdict"

  # (b) string "true": FAIL, exit 1, the reason names the type.
  probe hook "$strtype"
  [[ $prc -eq 1 ]] || sfail "(b) string type: exit $prc, want 1"
  grep -q "^verdict: FAIL: .*string" <<<"$pout" || sfail "(b) string type: FAIL line does not name the type"

  # (c) no hook call: exit 1.
  probe none ""
  [[ $prc -eq 1 ]] || sfail "(c) no hook call: exit $prc, want 1"
  grep -q "^verdict: FAIL: no Bash call captured" <<<"$pout" || sfail "(c) no hook call: wrong FAIL reason"

  # (d) stub outlives --timeout 2: exit 1 within a few seconds, and no stub child left running.
  # The bound is 20s, well under the stub's 47s sleep, so a loaded host does not flake it.
  start=$SECONDS
  probe sleep "" --timeout 2
  elapsed=$((SECONDS - start))
  [[ $prc -eq 1 ]] || sfail "(d) timeout: exit $prc, want 1"
  [[ $elapsed -le 20 ]] || sfail "(d) timeout: took ${elapsed}s, want <= 20"
  for _ in 1 2 3 4 5; do pgrep -f "sleep 47" >/dev/null || break; sleep 0.2; done
  ! pgrep -f "sleep 47" >/dev/null || sfail "(d) timeout: stub child still running"

  # Every probe run removed its temp dir.
  left="$(find "$st/tmp" -mindepth 1 -maxdepth 1 2>/dev/null)"
  [[ -z "$left" ]] || sfail "temp dir left behind: $left"
  echo "hook live probe selftest: PASS"
  exit 0
fi

# ---------------------------------------------------------------------------------------------
# Live mode.
# ---------------------------------------------------------------------------------------------
claude="${SDLC_PROBE_CLAUDE:-claude}"
command -v "$claude" >/dev/null || { echo "hook-live-probe: claude binary not found: $claude" >&2; exit 2; }

tmp="$(mktemp -d "${TMPDIR:-/tmp}/hook-live-probe.XXXXXX")" || { echo "hook-live-probe: mktemp failed" >&2; exit 2; }
runner=""
cleanup() {
  if [[ -n "$runner" ]]; then kill "$runner" 2>/dev/null; wait "$runner" 2>/dev/null; runner=""; fi
  rm -rf "$tmp"
}
trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

# Capture wrapper: the first Bash call's stdin goes to payload.json and the hook's exit code to
# rc (a model that retries after the deny must not overwrite the call under test). Every call
# is piped into the real hook; its stderr is forwarded and its exit code returned.
cat >"$tmp/capture.sh" <<EOF
#!/usr/bin/env bash
tmp=$(printf '%q' "$tmp")
hook=$(printf '%q' "$hook")
input="\$(cat)"
first=0
[[ -e "\$tmp/payload.json" ]] || { first=1; printf '%s' "\$input" >"\$tmp/payload.json"; }
printf '%s' "\$input" | "\$hook"
rc=\$?
[[ \$first -eq 1 ]] && echo "\$rc" >"\$tmp/rc"
exit "\$rc"
EOF
chmod +x "$tmp/capture.sh"

jq -n --arg cmd "$tmp/capture.sh" \
  '{hooks:{PreToolUse:[{matcher:"Bash",hooks:[{type:"command",command:$cmd}]}]}}' >"$tmp/settings.json"

prompt='This is a hook test. Call the Bash tool exactly once, with command "sleep 1" and run_in_background set to true. Whatever the result, do not call any tool again; reply with one word and stop.'

# Timeout runner: python3 starts claude in its own session and kills the whole process group on
# timeout, on SIGTERM, and after claude exits, so no child outlives the probe.
# shellcheck disable=SC2016
runner_py='
import os, signal, subprocess, sys
limit = float(sys.argv[1]); log = sys.argv[2]; cmd = sys.argv[3:]
def stop(p):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(p.pid, sig)
        except (ProcessLookupError, PermissionError):
            return
        try:
            p.wait(timeout=5)
            return
        except subprocess.TimeoutExpired:
            pass
with open(log, "wb") as f:
    p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT,
                         start_new_session=True)
    def on_term(*_):
        stop(p)
        sys.exit(143)
    signal.signal(signal.SIGTERM, on_term)
    try:
        rc = p.wait(timeout=limit)
    except subprocess.TimeoutExpired:
        stop(p)
        sys.exit(124)
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    sys.exit(rc)
'

(cd "$tmp" && exec python3 -c "$runner_py" "$timeout" "$tmp/claude.log" \
  env -u SDLC_ROLE SDLC_HEADLESS=1 "$claude" -p --model "$model" \
  --settings "$tmp/settings.json" --dangerously-skip-permissions "$prompt") &
runner=$!
wait "$runner"
run_rc=$?
runner=""

# Verdict.
reason=""
payload_pretty="(none)"
hook_rc="none"
[[ -s "$tmp/rc" ]] && hook_rc="$(tr -d '[:space:]' <"$tmp/rc")"
if [[ ! -s "$tmp/payload.json" ]]; then
  reason="no Bash call captured"
  [[ $run_rc -eq 124 ]] && reason="$reason (claude timed out after ${timeout}s)"
elif ! payload_pretty="$(jq . "$tmp/payload.json" 2>/dev/null)"; then
  payload_pretty="$(cat "$tmp/payload.json")"
  reason="payload is not valid JSON"
else
  tool="$(jq -r '.tool_name // "(missing)"' "$tmp/payload.json")"
  has="$(jq -r '(.tool_input // {}) | type == "object" and has("run_in_background")' "$tmp/payload.json")"
  type="$(jq -r '.tool_input.run_in_background | type' "$tmp/payload.json")"
  val="$(jq -c '.tool_input.run_in_background' "$tmp/payload.json")"
  if [[ "$tool" != "Bash" ]]; then
    reason="no Bash call captured (tool_name is $tool)"
  elif [[ "$has" != "true" ]]; then
    reason="field missing: tool_input.run_in_background"
  elif [[ "$type" != "boolean" ]]; then
    reason="wrong JSON type: tool_input.run_in_background is $type ($val), want boolean"
  elif [[ "$val" != "true" ]]; then
    reason="tool_input.run_in_background is $val, want true"
  elif [[ "$hook_rc" != "2" ]]; then
    reason="hook exit code $hook_rc, not 2"
  fi
fi
if [[ -z "$reason" ]]; then verdict="verdict: PASS"; code=0; else verdict="verdict: FAIL: $reason"; code=1; fi

printf '%s\n' "$payload_pretty"
echo "hook exit code: $hook_rc"
if [[ $code -ne 0 && -s "$tmp/claude.log" ]]; then
  { echo "claude output (last 20 lines):"; tail -n 20 "$tmp/claude.log"; } >&2
fi
echo "$verdict"

if [[ -n "$out" ]]; then
  version="$("$claude" --version 2>/dev/null | head -n 1)"
  {
    echo "# Hook live probe"
    echo
    echo "- date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "- model: $model"
    echo "- claude --version: ${version:-unknown}"
    echo
    echo "Captured PreToolUse(Bash) payload:"
    echo
    echo '```json'
    printf '%s\n' "$payload_pretty"
    echo '```'
    echo
    echo "hook exit code: $hook_rc"
    echo
    echo "$verdict"
  } >"$out" || { echo "hook-live-probe: cannot write $out" >&2; exit 2; }
fi
exit "$code"
