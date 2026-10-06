#!/usr/bin/env bash
# PreToolUse(Bash): inside a role run (SDLC_ROLE set by scripts/run.sh or fanout), block a
# search of the whole filesystem or a home folder, because it can run for many minutes with no
# output and stall the run (| head does not stop it when nothing matches).
# Blocked (exit 2): a search command in command position with a path operand that is exactly
# /, /*, ~, ~/, $HOME, ${HOME}, $HOME/, ${HOME}/, /Users, /home, /Volumes, /System, /Library,
# /private (a trailing / allowed), or a home folder itself (/Users/<name>, /home/<name>).
# The search commands are find, bfs, fd, fdfind, rg, ag, grep or egrep with -r, -R, or
# --recursive (also in a short-flag cluster such as -rn), du, ls -R, and tree. For grep, rg,
# ag, fd, and fdfind the first positional word is the pattern, not a path, unless the pattern
# comes from an option (-e, -f, rg --files, ag -g); fd --search-path and --base-directory
# values count as paths. For find only the starting points before the expression count.
# Command position is the start of the command or after ; & | ( { ` or $( , optionally
# behind sudo, command, env, nohup, exec, time, nice, stdbuf, timeout N, xargs, a VAR=value
# assignment, or a shell keyword. Every such search is blocked, with or without -maxdepth.
# Allowed: a path below those roots (/tmp/x, ~/.claude/plugins, "$HOME/.claude/plugins",
# /Users/me/Projects/x), . and relative paths, ls / without -R, text that only mentions a
# search inside a quoted argument (grep -n "find / -name x" f), and anything with no role.
#
# Masking follows block-pattern-kill.sh: single-quoted, $'...' and double-quoted contents are
# kept when they are one plain word or only "$VAR", "${VAR}" (a trailing / allowed), and
# otherwise replaced by one placeholder word so the positions of the other words hold;
# unquoted backslashes and comments are removed. Fails closed, scanning the raw text with a
# looser match, when python3 is missing or errors, when a quote is unterminated, when the
# command holds a heredoc (<<), or when a shell or evaluator (bash, sh, zsh, dash, ksh, fish,
# eval, ssh, su) appears as a command word, so bash -c "find / -name x" stays blocked.
[[ -n "${SDLC_ROLE:-}" ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""')

# Cheap exit: no search command word appears, even with quotes and backslashes removed.
pf=$(tr -d "\\\\'\"" <<<"$cmd")
re='(^|[^[:alnum:]_-])(find|bfs|fd|fdfind|rg|ag|e?grep|du|ls|tree)([^[:alnum:]_-]|$)'
[[ $pf =~ $re ]] || exit 0

block() {
  echo "Blocked for sdlc role '$SDLC_ROLE': searching the whole filesystem or a home folder (find /, find ~, rg x /, grep -r x \$HOME, du /, ls -R /, tree /) can run for many minutes with no output and stall the run; | head does not stop it when nothing matches. Search a bounded path instead: the repository (.), a named subfolder such as ~/.claude/plugins, or \$CLAUDE_PLUGIN_ROOT." >&2
  exit 2
}

# Prints "block" or "ok" for the masked command, or exits non-zero to make the hook scan the
# raw command.
read -r -d '' analyzer <<'PY' || true
import re, sys

cmd = sys.argv[1]
SHELL_WORD = (r'(?:^|[\s;&|(`{/])(?:bash|sh|zsh|dash|ksh|fish|eval|ssh|su)'
              r'(?=$|[\s;&|)`}<>])')
if re.search(SHELL_WORD, cmd) or re.search(r'<<(?!<)', cmd):
    sys.exit(1)
PLAIN = re.compile(r'[A-Za-z0-9_./=:+,@%-]*\Z')
VAR = re.compile(r'\$(?:[A-Za-z_]\w*|\{[A-Za-z_]\w*\})/?\Z')
HOLE = ' __quoted__ '
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
        out.append(body if PLAIN.match(body) else HOLE)
        i = j + 1
    elif c == '"':
        j = i + 1
        while j < n and cmd[j] != '"':
            j += 2 if cmd[j] == '\\' else 1
        if j >= n:
            sys.exit(1)
        body = cmd[i + 1:j]
        if PLAIN.match(body) or VAR.match(body):
            out.append(body)
        elif '$(' in body or '`' in body:
            out.append(' ' + body + ' ')
        else:
            out.append(HOLE)
        i = j + 1
    elif c == '#' and (i == 0 or cmd[i - 1] in ' \t\n;&|()<>'):
        j = cmd.find('\n', i)
        i = n if j < 0 else j
    else:
        out.append(c)
        i += 1
masked = ''.join(out)

ROOT = re.compile(r'(?:/|/\*|//|~/?|\$HOME/?|\$\{HOME\}/?'
                  r'|/(?:Users|home|Volumes|System|Library|private)/?'
                  r'|/(?:Users|home)/[^/\s]+/?)\Z')
ASSIGN = re.compile(r'[A-Za-z_]\w*=')
REDIR = re.compile(r'\d*(?:>>?|<)&?')
KEYWORDS = {'then', 'do', 'else', 'elif', 'if', 'while', 'until', '!'}
WRAP_VALUE = {'sudo': {'-u', '-g', '-C', '-D', '-h', '-p', '-U'},
              'env': {'-u', '-C', '-S', '--unset', '--chdir'},
              'timeout': {'-s', '-k', '--signal', '--kill-after'},
              'nice': {'-n', '--adjustment'},
              'stdbuf': {'-i', '-o', '-e'},
              'xargs': {'-I', '-n', '-P', '-L', '-d', '-E', '-s', '-a', '--arg-file',
                        '--delimiter', '--max-args', '--max-procs', '--max-lines',
                        '--max-chars', '--eof', '--replace'}}
WRAPPERS = set(WRAP_VALUE) | {'command', 'nohup', 'exec', 'time'}
GREP_VALUE = {'-e', '--regexp', '-f', '--file', '-m', '--max-count', '-A', '-B', '-C',
              '--after-context', '--before-context', '--context', '--include', '--exclude',
              '--exclude-dir', '--exclude-from', '--label', '--color', '--colour', '-d',
              '--directories', '-D', '--devices', '--binary-files', '--group-separator'}
RG_VALUE = {'-e', '--regexp', '-f', '--file', '-g', '--glob', '--iglob', '-t', '--type',
            '-T', '--type-not', '--type-add', '--type-clear', '-m', '--max-count', '-A',
            '-B', '-C', '--after-context', '--before-context', '--context', '-j',
            '--threads', '-M', '--max-columns', '-E', '--encoding', '-r', '--replace', '-d',
            '--max-depth', '--maxdepth', '--pre', '--pre-glob', '--sort', '--sortr',
            '--max-filesize', '--color', '--colors', '--context-separator',
            '--field-context-separator', '--field-match-separator', '--path-separator',
            '--ignore-file', '--engine', '--dfa-size-limit', '--regex-size-limit'}
AG_VALUE = {'-G', '--file-search-regex', '-g', '-A', '-B', '-C', '--after', '--before',
            '--context', '-m', '--max-count', '--depth', '--ignore', '--ignore-dir',
            '-p', '--path-to-ignore', '--pager', '-W', '--width'}
FD_VALUE = {'-e', '--extension', '-t', '--type', '-E', '--exclude', '-d', '--max-depth',
            '--min-depth', '--exact-depth', '-j', '--threads', '-S', '--size',
            '--changed-within', '--changed-before', '-o', '--owner', '-c', '--color',
            '--format', '--ignore-file', '--max-results', '--path-separator',
            '--search-path', '--base-directory', '--batch-size'}
FD_PATH_OPTS = {'--search-path', '--base-directory'}
DU_VALUE = {'-d', '--max-depth', '-B', '--block-size', '-t', '--threshold', '--exclude',
            '-X', '--exclude-from', '--time-style'}
TREE_VALUE = {'-L', '-P', '-I', '-o', '-H', '-T', '--charset', '--filelimit', '--timefmt',
              '--sort', '--fromfile'}


def is_root(t):
    return bool(ROOT.match(t))


def short_flag(args, letters):
    for a in args:
        if a == '--':
            break
        if a.startswith('-') and not a.startswith('--') and len(a) > 1:
            if any(ch in letters for ch in a[1:]):
                return True
    return False


def positional(args, vopts):
    res, vals, i, after = [], [], 0, False
    while i < len(args):
        a = args[i]
        if not after and a == '--':
            after = True
        elif not after and a.startswith('-') and len(a) > 1:
            if '=' in a and a.startswith('--'):
                vals.append((a.split('=', 1)[0], a.split('=', 1)[1]))
            elif a in vopts and i + 1 < len(args):
                vals.append((a, args[i + 1]))
                i += 1
        else:
            res.append(a)
        i += 1
    return res, vals


def pattern_tool(args, vopts, pattern_opts):
    pos, vals = positional(args, vopts)
    if not any(o in pattern_opts for o, _ in vals) and not (set(args) & pattern_opts):
        pos = pos[1:]
    return any(is_root(p) for p in pos)


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
        else:
            break
    return t[i:]


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
    if base == 'find':
        i = 0
        while i < len(args) and args[i] in ('-H', '-L', '-P', '-D') or (
                i < len(args) and re.match(r'-O\d*\Z', args[i])):
            i += 2 if args[i] == '-D' else 1
        for a in args[i:]:
            if a.startswith('-') or a in ('!', ','):
                break
            if is_root(a):
                return True
        return False
    if base == 'bfs':
        return any(is_root(a) for a in args)
    if base in ('grep', 'egrep'):
        rec = short_flag(args, 'rR') or any(
            a in ('--recursive', '--dereference-recursive') for a in args)
        return rec and pattern_tool(args, GREP_VALUE, {'-e', '--regexp', '-f', '--file'})
    if base == 'rg':
        return pattern_tool(args, RG_VALUE,
                            {'-e', '--regexp', '-f', '--file', '--files', '--type-list'})
    if base == 'ag':
        return pattern_tool(args, AG_VALUE, {'-g'})
    if base in ('fd', 'fdfind'):
        pos, vals = positional(args, FD_VALUE)
        if any(o in FD_PATH_OPTS and is_root(v) for o, v in vals):
            return True
        return any(is_root(p) for p in pos[1:])
    if base == 'du':
        return any(is_root(p) for p in positional(args, DU_VALUE)[0])
    if base == 'tree':
        return any(is_root(p) for p in positional(args, TREE_VALUE)[0])
    if base == 'ls':
        rec = short_flag(args, 'R') or '--recursive' in args
        return rec and any(is_root(p) for p in positional(args, set())[0])
    return False


masked = re.sub(r'\$\{([A-Za-z_]\w*)\}', r'$\1', masked)
segs = re.split(r'\$\(|&&|\|\||[;&|()`\n]|(?:^|(?<=\s))[{}](?=[\s;]|$)', masked)
print('block' if any(segment(s.split()) for s in segs) else 'ok')
PY

if verdict=$(python3 -c "$analyzer" "$cmd" 2>/dev/null); then
  [[ $verdict == block ]] && block
  [[ $verdict == ok ]] && exit 0
fi

# Fail closed: a looser match on the raw text. A search word, then in the same pipeline stage
# a root operand as a whole word, optionally quoted; grep needs a recursive flag and ls -R.
# A root or flag match ends by taking one separator, so the next one may start right there.
word='(^|[^[:alnum:]_-])'
sp='[[:space:]]+'
tok='[^[:space:];&|]+'
more="(${sp}${tok})*${sp}"
tend="([[:space:];&|)\`\"']|$)"
rt="[\"']?(/|/\\*|//|~/?|\\\$HOME/?|\\\$\\{HOME\\}/?|/(Users|home|Volumes|System|Library|private)/?|/(Users|home)/[^/[:space:];&|)\"'\`]+/?)[\"']?${tend}"
gr="(-[[:alpha:]]*[rR][[:alpha:]]*|--recursive|--dereference-recursive)${tend}"
lr="(-[[:alpha:]]*R[[:alpha:]]*|--recursive)${tend}"
loose="${word}(find|bfs|fd|fdfind|rg|ag|du|tree)${more}${rt}"
loose+="|${word}e?grep${more}${gr}([^;&|]*[[:space:]])?${rt}"
loose+="|${word}e?grep${more}${rt}([^;&|]*[[:space:]])?${gr}"
loose+="|${word}ls${more}${lr}([^;&|]*[[:space:]])?${rt}"
loose+="|${word}ls${more}${rt}([^;&|]*[[:space:]])?${lr}"
raw=$(tr -d '\\' <<<"$cmd" | tr '\n' ' ')
grep -Eq "$loose" <<<"$raw" && block
exit 0
