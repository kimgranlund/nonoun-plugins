#!/usr/bin/env bash
# PreToolUse(Bash): inside a builder run (hooks/_role.sh resolves builder: SDLC_ROLE=builder, set by
# scripts/run.sh, else a sdlc-lite:builder-L<n> sub-agent's agent_type), block a
# repo-wide formatter, --fix linter, or format script, because builder rule 6 says to run
# them only on the files the step changed, with those paths passed explicitly.
# Blocked (exit 2):
#   a project format script: npm|pnpm|yarn|bun run <name>, bare pnpm|yarn|bun <name>, or
#   make <name>, where <name> is format, fmt, prettier, lint:fix, lint-fix, or fix, or starts
#   with format or fmt, unless explicit file paths follow (npm run format -- a.ts);
#   a formatter or fixer in write or fix mode whose targets are missing, or are a directory,
#   . or .., a glob (* or ?), a trailing /, a ./... package pattern, or a $ expansion:
#   prettier --write/-w, eslint --fix, black, ruff format, ruff check --fix, gofmt -w, go fmt,
#   cargo fmt (always, unless --check), rustfmt, biome format/check --write, dprint fmt,
#   stylelint --fix, clang-format -i.
# Allowed: the same tools on explicit file paths (prettier --write a.ts, eslint --fix
# src/a.ts src/b.ts), check-only modes (--check, --diff), other scripts (npm test), and text
# that only mentions the words inside a quoted argument (grep -n 'npm run format' f).
# A target counts as a file when it is an existing regular file, or when it does not exist as
# a directory and its last path part holds a dot after its first character. What a project
# script actually runs is never worked out: package.json and Makefiles are not read.
# Command position is the start of the command or after ; & | ( { ` or $( , optionally behind
# sudo, env, npx, bunx, pnpm/yarn/npm exec or dlx, yarn/pnpm/bun <tool>, command, nohup, exec,
# time, nice, timeout N, a VAR=value assignment, a shell keyword, or python -m.
# Masking follows block-pattern-kill.sh: quoted contents are kept only when they are one plain
# word, unquoted backslashes and comments are removed. Fails closed, scanning the raw text
# with a looser word match, when python3 is missing or errors, when a quote is unterminated,
# when the command holds a heredoc (<<), or when a shell or evaluator (bash, sh, zsh, dash,
# ksh, fish, eval, ssh, su) appears as a command word, so bash -c 'npm run format' is blocked.
# Every other role, and a session with no role, passes unchanged.
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
input=$(cat)
role=$(sdlc_role "$input")
[[ "$role" == builder ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""' <<<"$input")

# Cheap exit: no formatter or format-script word appears, even with quotes and backslashes
# removed.
pf=$(tr -d "\\\\'\"" <<<"$cmd")
[[ $pf == *format* || $pf == *fmt* || $pf == *fix* || $pf == *prettier* ||
  $pf == *black* || $pf == *ruff* || $pf == *biome* ]] || exit 0

block() {
  echo "Blocked for sdlc role '$role' by builder rule 6: a repo-wide formatter, --fix linter, or format script (no file arguments, or a directory, ., or a glob) rewrites files this step did not ask for. Run the formatter only on the files this step changed and pass those paths explicitly, for example prettier --write <paths> or npm run format -- <paths>." >&2
  exit 2
}

# Prints "block" or "ok" for the masked command, or exits non-zero to make the hook scan the
# raw command.
read -r -d '' analyzer <<'PY' || true
import os, re, sys

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
        nxt = cmd[i + 1:i + 2]
        out.append(' ' if nxt == '\n' else nxt)
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
masked = ''.join(out)

ASSIGN = re.compile(r'[A-Za-z_]\w*=')
REDIR = re.compile(r'\d*(?:>>?|<)&?')
KEYWORDS = {'then', 'do', 'else', 'elif', 'if', 'while', 'until', '!'}
WRAP_VALUE = {'sudo': {'-u', '-g', '-C', '-D', '-h', '-p', '-U'},
              'env': {'-u', '-C', '-S', '--unset', '--chdir'},
              'npx': {'-p', '--package', '-c', '--call'},
              'bunx': {'-p', '--package'},
              'timeout': {'-s', '-k', '--signal', '--kill-after'},
              'nice': {'-n', '--adjustment'}}
WRAPPERS = set(WRAP_VALUE) | {'command', 'nohup', 'exec', 'time'}
PM = {'npm', 'pnpm', 'yarn', 'bun'}
PM_VALUE = {'-C', '--prefix', '--dir', '--cwd', '--filter', '-F', '-w', '--workspace'}
MAKE_VALUE = {'-C', '-f', '-I', '-o', '-W', '--directory', '--file', '--makefile',
              '--include-dir', '--old-file', '--what-if', '--new-file', '--assume-new'}
FMT_NAMES = {'format', 'fmt', 'prettier', 'lint:fix', 'lint-fix', 'fix'}
VALUE_OPTS = {
    'prettier': {'--config', '--ignore-path', '--plugin', '--parser', '--log-level',
                 '--cache-location', '--cache-strategy', '--stdin-filepath',
                 '--config-precedence', '--end-of-line', '--print-width', '--tab-width',
                 '--trailing-comma', '--arrow-parens', '--prose-wrap', '--quote-props'},
    'eslint': {'-c', '--config', '--ext', '--rulesdir', '--resolve-plugins-relative-to',
               '--parser', '--parser-options', '--plugin', '--rule', '--env', '--global',
               '--ignore-path', '--ignore-pattern', '-f', '--format', '-o', '--output-file',
               '--max-warnings', '--cache-location', '--cache-strategy', '--fix-type',
               '--stdin-filename', '--flag'},
    'black': {'-l', '--line-length', '-t', '--target-version', '--config', '--include',
              '--exclude', '--extend-exclude', '--force-exclude', '--required-version',
              '-W', '--workers', '--python-cell-magics', '--stdin-filename'},
    'ruff': {'--config', '--select', '--ignore', '--extend-select', '--extend-ignore',
             '--fixable', '--unfixable', '--line-length', '--target-version', '--exclude',
             '--extend-exclude', '--stdin-filename', '--cache-dir', '--output-format'},
    'gofmt': {'-r'},
    'rustfmt': {'--edition', '--config-path', '--config', '--emit', '--color',
                '--style-edition'},
    'biome': {'--config-path', '--max-diagnostics', '--log-level', '--diagnostic-level',
              '--reporter', '--stdin-file-path'},
    'dprint': {'-c', '--config', '--excludes', '--includes', '--log-level'},
    'stylelint': {'-c', '--config', '--config-basedir', '--custom-syntax', '--ignore-path',
                  '--ignore-pattern', '-f', '--formatter', '--custom-formatter', '-o',
                  '--output-file', '--max-warnings', '--cache-location', '--stdin-filename'},
    'clang-format': {'--style', '-style', '--assume-filename', '--fallback-style'},
}
TOOLS = set(VALUE_OPTS) | {'go', 'cargo'}


def fmt_name(s):
    return s in FMT_NAMES or s.startswith('format') or s.startswith('fmt')


def filelike(t):
    if '*' in t or '?' in t or '$' in t or t in ('.', '..'):
        return False
    if t.endswith('/') or t.endswith('...'):
        return False
    if os.path.isdir(t):
        return False
    if os.path.isfile(t):
        return True
    return '.' in t.rsplit('/', 1)[-1].lstrip('.')


def positional(args, vopts=frozenset()):
    res, i, after = [], 0, False
    while i < len(args):
        a = args[i]
        if not after and a == '--':
            after = True
        elif not after and a.startswith('-') and len(a) > 1:
            if (a in vopts and i + 1 < len(args)
                    and not args[i + 1].startswith('-')):
                i += 1
        else:
            res.append(a)
        i += 1
    return res


def bad_targets(ts):
    return not ts or not all(filelike(t) for t in ts)


def skip_opts(args, vopts, i=0):
    while i < len(args) and args[i].startswith('-') and args[i] != '--':
        i += 2 if args[i] in vopts else 1
    return i


def strip_wrappers(t):
    i = 0
    while i < len(t):
        w = t[i]
        base = w.rsplit('/', 1)[-1]
        if ASSIGN.match(w) or w in KEYWORDS:
            i += 1
        elif base in WRAPPERS:
            vopts = WRAP_VALUE.get(base, set())
            i += 1
            while i < len(t) and (t[i].startswith('-') or ASSIGN.match(t[i])):
                i += 2 if t[i] in vopts else 1
            if base == 'timeout' and i < len(t):
                i += 1
        elif (base in PM and i + 1 < len(t)
              and t[i + 1] in ('exec', 'dlx', 'x')):
            i = skip_opts(t, {'-p', '--package'}, i + 2)
        else:
            break
    return t[i:]


def tool(base, args):
    if any(a in ('--version', '--help', '-h') for a in args):
        return False
    vopts = VALUE_OPTS.get(base, frozenset())
    if base == 'prettier':
        return ('--write' in args or '-w' in args) and bad_targets(positional(args, vopts))
    if base in ('eslint', 'stylelint'):
        return '--fix' in args and bad_targets(positional(args, vopts))
    if base == 'black':
        return (not {'--check', '--diff'} & set(args)
                and bad_targets(positional(args, vopts)))
    if base == 'rustfmt':
        return '--check' not in args and bad_targets(positional(args, vopts))
    if base == 'gofmt':
        return '-w' in args and bad_targets(positional(args, vopts))
    if base == 'clang-format':
        return ('-i' in args or '--i' in args) and bad_targets(positional(args, vopts))
    pos = positional(args, vopts)
    sub, rest = (pos[0], pos[1:]) if pos else (None, [])
    if base == 'ruff':
        if '--diff' in args:
            return False
        if sub == 'format':
            return '--check' not in args and bad_targets(rest)
        if sub in ('rule', 'config', 'version', 'server', 'clean', 'analyze'):
            return False
        fix = '--fix' in args or '--fix-only' in args
        return fix and bad_targets(rest if sub == 'check' else pos)
    if base == 'biome':
        write = {'--write', '--fix', '--apply', '--apply-unsafe'} & set(args)
        return sub in ('format', 'check') and bool(write) and bad_targets(rest)
    if base == 'dprint':
        return sub == 'fmt' and bad_targets(rest)
    if base == 'go':
        return sub == 'fmt' and bad_targets(rest)
    if base == 'cargo':
        subs = [a for a in pos if not a.startswith('+')]
        return bool(subs) and subs[0] == 'fmt' and '--check' not in args
    return False


def segment(tokens):
    toks, i = [], 0
    while i < len(tokens):
        m = REDIR.match(tokens[i])
        if m:
            i += 1 if m.end() < len(tokens[i]) else 2
            continue
        toks.append(tokens[i])
        i += 1
    t = strip_wrappers(toks)
    if not t:
        return False
    base, args = t[0].rsplit('/', 1)[-1], t[1:]
    if base in ('python', 'python3') and len(args) >= 2 and args[0] == '-m':
        base, args = args[1], args[2:]
    if base in PM:
        j = skip_opts(args, PM_VALUE)
        if j >= len(args):
            return False
        sub = args[j]
        if sub in ('run', 'run-script'):
            k = skip_opts(args, PM_VALUE, j + 1)
            return (k < len(args) and fmt_name(args[k])
                    and bad_targets(positional(args[k + 1:])))
        if base != 'npm' and fmt_name(sub):
            return bad_targets(positional(args[j + 1:]))
        if base != 'npm' and sub in TOOLS:
            return tool(sub, args[j + 1:])
        return False
    if base in ('make', 'gmake'):
        pos, i = [], 0
        while i < len(args):
            a = args[i]
            if a.startswith('-'):
                i += 2 if a in MAKE_VALUE else 1
                continue
            if not ASSIGN.match(a) and not a.isdigit():
                pos.append(a)
            i += 1
        for k, a in enumerate(pos):
            if fmt_name(a):
                return bad_targets(pos[k + 1:])
        return False
    if base in TOOLS:
        return tool(base, args)
    return False


segs = re.split(r'\$\(|&&|\|\||[;&|(){}`\n]', masked)
print('block' if any(segment(s.split()) for s in segs) else 'ok')
PY

if verdict=$(python3 -c "$analyzer" "$cmd" 2>/dev/null); then
  [[ $verdict == block ]] && block
  [[ $verdict == ok ]] && exit 0
fi

# Fail closed: a looser word match on the raw text. It ignores targets, so an explicit file
# path inside bash -c or a heredoc is blocked too.
word='(^|[^[:alnum:]_-])'
wend='([^[:alnum:]_-]|$)'
tok='([[:space:]]+[^[:space:];&|]+)*[[:space:]]+'
names='((format|fmt)[[:alnum:]_:-]*|prettier|lint[:-]fix|fix)([^[:alnum:]_:-]|$)'
loose="${word}(npm|pnpm|yarn|bun|make)${tok}${names}"
loose+="|${word}prettier[[:space:]]([^;&|]*[[:space:]])?(--write|-w)${wend}"
loose+="|${word}(eslint|stylelint)${wend}[^;&|]*--fix${wend}"
loose+="|${word}(black|rustfmt)${wend}"
loose+="|${word}ruff[[:space:]]([^;&|]*[[:space:]])?(format|--fix|--fix-only)${wend}"
loose+="|${word}gofmt[[:space:]]([^;&|]*[[:space:]])?-w${wend}"
loose+="|${word}(go|cargo|dprint)${tok}fmt${wend}"
loose+="|${word}biome${wend}[^;&|]*--(write|fix|apply)"
loose+="|${word}clang-format[[:space:]]([^;&|]*[[:space:]])?--?i${wend}"
raw=$(tr -d '\\' <<<"$cmd" | tr '\n' ' ')
grep -Eq "$loose" <<<"$raw" && block
exit 0
