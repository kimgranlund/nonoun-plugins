#!/usr/bin/env python3
"""wtroot.py: where SDLC Lite puts worktrees and scratch, who owns each run folder, and the crash sweep (T-0550).

Usage: wtroot.py main [--cwd D]                          print the main checkout of the repository holding D
       wtroot.py root [--cwd D]                          print the worktree root (see Root)
       wtroot.py legacy [--cwd D]                        print each legacy root, one per line (none for a bare clone)
       wtroot.py scratch NAME [--cwd D]                  print (and create, with no marker) the scratch dir for NAME
       wtroot.py evidence TICKET [--cwd D]               print (and create) the evidence dir for TICKET
       wtroot.py mark DIR --pid N [--role R] [--ticket T] [--running F]
                                                         write DIR/.owner.json (creating DIR)
       wtroot.py sweep [--cwd D] [--hours H] [--apply]   a dry run by default; --apply removes dead-owner folders
       wtroot.py owner KIND [--ticket T] [--cwd D]       print the checkout that owns KIND for T (see Owner trees)
       wtroot.py selftest | owner-selftest

Root. Every worktree SDLC Lite makes lives in a sibling folder outside the repo, <main checkout parent>/<main
checkout name>.worktrees/ (T-0563), on both hosts, so no watcher, test runner, indexer or .sdlc walker in the repo
sees a lane: lanes (<root>/<lane>), fanout lanes (<root>/fanout/<lane>) and role throwaway trees
(<root>/tmp/<agent name>/). The main checkout is the parent of git rev-parse --git-common-dir, never the current
tree's toplevel, so a role started inside a lane gets the same root and never nests (<lane>/.worktrees/tmp/... was
seen in maison, 2026-10-14). A non-bare, non-.git common dir falls back to --show-toplevel. A bare clone (core.bare,
lanes beside the bare dir, T-0561) has no main checkout the agents may use: its root is <bare parent>/lanes, outside
every lane. A `worktree_root: <path>` line in .sdlc/config overrides either default; a relative path resolves against
the main checkout, or for a bare clone against the bare dir's parent (the config is read from the current lane).
Legacy roots, still read for one release and moved by migrate-worktrees.sh: <main checkout>/.claude/worktrees
(0.23.0 and 0.23.1, T-0550) and <main checkout>/.worktrees (before 0.23.0). A worktree Claude Code makes for itself
under .claude/worktrees/ (Agent isolation: worktree, claude --worktree, EnterWorktree) is host-owned, not a root.

Host-owned. host_owned(path) names the host of a tree the host made for itself: Codex for ~/.codex/worktrees/*, Claude
Code for .claude/worktrees/agent-*. lanes.py sweep prints `kept <lane>: host-owned (<host>)` for one and never closes
it; dispatch.py never reports one as a stray (T-0564).

Scratch. Files that are not worktrees (probe files, mutated copies) go to <system temp dir>/sdlc-lite/<repo key>/<name>,
the system temp dir being $TMPDIR (tempfile.gettempdir()), as Claude Code's session scratchpad; never into the repo.

Evidence. Screenshots, videos and other binary run evidence go to <user cache>/sdlc-lite/<repo key>/evidence/<ticket>/
(T-0568), the user cache being $XDG_CACHE_HOME, else ~/Library/Caches on macOS, else ~/.cache, with the repo key
scratch uses. Unlike scratch it survives a reboot and the sweep never reads it; a record cites the path, the repo holds
only text.

Owner marker. Each run folder holds .owner.json: pid, started (epoch seconds), started_at, role, ticket, and an
optional running path (a *.running marker). An owner is live while its pid runs or its running file exists.

Sweep. For each folder directly under <root>/tmp (and each legacy root's tmp), and under every repo's scratch dir (<system temp dir>/sdlc-lite/*,
so a throwaway repo's scratch is swept too; an emptied scratch dir of a repo goes with --apply): no .owner.json prints
`unmarked: <path>` and is never deleted (legacy or hand-made); a live owner prints `kept <path>: owner live`; a dead
owner younger than the limit (default 2 hours, lanes.py passes lane_min_age_hours) prints `kept <path>: recent`;
else `would remove <path>` (dry run) or, with --apply, its registered worktrees are removed with git worktree remove
--force, the folder is deleted, and it prints `removed <path>`. An unmarked run.sh prefix (<role>-<pid>) is left to
reap-tmp-worktrees.sh and not listed. lanes.py sweep and dispatch.py record call sweep().

Owner trees (T-0749). OWNERS maps each kind of sdlc state (records, base-sha, end-sha, config, branch, worktree,
roadmap, router, ticket-close, lane-close) to the checkouts that own it, in order: primary (the main checkout), integration
(the worktree holding the lane's into branch, when not the main checkout) and lane (the worktree whose .lane.json or host
record lists the ticket). owner_tree(kind, ticket, cwd) returns the first that exists; owner_rule(kind) the whole row,
with the note naming a script that disagrees today. The rule table is in docs/references/sdlc-internals.md.

Importable: main_top, bare_parent, default_root, root, legacy_roots, is_legacy, host_owned, tmp_root, tmp_roots,
scratch_root, scratch_dir, cache_root, evidence_dir, mark, owner, live, sweep, OWNERS, owner_trees, owner_rule, owner_tree.
"""
import argparse, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

Path = pathlib.Path
SUFFIX = '.worktrees'  # the sibling root is <main checkout parent>/<main checkout name>.worktrees (T-0563)
CLAUDE = ('.claude', 'worktrees')  # the 0.23 root, now legacy; also where Claude Code puts its own worktrees
LEGACY = '.worktrees'  # the root before 0.23.0
MARKER = '.owner.json'
SWEEP_HOURS = 2.0
RUNNER = re.compile(r'^[a-z]+-[0-9]+$')


def _git(cwd, *args):
    try:
        r = subprocess.run(['git', '-C', str(cwd), *args], capture_output=True, text=True)
    except OSError:
        return ''
    return r.stdout.strip() if r.returncode == 0 else ''


def main_top(cwd='.'):
    """The main checkout of the repository holding cwd (the parent of the common .git dir), else its toplevel, else None."""
    cwd = os.path.abspath(str(cwd))
    common = _git(cwd, 'rev-parse', '--path-format=absolute', '--git-common-dir') or _git(cwd, 'rev-parse', '--git-common-dir')
    if common:
        common = os.path.normpath(os.path.join(cwd, common))
        if os.path.basename(common) == '.git':
            return os.path.dirname(common)
    top = _git(cwd, 'rev-parse', '--show-toplevel')
    return top or None


def bare_parent(cwd='.'):
    """The parent of the bare common dir when cwd is in a bare clone (or one of its lanes), else None (T-0561)."""
    cwd = os.path.abspath(str(cwd))
    common = _git(cwd, 'rev-parse', '--path-format=absolute', '--git-common-dir') or _git(cwd, 'rev-parse', '--git-common-dir')
    if not common or _git(cwd, 'config', '--bool', 'core.bare') != 'true':
        return None
    return os.path.dirname(os.path.normpath(os.path.join(cwd, common)))


def _config_root(top):
    """The worktree_root: line of <top>/.sdlc/config, or None."""
    try:
        text = Path(top, '.sdlc', 'config').read_text(encoding='utf-8')
    except (OSError, TypeError):
        return None
    for line in text.splitlines():
        m = re.match(r'\s*worktree_root\s*:\s*(.*?)\s*$', line)
        if m and m.group(1):
            return os.path.expanduser(m.group(1))
    return None


def default_root(top):
    """The sibling root of a main checkout: <its parent>/<its name>.worktrees (T-0563)."""
    top = Path(os.path.abspath(str(top)))
    return top.parent / (top.name + SUFFIX)


def root(cwd='.'):
    """The worktree root, or None outside a repository: a worktree_root: line in .sdlc/config (relative to the main
    checkout, or to a bare clone's parent dir), else the sibling <main checkout parent>/<name>.worktrees (T-0563),
    else for a bare clone <bare parent>/lanes (T-0561)."""
    bare = bare_parent(cwd)
    if bare:
        top = _git(os.path.abspath(str(cwd)), 'rev-parse', '--show-toplevel')
        conf = _config_root(top) if top else None
        return Path(os.path.normpath(os.path.join(bare, conf))) if conf else Path(bare, 'lanes')
    top = main_top(cwd)
    if not top:
        return None
    conf = _config_root(top)
    return Path(os.path.normpath(os.path.join(top, conf))) if conf else default_root(top)


def legacy_roots(cwd='.'):
    """The legacy roots read for one release: <main checkout>/.claude/worktrees and <main checkout>/.worktrees; none for a
    bare clone."""
    top = main_top(cwd)
    return [Path(top, *CLAUDE), Path(top, LEGACY)] if top and not bare_parent(cwd) else []


def is_legacy(path, cwd='.'):
    """True when path lies under a legacy root of the repository holding cwd."""
    return any(_under(str(path), str(r)) for r in legacy_roots(cwd))


def host_owned(path):
    """'Codex' for a host-owned tree under ~/.codex/worktrees, 'Claude Code' for one under .claude/worktrees/agent-*,
    else None: a worktree the host made for itself, never listed for removal (T-0564)."""
    if _under(str(path), os.path.expanduser(os.path.join('~', '.codex', 'worktrees'))):
        return 'Codex'
    parts = Path(os.path.realpath(str(path))).parts
    if any(parts[i:i + 2] == CLAUDE and parts[i + 2].startswith('agent-') for i in range(len(parts) - 2)):
        return 'Claude Code'
    return None


def tmp_root(cwd='.'):
    r = root(cwd)
    return r / 'tmp' if r else None


def tmp_roots(cwd='.'):
    """<root>/tmp, then each legacy root's tmp, without duplicates (a worktree_root: line may name a legacy root)."""
    return list(dict.fromkeys([t for t in [tmp_root(cwd)] + [r / 'tmp' for r in legacy_roots(cwd)] if t is not None]))


def repo_key(cwd='.'):
    """<main checkout name>-<8 hex of its path>, the same from every lane."""
    top = main_top(cwd) or os.path.abspath(str(cwd))
    return '%s-%s' % (os.path.basename(top) or 'repo', hashlib.sha1(top.encode()).hexdigest()[:8])


def scratch_root(cwd='.'):
    """<system temp dir>/sdlc-lite/<repo key>."""
    return Path(tempfile.gettempdir(), 'sdlc-lite', repo_key(cwd))


def scratch_dir(name, cwd='.'):
    return scratch_root(cwd) / name


def cache_root():
    """The user cache: $XDG_CACHE_HOME, else ~/Library/Caches on macOS, else ~/.cache."""
    if os.environ.get('XDG_CACHE_HOME'):
        return Path(os.environ['XDG_CACHE_HOME'])
    return Path(os.path.expanduser('~/Library/Caches' if sys.platform == 'darwin' else '~/.cache'))


def evidence_dir(ticket, cwd='.'):
    """<user cache>/sdlc-lite/<repo key>/evidence/<ticket>: binary evidence, outside the repo and the sweep (T-0568)."""
    return cache_root() / 'sdlc-lite' / repo_key(cwd) / 'evidence' / ticket


def mark(d, pid, role=None, ticket=None, running=None, now=None):
    """Write d/.owner.json (creating d) and return the record."""
    now = time.time() if now is None else now
    rec = dict(pid=int(pid), started=int(now), started_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
               role=role, ticket=ticket, running=str(running) if running else None)
    d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    (d / MARKER).write_text(json.dumps(rec, separators=(',', ':')) + '\n', encoding='utf-8')
    return rec


def owner(d):
    try:
        rec = json.loads((Path(d) / MARKER).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return rec if isinstance(rec, dict) else None


def pid_alive(pid):
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def live(rec):
    return pid_alive(rec.get('pid')) or bool(rec.get('running') and os.path.exists(rec['running']))


def _under(p, d):
    p, d = os.path.realpath(p), os.path.realpath(d)
    return p == d or p.startswith(d.rstrip(os.sep) + os.sep)


def sweep(cwd='.', hours=None, apply=False, now=None, parents=None):
    """[(verdict, path)] for each folder directly under each tmp root and scratch dir; verdict is one of unmarked, live,
    recent, would remove, removed, failed. Only a dead owner past the limit is removed, and only with apply."""
    hours = SWEEP_HOURS if hours is None else float(hours)
    now = time.time() if now is None else now
    top = main_top(cwd)
    if parents is None:  # this repo's tmp dirs (legacy ones too), and every repo's scratch dir (it outlives the repo)
        base = scratch_root(cwd).parent
        keys = sorted(k for k in base.iterdir() if k.is_dir() and not k.is_symlink()) if base.is_dir() else []
        parents = tmp_roots(cwd) + keys
    out = []
    for parent in parents:
        if not Path(parent).is_dir():
            continue
        for d in sorted(Path(parent).iterdir()):
            if not d.is_dir() or d.is_symlink():
                continue
            rec = owner(d)
            if rec is None and RUNNER.match(d.name):
                continue  # a run.sh prefix <role>-<pid>: reap-tmp-worktrees.sh owns it
            if rec is None:
                out.append(('unmarked', str(d)))
            elif live(rec):
                out.append(('live', str(d)))
            elif now - float(rec.get('started') or 0) < hours * 3600:
                out.append(('recent', str(d)))
            elif not apply:
                out.append(('would remove', str(d)))
            else:
                ok = True
                if top:
                    for line in _git(top, 'worktree', 'list', '--porcelain').splitlines():
                        if line.startswith('worktree ') and _under(line[9:], d):
                            ok = subprocess.run(['git', '-C', top, 'worktree', 'remove', '--force', '--force', line[9:]],
                                                capture_output=True).returncode == 0 and ok
                shutil.rmtree(d, ignore_errors=True)
                if top:
                    _git(top, 'worktree', 'prune')
                out.append(('removed' if ok and not d.exists() else 'failed', str(d)))
        if apply and Path(parent).parent == scratch_root(cwd).parent:
            try:
                Path(parent).rmdir()  # an emptied scratch dir of a repo
            except OSError:
                pass
    return out


def lines(res):
    word = {'unmarked': 'unmarked: %s', 'live': 'kept %s: owner live', 'recent': 'kept %s: recent',
            'would remove': 'would remove %s', 'removed': 'removed %s', 'failed': 'could not remove %s'}
    return [word[v] % p for v, p in res]


# Owner trees (T-0749): which checkout owns each kind of sdlc state while a ticket is in flight, derived from what the
# scripts do today (docs/references/sdlc-internals.md, the owner-tree table). Each row: the trees in preference order
# (the first that exists wins), who writes, who reads, and a note naming a script that disagrees today.
OWNERS = {
    'records': (('lane', 'primary'), 'dispatch.py prepare and record (order.records_dir of the handoff dir)',
                'dispatch.py, fanout.py land (lane, then integration, then primary), lanes.py close (carries to primary)',
                '#55: prepare --tree <lane> for a primary handoff writes primary records while land reads the lane first'),
    'base-sha': (('lane', 'primary'), 'dispatch.py prepare (records dir)',
                 'dispatch.build_base (records dir, then the twin in the execution tree, T-0717)',
                 '#49: build_base falls back to the lane start (.lane.json base_sha) when no base-sha is in the execution tree'),
    'end-sha': (('lane', 'primary'), 'dispatch.py record for a builder (records dir)',
                'dispatch.step_end for the verifier Diff range (the object must exist in the execution tree)',
                '#47: end-sha records the end tree before a review fix, so a later fix in the lane falls outside it'),
    'config': (('integration', 'primary'), 'the repo owner (.sdlc/config: merge_gate, light_scope)',
               'fanout.py land gate_class and light_refusal via config_root (T-0722)',
               '#58: fanout.py run light_refusal and lanes.py read the primary config only; wtroot._config_root reads the current tree'),
    'branch': (('integration', 'primary'), 'lanes.py open (T-0680; primary with --root or a ticket missing there)',
               'lanes.py list and close (cleared in both trees, T-0695, T-0713)',
               'a main tracking an upstream writes no line at all (T-0609)'),
    'worktree': (('integration', 'primary'), 'lanes.py open, beside the branch: line',
                 'lanes.py close (cleared with the branch: line)', 'as branch'),
    'roadmap': (('integration', 'primary'), 'tickets.record_branch and tickets.py close (regenerated where they write)',
                'fanout.merge_generated resolves roadmap conflicts on merge', 'as branch'),
    'router': (('integration', 'primary'), 'tickets.record_branch and tickets.py close (regenerated where they write)',
               'roles reading .sdlc/AGENTS.md', 'as branch'),
    'ticket-close': (('integration', 'primary'), 'fanout.py land (tickets.py close on the integration branch)',
                     'lanes.py finish step 6 closes in primary when land did not',
                     '#59: the closed folder lands on integration while the lane keeps an open copy'),
    'lane-close': (('primary',), 'lanes.py close_lane run from primary (archive ref, carried records, `lane closed` commit)',
                   'lanes.py finish, archive list and restore',
                   '#46/#57: close commits in primary while land merges into integration; only the branch: clear goes to integration (T-0695)'),
}


def _top(cwd):
    top = _git(os.path.abspath(str(cwd)), 'rev-parse', '--show-toplevel')
    return os.path.realpath(top) if top else None


def _lane_rec(path, cwd):
    """The lane record of a tree: .lane.json at its top, else its host record <root>/host/<leaf>.lane.json (T-0745)."""
    r = root(cwd)
    for f in (Path(path, '.lane.json'), Path(r, 'host', Path(path).name + '.lane.json') if r else None):
        try:
            rec = json.loads(f.read_text(encoding='utf-8')) if f else None
        except (OSError, ValueError):
            continue
        if isinstance(rec, dict):
            return rec
    return {}


def owner_trees(ticket=None, cwd='.'):
    """{'primary', 'integration', 'lane'}: the main checkout, the lane worktree whose record lists ticket (else the
    current tree when it is not the main checkout), and the worktree holding that lane's into branch when it is not the
    main checkout; None for a tree that does not exist."""
    primary = main_top(cwd)
    primary = os.path.realpath(primary) if primary else None
    trees, cur = [], None
    for line in _git(os.path.abspath(str(cwd)), 'worktree', 'list', '--porcelain').splitlines():
        if line.startswith('worktree '):
            cur = [os.path.realpath(line[len('worktree '):]), None]
            trees.append(cur)
        elif line.startswith('branch refs/heads/') and cur:
            cur[1] = line[len('branch refs/heads/'):]
    lane, rec = None, {}
    for p, _ in trees:
        r = _lane_rec(p, cwd) if p != primary else {}
        if ticket and ticket in (r.get('tickets') or []) and r.get('kind') != 'integration':
            lane, rec = p, r
            break
    here = _top(cwd)
    if lane is None and not ticket and here and here != primary:
        lane, rec = here, _lane_rec(here, cwd)
    into = str(rec.get('into') or '').replace('refs/heads/', '')
    integ = next((p for p, b in trees if into and b == into and p != primary), None)
    wrap = lambda p: Path(p) if p else None  # noqa: E731
    return {'primary': wrap(primary), 'integration': wrap(integ), 'lane': wrap(lane)}


def owner_rule(kind):
    """The OWNERS row for kind as a dict (trees, writer, reader, note); ValueError for an unknown kind."""
    if kind not in OWNERS:
        raise ValueError('unknown kind %r: one of %s' % (kind, ', '.join(OWNERS)))
    return dict(zip(('trees', 'writer', 'reader', 'note'), OWNERS[kind]))


def owner_tree(kind, ticket=None, cwd='.'):
    """The checkout that owns kind for ticket (owner_rule(kind)['trees'], the first that exists), else None."""
    trees = owner_trees(ticket, cwd)
    return next((trees[t] for t in owner_rule(kind)['trees'] if trees[t] is not None), None)


def owner_selftest():
    """One case per OWNERS kind across primary, integration and lane trees in a throwaway repo, then the fallbacks."""
    fails = []

    def expect(label, ok):
        print(('ok: ' if ok else 'FAIL: ') + label)
        if not ok:
            fails.append(label)

    def g(cwd, *a):
        subprocess.run(['git', '-C', str(cwd), *a], check=True, capture_output=True)

    want = {'records': 'lane', 'base-sha': 'lane', 'end-sha': 'lane', 'config': 'integration', 'branch': 'integration',
            'worktree': 'integration', 'roadmap': 'integration', 'router': 'integration', 'ticket-close': 'integration',
            'lane-close': 'primary'}
    with tempfile.TemporaryDirectory() as t:
        base = Path(os.path.realpath(t))
        repo = base / 'repo'
        repo.mkdir()
        g(repo, 'init', '-q', '-b', 'main')
        g(repo, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'init')
        sib = base / 'repo.worktrees'
        integ, lane, solo = sib / 'fanout' / 'integ', sib / 'fanout' / 'lane-a', sib / 'solo-b'
        g(repo, 'worktree', 'add', '-q', '-b', 'integ', str(integ), 'HEAD')
        g(repo, 'worktree', 'add', '-q', '-b', 'integ-lane-a', str(lane), 'HEAD')
        g(repo, 'worktree', 'add', '-q', '-b', 'solo-b', str(solo), 'HEAD')
        (lane / '.lane.json').write_text(json.dumps({'lane': 'lane-a', 'kind': 'fanout', 'tickets': ['T-0001'],
                                                     'into': 'integ'}), encoding='utf-8')
        (solo / '.lane.json').write_text(json.dumps({'lane': 'solo-b', 'kind': 'solo', 'tickets': ['T-0002'],
                                                     'into': 'main'}), encoding='utf-8')
        expect('owner_trees names primary, integration and lane for a fanout ticket, from any tree',
               all(owner_trees('T-0001', c) == {'primary': repo, 'integration': integ, 'lane': lane}
                   for c in (repo, integ, lane)))
        name = {'primary': repo, 'integration': integ, 'lane': lane}
        for kind in OWNERS:
            got = [owner_tree(kind, 'T-0001', c) for c in (repo, lane)]
            expect('%s is owned by the %s tree, from primary and from the lane (got %s)' % (kind, want[kind], [x and x.name for x in got]),
                   got == [name[want[kind]]] * 2)
        fall = {'lane': solo, 'integration': repo, 'primary': repo}
        for kind in OWNERS:
            got = owner_tree(kind, 'T-0002', solo)
            expect('fallback: %s for a solo lane into main is %s (got %s)' % (kind, fall[want[kind]].name, got and got.name),
                   got == fall[want[kind]])
        expect('fallback: a ticket with no lane leaves the lane kinds in primary',
               owner_tree('records', 'T-0009', repo) == repo and owner_tree('config', 'T-0009', repo) == repo)
        host = sib / 'host-c'
        g(repo, 'worktree', 'add', '-q', '-b', 'host-c', str(host), 'HEAD')
        (sib / 'host').mkdir()
        (sib / 'host' / 'host-c.lane.json').write_text(json.dumps({'lane': 'host-c', 'kind': 'host',
                                                                   'tickets': ['T-0003'], 'into': 'integ'}))
        expect('a host record (no .lane.json) names the lane and its integration tree (T-0745)',
               owner_tree('base-sha', 'T-0003', repo) == host and owner_tree('config', 'T-0003', repo) == integ)
        expect('no ticket: the current tree is the lane', owner_tree('records', None, lane) == lane
               and owner_tree('records', None, repo) == repo)
        try:
            owner_rule('nope')
            expect('an unknown kind raises ValueError', False)
        except ValueError:
            expect('an unknown kind raises ValueError', True)
    print('wtroot.py owner-selftest: %s' % ('FAIL' if fails else 'ok'))
    return 1 if fails else 0


def selftest():
    fails = []

    def expect(label, ok):
        print(('ok: ' if ok else 'FAIL: ') + label)
        if not ok:
            fails.append(label)

    def g(cwd, *a):
        subprocess.run(['git', '-C', str(cwd), *a], check=True, capture_output=True)

    with tempfile.TemporaryDirectory() as t:
        base = Path(os.path.realpath(t))
        repo = base / 'repo'
        repo.mkdir()
        g(repo, 'init', '-q', '-b', 'main')
        g(repo, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'init')
        sib = base / 'repo.worktrees'
        lane = sib / 'lane-a'
        g(repo, 'worktree', 'add', '-q', '--detach', str(lane), 'HEAD')
        old = repo / '.claude' / 'worktrees' / 'lane-old'
        g(repo, 'worktree', 'add', '-q', '--detach', str(old), 'HEAD')
        expect('root from the main checkout is the sibling <parent>/<name>.worktrees, outside the main checkout (T-0563)',
               root(repo) == sib and not _under(str(root(repo)), str(repo)))
        expect('root from a lane is the same sibling root, not nested in the lane',
               root(lane) == sib and not _under(str(root(lane)), str(lane)))
        expect('root from a legacy .claude/worktrees lane is the same sibling root', root(old) == sib)
        expect('a lane under .claude/worktrees is read as legacy, a sibling lane is not',
               is_legacy(old, repo) and is_legacy(old, old) and not is_legacy(lane, repo))
        host = repo / '.claude' / 'worktrees' / 'agent-x'
        expect('host-owned: Claude Code for .claude/worktrees/agent-*, Codex for ~/.codex/worktrees/*, none for a lane',
               host_owned(host / 'sub') == 'Claude Code' and host_owned(os.path.expanduser('~/.codex/worktrees/ab/r')) == 'Codex'
               and host_owned(old) is None and host_owned(lane) is None)
        expect('legacy roots are <main>/.claude/worktrees and <main>/.worktrees, from a lane too',
               legacy_roots(lane) == [repo / '.claude' / 'worktrees', repo / '.worktrees'])
        # negative control: the toplevel of the lane (the old rule) does nest
        expect('control: --show-toplevel from the lane is the lane itself (the nesting the rule avoids)',
               _git(lane, 'rev-parse', '--show-toplevel') == str(lane))
        expect('the sweep reads <root>/tmp, then the legacy tmp dirs', tmp_roots(lane) == [
            sib / 'tmp', repo / '.claude' / 'worktrees' / 'tmp', repo / '.worktrees' / 'tmp'])
        expect('root outside a repository is None', root(base) is None)
        expect('scratch dir sits under the system temp dir, not the repo',
               _under(str(scratch_dir('x', repo)), tempfile.gettempdir()) and not _under(str(scratch_dir('x', repo)), str(repo)))
        expect('scratch root is the same from the lane and the main checkout', scratch_root(lane) == scratch_root(repo))
        saved = os.environ.pop('XDG_CACHE_HOME', None)
        try:
            ev = evidence_dir('T-1', repo)
            expect('evidence dir sits under the user cache, keyed like scratch (T-0568)',
                   _under(str(ev), str(cache_root())) and ev.parent.parent.name == scratch_root(repo).name
                   and str(ev).endswith(os.path.join('sdlc-lite', ev.parent.parent.name, 'evidence', 'T-1')))
            expect('evidence dir is outside the repo and the system temp dir', not _under(str(ev), str(repo))
                   and not _under(str(ev), tempfile.gettempdir()))
            expect('evidence dir is the same from the lane and the main checkout', evidence_dir('T-1', lane) == ev)
            os.environ['XDG_CACHE_HOME'] = str(base / 'xdg')
            expect('evidence dir honors XDG_CACHE_HOME', evidence_dir('T-1', lane) == base / 'xdg' / 'sdlc-lite'
                   / scratch_root(repo).name / 'evidence' / 'T-1')
            out = subprocess.run([sys.executable, os.path.abspath(__file__), 'evidence', 'T-2', '--cwd', str(lane)],
                                 capture_output=True, text=True).stdout.strip()
            expect('wtroot.py evidence prints and creates the dir', out == str(base / 'xdg' / 'sdlc-lite'
                   / scratch_root(repo).name / 'evidence' / 'T-2') and Path(out).is_dir())
        finally:
            os.environ.pop('XDG_CACHE_HOME', None)
            if saved is not None:
                os.environ['XDG_CACHE_HOME'] = saved

        # T-0561: a bare clone with lanes beside it (gen-ui-kit: <dir>/.bare, <dir>/lanes/<lane>, <dir>/main)
        kit = base / 'ui-kit'
        g(base, 'clone', '-q', '--bare', str(repo), str(kit / '.bare'))
        blane = kit / 'lanes' / 'lane-b'
        g(kit / '.bare', 'worktree', 'add', '-q', '--detach', str(blane), 'HEAD')
        g(kit / '.bare', 'worktree', 'add', '-q', '--detach', str(kit / 'main'), 'HEAD')
        expect('control: the old rule (--show-toplevel) from a bare-clone lane is the lane itself',
               _git(blane, 'rev-parse', '--show-toplevel') == str(blane))
        expect('bare clone: root from a lane is <bare parent>/lanes, outside the lane', root(blane) == kit / 'lanes'
               and not _under(str(root(blane)), str(blane)))
        expect('bare clone: the tmp prefix from a lane is outside every lane',
               tmp_root(blane) == kit / 'lanes' / 'tmp' and not _under(str(tmp_root(blane)), str(blane)))
        expect('bare clone: root from the bare dir itself is the same', root(kit / '.bare') == kit / 'lanes')
        expect('bare clone: no legacy root, so the sweep reads only <bare parent>/lanes/tmp',
               legacy_roots(blane) == [] and tmp_roots(blane) == [kit / 'lanes' / 'tmp'])
        (blane / '.sdlc').mkdir()
        (blane / '.sdlc' / 'config').write_text('# x\nworktree_root: ../trees\n', encoding='utf-8')
        expect('bare clone: a relative worktree_root: line resolves against the bare parent, not the lane',
               root(blane) == kit.parent / 'trees')
        (repo / '.sdlc').mkdir()
        (repo / '.sdlc' / 'config').write_text('worktree_root: %s\n' % (base / 'abs'), encoding='utf-8')
        expect('an absolute worktree_root: line in the main checkout config wins, from a lane too',
               root(repo) == base / 'abs' and root(lane) == base / 'abs')
        (repo / '.sdlc' / 'config').unlink()

        tmp = base / 'tmpparent'
        dead = subprocess.Popen([sys.executable, '-c', 'pass'])
        dead.wait()
        now = time.time()
        mark(tmp / 'dead-old', dead.pid, role='verifier', ticket='T-1', now=now - 3 * 3600)
        g(repo, 'worktree', 'add', '-q', '--detach', str(tmp / 'dead-old' / 'w'), 'HEAD')
        mark(tmp / 'dead-young', dead.pid, role='verifier', now=now - 60)
        mark(tmp / 'live-old', os.getpid(), role='builder', now=now - 3 * 3600)
        run_file = base / 'x.running'
        run_file.write_text('1\n')
        mark(tmp / 'running-old', dead.pid, role='builder', running=run_file, now=now - 3 * 3600)
        (tmp / 'unmarked').mkdir()
        (tmp / ('builder-%d' % dead.pid)).mkdir()
        dry = dict((Path(p).name, v) for v, p in sweep(repo, hours=2, now=now, parents=[tmp]))
        expect('dry run changes nothing', all((tmp / n).is_dir() for n in ('dead-old', 'dead-young', 'live-old', 'unmarked')))
        expect('dry run reports the dead old folder as would remove', dry.get('dead-old') == 'would remove')
        res = dict((Path(p).name, v) for v, p in sweep(repo, hours=2, now=now, apply=True, parents=[tmp]))
        expect('sweep removes a dead-owner folder past the limit, and its worktree',
               res.get('dead-old') == 'removed' and not (tmp / 'dead-old').exists()
               and str(tmp / 'dead-old' / 'w') not in _git(repo, 'worktree', 'list'))
        expect('sweep keeps a dead owner younger than the limit', res.get('dead-young') == 'recent' and (tmp / 'dead-young').is_dir())
        expect('sweep keeps a live pid owner', res.get('live-old') == 'live' and (tmp / 'live-old').is_dir())
        expect('sweep keeps an owner whose running file exists', res.get('running-old') == 'live' and (tmp / 'running-old').is_dir())
        expect('sweep reports an unmarked folder and keeps it', res.get('unmarked') == 'unmarked' and (tmp / 'unmarked').is_dir())
        run_file.unlink()
        res = dict((Path(p).name, v) for v, p in sweep(repo, hours=2, now=now, apply=True, parents=[tmp]))
        expect('a running file gone and the pid dead: removed', res.get('running-old') == 'removed')
        expect('an unmarked run.sh prefix is left to reap-tmp-worktrees.sh, not listed or removed',
               'builder-%d' % dead.pid not in res and (tmp / ('builder-%d' % dead.pid)).is_dir())
        expect('lines() words the verdicts', lines([('unmarked', '/x')]) == ['unmarked: /x'])
    if owner_selftest():
        fails.append('owner-selftest')
    print('wtroot.py selftest: %s' % ('FAIL' if fails else 'ok'))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog='wtroot.py', description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', metavar='{main,root,legacy,scratch,evidence,mark,sweep,owner,selftest,owner-selftest}')
    for n in ('main', 'root', 'legacy'):
        sub.add_parser(n).add_argument('--cwd', default='.')
    p = sub.add_parser('scratch')
    p.add_argument('name')
    p.add_argument('--cwd', default='.')
    p = sub.add_parser('evidence')
    p.add_argument('ticket')
    p.add_argument('--cwd', default='.')
    p = sub.add_parser('mark')
    p.add_argument('dir')
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--role')
    p.add_argument('--ticket')
    p.add_argument('--running')
    p = sub.add_parser('sweep')
    p.add_argument('--cwd', default='.')
    p.add_argument('--hours', type=float)
    p.add_argument('--apply', action='store_true')
    p = sub.add_parser('owner')
    p.add_argument('kind', choices=list(OWNERS))
    p.add_argument('--ticket')
    p.add_argument('--cwd', default='.')
    sub.add_parser('selftest')
    sub.add_parser('owner-selftest')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'owner-selftest':
        return owner_selftest()
    if a.cmd == 'owner':
        o = owner_tree(a.kind, a.ticket, a.cwd)
        print(o or '')
        return 0 if o else 1
    if a.cmd == 'main':
        top = main_top(a.cwd)
        print(top or '')
        return 0 if top else 1
    if a.cmd == 'root':
        r = root(a.cwd)
        print(r or '')
        return 0 if r else 1
    if a.cmd == 'legacy':
        for r in legacy_roots(a.cwd):
            print(r)
        return 0
    if a.cmd == 'scratch':
        d = scratch_dir(a.name, a.cwd)
        d.mkdir(parents=True, exist_ok=True)
        print(d)
        return 0
    if a.cmd == 'evidence':
        d = evidence_dir(a.ticket, a.cwd)
        d.mkdir(parents=True, exist_ok=True)
        print(d)
        return 0
    if a.cmd == 'mark':
        mark(a.dir, a.pid, a.role, a.ticket, a.running)
        return 0
    if a.cmd == 'sweep':
        for line in lines(sweep(a.cwd, a.hours, a.apply)):
            print(line)
        return 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
