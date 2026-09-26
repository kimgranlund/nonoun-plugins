#!/usr/bin/env python3
"""Run ticket lanes in parallel: one git worktree and one headless conductor per lane, each lane
merged into an integration branch under a lock, gated, and closed there. Main is never touched.

Usage: fanout.py run <lane>=<id>[,<id>...]... [--root .sdlc] [--base REF] [--integration BRANCH]
                     [--lanes-dir DIR] [--gate CMD]... [--driver CMD] [--rewrite-refs] [--dry-run]
       fanout.py selftest

run
  Preflight (every refusal prints on stderr, exits 2, and creates nothing): the cwd is in a git
  work tree with a commit; --root (default .sdlc, relative to the cwd) lies inside the toplevel,
  and its path relative to the toplevel (rel) is the ticket root in every worktree; lane names
  match ^[a-z0-9]+(-[a-z0-9]+)*$ (not `integration` or `logs`, which name the lanes dir's own
  entries); each id is T-NNNN, resolves through tickets.load(root) to exactly one folder whose
  status is not done or dropped, has its handoff committed at the start commit, and appears once
  across all lanes. The integration branch is --integration or fanout/<YYYY-MM-DD>; lane branches
  are <integration>-<lane> (a slash form would collide with the integration ref). --lanes-dir
  (relative to the cwd) defaults to <toplevel>/.worktrees/fanout. The lanes dir is never the
  toplevel itself; inside the toplevel it must be gitignored: for the default,
  `git check-ignore -q .worktrees/x` run from the toplevel must pass (else it refuses, naming
  `.worktrees/` to add to .gitignore); for an explicit --lanes-dir inside the toplevel, the same
  check runs on <its path relative to the toplevel>/x and a refusal names that path. An explicit
  --lanes-dir outside the toplevel needs no ignore check. It refuses when a lane branch,
  <lanes-dir>/<lane> or <lanes-dir>/integration exists, or when the integration branch is
  checked out in some worktree.
  --dry-run prints the plan (base sha, integration branch, per lane its branch, worktree and
  tickets, the gates, the driver, the close command) and exits 0, creating nothing.
  Setup, sequential: create the integration branch at --base (default HEAD) unless it exists
  (then reuse it; --base is ignored); `git worktree add <lanes-dir>/integration <integration>`;
  per lane `git worktree add -b <lane branch> <lanes-dir>/<lane> <integration>`; make
  <lanes-dir>/logs/. A ticket handoff missing in a lane worktree removes what this run created
  and exits 2 (the .sdlc/ trail must be committed).
  Then one thread per lane. A lane walks its tickets in order and stops at its first outcome
  other than `merged`; every later ticket is `skipped`. Per ticket:
    1. sync, under the lock: `git merge --ff --no-edit <integration>` in the lane worktree;
       a conflict is aborted (`sync conflict`). Under the lock so a lane never picks up a merge
       whose gates are still running.
    2. driver, outside the lock: `bash -c <driver>`, cwd the lane worktree, stdin /dev/null,
       output to <lanes-dir>/logs/<lane>-<id>.log, env FANOUT_LANE, FANOUT_TICKET, FANOUT_SLUG,
       FANOUT_HANDOFF (absolute), FANOUT_ROOT (absolute lane root), FANOUT_INTEGRATION,
       FANOUT_PLUGIN_ROOT, SDLC_HEADLESS=1 (hooks/block-background.sh denies Bash and Agent run_in_background),
       SDLC_ROLE=conductor (hooks/block-publish.sh blocks git push, gh writes, and package publishing
       in the Claude sessions the driver launches),
       and BASH_DEFAULT_TIMEOUT_MS=BASH_MAX_TIMEOUT_MS=3600000 as bench.sh sets them. Default: a headless conductor (claude -p --agent sdlc-lite:conductor, Opus
       medium) told to run /sdlc-lite:chain on the handoff unattended, run the filer but not
       close the ticket, and never commit, push, or publish. --driver replaces it (stubs,
       tests). Non-zero exit: `driver failed rc=<n>`, the tree left as is.
    3. commit in the lane: `git add -A`, `git commit -m "<id>: <title>"`; nothing staged:
       `no changes` (no merge, no close).
    4. under an exclusive fcntl.flock on <lanes-dir>/merge.lock, in the integration worktree:
       `git merge --no-ff --no-edit -m "Merge <lane branch>: <id>" <lane branch>` (a conflict
       is aborted: `merge conflict`); each --gate in order via bash -c, output to
       logs/gate-<lane>-<id>-<k>.log; the first red one runs `git reset --hard <pre-merge HEAD>`
       (`red: <gate> rc=<n>`). All green: copy the lane's <rel>/<slug>/ in when the integration
       copy has no filer-L*.md, run `tickets.py --root <rel> close <slug>` there (with
       --rewrite-refs when given: in numbered mode, files outside the ticket folder that cite
       <rel>/NNNN-<slug> are rewritten to <rel>/.NNNN-<slug>), and commit `close <id>`
       (`merged`), staging <rel> plus every path outside it that the close changed (a
       `git status --porcelain` snapshot before and after; never the whole worktree); a close
       refusal gives `merged, close refused: <first line>` (without --rewrite-refs, a refusal
       naming that flag adds `; fanout.py run --rewrite-refs rewrites them`) and the merge stands.
  Prints `[<lane>] <id> <event>` lines as they happen, writes <lanes-dir>/report.md
  (| Lane | Ticket | Outcome | Commit |, the integration branch and its tip, the worktree paths,
  the gates or that none were given) and prints it. Exit 0 only when every ticket is `merged`,
  else 1; 2 for a refusal. checkout, switch, reset and commit run only inside the lanes dir;
  nothing is pushed; the worktrees stay for inspection.

selftest
  A throwaway repo in a temp dir, a stub driver, two lanes: proves three merges, a red gate's
  merge reset, main untouched, closes on the integration branch, the pre-ticket sync, a lane
  stopping at its first failure, board.py --lanes listing both lanes, and that --dry-run and
  the refusals create nothing. A numbered-mode repo with docs/spec.md citing the ticket folder
  proves that without --rewrite-refs the close is refused (naming the flag) and the ticket stays
  open, that with it the ticket closes to .0001-x and the `close <id>` commit carries the
  rewritten docs/spec.md, the integration worktree stays clean either way, and the dry-run
  close: line matches each mode.
"""
import argparse, datetime, fcntl, os, pathlib, re, shlex, shutil, subprocess, sys, tempfile, threading

import tickets  # same scripts/ dir: the only front matter parser

SCRIPTS = pathlib.Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
LANE_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
RESERVED = ('integration', 'logs')
ENV = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}
# No auto gc or maintenance while lanes write refs and objects concurrently.
GIT_CFG = ('-c', 'gc.auto=0', '-c', 'maintenance.auto=false')
TIMEOUT_MS = '3600000'
PROMPT = ('Run /sdlc-lite:chain {handoff} unattended. No person is present: never ask the user and '
          'never use AskUserQuestion; where a step would ask, take its recommended option and go on. '
          'In the file stage run the filer only and do not close the ticket (no tickets.py close), '
          'because /fanout closes it on the integration branch after the merge. '
          'Never commit, push, or publish: fanout.py commits this lane when you finish.')


class Refuse(Exception):
    """A preflight or setup refusal: the message goes to stderr and run exits 2."""


def git(cwd, *args):
    return subprocess.run(['git', *GIT_CFG, '-C', str(cwd), *args], env=ENV, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True)


def git_out(cwd, *args):
    p = git(cwd, *args)
    if p.returncode:
        raise Refuse(f'git {" ".join(args)} failed: {p.stderr.strip() or p.returncode}')
    return p.stdout.strip()


def first_line(text, default=''):
    lines = [ln.strip() for ln in (text or '').splitlines() if ln.strip()]
    return lines[0] if lines else default


def cell(text):
    return ' '.join(str(text).split()).replace('|', '\\|')


def default_driver(handoff_rel):
    return ' '.join(shlex.quote(x) for x in (
        'claude', '-p', '--plugin-dir', str(PLUGIN), '--agent', 'sdlc-lite:conductor', '--model', 'opus',
        '--effort', 'medium', '--dangerously-skip-permissions', PROMPT.format(handoff=handoff_rel)))


class Ticket:
    def __init__(self, tid, slug, title):
        self.id, self.slug, self.title = tid, slug, title


class Lane:
    def __init__(self, name, tids):
        self.name, self.tids, self.tickets = name, tids, []
        self.branch = self.dir = None
        self.results = []  # (ticket id, outcome, commit)


def branch_clash(name, refs):
    """An existing ref that blocks creating refs/heads/<name>: the same ref, or a directory/file clash."""
    full = 'refs/heads/' + name
    for r in refs:
        if r == full or full.startswith(r + '/') or r.startswith(full + '/'):
            return r
    return None


def preflight(a):
    """Every check before any write. Returns the run context; raises Refuse."""
    cwd = pathlib.Path.cwd()
    p = git(cwd, 'rev-parse', '--is-inside-work-tree')
    if p.returncode or p.stdout.strip() != 'true':
        raise Refuse('not a git repo: run fanout.py inside a git work tree with a commit')
    if git(cwd, 'rev-parse', '--verify', '-q', 'HEAD').returncode:
        raise Refuse('git repo has no commit: commit first')
    top = pathlib.Path(git_out(cwd, 'rev-parse', '--show-toplevel')).resolve()
    root = (cwd / a.root).resolve()
    try:
        rel = root.relative_to(top)
    except ValueError:
        raise Refuse(f'--root {a.root} is {root}, outside the git toplevel {top}')
    if not root.is_dir():
        raise Refuse(f'--root {a.root}: {root} is not a dir')

    try:
        ts = tickets.load(root)
    except (OSError, UnicodeDecodeError) as e:
        raise Refuse(f'{root}: cannot read tickets: {e}')
    lanes, seen, errs = [], {}, []
    for spec in a.lanes:
        name, eq, ids = spec.partition('=')
        tids = [x.strip() for x in ids.split(',') if x.strip()]
        if not eq or not tids:
            errs.append(f'{spec!r}: want <lane>=<id>[,<id>...]')
            continue
        if not LANE_RE.fullmatch(name):
            errs.append(f'lane {name!r} must match ^[a-z0-9]+(-[a-z0-9]+)*$')
        elif name in RESERVED:
            errs.append(f'lane {name!r} is reserved (the lanes dir holds {" and ".join(RESERVED)})')
        elif any(x.name == name for x in lanes):
            errs.append(f'lane {name!r} is given twice')
        lane = Lane(name, tids)
        lanes.append(lane)
        for tid in tids:
            if not tickets.ID_RE.fullmatch(tid):
                errs.append(f'{name}: {tid!r} is not a ticket id like T-0001')
                continue
            if tid in seen:
                errs.append(f'{tid} appears in lane {seen[tid]} and lane {name}; a ticket runs in one lane only')
                continue
            seen[tid] = name
            hits = [(s, m) for s, m in ts if m.get('id') == tid]
            if not hits:
                errs.append(f'{tid}: no ticket under {root} has this id')
            elif len(hits) > 1:
                errs.append(f'{tid}: {len(hits)} folders share this id ({", ".join(s for s, _ in hits)})')
            elif hits[0][1].get('status') in ('done', 'dropped'):
                errs.append(f'{tid} ({hits[0][0]}): status is {hits[0][1]["status"]}, nothing to run')
            else:
                s, m = hits[0]
                lane.tickets.append(Ticket(tid, s, str(m.get('title', ''))))
    if not lanes and not errs:
        errs.append('no lanes given: want <lane>=<id>[,<id>...]')
    if errs:
        raise Refuse('\n'.join(errs))

    integration = a.integration or f'fanout/{datetime.date.today().isoformat()}'
    names = [integration] + [f'{integration}-{x.name}' for x in lanes]
    for n in names:
        if git(cwd, 'check-ref-format', '--branch', n).returncode:
            raise Refuse(f'{n!r} is not a valid branch name')
    refs = git_out(cwd, 'for-each-ref', '--format=%(refname)', 'refs/heads/').splitlines()
    reuse = ('refs/heads/' + integration) in refs
    if reuse:
        start = git_out(cwd, 'rev-parse', '--verify', f'refs/heads/{integration}^{{commit}}')
    else:
        clash = branch_clash(integration, refs)
        if clash:
            raise Refuse(f'integration branch {integration} clashes with the existing ref {clash}')
        base = a.base or 'HEAD'
        p = git(cwd, 'rev-parse', '--verify', '-q', f'{base}^{{commit}}')
        if p.returncode:
            raise Refuse(f'--base {base} is not a commit')
        start = p.stdout.strip()

    lanes_dir = (cwd / a.lanes_dir).resolve() if a.lanes_dir else top / '.worktrees' / 'fanout'
    if lanes_dir == top:
        raise Refuse(f'--lanes-dir {lanes_dir} is the work tree toplevel; lanes need their own dir')
    if top in lanes_dir.parents:
        # lanes inside the work tree must be gitignored, or every lane shows up as untracked files
        inner = lanes_dir.relative_to(top).as_posix()
        probe, want = ('.worktrees/x', '.worktrees/') if not a.lanes_dir else (f'{inner}/x', f'{inner}/')
        p = git(top, 'check-ignore', '-q', probe)
        if p.returncode == 1:
            what = 'the default lanes dir' if not a.lanes_dir else '--lanes-dir'
            raise Refuse(f'{what} {lanes_dir} is inside the work tree {top} but {want} is not gitignored; '
                         f'add {want} to .gitignore, or pass --lanes-dir outside the repo')
        if p.returncode:
            raise Refuse(f'git check-ignore {probe} failed: {p.stderr.strip() or p.returncode}')
    if lanes_dir.exists() and not lanes_dir.is_dir():
        raise Refuse(f'--lanes-dir {lanes_dir} exists and is not a dir')
    wts = git_out(cwd, 'worktree', 'list', '--porcelain').splitlines()
    wt_path = None
    for line in wts:
        if line.startswith('worktree '):
            wt_path = line[len("worktree "):]
        elif line == f'branch refs/heads/{integration}':
            raise Refuse(f'integration branch {integration} is checked out in {wt_path}; '
                         f'git worktree add cannot check it out twice')
    integ_dir = lanes_dir / 'integration'
    if integ_dir.exists():
        raise Refuse(f'{integ_dir} exists (an earlier run?); remove it with git worktree remove, '
                     f'or pass another --lanes-dir')
    for lane in lanes:
        lane.branch, lane.dir = f'{integration}-{lane.name}', lanes_dir / lane.name
        clash = branch_clash(lane.branch, refs)
        if clash:
            raise Refuse(f'lane branch {lane.branch} already exists or clashes with {clash}')
        if lane.dir.exists():
            raise Refuse(f'{lane.dir} already exists')

    relp = rel.as_posix()
    missing = []
    for lane in lanes:
        for t in lane.tickets:
            path = f'{t.slug}/handoff.md' if relp == '.' else f'{relp}/{t.slug}/handoff.md'
            if git(cwd, 'cat-file', '-e', f'{start}:{path}').returncode:
                missing.append(path)
    if missing:
        raise Refuse(f'not committed at {start[:12]}: {", ".join(missing)}; lanes see only committed '
                     f'files, so commit the .sdlc/ trail first')

    return {'cwd': cwd, 'top': top, 'root': root, 'rel': rel, 'lanes': lanes, 'integration': integration,
            'reuse': reuse, 'start': start, 'base': a.base or 'HEAD', 'lanes_dir': lanes_dir,
            'integ_dir': integ_dir, 'logs': lanes_dir / 'logs', 'gates': list(a.gate or []),
            'driver': a.driver, 'rewrite_refs': bool(getattr(a, 'rewrite_refs', False)),
            'numbered': tickets.config_numbered(root)}


def driver_for(ctx, t):
    if ctx['driver']:
        return ctx['driver']
    return default_driver((ctx['rel'] / t.slug / 'handoff.md').as_posix())


def print_plan(ctx):
    out = ['fanout plan (dry run: nothing created)']
    if ctx['reuse']:
        out.append(f"integration branch {ctx['integration']} exists at {ctx['start']}: reuse it (--base ignored)")
    else:
        out.append(f"base: {ctx['start']} ({ctx['base']})")
        out.append(f"integration branch: {ctx['integration']} (new, at the base)")
    out.append(f"integration worktree: {ctx['integ_dir']}")
    out.append(f"ticket root in each worktree: {ctx['rel'].as_posix()}")
    for lane in ctx['lanes']:
        out.append(f'lane {lane.name}: branch {lane.branch}, worktree {lane.dir}')
        for t in lane.tickets:
            out.append(f'  {t.id} {t.slug}: {t.title}')
    if ctx['gates']:
        out += [f'gate {k}: {g}' for k, g in enumerate(ctx['gates'], 1)]
    else:
        out.append('gates: none given (merges will not be gated)')
    if ctx['driver']:
        out.append(f"driver: {ctx['driver']}")
    else:
        out.append(f"driver: {default_driver('<handoff>')}")
        out.append("  (<handoff> is each ticket's handoff path relative to the lane worktree)")
    if ctx['rewrite_refs']:
        out.append('close: tickets.py close <slug> --rewrite-refs '
                   '(files citing a ticket folder are rewritten to its .NNNN-<slug> path)')
    elif ctx['numbered']:
        out.append('close: tickets.py close <slug> (numbered folders: a file citing a ticket folder '
                   'refuses the close; --rewrite-refs rewrites them)')
    else:
        out.append('close: tickets.py close <slug>')
    out.append(f"logs: {ctx['logs']}")
    print('\n'.join(out))


def setup(ctx):
    """Branches and worktrees, sequentially. On any failure, remove what this run created and raise."""
    made_dir, worktrees, branches = False, [], []
    cwd, lanes_dir, integration = ctx['cwd'], ctx['lanes_dir'], ctx['integration']

    def rollback():
        for w in reversed(worktrees):
            git(cwd, 'worktree', 'remove', '--force', str(w))
        for b in reversed(branches):
            git(cwd, 'branch', '-D', b)
        git(cwd, 'worktree', 'prune')
        if made_dir:
            shutil.rmtree(lanes_dir, ignore_errors=True)

    try:
        if not lanes_dir.exists():
            lanes_dir.mkdir(parents=True)
            made_dir = True
        if ctx['reuse']:
            print(f"reusing integration branch {integration} at {ctx['start'][:12]}", flush=True)
        else:
            git_out(cwd, 'branch', integration, ctx['start'])
            branches.append(integration)
            print(f"created integration branch {integration} at {ctx['start'][:12]} ({ctx['base']})", flush=True)
        git_out(cwd, 'worktree', 'add', '-q', str(ctx['integ_dir']), integration)
        worktrees.append(ctx['integ_dir'])
        print(f"worktree integration: {ctx['integ_dir']}", flush=True)
        for lane in ctx['lanes']:
            git_out(cwd, 'worktree', 'add', '-q', '-b', lane.branch, str(lane.dir), integration)
            worktrees.append(lane.dir)
            branches.append(lane.branch)
            print(f'worktree {lane.name}: {lane.dir} (branch {lane.branch})', flush=True)
        missing = [str(lane.dir / ctx['rel'] / t.slug / 'handoff.md')
                   for lane in ctx['lanes'] for t in lane.tickets
                   if not (lane.dir / ctx['rel'] / t.slug / 'handoff.md').is_file()]
        if missing:
            raise Refuse(f'missing in the lane worktrees: {", ".join(missing)}; the .sdlc/ trail must be '
                         f'committed; removed what this run created')
        ctx['logs'].mkdir(parents=True, exist_ok=True)
    except BaseException:
        rollback()
        raise


class MergeLock:
    """Exclusive fcntl.flock on <lanes-dir>/merge.lock (macOS has no flock binary), plus a thread lock
    so lane threads in this process serialize whatever the platform's flock semantics."""

    def __init__(self, path):
        self.path, self.local, self.f = path, threading.Lock(), None

    def __enter__(self):
        self.local.acquire()
        try:
            self.f = open(self.path, 'a')
            fcntl.flock(self.f, fcntl.LOCK_EX)
        except BaseException:
            if self.f:
                self.f.close()
            self.local.release()
            raise
        return self

    def __exit__(self, *exc):
        try:
            fcntl.flock(self.f, fcntl.LOCK_UN)
            self.f.close()
        finally:
            self.f = None
            self.local.release()


PRINT = threading.Lock()


def say(lane, tid, event):
    with PRINT:
        print(f'[{lane.name}] {tid} {event}', flush=True)


def in_merge(wt):
    return git(wt, 'rev-parse', '-q', '--verify', 'MERGE_HEAD').returncode == 0


def porcelain(wt):
    """The set of (status, path) entries in `git status --porcelain`, as paths tagged by status,
    so a before/after diff names every path whose state changed."""
    p = git(wt, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
    if p.returncode:
        raise Refuse(f'git status failed: {p.stderr.strip() or p.returncode}')
    items, parts, k = set(), p.stdout.split('\0'), 0
    while k < len(parts):
        e = parts[k]
        k += 1
        if len(e) < 4:
            continue
        items.add((e[:2], e[3:]))
        if e[0] in 'RC' and k < len(parts):
            items.add((e[:2], parts[k]))
            k += 1
    return items


def run_ticket(ctx, lane, t, lock):
    """One ticket through sync, driver, lane commit, and the locked merge. Returns (outcome, commit)."""
    wt, integ, rel, integration = lane.dir, ctx['integ_dir'], ctx['rel'], ctx['integration']
    with lock:
        p = git(wt, 'merge', '--ff', '--no-edit', integration)
        if p.returncode:
            if in_merge(wt):
                git(wt, 'merge', '--abort')
                return 'sync conflict', ''
            return f'sync failed: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', ''

    env = dict(ENV, FANOUT_LANE=lane.name, FANOUT_TICKET=t.id, FANOUT_SLUG=t.slug,
               FANOUT_HANDOFF=str(wt / rel / t.slug / 'handoff.md'), FANOUT_ROOT=str(wt / rel),
               FANOUT_INTEGRATION=integration, FANOUT_PLUGIN_ROOT=str(PLUGIN), SDLC_HEADLESS='1', SDLC_ROLE='conductor',
               BASH_DEFAULT_TIMEOUT_MS=TIMEOUT_MS, BASH_MAX_TIMEOUT_MS=TIMEOUT_MS)
    log = ctx['logs'] / f'{lane.name}-{t.id}.log'
    say(lane, t.id, f'driver started (log {log})')
    with open(log, 'wb') as f:
        rc = subprocess.run(['bash', '-c', driver_for(ctx, t)], cwd=str(wt), stdin=subprocess.DEVNULL,
                            stdout=f, stderr=subprocess.STDOUT, env=env).returncode
    if rc:
        return f'driver failed rc={rc}', ''

    p = git(wt, 'add', '-A')
    if p.returncode:
        return f'lane add failed: {first_line(p.stderr, f"rc={p.returncode}")}', ''
    if git(wt, 'diff', '--cached', '--quiet').returncode == 0:
        return 'no changes', ''
    p = git(wt, 'commit', '-q', '-m', f'{t.id}: {t.title}')
    if p.returncode:
        return f'lane commit failed: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', ''
    lane_sha = git_out(wt, 'rev-parse', 'HEAD')
    say(lane, t.id, f'committed {lane_sha[:7]} on {lane.branch}')

    with lock:
        before = git_out(integ, 'rev-parse', 'HEAD')
        p = git(integ, 'merge', '--no-ff', '--no-edit', '-m', f'Merge {lane.branch}: {t.id}', lane.branch)
        if p.returncode:
            conflict = in_merge(integ)
            if not conflict or git(integ, 'merge', '--abort').returncode:
                git(integ, 'reset', '-q', '--hard', before)
            if conflict:
                return 'merge conflict', lane_sha[:7]
            return f'merge failed: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}', lane_sha[:7]
        merge_sha = git_out(integ, 'rev-parse', 'HEAD')
        for k, gate in enumerate(ctx['gates'], 1):
            with open(ctx['logs'] / f'gate-{lane.name}-{t.id}-{k}.log', 'wb') as f:
                rc = subprocess.run(['bash', '-c', gate], cwd=str(integ), stdin=subprocess.DEVNULL,
                                    stdout=f, stderr=subprocess.STDOUT, env=ENV).returncode
            if rc:
                git_out(integ, 'reset', '-q', '--hard', before)
                return f'red: {gate} rc={rc}', lane_sha[:7]
        src, dst = wt / rel / t.slug, integ / rel / t.slug
        if not any(dst.glob('filer-L*.md')) and src.is_dir():
            shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
        argv = [sys.executable, str(SCRIPTS / 'tickets.py'), '--root', rel.as_posix(), 'close', t.slug]
        if ctx['rewrite_refs']:
            argv.append('--rewrite-refs')
        pre = porcelain(integ)
        p = subprocess.run(argv, cwd=str(integ), stdin=subprocess.DEVNULL, env=ENV, capture_output=True, text=True)
        if p.returncode:
            # the close wrote nothing; drop any copied files so a later close commit cannot sweep them in
            git(integ, 'clean', '-fdq', '--', (rel / t.slug).as_posix())
            why = f'merged, close refused: {first_line(p.stderr or p.stdout, f"rc={p.returncode}")}'
            if not ctx['rewrite_refs'] and '--rewrite-refs' in (p.stderr or '') + (p.stdout or ''):
                why += '; fanout.py run --rewrite-refs rewrites them'
            return why, merge_sha[:7]
        relp = rel.as_posix()
        changed = {path for _, path in porcelain(integ) - pre}
        extra = sorted(path for path in changed
                       if relp != '.' and path != relp and not path.startswith(relp + '/'))
        git_out(integ, 'add', '-A', '--', relp, *extra)
        if git(integ, 'diff', '--cached', '--quiet').returncode:
            git_out(integ, 'commit', '-q', '-m', f'close {t.id}')
        return 'merged', merge_sha[:7]


def run_lane(ctx, lane, lock):
    stopped = False
    for t in lane.tickets:
        if stopped:
            outcome, commit = 'skipped', ''
        else:
            try:
                outcome, commit = run_ticket(ctx, lane, t, lock)
            except Exception as e:  # a git or IO failure mid-ticket: record it, stop the lane
                outcome, commit = f'error: {first_line(str(e), type(e).__name__)}', ''
            stopped = outcome != 'merged'
        lane.results.append((t.id, outcome, commit))
        say(lane, t.id, outcome)


def report(ctx):
    integ = ctx['integ_dir']
    tip = git(integ, 'rev-parse', 'HEAD').stdout.strip()
    out = ['# fanout report', '',
           f"- Integration branch: `{ctx['integration']}` at `{tip}`"
           + (' (reused)' if ctx['reuse'] else f" (from `{ctx['start'][:12]}`)"),
           f'- Integration worktree: `{integ}`']
    out += [f'- Lane `{x.name}`: `{x.dir}` (branch `{x.branch}`)' for x in ctx['lanes']]
    if ctx['gates']:
        out += [f'- Gate {k}: `{g}`' for k, g in enumerate(ctx['gates'], 1)]
    else:
        out.append('- No gates given: merges were not gated.')
    out.append(f"- Logs: `{ctx['logs']}`")
    out += ['', '| Lane | Ticket | Outcome | Commit |', '|---|---|---|---|']
    for lane in ctx['lanes']:
        for tid, outcome, commit in lane.results:
            out.append(f'| {lane.name} | {tid} | {cell(outcome)} | {commit or "-"} |')
    text = '\n'.join(out) + '\n'
    (ctx['lanes_dir'] / 'report.md').write_text(text, encoding='utf-8')
    return text


def cmd_run(a):
    try:
        ctx = preflight(a)
        if a.dry_run:
            print_plan(ctx)
            return 0
        setup(ctx)
    except Refuse as e:
        print(f'fanout: {e}', file=sys.stderr)
        return 2
    lock = MergeLock(ctx['lanes_dir'] / 'merge.lock')
    threads = [threading.Thread(target=run_lane, args=(ctx, lane, lock), name=lane.name, daemon=True)
               for lane in ctx['lanes']]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    text = report(ctx)
    print()
    print(text, end='')
    results = [r for lane in ctx['lanes'] for r in lane.results]
    ok = bool(results) and all(outcome == 'merged' for _, outcome, _ in results)
    return 0 if ok else 1


# ---------- selftest ----------

STUB = r'''#!/usr/bin/env bash
set -eu
[ "${SDLC_HEADLESS:-}" = 1 ] || { echo "SDLC_HEADLESS not set" >&2; exit 1; }
[ "${SDLC_ROLE:-}" = conductor ] || { echo "SDLC_ROLE not conductor" >&2; exit 1; }
echo "$FANOUT_TICKET" >"$FANOUT_TICKET.txt"
ls >"$FANOUT_TICKET.saw"
printf '## Warnings\nNone\n\n## Follow-ups\nNone\n' >"$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"
if [ "$FANOUT_TICKET" = T-0003 ]; then touch RED; fi
if [ "$FANOUT_TICKET" = T-0002 ]; then
  i=0
  until git cat-file -e "$FANOUT_INTEGRATION:T-0001.txt" 2>/dev/null; do
    i=$((i + 1))
    [ "$i" -le 600 ] || { echo "timed out waiting for T-0001.txt on $FANOUT_INTEGRATION" >&2; exit 1; }
    sleep 0.1
  done
fi
'''


def selftest():
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def sh(cwd, *args):
        return subprocess.run(['git', '-C', str(cwd), *args], env=ENV, capture_output=True, text=True)

    def make_repo(repo, specs, extra=None):
        (repo / '.sdlc').mkdir(parents=True)
        for name, body in (extra or {}).items():
            (repo / name).write_text(body, encoding='utf-8')
        for slug, tid, status in specs:
            (repo / '.sdlc' / slug).mkdir()
            (repo / '.sdlc' / slug / 'handoff.md').write_text(
                f'---\nid: {tid}\ntitle: "Ticket {slug}"\ntype: chore\nstatus: {status}\nsize: S\n'
                f'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\n{slug}\n', encoding='utf-8')
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                     ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                     ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
            p = sh(repo, *args)
            expect(f'fixture git {args} exited 0, got {p.returncode} stderr={p.stderr!r}', p.returncode == 0)

    def fanout(cwd, *args):
        return subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', *args],
                              cwd=str(cwd), env=ENV, capture_output=True, text=True, timeout=300)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp).resolve()

        # 1. Two lanes, a stub driver, a gate that goes red on T-0003.
        repo, lanes = tmp / 'repo', tmp / 'lanes'
        make_repo(repo, [(s, f'T-000{i}', 'ready') for i, s in enumerate('abcde', 1)])
        stub = tmp / 'stub.sh'
        stub.write_text(STUB)
        stub.chmod(0o755)
        main0 = sh(repo, 'rev-parse', 'main').stdout.strip()
        proc = fanout(repo, 'alpha=T-0001,T-0003,T-0005', 'beta=T-0002,T-0004', '--base', 'main',
                      '--integration', 'fanout/test', '--lanes-dir', str(lanes), '--driver', shlex.quote(str(stub)),
                      '--gate', 'test ! -e RED')
        ran = f'(stdout={proc.stdout!r} stderr={proc.stderr!r})'
        expect(f'run exits 1 (T-0003 red, T-0005 skipped), got {proc.returncode} {ran}', proc.returncode == 1)
        expect('main sha unchanged', sh(repo, 'rev-parse', 'main').stdout.strip() == main0 and main0)
        expect('the repo still has main checked out',
               sh(repo, 'symbolic-ref', 'HEAD').stdout.strip() == 'refs/heads/main')
        status = sh(repo, 'status', '--porcelain')
        expect(f'git status --porcelain empty in the repo, got {status.stdout!r}',
               status.returncode == 0 and status.stdout == '')
        merges = sh(repo, 'rev-list', '--merges', '--count', 'fanout/test').stdout.strip()
        expect(f'fanout/test has exactly three merge commits, got {merges!r}', merges == '3')
        for f in ('T-0001.txt', 'T-0002.txt', 'T-0004.txt'):
            expect(f'fanout/test holds {f}', sh(repo, 'cat-file', '-e', f'fanout/test:{f}').returncode == 0)
        for f in ('T-0003.txt', 'RED'):
            expect(f'fanout/test does not hold {f} (the red merge was reset)',
                   sh(repo, 'cat-file', '-e', f'fanout/test:{f}').returncode != 0)
        for slug, want in (('a', 'done'), ('b', 'done'), ('c', 'ready'), ('d', 'done'), ('e', 'ready')):
            shown = sh(repo, 'show', f'fanout/test:.sdlc/{slug}/handoff.md')
            expect(f'fanout/test:.sdlc/{slug}/handoff.md says status: {want}, got {shown.stdout[:120]!r}',
                   shown.returncode == 0 and re.search(rf'^status: {want}\b', shown.stdout, re.M))
        rows = {}
        rep = lanes / 'report.md'
        text = rep.read_text() if rep.is_file() else ''
        for line in text.splitlines():
            c = [x.strip() for x in line.strip('|').split('|')]
            if line.startswith('| ') and len(c) == 4 and tickets.ID_RE.fullmatch(c[1]):
                rows[c[1]] = (c[0], c[2])
        expect(f'report rows for all five tickets, got {rows}', len(rows) == 5)
        for tid, lane in (('T-0001', 'alpha'), ('T-0002', 'beta'), ('T-0004', 'beta')):
            expect(f'report: {tid} merged in {lane}, got {rows.get(tid)}', rows.get(tid) == (lane, 'merged'))
        expect(f'report: T-0003 red, got {rows.get("T-0003")}',
               rows.get('T-0003', ('', ''))[1].startswith('red: test ! -e RED rc='))
        expect(f'report: T-0005 skipped, got {rows.get("T-0005")}', rows.get('T-0005') == ('alpha', 'skipped'))
        expect('the report was printed', 'fanout report' in proc.stdout and '| alpha | T-0005 | skipped |' in proc.stdout)
        expect('alpha worktree kept, holding its red T-0003.txt', (lanes / 'alpha' / 'T-0003.txt').is_file())
        expect('alpha stopped after T-0003: no T-0005.txt in the alpha worktree',
               (lanes / 'alpha').is_dir() and not (lanes / 'alpha' / 'T-0005.txt').exists())
        saw = lanes / 'beta' / 'T-0004.saw'
        seen = saw.read_text().split() if saw.is_file() else []
        expect(f'T-0004.saw in beta lists T-0001.txt (synced before the ticket), got {seen}', 'T-0001.txt' in seen)
        board = subprocess.run([sys.executable, str(SCRIPTS / 'board.py'), '--lanes', '--root', str(repo / '.sdlc')],
                               env=ENV, capture_output=True, text=True)
        cells = {}
        for line in board.stdout.splitlines():
            c = [x.strip() for x in line.strip('|').split('|')]
            if line.startswith('| ') and len(c) == 3:
                cells[c[0]] = c[1]
        expect(f'board.py --lanes exits 0, got {board.returncode} stderr={board.stderr!r}', board.returncode == 0)
        expect(f'board.py --lanes lists alpha on fanout/test-alpha, got {cells}', cells.get('alpha') == 'fanout/test-alpha')
        expect(f'board.py --lanes lists beta on fanout/test-beta, got {cells}', cells.get('beta') == 'fanout/test-beta')

        # 2. --dry-run and refusals create nothing.
        rr, rl = tmp / 'refuse', tmp / 'rlanes'
        make_repo(rr, [('x', 'T-0001', 'ready'), ('y', 'T-0002', 'done')], {'.gitignore': '.worktrees/\n'})
        default_lanes = rr / '.worktrees' / 'fanout'
        proc = fanout(rr, '--dry-run', '--integration', 'fanout/dry', 'alpha=T-0001')
        expect(f'--dry-run exits 0 naming the lane branch and the default lanes dir under .worktrees/fanout, '
               f'got {proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}',
               proc.returncode == 0 and 'fanout/dry-alpha' in proc.stdout
               and f'integration worktree: {default_lanes / "integration"}' in proc.stdout
               and f'worktree {default_lanes / "alpha"}' in proc.stdout)
        proc = fanout(rr, '--dry-run', '--lanes-dir', str(rl), 'alpha=T-0001')
        expect(f'--dry-run with --lanes-dir exits 0, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 0 and str(rl) in proc.stdout)
        for label, args in (('the same id in two lanes', ('alpha=T-0001', 'beta=T-0001')),
                            ('an unknown id', ('alpha=T-0009',)),
                            ('a done ticket', ('alpha=T-0002',))):
            # a no-op driver: if a refusal regresses, the run must never reach the default claude driver
            proc = fanout(rr, '--lanes-dir', str(rl), '--driver', 'exit 3', *args)
            expect(f'{label} exits 2 with a reason, got {proc.returncode} stderr={proc.stderr!r}',
                   proc.returncode == 2 and proc.stderr.strip() and 'Traceback' not in proc.stderr)
        expect('dry run and refusals create no fanout/* branch',
               sh(rr, 'branch', '--list', 'fanout/*').stdout.strip() == '')
        expect('dry run and refusals add no worktree',
               len([ln for ln in sh(rr, 'worktree', 'list').stdout.splitlines() if ln.strip()]) == 1)
        expect('dry run and refusals create no lanes dir', not rl.exists() and not default_lanes.exists())
        expect('dry run and refusals leave the status clean', sh(rr, 'status', '--porcelain').stdout == '')

        # 3. A repo that does not ignore .worktrees/ refuses the default lanes dir, creating nothing.
        ru = tmp / 'unignored'
        make_repo(ru, [('x', 'T-0001', 'ready')])
        proc = fanout(ru, '--dry-run', 'alpha=T-0001')
        expect(f'unignored .worktrees/: default-dir --dry-run exits 2 naming .gitignore and .worktrees/, '
               f'got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 2 and '.gitignore' in proc.stderr and '.worktrees/' in proc.stderr
               and 'Traceback' not in proc.stderr)
        expect('unignored .worktrees/: no .worktrees dir created', not (ru / '.worktrees').exists())
        expect('unignored .worktrees/: no fanout/* branch', sh(ru, 'branch', '--list', 'fanout/*').stdout.strip() == '')
        expect('unignored .worktrees/: no worktree added',
               len([ln for ln in sh(ru, 'worktree', 'list').stdout.splitlines() if ln.strip()]) == 1)

        # 4. Numbered mode, a file outside the ticket root citing the ticket folder: without
        # --rewrite-refs the close is refused; with it the close commit carries the rewrite.
        numbered_stub = ('printf "## Warnings\\nNone\\n\\n## Follow-ups\\nNone\\n" '
                         '> "$FANOUT_ROOT/$FANOUT_SLUG/filer-L1.md"; echo x > x.txt')

        def make_numbered(repo):
            (repo / '.sdlc' / '0001-x').mkdir(parents=True)
            (repo / 'docs').mkdir()
            (repo / '.sdlc' / 'config').write_text('ticket_folders: numbered\n', encoding='utf-8')
            (repo / '.sdlc' / '0001-x' / 'handoff.md').write_text(
                '---\nid: T-0001\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
                'depends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n', encoding='utf-8')
            (repo / 'docs' / 'spec.md').write_text('see .sdlc/0001-x/handoff.md\n', encoding='utf-8')
            (repo / '.gitignore').write_text('.worktrees/\n', encoding='utf-8')
            for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'fanout selftest'),
                         ('config', 'user.email', 'selftest@example.invalid'), ('config', 'commit.gpgsign', 'false'),
                         ('add', '-A'), ('commit', '-q', '-m', 'fixture')):
                q = sh(repo, *args)
                expect(f'numbered fixture git {args} exited 0, got {q.returncode}', q.returncode == 0)

        def outcome(repo):
            rep = repo / '.worktrees' / 'fanout' / 'report.md'
            for line in (rep.read_text() if rep.is_file() else '').splitlines():
                c = [x.strip() for x in line.strip('|').split('|')]
                if line.startswith('| ') and len(c) == 4 and c[1] == 'T-0001':
                    return c[2]
            return None

        integ_clean = lambda repo: sh(repo / '.worktrees' / 'fanout' / 'integration', 'status', '--porcelain').stdout == ''
        nr = tmp / 'numbered-off'
        make_numbered(nr)
        proc = fanout(nr, '--dry-run', 'a=T-0001')
        expect(f'numbered dry run without the flag names the refusal, got {proc.stdout!r}',
               proc.returncode == 0 and '\nclose: tickets.py close <slug> (numbered folders' in proc.stdout)
        proc = fanout(nr, '--dry-run', '--rewrite-refs', 'a=T-0001')
        expect(f'dry run with the flag shows it, got {proc.stdout!r}',
               proc.returncode == 0 and '\nclose: tickets.py close <slug> --rewrite-refs' in proc.stdout)
        proc = fanout(nr, 'a=T-0001', '--integration', 'fanout/t', '--driver', numbered_stub)
        got = outcome(nr) or ''
        expect(f'numbered without the flag exits 1, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 1)
        expect(f'numbered without the flag: merged, close refused naming --rewrite-refs, got {got!r}',
               got.startswith('merged, close refused') and '--rewrite-refs' in got)
        shown = sh(nr, 'show', 'fanout/t:.sdlc/0001-x/handoff.md').stdout
        expect(f'numbered without the flag: 0001-x still ready, got {shown[:120]!r}',
               re.search(r'^status: ready\b', shown, re.M))
        expect('numbered without the flag: integration worktree clean', integ_clean(nr))

        nw = tmp / 'numbered-on'
        make_numbered(nw)
        proc = fanout(nw, 'a=T-0001', '--integration', 'fanout/t', '--rewrite-refs', '--driver', numbered_stub)
        expect(f'numbered with the flag exits 0, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 0)
        expect(f'numbered with the flag: merged, got {outcome(nw)!r}', outcome(nw) == 'merged')
        expect('numbered with the flag: tip is close T-0001',
               sh(nw, 'log', '-1', '--format=%s', 'fanout/t').stdout.strip() == 'close T-0001')
        expect('numbered with the flag: close commit changes docs/spec.md',
               'docs/spec.md' in sh(nw, 'diff', '--name-only', 'fanout/t~1', 'fanout/t').stdout.split())
        expect('numbered with the flag: docs/spec.md cites the dot path',
               sh(nw, 'show', 'fanout/t:docs/spec.md').stdout == 'see .sdlc/.0001-x/handoff.md\n')
        expect('numbered with the flag: .sdlc/.0001-x/handoff.md on the branch',
               sh(nw, 'cat-file', '-e', 'fanout/t:.sdlc/.0001-x/handoff.md').returncode == 0)
        expect('numbered with the flag: integration worktree clean', integ_clean(nw))

    if misses:
        print('fanout selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('fanout selftest: PASS')
    return 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    if argv[:1] != ['run']:
        print('usage: fanout.py run <lane>=<id>[,<id>...]... [--root .sdlc] [--base REF] [--integration BRANCH] '
              '[--lanes-dir DIR] [--gate CMD]... [--driver CMD] [--rewrite-refs] [--dry-run] | fanout.py selftest', file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(prog='fanout.py run', description=__doc__.split('\n')[0])
    ap.add_argument('lanes', nargs='+', metavar='<lane>=<id>[,<id>...]')
    ap.add_argument('--root', default='.sdlc', help='ticket root, relative to the cwd (default .sdlc)')
    ap.add_argument('--base', help='commit for a new integration branch (default HEAD)')
    ap.add_argument('--integration', help='integration branch (default fanout/<YYYY-MM-DD>)')
    ap.add_argument('--lanes-dir', help='where the worktrees, logs and report go '
                    '(default <toplevel>/.worktrees/fanout); inside the repo it must be gitignored '
                    '(add .worktrees/ or the dir to .gitignore) or run refuses with exit 2')
    ap.add_argument('--gate', action='append', metavar='CMD', help='run in the integration worktree after each merge; '
                    'red resets the merge (repeatable, in order)')
    ap.add_argument('--driver', metavar='CMD', help='run per ticket in the lane worktree via bash -c '
                    '(default: a headless sdlc-lite conductor running /sdlc-lite:chain)')
    ap.add_argument('--rewrite-refs', action='store_true', help='opt-in, numbered mode only: when a ticket '
                    'closes, rewrite files outside the ticket folder that cite <rel>/NNNN-<slug> to '
                    '<rel>/.NNNN-<slug> (passed to tickets.py close). Without it such a close is refused')
    ap.add_argument('--dry-run', action='store_true', help='print the plan and create nothing')
    return cmd_run(ap.parse_intermixed_args(argv[1:]))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
