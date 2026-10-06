#!/usr/bin/env python3
"""Machine-wide semaphore for heavy gates (npm test, browser shards, tsc): at most N run at once across
every session and repo, so a pile of lanes does not run the machine out of CPU and memory.

Usage: gate_lock.py run [--slots N] [--name X] [--nice] [--timeout SECS] -- <cmd...>
       gate_lock.py status
       gate_lock.py reap [--older-than MIN] [--kill] [--match REGEX]
       gate_lock.py selftest

  run     takes one of N slots (--slots, else env SDLC_GATE_SLOTS, else 2), runs the command in it, releases
          the slot, and exits with the command's status (a command killed by signal n gives 128+n, a command
          that cannot start gives 127 or 126). The lock dir is ${TMPDIR:-/tmp}/sdlc-gate-locks, one file
          slot-<i> per slot holding the holder's pid, start time, name (--name, default the command) and
          command; the file is created exclusively (written whole, then hard-linked into place) under a short
          flock, so two runs never share a slot. A slot whose pid is dead (gone, a zombie, or reused by a
          process that started after the slot was taken) is stolen. A full lock dir makes the run wait up to
          --timeout seconds (default 1800); every SDLC_GATE_REPORT_SECS (default 15) of waiting it prints
          who holds the slots on stderr. A timeout prints one stderr line and exits 3.
          The command runs in its own process group with SDLC_GATE_WORKERS=max(1, floor(cpus / slots)) in its
          environment (for Playwright and vitest worker settings) and SDLC_GATE_LOCK_HELD=1; a `run` inside
          a command that already holds a slot runs its command with no second slot, so nesting cannot
          deadlock. --nice runs the command at nice 10. On SIGTERM, SIGINT, or SIGHUP the command's process
          group is killed first (SIGTERM, then SIGKILL after 5 s), then the slot is released, and the exit is
          128+signal. Fewer than 1 slot (SDLC_GATE_SLOTS=0) runs the command with no lock and no env change.
  status  lists the slot files: slot, pid, name, age (a dead holder is marked); `no holders` when empty.
  reap    lists leftover browser processes from finished runs and stops nothing: a process whose command line
          matches chrome-headless-shell, chromium, chrome for testing, playwright, or vite preview (case
          ignored), whose parent pid is 1 or no longer exists, and that has run at least --older-than minutes
          (default 30). A matching process with a live parent is never listed as stoppable and never stopped
          (a count of those is printed). --kill sends each listed pid SIGTERM, SIGKILL after 2 s, and prints
          each pid it stops; the process is checked again just before each signal. --match REGEX only narrows
          the set (the selftest uses it so it never touches a real process). Review the list first: a browser
          you started yourself from the desktop also has parent pid 1 and matches by name when it is Chromium.
  selftest  real child processes in a temp TMPDIR: two holders run and a third waits, then runs when one
          exits; a SIGKILLed holder's slot is stolen; SDLC_GATE_WORKERS and the exit status reach and leave
          the command; the timeout exits 3; SIGTERM kills the command and frees the slot; and a negative
          control, a copy with the slot cap removed, must fail the three-holder case. The reap cases use a fake
          orphan (double fork, parent pid 1) and a fake with a live parent, both named to match: by default the
          orphan is listed and stays alive, --kill stops it, the live-parent fake is neither listed nor stopped,
          and a copy with the parent check removed must list the live-parent fake.
"""
import argparse, fcntl, json, os, pathlib, re, shlex, shutil, signal, subprocess, sys, tempfile, time

DEFAULT_SLOTS = 2
DEFAULT_TIMEOUT = 1800.0
POLL = 0.2
KILL_GRACE = 5.0
PID_SLACK = 5.0  # a live pid that started this much after the slot was taken is a reused pid
SLOT_RE = re.compile(r'slot-(\d+)$')


def lock_dir():
    return pathlib.Path(os.environ.get('TMPDIR') or '/tmp') / 'sdlc-gate-locks'


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
    """None when pid is gone or a zombie; else its start time (epoch seconds), 0.0 when that is unknown."""
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


def holder_alive(h):
    st = proc_start(h['pid'])
    if st is None:
        return False
    return not (st and h.get('start') and st > h['start'] + PID_SLACK)


def read_slot(path):
    try:
        d = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) and isinstance(d.get('pid'), int) else None


def slot_range(slots):
    return range(slots)  # SLOT-CAP: the selftest's negative control removes this cap


def try_acquire(d, slots, name, cmd, tmp):
    """The index of a slot now held by this process, or None when all are held by live processes."""
    with open(d / '.mutex', 'a') as mx:
        fcntl.flock(mx, fcntl.LOCK_EX)
        for i in slot_range(slots):
            path = d / f'slot-{i}'
            if path.exists():
                h = read_slot(path)
                if h and holder_alive(h):
                    continue
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
                except OSError:
                    continue
            try:
                tmp.write_text(json.dumps({'pid': os.getpid(), 'start': time.time(), 'name': name, 'cmd': cmd[:200]}))
                os.link(tmp, path)
            except FileExistsError:
                continue
            return i
    return None


def release_all(d, pid):
    for path in d.glob('slot-*'):
        h = read_slot(path)
        if h and h['pid'] == pid:
            try:
                path.unlink()
            except OSError:
                pass


def holders_text(d):
    now, out = time.time(), []
    for path in sorted(d.glob('slot-*')):
        h = read_slot(path)
        if h:
            out.append(f"{path.name} pid {h['pid']} name {h.get('name', '?')} age {int(now - h.get('start', now))}s")
    return '; '.join(out) or 'no holders'


class Stop(Exception):
    def __init__(self, sig):
        super().__init__(sig)
        self.sig = sig


def on_signal(sig, frame):
    raise Stop(sig)


def kill_group(child):
    try:
        os.killpg(child.pid, signal.SIGTERM)
    except OSError:
        pass
    end = time.time() + KILL_GRACE
    while child.poll() is None and time.time() < end:
        time.sleep(0.05)
    if child.poll() is None:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except OSError:
            pass
        child.wait()


def run(slots, name, nice, timeout, cmd):
    held = os.environ.get('SDLC_GATE_LOCK_HELD') == '1'
    env = dict(os.environ)
    if slots >= 1:
        env['SDLC_GATE_WORKERS'] = str(max(1, (os.cpu_count() or 1) // slots))
        env['SDLC_GATE_LOCK_HELD'] = '1'
    d, tmp, child, rc = lock_dir(), None, None, 1
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)
    try:
        if slots >= 1 and not held:
            d.mkdir(parents=True, exist_ok=True)
            tmp = d / f'.tmp-{os.getpid()}'
            t0 = time.time()
            report = float(os.environ.get('SDLC_GATE_REPORT_SECS') or 15)
            next_report = t0 + report
            while try_acquire(d, slots, name, cmd, tmp) is None:
                now = time.time()
                if now >= t0 + timeout:
                    print(f'gate_lock: timeout after {timeout:g}s waiting for a slot of {slots} ({holders_text(d)})', file=sys.stderr)
                    return 3
                if now >= next_report:
                    print(f'gate_lock: {name} waiting for a slot of {slots} ({int(now - t0)}s so far); held by: {holders_text(d)}',
                          file=sys.stderr, flush=True)
                    next_report = now + report
                time.sleep(min(POLL, max(0.01, t0 + timeout - now)))
            waited = time.time() - t0
            if waited >= report:
                print(f'gate_lock: {name} got a slot after {int(waited)}s', file=sys.stderr, flush=True)
        child = subprocess.Popen(cmd, env=env, start_new_session=True,
                                 preexec_fn=(lambda: os.nice(10)) if nice else None)
        rc = child.wait()
        rc = 128 - rc if rc < 0 else rc
    except Stop as stop:
        rc = 128 + stop.sig
    except OSError as e:
        print(f'gate_lock: cannot run {cmd[0]}: {e.strerror or e}', file=sys.stderr)
        rc = 127 if isinstance(e, FileNotFoundError) else 126
    finally:
        for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            signal.signal(s, signal.SIG_IGN)
        if child is not None and child.poll() is None:
            kill_group(child)
        if slots >= 1 and not held:
            release_all(d, os.getpid())
            if tmp is not None:
                try:
                    tmp.unlink()
                except OSError:
                    pass
    return rc


def cmd_status():
    d, now, rows = lock_dir(), time.time(), []
    for path in d.glob('slot-*'):
        m = SLOT_RE.match(path.name)
        h = read_slot(path)
        if m and h:
            dead = '' if holder_alive(h) else '  (dead: will be stolen)'
            rows.append((int(m.group(1)), f"slot {m.group(1)}  pid {h['pid']}  name {h.get('name', '?')}  "
                                          f"age {int(now - h.get('start', now))}s{dead}"))
    print('\n'.join(line for _, line in sorted(rows)) or 'no holders')
    return 0


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


def selftest():
    script = pathlib.Path(__file__).resolve()
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def waitfor(pred, secs=15):
        end = time.time() + secs
        while time.time() < end:
            if pred():
                return True
            time.sleep(0.05)
        return pred()

    def clean_env(tmp, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith('SDLC_GATE_')}
        env['TMPDIR'] = str(tmp)
        env.update(extra)
        return env

    def gl(py, env, *args, timeout=60, **kw):
        return subprocess.run([sys.executable, str(py), *args], env=env, capture_output=True, text=True, timeout=timeout, **kw)

    def holder(py, env, m, n, slots, *extra):
        """A gate_lock run whose command holds its slot until <m>/go-<n> exists; stderr goes to <m>/err-<n>."""
        return subprocess.Popen([sys.executable, str(py), 'run', '--slots', str(slots), '--name', f'H{n}', '--timeout', '60',
                                 *extra, '--', 'sh', '-c', HOLD],
                                env=dict(env, GL_M=str(m), GL_N=str(n)), stdout=subprocess.DEVNULL,
                                stderr=open(m / f'err-{n}', 'w'))

    def three_holders(py, tmp, label):
        """Two slots, three holders: the third must wait (and say so), then run after one exits. Returns misses."""
        m, bad = tmp / f'm-{label}', []
        m.mkdir()
        env = clean_env(tmp / f'tmp-{label}', SDLC_GATE_REPORT_SECS='0.3')
        (tmp / f'tmp-{label}').mkdir()
        procs = []
        try:
            procs = [holder(py, env, m, 1, 2), holder(py, env, m, 2, 2)]
            if not waitfor(lambda: (m / 'started-1').exists() and (m / 'started-2').exists()):
                return ['the first two holders did not start']
            procs.append(holder(py, env, m, 3, 2))
            # the third either says it is waiting (the cap held) or starts (no cap)
            waitfor(lambda: (m / 'started-3').exists() or 'waiting for a slot' in (m / 'err-3').read_text(), 5)
            if (m / 'started-3').exists():
                return ['the third holder started at once with two slots held']
            if label == 'real':
                st = gl(py, env, 'status')
                expect('status lists both holders with their names', st.returncode == 0 and 'name H1' in st.stdout
                       and 'name H2' in st.stdout and 'name H3' not in st.stdout and 'age ' in st.stdout)
                expect('the waiting third holder names the holders on stderr', 'H1' in (m / 'err-3').read_text())
            (m / 'go-1').touch()
            if not waitfor(lambda: (m / 'started-3').exists()):
                bad.append('the third holder did not run after one exited')
            for n in (1, 2, 3):
                (m / f'go-{n}').touch()
            for p in procs:
                if p.wait(timeout=30) != 0:
                    bad.append(f'a holder exited {p.returncode}')
            return bad
        finally:
            for n in (1, 2, 3):
                (m / f'go-{n}').touch()
            for p in procs:
                if p.poll() is None:
                    p.kill()
                    p.wait()

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

    with tempfile.TemporaryDirectory() as t:
        tmp = pathlib.Path(t).resolve()

        # 1. three holders, two slots (real script), then status, then the negative control
        got = three_holders(script, tmp, 'real')
        expect(f'three holders with two slots: {got}', not got)
        src = script.read_text()
        cap = 'return range(slots)' + '  # SLOT-CAP'  # joined so this line does not match itself
        expect('negative control: the slot cap line is in the script exactly once', src.count(cap) == 1)
        mutant_src = src.replace(cap, 'return range(slots + 1000)  # SLOT-CAP')
        (tmp / 'mutant').mkdir()
        mutant = tmp / 'mutant' / 'gate_lock.py'
        mutant.write_text(mutant_src)
        got = three_holders(mutant, tmp, 'mutant')
        expect(f'negative control: with the slot cap removed the three-holder case must fail, got {got}',
               got and 'third holder started at once' in got[0])
        if got:
            print(f'gate_lock selftest: negative control observed (no slot cap): {got[0]}')

        # 2. a SIGKILLed holder's slot is stolen (the zombie is not reaped yet)
        env = clean_env(tmp / 'tmp-steal')
        (tmp / 'tmp-steal').mkdir()
        m = tmp / 'm-steal'
        m.mkdir()
        a = subprocess.Popen([sys.executable, str(script), 'run', '--slots', '1', '--name', 'victim', '--', 'sh', '-c',
                              'echo $$ >"$GL_M/a.pid"; ' + HOLD], env=dict(env, GL_M=str(m), GL_N='a'),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            ok = waitfor(lambda: (m / 'started-a').exists())
            expect('steal: the victim holder started', ok)
            st = gl(script, env, 'status')
            expect(f'steal: status shows the victim, got {st.stdout!r}', 'name victim' in st.stdout)
            a.kill()
            t0 = time.time()
            b = gl(script, dict(env, GL_M=str(m)), 'run', '--slots', '1', '--timeout', '20', '--', 'sh', '-c',
                   'touch "$GL_M/b-ran"')
            expect(f'steal: the next run took the dead holder\'s slot, rc={b.returncode} stderr={b.stderr!r}',
                   b.returncode == 0 and (m / 'b-ran').exists() and time.time() - t0 < 15)
            st = gl(script, env, 'status')
            expect(f'steal: no holders left, got {st.stdout!r}', st.stdout.strip() == 'no holders')
        finally:
            a.wait()
            (m / 'go-a').touch()
            try:
                os.killpg(int((m / 'a.pid').read_text()), signal.SIGKILL)
            except (OSError, ValueError):
                pass

        # 3. SDLC_GATE_WORKERS, the exit status, an unrunnable command, pass-through, and nice
        env = clean_env(tmp / 'tmp-misc')
        (tmp / 'tmp-misc').mkdir()
        cpus = os.cpu_count() or 1
        for slots, want in ((2, max(1, cpus // 2)), (1, cpus), (100000, 1)):
            r = gl(script, env, 'run', '--slots', str(slots), '--', 'sh', '-c', 'echo "$SDLC_GATE_WORKERS"')
            expect(f'workers: {slots} slots gives {want}, got {r.stdout!r} {r.stderr!r}', r.stdout.strip() == str(want))
        r = gl(script, dict(env, SDLC_GATE_SLOTS='4'), 'run', '--', 'sh', '-c', 'echo "$SDLC_GATE_WORKERS"')
        expect(f'workers: SDLC_GATE_SLOTS=4 gives {max(1, cpus // 4)}, got {r.stdout!r}', r.stdout.strip() == str(max(1, cpus // 4)))
        for argv, want in ((['sh', '-c', 'exit 7'], 7), (['sh', '-c', 'exit 0'], 0), (['sh', '-c', 'kill -9 $$'], 137),
                           (['no-such-command-gate-lock'], 127)):
            r = gl(script, env, 'run', '--slots', '2', '--', *argv)
            expect(f'exit status: {argv[-1]} gives {want}, got {r.returncode} {r.stderr!r}', r.returncode == want)
        r = gl(script, env, 'run', '--slots', '0', '--', 'sh', '-c', 'echo "[$SDLC_GATE_WORKERS][$SDLC_GATE_LOCK_HELD]"')
        expect(f'pass-through: 0 slots runs with no env change, got {r.stdout!r}', r.stdout.strip() == '[][]')
        r = gl(script, dict(env, SDLC_GATE_SLOTS='0'), 'run', '--', 'sh', '-c', 'echo "[$SDLC_GATE_WORKERS]"')
        expect(f'pass-through: SDLC_GATE_SLOTS=0 runs with no env change, got {r.stdout!r}', r.stdout.strip() == '[]')
        probe = 'import os; print(os.nice(0))'
        base = int(subprocess.run([sys.executable, '-c', probe], env=env, capture_output=True, text=True).stdout.strip())
        r = gl(script, env, 'run', '--slots', '2', '--nice', '--', sys.executable, '-c', probe)
        expect(f'nice: --nice raises niceness 10 from {base}, got {r.stdout!r} {r.stderr!r}',
               r.stdout.strip() == str(min(19, base + 10)))
        r = gl(script, env, 'run', '--slots', '2', '--', 'sh', '-c', f'{shlex.quote(sys.executable)} {shlex.quote(str(script))} run --slots 1 -- sh -c "echo inner"')
        expect(f'nesting: a run inside a held slot runs without a second slot, got {r.stdout!r} {r.stderr!r}',
               r.returncode == 0 and r.stdout.strip() == 'inner')

        # 4. the timeout path: exit 3 and one stderr line
        env = clean_env(tmp / 'tmp-timeout')
        (tmp / 'tmp-timeout').mkdir()
        m = tmp / 'm-timeout'
        m.mkdir()
        h = holder(script, env, m, 1, 1)
        try:
            expect('timeout: the holder started', waitfor(lambda: (m / 'started-1').exists()))
            t0 = time.time()
            r = gl(script, env, 'run', '--slots', '1', '--timeout', '1', '--', 'true')
            lines = [x for x in r.stderr.splitlines() if x.strip()]
            expect(f'timeout: exits 3 with one stderr line naming the holder, got rc={r.returncode} {r.stderr!r}',
                   r.returncode == 3 and len(lines) == 1 and lines[0].startswith('gate_lock: timeout') and 'H1' in lines[0])
            expect('timeout: it waited about the timeout', 0.9 <= time.time() - t0 < 14)
        finally:
            (m / 'go-1').touch()
            h.wait()

        # 5. SIGTERM kills the command's process group, frees the slot, and exits 128+15
        env = clean_env(tmp / 'tmp-term')
        (tmp / 'tmp-term').mkdir()
        m = tmp / 'm-term'
        m.mkdir()
        a = subprocess.Popen([sys.executable, str(script), 'run', '--slots', '1', '--name', 'term', '--', 'sh', '-c',
                              'echo $$ >"$GL_M/c.pid"; touch "$GL_M/started"; exec sleep 60'],
                             env=dict(env, GL_M=str(m)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            expect('sigterm: the command started', waitfor(lambda: (m / 'started').exists()))
            cpid = int((m / 'c.pid').read_text() or 0) if (m / 'c.pid').exists() else 0
            a.terminate()
            rc = a.wait(timeout=30)
            expect(f'sigterm: exits 143, got {rc}', rc == 143)

            def dead(pid):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    return True
                return False
            expect('sigterm: the command was killed', cpid > 0 and waitfor(lambda: dead(cpid), 10))
            st = gl(script, env, 'status')
            expect(f'sigterm: the slot is released, got {st.stdout!r}', st.stdout.strip() == 'no holders')
        finally:
            if a.poll() is None:
                a.kill()
                a.wait()

        # 6. reap: which command lines match, then a fake orphan and a fake with a live parent (never a real process:
        #    every reap run here is narrowed by --match to the fakes' unique name), then the negative control
        for cmd, want in (('/x/chrome-headless-shell --headless', True), ('/Applications/Chromium.app/Contents/MacOS/Chromium', True),
                          ('/x/Google Chrome for Testing --remote-debugging-pipe', True), ('node /x/node_modules/playwright/cli.js test', True),
                          ('node /x/node_modules/.bin/vite preview --port 4173', True), ('node /x/vite/bin/vite.js preview', True),
                          ('node /x/node_modules/.bin/vite build', False), ('/usr/bin/python3 server.py', False),
                          ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', False)):
            expect(f'reap match: {cmd!r} should {"" if want else "not "}match', bool(REAP_RE.search(cmd)) == want)
        tok = f'{os.getpid():x}{int(time.time()):x}'
        got = reap_case(script, tmp, 'real', tok, True)
        expect(f'reap: fake orphan and live-parent fake: {got}', not got)
        pc = 'return ppid == 1 or proc_start(ppid) is None' + '  # PARENT-CHECK'  # joined so this line does not match itself
        expect('negative control: the parent check line is in the script exactly once', src.count(pc) == 1)
        (tmp / 'mutant-reap').mkdir()
        mutant = tmp / 'mutant-reap' / 'gate_lock.py'
        mutant.write_text(src.replace(pc, 'return True  # PARENT-CHECK'))
        got = reap_case(mutant, tmp, 'mutant', tok, False)
        expect(f'negative control: with the parent check removed the live-parent case must fail, got {got}',
               any(x.startswith('live-parent') for x in got))
        for x in got:
            if x.startswith('live-parent'):
                print(f'gate_lock selftest: negative control observed (no parent check): {x[:150]}')
                break

    if misses:
        print('gate_lock selftest: FAIL, these did not hold:', file=sys.stderr)
        for x in misses:
            print(f'  - {x}', file=sys.stderr)
        return 1
    print('gate_lock selftest: PASS')
    return 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    if argv[:1] == ['status']:
        return cmd_status()
    if argv[:1] == ['reap']:
        return cmd_reap(argv[1:])
    if argv[:1] != ['run'] or '--' not in argv:
        print('usage: gate_lock.py run [--slots N] [--name X] [--nice] [--timeout SECS] -- <cmd...> | status | reap [--older-than MIN] [--kill] [--match REGEX] | selftest',
              file=sys.stderr)
        return 2
    cut = argv.index('--')
    ap = argparse.ArgumentParser(prog='gate_lock.py run', description=__doc__.split('\n')[0])
    ap.add_argument('--slots', type=int, help=f'slots (default env SDLC_GATE_SLOTS, else {DEFAULT_SLOTS}; below 1 runs with no lock)')
    ap.add_argument('--name', help='holder name shown in status and wait lines (default the command)')
    ap.add_argument('--nice', action='store_true', help='run the command at nice 10')
    ap.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help=f'seconds to wait for a slot (default {DEFAULT_TIMEOUT:g}); exit 3 on timeout')
    a = ap.parse_args(argv[1:cut])
    cmd = argv[cut + 1:]
    if not cmd:
        print('gate_lock.py run: no command after --', file=sys.stderr)
        return 2
    slots = a.slots
    if slots is None:
        try:
            slots = int(os.environ.get('SDLC_GATE_SLOTS') or DEFAULT_SLOTS)
        except ValueError:
            print(f'gate_lock.py run: SDLC_GATE_SLOTS must be an integer, got {os.environ["SDLC_GATE_SLOTS"]!r}', file=sys.stderr)
            return 2
    return run(slots, a.name or os.path.basename(cmd[0]), a.nice, a.timeout, cmd)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
