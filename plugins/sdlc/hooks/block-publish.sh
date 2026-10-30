#!/usr/bin/env bash
# PreToolUse(Bash): inside a role run (a role from hooks/_role.sh: SDLC_ROLE, else the sub-agent's
# agent_type), block commands that
# publish outside the machine. Publishing happens only from the user's session after approval.
#
# The publish pattern is matched against a masked copy of the command, so text that only
# mentions a publish phrase is allowed. Masked away: heredoc bodies (<<WORD, <<'WORD',
# <<"WORD", <<-WORD, up to the terminator line), single-quoted and $'...' contents,
# double-quoted contents, and comments. A double-quoted string or unquoted heredoc body that
# holds a $(...) or backtick substitution stays as scannable text. Masking inserts no |, ; or &.
# Fails closed: the raw command is scanned (the pre-masking behavior) when python3 is missing
# or the masker errors, when a quote, heredoc, or $( is unterminated, when the command holds
# (( , or when a shell or evaluator (bash, sh, zsh, dash, ksh, eval, xargs, ssh, source, .,
# env) appears as a command word anywhere, so bash -c "...", cat <<EOF | sh, and eval stay blocked.
# It also scans the raw command on interpreter inline code: after masking, an interpreter word
# (python, python3, python3.12 and other versions, node, perl, ruby, path-qualified too, as in
# /usr/bin/python3) in command position followed, after any other options, by its inline-code
# flag: python -c; node -e, -p, --eval, --print; perl -e, -E; ruby -e (ruby -E is encoding, not
# code). The flag counts inside a short-option cluster (perl -ne, python3 -Sc). Options that
# take a separate value word may come before the flag (python3 -X dev -c, node --require x -e,
# perl -I lib -e); any other non-option word ends the option run. A plain
# python3 script.py keeps the masked scan, and an interpreter word inside quotes is masked away.
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
input=$(cat)
role=$(sdlc_role "$input")
[[ -n "$role" ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""' <<<"$input")
pattern='(^|[^[:alnum:]_-])(git[[:space:]]+push|gh[[:space:]]+(pr|issue)[[:space:]]+(create|merge|comment|edit|close|reopen|review|ready|delete)|gh[[:space:]]+release|gh[[:space:]]+api[^|;&]*(-X|--method)[[:space:]]*(POST|PATCH|PUT|DELETE)|(npm|pnpm|yarn)[[:space:]]+publish)'

# Masking only removes text, so a command whose raw text does not match is allowed as before.
grep -Eq "$pattern" <<<"$cmd" || exit 0

# Prints the masked command, or exits non-zero to make the hook scan the raw command.
read -r -d '' masker <<'PY' || true
import re, sys

cmd = sys.argv[1]
SHELL_WORD = (r'(?:^|[\s;&|(`{/])(?:bash|sh|zsh|dash|ksh|eval|xargs|ssh|source|\.|env)'
              r'(?=$|[\s;&|)`}<>])')
if re.search(SHELL_WORD, cmd) or '((' in cmd:
    sys.exit(1)


class Bad(Exception):
    pass


def dquote(s, i, end='"'):
    """Scan double-quoted text from i. Returns (index of end quote, holds a substitution)."""
    sub, n = False, len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            i += 2
            continue
        if end and c == end:
            return i, sub
        if s.startswith('$(', i):
            sub = True
            i = parse(s, i + 2, True, []) + 1
            continue
        if c == '`':
            sub = True
            j = i + 1
            while j < n and s[j] != '`':
                j += 2 if s[j] == '\\' else 1
            if j >= n:
                raise Bad
            i = j + 1
            continue
        i += 1
    if end:
        raise Bad
    return i, sub


def heredoc_word(s, i):
    strip = False
    if i < len(s) and s[i] == '-':
        strip, i = True, i + 1
    while i < len(s) and s[i] in ' \t':
        i += 1
    word, quoted = [], False
    while i < len(s) and s[i] not in ' \t\n;&|<>()':
        c = s[i]
        if c in '\'"':
            j = s.find(c, i + 1)
            if j < 0:
                raise Bad
            word.append(s[i + 1:j])
            quoted, i = True, j + 1
        elif c == '\\':
            word.append(s[i + 1:i + 2])
            quoted, i = True, i + 2
        else:
            word.append(c)
            i += 1
    if not word or not ''.join(word):
        raise Bad
    return i, (''.join(word), strip, quoted)


def bodies(s, i, pending, out):
    """Skip each pending heredoc body and its terminator line; return the next index."""
    for word, strip, quoted in pending:
        start = i
        while True:
            if i >= len(s):
                raise Bad
            j = s.find('\n', i)
            line_end = len(s) if j < 0 else j
            line = s[i:line_end]
            if (line.lstrip('\t') if strip else line) == word:
                body = s[start:i]
                if not quoted and dquote(body, 0, None)[1]:
                    out.append(body)
                i = line_end + 1 if j >= 0 else line_end
                break
            if j < 0:
                raise Bad
            i = j + 1
    return i


def parse(s, i, stop, out):
    """Unquoted text from i. With stop, return the index of the ) closing a $( ."""
    depth, pending, n = 0, [], len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            out.append(s[i:i + 2])
            i += 2
        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise Bad
            out.append("''")
            i = j + 1
        elif s.startswith("$'", i):
            j = i + 2
            while j < n and s[j] != "'":
                j += 2 if s[j] == '\\' else 1
            if j >= n:
                raise Bad
            out.append("$''")
            i = j + 1
        elif c == '"':
            j, sub = dquote(s, i + 1)
            out.append('"' + (s[i + 1:j] if sub else '') + '"')
            i = j + 1
        elif c == '#' and (i == 0 or s[i - 1] in ' \t\n;&|()<>'):
            j = s.find('\n', i)
            i = n if j < 0 else j
        elif s.startswith('<<<', i):
            out.append('<<<')
            i += 3
        elif s.startswith('<<', i):
            i, doc = heredoc_word(s, i + 2)
            pending.append(doc)
            out.append('<<W')
        elif c == '\n' and pending:
            out.append('\n')
            i = bodies(s, i + 1, pending, out)
            pending = []
        else:
            if stop and c == '(':
                depth += 1
            elif stop and c == ')':
                if depth == 0:
                    return i
                depth -= 1
            out.append(c)
            i += 1
    if stop or pending:
        raise Bad
    return i


try:
    masked = []
    parse(cmd, 0, False, masked)
except Exception:
    sys.exit(1)
masked = ''.join(masked)
# Options that take a separate value word (python3 -X dev -c): the value word joins the run.
VALOPTS = {
    'python': ['-X', '-W', '--check-hash-based-pycs'],
    'node': ['-r', '--require', '--import', '--loader', '--experimental-loader', '-C',
             '--conditions', '--input-type', '--title', '--env-file', '--inspect-port',
             '--max-http-header-size', '--openssl-config', '--redirect-warnings',
             '--stack-trace-limit', '--unhandled-rejections', '--disable-warning',
             '--diagnostic-dir', '--heapsnapshot-signal', '--icu-data-dir',
             '--report-dir', '--report-directory', '--report-filename', '--report-signal',
             '--secure-heap', '--secure-heap-min', '--tls-cipher-list', '--use-largepages',
             '--watch-path', '--experimental-policy', '--policy-integrity',
             '--cpu-prof-dir', '--cpu-prof-name', '--heap-prof-dir', '--heap-prof-name',
             '--dns-result-order', '--trace-event-categories', '--trace-event-file-pattern'],
    'perl': ['-I', '-M', '-m', '-x'],
    'ruby': ['-I', '-r', '-C', '-E', '-x', '-W'],
}
def opts(name):
    vals = '|'.join(re.escape(v) for v in sorted(VALOPTS[name], key=len, reverse=True))
    return r'(?:\s+(?:(?:' + vals + r')\s+\S+|-\S+))*?\s+'
INTERP = (r'(?:^|[\s;&|(`{/])(?:'
          r'python(?:\d+(?:\.\d+)*)?' + opts('python') + r'-[A-Za-z]*c(?![\w-])'
          r'|node' + opts('node') + r'(?:-[A-Za-z]*[ep](?![\w-])|--(?:eval|print)(?![\w-]))'
          r'|perl' + opts('perl') + r'-[A-Za-z]*[eE](?![\w-])'
          r'|ruby' + opts('ruby') + r'-[A-Za-z]*e(?![\w-])'
          r')')
if re.search(INTERP, masked):
    sys.exit(1)
sys.stdout.write(masked)
PY

scan=$(python3 -c "$masker" "$cmd" 2>/dev/null) || scan=$cmd
if grep -Eq "$pattern" <<<"$scan"; then
  echo "Blocked for sdlc role '$role': publishing is the user's call. Draft it in your final message instead." >&2
  exit 2
fi
exit 0
