#!/usr/bin/env bash
# Opt-in live probe for hooks/block-background.sh. Default (Bash) mode runs one real, small
# `claude -p` session that is told to call Bash once with run_in_background: true, captures the
# exact PreToolUse(Bash) payload Claude Code sends, and checks that tool_input.run_in_background
# arrives as a JSON boolean true and that block-background.sh denies the call (exit 2) with
# SDLC_HEADLESS=1.
# --agent mode (hook-live-probe.sh --agent) runs two small sessions instead. The deny run is told
# to call the Agent tool without run_in_background; the allow run is told to call it with
# run_in_background: false. It passes only when both calls reach PreToolUse as tool_name Agent
# (so a "matcher": "Agent" hook entry fires), the deny run's field is absent or boolean true and
# the hook exits 2, the allow run's field is the JSON boolean false and the hook exits 0, and a
# PostToolUse(Agent) record proves the allowed call ran. A match-all logger records every
# tool_name, so a FAIL names the tool called instead (for example Task).
# Live mode spends model calls, so check.sh never runs it; check.sh runs only --selftest, which
# is offline (a stub claude, no model call) and covers both the Bash and the Agent path.
#
# Usage: hook-live-probe.sh [--agent] [--out FILE] [--model M] [--timeout SEC] [--selftest]
#   --agent        probe the Agent tool (two claude runs) instead of Bash
#   --out FILE     also write the report as markdown to FILE
#   --model M      model for the probe session (default: haiku)
#   --timeout SEC  bound each claude run (default: 120)
#   --selftest     offline selftest with a stub claude; makes no model call
# The claude binary is ${SDLC_PROBE_CLAUDE:-claude}.
# Everything is written into a mktemp -d dir removed by trap, apart from the --out file. It never
# touches user or project settings files and never passes --plugin-dir: the hooks are registered
# only through --settings <tmp>/.../settings.json.
# Exit: 0 PASS, 1 FAIL or inconclusive, 2 usage or setup error.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
hook="$(cd "$here/../hooks" && pwd)/block-background.sh"
self="$here/$(basename "$0")"

usage() { echo "usage: hook-live-probe.sh [--agent] [--out FILE] [--model M] [--timeout SEC] [--selftest]" >&2; exit 2; }

out="" model="haiku" timeout=120 selftest=0 agent=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) agent=1; shift ;;
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

# The allow run's subagent prompt. The selftest stub tells the two Agent runs apart by it.
allow_marker="Reply with the word ok and use no tools"

# ---------------------------------------------------------------------------------------------
# Selftest: offline, stub claude, cases (a) to (e) for Bash, (f) to (j) for Agent, and no probe
# temp dir left behind.
# ---------------------------------------------------------------------------------------------
if [[ $selftest -eq 1 ]]; then
  st="$(mktemp -d "${TMPDIR:-/tmp}/hook-live-probe-selftest.XXXXXX")"
  trap 'rm -rf "$st"' EXIT
  trap 'rm -rf "$st"; exit 130' INT
  trap 'rm -rf "$st"; exit 143' TERM
  sfail() { echo "hook live probe selftest: FAIL: $*"; exit 1; }
  mkdir -p "$st/tmp"
  # Stub claude. STUB_MODE: hook (pipe the payload into the registered hooks), none (call no
  # hook), sleep (outlive the timeout), nodeny (cases (e) and (j): like hook, but with
  # SDLC_HEADLESS and SDLC_ROLE unset, so the hook exits 0). The payload is STUB_ALLOW_PAYLOAD
  # when the prompt holds the allow marker, else STUB_PAYLOAD. Hooks are found by matcher (the
  # payload's tool_name, or a match-all "*", "" or missing matcher), like Claude Code does; the
  # PostToolUse hooks run only when every PreToolUse hook exited 0. --version prints a fake
  # version.
  cat >"$st/claude" <<EOF
#!/usr/bin/env bash
marker=$(printf '%q' "$allow_marker")
EOF
  cat >>"$st/claude" <<'EOF'
settings="" prompt=""
while [[ $# -gt 0 ]]; do
  [[ "$1" == "--version" ]] && { echo "0.0.0 (stub)"; exit 0; }
  [[ "$1" == "--settings" && $# -ge 2 ]] && settings="$2"
  prompt="$1"
  shift
done
case "${STUB_MODE:-hook}" in
  none) exit 0 ;;
  sleep) sleep 47; exit 0 ;;
esac
payload="${STUB_PAYLOAD:-}"
[[ "$prompt" == *"$marker"* ]] && payload="${STUB_ALLOW_PAYLOAD:-}"
tool="$(jq -r '.tool_name // ""' <<<"$payload" 2>/dev/null)"
hooks_for() {
  jq -r --arg ev "$1" --arg t "$tool" \
    '.hooks[$ev][]? | select(.matcher == null or .matcher == "" or .matcher == "*" or .matcher == $t) | .hooks[].command' \
    "$settings"
}
run_hook() {
  if [[ "${STUB_MODE:-hook}" == "nodeny" ]]; then
    printf '%s' "$payload" | env -u SDLC_HEADLESS -u SDLC_ROLE "$1" 2>/dev/null
  else
    printf '%s' "$payload" | "$1" 2>/dev/null
  fi
}
blocked=0
while IFS= read -r cmd; do
  [[ -n "$cmd" ]] || continue
  run_hook "$cmd" || blocked=1
done < <(hooks_for PreToolUse)
if [[ $blocked -eq 0 ]]; then
  while IFS= read -r cmd; do
    [[ -n "$cmd" ]] || continue
    run_hook "$cmd"
  done < <(hooks_for PostToolUse)
fi
exit 0
EOF
  chmod +x "$st/claude"
  # probe <mode> <payload> [args...]: runs the probe against the stub; sets pout and prc.
  # PROBE_SCRIPT (default: this script) and STUB_ALLOW_PAYLOAD pass through from the caller.
  probe() {
    local mode="$1" payload="$2"; shift 2
    pout="$(TMPDIR="$st/tmp" SDLC_PROBE_CLAUDE="$st/claude" STUB_MODE="$mode" STUB_PAYLOAD="$payload" \
      STUB_ALLOW_PAYLOAD="${STUB_ALLOW_PAYLOAD:-}" bash "${PROBE_SCRIPT:-$self}" "$@" 2>/dev/null)"
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

  # (e) boolean true, but the hook exits 0 (not 2): FAIL, exit 1, the reason names the exit code.
  probe nodeny "$good"
  [[ $prc -eq 1 ]] || sfail "(e) hook exit 0: exit $prc, want 1"
  grep -q "^verdict: FAIL: hook exit code 0, not 2" <<<"$pout" || sfail "(e) hook exit 0: FAIL line does not name the hook exit code"

  # Agent payloads: the deny run leaves run_in_background out, the allow run passes false.
  adeny='{"tool_name":"Agent","tool_input":{"description":"hook probe","prompt":"Say hello","subagent_type":"general-purpose"}}'
  aallow='{"tool_name":"Agent","tool_input":{"description":"hook probe","prompt":"Reply with the word ok and use no tools","subagent_type":"general-purpose","run_in_background":false}}'
  atrue='{"tool_name":"Agent","tool_input":{"description":"hook probe","prompt":"Say hello","subagent_type":"general-purpose","run_in_background":true}}'
  astrfalse='{"tool_name":"Agent","tool_input":{"description":"hook probe","prompt":"Reply with the word ok and use no tools","subagent_type":"general-purpose","run_in_background":"false"}}'
  tdeny='{"tool_name":"Task","tool_input":{"description":"hook probe","prompt":"Say hello","subagent_type":"general-purpose"}}'
  tallow='{"tool_name":"Task","tool_input":{"description":"hook probe","prompt":"Reply with the word ok and use no tools","subagent_type":"general-purpose","run_in_background":false}}'

  # (f) missing field plus false, with the real hook: PASS, exit 0; the --out report has the
  # heading and both agent lines, and ends with the verdict line.
  STUB_ALLOW_PAYLOAD="$aallow" probe hook "$adeny" --agent --out "$st/agent-report.md"
  [[ $prc -eq 0 ]] || sfail "(f) agent missing plus false: exit $prc, want 0 ($(grep '^verdict' <<<"$pout"))"
  grep -qx "verdict: PASS" <<<"$pout" || sfail "(f) agent: no 'verdict: PASS' line"
  grep -qx "agent deny: tool_name Agent, run_in_background (absent), hook exit code 2" <<<"$pout" \
    || sfail "(f) agent: stdout lacks the agent deny line"
  grep -qx "agent allow: tool_name Agent, run_in_background false, hook exit code 0, posttooluse yes" <<<"$pout" \
    || sfail "(f) agent: stdout lacks the agent allow line"
  grep -qx "# Hook live probe (Agent)" "$st/agent-report.md" || sfail "(f) --out report lacks heading"
  grep -qx "agent deny: tool_name Agent, run_in_background (absent), hook exit code 2" "$st/agent-report.md" \
    || sfail "(f) --out report lacks the agent deny line"
  grep -qx "agent allow: tool_name Agent, run_in_background false, hook exit code 0, posttooluse yes" "$st/agent-report.md" \
    || sfail "(f) --out report lacks the agent allow line"
  [[ "$(tail -n 1 "$st/agent-report.md")" == "verdict: PASS" ]] || sfail "(f) --out report last line is not the verdict"

  # (f2) deny payload with boolean true passes too.
  STUB_ALLOW_PAYLOAD="$aallow" probe hook "$atrue" --agent
  [[ $prc -eq 0 ]] || sfail "(f2) agent true plus false: exit $prc, want 0"

  # (g) the subagent tool reaches PreToolUse as Task: the Agent matcher never fires, FAIL names Task.
  STUB_ALLOW_PAYLOAD="$tallow" probe hook "$tdeny" --agent
  [[ $prc -eq 1 ]] || sfail "(g) tool_name Task: exit $prc, want 1"
  grep -q "^verdict: FAIL: .*no Agent call captured.*Task" <<<"$pout" || sfail "(g) tool_name Task: FAIL line does not name Task"

  # (h) run_in_background as the string "false": FAIL naming the type.
  STUB_ALLOW_PAYLOAD="$astrfalse" probe hook "$adeny" --agent
  [[ $prc -eq 1 ]] || sfail "(h) string \"false\": exit $prc, want 1"
  grep -q "^verdict: FAIL: .*agent allow: wrong JSON type.*string" <<<"$pout" || sfail "(h) string \"false\": FAIL line does not name the type"

  # (i) the hook denies the allow payload: FAIL naming the hook exit code. A copy of this script
  # runs against a hook that always exits 2.
  mkdir -p "$st/deny-all/scripts" "$st/deny-all/hooks"
  cp "$self" "$st/deny-all/scripts/hook-live-probe.sh"
  printf '#!/usr/bin/env bash\ncat >/dev/null\nexit 2\n' >"$st/deny-all/hooks/block-background.sh"
  chmod +x "$st/deny-all/hooks/block-background.sh"
  STUB_ALLOW_PAYLOAD="$aallow" PROBE_SCRIPT="$st/deny-all/scripts/hook-live-probe.sh" probe hook "$adeny" --agent
  [[ $prc -eq 1 ]] || sfail "(i) allow denied: exit $prc, want 1"
  grep -q "^verdict: FAIL: .*agent allow: hook exit code 2, not 0" <<<"$pout" || sfail "(i) allow denied: FAIL line does not name the hook exit code"

  # (j) deny payload true, but the hook runs without SDLC_HEADLESS and exits 0: FAIL.
  STUB_ALLOW_PAYLOAD="$aallow" probe nodeny "$atrue" --agent
  [[ $prc -eq 1 ]] || sfail "(j) agent hook exit 0: exit $prc, want 1"
  grep -q "^verdict: FAIL: .*agent deny: hook exit code 0, not 2" <<<"$pout" || sfail "(j) agent hook exit 0: FAIL line does not name the hook exit code"

  # Every probe run, Bash and Agent, removed its temp dir.
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

# write_capture <dir>: the capture wrapper. The first call's stdin goes to <dir>/payload.json and
# the hook's exit code to <dir>/rc (a model that retries after the deny must not overwrite the
# call under test). Every call is piped into the real hook; its stderr is forwarded and its exit
# code returned.
write_capture() {
  local dir="$1"
  cat >"$dir/capture.sh" <<EOF
#!/usr/bin/env bash
tmp=$(printf '%q' "$dir")
hook=$(printf '%q' "$hook")
input="\$(cat)"
first=0
[[ -e "\$tmp/payload.json" ]] || { first=1; printf '%s' "\$input" >"\$tmp/payload.json"; }
printf '%s' "\$input" | "\$hook"
rc=\$?
[[ \$first -eq 1 ]] && echo "\$rc" >"\$tmp/rc"
exit "\$rc"
EOF
  chmod +x "$dir/capture.sh"
}

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

# run_claude <dir> <prompt>: one claude run in <dir> with <dir>/settings.json, output in
# <dir>/claude.log; sets run_rc (124 on timeout).
run_claude() {
  local dir="$1" prompt="$2"
  (cd "$dir" && exec python3 -c "$runner_py" "$timeout" "$dir/claude.log" \
    env -u SDLC_ROLE SDLC_HEADLESS=1 "$claude" -p --model "$model" \
    --settings "$dir/settings.json" --dangerously-skip-permissions "$prompt") &
  runner=$!
  wait "$runner"
  run_rc=$?
  runner=""
}

# ---------------------------------------------------------------------------------------------
# Agent mode: a deny run and an allow run.
# ---------------------------------------------------------------------------------------------
if [[ $agent -eq 1 ]]; then
  deny_prompt='This is a hook test. Call the Agent tool (the subagent tool; it may be named Task) exactly once, with subagent_type "general-purpose", description "hook probe", and prompt "Say hello". Leave the run_in_background parameter out entirely. Whatever the result, do not call any tool again; reply with one word and stop.'
  allow_prompt="This is a hook test. Call the Agent tool (the subagent tool; it may be named Task) exactly once, with subagent_type \"general-purpose\", description \"hook probe\", run_in_background set to false, and prompt \"$allow_marker\". Wait for its result. Whatever the result, do not call any tool again; reply with one word and stop."

  # setup_run <dir>: capture (PreToolUse, matcher Agent), logger (PreToolUse, match-all: appends
  # every tool_name to tools.log) and recorder (PostToolUse, matcher Agent: appends to post.json).
  setup_run() {
    local dir="$1" q
    mkdir -p "$dir"
    write_capture "$dir"
    q="$(printf '%q' "$dir")"
    printf '#!/usr/bin/env bash\njq -r '\''.tool_name // "(missing)"'\'' >>%s/tools.log 2>/dev/null\nexit 0\n' "$q" >"$dir/log.sh"
    printf '#!/usr/bin/env bash\ncat >>%s/post.json\necho >>%s/post.json\nexit 0\n' "$q" "$q" >"$dir/post.sh"
    chmod +x "$dir/log.sh" "$dir/post.sh"
    jq -n --arg cap "$dir/capture.sh" --arg log "$dir/log.sh" --arg post "$dir/post.sh" \
      '{hooks:{
         PreToolUse:[{matcher:"Agent",hooks:[{type:"command",command:$cap}]},
                     {matcher:"*",hooks:[{type:"command",command:$log}]}],
         PostToolUse:[{matcher:"Agent",hooks:[{type:"command",command:$post}]}]}}' >"$dir/settings.json"
  }

  # eval_run <dir> <deny|allow> <run_rc>: sets r_tool, r_bg, r_rc, r_post, r_pretty, r_reason.
  eval_run() {
    local dir="$1" kind="$2" rrc="$3" seen has type
    r_tool="(none)" r_bg="(absent)" r_rc="none" r_post="no" r_pretty="(none)" r_reason=""
    [[ -s "$dir/rc" ]] && r_rc="$(tr -d '[:space:]' <"$dir/rc")"
    [[ -s "$dir/post.json" ]] && r_post="yes"
    if [[ ! -s "$dir/payload.json" ]]; then
      seen="$(sort -u "$dir/tools.log" 2>/dev/null | sed '/^$/d' | paste -sd, - | sed 's/,/, /g')"
      if [[ -z "$seen" ]]; then r_reason="no Agent call captured (no tool call seen)"
      elif [[ "$seen" == *,* ]]; then r_reason="no Agent call captured (tool names seen: $seen)"
      else r_reason="no Agent call captured (tool_name is $seen)"
      fi
      [[ "$rrc" -eq 124 ]] && r_reason="$r_reason (claude timed out after ${timeout}s)"
    elif ! r_pretty="$(jq . "$dir/payload.json" 2>/dev/null)"; then
      r_pretty="$(cat "$dir/payload.json")"
      r_reason="payload is not valid JSON"
    else
      r_tool="$(jq -r '.tool_name // "(missing)"' "$dir/payload.json")"
      has="$(jq -r '(.tool_input // {}) | type == "object" and has("run_in_background")' "$dir/payload.json")"
      type="$(jq -r '.tool_input.run_in_background | type' "$dir/payload.json")"
      [[ "$has" == "true" ]] && r_bg="$(jq -c '.tool_input.run_in_background' "$dir/payload.json")"
      if [[ "$r_tool" != "Agent" ]]; then
        r_reason="no Agent call captured (tool_name is $r_tool)"
      elif [[ "$kind" == "deny" ]]; then
        if [[ "$has" == "true" && "$type" != "boolean" ]]; then
          r_reason="wrong JSON type: tool_input.run_in_background is $type ($r_bg), want absent or boolean true"
        elif [[ "$has" == "true" && "$r_bg" != "true" ]]; then
          r_reason="tool_input.run_in_background is $r_bg, want absent or true"
        elif [[ "$r_rc" != "2" ]]; then
          r_reason="hook exit code $r_rc, not 2"
        fi
      else
        if [[ "$has" != "true" ]]; then
          r_reason="field missing: tool_input.run_in_background"
        elif [[ "$type" != "boolean" ]]; then
          r_reason="wrong JSON type: tool_input.run_in_background is $type ($r_bg), want boolean"
        elif [[ "$r_bg" != "false" ]]; then
          r_reason="tool_input.run_in_background is $r_bg, want false"
        elif [[ "$r_rc" != "0" ]]; then
          r_reason="hook exit code $r_rc, not 0"
        elif [[ "$r_post" != "yes" ]]; then
          r_reason="no PostToolUse(Agent) record"
        fi
      fi
    fi
    [[ -n "$r_reason" ]] && r_reason="agent $kind: $r_reason"
  }

  setup_run "$tmp/deny"
  setup_run "$tmp/allow"
  run_claude "$tmp/deny" "$deny_prompt"; deny_run_rc=$run_rc
  run_claude "$tmp/allow" "$allow_prompt"; allow_run_rc=$run_rc

  eval_run "$tmp/deny" deny "$deny_run_rc"
  deny_line="agent deny: tool_name $r_tool, run_in_background $r_bg, hook exit code $r_rc"
  deny_pretty="$r_pretty" deny_reason="$r_reason"
  eval_run "$tmp/allow" allow "$allow_run_rc"
  allow_line="agent allow: tool_name $r_tool, run_in_background $r_bg, hook exit code $r_rc, posttooluse $r_post"
  allow_pretty="$r_pretty" allow_reason="$r_reason"

  reason="$deny_reason"
  if [[ -n "$allow_reason" ]]; then reason="${reason:+$reason; }$allow_reason"; fi
  if [[ -z "$reason" ]]; then verdict="verdict: PASS"; code=0; else verdict="verdict: FAIL: $reason"; code=1; fi

  echo "$deny_line"
  echo "$allow_line"
  if [[ $code -ne 0 ]]; then
    for kind in deny allow; do
      [[ -s "$tmp/$kind/claude.log" ]] || continue
      { echo "claude output, $kind run (last 20 lines):"; tail -n 20 "$tmp/$kind/claude.log"; } >&2
    done
  fi
  echo "$verdict"

  if [[ -n "$out" ]]; then
    version="$("$claude" --version 2>/dev/null | head -n 1)"
    {
      echo "# Hook live probe (Agent)"
      echo
      echo "- date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "- model: $model"
      echo "- claude --version: ${version:-unknown}"
      echo
      echo "Captured PreToolUse(Agent) payload, deny run:"
      echo
      echo '```json'
      printf '%s\n' "$deny_pretty"
      echo '```'
      echo
      echo "Captured PreToolUse(Agent) payload, allow run:"
      echo
      echo '```json'
      printf '%s\n' "$allow_pretty"
      echo '```'
      echo
      echo "$deny_line"
      echo "$allow_line"
      echo
      echo "$verdict"
    } >"$out" || { echo "hook-live-probe: cannot write $out" >&2; exit 2; }
  fi
  exit "$code"
fi

# ---------------------------------------------------------------------------------------------
# Bash mode.
# ---------------------------------------------------------------------------------------------
write_capture "$tmp"
jq -n --arg cmd "$tmp/capture.sh" \
  '{hooks:{PreToolUse:[{matcher:"Bash",hooks:[{type:"command",command:$cmd}]}]}}' >"$tmp/settings.json"

prompt='This is a hook test. Call the Bash tool exactly once, with command "sleep 1" and run_in_background set to true. Whatever the result, do not call any tool again; reply with one word and stop.'

run_claude "$tmp" "$prompt"

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
