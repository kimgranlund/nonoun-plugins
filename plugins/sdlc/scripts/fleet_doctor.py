#!/usr/bin/env python3
"""Fleet doctor: why are runs slow or stuck. No model call. `collect` writes one JSON snapshot of the machine and the
live roles, `detect` applies fixed rules to it and prints one finding per hit with its evidence and its fixed
resolutions, `resolve` carries out one resolution the person approved and refuses anything else.

Usage: fleet_doctor.py collect [REPO ...] [--fleet FILE] [--state-dir DIR] [--out FILE]
       fleet_doctor.py detect [SNAPSHOT] [--state-dir DIR] [--json] [--stdin-wait-min N] [--stall-min N]
                              [--check-factor X] [--load-factor X] [--runaway-cpu N] [--heavy-cpu N]
                              [--replan-share X]
       fleet_doctor.py resolve (--kill PID | --restart NAME) [--state-dir DIR] [--findings FILE]
       fleet_doctor.py selftest

collect: REPO defaults to the active entries of .sdlc/fleet.json, or the work root's fleet.json (--fleet), else the current directory; the first
repo is "this repo". It writes the snapshot to --out (default <state-dir>/snapshot.json) and prints its path. State
dir default: .sdlc/runtime/fleet-doctor under this repo. Snapshot keys:
  ts, this_repo, load1, cores, top[] {pid, cpu, age_s, cmd} (the 10 busiest processes)
  roles[]   every claude or codex process: pid, kind (headless, lane, session), cwd, repo, age_s,
            transcript_age_s (newest *.jsonl write under ~/.claude/projects/<cwd slug>, null when none),
            child_change_age_s (age of the youngest descendant, else the role's own age),
            children[] {pid, ppid, cpu, age_s, stat, cmd, work: browser|test|null}
  loose[]   processes outside every role tree at 50% CPU or more: pid, cpu, age_s, cmd
  checks[]  running check.sh: pid, age_s; check_median_s, check_samples (finished check.sh durations this tool
            observed, kept in <state-dir>/checks.json; a median needs 3)
  durations {repo: {role: {median_s, count}}} and tickets[] {repo, task, plan_s, total_s} from each repo's
            runs.jsonl in .sdlc/<task>/, .sdlc/tickets/<task>/ and .sdlc/runtime/tasks/<task>/ (open tasks only;
            tickets[] holds only replanned, built ones)

detect rules (one finding per hit; --json prints JSON lines, else a text table; both write
<state-dir>/findings.jsonl, which resolve reads):
  stdin-wait    a role descendant that reads stdin (cat, tee, head, read, less, more) idle (CPU under 1%) longer than
                --stdin-wait-min (5)
  stalled       a headless or lane role with no transcript write and no child change for --stall-min (20)
  slow-check    a running check.sh older than --check-factor (2) times the recorded median
  overloaded    load1 above --load-factor (1.5) times the cores
  runaway-proc  a process outside every role, alive over an hour, above --runaway-cpu (80) percent
  heavy-peer    another repo's roles running browser or test work at --heavy-cpu (50) percent or more in sum
  replan-cost   planner and plan-reviewer time above --replan-share (0.4) of a ticket's run time (10 min or more), for
                a ticket that was replanned (two planner runs or more) and built (a builder or solo run)

resolve acts only on the last findings file: --kill PID needs a finding that names that pid, and the pid must still
run the command the finding recorded; --restart NAME needs NAME in DAEMONS (daemons the OS respawns) and a
runaway-proc finding for it. Anything else exits 2 and touches nothing.
"""
import json, os, re, signal, statistics, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fleet_collect  # same scripts/ dir: run_bounded, parse_etime, classify_process
import fleet_config   # same scripts/ dir: the repo registry
import wtroot         # same scripts/ dir: the worktree root and the legacy roots

PS_CMD = 'ps'
LSOF_CMD = 'lsof'
LOAD_FN = os.getloadavg
CORES_FN = os.cpu_count
PROJECTS_DIR = os.path.expanduser('~/.claude/projects')
PROBE_TIMEOUT = 10.0
DAEMONS = ('fontd', 'mds_stores', 'mdworker_shared', 'photoanalysisd', 'mediaanalysisd', 'cloudd', 'bird')
STDIN_READERS = ('cat', 'tee', 'head', 'read', 'less', 'more')
PLAN_ROLES = ('planner', 'plan-reviewer')
TEST_RE = re.compile(r'playwright|vitest|\bjest\b|pytest|\bnpm (run )?test\b|\bpnpm (run )?test\b|cargo test|go test'
                     r'|check\.sh')
DEFAULTS = {'stdin_wait_min': 5.0, 'stall_min': 20.0, 'check_factor': 2.0, 'load_factor': 1.5, 'runaway_cpu': 80.0,
            'heavy_cpu': 50.0, 'replan_share': 0.4}
MIN_TICKET_S = 600
LONG_LIVED_S = 3600
LOOSE_CPU = 50.0

# Fixed resolutions per rule: (action, cost, risk). `{pid}` and `{name}` come from the finding.
RESOLUTIONS = {
    'stdin-wait': [('kill pid {pid} (the idle stdin reader; the role\'s command then fails and it goes on)',
                    'seconds', 'low: only that pid')],
    'stalled': [('ticket: file or link a ticket for the stall', 'minutes', 'none'),
                ('kill pid {pid} (stops the role; its lane needs a rerun)', 'the role\'s work so far', 'high')],
    'slow-check': [('message the busy factories one line: hold browser and test work until check.sh ends',
                    'one message', 'low'),
                   ('wait', 'time', 'none')],
    'overloaded': [('message the busy factories one line: pause new lanes until load drops', 'one message', 'low'),
                   ('wait', 'time', 'none')],
    'runaway-proc': [('restart {name} (killall; the OS respawns it)', 'seconds', 'low'),
                     ('kill pid {pid}', 'seconds', 'medium: not respawned')],
    'heavy-peer': [('message the {name} factory one line: throttle browser and test lanes', 'one message', 'low'),
                   ('wait', 'time', 'none')],
    'replan-cost': [('ticket: file or link a ticket on the replan cost', 'minutes', 'none')],
}


class DoctorError(Exception):
    pass


# --- collect -----------------------------------------------------------------

def ps_rows():
    """[{pid, ppid, cpu, age_s, stat, cmd}] from one ps call. This process is left out."""
    r = fleet_collect.run_bounded([PS_CMD, '-axo', 'pid=,ppid=,pcpu=,etime=,stat=,command='], PROBE_TIMEOUT)
    if not r.ok:
        raise DoctorError('ps failed: %s' % (r.err or r.out).strip()[:200])
    me, out = os.getpid(), []
    for line in r.out.splitlines():
        m = re.match(r'^\s*(\d+)\s+(\d+)\s+([\d.]+)\s+(\S+)\s+(\S+)\s+(.*)$', line)
        if not m or int(m.group(1)) == me:
            continue
        out.append({'pid': int(m.group(1)), 'ppid': int(m.group(2)), 'cpu': float(m.group(3)),
                    'age_s': fleet_collect.parse_etime(m.group(4)) or 0, 'stat': m.group(5), 'cmd': m.group(6)})
    return out


def cwds(pids):
    """{pid: cwd} from one lsof call; empty when lsof is missing or fails."""
    if not pids:
        return {}
    r = fleet_collect.run_bounded([LSOF_CMD, '-a', '-d', 'cwd', '-Fpn', '-p', ','.join(str(p) for p in pids)],
                                  PROBE_TIMEOUT)
    out, cur = {}, None
    for line in (r.out or '').splitlines():
        if line.startswith('p') and line[1:].isdigit():
            cur = int(line[1:])
        elif line.startswith('n') and cur is not None:
            out[cur] = line[1:]
    return out


def is_role(cmd):
    toks = cmd.split()
    if not toks:
        return False
    if fleet_collect.classify_process(cmd) == 'claude':
        return True
    return os.path.basename(toks[0]) == 'codex' or (len(toks) > 1 and os.path.basename(toks[1]) == 'codex')


def role_kind(cmd, cwd):
    toks = cmd.split()
    if '-p' in toks or '--print' in toks or (len(toks) > 1 and 'exec' in toks[1:3] and 'codex' in cmd):
        return 'headless'
    if cwd and in_lane(cwd):
        return 'lane'
    return 'session'


def lane_main(path):
    """Outside git: the main checkout a lane path names by wtroot's folder rules (<main>/.worktrees/...,
    <main>/.claude/worktrees/... (legacy), <parent>/<main>.worktrees/...), else None."""
    parts = path.split(os.sep)
    for i, s in enumerate(parts):
        if s == wtroot.LEGACY or tuple(parts[i:i + 2]) == wtroot.CLAUDE:
            return os.sep.join(parts[:i]) or None
        if s.endswith(wtroot.SUFFIX):
            return os.sep.join(parts[:i] + [s[:-len(wtroot.SUFFIX)]])
    return None


def in_lane(path):
    """True when path lies under the worktree root or a legacy root of its repository (wtroot.py, T-0575); outside
    git, when its folders name one (lane_main)."""
    r = wtroot.root(path) if os.path.isdir(path) else None
    if not r:
        return lane_main(path) is not None
    real = os.path.realpath(path)
    return any(real.startswith(os.path.realpath(str(d)) + os.sep) for d in [r] + wtroot.legacy_roots(path))


def repo_of(path):
    """The main checkout a path belongs to (wtroot.main_top, so a lane under any root names its main checkout);
    outside git the main checkout its lane folders name, else the nearest folder holding .git."""
    if not path:
        return None
    top = wtroot.main_top(path) if os.path.isdir(path) else None
    if top:
        return top
    if lane_main(path):
        return lane_main(path)
    p = path
    while p and p != os.sep:
        if os.path.exists(os.path.join(p, '.git')):
            return p
        p = os.path.dirname(p)
    return path


def slug(path):
    return re.sub(r'[^A-Za-z0-9]', '-', path)


def transcript_age(cwd, now):
    """Seconds since the newest *.jsonl write in the cwd's Claude project folder, or None."""
    if not cwd:
        return None
    d = os.path.join(PROJECTS_DIR, slug(cwd))
    best = None
    for root, _dirs, files in os.walk(d):
        for n in files:
            if n.endswith('.jsonl'):
                try:
                    m = os.stat(os.path.join(root, n)).st_mtime
                except OSError:
                    continue
                best = m if best is None or m > best else best
    return None if best is None else max(0, int(now - best))


def work_kind(cmd):
    if fleet_collect.classify_process(cmd) == 'chromium':
        return 'browser'
    return 'test' if TEST_RE.search(cmd) else None


def descendants(rows, pid):
    kids = {}
    for r in rows:
        kids.setdefault(r['ppid'], []).append(r)
    out, stack = [], [pid]
    while stack:
        for c in kids.get(stack.pop(), []):
            out.append(c)
            stack.append(c['pid'])
    return out


def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or '.')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1)
        f.write('\n')
    os.replace(tmp, path)


def track_checks(state_dir, checks):
    """Record finished check.sh runs: a pid seen last time and gone now finished at its last seen age.
    Returns (median_s or None, samples)."""
    path = os.path.join(state_dir, 'checks.json')
    st = read_json(path, {})
    seen, done = st.get('seen') or {}, st.get('done') or []
    live = {str(c['pid']): c['age_s'] for c in checks}
    for pid, age in seen.items():
        if pid not in live and isinstance(age, (int, float)) and age >= 60:
            done.append(int(age))
    done = done[-20:]
    write_json(path, {'seen': live, 'done': done})
    return (statistics.median(done) if len(done) >= 3 else None), len(done)


def task_runs(repo):
    """Yield (task, rows) for each open task's runs.jsonl under repo/.sdlc."""
    base = os.path.join(repo, '.sdlc')
    for parent in (base, os.path.join(base, 'tickets'), os.path.join(base, 'runtime', 'tasks')):
        try:
            names = sorted(os.listdir(parent))
        except OSError:
            continue
        for n in names:
            p = os.path.join(parent, n, 'runs.jsonl')
            if n.startswith('.') or not os.path.isfile(p):
                continue
            rows = []
            with open(p, encoding='utf-8', errors='replace') as f:
                for line in f:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(rec, dict) and isinstance(rec.get('duration_ms'), (int, float)):
                        rows.append(rec)
            yield n, rows


def run_stats(repo):
    by_role, tickets = {}, []
    for task, rows in task_runs(repo):
        plan = total = 0.0
        plans = sum(1 for rec in rows if rec.get('role') == 'planner')
        built = any(rec.get('role') in ('builder', 'solo') for rec in rows)
        for rec in rows:
            s = rec['duration_ms'] / 1000.0
            by_role.setdefault(str(rec.get('role')), []).append(s)
            total += s
            if rec.get('role') in PLAN_ROLES:
                plan += s
        if rows and plans >= 2 and built:   # a replan happened and the ticket got built
            tickets.append({'repo': repo, 'task': task, 'plan_s': round(plan), 'total_s': round(total)})
    return {r: {'median_s': round(statistics.median(v)), 'count': len(v)} for r, v in sorted(by_role.items())}, tickets


def collect(repos, state_dir, now=None):
    now = now or time.time()
    rows = ps_rows()
    role_rows = [r for r in rows if is_role(r['cmd'])]
    role_pids = {r['pid'] for r in role_rows}
    # a role nested inside another role (a claude child of a claude) is reported once, at the outer role
    outer = [r for r in role_rows if not any(a in role_pids for a in ancestors(rows, r['pid']))]
    cwd = cwds([r['pid'] for r in outer])
    in_tree, roles = set(), []
    for r in outer:
        kids = descendants(rows, r['pid'])
        in_tree.add(r['pid'])
        in_tree.update(k['pid'] for k in kids)
        c = cwd.get(r['pid'])
        roles.append({'pid': r['pid'], 'kind': role_kind(r['cmd'], c), 'cwd': c, 'repo': repo_of(c),
                      'age_s': r['age_s'], 'cmd': r['cmd'][:200], 'transcript_age_s': transcript_age(c, now),
                      'child_change_age_s': min([k['age_s'] for k in kids] or [r['age_s']]),
                      'children': [{'pid': k['pid'], 'ppid': k['ppid'], 'cpu': k['cpu'], 'age_s': k['age_s'],
                                    'stat': k['stat'], 'cmd': k['cmd'][:200], 'work': work_kind(k['cmd'])}
                                   for k in kids]})
    checks = [{'pid': r['pid'], 'age_s': r['age_s'], 'cmd': r['cmd'][:200]} for r in rows
              if re.search(r'(^|[\s/])check\.sh(\s|$)', r['cmd']) and re.match(r'^\S*\b(ba|z)?sh\s', r['cmd'])]
    median, samples = track_checks(state_dir, checks)
    durations, tickets = {}, []
    for repo in repos:
        durations[repo], t = run_stats(repo)
        tickets += t
    load1 = LOAD_FN()[0]
    return {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)), 'this_repo': repos[0] if repos else None,
            'load1': round(load1, 2), 'cores': CORES_FN() or 1,
            'top': [{'pid': r['pid'], 'cpu': r['cpu'], 'age_s': r['age_s'], 'cmd': r['cmd'][:120]}
                    for r in sorted(rows, key=lambda r: -r['cpu'])[:10]],
            'roles': roles,
            'loose': [{'pid': r['pid'], 'cpu': r['cpu'], 'age_s': r['age_s'], 'cmd': r['cmd'][:200]} for r in rows
                      if r['pid'] not in in_tree and r['cpu'] >= LOOSE_CPU],
            'checks': checks, 'check_median_s': median, 'check_samples': samples,
            'durations': durations, 'tickets': tickets}


def ancestors(rows, pid):
    parent = {r['pid']: r['ppid'] for r in rows}
    out, p, guard = [], parent.get(pid), 0
    while p and p != 1 and guard < 200:
        out.append(p)
        p, guard = parent.get(p), guard + 1
    return out


# --- detect ------------------------------------------------------------------

def mins(s):
    return '%dm' % round(s / 60.0)


def exe(cmd):
    toks = cmd.split()
    return os.path.basename(toks[0]) if toks else ''


def finding(rule, evidence, value, threshold, **kw):
    f = {'rule': rule, 'evidence': evidence, 'value': value, 'threshold': threshold}
    f.update(kw)
    f['resolutions'] = [{'action': a.format(pid=f.get('pid'), name=f.get('name')), 'cost': c, 'risk': r}
                        for a, c, r in RESOLUTIONS[rule]]
    return f


def detect(snap, th=None):
    th = dict(DEFAULTS, **(th or {}))
    out = []
    for role in snap.get('roles', []):
        for k in role.get('children', []):
            toks = k['cmd'].split()
            reader = exe(k['cmd']) in STDIN_READERS and all(t.startswith('-') or t == '-' for t in toks[1:])
            if reader and k['cpu'] < 1.0 and k['age_s'] > th['stdin_wait_min'] * 60:
                out.append(finding('stdin-wait', 'pid %d `%s` idle %s under role pid %d (%s)'
                                   % (k['pid'], k['cmd'][:60], mins(k['age_s']), role['pid'], role.get('cwd')),
                                   k['age_s'], th['stdin_wait_min'] * 60, pid=k['pid'], cmd=k['cmd'],
                                   role_pid=role['pid']))
        if role.get('kind') in ('headless', 'lane'):
            ta, ca = role.get('transcript_age_s'), role.get('child_change_age_s') or 0
            quiet = min(x for x in (ta, ca) if x is not None)
            lim = th['stall_min'] * 60
            if role.get('age_s', 0) > lim and (ta is None or ta > lim) and ca > lim:
                out.append(finding('stalled', 'role pid %d (%s, %s) transcript %s, last child change %s ago'
                                   % (role['pid'], role['kind'], role.get('cwd'),
                                      'none' if ta is None else mins(ta) + ' ago', mins(ca)),
                                   quiet, lim, pid=role['pid'], cmd=role.get('cmd', '')))
    med = snap.get('check_median_s')
    for c in snap.get('checks', []):
        if med and c['age_s'] > th['check_factor'] * med:
            out.append(finding('slow-check', 'check.sh pid %d running %s, median %s over %d runs'
                               % (c['pid'], mins(c['age_s']), mins(med), snap.get('check_samples', 0)),
                               c['age_s'], th['check_factor'] * med, pid=c['pid'], cmd=c.get('cmd', '')))
    load, cores = snap.get('load1', 0), snap.get('cores') or 1
    if load > th['load_factor'] * cores:
        busy = ', '.join('%d %s %.0f%%' % (p['pid'], exe(p['cmd']), p['cpu']) for p in snap.get('top', [])[:3])
        out.append(finding('overloaded', 'load %.1f on %d cores; top: %s' % (load, cores, busy),
                           load, th['load_factor'] * cores))
    for p in snap.get('loose', []):
        if p['cpu'] > th['runaway_cpu'] and p['age_s'] > LONG_LIVED_S:
            name = exe(p['cmd'])
            out.append(finding('runaway-proc', 'pid %d %s at %.0f%% CPU for %s%s'
                               % (p['pid'], name, p['cpu'], mins(p['age_s']),
                                  ' (OS respawns it)' if name in DAEMONS else ''),
                               p['cpu'], th['runaway_cpu'], pid=p['pid'], name=name, cmd=p['cmd']))
    peers = {}
    for role in snap.get('roles', []):
        if not role.get('repo') or role.get('repo') == snap.get('this_repo'):
            continue
        for k in role.get('children', []):
            if k.get('work'):
                agg = peers.setdefault(role['repo'], {'cpu': 0.0, 'n': 0, 'kinds': set()})
                agg['cpu'] += k['cpu']
                agg['n'] += 1
                agg['kinds'].add(k['work'])
    for repo, agg in sorted(peers.items()):
        if agg['cpu'] >= th['heavy_cpu']:
            out.append(finding('heavy-peer', '%s: %d %s processes at %.0f%% CPU'
                               % (repo, agg['n'], '+'.join(sorted(agg['kinds'])), agg['cpu']),
                               round(agg['cpu'], 1), th['heavy_cpu'], name=os.path.basename(repo), repo=repo))
    for t in snap.get('tickets', []):
        if t['total_s'] >= MIN_TICKET_S and t['plan_s'] > th['replan_share'] * t['total_s']:
            share = t['plan_s'] / float(t['total_s'])
            out.append(finding('replan-cost', '%s/.sdlc %s: planning %s of %s (%.0f%%)'
                               % (t['repo'], t['task'], mins(t['plan_s']), mins(t['total_s']), share * 100),
                               round(share, 2), th['replan_share'], task=t['task'], repo=t['repo']))
    return out


def render(findings):
    if not findings:
        return 'fleet doctor: no findings'
    lines = ['fleet doctor: %d finding%s' % (len(findings), '' if len(findings) == 1 else 's')]
    for i, f in enumerate(findings, 1):
        lines.append('%d. %s  %s' % (i, f['rule'], f['evidence']))
        for j, r in enumerate(f['resolutions']):
            lines.append('   %s %s  (cost: %s; risk: %s)' % ('*' if j == 0 else '-', r['action'], r['cost'], r['risk']))
    return '\n'.join(lines)


# --- resolve -----------------------------------------------------------------

def read_findings(path):
    out = []
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    except (OSError, ValueError) as e:
        raise DoctorError('no findings to act on (%s): run detect first' % e)
    return out


def current_cmd(pid):
    for r in ps_rows():
        if r['pid'] == pid:
            return r['cmd']
    return None


def resolve_kill(findings, pid, kill=os.kill):
    hit = [f for f in findings if f.get('pid') == pid and f['rule'] in ('stdin-wait', 'stalled', 'runaway-proc')]
    if not hit:
        raise DoctorError('pid %d is in no finding; nothing killed' % pid)
    cmd = current_cmd(pid)
    if cmd is None:
        raise DoctorError('pid %d is gone; nothing killed' % pid)
    if hit[0].get('cmd') and cmd[:200] != hit[0]['cmd'][:200]:
        raise DoctorError('pid %d now runs `%s`, not the finding\'s command; nothing killed' % (pid, cmd[:60]))
    kill(pid, signal.SIGTERM)
    return 'killed pid %d (%s, SIGTERM)' % (pid, hit[0]['rule'])


def resolve_restart(findings, name, run=None):
    if name not in DAEMONS:
        raise DoctorError('%s is not a daemon the OS respawns (%s); nothing restarted' % (name, ', '.join(DAEMONS)))
    if not any(f['rule'] == 'runaway-proc' and f.get('name') == name for f in findings):
        raise DoctorError('%s is in no runaway-proc finding; nothing restarted' % name)
    (run or (lambda c: subprocess.run(c, check=False)))(['killall', name])
    return 'restarted %s (killall; the OS respawns it)' % name


# --- cli ---------------------------------------------------------------------

def default_state_dir(repo):
    return os.path.join(repo, '.sdlc', 'runtime', 'fleet-doctor')


def git_root(path):
    r = fleet_collect.run_bounded(['git', '-C', path, 'rev-parse', '--show-toplevel'], PROBE_TIMEOUT)
    return r.out.strip() if r.ok and r.out.strip() else os.path.abspath(path)


def take(argv, flag, cast=str):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 >= len(argv):
            raise DoctorError('%s needs a value' % flag)
        val = argv[i + 1]
        del argv[i:i + 2]
        try:
            return cast(val)
        except ValueError:
            raise DoctorError('%s: bad value %s' % (flag, val))
    return None


def main(argv):
    if not argv:
        print(__doc__.split('\n\n')[1], file=sys.stderr)
        return 2
    cmd, argv = argv[0], list(argv[1:])
    if cmd == 'selftest':
        return selftest()
    here = repo_of(git_root(os.getcwd()))   # a lane worktree reports as its main checkout
    state = take(argv, '--state-dir')
    if cmd == 'collect':
        fleet, out = take(argv, '--fleet'), take(argv, '--out')
        repos = [os.path.abspath(a) for a in argv if not a.startswith('-')]
        if not repos:
            fpath = fleet or fleet_config.default_path(here)
            if os.path.exists(fpath):
                repos = [os.path.expanduser(r['path']) for r in fleet_config.load(fpath)['repos']
                         if r['status'] == 'active']
            if here not in repos:
                repos.insert(0, here)
        state = state or default_state_dir(repos[0])
        snap = collect(repos, state)
        out = out or os.path.join(state, 'snapshot.json')
        write_json(out, snap)
        print(out)
        return 0
    state = state or default_state_dir(here)
    fpath = take(argv, '--findings') or os.path.join(state, 'findings.jsonl')
    if cmd == 'detect':
        th = {}
        for flag, key in (('--stdin-wait-min', 'stdin_wait_min'), ('--stall-min', 'stall_min'),
                          ('--check-factor', 'check_factor'), ('--load-factor', 'load_factor'),
                          ('--runaway-cpu', 'runaway_cpu'), ('--heavy-cpu', 'heavy_cpu'),
                          ('--replan-share', 'replan_share')):
            v = take(argv, flag, float)
            if v is not None:
                th[key] = v
        as_json = '--json' in argv
        rest = [a for a in argv if a != '--json']
        if any(a.startswith('-') for a in rest):
            raise DoctorError('unknown flag %s' % [a for a in rest if a.startswith('-')][0])
        snap = read_json(rest[0] if rest else os.path.join(state, 'snapshot.json'), None)
        if not isinstance(snap, dict):
            raise DoctorError('no snapshot: run collect first')
        found = detect(snap, th)
        os.makedirs(os.path.dirname(fpath) or '.', exist_ok=True)
        with open(fpath, 'w', encoding='utf-8') as f:
            for x in found:
                f.write(json.dumps(x, sort_keys=True) + '\n')
        print('\n'.join(json.dumps(x, sort_keys=True) for x in found) if as_json else render(found))
        return 0
    if cmd == 'resolve':
        pid, name = take(argv, '--kill', int), take(argv, '--restart')
        if (pid is None) == (name is None) or argv:
            raise DoctorError('resolve takes exactly one of --kill PID or --restart NAME')
        findings = read_findings(fpath)
        print(resolve_kill(findings, pid) if pid is not None else resolve_restart(findings, name))
        return 0
    raise DoctorError('unknown command %s' % cmd)


# --- selftest ----------------------------------------------------------------

def _role(**kw):
    r = {'pid': 100, 'kind': 'lane', 'cwd': '/r/this/.worktrees/a', 'repo': '/r/this', 'age_s': 7200,
         'cmd': 'claude -p x', 'transcript_age_s': 30, 'child_change_age_s': 30, 'children': []}
    r.update(kw)
    return r


def _kid(**kw):
    k = {'pid': 200, 'ppid': 100, 'cpu': 0.0, 'age_s': 30, 'stat': 'S', 'cmd': 'cat', 'work': None}
    k.update(kw)
    return k


def _snap(**kw):
    s = {'this_repo': '/r/this', 'load1': 4.0, 'cores': 20, 'top': [], 'roles': [], 'loose': [], 'checks': [],
         'check_median_s': None, 'check_samples': 0, 'durations': {}, 'tickets': []}
    s.update(kw)
    return s


# Per rule: (positive snapshot, negative-control snapshot). The negative is the same shape just short of the rule.
CASES = {
    'stdin-wait': (_snap(roles=[_role(children=[_kid(age_s=39 * 60)])]),
                   _snap(roles=[_role(children=[_kid(age_s=39 * 60, cmd='cat /tmp/file')])])),
    'stalled': (_snap(roles=[_role(transcript_age_s=40 * 60, child_change_age_s=40 * 60)]),
                _snap(roles=[_role(kind='session', transcript_age_s=40 * 60, child_change_age_s=40 * 60)])),
    'slow-check': (_snap(checks=[{'pid': 300, 'age_s': 47 * 60, 'cmd': 'bash check.sh'}], check_median_s=18 * 60,
                         check_samples=5),
                   _snap(checks=[{'pid': 300, 'age_s': 30 * 60, 'cmd': 'bash check.sh'}], check_median_s=18 * 60,
                         check_samples=5)),
    'overloaded': (_snap(load1=54.0), _snap(load1=29.0)),
    'runaway-proc': (_snap(loose=[{'pid': 400, 'cpu': 101.0, 'age_s': 26 * 86400, 'cmd': '/System/x/fontd'}]),
                     _snap(loose=[{'pid': 400, 'cpu': 101.0, 'age_s': 600, 'cmd': '/System/x/fontd'}])),
    'heavy-peer': (_snap(roles=[_role(repo='/r/maison', children=[_kid(cpu=180.0, cmd='node playwright test',
                                                                       work='test')])]),
                   _snap(roles=[_role(children=[_kid(cpu=180.0, cmd='node playwright test', work='test')])])),
    'replan-cost': (_snap(tickets=[{'repo': '/r/this', 'task': '0543-x', 'plan_s': 1500, 'total_s': 3000}]),
                    _snap(tickets=[{'repo': '/r/this', 'task': '0543-x', 'plan_s': 900, 'total_s': 3000}])),
}

# Each is silent: one condition of a rule just short of its threshold, so a dropped or loosened condition turns red.
BOUNDARY = [
    ('stdin-wait reader aged 4 min', _snap(roles=[_role(children=[_kid(age_s=4 * 60)])])),
    ('stdin-wait reader at 5% CPU', _snap(roles=[_role(children=[_kid(age_s=39 * 60, cpu=5.0)])])),
    ('stalled with a transcript write 10 min ago',
     _snap(roles=[_role(transcript_age_s=10 * 60, child_change_age_s=40 * 60)])),
    ('stalled with a child change 10 min ago',
     _snap(roles=[_role(transcript_age_s=40 * 60, child_change_age_s=10 * 60)])),
    ('slow-check at exactly 2x the median', _snap(checks=[{'pid': 300, 'age_s': 36 * 60, 'cmd': 'bash check.sh'}],
                                                  check_median_s=18 * 60, check_samples=5)),
    ('overloaded at exactly 1.5x the cores', _snap(load1=30.0)),
    ('runaway-proc at 79% CPU', _snap(loose=[{'pid': 400, 'cpu': 79.0, 'age_s': 26 * 86400, 'cmd': '/System/x/fontd'}])),
    ('heavy-peer at 49% CPU', _snap(roles=[_role(repo='/r/maison', children=[_kid(cpu=49.0, cmd='node playwright test',
                                                                                  work='test')])])),
    ('replan-cost on a 500 s ticket', _snap(tickets=[{'repo': '/r/this', 'task': '0543-x', 'plan_s': 400,
                                                      'total_s': 500}])),
]


def selftest():
    fails = []

    def check(name, ok):
        print('%s: %s' % ('ok' if ok else 'FAIL', name))
        if not ok:
            fails.append(name)

    for rule in RESOLUTIONS:
        check('case table covers %s' % rule, rule in CASES)
    for rule, (pos, neg) in CASES.items():
        got = [f['rule'] for f in detect(pos)]
        check('%s positive: fires once' % rule, got == [rule])
        neg_got = [f['rule'] for f in detect(neg)]
        check('%s negative control: silent (observed %s)' % (rule, neg_got or 'nothing'), neg_got == [])
    for name, snap in BOUNDARY:
        got = [x['rule'] for x in detect(snap)]
        check('boundary: %s is silent (observed %s)' % (name, got or 'nothing'), got == [])
    f = detect(CASES['stdin-wait'][0])[0]
    check('stdin-wait names the reader pid and resolutions', f['pid'] == 200 and 'kill pid 200' in
          f['resolutions'][0]['action'])
    check('slow-check with no recorded median is silent', detect(_snap(checks=[{'pid': 1, 'age_s': 99999,
                                                                                'cmd': 'bash check.sh'}])) == [])
    check('stdin-wait threshold flag at 0 fires on a young reader',
          [x['rule'] for x in detect(_snap(roles=[_role(children=[_kid(age_s=2)])]), {'stdin_wait_min': 0})]
          == ['stdin-wait'])
    check('runaway-proc marks a listed daemon', 'OS respawns' in detect(CASES['runaway-proc'][0])[0]['evidence'])

    # collect over a stubbed ps, lsof and runs tree
    global ps_rows, cwds, LOAD_FN, CORES_FN, PROJECTS_DIR
    saved = (ps_rows, cwds, LOAD_FN, CORES_FN, PROJECTS_DIR)
    d = tempfile.mkdtemp()
    try:
        repo = os.path.join(d, 'this')
        task = os.path.join(repo, '.sdlc', '0001-x')
        os.makedirs(task)
        os.makedirs(os.path.join(repo, '.sdlc', '.0002-closed'))
        with open(os.path.join(task, 'runs.jsonl'), 'w') as fh:
            fh.write(json.dumps({'role': 'planner', 'duration_ms': 600000}) + '\n')
            fh.write(json.dumps({'role': 'planner', 'duration_ms': 600000}) + '\n')
            fh.write(json.dumps({'role': 'builder', 'duration_ms': 600000}) + '\n')
        unbuilt = os.path.join(repo, '.sdlc', '0003-planning')
        os.makedirs(unbuilt)
        with open(os.path.join(unbuilt, 'runs.jsonl'), 'w') as fh:
            for _ in range(2):
                fh.write(json.dumps({'role': 'planner', 'duration_ms': 900000}) + '\n')
        with open(os.path.join(repo, '.sdlc', '.0002-closed', 'runs.jsonl'), 'w') as fh:
            fh.write(json.dumps({'role': 'planner', 'duration_ms': 9}) + '\n')
        lane = os.path.join(repo, '.worktrees', 'a')
        os.makedirs(os.path.join(d, 'projects', slug(lane)))
        open(os.path.join(d, 'projects', slug(lane), 's.jsonl'), 'w').close()
        rows = [{'pid': 10, 'ppid': 1, 'cpu': 1.0, 'age_s': 5000, 'stat': 'S', 'cmd': 'claude -p --agent x'},
                {'pid': 11, 'ppid': 10, 'cpu': 0.0, 'age_s': 2400, 'stat': 'S', 'cmd': '/bin/zsh -c cat > /tmp/x'},
                {'pid': 12, 'ppid': 11, 'cpu': 0.0, 'age_s': 2400, 'stat': 'S', 'cmd': 'cat'},
                {'pid': 13, 'ppid': 10, 'cpu': 0.0, 'age_s': 60, 'stat': 'S', 'cmd': 'claude --agent nested'},
                {'pid': 20, 'ppid': 1, 'cpu': 101.0, 'age_s': 90000, 'stat': 'R', 'cmd': '/System/fontd'},
                {'pid': 30, 'ppid': 1, 'cpu': 5.0, 'age_s': 30, 'stat': 'S', 'cmd': 'bash scripts/check.sh'}]
        ps_rows = lambda: rows
        cwds = lambda pids: {10: lane}
        LOAD_FN, CORES_FN, PROJECTS_DIR = (lambda: (3.0, 3.0, 3.0)), (lambda: 8), os.path.join(d, 'projects')
        state = os.path.join(d, 'state')
        snap = collect([repo], state)
        check('collect: one outer role (nested claude folded in)', [r['pid'] for r in snap['roles']] == [10])
        check('collect: role kind headless, repo from the lane path',
              snap['roles'][0]['kind'] == 'headless' and snap['roles'][0]['repo'] == repo)
        check('collect: transcript found by cwd slug', snap['roles'][0]['transcript_age_s'] is not None)
        check('collect: fontd is loose, role children are not', [p['pid'] for p in snap['loose']] == [20])
        check('collect: open, replanned, built ticket only; planner share', snap['tickets'] == [{'repo': repo, 'task': '0001-x',
                                                                               'plan_s': 1200, 'total_s': 1800}])
        check('collect: check.sh seen, no median yet', [c['pid'] for c in snap['checks']] == [30]
              and snap['check_median_s'] is None)
        rules = sorted(f['rule'] for f in detect(snap))
        check('collect then detect: stdin-wait, runaway-proc, replan-cost (observed %s)' % rules,
              rules == ['replan-cost', 'runaway-proc', 'stdin-wait'])
        for age in (1000, 1100, 1200):   # three finished check.sh runs give a median
            rows[-1] = dict(rows[-1], pid=rows[-1]['pid'] + 1, age_s=age)
            collect([repo], state)
        rows[-1] = dict(rows[-1], pid=99, age_s=60)
        snap = collect([repo], state)
        check('collect: finished check.sh runs give a median', snap['check_median_s'] == 1100
              and snap['check_samples'] == 3)
        # T-0575: a role whose cwd is a lane under the sibling root (wtroot.py root, <parent>/<repo>.worktrees)
        sib = os.path.realpath(os.path.join(d, 'sib'))
        os.makedirs(sib)
        sl = os.path.join(sib + '.worktrees', 'a')
        for a in (['init', '-q'], ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'i'],
                  ['worktree', 'add', '-q', '--detach', sl, 'HEAD']):
            subprocess.run(['git', '-C', sib] + a, check=True, capture_output=True)
        check('sibling root: a role in a lane under <repo>.worktrees is a lane role of the main checkout',
              role_kind('claude --agent x', sl) == 'lane' and repo_of(sl) == sib)
        check('sibling root control: a role in the main checkout is a session role of it',
              role_kind('claude --agent x', sib) == 'session' and repo_of(sib) == sib)
    finally:
        ps_rows, cwds, LOAD_FN, CORES_FN, PROJECTS_DIR = saved

    # resolve: acts only on what a finding names
    procs = [subprocess.Popen(['sleep', '60']) for _ in range(2)]
    try:
        target, sibling = procs
        cmd = current_cmd(target.pid)
        findings = [{'rule': 'stdin-wait', 'pid': target.pid, 'cmd': cmd}]
        for bad, why in ((sibling.pid, 'a pid in no finding'),):
            try:
                resolve_kill(findings, bad)
                check('resolve refuses %s' % why, False)
            except DoctorError:
                check('resolve refuses %s' % why, sibling.poll() is None)
        try:
            resolve_kill([{'rule': 'stdin-wait', 'pid': target.pid, 'cmd': 'something else'}], target.pid)
            check('resolve refuses a reused pid', False)
        except DoctorError:
            check('resolve refuses a reused pid', target.poll() is None)
        resolve_kill(findings, target.pid)
        target.wait(timeout=5)
        check('resolve kills the named pid only', target.returncode is not None and sibling.poll() is None)
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
                p.wait()
    ran = []
    for name, fs, why in (('Finder', [{'rule': 'runaway-proc', 'name': 'Finder'}], 'a name not in DAEMONS'),
                          ('fontd', [], 'a daemon with no runaway-proc finding')):
        try:
            resolve_restart(fs, name, run=ran.append)
            check('restart refuses %s' % why, False)
        except DoctorError:
            check('restart refuses %s' % why, ran == [])
    resolve_restart([{'rule': 'runaway-proc', 'name': 'fontd'}], 'fontd', run=ran.append)
    check('restart runs killall for a listed daemon', ran == [['killall', 'fontd']])
    print('fleet_doctor selftest: %s' % ('FAIL %d' % len(fails) if fails else 'ok'))
    return 1 if fails else 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except (DoctorError, fleet_config.FleetError) as e:
        print('fleet_doctor.py: %s' % e, file=sys.stderr)
        sys.exit(2)
