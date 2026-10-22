#!/usr/bin/env python3
"""Shared admission authority for heavy gates (npm test, browser shards, tsc): one weighted FIFO queue per
OS user and host, across every session, repo and worktree, so a pile of lanes does not run the machine out of
CPU and memory. Design: docs/specs/sdlc-lite/gate-lock-admission.md (protocol sdlc-gate/2, tickets T-0386, T-0409).

Usage: gate_lock.py run [--need RES=N[,RES=N...]] [--slots N] [--priority P] [--name X] [--repo PATH] [--nice]
                        [--timeout SECS] [--receipt FILE] -- <cmd...>
       gate_lock.py context [--json] | capabilities --json | status [--json]
       gate_lock.py policy show | policy set [RES=N...] [max_load=N] [node_heap_mb=N] [--default RES=N...] | policy reset
       gate_lock.py reset --confirm | reap [--older-than MIN] [--kill] [--match REGEX] | selftest

  run     queues for a grant of the weighted demand (a vector of resources, all or none), waits in order, runs the
          command in its own process group, drains the group, and releases. It exits with the command's status
          (a command killed by signal n gives 128+n, a command that cannot start gives 127 or 126). Every
          admission failure exits 3 with one first stderr line `gate_lock: <code>: <detail>` (codes: timeout,
          too_large, bad_context, state_unavailable, ledger_corrupt); the wait timeout keeps `gate_lock: timeout
          after ...`. State root: $SDLC_GATE_DIR (tests), else <home>/.local/state/sdlc-lite/gate-lock from the
          password database, never TMPDIR. ledger.json holds boot id, grants and queue under a short flock; the
          optional policy.json holds capacity and default_need. Built-in policy (the approved numbers):
          capacity compute_units 6 and browser_jobs 3, default_need compute_units 3 (so two undeclared gates run
          at once). A run with no --need asks for default_need; --slots N (or SDLC_GATE_SLOTS=N, 1 or more) asks
          for max(1, compute capacity // N) compute units, a demand share and never a cap; --need names resources
          (a resource the policy does not cap is recorded and not charged). A need above a capped resource is
          too_large at once. Order: highest --priority (default 0, or SDLC_GATE_PRIORITY) first, then FIFO by
          arrival; among the repos at the top priority, round robin after the repo granted last; the head keeps its
          turn until it fits (no backfill); a queued job is never preempted by a later one and a running job is
          never stopped by admission. Load cap: when policy.json has a top-level max_load (a whole number, set
          with `policy set max_load=N`; 0 is off; absent is max(1, int(0.8 * CPU count)), and `policy show` says
          `default from N CPUs` then), no new grant is admitted while a grant is held and the
          host's 1-minute load average (os.getloadavg) is above it; a load equal to it admits, with no grant held the head is admitted at any load (load from outside never starves the queue), a held grant is
          never stopped, the refused head keeps its round-robin turn, and a host that reports no load average
          is not capped. It is an absolute load, so pick load per CPU times the CPU count. SDLC_GATE_LOAD_FILE
          (tests only) names a file holding the load to use; SDLC_GATE_CPUS (tests only) is the CPU count.
          Node heap cap: a top-level `run` appends --max-old-space-size=<MB> to the command's NODE_OPTIONS unless
          NODE_OPTIONS already holds a --max-old-space-size, so one leaking test fails fast instead of taking the
          machine's memory, and prints one stderr line naming the cap. MB is the policy key node_heap_mb (`policy
          set node_heap_mb=N`; 0 is off; absent is 4096, and `policy show` says `built-in default`). A nested run
          inherits the flag; --slots 0 runs with no env change.
          A grant stays charged while its wrapper is alive with the recorded start
          identity or its process group has a member; a dead holder with no live group is reclaimed, a dead
          wrapper with a live group stays charged (an orphaned group). The command gets SDLC_GATE_GRANT,
          SDLC_GATE_WORKERS (the granted compute units), SDLC_GATE_DIR and SDLC_GATE_LOCK_HELD=1. A `run` inside
          a grant (SDLC_GATE_GRANT of a live grant, same process group) takes no queue turn and no new charge;
          an unknown or dead grant is bad_context; SDLC_GATE_LOCK_HELD=1 alone is a top-level request. --nice
          runs the command at nice 10. SIGTERM, SIGINT and SIGHUP while queued remove the entry (exit 128+sig,
          no child); while running the group is killed (SIGTERM, SIGKILL after 5 s) before release. After the
          command exits its group is drained the same way before the grant is released. Fewer than 1 slot
          (SDLC_GATE_SLOTS=0) runs the command with no admission and no env change. --receipt writes a JSON
          receipt last (outcome, rc, wait_ms, run_ms, cleanup_ms, total_ms).
  context   exit 0 and print the grant when the caller runs inside a valid grant, else exit 1.
  status    queued and admitted rows (name, pid, need, repo, priority, age); `no holders` when empty; legacy
            slot holders from older plugin versions are listed and called a partial protection. With max_load
            set, a queue that waits on the load ends with `waiting: load <n.n> over cap <N>`. --json for tools
            (it gains `load`: value, max_load, over, only when max_load is set).
  capabilities  read only: protocol, state root, boot id, the policy in force, legacy holders seen.
  policy / reset  operator only: show, set or reset policy.json; `reset --confirm` replaces an unparseable ledger.
  reap    lists leftover browser processes from finished runs and stops nothing: a process whose command line
          matches chrome-headless-shell, chromium, chrome for testing, playwright, or vite preview (case
          ignored), whose parent pid is 1 or no longer exists, and that has run at least --older-than minutes
          (default 30). A matching process with a live parent is never listed as stoppable and never stopped
          (a count of those is printed). --kill sends each listed pid SIGTERM, SIGKILL after 2 s, and prints
          each pid it stops; the process is checked again just before each signal. --match REGEX only narrows
          the set (the selftest uses it so it never touches a real process). Review the list first: a browser
          you started yourself from the desktop also has parent pid 1 and matches by name when it is Chromium.
          Admission never calls it.
  selftest  real child processes in a temp SDLC_GATE_DIR: weighted caps, FIFO, priority, liveness (a dead holder
          reclaimed, a live group not), nesting, cancel, timeout, reboot, corrupt ledger, receipts, status, the
          legacy bridge, the load cap and the old exit codes, each control observed failing in a mutant copy of this script;
          then the reap cases with a fake orphan and a live-parent fake.
"""
import argparse, contextlib, fcntl, json, os, pathlib, pwd, re, secrets, shlex, shutil, signal, struct, subprocess, sys, tempfile, time

PROTOCOL = 'sdlc-gate/2'
DEFAULT_TIMEOUT = 1800.0
POLL = 0.2
KILL_GRACE = 5.0
PID_SLACK = 5.0  # legacy slot files only: a live pid that started this much after the slot was taken is a reused pid
SLOT_RE = re.compile(r'slot-(\d+)$')
BUILTIN_POLICY = {'capacity': {'compute_units': 6, 'browser_jobs': 3}, 'default_need': {'compute_units': 3}}
DEFAULT_NODE_HEAP_MB = 4096
COMPUTE = 'compute_units'


class GateError(Exception):
    def __init__(self, code, detail):
        super().__init__(f'{code}: {detail}')
        self.code, self.detail = code, detail


# ---- processes: identity and liveness ------------------------------------------------------------------------

def parse_etime(text):
    """Seconds from ps's [[dd-]hh:]mm:ss."""
    days = 0
    if '-' in text:
        d, text = text.split('-', 1)
        days = int(d)
    nums = [int(x) for x in text.split(':')]
    while len(nums) < 3:
        nums.insert(0, 0)
    return ((days * 24 + nums[0]) * 60 + nums[1]) * 60 + nums[2]


def proc_start(pid):
    """Legacy and reap helper. None when pid is gone or a zombie; else its start time (epoch seconds), 0.0 when unknown."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except OSError:
        pass  # EPERM: it exists, another user owns it
    try:
        p = subprocess.run(['ps', '-o', 'stat=,etime=', '-p', str(pid)], capture_output=True, text=True, timeout=5)
        parts = p.stdout.split()
        if len(parts) >= 2 and parts[0].startswith('Z'):
            return None
        return time.time() - parse_etime(parts[1]) if len(parts) >= 2 else 0.0
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0.0


def legacy_alive(h):
    st = proc_start(h['pid'])
    if st is None:
        return False
    return not (st and h.get('start') and st > h['start'] + PID_SLACK)


_LIBPROC = []


def _darwin_ident(pid):
    """(is_zombie, identity) from proc_pidinfo(PROC_PIDTBSDINFO), or None when it cannot be read (the byte count is
    checked: pid 1 and other users' processes return 0)."""
    import ctypes
    if not _LIBPROC:
        try:
            _LIBPROC.append(ctypes.CDLL('/usr/lib/libproc.dylib'))
        except OSError:
            _LIBPROC.append(None)
    lib = _LIBPROC[0]
    if lib is None:
        return None
    buf = ctypes.create_string_buffer(136)
    if lib.proc_pidinfo(pid, 3, 0, buf, 136) != 136:
        return None
    status = struct.unpack_from('<I', buf.raw, 4)[0]
    sec, usec = struct.unpack_from('<QQ', buf.raw, 120)
    return status == 5, f'{sec}.{usec:06d}'


def _linux_ident(pid):
    try:
        text = pathlib.Path(f'/proc/{pid}/stat').read_text()
        rest = text[text.rindex(')') + 2:].split()
        return rest[0] == 'Z', rest[19]
    except (OSError, ValueError, IndexError):
        return None


def _ps_ident(pid):
    try:
        p = subprocess.run(['ps', '-o', 'stat=,lstart=', '-p', str(pid)], capture_output=True, text=True, timeout=5)
        parts = p.stdout.split(None, 1)
        if len(parts) == 2:
            return parts[0].startswith('Z'), ' '.join(parts[1].split())
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def pid_start(pid):
    """None when pid is gone or a zombie; '' when it is alive but its start identity cannot be read; else its exact
    start identity (compared for equality, never with slack)."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except OSError:
        pass  # EPERM: it exists
    got = None
    if sys.platform == 'darwin':
        got = _darwin_ident(pid)
    elif sys.platform.startswith('linux'):
        got = _linux_ident(pid)
    if got is None:
        got = _ps_ident(pid)
    if got is None:
        return ''
    return None if got[0] else got[1]


def alive(pid, start):
    cur = pid_start(pid)
    if cur is None:
        return False
    if start and cur and cur != start: return False  # IDENT
    return True  # an unreadable identity counts as alive


def group_alive(pgid):
    """True when the process group has any member of this user (EPERM is a zombie-only group on macOS)."""
    if not pgid:
        return False
    try:
        os.killpg(pgid, 0)
    except OSError:
        return False
    return True


def grant_live(g):
    wrapper = alive(g['pid'], g.get('pid_start'))
    return wrapper or group_alive(g.get('pgid'))  # GRANT-LIVE


_BOOT = []


def boot_id():
    if _BOOT:
        return _BOOT[0]
    out = ''
    try:
        if sys.platform == 'darwin':
            out = subprocess.run(['sysctl', '-n', 'kern.bootsessionuuid'], capture_output=True, text=True, timeout=5).stdout.strip()
        elif sys.platform.startswith('linux'):
            out = pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    except (OSError, subprocess.SubprocessError):
        out = ''
    _BOOT.append(out)
    return out


# ---- state root, ledger, policy ------------------------------------------------------------------------------

def state_root():
    env = os.environ.get('SDLC_GATE_DIR')
    if env:
        return pathlib.Path(env)
    try:
        home = pwd.getpwuid(os.getuid()).pw_dir
    except KeyError:
        raise GateError('state_unavailable', 'no home directory for this user in the password database')
    return pathlib.Path(home) / '.local' / 'state' / 'sdlc-lite' / 'gate-lock'


def empty_ledger():
    return {'protocol': PROTOCOL, 'boot': boot_id(), 'seq': 0, 'rr': '', 'grants': [], 'queue': []}


def load_ledger(root):
    path = root / 'ledger.json'
    try:
        text = path.read_text()
    except FileNotFoundError:
        return empty_ledger()
    except OSError as e:
        raise GateError('state_unavailable', f'cannot read {path}: {e.strerror or e}')
    try:
        d = json.loads(text)
        if not (isinstance(d, dict) and isinstance(d.get('grants'), list) and isinstance(d.get('queue'), list)
                and isinstance(d.get('seq'), int)):
            raise ValueError('wrong shape')
    except ValueError as e:
        raise GateError('ledger_corrupt', f'{path} does not parse ({e}); check that no gate runs, then gate_lock.py reset --confirm')
    if d.get('boot', '') != boot_id():
        return empty_ledger()  # a ledger from before a reboot: every entry in it is dead
    return d


def save_ledger(root, d):
    path = root / 'ledger.json'
    tmp = root / f'.ledger-{os.getpid()}.tmp'
    try:
        with open(tmp, 'w') as f:
            f.write(json.dumps(d, sort_keys=True))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except OSError as e:
        raise GateError('state_unavailable', f'cannot write {path}: {e.strerror or e}')


@contextlib.contextmanager
def mutex(root):
    try:
        root.mkdir(parents=True, exist_ok=True)
        mx = open(root / '.mutex', 'a')
    except OSError as e:
        raise GateError('state_unavailable', f'cannot use state root {root}: {e.strerror or e}')
    with mx:
        fcntl.flock(mx, fcntl.LOCK_EX)
        yield


@contextlib.contextmanager
def txn(root):
    """The ledger under the mutex; written back (atomically) only when the body changed it and did not raise."""
    with mutex(root):
        ledger = load_ledger(root)
        before = json.dumps(ledger, sort_keys=True)
        yield ledger
        if json.dumps(ledger, sort_keys=True) != before:
            save_ledger(root, ledger)


def read_ledger(root):
    """The ledger as saved, without creating anything; an absent state root reads as empty."""
    if not (root / 'ledger.json').exists():
        return empty_ledger()
    with mutex(root):
        return load_ledger(root)


def cpu_count():
    """The CPU count the default load cap derives from; SDLC_GATE_CPUS (tests only) replaces it."""
    try:
        return max(1, int(os.environ['SDLC_GATE_CPUS']))
    except (KeyError, ValueError):
        return os.cpu_count() or 1


def set_default_max_load(pol):
    """A policy with no max_load key caps admission at 0.8 x the CPU count; max_load_default says where it came from."""
    if 'max_load' not in pol:
        n = cpu_count()
        pol['max_load'] = max(1, int(0.8 * n))  # LOAD-DEFAULT
        pol['max_load_default'] = f'default from {n} CPUs'


def set_default_node_heap(pol):
    """A policy with no node_heap_mb key caps the Node heap of a gate at 4096 MB; node_heap_mb_default says where it came from."""
    if 'node_heap_mb' not in pol:
        pol['node_heap_mb'] = DEFAULT_NODE_HEAP_MB
        pol['node_heap_mb_default'] = 'built-in default'


def load_policy(root):
    """(policy, source): built-in numbers, each key replaced by policy.json's when present."""
    pol = {k: dict(v) for k, v in BUILTIN_POLICY.items()}
    path = root / 'policy.json'
    if not path.exists():
        set_default_max_load(pol)
        set_default_node_heap(pol)
        return pol, 'builtin'
    try:
        d = json.loads(path.read_text())
        if not isinstance(d, dict):
            raise ValueError('not an object')
        for key in ('capacity', 'default_need'):
            if key in d:
                if not (isinstance(d[key], dict) and all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in d[key].values())):
                    raise ValueError(f'{key} must map resources to whole numbers')
                pol[key] = dict(d[key])
        if 'max_load' in d:
            if not (isinstance(d['max_load'], int) and not isinstance(d['max_load'], bool) and d['max_load'] >= 0):
                raise ValueError('max_load must be a whole number')
            pol['max_load'] = d['max_load']  # 0 is off, kept so a later `policy set` does not bring the default back
        if 'node_heap_mb' in d:
            if not (isinstance(d['node_heap_mb'], int) and not isinstance(d['node_heap_mb'], bool) and d['node_heap_mb'] >= 0):
                raise ValueError('node_heap_mb must be a whole number')
            pol['node_heap_mb'] = d['node_heap_mb']  # 0 is off
    except (OSError, ValueError) as e:
        raise GateError('state_unavailable', f'{path} is not a usable policy: {e}')
    set_default_max_load(pol)
    set_default_node_heap(pol)
    return pol, 'file'


def parse_needs(text):
    out = {}
    for part in (text or '').split(','):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*)=(\d+)', part)
        if not m:
            raise ValueError(f'{part!r} is not RES=N')
        out[m.group(1)] = int(m.group(2))
    return out


def compute_base(pol):
    return pol['capacity'].get(COMPUTE) or (os.cpu_count() or 1)


def default_need(pol):
    need = dict(pol['default_need'])
    if COMPUTE not in need:
        need[COMPUTE] = max(1, compute_base(pol) // 2)
    return need


def build_need(pol, explicit, slots):
    need = default_need(pol)
    if slots is not None and slots >= 1:
        need[COMPUTE] = max(1, compute_base(pol) // slots)
    need.update(explicit)
    return need


def check_size(pol, need):
    for r, n in need.items():
        c = pol['capacity'].get(r)
        if c is not None and n > c:
            raise GateError('too_large', f'need {r}={n} is above the capacity {c}')


def fits(usage, need, cap):
    for r, n in need.items():
        c = cap.get(r)
        if c is None:
            continue  # a resource the policy does not cap is recorded and not charged
        if usage.get(r, 0) + n > c: return False  # SLOT-CAP
    return True


def add_usage(usage, need):
    for r, n in need.items():
        usage[r] = usage.get(r, 0) + n


def order_key(e): return (-e['priority'], e['seq'])  # QUEUE-ORDER


def host_load():
    """The host's 1-minute load average, or None when the host does not report one (the load cap is then not
    applied). SDLC_GATE_LOAD_FILE (tests only) names a file holding the number to use instead."""
    path = os.environ.get('SDLC_GATE_LOAD_FILE')
    if path:
        try:
            return float(pathlib.Path(path).read_text().strip())
        except (OSError, ValueError):
            pass
    try:
        return os.getloadavg()[0]
    except (OSError, AttributeError):
        return None


def schedule(ledger, pol, legacy_n=0, load=None):
    """Grant queue heads while they fit: highest priority first, then arrival; among the repos at the top priority
    round robin after the repo granted last; the selected head keeps its turn until it fits (no backfill). With a
    max_load in the policy, nothing more is granted while the load (read once per call when not given) is above it
    and a grant is held; with none held the head is admitted at any load, so load from outside never starves the queue."""
    cap, usage = pol['capacity'], {}
    max_load = pol.get('max_load')
    if max_load and load is None:
        load = host_load()
    for g in ledger['grants']:
        add_usage(usage, g['need'])
    for _ in range(legacy_n):
        add_usage(usage, default_need(pol))
    granted = []
    while ledger['queue']:
        heads, first = {}, {}
        for e in sorted(ledger['queue'], key=order_key):
            heads.setdefault(e['repo'], e)
        for e in ledger['queue']:
            first[e['repo']] = min(first.get(e['repo'], e['seq']), e['seq'])
        top = min(order_key(h)[0] for h in heads.values())
        cl = sorted((r for r, h in heads.items() if order_key(h)[0] == top), key=lambda r: first[r])
        if ledger.get('rr') in cl:
            i = cl.index(ledger['rr']) + 1
            cl = cl[i:] + cl[:i]
        entry = heads[cl[0]]
        if max_load and load is not None and load > max_load and (ledger['grants'] or legacy_n): break  # LOAD-CAP
        if not fits(usage, entry['need'], cap):
            break
        ledger['queue'].remove(entry)
        entry['granted_at'] = time.time()
        ledger['grants'].append(entry)
        ledger['rr'] = entry['repo']
        add_usage(usage, entry['need'])
        granted.append(entry['id'])
    return granted


def prune(ledger):
    ledger['queue'] = [e for e in ledger['queue'] if alive(e['pid'], e.get('pid_start'))]
    ledger['grants'] = [g for g in ledger['grants'] if grant_live(g)]


def legacy_holders():
    """Live slot files written by older plugin versions, read only (never deleted, stolen or signalled)."""
    dirs = [pathlib.Path(os.environ.get('TMPDIR') or '/tmp') / 'sdlc-gate-locks']
    if not os.environ.get('SDLC_GATE_DIR'):
        dirs.append(pathlib.Path('/tmp/sdlc-gate-locks'))
    seen, out = set(), []
    for d in dirs:
        try:
            real = d.resolve()
            paths = sorted(real.glob('slot-*'))
        except OSError:
            continue
        if real in seen:
            continue
        seen.add(real)
        for path in paths:
            try:
                h = json.loads(path.read_text())
            except (OSError, ValueError):
                continue
            if isinstance(h, dict) and isinstance(h.get('pid'), int) and legacy_alive(h):
                out.append({'dir': str(real), 'slot': path.name, 'pid': h['pid'], 'name': h.get('name', '?'), 'start': h.get('start', 0)})
    return out


def repo_identity(cwd, override=None):
    if override:
        return os.path.realpath(override)
    try:
        p = subprocess.run(['git', 'rev-parse', '--git-common-dir'], cwd=cwd, capture_output=True, text=True, timeout=10)
        if p.returncode == 0 and p.stdout.strip():
            return os.path.realpath(os.path.join(cwd, p.stdout.strip()))
    except (OSError, subprocess.SubprocessError):
        pass
    return os.path.realpath(cwd)


def need_text(need):
    return ','.join(f'{k}={v}' for k, v in sorted(need.items())) or 'none'


def holders_text(ledger):
    now, out = time.time(), []
    for g in sorted(ledger['grants'], key=lambda g: g['seq']):
        out.append(f"pid {g['pid']} name {g.get('name', '?')} need {need_text(g['need'])} age {int(now - g.get('granted_at', now))}s")
    return '; '.join(out) or 'no holders'


def queue_view(ledger):
    return sorted(ledger['queue'], key=order_key)


# ---- run ------------------------------------------------------------------------------------------------------

class Stop(Exception):
    def __init__(self, sig):
        super().__init__(sig)
        self.sig = sig


def on_signal(sig, frame):
    raise Stop(sig)


def drain_group(pgid, child=None):
    """SIGTERM the group, SIGKILL after KILL_GRACE, until killpg(pgid, 0) reports no member."""
    def settle(secs):
        end = time.time() + secs
        while time.time() < end:
            if child is not None:
                child.poll()
            if not group_alive(pgid):
                return True
            time.sleep(0.05)
        if child is not None:
            child.poll()
        return not group_alive(pgid)
    if child is not None:
        child.poll()
    if not group_alive(pgid):
        return
    for sig, wait in ((signal.SIGTERM, KILL_GRACE), (signal.SIGKILL, KILL_GRACE)):
        try:
            os.killpg(pgid, sig)
        except OSError:
            pass
        if settle(wait):
            return


def write_receipt(path, d):
    if not path:
        return
    try:
        pathlib.Path(path).write_text(json.dumps(d, sort_keys=True))
    except OSError as e:
        print(f'gate_lock: cannot write receipt {path}: {e.strerror or e}', file=sys.stderr)


def validate_grant(root, gid):
    """The live grant with this id whose process group is the caller's, else GateError bad_context."""
    with txn(root) as L:
        g = next((g for g in L['grants'] if g['id'] == gid), None)
        if g is None or not grant_live(g):
            raise GateError('bad_context', f'SDLC_GATE_GRANT {gid} is unknown or no longer live')
        if g.get('pgid') != os.getpgrp():
            raise GateError('bad_context', f'SDLC_GATE_GRANT {gid} belongs to another process group')
        return dict(g)


def apply_heap_cap(env, pol):
    """Append --max-old-space-size=<node_heap_mb> to NODE_OPTIONS unless it holds one or the policy turns the cap off."""
    mb = pol.get('node_heap_mb') or 0
    opts = env.get('NODE_OPTIONS', '')
    if mb < 1 or re.search(r'--max[-_]old[-_]space[-_]size', opts):
        return
    env['NODE_OPTIONS'] = (opts + f' --max-old-space-size={mb}').strip()  # HEAP-CAP
    print(f'gate_lock: node heap capped at {mb} MB (NODE_OPTIONS --max-old-space-size={mb}; policy node_heap_mb, 0 is off)',
          file=sys.stderr, flush=True)


def start_child(cmd, env, nice, new_session):
    return subprocess.Popen(cmd, env=env, start_new_session=new_session,
                            preexec_fn=(lambda: os.nice(10)) if nice else None)


def run_nested(root, pol, gid, need, nice, cmd, receipt, name, t0):
    """A run inside a valid grant: same process group, no queue turn, no new charge."""
    g = validate_grant(root, gid)
    for r, n in need.items():
        if pol['capacity'].get(r) is not None and n > g['need'].get(r, 0):
            raise GateError('too_large', f'need {r}={n} is above the enclosing grant {g["need"].get(r, 0)}')
    env = dict(os.environ)
    env['SDLC_GATE_WORKERS'] = str(min(need.get(COMPUTE, 1), g['need'].get(COMPUTE, need.get(COMPUTE, 1))))
    env['SDLC_GATE_LOCK_HELD'] = '1'
    child, rc, outcome = None, 1, 'ok'
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)
    t_run = time.monotonic()
    try:
        child = start_child(cmd, env, nice, False)
        rc = child.wait()
        rc = 128 - rc if rc < 0 else rc
        outcome = 'signal' if rc > 128 else 'ok' if rc == 0 else 'child_failed'
    except Stop as stop:
        rc, outcome = 128 + stop.sig, 'signal'
    except OSError as e:
        print(f'gate_lock: cannot run {cmd[0]}: {e.strerror or e}', file=sys.stderr)
        rc, outcome = (127 if isinstance(e, FileNotFoundError) else 126), 'spawn_failed'
    finally:
        for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(s, signal.SIG_IGN)
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(KILL_GRACE)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    now = time.monotonic()
    write_receipt(receipt, {'protocol': PROTOCOL, 'grant': gid, 'name': name, 'nested': True, 'need': need, 'outcome': outcome, 'rc': rc,
                            'wait_ms': 0, 'run_ms': int((now - t_run) * 1000), 'cleanup_ms': 0, 'total_ms': int((now - t0) * 1000)})
    return rc


def run(slots, name, nice, timeout, cmd, explicit_need=None, priority=0, repo_arg=None, receipt=None):
    t0 = time.monotonic()
    bare = slots is not None and slots < 1
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)
    if bare:
        return run_bare(name, nice, cmd, receipt, t0)
    try:
        root = state_root()
        pol, _ = load_policy(root)
        need = build_need(pol, explicit_need or {}, slots)
        check_size(pol, need)
        gid_env = os.environ.get('SDLC_GATE_GRANT')
        if gid_env:
            return run_nested(root, pol, gid_env, need, nice, cmd, receipt, name, t0)
        return run_top(root, pol, need, name, nice, timeout, cmd, priority, repo_arg, receipt, t0)
    except GateError as e:
        print(f'gate_lock: {e.code}: {e.detail}', file=sys.stderr)
        write_receipt(receipt, {'protocol': PROTOCOL, 'grant': None, 'name': name, 'outcome': e.code, 'rc': 3, 'wait_ms': 0, 'run_ms': None,
                                'cleanup_ms': 0, 'total_ms': int((time.monotonic() - t0) * 1000)})
        return 3
    except Stop as stop:
        return 128 + stop.sig


def run_bare(name, nice, cmd, receipt, t0):
    child, rc, outcome = None, 1, 'ok'
    try:
        child = start_child(cmd, dict(os.environ), nice, True)
        rc = child.wait()
        rc = 128 - rc if rc < 0 else rc
        outcome = 'signal' if rc > 128 else 'ok' if rc == 0 else 'child_failed'
    except Stop as stop:
        rc, outcome = 128 + stop.sig, 'signal'
    except OSError as e:
        print(f'gate_lock: cannot run {cmd[0]}: {e.strerror or e}', file=sys.stderr)
        rc, outcome = (127 if isinstance(e, FileNotFoundError) else 126), 'spawn_failed'
    finally:
        for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(s, signal.SIG_IGN)
        if child is not None and child.poll() is None:
            drain_group(child.pid, child)
            child.wait()
    write_receipt(receipt, {'protocol': PROTOCOL, 'grant': None, 'name': name, 'outcome': outcome, 'rc': rc, 'wait_ms': 0,
                            'run_ms': int((time.monotonic() - t0) * 1000), 'cleanup_ms': 0, 'total_ms': int((time.monotonic() - t0) * 1000)})
    return rc


def run_top(root, pol, need, name, nice, timeout, cmd, priority, repo_arg, receipt, t0):
    legacy_n = len(legacy_holders())
    me = {'id': secrets.token_hex(16), 'repo': repo_identity(os.getcwd(), repo_arg), 'name': name, 'cmd': ' '.join(cmd)[:200], 'need': need,
          'priority': priority, 'pid': os.getpid(), 'pid_start': pid_start(os.getpid()) or '', 'pgid': None, 'enqueued_at': time.time()}
    gid, child, rc, outcome, pgid = me['id'], None, 1, 'ok', None
    t_grant = t_run = t_exit = None
    env = dict(os.environ)
    report = float(os.environ.get('SDLC_GATE_REPORT_SECS') or 15)
    try:
        with txn(root) as L:
            prune(L)
            L['seq'] += 1
            me['seq'] = L['seq']
            L['queue'].append(me)
            schedule(L, pol, legacy_n)
        next_report, last_legacy = t0 + report, time.monotonic()
        while True:
            try:
                pol, _ = load_policy(root)  # a capacity set by `policy set` after this run queued reaches it
            except GateError:
                pass  # keep the last good policy for this poll
            with txn(root) as L:
                prune(L)
                schedule(L, pol, legacy_n)
                mine = next((g for g in L['grants'] if g['id'] == gid), None)
                if mine is None:
                    qs = queue_view(L)
                    pos = next((i + 1 for i, e in enumerate(qs) if e['id'] == gid), None)
                    holders = holders_text(L)
                    nqueue = len(qs)
            if mine is not None:
                break
            now = time.monotonic()
            if pos is None:
                raise GateError('state_unavailable', 'this run\'s queue entry was removed from the ledger')
            if now >= t0 + timeout:
                outcome = 'timeout'
                raise GateError('timeout', f'after {timeout:g}s waiting for a grant of {need_text(need)} ({holders})')
            if now >= next_report:
                print(f'gate_lock: {name} waiting for a slot, position {pos} of {nqueue} (need {need_text(need)}, {int(now - t0)}s so far); '
                      f'admitted: {holders}', file=sys.stderr, flush=True)
                next_report = now + report
            if now - last_legacy > 5:
                legacy_n, last_legacy = len(legacy_holders()), now
            time.sleep(min(POLL, max(0.01, t0 + timeout - now)))
        t_grant = time.monotonic()
        if t_grant - t0 >= report:
            print(f'gate_lock: {name} got a slot after {int(t_grant - t0)}s', file=sys.stderr, flush=True)
        env['SDLC_GATE_GRANT'] = gid
        env['SDLC_GATE_WORKERS'] = str(need.get(COMPUTE, 1))
        env['SDLC_GATE_DIR'] = str(root)
        env['SDLC_GATE_LOCK_HELD'] = '1'
        apply_heap_cap(env, pol)
        t_run = time.monotonic()
        child = start_child(cmd, env, nice, True)
        pgid = child.pid
        with txn(root) as L:
            g = next((g for g in L['grants'] if g['id'] == gid), None)
            if g is not None:
                g['pgid'] = pgid
        rc = child.wait()
        t_exit = time.monotonic()
        rc = 128 - rc if rc < 0 else rc
        outcome = 'signal' if rc > 128 else 'ok' if rc == 0 else 'child_failed'
    except Stop as stop:
        rc, outcome = 128 + stop.sig, 'signal'
    except OSError as e:
        print(f'gate_lock: cannot run {cmd[0]}: {e.strerror or e}', file=sys.stderr)
        rc, outcome = (127 if isinstance(e, FileNotFoundError) else 126), 'spawn_failed'
    except GateError as e:
        outcome, rc = e.code, 3
        print(f'gate_lock: {e.code}: {e.detail}' if e.code != 'timeout' else f'gate_lock: timeout {e.detail}', file=sys.stderr)
    finally:
        for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(s, signal.SIG_IGN)
        if t_exit is None and t_run is not None:
            t_exit = time.monotonic()
        if child is not None:
            drain_group(pgid, child)  # DRAIN
            child.wait()
        try:
            with txn(root) as L:
                L['queue'] = [e for e in L['queue'] if e['id'] != gid]
                L['grants'] = [g for g in L['grants'] if g['id'] != gid]
                prune(L)
                schedule(L, pol, legacy_n)
        except GateError as e:
            print(f'gate_lock: {e.code}: {e.detail}', file=sys.stderr)
            if outcome == 'ok':
                outcome, rc = e.code, 3
    t_end = time.monotonic()
    write_receipt(receipt, {'protocol': PROTOCOL, 'grant': gid if t_grant else None, 'name': name, 'repo': me['repo'], 'need': need,
                            'outcome': outcome, 'rc': rc, 'wait_ms': int(((t_grant or t_end) - t0) * 1000),
                            'run_ms': int((t_exit - t_run) * 1000) if t_run is not None and t_exit is not None else None,
                            'cleanup_ms': int((t_end - (t_exit or t_end)) * 1000), 'total_ms': int((t_end - t0) * 1000),
                            'enqueued_at': me['enqueued_at']})
    return rc


# ---- read-only and operator commands -------------------------------------------------------------------------

def status_data(root):
    L = read_ledger(root)
    now = time.time()
    grants = []
    for g in sorted(L['grants'], key=lambda g: g['seq']):
        wrapper = alive(g['pid'], g.get('pid_start'))
        group = group_alive(g.get('pgid'))
        state = 'admitted' if wrapper else 'orphaned_group' if group else 'dead'
        grants.append({'state': state, 'id': g['id'], 'name': g.get('name', '?'), 'pid': g['pid'], 'pgid': g.get('pgid'), 'need': g['need'],
                       'repo': g['repo'], 'priority': g.get('priority', 0), 'age_s': int(now - g.get('granted_at', now))})
    queue = []
    held = sum(g['need'].get(COMPUTE, 0) for g in L['grants'])
    holders = [g.get('name', '?') for g in sorted(L['grants'], key=lambda g: g['seq'])]
    ahead = held
    for i, e in enumerate(queue_view(L)):
        queue.append({'state': 'queued' if alive(e['pid'], e.get('pid_start')) else 'dead', 'position': i + 1, 'id': e['id'],
                      'name': e.get('name', '?'), 'pid': e['pid'], 'need': e['need'], 'repo': e['repo'], 'priority': e['priority'],
                      'waited_s': int(now - e.get('enqueued_at', now)), 'ahead': ahead, 'blocking': holders})
        ahead += e['need'].get(COMPUTE, 0)
    d = {'protocol': PROTOCOL, 'state_root': str(root), 'boot': L.get('boot', ''), 'grants': grants, 'queue': queue, 'legacy': legacy_holders()}
    try:
        max_load = load_policy(root)[0].get('max_load')
    except GateError:
        max_load = None  # a policy that does not load gives no load fact and never fails status
    if max_load:
        load = host_load()
        d['load'] = {'value': load, 'max_load': max_load,
                     'over': load is not None and load > max_load and bool(grants or d['legacy'])}
    return d


def cmd_status(argv):
    as_json = '--json' in argv
    try:
        root = state_root()
        d = status_data(root)
    except GateError as e:
        print(f'gate_lock: {e.code}: {e.detail}', file=sys.stderr)
        return 3
    if as_json:
        print(json.dumps(d, indent=1, sort_keys=True))
        return 0
    rows = []
    for g in d['grants']:
        note = {'admitted': '', 'orphaned_group': '  (orphaned group: wrapper dead, still charged)', 'dead': '  (dead: will be reclaimed)'}[g['state']]
        rows.append(f"{'admitted' if g['state'] != 'dead' else 'dead':<9} name {g['name']}  pid {g['pid']}  need {need_text(g['need'])}  "
                    f"repo {os.path.basename(g['repo'])}  priority {g['priority']}  age {g['age_s']}s{note}")
    for q in d['queue']:
        rows.append(f"{'queued' if q['state'] == 'queued' else 'dead':<9} name {q['name']}  pid {q['pid']}  #{q['position']}  need {need_text(q['need'])}  "
                    f"repo {os.path.basename(q['repo'])}  priority {q['priority']}  age {q['waited_s']}s  "
                    f"ahead {q['ahead']}  blocking {','.join(q['blocking']) or 'none'}")
    if d['queue'] and d.get('load', {}).get('over'):
        rows.append(f"waiting: load {d['load']['value']:.1f} over cap {d['load']['max_load']}")
    for h in d['legacy']:
        rows.append(f"legacy    name {h['name']}  pid {h['pid']}  {h['slot']} in {h['dir']} (charged the default need; never touched)")
    if d['legacy']:
        rows.append('protection is partial: legacy holders from an older plugin version are running')
    print('\n'.join(rows) or 'no holders')
    return 0


def cmd_context(argv):
    gid = os.environ.get('SDLC_GATE_GRANT')
    if not gid:
        return 1
    try:
        g = validate_grant(state_root(), gid)
    except GateError:
        return 1
    d = {'id': g['id'], 'name': g.get('name'), 'need': g['need'], 'repo': g['repo'], 'SDLC_GATE_WORKERS': os.environ.get('SDLC_GATE_WORKERS') or str(g['need'].get(COMPUTE, 1))}
    if '--json' in argv:
        print(json.dumps(d))
    else:
        print(f"grant {d['id']} name {d['name']} need {need_text(d['need'])} repo {d['repo']} workers {d['SDLC_GATE_WORKERS']}")
    return 0


def cmd_capabilities(argv):
    try:
        root = state_root()
        pol, src = load_policy(root)
    except GateError as e:
        print(f'gate_lock: {e.code}: {e.detail}', file=sys.stderr)
        return 3
    d = {'protocol': PROTOCOL, 'state_root': str(root), 'boot': boot_id(), 'policy': {'source': src, **pol},
         'resources': sorted(set(pol['capacity']) | set(pol['default_need'])), 'legacy_holders': len(legacy_holders())}
    print(json.dumps(d, indent=1, sort_keys=True))
    return 0


def cmd_policy(argv):
    try:
        root = state_root()
        sub = argv[0] if argv else ''
        if sub == 'show':
            pol, src = load_policy(root)
            print(json.dumps({'source': src, **pol}, indent=1, sort_keys=True))
            return 0
        if sub == 'reset':
            with mutex(root):
                try:
                    (root / 'policy.json').unlink()
                except FileNotFoundError:
                    pass
            print('policy reset to the built-in numbers')
            return 0
        if sub == 'set':
            rest, default_at = argv[1:], None
            if '--default' in rest:
                default_at = rest.index('--default')
            cap_args = rest[:default_at] if default_at is not None else rest
            def_args = rest[default_at + 1:] if default_at is not None else []
            try:
                caps, defs = parse_needs(','.join(cap_args)), parse_needs(','.join(def_args))
            except ValueError as e:
                print(f'gate_lock.py policy set: {e}', file=sys.stderr)
                return 2
            max_load = caps.pop('max_load', None)  # a top-level key, never a capacity; 0 turns it off
            node_heap = caps.pop('node_heap_mb', None)  # likewise; 0 turns the heap cap off
            if not caps and not defs and max_load is None and node_heap is None:
                print('usage: gate_lock.py policy set [RES=N...] [max_load=N] [node_heap_mb=N] [--default RES=N...]', file=sys.stderr)
                return 2
            if any(v < 1 for v in caps.values()):
                print('gate_lock.py policy set: a capacity must be 1 or more', file=sys.stderr)
                return 2
            with mutex(root):
                pol, _ = load_policy(root)
                if 'max_load_default' in pol:  # the default is derived at load time, never written into the file
                    pol.pop('max_load'), pol.pop('max_load_default')
                if 'node_heap_mb_default' in pol:  # likewise derived at load time
                    pol.pop('node_heap_mb'), pol.pop('node_heap_mb_default')
                pol['capacity'].update(caps)
                pol['default_need'].update(defs)
                if max_load is not None:
                    pol['max_load'] = max_load  # 0 is written: it turns the default cap off
                if node_heap is not None:
                    pol['node_heap_mb'] = node_heap  # 0 is written: it turns the heap cap off
                tmp = root / f'.policy-{os.getpid()}.tmp'
                tmp.write_text(json.dumps(pol, sort_keys=True))
                os.replace(tmp, root / 'policy.json')
            print(f'policy set: capacity {need_text(pol["capacity"])}; default need {need_text(pol["default_need"])}'
                  + (f'; max load {pol["max_load"]}' if pol.get('max_load') else '')
                  + (f'; node heap {pol["node_heap_mb"]} MB' if pol.get('node_heap_mb') else ''))
            return 0
    except GateError as e:
        print(f'gate_lock: {e.code}: {e.detail}', file=sys.stderr)
        return 3
    print('usage: gate_lock.py policy show | set [RES=N...] [max_load=N] [node_heap_mb=N] [--default RES=N...] | reset', file=sys.stderr)
    return 2


def cmd_reset(argv):
    if '--confirm' not in argv:
        print('usage: gate_lock.py reset --confirm (operator only: replaces an unparseable ledger after you checked that no gate runs)', file=sys.stderr)
        return 2
    try:
        root = state_root()
        with mutex(root):
            try:
                load_ledger(root)
                print('gate_lock: reset refused: the ledger parses', file=sys.stderr)
                return 2
            except GateError as e:
                if e.code != 'ledger_corrupt':
                    raise
            keep = root / f'ledger.json.corrupt-{int(time.time())}'
            os.replace(root / 'ledger.json', keep)
            save_ledger(root, empty_ledger())
            print(f'ledger replaced with an empty one; the old file is {keep}')
            return 0
    except GateError as e:
        print(f'gate_lock: {e.code}: {e.detail}', file=sys.stderr)
        return 3


REAP_RE = re.compile(r'chrome-headless-shell|chromium|chrome[ -]for[ -]testing|playwright|vite(?:\.js)?\s+preview', re.I)
REAP_AGE_MIN = 30.0
REAP_TERM_WAIT = 2.0


def ps_rows():
    """Every process as (pid, ppid, age seconds, command line) from ps; [] when ps cannot run."""
    try:
        p = subprocess.run(['ps', '-axww', '-o', 'pid=,ppid=,etime=,command='], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return []
    rows = []
    for line in p.stdout.splitlines():
        parts = line.split(None, 3)
        try:
            if len(parts) == 4:
                rows.append((int(parts[0]), int(parts[1]), parse_etime(parts[2]), parts[3].strip()))
        except ValueError:
            continue
    return rows


def is_orphan(ppid):
    return ppid == 1 or proc_start(ppid) is None  # PARENT-CHECK


def leftovers(older_than_min, only=None):
    """(orphans, live): the matching processes with no live parent that are old enough, as ps rows, and how many
    matching processes were skipped because their parent is alive."""
    me, orphans, live = os.getpid(), [], 0
    for row in ps_rows():
        pid, ppid, age, cmd = row
        if pid == me or not REAP_RE.search(cmd) or (only and not only.search(cmd)):
            continue
        if not is_orphan(ppid):
            live += 1
        elif age >= older_than_min * 60:
            orphans.append(row)
    return orphans, live


def fmt_age(sec):
    return f'{sec}s' if sec < 60 else f'{sec // 60}m' if sec < 3600 else f'{sec // 3600}h{sec % 3600 // 60:02d}m'


def reap_stop(pid, cmd):
    """SIGTERM, SIGKILL after REAP_TERM_WAIT. Returns 'TERM', 'KILL', 'gone' (already exited or no longer the
    same orphan), or an error text."""
    def same():
        r = next((r for r in ps_rows() if r[0] == pid), None)
        return r is not None and r[3] == cmd and is_orphan(r[1])
    try:
        if not same():
            return 'gone'
        os.kill(pid, signal.SIGTERM)
        end = time.time() + REAP_TERM_WAIT
        while time.time() < end and proc_start(pid) is not None:
            time.sleep(0.05)
        if proc_start(pid) is None:
            return 'TERM'
        if not same():
            return 'gone'
        os.kill(pid, signal.SIGKILL)
        return 'KILL'
    except ProcessLookupError:
        return 'gone'
    except OSError as e:
        return f'not stopped: {e.strerror or e}'


def cmd_reap(argv):
    ap = argparse.ArgumentParser(prog='gate_lock.py reap', description='list (and with --kill stop) orphaned browser processes')
    ap.add_argument('--older-than', type=float, default=REAP_AGE_MIN, metavar='MIN', help=f'minimum age in minutes (default {REAP_AGE_MIN:g})')
    ap.add_argument('--kill', action='store_true', help='SIGTERM, then SIGKILL after 2 s, each listed pid (default: list only)')
    ap.add_argument('--match', metavar='REGEX', help='also require this regex to match the command line (only narrows)')
    a = ap.parse_args(argv)
    if a.older_than < 0:
        ap.error('--older-than must not be negative')
    try:
        only = re.compile(a.match) if a.match else None
    except re.error as e:
        ap.error(f'--match: {e}')
    orphans, live = leftovers(a.older_than, only)
    for pid, ppid, age, cmd in sorted(orphans):
        print(f'pid {pid}  age {fmt_age(age)}  parent {ppid}  {cmd[:200]}')
    if live:
        print(f'{live} matching process(es) with a live parent skipped')
    if not orphans:
        print(f'no leftover browser processes older than {a.older_than:g} min')
        return 0
    if not a.kill:
        print(f'{len(orphans)} leftover process(es); nothing stopped (rerun with --kill to stop them)')
        return 0
    failed = 0
    for pid, ppid, age, cmd in sorted(orphans):
        r = reap_stop(pid, cmd)
        if r in ('TERM', 'KILL'):
            print(f'stopped pid {pid} ({r})')
        else:
            print(f'pid {pid} {r}', file=sys.stdout if r == 'gone' else sys.stderr)
            failed += r != 'gone'
    return 1 if failed else 0


# ---- selftest ---------------------------------------------------------------------------------------------

HOLD = 'touch "$GL_M/started-$GL_N"; until test -e "$GL_M/go-$GL_N"; do sleep 0.05; done'
# markers the mutant copies edit; each is joined so the selftest's own text does not contain the marked line
M_CAP = 'if usage.get(r, 0) + n > c: return False' + '  # SLOT-CAP'
M_ORDER = "return (-e['priority'], e['seq'])" + '  # QUEUE-ORDER'
M_LIVE = "return wrapper or group_alive(g.get('pgid'))" + '  # GRANT-LIVE'
M_IDENT = 'if start and cur and cur != start: return False' + '  # IDENT'
M_DRAIN = 'drain_group(pgid, child)' + '  # DRAIN'
M_LOADDEF = "pol['max_load'] = max(1, int(0.8 * n))" + '  # LOAD-DEFAULT'
M_HEAP = "env['NODE_OPTIONS'] = (opts + f' --max-old-space-size={mb}').strip()" + '  # HEAP-CAP'
M_LOAD = "if max_load and load is not None and load > max_load and (ledger['grants'] or legacy_n): break" + '  # LOAD-CAP'
# the reap fakes: a python that records its pid and sleeps, its last argument the name that makes it match;
# the orphaner double forks it so its parent is pid 1 and its own command line carries no matching name
REAP_FAKE = "import os,time; open(os.environ['GL_PIDFILE'],'w').write(str(os.getpid())); time.sleep(300)"
REAP_ORPHANER = ("import os,sys\n"
                 "if os.fork() == 0:\n"
                 "    os.setsid()\n"
                 "    if os.fork() == 0:\n"
                 "        os.execv(sys.executable, [sys.executable, '-c', sys.argv[1], os.environ['GL_NAME']])\n"
                 "    os._exit(0)\n"
                 "os._exit(0)")


def waitfor(pred, secs=15):
    end = time.time() + secs
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.05)
    return pred()


_ISO = {'issued': [], 'watch': [], 'hits': [], 'hooked': False}  # the selftest's own isolation record


def _iso_hook(event, args):
    """Audit hook: while armed, an open for writing under a watched (real) state root is recorded."""
    if event != 'open' or not _ISO['watch']:
        return
    path, mode, flags = (list(args) + [None, None])[:3]
    if not isinstance(path, (str, bytes, os.PathLike)):
        return
    path = os.fsdecode(path)
    writes = (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC)) or \
             (isinstance(mode, str) and any(c in mode for c in 'wax+'))
    if writes and any(path == w or path.startswith(w.rstrip(os.sep) + os.sep) for w in _ISO['watch']):
        _ISO['hits'].append(path)


def iso_misses(base, real_root, issued, hits):
    """What the selftest itself could have done to the real state root: handed a case a state root outside its own
    temp dir (or the real root, or none), or opened a file under the real root for writing in this process."""
    out = []
    real = str(real_root.resolve())
    for r in issued:
        if not r:
            out.append('a case ran with no private SDLC_GATE_DIR')
            continue
        rp = str(pathlib.Path(r).resolve())
        if rp == real or rp.startswith(real + os.sep):
            out.append(f'a case was given the real state root {rp}')
        elif not (rp == str(base) or rp.startswith(str(base) + os.sep)):
            out.append(f'a case was given a state root outside the selftest temp dir: {rp}')
    out.extend(f'the selftest opened {h} for writing' for h in hits)
    return out


def env_for(base, label, **extra):
    """A clean environment with a private state root and TMPDIR (the legacy dir), so no selftest case touches the real namespace."""
    tm = base / f'tmp-{label}'
    tm.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith('SDLC_GATE_')}
    env['TMPDIR'] = str(tm)
    env['SDLC_GATE_DIR'] = str(base / f'state-{label}')
    quiet = base / f'load0-{label}'  # the default load cap must not hold a case back on a busy host
    quiet.write_text('0\n')
    env['SDLC_GATE_LOAD_FILE'] = str(quiet)
    env.update(extra)
    _ISO['issued'].append(env.get('SDLC_GATE_DIR'))
    return env


def gl(py, env, *args, timeout=60, **kw):
    _ISO['issued'].append(env.get('SDLC_GATE_DIR'))
    return subprocess.run([sys.executable, str(py), *args], env=env, capture_output=True, text=True, timeout=timeout, **kw)


def holder(py, env, m, n, *args):
    """A gate_lock run whose command holds its grant until <m>/go-<n> exists; stderr goes to <m>/err-<n>, the command's pid
    (also its process group) to <m>/pid-<n>."""
    return subprocess.Popen([sys.executable, str(py), 'run', '--name', f'H{n}', '--timeout', '60', *args, '--', 'sh', '-c',
                             'echo $$ >"$GL_M/pid-$GL_N"; ' + HOLD],
                            env=dict(env, GL_M=str(m), GL_N=str(n)), stdout=subprocess.DEVNULL, stderr=open(m / f'err-{n}', 'w'))


def release_all(m, procs):
    """Let every holder finish (a holder admitted late gets its go file as soon as it starts); kill what stays after 20 s."""
    end = time.time() + 20
    while time.time() < end and any(p.poll() is None for p in procs):
        for f in list(m.glob('started-*')) + list(m.glob('pid-*')):
            (m / f'go-{f.name.split("-", 1)[1]}').touch()
        time.sleep(0.05)
    for p in procs:
        if p.poll() is None:
            p.kill()
            p.wait()


def queued_names(py, env):
    r = gl(py, env, 'status', '--json')
    try:
        return [q['name'] for q in json.loads(r.stdout)['queue']] if r.returncode == 0 else []
    except ValueError:
        return []


def case_cap(py, base, label):
    """Weighted caps: two default gates hold, a third waits and says so; a browser job beyond the browser cap waits."""
    m, bad, procs = base / f'm-{label}', [], []
    m.mkdir()
    env = env_for(base, label, SDLC_GATE_REPORT_SECS='0.3')
    try:
        procs = [holder(py, env, m, 1), holder(py, env, m, 2)]
        if not waitfor(lambda: (m / 'started-1').exists() and (m / 'started-2').exists()):
            return ['the first two default gates did not start together']
        procs.append(holder(py, env, m, 3))
        waitfor(lambda: (m / 'started-3').exists() or 'waiting for a slot' in (m / 'err-3').read_text(), 5)
        if (m / 'started-3').exists():
            return ['the third holder started at once with the compute capacity held']
        if label.startswith('real'):
            st = gl(py, env, 'status')
            if not (st.returncode == 0 and 'name H1' in st.stdout and 'name H2' in st.stdout and 'name H3' in st.stdout and 'age ' in st.stdout):
                bad.append(f'status does not list the holders and the waiter, got {st.stdout!r}')
            if 'H1' not in (m / 'err-3').read_text():
                bad.append('the waiting third holder does not name the holders on stderr')
        (m / 'go-1').touch()
        if not waitfor(lambda: (m / 'started-3').exists()):
            bad.append('the third holder did not run after one exited')
        release_all(m, procs)
        for p in procs:
            if p.returncode != 0:
                bad.append(f'a holder exited {p.returncode}')
        # browser cap 3: two jobs of 2 browsers cannot run together
        m2 = base / f'm2-{label}'
        m2.mkdir()
        env2 = env_for(base, label + 'b')
        procs = [holder(py, env2, m2, 1, '--need', 'compute_units=1,browser_jobs=2')]
        if not waitfor(lambda: (m2 / 'started-1').exists()):
            return bad + ['the first browser job did not start']
        procs.append(holder(py, env2, m2, 2, '--need', 'compute_units=1,browser_jobs=2'))
        waitfor(lambda: 'H2' in queued_names(py, env2) or (m2 / 'started-2').exists(), 5)
        if (m2 / 'started-2').exists():
            bad.append('a second browser job of 2 started at once with the browser cap 3')
        release_all(m2, procs)
        return bad
    finally:
        release_all(m, procs)


def case_sequence(py, base, label, specs, order):
    """A holds the whole compute capacity; the specs (name, priority) queue behind it in that order; releasing A must
    admit them one at a time in `order`."""
    m, bad, procs = base / f'm-{label}', [], []
    m.mkdir()
    env = env_for(base, label)
    try:
        procs.append(holder(py, env, m, 'A', '--need', 'compute_units=6'))
        if not waitfor(lambda: (m / 'started-A').exists()):
            return ['the first holder did not start']
        for n, prio in specs:
            procs.append(holder(py, env, m, n, '--need', 'compute_units=6', '--priority', str(prio)))
            if not waitfor(lambda: f'H{n}' in queued_names(py, env)):
                return [f'{n} did not show as queued']
        (m / 'go-A').touch()
        got = []
        for n in order:
            if not waitfor(lambda: (m / f'started-{n}').exists()):
                bad.append(f'{n} was not admitted next (admitted so far {got}, started {sorted(x.name for x in m.glob("started-*"))})')
                break
            early = [x for x, _ in specs if x != n and x not in got and (m / f'started-{x}').exists()]
            if early:
                bad.append(f'{early} ran together with {n}')
                break
            got.append(n)
            (m / f'go-{n}').touch()
        return bad
    finally:
        release_all(m, procs)


def kill_wrapper(p):
    p.kill()
    p.wait()


def case_reclaim(py, base, label):
    """A holder whose wrapper and command are both gone is reclaimed: the next run is admitted."""
    m, procs = base / f'm-{label}', []
    m.mkdir()
    env = env_for(base, label)
    try:
        procs = [holder(py, env, m, 'X', '--need', 'compute_units=6')]
        if not waitfor(lambda: (m / 'pid-X').exists() and (m / 'started-X').exists()):
            return ['the holder did not start']
        cpid = int((m / 'pid-X').read_text())
        kill_wrapper(procs[0])
        os.killpg(cpid, signal.SIGKILL)
        waitfor(lambda: not group_alive(cpid), 10)
        t0 = time.time()
        r = gl(py, env, 'run', '--need', 'compute_units=6', '--timeout', '6', '--', 'touch', str(m / 'ran'))
        if not (r.returncode == 0 and (m / 'ran').exists() and time.time() - t0 < 5):
            return [f'the dead holder was not reclaimed, rc={r.returncode} {r.stderr!r}']
        return []
    finally:
        release_all(m, procs)


def case_livegroup(py, base, label):
    """A dead wrapper whose command group is alive keeps its charge (shown as an orphaned group) until the group is gone."""
    m, procs = base / f'm-{label}', []
    m.mkdir()
    env = env_for(base, label)
    bad = []
    try:
        procs = [holder(py, env, m, 'X', '--need', 'compute_units=6')]
        if not waitfor(lambda: (m / 'pid-X').exists() and (m / 'started-X').exists()):
            return ['the holder did not start']
        cpid = int((m / 'pid-X').read_text())
        kill_wrapper(procs[0])
        r = gl(py, env, 'run', '--need', 'compute_units=6', '--timeout', '2', '--', 'true')
        if not (r.returncode == 3 and r.stderr.startswith('gate_lock: timeout')):
            bad.append(f'a live group lost its charge when its wrapper died, rc={r.returncode} {r.stderr!r}')
        if label.startswith('real'):
            st = gl(py, env, 'status')
            if 'orphaned group' not in st.stdout:
                bad.append(f'status does not show the orphaned group, got {st.stdout!r}')
        os.killpg(cpid, signal.SIGKILL)
        waitfor(lambda: not group_alive(cpid), 10)
        r = gl(py, env, 'run', '--need', 'compute_units=6', '--timeout', '6', '--', 'true')
        if r.returncode != 0:
            bad.append(f'the group was gone but the charge stayed, rc={r.returncode} {r.stderr!r}')
        return bad
    finally:
        release_all(m, procs)


def case_ident(py, base, label):
    """A grant whose pid is alive but whose recorded start identity differs is a reused pid and is reclaimed; the exact
    identity of a live process holds its charge."""
    bad = []
    me = os.getpid()
    for tag, start, want in (('real', pid_start(me), 3), ('reused', 'bogus-start-identity', 0)):
        env = env_for(base, f'{label}-{tag}')
        root = pathlib.Path(env['SDLC_GATE_DIR'])
        root.mkdir(parents=True)
        entry = {'id': 'f' * 32, 'seq': 1, 'repo': '/x', 'name': 'fab', 'cmd': 'x', 'need': {COMPUTE: 6}, 'priority': 0, 'pid': me,
                 'pid_start': start, 'pgid': None, 'enqueued_at': time.time(), 'granted_at': time.time()}
        (root / 'ledger.json').write_text(json.dumps({'protocol': PROTOCOL, 'boot': boot_id(), 'seq': 1, 'rr': '', 'grants': [entry], 'queue': []}))
        r = gl(py, env, 'run', '--need', 'compute_units=6', '--timeout', '1', '--', 'true')
        if r.returncode != want:
            bad.append(f'{tag}: a grant with {"the live identity" if tag == "real" else "a reused pid"} gave rc {r.returncode}, wanted {want} {r.stderr!r}')
    return bad


def case_drain(py, base, label):
    """The command's leader exits at once and leaves a descendant in its group: the descendant is gone before run returns."""
    m = base / f'm-{label}'
    m.mkdir()
    env = env_for(base, label, GL_M=str(m))
    r = gl(py, env, 'run', '--', 'sh', '-c', 'sleep 300 >/dev/null 2>&1 & echo $! >"$GL_M/d.pid"')
    try:
        dpid = int((m / 'd.pid').read_text())
    except (OSError, ValueError):
        return [f'the descendant did not start, rc={r.returncode} {r.stderr!r}']
    try:
        if pid_start(dpid) is not None:
            return [f'the descendant {dpid} still runs after the run returned (rc {r.returncode})']
        return []
    finally:
        try:
            os.kill(dpid, signal.SIGKILL)
        except OSError:
            pass


def case_load(py, base, label):
    """The load cap: with max_load 24 and a load of 36.5 a second gate that fits the capacity is not admitted, the
    holder keeps its grant, and status says why; once the load is 10 the waiter runs. The load comes from one file
    every process of the case reads (SDLC_GATE_LOAD_FILE), replaced atomically so no poll reads half a write."""
    m, bad, procs = base / f'm-{label}', [], []
    m.mkdir()
    lf = base / f'load-{label}'
    env = env_for(base, label, SDLC_GATE_LOAD_FILE=str(lf))

    def set_load(v):
        tmp = base / f'load-{label}.tmp'
        tmp.write_text(f'{v}\n')
        os.replace(tmp, lf)
    try:
        set_load(1)
        r = gl(py, env, 'policy', 'set', 'max_load=24')
        if r.returncode != 0 or 'max load 24' not in r.stdout:
            return [f'policy set max_load=24 did not take, rc={r.returncode} {r.stdout!r} {r.stderr!r}']
        procs = [holder(py, env, m, 1)]
        if not waitfor(lambda: (m / 'started-1').exists()):
            return ['the holder did not start with the load under the cap']
        set_load(36.5)
        procs.append(holder(py, env, m, 2))  # two default needs fit the capacity, so only the load holds it
        waitfor(lambda: 'H2' in queued_names(py, env) or (m / 'started-2').exists(), 5)
        time.sleep(3 * POLL)
        if (m / 'started-2').exists():
            return ['the waiter ran over the load cap']
        st = gl(py, env, 'status')
        rows = st.stdout.splitlines()
        if not any(x.startswith('admitted') and 'name H1' in x for x in rows):
            bad.append(f'the holder lost its grant when the load rose, got {st.stdout!r}')
        if not (any(x.startswith('queued') and 'name H2' in x for x in rows) and 'waiting: load 36.5 over cap 24' in rows):
            bad.append(f'status does not show the waiter and the load reason, got {st.stdout!r}')
        js = {}
        try:
            js = json.loads(gl(py, env, 'status', '--json').stdout).get('load') or {}
        except ValueError:
            pass
        if js != {'value': 36.5, 'max_load': 24, 'over': True}:
            bad.append(f'status --json does not carry the load fact, got {js}')
        set_load(10)
        if not waitfor(lambda: (m / 'started-2').exists()):
            bad.append('the waiter did not run after the load dropped under the cap')
        return bad
    finally:
        release_all(m, procs)


def case_load_idle(py, base, label):
    """The starvation guard: with max_load 24, a load of 36.5 from outside and no grant held, the first gate is
    admitted at once; a second one then waits on the load while the first holds."""
    m, bad, procs = base / f'm-{label}', [], []
    m.mkdir()
    lf = base / f'load-{label}'
    env = env_for(base, label, SDLC_GATE_LOAD_FILE=str(lf))
    lf.write_text('36.5\n')
    try:
        r = gl(py, env, 'policy', 'set', 'max_load=24')
        if r.returncode != 0:
            return [f'policy set max_load=24 did not take, rc={r.returncode} {r.stderr!r}']
        procs = [holder(py, env, m, 1)]
        if not waitfor(lambda: (m / 'started-1').exists()):
            return ['the starved head: no grant was held and the load was over the cap, yet the first gate was not admitted']
        procs.append(holder(py, env, m, 2))
        waitfor(lambda: 'H2' in queued_names(py, env) or (m / 'started-2').exists(), 5)
        time.sleep(3 * POLL)
        if (m / 'started-2').exists():
            bad.append('the second gate ran over the load cap while the first held a grant')
        return bad
    finally:
        release_all(m, procs)


def case_load_default(py, base, label):
    """The default load cap: with no max_load in the policy and 10 CPUs (SDLC_GATE_CPUS) the cap is 8, so a load of
    12 keeps a second gate that fits the capacity waiting while the holder keeps its grant; `policy show` names the
    default and `policy set compute_units=6` does not write it into policy.json; `policy set max_load=0` turns the cap
    off and the waiter runs."""
    m, bad, procs = base / f'm-{label}', [], []
    m.mkdir()
    lf = base / f'load-{label}'
    env = env_for(base, label, SDLC_GATE_LOAD_FILE=str(lf), SDLC_GATE_CPUS='10')
    lf.write_text('1\n')
    try:
        procs = [holder(py, env, m, 1)]
        if not waitfor(lambda: (m / 'started-1').exists()):
            return ['the holder did not start with the load under the default cap']
        lf.write_text('12\n')
        procs.append(holder(py, env, m, 2))
        waitfor(lambda: 'H2' in queued_names(py, env) or (m / 'started-2').exists(), 5)
        time.sleep(3 * POLL)
        if (m / 'started-2').exists():
            return ['the waiter ran over the default load cap']
        r = gl(py, env, 'policy', 'show')
        if not ('"max_load": 8' in r.stdout and 'default from 10 CPUs' in r.stdout):
            bad.append(f'policy show does not name the default cap of 8 from 10 CPUs, got {r.stdout!r}')
        r = gl(py, env, 'policy', 'set', 'compute_units=6')
        pf = pathlib.Path(env['SDLC_GATE_DIR']) / 'policy.json'
        if r.returncode != 0 or 'max_load' in pf.read_text():
            bad.append(f'policy set compute_units=6 wrote the default cap into policy.json, got {r.returncode} {pf.read_text()!r}')
        r = gl(py, env, 'policy', 'set', 'max_load=0')
        if r.returncode != 0:
            return bad + [f'policy set max_load=0 failed, rc={r.returncode} {r.stderr!r}']
        if not waitfor(lambda: (m / 'started-2').exists()):
            bad.append('max_load=0 did not turn the default cap off: the waiter did not run')
        r = gl(py, env, 'policy', 'show')
        if '"max_load": 0' not in r.stdout or 'default from' in r.stdout:
            bad.append(f'policy show after max_load=0 still shows the default, got {r.stdout!r}')
        return bad
    finally:
        release_all(m, procs)


def case_heap(py, base, label):
    """The Node heap cap: a run with no NODE_OPTIONS passes the child --max-old-space-size=4096 and says so on stderr;
    an existing --max-old-space-size is left alone; `policy set node_heap_mb=0` adds nothing; `policy show` shows the key."""
    env = env_for(base, label)
    env.pop('NODE_OPTIONS', None)
    show = ['sh', '-c', 'echo "[$NODE_OPTIONS]"']
    bad = []
    r = gl(py, env, 'run', '--', *show)
    if r.stdout.strip() != '[--max-old-space-size=4096]' or 'node heap capped at 4096' not in r.stderr:
        bad.append(f'heap cap missing: no NODE_OPTIONS gave {r.stdout!r} {r.stderr!r}, wanted [--max-old-space-size=4096] and one stderr line')
    r = gl(py, dict(env, NODE_OPTIONS='--max-old-space-size=2048'), 'run', '--', *show)
    if r.stdout.strip() != '[--max-old-space-size=2048]' or 'node heap capped' in r.stderr:
        bad.append(f'heap cap overrode the caller: got {r.stdout!r} {r.stderr!r}')
    r = gl(py, dict(env, NODE_OPTIONS='--trace-warnings'), 'run', '--', *show)
    if r.stdout.strip() != '[--trace-warnings --max-old-space-size=4096]':
        bad.append(f'heap cap lost the existing options: got {r.stdout!r}')
    r = gl(py, env, 'policy', 'show')
    if '"node_heap_mb": 4096' not in r.stdout or 'built-in default' not in r.stdout:
        bad.append(f'policy show does not name node_heap_mb 4096 as the default, got {r.stdout!r}')
    r = gl(py, env, 'policy', 'set', 'node_heap_mb=1024')
    pf = pathlib.Path(env['SDLC_GATE_DIR']) / 'policy.json'
    r2 = gl(py, env, 'run', '--', *show)
    if r.returncode != 0 or r2.stdout.strip() != '[--max-old-space-size=1024]':
        bad.append(f'policy set node_heap_mb=1024 did not take, got {r.returncode} {r.stderr!r} {r2.stdout!r}')
    gl(py, env, 'policy', 'reset')
    r = gl(py, env, 'policy', 'set', 'compute_units=6')
    if 'node_heap_mb' in pf.read_text():
        bad.append(f'policy set compute_units=6 wrote the default heap cap into policy.json, got {pf.read_text()!r}')
    r = gl(py, env, 'policy', 'set', 'node_heap_mb=0')
    r2 = gl(py, env, 'run', '--', *show)
    if r.returncode != 0 or r2.stdout.strip() != '[]' or 'node heap capped' in r2.stderr:
        bad.append(f'policy set node_heap_mb=0 still caps: got {r.returncode} {r2.stdout!r} {r2.stderr!r}')
    return bad


def case_rr():
    """Round robin across repos with FIFO inside a repo, on a fabricated ledger (no processes); then the same
    ledger with a max_load: under the cap the order holds, over it nothing is granted and the turn does not move."""
    pol = {k: dict(v) for k, v in BUILTIN_POLICY.items()}

    def entry(i, repo, units=6):
        return {'id': i, 'seq': int(i[1:]), 'repo': repo, 'need': {COMPUTE: units}, 'priority': 0}

    def fresh(rr, units=6):
        return {'grants': [], 'rr': rr, 'queue': [entry('a1', 'A', units), entry('a2', 'A', units), entry('b3', 'B', units)]}

    def rounds(pol, **kw):
        L, got = fresh(''), []
        for _ in range(3):
            schedule(L, pol, **kw)
            got += [g['id'] for g in L['grants']]
            L['grants'] = []
        return got
    got = rounds(pol)
    bad = [] if got == ['a1', 'b3', 'a2'] else [f'repos A,A,B were granted {got}, wanted a1, b3, a2']
    capped = dict(pol, max_load=24)
    got = rounds(capped, load=10)
    if got != ['a1', 'b3', 'a2']:
        bad.append(f'under the load cap repos A,A,B were granted {got}, wanted a1, b3, a2')
    if rounds(capped, load=24) != ['a1', 'b3', 'a2']:
        bad.append('a load equal to the cap did not admit')
    L = fresh('A', 1)  # one unit each, so all three fit capacity and only the load cap can refuse them
    L['grants'] = [entry('h0', 'Z', 1)]  # a held grant: the cap now applies
    granted = schedule(L, capped, load=36.5)
    if granted or len(L['grants']) != 1 or L['rr'] != 'A' or len(L['queue']) != 3:
        bad.append(f'over the load cap with a grant held the schedule granted {granted} and left rr {L["rr"]!r}, wanted nothing granted and rr A')
    L = fresh('A', 1)
    granted = schedule(L, capped, load=36.5)
    if granted != ['b3']:
        bad.append(f'over the load cap with no grant held the schedule granted {granted}, wanted only b3 (the head, then the cap holds)')
    return bad


def clean_env(tmp, **extra):
    return env_for(tmp, 'x', **extra)


def reap_case(py, tmp, label, tok, stop):
    """A fake orphan (double fork, so its parent is pid 1) and a fake with a live parent, both named to match
    and both found only through --match <their unique name>: the orphan is listed and alive by default, not
    listed under the default age, and (when stop) stopped by --kill; the live-parent fake is never listed
    and (when stop) never stopped. Returns the misses."""
    d, bad, pids, live = tmp / f'reap-{label}', [], {}, None
    d.mkdir()
    name = f'chrome-headless-shell-{tok}-{label}'
    env = clean_env(d)
    args = ('--match', re.escape(name))

    def listed(out, pid):
        return any(x.startswith(f'pid {pid} ') for x in out.splitlines())

    def alive(pid):
        return proc_start(pid) is not None

    def pid_of(f):
        try:
            return int((d / f).read_text())
        except (OSError, ValueError):
            return 0
    try:
        subprocess.run([sys.executable, '-c', REAP_ORPHANER, REAP_FAKE], env=dict(env, GL_PIDFILE=str(d / 'o.pid'), GL_NAME=name),
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        live = subprocess.Popen([sys.executable, '-c', REAP_FAKE, name], env=dict(env, GL_PIDFILE=str(d / 'l.pid')),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not waitfor(lambda: pid_of('o.pid') and pid_of('l.pid')):
            return ['the fake processes did not start']
        o, l = pids['orphan'], pids['live'] = pid_of('o.pid'), pid_of('l.pid')

        def parentless():
            row = next((r for r in ps_rows() if r[0] == o), None)
            return row is not None and (row[1] == 1 or proc_start(row[1]) is None)
        if not waitfor(parentless):
            return ['the fake orphan was not reparented to pid 1']
        r = gl(py, env, 'reap', '--older-than', '0', *args)
        if not (r.returncode == 0 and listed(r.stdout, o) and 'nothing stopped' in r.stdout and alive(o)):
            bad.append(f'orphan: not listed by default or not left alone, rc={r.returncode} {r.stdout!r} {r.stderr!r}')
        if listed(r.stdout, l):
            bad.append(f'live-parent: the process with a live parent was listed as stoppable, got {r.stdout!r}')
        r = gl(py, env, 'reap', *args)
        if listed(r.stdout, o):
            bad.append(f'orphan: listed under the default {REAP_AGE_MIN:g} minute threshold, got {r.stdout!r}')
        if stop:
            r = gl(py, env, 'reap', '--older-than', '0', '--kill', *args)
            if not (r.returncode == 0 and f'stopped pid {o} ' in r.stdout and waitfor(lambda: not alive(o), 10)):
                bad.append(f'orphan: --kill did not stop it, rc={r.returncode} {r.stdout!r} {r.stderr!r}')
            if listed(r.stdout, l) or f'stopped pid {l} ' in r.stdout or not alive(l):
                bad.append(f'live-parent: --kill touched the process with a live parent, got {r.stdout!r}')
        return bad
    finally:
        for pid in pids.values():
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        if live is not None:
            live.kill()
            live.wait()


def selftest():
    script = pathlib.Path(__file__).resolve()
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    # Isolation compares only what this selftest could have written. The real root is shared with every other
    # session's gate run, so a snapshot of it (its ledger mtime) changes without any fault here.
    real_root = pathlib.Path(pwd.getpwuid(os.getuid()).pw_dir) / '.local' / 'state' / 'sdlc-lite' / 'gate-lock'
    _ISO.update(issued=[], hits=[], watch=[str(real_root), str(real_root.resolve())])
    if not _ISO['hooked']:
        sys.addaudithook(_iso_hook)
        _ISO['hooked'] = True
    with tempfile.TemporaryDirectory() as t:
        base = pathlib.Path(t).resolve()
        src = script.read_text()

        # 1. each control passes on the real script and is observed failing in a mutant copy with its line changed
        controls = (
            ('weighted cap', lambda p, b, lb: case_cap(p, b, lb), M_CAP, 'pass  # SLOT-CAP', 'started at once'),
            ('FIFO order', lambda p, b, lb: case_sequence(p, b, lb, [('B', 0), ('C', 0), ('D', 0)], ['B', 'C', 'D']), M_ORDER,
             "return (-e['priority'], -e['seq'])  # QUEUE-ORDER", 'was not admitted next'),
            ('priority', lambda p, b, lb: case_sequence(p, b, lb, [('B', 0), ('C', 5)], ['C', 'B']), M_ORDER,
             "return (0, e['seq'])  # QUEUE-ORDER", 'was not admitted next'),
            ('dead holder reclaimed', case_reclaim, M_LIVE, 'return True  # GRANT-LIVE', 'not reclaimed'),
            ('live group not reclaimed', case_livegroup, M_LIVE, 'return wrapper  # GRANT-LIVE', 'lost its charge'),
            ('start identity', case_ident, M_IDENT, 'pass  # IDENT', 'reused pid'),
            ('group drain', case_drain, M_DRAIN, 'pass  # DRAIN', 'still runs'),
            ('load cap', case_load, M_LOAD, 'pass  # LOAD-CAP', 'ran over the load cap'),
            ('load cap starvation guard', case_load_idle, M_LOAD,
             "if max_load and load is not None and load > max_load: break  # LOAD-CAP", 'starved head'),
            ('default load cap', case_load_default, M_LOADDEF, 'pass  # LOAD-DEFAULT', 'ran over the default load cap'),
            ('node heap cap', case_heap, M_HEAP, 'pass  # HEAP-CAP', 'heap cap missing'))
        for i, (label, case, marker, repl, tell) in enumerate(controls):
            got = case(script, base, f'real{i}')
            expect(f'{label}: {got}', not got)
            expect(f'negative control: the {label} line is in the script exactly once', src.count(marker) == 1)
            mdir = base / f'mutant{i}'
            mdir.mkdir()
            mutant = mdir / 'gate_lock.py'
            mutant.write_text(src.replace(marker, repl))
            got = case(mutant, base, f'mut{i}')
            expect(f'negative control: with the {label} line changed the case must fail ({tell!r}), got {got}', any(tell in x for x in got))
            if got:
                print(f'gate_lock selftest: negative control observed ({label}): {got[0][:140]}')
        got = case_rr()
        expect(f'round robin across repos: {got}', not got)

        # 2. SDLC_GATE_WORKERS, the exit status, an unrunnable command, pass-through, nice, receipts
        env = env_for(base, 'misc')
        for args, want in (((), '3'), (('--slots', '2'), '3'), (('--slots', '1'), '6'), (('--slots', '100000'), '1'),
                           (('--need', 'compute_units=2'), '2'), (('--need', 'browser_jobs=1'), '3')):
            r = gl(script, env, 'run', *args, '--', 'sh', '-c', 'echo "$SDLC_GATE_WORKERS"')
            expect(f'workers: {args} gives {want}, got {r.stdout!r} {r.stderr!r}', r.stdout.strip() == want)
        r = gl(script, dict(env, SDLC_GATE_SLOTS='4'), 'run', '--', 'sh', '-c', 'echo "$SDLC_GATE_WORKERS"')
        expect(f'workers: SDLC_GATE_SLOTS=4 gives 1, got {r.stdout!r}', r.stdout.strip() == '1')
        r = gl(script, env, 'run', '--', 'sh', '-c', 'echo "[$SDLC_GATE_GRANT][$SDLC_GATE_DIR][$SDLC_GATE_LOCK_HELD]"')
        expect(f'env: the command sees its grant, the state root and the held marker, got {r.stdout!r}',
               re.fullmatch(r'\[[0-9a-f]{32}\]\[' + re.escape(env['SDLC_GATE_DIR']) + r'\]\[1\]', r.stdout.strip()) is not None)
        for argv, want in ((['sh', '-c', 'exit 7'], 7), (['sh', '-c', 'exit 0'], 0), (['sh', '-c', 'kill -9 $$'], 137),
                           (['no-such-command-gate-lock'], 127)):
            r = gl(script, env, 'run', '--slots', '2', '--', *argv)
            expect(f'exit status: {argv[-1]} gives {want}, got {r.returncode} {r.stderr!r}', r.returncode == want)
        r = gl(script, env, 'run', '--slots', '0', '--', 'sh', '-c', 'echo "[$SDLC_GATE_WORKERS][$SDLC_GATE_LOCK_HELD][$SDLC_GATE_GRANT]"')
        expect(f'pass-through: 0 slots runs with no env change, got {r.stdout!r}', r.stdout.strip() == '[][][]')
        r = gl(script, dict(env, SDLC_GATE_SLOTS='0'), 'run', '--', 'sh', '-c', 'echo "[$SDLC_GATE_WORKERS]"')
        expect(f'pass-through: SDLC_GATE_SLOTS=0 runs with no env change, got {r.stdout!r}', r.stdout.strip() == '[]')
        probe = 'import os; print(os.nice(0))'
        basenice = int(subprocess.run([sys.executable, '-c', probe], env=env, capture_output=True, text=True).stdout.strip())
        r = gl(script, env, 'run', '--nice', '--', sys.executable, '-c', probe)
        expect(f'nice: --nice raises niceness 10 from {basenice}, got {r.stdout!r} {r.stderr!r}', r.stdout.strip() == str(min(19, basenice + 10)))
        r = gl(script, env, 'run', '--need', 'compute_units=7', '--receipt', str(base / 'r-big.json'), '--', 'true')
        first = r.stderr.splitlines()[0] if r.stderr else ''
        expect(f'too_large: a need above the capacity exits 3 at once with one coded line, got rc={r.returncode} {r.stderr!r}',
               r.returncode == 3 and first.startswith('gate_lock: too_large: ') and len(r.stderr.splitlines()) == 1)
        rec = json.loads((base / 'r-big.json').read_text()) if (base / 'r-big.json').exists() else {}
        expect(f'receipt: a too_large run records its outcome, got {rec}', rec.get('outcome') == 'too_large' and rec.get('rc') == 3)
        r = gl(script, env, 'run', '--receipt', str(base / 'r-ok.json'), '--', 'sh', '-c', 'exit 4')
        rec = json.loads((base / 'r-ok.json').read_text()) if (base / 'r-ok.json').exists() else {}
        expect(f'receipt: outcome child_failed, rc and four durations, got {rec}',
               rec.get('outcome') == 'child_failed' and rec.get('rc') == 4 and r.returncode == 4 and rec.get('protocol') == PROTOCOL
               and all(isinstance(rec.get(k), int) for k in ('wait_ms', 'run_ms', 'cleanup_ms', 'total_ms')) and rec.get('grant'))
        r = gl(script, env, 'run', '--receipt', str(base / 'r-ok2.json'), '--', 'true')
        rec = json.loads((base / 'r-ok2.json').read_text()) if (base / 'r-ok2.json').exists() else {}
        expect(f'receipt: outcome ok, got {rec}', rec.get('outcome') == 'ok' and rec.get('rc') == 0)
        r = gl(script, env, 'status')
        expect(f'status: nothing left after the runs, got {r.stdout!r}', r.stdout.strip() == 'no holders')

        # 3. nesting, forged context, context, the held marker alone
        env = env_for(base, 'nest')
        inner = f'{shlex.quote(sys.executable)} {shlex.quote(str(script))}'
        r = gl(script, env, 'run', '--need', 'compute_units=6', '--', 'sh', '-c', f'{inner} run --timeout 3 -- sh -c "echo inner:\\$SDLC_GATE_WORKERS"')
        expect(f'nesting: a run inside a full grant takes no second turn, got rc={r.returncode} {r.stdout!r} {r.stderr!r}',
               r.returncode == 0 and r.stdout.strip() == 'inner:3')
        r = gl(script, env, 'run', '--', 'sh', '-c', f'{inner} run --need compute_units=5 -- true')
        expect(f'nesting: a need above the grant is too_large, got rc={r.returncode} {r.stderr!r}',
               r.returncode == 3 and r.stderr.startswith('gate_lock: too_large'))
        r = gl(script, env, 'run', '--', 'sh', '-c', f'{inner} run --need compute_units=2 -- sh -c "echo \\$SDLC_GATE_WORKERS"')
        expect(f'nesting: workers are the smaller of the two needs, got {r.stdout!r} {r.stderr!r}', r.stdout.strip() == '2')
        hop = (f'import subprocess,sys; sys.exit(subprocess.run([sys.executable, {str(script)!r}, "run", "--", "true"], start_new_session=True).returncode)')
        r = gl(script, env, 'run', '--', sys.executable, '-c', hop)
        expect(f'nesting: a run from another process group is bad_context, got rc={r.returncode} {r.stderr!r}',
               r.returncode == 3 and r.stderr.startswith('gate_lock: bad_context'))
        r = gl(script, dict(env, SDLC_GATE_GRANT='deadbeef' * 4), 'run', '--', 'true')
        expect(f'forged: an unknown grant id is bad_context and the command does not run, got rc={r.returncode} {r.stderr!r}',
               r.returncode == 3 and r.stderr.startswith('gate_lock: bad_context'))
        r = gl(script, env, 'run', '--', 'sh', '-c', f'{inner} context --json')
        ctx = {}
        try:
            ctx = json.loads(r.stdout)
        except ValueError:
            pass
        expect(f'context: inside a grant prints it, got rc={r.returncode} {r.stdout!r}', r.returncode == 0 and ctx.get('need') == {COMPUTE: 3})
        r = gl(script, env, 'context')
        expect(f'context: outside a grant exits 1, got {r.returncode}', r.returncode == 1)
        m = base / 'm-held'
        m.mkdir()
        h = holder(script, env, m, 'A', '--need', 'compute_units=6')
        try:
            expect('held: the holder started', waitfor(lambda: (m / 'started-A').exists()))
            r = gl(script, dict(env, SDLC_GATE_LOCK_HELD='1'), 'run', '--timeout', '1', '--', 'true')
            expect(f'held: SDLC_GATE_LOCK_HELD=1 alone is a top-level request that waits, got rc={r.returncode} {r.stderr!r}',
                   r.returncode == 3 and r.stderr.startswith('gate_lock: timeout'))
            # 4. the timeout path: exit 3, one stderr line naming the holder, and no queue entry left
            t0 = time.time()
            r = gl(script, env, 'run', '--timeout', '1', '--', 'true')
            lines = [x for x in r.stderr.splitlines() if x.strip()]
            expect(f'timeout: exits 3 with one stderr line naming the holder, got rc={r.returncode} {r.stderr!r}',
                   r.returncode == 3 and len(lines) == 1 and lines[0].startswith('gate_lock: timeout after') and 'H1' not in lines[0] and 'HA' in lines[0])
            expect('timeout: it waited about the timeout', 0.9 <= time.time() - t0 < 14)
            expect(f'timeout: the queue entry is removed, got {queued_names(script, env)}', queued_names(script, env) == [])
            # status rows: admitted and queued
            w = subprocess.Popen([sys.executable, str(script), 'run', '--name', 'WAIT', '--priority', '2', '--timeout', '60', '--',
                                  'touch', str(m / 'wait-ran')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            expect('status: the waiter queues', waitfor(lambda: 'WAIT' in queued_names(script, env)))
            st = gl(script, env, 'status')
            rows = st.stdout.splitlines()
            expect(f'status: an admitted row and a queued row, got {st.stdout!r}',
                   any(x.startswith('admitted') and 'name HA' in x for x in rows) and any(x.startswith('queued') and 'name WAIT' in x and 'priority 2' in x and '#1' in x for x in rows))
            js = json.loads(gl(script, env, 'status', '--json').stdout)
            expect(f'status --json: grants and queue with states, got {js}', js['grants'][0]['state'] == 'admitted' and js['queue'][0]['state'] == 'queued'
                   and js['queue'][0]['position'] == 1)
            expect(f'status --json: the queued row has ahead and blocking, got {js["queue"][0]}',
                   js['queue'][0].get('ahead') == 6 and js['queue'][0].get('blocking') == ['HA']
                   and any('ahead 6' in x and 'blocking HA' in x for x in rows if x.startswith('queued')))
            # cancel while queued: no child, entry removed, exit 128+15
            w.terminate()
            rc = w.wait(timeout=30)
            expect(f'cancel: a queued run exits 143, got {rc}', rc == 143)
            expect('cancel: the cancelled waiter never ran', not (m / 'wait-ran').exists())
            expect(f'cancel: its queue entry is removed, got {queued_names(script, env)}', queued_names(script, env) == [])
            # a queued waiter sees a capacity raised after it queued
            w = subprocess.Popen([sys.executable, str(script), 'run', '--name', 'REPOL', '--need', 'compute_units=1', '--timeout', '60', '--',
                                  'touch', str(m / 'repol-ran')], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            expect('policy reload: the waiter queues behind the full holder', waitfor(lambda: 'REPOL' in queued_names(script, env)))
            time.sleep(0.6)
            expect('policy reload: it has not run while the capacity is 6', not (m / 'repol-ran').exists())
            gl(script, env, 'policy', 'set', 'compute_units=20')
            expect('policy reload: the queued waiter is admitted after policy set compute_units=20', waitfor(lambda: (m / 'repol-ran').exists()))
            w.wait(timeout=30)
            gl(script, env, 'policy', 'reset')
        finally:
            release_all(m, [h])

        # 5. SIGTERM kills the command's process group, frees the grant, and exits 128+15
        env = env_for(base, 'term')
        m = base / 'm-term'
        m.mkdir()
        a = subprocess.Popen([sys.executable, str(script), 'run', '--name', 'term', '--', 'sh', '-c',
                              'echo $$ >"$GL_M/c.pid"; touch "$GL_M/started"; exec sleep 60'],
                             env=dict(env, GL_M=str(m)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            expect('sigterm: the command started', waitfor(lambda: (m / 'started').exists()))
            cpid = int((m / 'c.pid').read_text() or 0) if (m / 'c.pid').exists() else 0
            a.terminate()
            rc = a.wait(timeout=30)
            expect(f'sigterm: exits 143, got {rc}', rc == 143)
            expect('sigterm: the command was killed', cpid > 0 and waitfor(lambda: pid_start(cpid) is None, 10))
            st = gl(script, env, 'status')
            expect(f'sigterm: the grant is released, got {st.stdout!r}', st.stdout.strip() == 'no holders')
        finally:
            if a.poll() is None:
                a.kill()
                a.wait()

        # 6. state: a ledger from another boot is empty; a corrupt ledger fails closed until reset --confirm; policy; legacy bridge
        env = env_for(base, 'state')
        root = pathlib.Path(env['SDLC_GATE_DIR'])
        root.mkdir(parents=True)
        entry = {'id': 'e' * 32, 'seq': 1, 'repo': '/x', 'name': 'old', 'cmd': 'x', 'need': {COMPUTE: 6}, 'priority': 0, 'pid': os.getpid(),
                 'pid_start': pid_start(os.getpid()), 'pgid': None, 'enqueued_at': time.time(), 'granted_at': time.time()}
        (root / 'ledger.json').write_text(json.dumps({'protocol': PROTOCOL, 'boot': 'another-boot-id', 'seq': 1, 'rr': '', 'grants': [entry], 'queue': []}))
        r = gl(script, env, 'run', '--need', 'compute_units=6', '--timeout', '2', '--', 'true')
        expect(f'reboot: a ledger from another boot id is empty, got rc={r.returncode} {r.stderr!r}', r.returncode == 0)
        (root / 'ledger.json').write_text('{not json')
        r = gl(script, env, 'run', '--', 'true')
        expect(f'corrupt: a ledger that does not parse fails closed with a coded line, got rc={r.returncode} {r.stderr!r}',
               r.returncode == 3 and r.stderr.startswith('gate_lock: ledger_corrupt'))
        r = gl(script, env, 'reset')
        expect(f'reset: without --confirm it refuses, got {r.returncode}', r.returncode == 2)
        r = gl(script, env, 'reset', '--confirm')
        expect(f'reset: --confirm replaces the corrupt ledger, got rc={r.returncode} {r.stdout!r} {r.stderr!r}', r.returncode == 0 and any(root.glob('ledger.json.corrupt-*')))
        r = gl(script, env, 'run', '--', 'true')
        expect(f'reset: runs work afterwards, got {r.returncode} {r.stderr!r}', r.returncode == 0)
        r = gl(script, env, 'reset', '--confirm')
        expect(f'reset: refused while the ledger parses, got {r.returncode}', r.returncode == 2)
        r = gl(script, env, 'policy', 'show')
        expect(f'policy: the built-in numbers are 6 compute units and 3 browser jobs, got {r.stdout!r}',
               '"compute_units": 6' in r.stdout and '"browser_jobs": 3' in r.stdout and '"builtin"' in r.stdout)
        r = gl(script, env, 'policy', 'set', 'compute_units=4')
        r2 = gl(script, env, 'run', '--need', 'compute_units=5', '--', 'true')
        expect(f'policy: set lowers the capacity so a need of 5 is too_large, got {r.returncode} {r2.returncode} {r2.stderr!r}',
               r.returncode == 0 and r2.returncode == 3 and r2.stderr.startswith('gate_lock: too_large'))
        r = gl(script, env, 'policy', 'reset')
        r2 = gl(script, env, 'run', '--need', 'compute_units=5', '--', 'true')
        expect(f'policy: reset restores the built-in numbers, got {r.returncode} {r2.returncode} {r2.stderr!r}', r.returncode == 0 and r2.returncode == 0)
        r = gl(script, env, 'capabilities', '--json')
        expect(f'capabilities: protocol and policy, got {r.stdout[:200]!r}', r.returncode == 0 and PROTOCOL in r.stdout and '"source"' in r.stdout)
        legacy = pathlib.Path(env['TMPDIR']) / 'sdlc-gate-locks'
        legacy.mkdir()
        (legacy / 'slot-0').write_text(json.dumps({'pid': os.getpid(), 'start': time.time(), 'name': 'oldholder', 'cmd': 'x'}))
        r = gl(script, env, 'run', '--need', 'compute_units=4', '--timeout', '1', '--', 'true')
        expect(f'legacy: a live old-version holder is charged 3 compute units, so a need of 4 waits, got rc={r.returncode} {r.stderr!r}',
               r.returncode == 3 and r.stderr.startswith('gate_lock: timeout'))
        r = gl(script, env, 'run', '--need', 'compute_units=3', '--timeout', '5', '--', 'true')
        expect(f'legacy: a need that fits beside it runs, got rc={r.returncode} {r.stderr!r}', r.returncode == 0)
        st = gl(script, env, 'status')
        expect(f'legacy: status lists the holder and says protection is partial, got {st.stdout!r}', 'legacy' in st.stdout and 'oldholder' in st.stdout and 'partial' in st.stdout)
        expect('legacy: the old slot file is never touched', (legacy / 'slot-0').exists())

        # 7. reap: which command lines match, then a fake orphan and a fake with a live parent (never a real process:
        #    every reap run here is narrowed by --match to the fakes' unique name), then the negative control
        for cmd, want in (('/x/chrome-headless-shell --headless', True), ('/Applications/Chromium.app/Contents/MacOS/Chromium', True),
                          ('/x/Google Chrome for Testing --remote-debugging-pipe', True), ('node /x/node_modules/playwright/cli.js test', True),
                          ('node /x/node_modules/.bin/vite preview --port 4173', True), ('node /x/vite/bin/vite.js preview', True),
                          ('node /x/node_modules/.bin/vite build', False), ('/usr/bin/python3 server.py', False),
                          ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', False)):
            expect(f'reap match: {cmd!r} should {"" if want else "not "}match', bool(REAP_RE.search(cmd)) == want)
        tok = f'{os.getpid():x}{int(time.time()):x}'
        got = reap_case(script, base, 'real', tok, True)
        expect(f'reap: fake orphan and live-parent fake: {got}', not got)
        pc = 'return ppid == 1 or proc_start(ppid) is None' + '  # PARENT-CHECK'  # joined so this line does not match itself
        expect('negative control: the parent check line is in the script exactly once', src.count(pc) == 1)
        (base / 'mutant-reap').mkdir()
        mutant = base / 'mutant-reap' / 'gate_lock.py'
        mutant.write_text(src.replace(pc, 'return True  # PARENT-CHECK'))
        got = reap_case(mutant, base, 'mutant', tok, False)
        expect(f'negative control: with the parent check removed the live-parent case must fail, got {got}',
               any(x.startswith('live-parent') for x in got))
        for x in got:
            if x.startswith('live-parent'):
                print(f'gate_lock selftest: negative control observed (no parent check): {x[:150]}')
                break

        # 8. isolation, with negative controls: a real-root env or a write under a watched root must be caught
        for label, issued, want in (('the real root', [str(real_root)], 'real state root'), ('no root at all', [None], 'no private'),
                                    ('a root outside the temp dir', ['/tmp/elsewhere-gl'], 'outside the selftest temp dir')):
            got = iso_misses(base, real_root, issued, [])
            expect(f'negative control: a case given {label} must be flagged, got {got}', any(want in x for x in got))
            if got:
                print(f'gate_lock selftest: negative control observed (isolation, {label}): {got[0][:120]}')
        fake_real = base / 'fake-real-root'
        fake_real.mkdir()
        keep_watch, keep_hits = _ISO['watch'], _ISO['hits']
        _ISO['watch'], _ISO['hits'] = [str(fake_real)], []
        (fake_real / 'ledger.json').write_text('{}')
        wrote = list(_ISO['hits'])
        _ISO['watch'], _ISO['hits'] = keep_watch, keep_hits
        expect(f'negative control: an in-process write under a watched root must be recorded, got {wrote}', len(wrote) >= 1)
        if wrote:
            print(f'gate_lock selftest: negative control observed (isolation, in-process write): {wrote[0][-60:]}')
        issued, hits = list(_ISO['issued']), list(_ISO['hits'])
        expect('isolation: the selftest handed out private state roots', len(issued) > 0)
        for x in iso_misses(base, real_root, issued, hits):
            expect(f'isolation: {x}', False)

    if misses:
        print('gate_lock selftest: FAIL, these did not hold:', file=sys.stderr)
        for x in misses:
            print(f'  - {x}', file=sys.stderr)
        return 1
    print('gate_lock selftest: PASS')
    return 0


USAGE = ('usage: gate_lock.py run [--need RES=N,...] [--slots N] [--priority P] [--name X] [--repo PATH] [--nice] [--timeout SECS] [--receipt FILE] -- <cmd...> '
         '| context [--json] | capabilities --json | status [--json] | policy show|set|reset | reset --confirm | reap [--older-than MIN] [--kill] [--match REGEX] | selftest')


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    if argv[:1] == ['status']:
        return cmd_status(argv[1:])
    if argv[:1] == ['context']:
        return cmd_context(argv[1:])
    if argv[:1] == ['capabilities']:
        return cmd_capabilities(argv[1:])
    if argv[:1] == ['policy']:
        return cmd_policy(argv[1:])
    if argv[:1] == ['reset']:
        return cmd_reset(argv[1:])
    if argv[:1] == ['reap']:
        return cmd_reap(argv[1:])
    if argv[:1] != ['run'] or '--' not in argv:
        print(USAGE, file=sys.stderr)
        return 2
    cut = argv.index('--')
    ap = argparse.ArgumentParser(prog='gate_lock.py run', description=__doc__.split('\n')[0])
    ap.add_argument('--slots', type=int, help='demand share: max(1, compute capacity // N) compute units (default env SDLC_GATE_SLOTS; below 1 runs with no admission)')
    ap.add_argument('--need', help='weighted demand, RES=N[,RES=N...] (default: the policy default need)')
    ap.add_argument('--priority', type=int, help='queue priority, higher first (default env SDLC_GATE_PRIORITY, else 0)')
    ap.add_argument('--name', help='holder name shown in status and wait lines (default the command)')
    ap.add_argument('--repo', help='repo identity for round robin (default the git common dir of the cwd)')
    ap.add_argument('--nice', action='store_true', help='run the command at nice 10')
    ap.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help=f'seconds to wait for a grant (default {DEFAULT_TIMEOUT:g}); exit 3 on timeout')
    ap.add_argument('--receipt', help='write a JSON receipt to this file when the run ends')
    a = ap.parse_args(argv[1:cut])
    cmd = argv[cut + 1:]
    if not cmd:
        print('gate_lock.py run: no command after --', file=sys.stderr)
        return 2
    slots = a.slots
    if slots is None and os.environ.get('SDLC_GATE_SLOTS'):
        try:
            slots = int(os.environ['SDLC_GATE_SLOTS'])
        except ValueError:
            print(f'gate_lock.py run: SDLC_GATE_SLOTS must be an integer, got {os.environ["SDLC_GATE_SLOTS"]!r}', file=sys.stderr)
            return 2
    try:
        need = parse_needs(a.need)
        priority = a.priority if a.priority is not None else int(os.environ.get('SDLC_GATE_PRIORITY') or 0)
    except ValueError as e:
        print(f'gate_lock.py run: {e}', file=sys.stderr)
        return 2
    return run(slots, a.name or os.path.basename(cmd[0]), a.nice, a.timeout, cmd, need, priority, a.repo, a.receipt)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
