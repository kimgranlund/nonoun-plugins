#!/usr/bin/env bash
# PreToolUse(Bash) hook (T-0876, #98; Claude Code only, Codex runs no hooks). Opt-in: it acts only when the
# repository's .sdlc/config has a `risky_paths: <glob> [<glob>...]` line (git :(glob) pathspecs from the repo
# root, parsed like hash_bound:; hash_bound: alone does not turn it on). It is silent for a role (_role.sh) and
# for a headless session (SDLC_HEADLESS=1), where no user is there to answer an offer.
# For a `git commit` or `git merge <ref>` in command position whose paths match a glob (commit: the staged paths,
# plus tracked changes with -a and worktree changes and untracked files when a `git add` runs earlier in the same
# command; merge: git diff --name-only HEAD...<ref>), it prints hookSpecificOutput.additionalContext asking the
# model to offer /sdlc:verify once in one line, and writes a marker under the git dir keyed by the sorted hit
# paths and the staged tree (with the worktree blob ids in the -a or git add case) or the merged ref's sha, so
# the same change is reminded once. Never blocks: it prints no permission decision and always exits 0.
set -uo pipefail
input="$(cat)"
# Cheap bail for the common case: one glob match per word, linear in the command length.
[[ "$input" == *git* ]] || exit 0
[[ "$input" == *commit* || "$input" == *merge* ]] || exit 0
[[ "${SDLC_HEADLESS:-}" == 1 ]] && exit 0
command -v python3 >/dev/null 2>&1 && command -v git >/dev/null 2>&1 || exit 0
# shellcheck source=_role.sh
. "$(dirname "${BASH_SOURCE[0]}")/_role.sh"
[[ -z "$(sdlc_role "$input")" ]] || exit 0
SDLC_RISKY_INPUT="$input" python3 - <<'PY' 2>/dev/null || true
import hashlib, json, os, re, shlex, subprocess, sys

RISKY_RE = re.compile(r'\s*risky_paths\s*:\s*([^#]*?)\s*(?:#.*)?')
SEP = set(';&|()')
PREFIX = {'command', 'env', 'sudo', 'nohup', 'time', 'exec'}
GIT_VAL_OPTS = {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--super-prefix', '--config-env'}
MERGE_VAL_OPTS = {'-m', '-F', '-s', '-X', '--strategy', '--strategy-option', '--file', '--into-name', '--cleanup'}
MERGE_STOP = {'--abort', '--continue', '--quit', '--skip'}


def git(repo, *args):
    r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, timeout=10)
    return r.stdout if r.returncode == 0 else None


def globs(top):
    path = os.path.join(top, '.sdlc', 'config')
    out = []
    try:
        lines = open(path, encoding='utf-8').read().splitlines()
    except OSError:
        return out
    for line in lines:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = RISKY_RE.fullmatch(line)
        for g in (m.group(1).split() if m else []):
            if g not in out:
                out.append(g)
    return out


def commands(cmd):
    """Simple commands as word lists, split at ; & | ( ) and newlines. A command that does not tokenize gives none."""
    lex = shlex.shlex(cmd.replace('\n', ' ; '), posix=True, punctuation_chars=';&|()')
    lex.whitespace_split = True
    cur, out = [], []
    try:
        for tok in lex:
            if tok and set(tok) <= SEP:
                if cur:
                    out.append(cur)
                cur = []
            else:
                cur.append(tok)
    except ValueError:
        return []
    if cur:
        out.append(cur)
    return out


def git_call(words, cwd):
    """(repo dir, subcommand, its args) for a git command in command position, else None."""
    i = 0
    while i < len(words) and (re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', words[i]) or words[i] in PREFIX):
        i += 1
    if i >= len(words) or os.path.basename(words[i]) != 'git':
        return None
    i += 1
    repo = cwd
    while i < len(words) and words[i].startswith('-'):
        w = words[i]
        if w in GIT_VAL_OPTS and i + 1 < len(words):
            if w == '-C':
                repo = os.path.join(repo, os.path.expanduser(words[i + 1]))
            i += 2
        else:
            i += 1
    if i >= len(words):
        return None
    return repo, words[i], words[i + 1:]


def commit_all(args):
    for a in args:
        if a == '--all':
            return True
        if a.startswith('-') and not a.startswith('--'):
            for ch in a[1:]:
                if ch == 'a':
                    return True
                if ch in 'mFcCtS':
                    break
    return False


def merge_ref(args):
    i = 0
    while i < len(args):
        a = args[i]
        if a in MERGE_STOP:
            return None
        if a == '--':
            return args[i + 1] if i + 1 < len(args) else None
        if a in MERGE_VAL_OPTS:
            i += 2
            continue
        if a.startswith('-'):
            i += 1
            continue
        return a
    return None


def lines(text):
    return sorted({p for p in (text or '').splitlines() if p})


def main():
    d = json.loads(os.environ['SDLC_RISKY_INPUT'])
    cmd = (d.get('tool_input') or {}).get('command') or ''
    cwd = d.get('cwd') or os.getcwd()
    added = False  # a `git add` ran earlier in this command
    for words in commands(cmd):
        if words[:1] == ['cd'] and len(words) == 2:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        call = git_call(words, cwd)
        if not call:
            continue
        repo, sub, args = call
        if sub == 'add':
            added = True
            continue
        if sub not in ('commit', 'merge'):
            continue
        top = (git(repo, 'rev-parse', '--show-toplevel') or '').strip()
        if not top:
            continue
        gl = globs(top)
        if not gl:
            return
        spec = ['--'] + [f':(top,glob){g}' for g in gl]
        if sub == 'commit':
            hits = lines(git(top, 'diff', '--cached', '--name-only', *spec))
            pending = added or commit_all(args)
            if pending:
                hits = sorted(set(hits) | set(lines(git(top, 'diff', '--name-only', *spec))))
            if added:
                hits = sorted(set(hits) | set(lines(git(top, 'ls-files', '--others', '--exclude-standard', *spec))))
            tree = (git(top, 'write-tree') or '').strip()
            if not hits or not tree:
                continue
            key = ['commit', tree]
            if pending:
                for p in hits:
                    f = os.path.join(top, p)
                    key.append(p + '=' + ((git(top, 'hash-object', '--', p) or '').strip() if os.path.isfile(f) else 'deleted'))
            what = 'this commit'
        else:
            ref = merge_ref(args)
            if not ref:
                continue
            sha = (git(top, 'rev-parse', '--verify', '--quiet', ref + '^{commit}') or '').strip()
            if not sha:
                continue
            hits = lines(git(top, 'diff', '--name-only', f'HEAD...{sha}', *spec))
            if not hits:
                continue
            key = ['merge', sha]
            what = f'this merge of {ref}'
        key += hits
        digest = hashlib.sha256('\0'.join(key).encode()).hexdigest()[:32]
        mdir = (git(top, 'rev-parse', '--git-path', 'sdlc-risky-reminded') or '').strip()
        if not mdir:
            continue
        mdir = os.path.join(top, mdir)
        marker = os.path.join(mdir, digest)
        if os.path.exists(marker):
            continue
        os.makedirs(mdir, exist_ok=True)
        open(marker, 'w').close()
        shown = ', '.join(hits[:5]) + (f' (+{len(hits) - 5} more)' if len(hits) > 5 else '')
        msg = (f'risky change: {what} touches paths .sdlc/config lists under risky_paths: {shown}. '
               'Offer /sdlc:verify to the user once, in one line; never force it, and do not offer it again for this change. '
               '(warn-risky-change.sh reminds once per change.)')
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': msg}}))
        return


try:
    main()
except Exception:
    pass
PY
exit 0
