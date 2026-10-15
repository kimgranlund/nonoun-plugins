"""Git reader: read-only facts of one repo, through `git -C <repo>` subprocesses.

read(repo, integration=None, limit=2000) returns one dict:
  worktrees        one {path, branch, nested} per `git worktree list --porcelain` entry; branch
                   is the short name, None when detached; nested is True when the path holds a
                   worktree root (the legacy `.claude/worktrees/`, or the pre-0.23.0 `.worktrees/`) twice or lies
                   under its `tmp/`;
  branches         `git for-each-ref --format=%(refname:short) refs/heads`, in its order;
  tracked_runtime  `git ls-files` paths ending in .log, .running, .run.lock, or .board-state.json;
  resets           one (sha, reflog subject) per `reset: moving to` entry of `git reflog show HEAD`,
                   run in integration when given, else in repo;
  commits          one (sha, subject) per `git log --format=%H%x09%s -n <limit>` commit whose
                   subject is `Merge <lane>: <id>`, `close <id>`, or `wip(<id>): <outcome>`;
  problems         one line per repo that is not a git work tree or git command that failed.
A repo that is not a git work tree gives empty lists and a problems entry. Nothing is written:
every command is a read, and GIT_OPTIONAL_LOCKS=0 keeps git from refreshing the index.
"""
import os, re, subprocess

FIELDS = ('worktrees', 'branches', 'tracked_runtime', 'resets', 'commits', 'problems')
RUNTIME_SUFFIXES = ('.log', '.running', '.run.lock', '.board-state.json')
TICKET = r'T-\d+'
COMMIT_RE = re.compile(r'^(?:Merge \S+: ' + TICKET + r'|close ' + TICKET + r'|wip\(' + TICKET
                       + r'\): .+)$')
RESET = 'reset: moving to'
# Inherited GIT_* repo selectors would point every -C command at another repo.
_DROP_ENV = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR',
             'GIT_OBJECT_DIRECTORY', 'GIT_NAMESPACE', 'GIT_CEILING_DIRECTORIES')


def _env():
    env = {k: v for k, v in os.environ.items() if k not in _DROP_ENV}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_TERMINAL_PROMPT'] = '0'
    return env


def _git(repo, *args):
    """(returncode, stdout lines, stderr text) of `git -C repo args`; rc 127 when git is missing."""
    try:
        p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True,
                           errors='replace', env=_env(), stdin=subprocess.DEVNULL)
    except OSError as e:
        return 127, [], str(e)
    return p.returncode, p.stdout.splitlines(), p.stderr.strip()


def is_work_tree(path):
    if not path or not os.path.isdir(path):
        return False
    rc, out, _ = _git(path, 'rev-parse', '--is-inside-work-tree')
    return rc == 0 and out == ['true']


def nested(path):
    p = path.replace(os.sep, '/').rstrip('/') + '/'
    roots = ('.worktrees/', '.claude/worktrees/')  # T-0550, T-0563: legacy roots, still read for one release
    return (sum(p.count(r) for r in roots) >= 2 or any('/' + r + 'tmp/' in p or p.startswith(r + 'tmp/') for r in roots))


def _lines(repo, problems, *args):
    rc, out, err = _git(repo, *args)
    if rc:
        problems.append(f'{repo}: git {" ".join(args)} failed rc={rc}' + (f': {err}' if err else ''))
        return []
    return out


def _worktrees(lines):
    out, cur = [], None
    for line in lines + ['']:
        if line.startswith('worktree '):
            cur = {'path': line[len('worktree '):], 'branch': None}
        elif cur is not None and line.startswith('branch '):
            ref = line[len('branch '):]
            cur['branch'] = ref[len('refs/heads/'):] if ref.startswith('refs/heads/') else ref
        elif not line and cur is not None:
            cur['nested'] = nested(cur['path'])
            out.append(cur)
            cur = None
    return out


def _split(line):
    sha, _, rest = line.partition('\t')
    return sha, rest


def read(repo, integration=None, limit=2000):
    rec = {k: [] for k in FIELDS}
    problems = rec['problems']
    if not is_work_tree(repo):
        problems.append(f'{repo}: not a git work tree')
        return rec
    rec['worktrees'] = _worktrees(_lines(repo, problems, 'worktree', 'list', '--porcelain'))
    rec['branches'] = [b for b in _lines(repo, problems, 'for-each-ref',
                                         '--format=%(refname:short)', 'refs/heads') if b]
    rec['tracked_runtime'] = [p for p in _lines(repo, problems, 'ls-files')
                              if p.endswith(RUNTIME_SUFFIXES)]
    where = integration or repo
    if integration and not is_work_tree(integration):
        problems.append(f'{integration}: not a git work tree')
    else:
        entries = [_split(l) for l in _lines(where, problems, 'reflog', 'show',
                                             '--format=%H%x09%gs', 'HEAD')]
        rec['resets'] = [e for e in entries if e[1].startswith(RESET)]
    entries = [_split(l) for l in _lines(repo, problems, 'log', '--format=%H%x09%s',
                                         '-n', str(int(limit)))]
    rec['commits'] = [e for e in entries if COMMIT_RE.match(e[1])]
    return rec
