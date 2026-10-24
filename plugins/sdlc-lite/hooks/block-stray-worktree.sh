#!/usr/bin/env bash
# PreToolUse(Bash): inside a role run (a role from hooks/_role.sh: SDLC_ROLE set by scripts/run.sh
# or fanout, else the sub-agent's agent_type), block a
# git worktree add that would leave a worktree or branch behind when the run ends. run.sh
# removes only the worktrees under $SDLC_TMP_WORKTREES and never deletes a branch. For each
# git worktree add (git global options such as -C <dir> may sit between git and worktree) it
# denies: -b, -B, or --orphan (they create a branch); an unset or empty SDLC_TMP_WORKTREES (a
# conductor has SDLC_ROLE but no prefix); a path that is not strictly under the prefix (a
# literal $SDLC_TMP_WORKTREES or ${SDLC_TMP_WORKTREES} in the path is expanded only when that variable is set and
# non-empty in the hook's environment, else it is denied since the shell expands it to an empty string (T-0708), a relative path
# is resolved against the hook JSON's cwd, else $PWD, and against -C; a path with a .. segment,
# an unresolved expansion, or a relative path after cd is denied); and any add without
# --detach/-d. Without --detach git can create a branch through DWIM (a name that exists only
# on a remote becomes a new tracking branch, no commit makes one named after the path) or check
# out an existing branch; with --detach it skips all branch DWIM whatever refs exist, so the
# rule stays textual and the hook never queries the repo.
# For a sub-agent role (no SDLC_ROLE) with no prefix variable, the prefix is `wtroot.py root --cwd <hook JSON's cwd>`
# plus /tmp, the parent of every dispatch tmp prefix: the sibling <main checkout>.worktrees/tmp outside the repo (never a
# lane, T-0550, T-0563), or under a worktree_root: line or a bare clone's <bare parent>/lanes (T-0561).
# The legacy <main checkout>/.claude/worktrees/tmp is denied; a session with no role may still add host-owned trees there.
# Allowed: git worktree add --detach "$SDLC_TMP_WORKTREES/<name>" <commit>, every other git
# worktree subcommand (list, remove, prune), a mention inside a quoted argument
# (grep -n "git worktree add" f), and anything outside a role run.
#
# Parsing: a small shell tokenizer removes quotes, splits commands at ; & | ( ) and newlines,
# drops comments and redirections, and also parses the inside of $(...) and backticks, so a
# quoted mention stays one word and never reads as a command. Fails closed, scanning the raw
# text and denying any git ... worktree add, when python3 is missing or the parser errors, when
# a quote is unterminated, when the command holds a heredoc (<<), or when a shell or evaluator
# (bash, sh, zsh, dash, ksh, fish, eval, ssh, su) appears as a command word, so
# bash -c "git worktree add /tmp/x HEAD" stays blocked.
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
json=$(cat)
role=$(sdlc_role "$json")
[[ -n "$role" ]] || exit 0
cmd=$(jq -r '.tool_input.command // ""' <<<"$json")

# Cheap exit: the word does not appear even with quotes and backslashes removed.
pf=$(tr -d "\\\\'\"" <<<"$cmd")
[[ $pf == *worktree* ]] || exit 0

cwd=$(jq -r '.cwd // ""' <<<"$json")
[[ -n $cwd ]] || cwd=$PWD
prefix=${SDLC_TMP_WORKTREES:-}
# A sub-agent has no per-run prefix in its environment: its dispatch brief names <worktree root>/tmp/<name>,
# the root from wtroot.py (the sibling <main checkout>.worktrees, T-0563, a worktree_root: line, or a bare clone's
# <bare parent>/lanes, T-0561), so any path under that tmp dir passes for it.
if [[ -z $prefix && -z "${SDLC_ROLE:-}" ]]; then
  top=$(python3 "$(dirname "${BASH_SOURCE[0]}")/../scripts/wtroot.py" root --cwd "$cwd" 2>/dev/null) || top=""
  [[ -n $top ]] && prefix="$top/tmp"
fi

block() {
  # A sub-agent has no SDLC_TMP_WORKTREES in its shell, so it is shown the literal prefix, never the variable (T-0735).
  # shellcheck disable=SC2016
  local form='$SDLC_TMP_WORKTREES'
  [[ -n "${SDLC_TMP_WORKTREES:-}" ]] || form=${prefix:-<the throwaway prefix your brief names>}
  echo "Blocked for sdlc role '$role': $1. The run removes only detached worktrees under its throwaway prefix (${prefix:-unset}) when it ends and never deletes a branch. Use the allowed form: git worktree add --detach \"$form/<name>\" <commit>. Never create a branch (-b, -B, --orphan) or a worktree anywhere else. To open or close a lane (a worktree with its branch), run python3 scripts/lanes.py open <name> or python3 scripts/lanes.py close <name>; the conductor, not a role, owns that." >&2
  exit 2
}

# Prints one reason per stray git worktree add (nothing when all are allowed), or exits
# non-zero to make the hook scan the raw command.
read -r -d '' checker <<'PY' || true
import posixpath, re, sys

cmd, prefix, cwd, varset = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == '1'
SHELL_WORD = (r'(?:^|[\s;&|(`{/])(?:bash|sh|zsh|dash|ksh|fish|eval|ssh|su)'
              r'(?=$|[\s;&|)`}<>])')
if re.search(SHELL_WORD, cmd) or re.search(r'<<(?!<)', cmd):
    sys.exit(1)

REDIR = '\0redir'


class Unparsable(Exception):
    pass


def skip_dquote(s, j):
    """s[j] is '"'; returns the index after the closing quote."""
    k = j + 1
    while k < len(s) and s[k] != '"':
        k += 2 if s[k] == '\\' else 1
    if k >= len(s):
        raise Unparsable
    return k + 1


def close_paren(s, j):
    """j is just after '$('; returns the index of the matching ')'."""
    depth = 1
    while j < len(s):
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == "'":
            k = s.find("'", j + 1)
            if k < 0:
                raise Unparsable
            j = k + 1
            continue
        if c == '"':
            j = skip_dquote(s, j)
            continue
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise Unparsable


def close_tick(s, j):
    """j is just after '`'; returns the index of the closing backtick."""
    while j < len(s) and s[j] != '`':
        j += 2 if s[j] == '\\' else 1
    if j >= len(s):
        raise Unparsable
    return j


def parse(s, cmds):
    """Appends each simple command in s to cmds as a list of words."""
    cur, word, has = [], [], False
    i, n = 0, len(s)

    def end_word():
        nonlocal word, has
        if has:
            cur.append(''.join(word))
        word, has = [], False

    def end_cmd():
        nonlocal cur
        end_word()
        if cur:
            cmds.append(cur)
        cur = []

    while i < n:
        c = s[i]
        if c == '\\':
            if i + 1 < n and s[i + 1] != '\n':
                word.append(s[i + 1])
                has = True
            i += 2
        elif s.startswith("$'", i):
            j = s.find("'", i + 2)
            if j < 0 or '\\' in s[i + 2:j]:
                raise Unparsable
            word.append(s[i + 2:j])
            has = True
            i = j + 1
        elif c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise Unparsable
            word.append(s[i + 1:j])
            has = True
            i = j + 1
        elif c == '"':
            i = dquote(s, i + 1, word, cmds)
            has = True
        elif s.startswith('$(', i):
            j = close_paren(s, i + 2)
            parse(s[i + 2:j], cmds)
            word.append(s[i:j + 1])
            has = True
            i = j + 1
        elif s.startswith('${', i):
            j = s.find('}', i)
            if j < 0:
                raise Unparsable
            word.append(s[i:j + 1])
            has = True
            i = j + 1
        elif c == '`':
            j = close_tick(s, i + 1)
            parse(s[i + 1:j], cmds)
            word.append(s[i:j + 1])
            has = True
            i = j + 1
        elif c in ';&|()\n':
            end_cmd()
            i += 1
        elif c in ' \t\r':
            end_word()
            i += 1
        elif c in '<>':
            if has and ''.join(word).isdigit():
                word, has = [], False
            end_word()
            while i < n and s[i] in '<>&|':
                i += 1
            cur.append(REDIR)
        elif c == '#' and not has:
            j = s.find('\n', i)
            i = n if j < 0 else j
        else:
            word.append(c)
            has = True
            i += 1
    end_cmd()


def dquote(s, i, word, cmds):
    """i is just after an opening '"'; returns the index after the closing one."""
    n = len(s)
    while i < n and s[i] != '"':
        c = s[i]
        if c == '\\' and i + 1 < n:
            nxt = s[i + 1]
            if nxt in '$`"\\':
                word.append(nxt)
            elif nxt != '\n':
                word.append(c + nxt)
            i += 2
        elif s.startswith('$(', i):
            j = close_paren(s, i + 2)
            parse(s[i + 2:j], cmds)
            word.append(s[i:j + 1])
            i = j + 1
        elif c == '`':
            j = close_tick(s, i + 1)
            parse(s[i + 1:j], cmds)
            word.append(s[i:j + 1])
            i = j + 1
        else:
            word.append(c)
            i += 1
    if i >= n:
        raise Unparsable
    return i + 1


VAR = re.compile(r'\$(?:\{SDLC_TMP_WORKTREES\}|SDLC_TMP_WORKTREES(?![A-Za-z0-9_]))')
GIT_ARG_OPTS = {'-C', '-c', '--git-dir', '--work-tree', '--namespace',
                '--super-prefix', '--config-env'}


def expand(p):
    # The shell expands the variable from its own environment, so the hook substitutes the prefix only when
    # the variable is set and non-empty in the hook process; unset, it stays literal and reads as unresolved.
    return VAR.sub(lambda m: prefix, p) if varset else p


def unresolved(p):
    return p.startswith('~') or any(ch in p for ch in '$`*?[')


def check_add(args, base, moved):
    """args follow 'git ... worktree add'; returns the reasons to deny."""
    reasons, pos, detach, i = [], [], False, 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == REDIR:
            i += 1
        elif a == '--':
            pos.extend(x for x in args[i:] if x != REDIR)
            break
        elif a.startswith('--'):
            name = a[2:].split('=', 1)[0]
            if name and 'orphan'.startswith(name):
                reasons.append(f'{a} creates a branch, which the run never deletes')
            elif name and 'detach'.startswith(name):
                detach = True
            elif len(name) >= 3 and 'reason'.startswith(name) and '=' not in a:
                i += 1
        elif a.startswith('-') and len(a) > 1:
            if 'b' in a or 'B' in a:
                reasons.append(f'{a} creates a branch, which the run never deletes')
                i += 1
            elif 'd' in a:
                detach = True
        else:
            pos.append(a)
    if not prefix:
        reasons.append('SDLC_TMP_WORKTREES is unset, so this session has no throwaway worktree prefix')
        return reasons
    if not pos:
        reasons.append('git worktree add names no path')
        return reasons
    path = expand(pos[0])
    root = posixpath.normpath(prefix)
    if not varset and VAR.search(pos[0]):
        reasons.append(f'the path {pos[0]} uses $SDLC_TMP_WORKTREES, which is unset where the shell runs it, so it expands to an empty string; write the literal prefix from the brief')
    elif unresolved(path):
        reasons.append(f'the path {pos[0]} cannot be resolved before it runs (the hook expands no variable except $SDLC_TMP_WORKTREES, so write "$SDLC_TMP_WORKTREES/<name>" or a literal path under it)')
    elif '..' in path.split('/'):
        reasons.append(f'the path {pos[0]} has a .. segment')
    elif not path.startswith('/') and (moved or base is None):
        reasons.append(f'the relative path {pos[0]} follows a cd or an unresolved -C')
    else:
        full = posixpath.normpath(posixpath.join(base or '/', path))
        if not full.startswith(root.rstrip('/') + '/'):
            reasons.append(f'the path {full} is not under $SDLC_TMP_WORKTREES ({prefix})')
    if not detach:
        reasons.append('without --detach git can create a branch (a name that exists only on a remote becomes a new tracking branch, no commit makes one named after the path) or check out an existing branch')
    return reasons


def check(words, moved):
    reasons = []
    for i, w in enumerate(words):
        if w == REDIR or posixpath.basename(w) != 'git':
            continue
        j, base = i + 1, cwd
        while j < len(words) and words[j] != REDIR and words[j].startswith('-'):
            opt = words[j]
            j += 1
            if opt in GIT_ARG_OPTS and j < len(words):
                if opt == '-C':
                    d = expand(words[j])
                    base = None if base is None or unresolved(d) else posixpath.join(base, d)
                j += 1
        if words[j:j + 2] == ['worktree', 'add']:
            reasons += check_add(words[j + 2:], base, moved)
    return reasons


try:
    cmds = []
    parse(cmd, cmds)
except Unparsable:
    sys.exit(1)
reasons, moved = [], False
for words in cmds:
    reasons += check(words, moved)
    first = next((w for w in words if w != REDIR), '')
    if posixpath.basename(first) in ('cd', 'pushd', 'popd'):
        moved = True
sys.stdout.write('; '.join(reasons))
PY

if found=$(python3 -c "$checker" "$cmd" "$prefix" "$cwd" "${SDLC_TMP_WORKTREES:+1}" 2>/dev/null); then
  [[ -n $found ]] && block "$found"
  exit 0
fi
raw=$(tr -d '\\' <<<"$cmd" | tr '\n' ' ')
word='(^|[^[:alnum:]_-])'
wend='([^[:alnum:]_-]|$)'
grep -Eq "${word}git[^[:alnum:]_-](.*[^[:alnum:]_-])?worktree[[:space:]]+add${wend}" <<<"$raw" &&
  block "a git worktree add the hook cannot parse safely (a shell or evaluator word, a heredoc, an unterminated quote, or no python3)"
exit 0
