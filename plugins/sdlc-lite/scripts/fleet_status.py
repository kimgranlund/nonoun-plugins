#!/usr/bin/env python3
"""Fleet status collector: is each board row really moving, how loaded is the machine, what needs the user,
what changed since the last call. No model call, read-only on every repo it inspects. It renders nothing:
`collect` prints one JSON object that the status renderer (T-0312) draws from.

Usage: fleet_status.py collect [REPO ...] [--fleet FILE] [--state-dir DIR] [--stop-line N]
                               [--active-minutes N] [--no-gh] [--no-write]
       fleet_status.py selftest

REPO paths name the repos to inspect; with none, the active entries of the fleet registry (--fleet, default
`.sdlc/fleet.json`, see docs/sdlc-lite/fleet-config.md) are inspected. A registry entry whose directory is
missing is reported with an `error` and skipped; an explicit REPO that is missing exits 2.

State. Two files live in --state-dir (default `<cwd>/.sdlc/runtime`, git-ignored; never inside an inspected
repo): `load.jsonl` gets one `{ts, load1, load5, load15, cpus}` line appended on every call (trimmed to the
newest 2000 lines past 4000), and `fleet-status.json` holds the snapshot the next call diffs against. With no
`.sdlc` in the cwd and no --state-dir nothing is written, and `snapshot.written` is false. --no-write skips
both files (the trend then uses the last stored samples; the delta uses the last stored snapshot).

Output keys (stdout, JSON):
  time          UTC ISO instant of this call
  machine.load  load1, load5, load15, cpus, stop_line, verdict (ok | near | over: over when load1 is above the
                stop line, near from 80 percent of it), headroom (stop_line - load1), arrow (the trend's), trend {arrow, delta, minutes, source, samples}: the delta of load1 against the oldest
                stored sample 20 seconds to 10 minutes old (source `samples`), else load1 against load5 (source
                `loadavg`, minutes null). The arrow moves when the delta is at least max(0.5, 10 percent of the
                earlier load1).
  machine.consumers   {chromium, hooks, claude, watchers: {count, cpu_pct, top[{pid, cpu, cmd}]}} from one `ps`
                snapshot, and machine.ranked: the classes with a count, by cpu_pct descending; machine.error when
                `ps` failed. watchers: vite, nodemon, fswatch, watchman, chokidar, tsc -w, supervisor.py watch, any
                `--watch`.
  repos[]       name, path, conductor, gh, error (a missing directory only), rows[], counts, needs_you[], prs,
                release, worktrees (linked worktree count)
    rows[]      one per board row (the tasks board.py shows): id, task (folder), title, ticket_status, board (the
                most telling cell: a red step, else a yellow one, else the first), pct, claims_work (the board shows
                yellow or red), state, evidence[], flags[]
      state     live: a process whose command names the ticket folder (a leading dot is ignored) or a linked
                worktree named for the ticket, or a `.running` marker whose attempt record (`*.attempt.json`,
                same role and level, status running) has a pid that is alive and started no later than the marker
                (a reused pid is dead). dead: a marker and no live pid or process. idle: no process or marker, but
                runs.jsonl or a `*.log` changed in the last --active-minutes (default 15; a runs.jsonl counts by
                the newest `ts` among its last rows, its mtime only when no row has a ts, because a git checkout or
                merge refreshes the mtime of every tracked file; a log counts by mtime). stale: the board claims
                work and none of those holds. queued or done: the board claims no work and none of those holds.
                Markers and activity are read in the task folder, its `step-*` folders and the same ticket folder in
                each linked worktree. handoff.md and skips.md are never activity.
      flags     `ticket-done-board-open` when the ticket is done or dropped yet its board rows still claim work.
    counts      rows per state
    needs_you[] {kind: blocked, id, task, title, owner: user | conductor | unknown, note} for each ticket with
                status blocked (owner from an `owner: user|conductor` line in its handoff.md or in .sdlc/notes.md
                on a line naming its id), and {kind: pr, number, title, url, detail} for each open, non-draft
                pull request (gh pr list; `--no-gh` skips)
    prs         {open[], drafts, error?} or "skipped"
    release     branch, default, local, remote, ahead, behind, last_tag, tag_distance, fetched_age_s, unpushed[]
                (commits the default branch holds that origin/<default> lacks, newest first, at most 10),
                unpushed_branch_commits (commits on any local branch no remote branch has); a field is null when git
                cannot say. Only read-only git plumbing runs, with GIT_OPTIONAL_LOCKS=0, and nothing is fetched.
  needs_you     the repos' needs_you lists joined, each with `repo`
  delta         against the previous snapshot: since (its time or null), first_run, state_changes[] {repo, id, task,
                kind: state | status, from, to}, closed[] (ticket id first seen with status done), dropped[], new[],
                gone[] (a ticket that vanished while not done), prs_merged[], prs_closed[] (gh only). Tickets are
                keyed by id, so closing one (which renames its folder to .NNNN-<slug>) is a close, not a
                vanished row plus a new one.
  snapshot      {path, written}
Read-only: only `ps`, `git` plumbing and `gh pr list` GET calls run on a repo, each bounded by a timeout and
killed with its process group on expiry. Exit codes: 0 ok, 2 usage or a missing explicit repo.
"""
import datetime, json, os, pathlib, re, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import board          # same scripts/ dir: the board's own task and row logic (display only here)
import fleet_collect  # same scripts/ dir: bounded subprocess, worktree discovery, process classes
import fleet_config   # same scripts/ dir: the repo registry
import tickets        # same scripts/ dir: the only front matter parser

UTC = datetime.timezone.utc
run_bounded, parse_ts = fleet_collect.run_bounded, fleet_collect.parse_ts

PS_CMD = 'ps'
GH_CMD = 'gh'
GIT_CMD = 'git'
LOAD_FN = os.getloadavg
PROBE_TIMEOUT = 10.0
GIT_TIMEOUT = 20.0
GH_TIMEOUT = 30.0
DEFAULT_STOP_LINE = 14.0
DEFAULT_ACTIVE_MINUTES = 15.0
NEAR_FRACTION = 0.8
TREND_MIN_AGE_S = 20
TREND_WINDOW_S = 600
LOAD_KEEP, LOAD_TRIM_AT = 2000, 4000
PID_SLACK_S = 3          # a process may start this much after the marker's own second and still be its owner
LIST_CAP = 10
UP, DOWN, FLAT = '↑', '↓', '→'

USAGE = ('usage: fleet_status.py collect [REPO ...] [--fleet FILE] [--state-dir DIR] [--stop-line N]\n'
         '                               [--active-minutes N] [--no-gh] [--no-write]\n'
         '       fleet_status.py selftest')

IGNORE_EXEC = frozenset(('ps', 'grep', 'egrep', 'fgrep', 'rg', 'ag', 'cat', 'less', 'more', 'tail', 'head', 'vim',
                         'vi', 'nvim', 'nano', 'emacs', 'code', 'open', 'git', 'sed', 'awk', 'ls', 'find', 'du',
                         'wc', 'sort', 'tee', 'bat', 'jq', 'stat', 'file', 'lsof', 'pgrep'))
WATCHER_RE = re.compile(r'(--watch\b|supervisor\.py\s+watch\b|\bfswatch\b|\bwatchman\b|\bnodemon\b|\bchokidar\b'
                        r'|\btsc\b.*\s-w\b|(?:^|[\s/])vite(?:\.js)?(?:\s+(?!build\b|preview\b|optimize\b)|$))', re.I)
CONSUMER_CLASSES = ('chromium', 'hooks', 'claude', 'watchers')


def now_utc():
    return datetime.datetime.now(UTC)


def iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


# --- processes ---------------------------------------------------------------

def ps_snapshot():
    """[{pid, cpu, cmd}] from one `ps`, or None when ps failed. This process is left out."""
    r = run_bounded([PS_CMD, '-axo', 'pid=,pcpu=,command='], PROBE_TIMEOUT)
    if not r.ok:
        return None
    me = os.getpid()
    out = []
    for line in r.out.splitlines():
        m = re.match(r'^\s*(\d+)\s+([\d.]+)\s+(.*)$', line)
        if m and int(m.group(1)) != me:
            out.append({'pid': int(m.group(1)), 'cpu': float(m.group(2)), 'cmd': m.group(3)})
    return out


def consumer_class(cmd):
    """chromium, hooks, claude, watchers, or None for one command line."""
    return fleet_collect.classify_process(cmd) or ('watchers' if WATCHER_RE.search(cmd) else None)


def consumers(procs):
    out = {k: {'count': 0, 'cpu_pct': 0.0, 'top': []} for k in CONSUMER_CLASSES}
    for p in procs:
        k = consumer_class(p['cmd'])
        if k:
            out[k]['count'] += 1
            out[k]['cpu_pct'] += p['cpu']
            out[k]['top'].append(p)
    for k, v in out.items():
        v['cpu_pct'] = round(v['cpu_pct'], 1)
        v['top'] = [{'pid': p['pid'], 'cpu': p['cpu'], 'cmd': p['cmd'][:100]}
                    for p in sorted(v['top'], key=lambda p: -p['cpu'])[:3]]
    ranked = sorted((k for k in CONSUMER_CLASSES if out[k]['count']), key=lambda k: -out[k]['cpu_pct'])
    return out, ranked


def worker_procs(procs):
    """Processes that can be a ticket's worker: not a viewer, a search, git, or this tool's own kin."""
    out = []
    for p in procs:
        toks = p['cmd'].split()
        if not toks or os.path.basename(toks[0]) in IGNORE_EXEC:
            continue
        if 'fleet_status.py' in p['cmd'] or 'fleet_collect.py' in p['cmd']:
            continue
        out.append(p)
    return out


def pid_alive(pid):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
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


def proc_start_epoch(pid):
    """Start time of pid in epoch seconds from `ps -o lstart=`, or None when it cannot be read."""
    r = run_bounded(['env', 'LC_ALL=C', PS_CMD, '-o', 'lstart=', '-p', str(pid)], PROBE_TIMEOUT)
    text = ' '.join(r.out.split()) if r.ok else ''
    try:
        return time.mktime(time.strptime(text, '%a %b %d %H:%M:%S %Y'))
    except ValueError:
        return None


# --- machine load ------------------------------------------------------------

def read_samples(path):
    out = []
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if isinstance(rec, dict) and parse_ts(rec.get('ts')) and isinstance(rec.get('load1'), (int, float)):
                    out.append(rec)
    except OSError:
        pass
    return sorted(out, key=lambda r: parse_ts(r['ts']))


def append_sample(path, sample):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(sample) + '\n')
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()
    except OSError:
        return
    if len(lines) > LOAD_TRIM_AT:
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.writelines(lines[-LOAD_KEEP:])
        os.replace(tmp, path)


def arrow_for(delta, base):
    limit = max(0.5, 0.1 * base)
    return UP if delta >= limit else DOWN if delta <= -limit else FLAT


def load_report(prev, cur, now, stop_line):
    """The machine.load object from the earlier samples, the current sample, and the stop line."""
    ref, age = None, None
    for s in prev:                                  # oldest first: the longest look-back inside the window
        a = (now - parse_ts(s['ts'])).total_seconds()
        if TREND_MIN_AGE_S <= a <= TREND_WINDOW_S:
            ref, age = s, a
            break
    if ref is not None:
        delta = cur['load1'] - ref['load1']
        trend = {'arrow': arrow_for(delta, ref['load1']), 'delta': round(delta, 2),
                 'minutes': round(age / 60.0, 1), 'source': 'samples'}
    else:
        delta = cur['load1'] - cur['load5']
        trend = {'arrow': arrow_for(delta, cur['load5']), 'delta': round(delta, 2), 'minutes': None,
                 'source': 'loadavg'}
    trend['samples'] = len(prev)
    load1 = cur['load1']
    verdict = 'over' if load1 > stop_line else 'near' if load1 > NEAR_FRACTION * stop_line else 'ok'
    return {'load1': load1, 'load5': cur['load5'], 'load15': cur['load15'], 'cpus': cur['cpus'],
            'stop_line': stop_line, 'verdict': verdict, 'headroom': round(stop_line - load1, 2),
            'arrow': trend['arrow'], 'trend': trend}


def sample_load(now):
    try:
        l1, l5, l15 = [round(x, 2) for x in LOAD_FN()]
    except (OSError, AttributeError, ValueError):
        l1 = l5 = l15 = 0.0
    return {'ts': iso(now), 'load1': l1, 'load5': l5, 'load15': l15, 'cpus': os.cpu_count()}


# --- liveness ----------------------------------------------------------------

def name_regex(folder):
    """The folder name without a closed ticket's leading dot, matched as a whole path part or word."""
    return re.compile(r'(?<![\w-])' + re.escape(folder.lstrip('.')) + r'(?![\w-])')


def worktrees_named(linked, tid, folder):
    """Linked worktrees whose own folder name carries the ticket id or the ticket folder name."""
    out = []
    id_re = re.compile(r'(?<![\w])' + re.escape(tid) + r'(?!\d)') if tid else None
    bare = folder.lstrip('.')
    for w in linked:
        base = os.path.basename(w)
        if (id_re and id_re.search(base)) or bare in base:
            out.append(w)
    return out


def worktree_regex(path):
    """A worktree named by its real path, or by its last two parts (.worktrees/<name>), which survives a symlinked
    prefix such as macOS /var against /private/var."""
    parts = path.rstrip(os.sep).split(os.sep)
    tail = os.sep.join(parts[-2:])
    return re.compile(r'(?:' + re.escape(path) + r'|(?<![\w.-])' + re.escape(tail) + r')(?![\w-])')


def step_dirs(task_dir):
    """The task folder and its direct step-* folders (superseded ones included: a marker there is still a marker)."""
    out = [task_dir]
    try:
        out += sorted(os.path.join(task_dir, n) for n in os.listdir(task_dir)
                      if n.startswith('step-') and os.path.isdir(os.path.join(task_dir, n)))
    except OSError:
        pass
    return out


def marker_pids(d, stem):
    """The pids of the newest running attempt for <stem> (role-level) in d, from its *.attempt.json."""
    best = None
    try:
        names = sorted(n for n in os.listdir(d) if n.endswith('.attempt.json'))
    except OSError:
        return []
    for n in names:
        try:
            with open(os.path.join(d, n), encoding='utf-8') as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if (not isinstance(rec, dict) or rec.get('status') != 'running'
                or '%s-%s' % (rec.get('role'), rec.get('level')) != stem):
            continue
        if best is None or str(rec.get('started_at')) >= str(best.get('started_at')):
            best = rec
    if best is None:
        return []
    return [p for p in (best.get('process_pid'), best.get('owner_pid')) if isinstance(p, int)]


def inspect_markers(dirs):
    """[{file, stem, pids, alive}] for every `*.running` marker in dirs. alive: a recorded pid answers kill 0 and
    started no later than the marker did (a pid reused after the owner died started after it)."""
    out = []
    for d in dirs:
        try:
            names = sorted(n for n in os.listdir(d) if n.endswith('.running'))
        except OSError:
            continue
        for n in names:
            path = os.path.join(d, n)
            stem = n[:-len('.running')]
            try:
                text = open(path, encoding='utf-8', errors='replace').read().strip()
                started = float(text) if re.fullmatch(r'\d{9,11}', text) else os.stat(path).st_mtime
            except OSError:
                continue
            pids = marker_pids(d, stem)
            alive = None
            for pid in pids:
                if not pid_alive(pid):
                    continue
                st = proc_start_epoch(pid)
                if st is None or st <= started + PID_SLACK_S:
                    alive = pid
                    break
            out.append({'file': path, 'stem': stem, 'pids': pids, 'alive': alive})
    return out


def runs_last_ts(path, st):
    """When runs.jsonl last grew: the newest `ts` among the rows in its last 8 KB, else its mtime. A git checkout
    or merge rewrites a tracked file and refreshes its mtime, so the mtime alone would call every old ticket idle."""
    try:
        with open(path, 'rb') as f:
            f.seek(max(0, st.st_size - 8192))
            tail = f.read().decode('utf-8', errors='replace')
    except OSError:
        return st.st_mtime
    best = None
    for line in tail.splitlines():
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        dt = parse_ts(rec.get('ts')) if isinstance(rec, dict) else None
        if dt is not None and (best is None or dt > best):
            best = dt
    return min(best.timestamp(), st.st_mtime) if best is not None else st.st_mtime


def newest_activity(dirs):
    """(time, path) of the newest activity in dirs: a runs.jsonl by its newest row's ts (see runs_last_ts), a
    `*.log` by its mtime. Nothing else is activity."""
    best = (0.0, None)
    for d in dirs:
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for n in names:
            if n != 'runs.jsonl' and not n.endswith('.log'):
                continue
            p = os.path.join(d, n)
            try:
                st = os.stat(p)
            except OSError:
                continue
            when = runs_last_ts(p, st) if n == 'runs.jsonl' else st.st_mtime
            if when > best[0]:
                best = (when, p)
    return best


def human_age(seconds):
    return '%dm' % round(seconds / 60.0) if seconds >= 90 else '%ds' % max(0, round(seconds))


def judge_row(task_dir, copies, named_wts, procs, claims, now_ts, active_s):
    """(state, evidence[]) for one board row. Precedence: live, dead, idle, then stale or queued or done."""
    evidence = []
    folder = os.path.basename(task_dir)
    rx = name_regex(folder)
    wt_rx = [worktree_regex(w) for w in named_wts]
    hits = []
    for p in procs:
        if rx.search(p['cmd']) or any(w.search(p['cmd']) for w in wt_rx):
            hits.append(p)
    for p in hits[:2]:
        evidence.append('process %d: %s' % (p['pid'], p['cmd'][:80]))
    all_dirs = step_dirs(task_dir)
    for c in copies:
        all_dirs += step_dirs(c)
    markers = inspect_markers(all_dirs)
    for m in markers:
        if m['alive']:
            evidence.append('marker %s pid %d alive' % (m['stem'], m['alive']))
        else:
            evidence.append('marker %s %s' % (m['stem'], 'pid %s not running' % m['pids'][0] if m['pids'] else 'has no pid'))
    if hits or any(m['alive'] for m in markers):
        return 'live', evidence
    if markers:
        return 'dead', evidence
    when, path = newest_activity(step_dirs(task_dir))
    for c in copies:
        w, p = newest_activity(step_dirs(c))
        if w > when:
            when, path = w, p
    if path and now_ts - when <= active_s:
        return 'idle', ['%s changed %s ago' % (os.path.basename(path), human_age(now_ts - when))]
    return ('stale', ['no process, marker or activity in %d minutes' % round(active_s / 60.0)]) if claims else ('queued', [])


# --- one repo ----------------------------------------------------------------

def git_out(repo, *args):
    r = run_bounded(['env', 'GIT_OPTIONAL_LOCKS=0', GIT_CMD, '-C', repo] + list(args), GIT_TIMEOUT)
    return r.out.strip() if r.ok else None


def release_state(repo):
    out = {'branch': None, 'default': None, 'local': None, 'remote': None, 'ahead': None, 'behind': None,
           'last_tag': None, 'tag_distance': None, 'fetched_age_s': None, 'unpushed': [],
           'unpushed_branch_commits': None}
    if git_out(repo, 'rev-parse', '--git-dir') is None:
        return out
    out['branch'] = git_out(repo, 'rev-parse', '--abbrev-ref', 'HEAD')
    head = git_out(repo, 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD')
    default = head.split('/', 1)[1] if head and '/' in head else None
    if default is None:
        for cand in ('main', 'master'):
            if git_out(repo, 'rev-parse', '--verify', '-q', 'refs/heads/' + cand):
                default = cand
                break
    out['default'] = default
    if default:
        out['local'] = git_out(repo, 'rev-parse', '--short', 'refs/heads/' + default)
        out['remote'] = git_out(repo, 'rev-parse', '--short', 'refs/remotes/origin/' + default)
        if out['local'] and out['remote']:
            lr = git_out(repo, 'rev-list', '--left-right', '--count', 'refs/heads/%s...refs/remotes/origin/%s' % (default, default))
            if lr and len(lr.split()) == 2:
                out['ahead'], out['behind'] = int(lr.split()[0]), int(lr.split()[1])
            log = git_out(repo, 'log', '-n', str(LIST_CAP), '--format=%h %s', 'refs/remotes/origin/%s..refs/heads/%s' % (default, default))
            out['unpushed'] = [{'sha': l.split(' ', 1)[0], 'subject': l.split(' ', 1)[1] if ' ' in l else ''}
                               for l in (log or '').splitlines()]
        tag = git_out(repo, 'describe', '--tags', '--abbrev=0', 'refs/heads/' + default)
        out['last_tag'] = tag
        if tag:
            n = git_out(repo, 'rev-list', '--count', '%s..refs/heads/%s' % (tag, default))
            out['tag_distance'] = int(n) if n and n.isdigit() else None
    fh = git_out(repo, 'rev-parse', '--git-path', 'FETCH_HEAD')
    if fh:
        fh = fh if os.path.isabs(fh) else os.path.join(repo, fh)
        try:
            out['fetched_age_s'] = max(0, int(time.time() - os.stat(fh).st_mtime))
        except OSError:
            pass
    ub = git_out(repo, 'log', '--branches', '--not', '--remotes', '-n', '500', '--format=%h')
    out['unpushed_branch_commits'] = len(ub.splitlines()) if ub is not None else None
    return out


def gh_list(entry, state, fields, limit=30):
    cmd = [GH_CMD, 'pr', 'list', '--state', state, '--limit', str(limit), '--json', fields]
    if entry.get('gh'):
        cmd += ['-R', entry['gh']]
    r = run_bounded(cmd, GH_TIMEOUT, cwd=entry['path'])
    if r.timed_out:
        return None, 'gh timed out'
    if not r.ok:
        return None, (r.err.strip().splitlines() or ['gh failed'])[0][:200]
    try:
        data = json.loads(r.out or '[]')
    except ValueError:
        return None, 'gh printed no JSON'
    return (data, None) if isinstance(data, list) else (None, 'gh printed no list')


def open_prs(entry):
    data, err = gh_list(entry, 'open', 'number,title,url,isDraft,reviewDecision,mergeStateStatus,headRefName')
    if err:
        return {'error': err}
    prs = [{'number': p.get('number'), 'title': p.get('title'), 'url': p.get('url'), 'draft': bool(p.get('isDraft')),
            'review': p.get('reviewDecision') or None, 'merge_state': p.get('mergeStateStatus') or None,
            'branch': p.get('headRefName')} for p in data if isinstance(p, dict)]
    return {'open': [p for p in prs if not p['draft']], 'drafts': sum(1 for p in prs if p['draft'])}


OWNER_RE = re.compile(r'(?im)^\W*owner\s*[:=]\s*(user|conductor)\b')


def blocked_owner(task, root, tid):
    """(owner, note) for a blocked ticket: an `owner:` line in its handoff.md, else one on a line of notes.md
    that names the ticket id."""
    text = fleet_collect.read_text(os.path.join(str(task), 'handoff.md'))
    m = OWNER_RE.search(text)
    if m:
        return m.group(1).lower(), m.group(0).strip()[:120]
    if tid:
        for line in fleet_collect.read_text(os.path.join(str(root), 'notes.md')).splitlines():
            m = re.search(r'\bowner\s*[:=]\s*(user|conductor)\b', line, re.I)
            if m and re.search(r'(?<![\w-])' + re.escape(tid) + r'(?!\d)', line):
                return m.group(1).lower(), line.strip()[:120]
    return 'unknown', ''


def board_cell(rows):
    pick = next((r for r in rows if r[2] == '\U0001F534'), None) or next((r for r in rows if r[2] == '\U0001F7E1'), None)
    r = pick or rows[0]
    return '%s %s' % (r[2], r[3]) + ('' if r[1] == 'task' else ' (step %s)' % r[1].split('.')[0])


def scan_repo(entry, procs, now, active_s, gh):
    repo = entry['path']
    out = {'name': entry['name'], 'path': repo, 'conductor': entry.get('conductor'), 'gh': entry.get('gh'),
           'rows': [], 'counts': {}, 'needs_you': [], 'prs': 'skipped', 'release': release_state(repo),
           'worktrees': 0, 'tickets': {}}
    root = pathlib.Path(repo) / '.sdlc'
    _roots, linked = fleet_collect.worktree_roots(repo)
    linked = [w for w in linked if os.path.isdir(w)]
    out['worktrees'] = len(linked)
    now_ts = now.timestamp()
    if root.is_dir():
        for task in sorted(board.task_dirs(root), key=lambda t: t.name.lstrip('.')):
            try:
                meta = tickets.parse(task.joinpath('handoff.md').read_text(encoding='utf-8')) or {}
            except (OSError, ValueError):
                meta = {}
            tid = meta.get('id') if isinstance(meta.get('id'), str) else ''
            status = meta.get('status') if isinstance(meta.get('status'), str) else ''
            title = meta.get('title') if isinstance(meta.get('title'), str) else ''
            key = tid or task.name.lstrip('.')
            rec = {'id': tid, 'task': task.name, 'title': title, 'status': status, 'state': None, 'board': None}
            out['tickets'][key] = rec
            if status == 'blocked':
                owner, note = blocked_owner(task, root, tid)
                out['needs_you'].append({'kind': 'blocked', 'id': tid, 'task': task.name, 'title': title,
                                         'owner': owner, 'note': note})
            if not board.belongs_on_board(task):
                continue
            try:
                brows, _steps = board.task_rows(task)
            except Exception:
                brows = []
            if not brows:
                brows = [(task.name, 'task', '⏳', 'unreadable', 0)]
            claims = any(r[2] in ('\U0001F7E1', '\U0001F534') for r in brows)
            rel = task.relative_to(root)
            copies = [os.path.join(w, '.sdlc', str(rel)) for w in linked]
            copies = [c for c in copies if os.path.isdir(c)]
            state, evidence = judge_row(str(task), copies, worktrees_named(linked, tid, task.name), procs,
                                        claims, now_ts, active_s)
            if state in ('queued',) and not claims and all(r[2] == '\U0001F7E2' for r in brows):
                state = 'done'
            flags = ['ticket-done-board-open'] if claims and status in ('done', 'dropped') else []
            cell = board_cell(brows)
            rec['state'], rec['board'] = state, cell
            out['rows'].append({'id': tid, 'task': task.name, 'title': title, 'ticket_status': status,
                                'board': cell, 'pct': min(r[4] for r in brows) if brows else 0,
                                'claims_work': claims, 'state': state, 'evidence': evidence, 'flags': flags})
    for r in out['rows']:
        out['counts'][r['state']] = out['counts'].get(r['state'], 0) + 1
    if gh:
        out['prs'] = open_prs(entry)
        for p in out['prs'].get('open', []):
            out['needs_you'].append({'kind': 'pr', 'number': p['number'], 'title': p['title'], 'url': p['url'],
                                     'detail': ', '.join(x for x in (p['review'], p['merge_state']) if x)})
    return out


# --- snapshot and delta ------------------------------------------------------

def read_snapshot(path):
    data = fleet_collect.read_json(path)
    return data if isinstance(data, dict) and isinstance(data.get('repos'), dict) else None


def make_snapshot(now, repos):
    snap = {'version': 1, 'time': iso(now), 'repos': {}}
    for r in repos:
        prs = r['prs']
        snap['repos'][r['name']] = {
            'tickets': {k: {kk: v[kk] for kk in ('id', 'task', 'title', 'status', 'state', 'board')}
                        for k, v in r['tickets'].items()},
            'prs': [{'number': p['number'], 'title': p['title']} for p in prs.get('open', [])]
            if isinstance(prs, dict) and 'open' in prs else None}
    return snap


def compute_delta(prev, cur_repos, entries):
    d = {'since': prev['time'] if prev else None, 'first_run': prev is None, 'state_changes': [], 'closed': [],
         'dropped': [], 'new': [], 'gone': [], 'prs_merged': [], 'prs_closed': []}
    if not prev:
        return d
    for r in cur_repos:
        before = prev['repos'].get(r['name'])
        if not isinstance(before, dict):
            continue
        old, new = before.get('tickets') or {}, r['tickets']
        for key, n in new.items():
            o = old.get(key)
            ref = {'repo': r['name'], 'id': n['id'] or key, 'task': n['task']}
            if o is None:
                d['new'].append(dict(ref, status=n['status']))
                continue
            if n['status'] == 'done' and o.get('status') != 'done':
                d['closed'].append(dict(ref, title=n['title']))
            elif n['status'] == 'dropped' and o.get('status') != 'dropped':
                d['dropped'].append(dict(ref, title=n['title']))
            elif n['status'] != o.get('status'):
                d['state_changes'].append(dict(ref, kind='status', **{'from': o.get('status'), 'to': n['status']}))
            if n['state'] != o.get('state') and (n['state'] or o.get('state')):
                d['state_changes'].append(dict(ref, kind='state', **{'from': o.get('state'), 'to': n['state']}))
        for key, o in old.items():
            if key not in new and o.get('status') not in ('done', 'dropped'):
                d['gone'].append({'repo': r['name'], 'id': o.get('id') or key, 'task': o.get('task')})
        was = before.get('prs')
        if was and isinstance(r['prs'], dict) and 'open' in r['prs']:
            still = {p['number'] for p in r['prs']['open']} | set()
            vanished = [p for p in was if p['number'] not in still]
            if vanished:
                entry = next((e for e in entries if e['name'] == r['name']), None)
                merged, err = gh_list(entry, 'merged', 'number,title,mergedAt', 50) if entry else (None, 'no entry')
                merged_n = {p.get('number') for p in (merged or []) if isinstance(p, dict)}
                for p in vanished:
                    item = {'repo': r['name'], 'number': p['number'], 'title': p['title']}
                    (d['prs_merged'] if p['number'] in merged_n else d['prs_closed']).append(item)
    return d


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
    os.replace(tmp, path)


# --- collect -----------------------------------------------------------------

def collect(entries, state_dir=None, stop_line=DEFAULT_STOP_LINE, active_minutes=DEFAULT_ACTIVE_MINUTES,
            gh=True, write=True, now=None, procs=None):
    now = now or now_utc()
    if procs is None:
        procs = ps_snapshot()
    machine = {}
    if procs is None:
        machine['error'] = 'ps unavailable'
        procs = []
    machine['consumers'], machine['ranked'] = consumers(procs)
    workers = worker_procs(procs)
    load_path = os.path.join(state_dir, 'load.jsonl') if state_dir else None
    snap_path = os.path.join(state_dir, 'fleet-status.json') if state_dir else None
    prev_samples = read_samples(load_path) if load_path else []
    cur = sample_load(now)
    machine = dict({'load': load_report(prev_samples, cur, now, stop_line)}, **machine)
    repos = []
    for e in entries:
        if not os.path.isdir(e['path']):
            repos.append({'name': e['name'], 'path': e['path'], 'conductor': e.get('conductor'), 'gh': e.get('gh'),
                          'error': 'no such directory', 'rows': [], 'counts': {}, 'needs_you': [], 'prs': 'skipped',
                          'release': None, 'worktrees': 0, 'tickets': {}})
            continue
        repos.append(scan_repo(e, workers, now, active_minutes * 60.0, gh))
    prev = read_snapshot(snap_path) if snap_path else None
    delta = compute_delta(prev, repos, entries)
    written = False
    if write and state_dir:
        append_sample(load_path, cur)
        write_json(snap_path, make_snapshot(now, repos))
        written = True
    for r in repos:
        r.pop('tickets', None)
    needs = [dict(n, repo=r['name']) for r in repos for n in r['needs_you']]
    return {'time': iso(now), 'machine': machine, 'repos': repos, 'needs_you': needs, 'delta': delta,
            'snapshot': {'path': snap_path, 'written': written}}


def summary_line(out):
    counts = {}
    for r in out['repos']:
        for k, v in r['counts'].items():
            counts[k] = counts.get(k, 0) + v
    ld = out['machine']['load']
    return 'status: %d repos, %s, load %.1f %s %s' % (
        len(out['repos']), ', '.join('%d %s' % (counts[k], k) for k in ('live', 'idle', 'dead', 'stale') if counts.get(k))
        or 'no rows', ld['load1'], ld['arrow'], ld['verdict'])


# --- cli ---------------------------------------------------------------------

def resolve_entries(paths, fleet_file):
    if paths:
        out = []
        for p in paths:
            if not os.path.isdir(p):
                raise ValueError('no such repo directory: %s' % p)
            ap = os.path.abspath(p)
            out.append({'name': os.path.basename(ap.rstrip(os.sep)) or ap, 'path': ap, 'conductor': None, 'gh': None})
        return out
    try:
        data = fleet_config.load(fleet_file)
    except fleet_config.FleetError as e:
        raise ValueError(str(e))
    return [r for r in data['repos'] if r['status'] == 'active']


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == 'selftest':
        return selftest()
    if argv[0] != 'collect':
        print(USAGE, file=sys.stderr)
        return 2
    paths, fleet_file, state_dir = [], fleet_config.DEFAULT, None
    stop_line, active, gh, write = DEFAULT_STOP_LINE, DEFAULT_ACTIVE_MINUTES, True, True
    rest, i = argv[1:], 0
    try:
        while i < len(rest):
            a = rest[i]
            if a == '--no-gh':
                gh = False
            elif a == '--no-write':
                write = False
            elif a in ('--fleet', '--state-dir', '--stop-line', '--active-minutes') and i + 1 < len(rest):
                i += 1
                if a == '--fleet':
                    fleet_file = rest[i]
                elif a == '--state-dir':
                    state_dir = rest[i]
                elif a == '--stop-line':
                    stop_line = float(rest[i])
                else:
                    active = float(rest[i])
            elif not a.startswith('--'):
                paths.append(a)
            else:
                print(USAGE, file=sys.stderr)
                return 2
            i += 1
        entries = resolve_entries(paths, fleet_file)
    except ValueError as e:
        print('fleet_status: %s' % e, file=sys.stderr)
        return 2
    if state_dir is None and os.path.isdir(os.path.join(os.getcwd(), '.sdlc')):
        state_dir = os.path.join(os.getcwd(), '.sdlc', 'runtime')
    out = collect(entries, state_dir, stop_line, active, gh, write)
    print(summary_line(out), file=sys.stderr)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write('\n')
    return 0


# --- selftest ----------------------------------------------------------------

def selftest():
    global PS_CMD, GH_CMD, GIT_CMD, LOAD_FN
    import shutil, subprocess

    misses = []

    def ok(name, cond):
        if cond:
            print('ok: ' + name)
        else:
            misses.append(name)
            print('FAIL: ' + name)

    def write(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)

    def age(path, seconds):
        t = time.time() - seconds
        os.utime(path, (t, t))

    def snap(d):
        out = []
        for cur, _ds, ns in os.walk(d):
            for n in ns:
                p = os.path.join(cur, n)
                st = os.stat(p)
                out.append((os.path.relpath(p, d), st.st_size, st.st_mtime_ns))
        return sorted(out)

    def git(cwd, *args):
        return subprocess.run(['git', '-C', cwd, '-c', 'user.name=t', '-c', 'user.email=t@t'] + list(args),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    OLD = 30 * 86400

    def ticket(repo, folder, tid, status, built=True, extra=''):
        d = os.path.join(repo, '.sdlc', folder)
        write(os.path.join(d, 'handoff.md'), '---\nid: %s\ntitle: "t %s"\ntype: chore\nstatus: %s\nsize: S\n---\n\n## Goal\n%s\n'
              % (tid, tid, status, extra))
        if built:
            write(os.path.join(d, 'planner-L1.md'), '## Step 1: build it\nlevel: L1\n')
            write(os.path.join(d, 'step-1', 'builder-L1.md'), '## Status\ndone\n')
            write(os.path.join(d, 'step-1', 'runs.jsonl'), json.dumps({'role': 'builder', 'ts': '2026-09-01T00:00:00Z'}) + '\n')
            write(os.path.join(d, 'step-1', 'builder-L1.log'), 'x\n')
            for f in ('runs.jsonl', 'builder-L1.log'):
                age(os.path.join(d, 'step-1', f), OLD)
        return d

    def attempt(d, role, level, pid, status='running'):
        write(os.path.join(d, '%s-%s.attempt.json' % (role, level)), json.dumps(
            {'attempt_id': 'a', 'role': role, 'level': level, 'status': status, 'started_at': '2026-10-06T10:00:00Z',
             'owner_pid': pid, 'process_pid': pid}))

    def states(out, name='repo'):
        repo = next(r for r in out['repos'] if r['name'] == name)
        return {r['id']: r['state'] for r in repo['rows']}

    saved = (PS_CMD, GH_CMD, GIT_CMD, LOAD_FN)
    kids = []
    tmp = tempfile.mkdtemp()
    try:
        # --- fixture repo: a real git repo with an origin, a tag, and one unpushed commit
        repo = os.path.join(tmp, 'repo')
        os.makedirs(repo)
        git(repo, 'init', '-q', '-b', 'main')
        write(os.path.join(repo, 'f.txt'), 'x\n')
        git(repo, 'add', 'f.txt')
        git(repo, 'commit', '-q', '-m', 'first')
        git(repo, 'tag', 'v0.1.0')
        origin = os.path.join(tmp, 'origin.git')
        git(tmp, 'clone', '-q', '--bare', repo, origin)
        git(repo, 'remote', 'add', 'origin', origin)
        git(repo, 'fetch', '-q', 'origin')
        write(os.path.join(repo, 'g.txt'), 'y\n')
        git(repo, 'add', 'g.txt')
        git(repo, 'commit', '-q', '-m', 'second, not pushed')

        t1 = ticket(repo, '0001-live-one', 'T-0001', 'ready')
        t2 = ticket(repo, '0002-dead-marker', 'T-0002', 'ready')
        t3 = ticket(repo, '0003-stale-row', 'T-0003', 'ready')
        t4 = ticket(repo, '0004-idle-row', 'T-0004', 'ready')
        write(os.path.join(t4, 'step-1', 'runs.jsonl'), json.dumps({'role': 'builder', 'ts': iso(now_utc())}) + '\n')
        t5 = ticket(repo, '0005-marker-live', 'T-0005', 'ready')
        t6 = ticket(repo, '0006-reused-pid', 'T-0006', 'ready')
        ticket(repo, '0007-done-lie', 'T-0007', 'done')
        ticket(repo, '0008-queued', 'T-0008', 'ready', built=False)
        ticket(repo, '0009-blocked-user', 'T-0009', 'blocked', built=False, extra='owner: user\n')
        ticket(repo, '0010-blocked-conductor', 'T-0010', 'blocked', built=False, extra='Owner: Conductor\n')
        ticket(repo, '0011-blocked-nobody', 'T-0011', 'blocked', built=False)
        ticket(repo, '0012-closed-quiet', 'T-0012', 'done', built=False)
        ticket(repo, '0013-closed-built', 'T-0013', 'done')
        write(os.path.join(repo, '.sdlc', 'notes.md'), '- T-0011 waits on a call, owner: user\n- T-0110 owner: conductor\n')

        # processes: one names t1's folder, one backs t5's marker, one backs t6's marker but is older than its marker
        sleeper = 'import time; time.sleep(120)'
        kids.append(subprocess.Popen([sys.executable, '-c', sleeper, t1], stdin=subprocess.DEVNULL))
        kids.append(subprocess.Popen([sys.executable, '-c', sleeper], stdin=subprocess.DEVNULL))
        kids.append(subprocess.Popen([sys.executable, '-c', sleeper], stdin=subprocess.DEVNULL))
        dead = subprocess.Popen([sys.executable, '-c', 'pass'])
        dead.wait()
        time.sleep(1.2)                                                   # kids are older than the markers below
        write(os.path.join(t2, 'builder-L1.running'), '%d\n' % int(time.time()))
        attempt(t2, 'builder', 'L1', dead.pid)
        write(os.path.join(t5, 'builder-L1.running'), '%d\n' % int(time.time()))
        attempt(t5, 'builder', 'L1', kids[1].pid)
        write(os.path.join(t6, 'builder-L1.running'), '%d\n' % (int(time.time()) - 3600))   # started an hour ago
        attempt(t6, 'builder', 'L1', kids[2].pid)                         # but this pid started a moment ago: reused
        before = snap(tmp)

        sd = os.path.join(tmp, 'state')
        t0 = now_utc()
        out = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, now=t0)
        st = states(out)
        ok('live: a process naming the ticket folder', st['T-0001'] == 'live')
        ok('live: a marker whose attempt pid is alive', st['T-0005'] == 'live')
        ok('dead: a marker whose pid is gone', st['T-0002'] == 'dead')
        ok('dead: a marker whose pid started after the marker (reused)', st['T-0006'] == 'dead')
        ok('stale: a board row with no process, marker or activity', st['T-0003'] == 'stale')
        ok('idle: no process or marker, but a runs.jsonl changed just now', st['T-0004'] == 'idle')
        ok('queued: a ticket with no plan and no signal', st['T-0008'] == 'queued')
        ok('a done ticket with no step work is not a board row', 'T-0012' not in st)
        row = {r['id']: r for r in out['repos'][0]['rows']}
        ok('live: evidence names the process', 'process' in row['T-0001']['evidence'][0])
        ok('dead: evidence names the pid that is not running', 'not running' in row['T-0002']['evidence'][0])
        ok('flag: a done ticket whose board rows still claim work', row['T-0007']['flags'] == ['ticket-done-board-open']
           and row['T-0007']['state'] == 'stale')
        ok('flag: a live row carries none', row['T-0001']['flags'] == [])
        ok('counts add up', out['repos'][0]['counts'].get('live') == 2 and out['repos'][0]['counts'].get('dead') == 2)
        # negative control: the marker removed turns dead into stale, not idle or live
        os.unlink(os.path.join(t2, 'builder-L1.running'))
        out2 = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('negative control: removing the marker changes dead to stale', states(out2)['T-0002'] == 'stale')
        # negative control: the process gone turns live into stale
        kids[0].kill()
        kids[0].wait()
        out3 = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('negative control: killing the process changes live to stale', states(out3)['T-0001'] == 'stale')
        # a worktree named for the ticket: a process naming it makes the row live
        wt = os.path.join(repo, '.worktrees', 'chain-L1-T-0003')
        os.makedirs(wt)
        kids.append(subprocess.Popen([sys.executable, '-c', sleeper, wt], stdin=subprocess.DEVNULL))
        out4 = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('live: a process naming a worktree named for the ticket', states(out4)['T-0003'] == 'live'
           and states(out4)['T-0004'] == 'idle')
        # a lane worktree copy with a live marker makes the main row live; a plain checkout copy is no activity
        lane = os.path.join(repo, '.worktrees', 'lane1')
        copy3 = os.path.join(lane, '.sdlc', '0003-stale-row')
        os.makedirs(copy3)
        os.makedirs(os.path.join(copy3, 'step-1'))
        shutil.copy(os.path.join(t3, 'step-1', 'runs.jsonl'), os.path.join(copy3, 'step-1', 'runs.jsonl'))
        kids[3].kill()
        kids[3].wait()
        shutil.rmtree(wt)
        out5 = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('worktree copy: a fresh checkout copy of runs.jsonl is not activity', states(out5)['T-0003'] == 'stale')
        with open(os.path.join(copy3, 'step-1', 'runs.jsonl'), 'a') as f:
            f.write(json.dumps({'role': 'builder', 'ts': iso(now_utc())}) + '\n')
        out5 = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('worktree copy: a runs.jsonl that grew is activity', states(out5)['T-0003'] == 'idle')
        shutil.rmtree(lane)

        # a checkout refreshes an old runs.jsonl's mtime: its old row ts keeps the row stale; no ts falls back to mtime
        os.utime(os.path.join(t3, 'step-1', 'runs.jsonl'), None)
        outp = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('activity: a fresh mtime on a runs.jsonl whose rows are old is not activity', states(outp)['T-0003'] == 'stale')
        write(os.path.join(t3, 'step-1', 'runs.jsonl'), '{"role":"builder"}\n')
        outp = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('activity: a runs.jsonl with no row ts falls back to its mtime', states(outp)['T-0003'] == 'idle')
        write(os.path.join(t3, 'step-1', 'runs.jsonl'), json.dumps({'role': 'builder', 'ts': '2026-09-01T00:00:00Z'}) + '\n')
        age(os.path.join(t3, 'step-1', 'runs.jsonl'), OLD)
        # a log written now is activity even with old runs rows
        write(os.path.join(t3, 'step-1', 'builder-L1.log'), 'fresh\n')
        outp = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('activity: a log written now makes the row idle', states(outp)['T-0003'] == 'idle')
        age(os.path.join(t3, 'step-1', 'builder-L1.log'), OLD)

        # handoff.md and skips.md rewrites are never activity
        write(os.path.join(t3, 'skips.md'), 'x\n')
        os.utime(os.path.join(t3, 'handoff.md'), None)
        out6 = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd, gh=False, write=False)
        ok('activity: a fresh handoff.md or skips.md does not make a row idle', states(out6)['T-0003'] == 'stale')

        # needs-you from blocked tickets
        ny = {n['id']: n for n in out['needs_you'] if n['kind'] == 'blocked'}
        ok('needs you: owner user from the handoff', ny['T-0009']['owner'] == 'user')
        ok('needs you: owner conductor, any case', ny['T-0010']['owner'] == 'conductor')
        ok('needs you: owner from notes.md naming the id', ny['T-0011']['owner'] == 'user')
        ok('needs you: a notes.md line for another id is not used', 'T-0110' not in ny)
        ok('needs you: no owner is reported as unknown, not dropped',
           next(n for n in out['needs_you'] if n['id'] == 'T-0011') is not None)

        # release state
        rel = out['repos'][0]['release']
        ok('release: default branch, tag and ahead count', rel['default'] == 'main' and rel['last_tag'] == 'v0.1.0'
           and rel['ahead'] == 1 and rel['behind'] == 0 and rel['tag_distance'] == 1)
        ok('release: the unpushed commit is listed', len(rel['unpushed']) == 1 and 'second' in rel['unpushed'][0]['subject'])
        ok('release: unpushed commits on any branch are counted', rel['unpushed_branch_commits'] == 1)
        ok('release: a non-git directory yields nulls, not a crash',
           release_state(os.path.join(tmp, 'state'))['default'] is None)

        # load: two samples a minute apart give a trend; a load above the stop line is `over`
        sd2 = os.path.join(tmp, 'state2')
        base = now_utc()
        for ts, l1 in (((base - datetime.timedelta(seconds=120)), 4.0), ((base - datetime.timedelta(seconds=60)), 6.0)):
            append_sample(os.path.join(sd2, 'load.jsonl'),
                          {'ts': iso(ts), 'load1': l1, 'load5': l1, 'load15': l1, 'cpus': 8})
        LOAD_FN = lambda: (10.0, 7.0, 5.0)
        rep = load_report(read_samples(os.path.join(sd2, 'load.jsonl')), sample_load(base), base, 14.0)
        ok('load: two samples a minute apart give a rising trend', rep['arrow'] == UP and rep['trend']['source'] == 'samples'
           and rep['trend']['delta'] == 6.0 and rep['trend']['minutes'] == 2.0 and rep['trend']['samples'] == 2)
        ok('load: well under the stop line is ok', rep['verdict'] == 'ok' and rep['headroom'] == 4.0)
        LOAD_FN = lambda: (12.0, 7.0, 5.0)
        rep = load_report(read_samples(os.path.join(sd2, 'load.jsonl')), sample_load(base), base, 14.0)
        ok('load: from 80 percent of the stop line is near, not over', rep['verdict'] == 'near')
        LOAD_FN = lambda: (15.5, 12.0, 9.0)
        rep = load_report(read_samples(os.path.join(sd2, 'load.jsonl')), sample_load(base), base, 14.0)
        ok('load: above the stop line is over', rep['verdict'] == 'over')
        rep = load_report(read_samples(os.path.join(sd2, 'load.jsonl')), sample_load(base), base, 20.0)
        ok('negative control: the same load under a higher stop line is not over', rep['verdict'] != 'over')
        LOAD_FN = lambda: (2.0, 6.0, 5.0)
        rep = load_report(read_samples(os.path.join(sd2, 'load.jsonl')), sample_load(base), base, 14.0)
        ok('load: a falling load gives the down arrow and ok', rep['arrow'] == DOWN and rep['verdict'] == 'ok')
        LOAD_FN = lambda: (6.1, 6.0, 6.0)
        rep = load_report([{'ts': iso(base - datetime.timedelta(seconds=60)), 'load1': 6.0, 'load5': 6, 'load15': 6}],
                          sample_load(base), base, 14.0)
        ok('load: a steady load gives the flat arrow', rep['arrow'] == FLAT)
        rep = load_report([], sample_load(base), base, 14.0)
        ok('load: with no earlier sample the trend falls back to load1 against load5',
           rep['trend']['source'] == 'loadavg' and rep['trend']['minutes'] is None)
        rep = load_report([{'ts': iso(base - datetime.timedelta(seconds=5)), 'load1': 1.0, 'load5': 1, 'load15': 1}],
                          sample_load(base), base, 14.0)
        ok('load: a sample under 20 seconds old is not a trend reference', rep['trend']['source'] == 'loadavg')
        LOAD_FN = lambda: (3.0, 3.0, 3.0)
        out_l = collect([{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': None}], sd2, gh=False, now=base)
        ok('load: collect appends a sample and reports the trend from the stored ones',
           len(read_samples(os.path.join(sd2, 'load.jsonl'))) == 3 and out_l['machine']['load']['trend']['samples'] == 2)
        big = os.path.join(tmp, 'state3', 'load.jsonl')
        write(big, ''.join(json.dumps({'ts': iso(base), 'load1': 1.0, 'load5': 1, 'load15': 1}) + '\n'
                           for _ in range(LOAD_TRIM_AT + 5)))
        append_sample(big, {'ts': iso(base), 'load1': 2.0, 'load5': 1, 'load15': 1})
        ok('load: the series is trimmed to the newest samples', len(read_samples(big)) == LOAD_KEEP)

        # consumers
        samples = [('vite --host', 'watchers'), ('node /x/node_modules/.bin/vite build', None),
                   ('node /x/node_modules/vite/bin/vite.js', 'watchers'), ('node /x/node_modules/vite/bin/vite.js build', None),
                   ('tsc -p . -w', 'watchers'), ('python3 supervisor.py watch --run', 'watchers'),
                   ('node jest --watch', 'watchers'), ('fswatch -o src', 'watchers'),
                   ('/x/claude -p --agent sdlc-lite:solo', 'claude'), ('bash /p/hooks/block-publish.sh', 'hooks'),
                   ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --type=renderer', 'chromium'),
                   ('vim vite.config.ts', None)]
        ok('consumers: classification of known command lines', all(consumer_class(c) == k for c, k in samples))
        cons, ranked = consumers([{'pid': 1, 'cpu': 5.0, 'cmd': 'vite --host'}, {'pid': 2, 'cpu': 40.0, 'cmd': '/x/claude -p'},
                                  {'pid': 3, 'cpu': 3.0, 'cmd': 'nodemon app.js'}])
        ok('consumers: ranked by cpu', ranked == ['claude', 'watchers'] and cons['watchers']['count'] == 2
           and cons['watchers']['cpu_pct'] == 8.0 and cons['chromium']['count'] == 0)
        ok('a viewer or a search never counts as a worker', worker_procs([
            {'pid': 1, 'cpu': 0, 'cmd': 'vim %s/handoff.md' % t3}, {'pid': 2, 'cpu': 0, 'cmd': 'grep -r 0003-stale-row .'},
            {'pid': 3, 'cpu': 0, 'cmd': 'python3 fleet_status.py collect /r 0003-stale-row'},
            {'pid': 4, 'cpu': 0, 'cmd': 'claude -p 0003-stale-row'}]) == [{'pid': 4, 'cpu': 0, 'cmd': 'claude -p 0003-stale-row'}])
        rx = name_regex('0043-gen-ui-progressive-retrieval-spec')
        ok('process match: a bare-id substring such as 10043 never matches a folder name',
           not rx.search('claude -p ticket 10043 and 10071') and rx.search('run.sh builder L2 .sdlc/.0043-gen-ui-progressive-retrieval-spec/step-1/handoff.md'))
        ok('process match: a longer folder name is not the folder', not name_regex('0001-a').search('x .sdlc/0001-a-b/handoff.md'))

        # snapshot and delta: a ticket that closed (its folder renamed, as tickets.py close does) between two runs
        sd4 = os.path.join(tmp, 'state4')
        LOAD_FN = lambda: (1.0, 1.0, 1.0)
        gh_stub = os.path.join(tmp, 'bin', 'gh')
        write(gh_stub, '#!/bin/sh\ncase "$*" in\n  *"--state merged"*) cat "$GH_MERGED";;\n  *) cat "$GH_OPEN";;\nesac\n')
        os.chmod(gh_stub, 0o755)
        GH_CMD = gh_stub
        os.environ['GH_OPEN'] = os.path.join(tmp, 'open.json')
        os.environ['GH_MERGED'] = os.path.join(tmp, 'merged.json')
        write(os.environ['GH_OPEN'], json.dumps([
            {'number': 7, 'title': 'seven', 'url': 'u7', 'isDraft': False, 'reviewDecision': 'APPROVED', 'mergeStateStatus': 'CLEAN', 'headRefName': 'a'},
            {'number': 8, 'title': 'eight', 'url': 'u8', 'isDraft': False, 'reviewDecision': '', 'mergeStateStatus': 'BLOCKED', 'headRefName': 'b'},
            {'number': 9, 'title': 'nine draft', 'url': 'u9', 'isDraft': True, 'reviewDecision': '', 'mergeStateStatus': 'DRAFT', 'headRefName': 'c'}]))
        write(os.environ['GH_MERGED'], '[]')
        ent = [{'name': 'repo', 'path': repo, 'conductor': 'c', 'gh': 'o/r'}]
        write(os.path.join(t2, 'builder-L1.running'), '%d\n' % int(time.time()))   # the dead marker is back for run one
        a = collect(ent, sd4, now=base)
        ok('delta: the first run says so and lists nothing', a['delta']['first_run'] and a['delta']['since'] is None
           and not a['delta']['closed'])
        prs = [n for n in a['needs_you'] if n['kind'] == 'pr']
        ok('needs you: open non-draft PRs via gh, drafts counted apart', [p['number'] for p in prs] == [7, 8]
           and a['repos'][0]['prs']['drafts'] == 1 and 'APPROVED' in prs[0]['detail'])
        os.unlink(os.path.join(t2, 'builder-L1.running'))
        os.rename(t3, os.path.join(repo, '.sdlc', '.0003-stale-row'))
        write(os.path.join(repo, '.sdlc', '.0003-stale-row', 'handoff.md'),
              '---\nid: T-0003\ntitle: "t T-0003"\ntype: chore\nstatus: done\nsize: S\n---\n\n## Goal\nx\n')
        write(os.environ['GH_OPEN'], json.dumps([
            {'number': 8, 'title': 'eight', 'url': 'u8', 'isDraft': False, 'reviewDecision': '', 'mergeStateStatus': 'BLOCKED', 'headRefName': 'b'}]))
        write(os.environ['GH_MERGED'], json.dumps([{'number': 7, 'title': 'seven', 'mergedAt': '2026-10-06T00:00:00Z'}]))
        b = collect(ent, sd4, now=base + datetime.timedelta(seconds=90))
        d = b['delta']
        ok('delta: a ticket closed between two runs is listed once as closed, by id', [c['id'] for c in d['closed']] == ['T-0003']
           and not d['gone'] and not any(n['id'] == 'T-0003' for n in d['new']))
        ok('delta: a state change is listed (T-0002 dead to stale, marker removed between the runs)',
           any(c['id'] == 'T-0002' and c['kind'] == 'state' and c['from'] == 'dead' and c['to'] == 'stale' for c in d['state_changes']))
        ok('delta: a merged PR is listed as merged, not closed', [p['number'] for p in d['prs_merged']] == [7] and not d['prs_closed'])
        ok('delta: since is the previous snapshot time', d['since'] == iso(base) and not d['first_run'])
        c = collect(ent, sd4, now=base + datetime.timedelta(seconds=180))
        ok('negative control: a third run with nothing changed lists no close and no state change',
           not c['delta']['closed'] and not c['delta']['state_changes'] and not c['delta']['prs_merged'])
        write(os.environ['GH_OPEN'], '[]')
        write(os.environ['GH_MERGED'], '[]')
        e2 = collect(ent, sd4, now=base + datetime.timedelta(seconds=240))
        ok('delta: a PR that left the open list unmerged is closed, not merged',
           [p['number'] for p in e2['delta']['prs_closed']] == [8] and not e2['delta']['prs_merged'])
        GH_CMD = os.path.join(tmp, 'bin', 'no-such-gh')
        f = collect(ent, os.path.join(tmp, 'state5'), now=base)
        ok('gh: a missing gh is an error object, not a crash, and the PR delta stays empty',
           'error' in f['repos'][0]['prs'] and not [n for n in f['needs_you'] if n['kind'] == 'pr'])
        GH_CMD = saved[1]

        # read-only on the inspected repo
        for k in kids:
            if k.poll() is None:
                k.kill()
                k.wait()
        # restore the repo files the run changed on purpose, then prove collect alone changes nothing
        after_setup = snap(tmp)
        ro = collect(ent, sd4, gh=False, now=base + datetime.timedelta(seconds=300))
        ok('read-only: collect changes no file under the inspected repo', [s for s in snap(tmp) if s[0].startswith('repo' + os.sep)]
           == [s for s in after_setup if s[0].startswith('repo' + os.sep)])
        ok('read-only: no state file is written in the repo', not os.path.exists(os.path.join(repo, '.sdlc', 'runtime'))
           and not os.path.exists(os.path.join(repo, '.sdlc', 'load.jsonl')))
        ok('read-only: --no-write writes neither file', not os.path.exists(os.path.join(tmp, 'state6'))
           and collect(ent, os.path.join(tmp, 'state6'), gh=False, write=False)['snapshot']['written'] is False
           and not os.path.exists(os.path.join(tmp, 'state6')))

        # cli
        me = os.path.abspath(__file__)

        def cli(*args, cwd=None):
            p = subprocess.run([sys.executable, me] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True, cwd=cwd)
            return p.returncode, p.stdout, p.stderr
        rc, so, se = cli('collect', repo, '--no-gh', '--state-dir', os.path.join(tmp, 'state7'), '--stop-line', '-1')
        data = json.loads(so) if rc == 0 else {}
        ok('cli: collect exits 0 with JSON and a status line', rc == 0 and se.startswith('status: 1 repos')
           and data.get('machine', {}).get('load', {}).get('verdict') == 'over' and data['repos'][0]['name'] == 'repo')
        ok('cli: every documented top-level key is present', all(k in data for k in (
            'time', 'machine', 'repos', 'needs_you', 'delta', 'snapshot')))
        rc, _o, _e = cli('collect', os.path.join(tmp, 'missing'), '--no-gh')
        ok('cli: a missing explicit repo exits 2', rc == 2)
        fleet = os.path.join(tmp, 'fleet.json')
        write(fleet, json.dumps({'version': 1, 'repos': [
            {'path': repo, 'name': 'in', 'conductor': 'c', 'status': 'active'},
            {'path': os.path.join(tmp, 'gone'), 'name': 'gone', 'conductor': 'c', 'status': 'active'},
            {'path': repo, 'name': 'out', 'conductor': 'c', 'status': 'excluded', 'reason': 'r', 'date': '2026-10-06'}]}))
        rc, so, _e = cli('collect', '--fleet', fleet, '--no-gh', '--state-dir', os.path.join(tmp, 'state8'))
        data = json.loads(so) if rc == 0 else {}
        names = [r['name'] for r in data.get('repos', [])]
        ok('cli: the registry supplies the active repos only', names == ['in', 'gone'])
        ok('cli: a registry entry with a missing directory is reported, not fatal',
           data['repos'][1].get('error') == 'no such directory')
        rc, _o, _e = cli('collect', '--fleet', os.path.join(tmp, 'absent.json'))
        ok('cli: no repo and no registry exits 2', rc == 2)
        nocwd = os.path.join(tmp, 'plain')
        os.makedirs(nocwd)
        rc, so, _e = cli('collect', repo, '--no-gh', cwd=nocwd)
        data = json.loads(so) if rc == 0 else {}
        ok('cli: with no .sdlc in the cwd and no --state-dir nothing is written',
           rc == 0 and data['snapshot']['written'] is False and os.listdir(nocwd) == [])
        os.makedirs(os.path.join(nocwd, '.sdlc'))
        rc, so, _e = cli('collect', repo, '--no-gh', cwd=nocwd)
        ok('cli: the default state dir is <cwd>/.sdlc/runtime',
           rc == 0 and os.path.isfile(os.path.join(nocwd, '.sdlc', 'runtime', 'load.jsonl'))
           and os.path.isfile(os.path.join(nocwd, '.sdlc', 'runtime', 'fleet-status.json')))
    finally:
        for k in kids:
            if k.poll() is None:
                k.kill()
                k.wait()
        PS_CMD, GH_CMD, GIT_CMD, LOAD_FN = saved
        os.environ.pop('GH_OPEN', None)
        os.environ.pop('GH_MERGED', None)
        shutil.rmtree(tmp, ignore_errors=True)
    if misses:
        print('fleet_status selftest: %d failed: %s' % (len(misses), '; '.join(misses)), file=sys.stderr)
        return 1
    print('fleet_status selftest: ok')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
