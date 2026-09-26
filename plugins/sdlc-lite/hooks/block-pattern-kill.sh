#!/usr/bin/env bash
# PreToolUse(Bash): inside a role run (SDLC_ROLE set by scripts/run.sh or fanout), block
# commands that kill processes by name pattern, because a pattern also matches processes that
# other sessions, lanes, or the user started. Blocked: pkill or killall in command position,
# kill fed by pgrep or ps (kill $(pgrep ...), kill `pgrep ...`, pgrep ... | xargs kill,
# kill $(ps ... | awk ...), ps ... | grep ... | awk ... | xargs kill), and a kill word held in
# a shell variable (p=pkill; $p x, k=killall; ${k} node, k=kill; "$k" ...). Command position
# is the start of the command or after ; & | ( { ` or $( , optionally behind sudo, xargs, env,
# command, nohup, timeout N, a VAR=value assignment, or a shell keyword.
# Allowed: kill <pid>, kill $pid, kill %1, kill $(cat pidfile), echo $! | xargs kill, a
# variable holding another command (cmd=ls; $cmd -la), and text that only mentions the words
# inside a quoted argument (grep -n "pkill" f).
#
# Simple masking: single-quoted, $'...' and double-quoted contents are kept when they are one
# plain word (so 'pkill' -f x is still seen as pkill) and dropped otherwise; a double-quoted
# string holding $( or a backtick, or only "$VAR" or "${VAR}", keeps its contents; unquoted
# backslashes and comments are removed. Fails closed, scanning the raw text with a looser word match, when python3 is
# missing or the masker errors, when a quote is unterminated, when the command holds a
# heredoc (<<), or when a shell or evaluator (bash, sh, zsh, dash, ksh, fish, eval, ssh, su)
# appears as a command word, so bash -c "pkill x" stays blocked.
[[ -n "${SDLC_ROLE:-}" ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""')

# Cheap exit: none of the words appear even with quotes and backslashes removed. A command
# with kill passes on when it also holds ps, or an assignment and a $ expansion.
pf=${cmd//[\\\'\"]/}
[[ $pf == *pkill* || $pf == *killall* || $pf == *pgrep* ]] ||
  [[ $pf == *kill* && ($pf == *ps* || ($pf == *=* && $pf == *\$*)) ]] || exit 0

# A wrapper word (with its flags, numbers, and assignments) that can precede a command.
w='(sudo|xargs|env|command|nohup|timeout|exec|time|then|do|else|if|while|until|!|[[:alpha:]_][[:alnum:]_]*=[^[:space:]]*)([[:space:]]+(-[^[:space:]]*|[0-9][^[:space:]]*|[[:alpha:]_][[:alnum:]_]*=[^[:space:]]*))*[[:space:]]+'
path='([^[:space:];&|()`]*/)?'
end='([[:space:]]|$|[;&|)`])'
cp="(^|[;&|({\`]|\\\$\\()[[:space:]]*($w)*$path"
strict="${cp}(pkill|killall)${end}"
strict+="|${cp}kill([[:space:]][^;&|]*)?(\\\$\\(|\`)[[:space:]]*($w)*${path}(pgrep|ps)${end}"
strict+="|${cp}(pgrep|ps)([[:space:]][^;&]*)?\\|[[:space:]]*($w)*xargs([[:space:]]+-[^[:space:]]*)*[[:space:]]+($w)*${path}kill${end}"
# A kill word held in a variable: NAME=<kill word> (plain or a path), then $NAME or ${NAME} in
# command position. ERE has no backreference, so the names are extracted first.
assign="(^|[^[:alnum:]_])[[:alpha:]_][[:alnum:]_]*=${path}(pkill|killall|kill)${end}"
word='(^|[^[:alnum:]_-])'
wend='([^[:alnum:]_-]|$)'
loose="${word}(pkill|killall)${wend}|${word}kill${wend}.*${word}(pgrep|ps)${wend}|${word}(pgrep|ps)${wend}.*${word}kill${wend}"
loose+="|[[:alpha:]_][[:alnum:]_]*=[\"']?([^[:space:];&|()\`]*/)?(pkill|killall|kill)${wend}.*(^|[;&|({\`]|\\\$\\()[[:space:]]*[\"']?\\\$\\{?[[:alpha:]_]"

block() {
  echo "Blocked for sdlc role '$SDLC_ROLE': killing by name pattern (pkill, killall, kill \$(pgrep ...), pgrep | xargs kill, kill \$(ps ...), ps ... | xargs kill, a kill word held in a variable) can stop processes other sessions started. Stop only the PIDs you started, for example save \$! at launch and kill that PID. Never kill by name pattern." >&2
  exit 2
}

# Blocks when the masked text assigns a kill word to a variable and expands it as a command.
held_kill() {
  local n
  while IFS= read -r n; do
    [[ -n $n ]] && grep -Eq "${cp}\\\$(${n}|\\{${n}\\})${end}" <<<"$1" && block
  done < <(grep -oE "$assign" <<<"$1" | sed -E 's/=.*//; s/.*[^[:alnum:]_]//')
  return 0
}

# Prints the masked command, or exits non-zero to make the hook scan the raw command.
read -r -d '' masker <<'PY' || true
import re, sys

cmd = sys.argv[1]
SHELL_WORD = (r'(?:^|[\s;&|(`{/])(?:bash|sh|zsh|dash|ksh|fish|eval|ssh|su)'
              r'(?=$|[\s;&|)`}<>])')
if re.search(SHELL_WORD, cmd) or re.search(r'<<(?!<)', cmd):
    sys.exit(1)
PLAIN = re.compile(r'[A-Za-z0-9_./=:+,@%-]*\Z')
VAR = re.compile(r'\$(?:[A-Za-z_]\w*|\{[A-Za-z_]\w*\})\Z')
out, i, n = [], 0, len(cmd)
while i < n:
    c = cmd[i]
    if c == '\\':
        out.append(cmd[i + 1:i + 2])
        i += 2
    elif c == "'" or cmd.startswith("$'", i):
        start = i + (2 if c == '$' else 1)
        j = cmd.find("'", start)
        if j < 0:
            sys.exit(1)
        body = cmd[start:j]
        if c == '$' and '\\' in body:
            sys.exit(1)
        if PLAIN.match(body):
            out.append(body)
        i = j + 1
    elif c == '"':
        j = i + 1
        while j < n and cmd[j] != '"':
            j += 2 if cmd[j] == '\\' else 1
        if j >= n:
            sys.exit(1)
        body = cmd[i + 1:j]
        if (PLAIN.match(body) or '$(' in body or '`' in body
                or VAR.match(body)):
            out.append(body)
        i = j + 1
    elif c == '#' and (i == 0 or cmd[i - 1] in ' \t\n;&|()<>'):
        j = cmd.find('\n', i)
        i = n if j < 0 else j
    else:
        out.append(c)
        i += 1
sys.stdout.write(''.join(out))
PY

if scan=$(python3 -c "$masker" "$cmd" 2>/dev/null); then
  grep -Eq "$strict" <<<"$scan" && block
  held_kill "$scan"
  exit 0
fi
raw=$(tr '\n' ' ' <<<"${cmd//\\/}")
grep -Eq "$loose" <<<"$raw" && block
exit 0
