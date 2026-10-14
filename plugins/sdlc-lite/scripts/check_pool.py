#!/usr/bin/env python3
"""Check pool: run check.sh's jobs in parallel, keep each job's output whole, and name the failures.

Usage: check_pool.py {run <dir> [--jobs N] | selftest}
  run       each file in <dir>, in name order, is one job: NUL-terminated fields, the job name and then its
            argv (check.sh writes them; no shell parses a command). Up to N jobs run at once (--jobs, else
            SDLC_CHECK_JOBS, else the core count), stdin /dev/null, stdout and stderr captured per job. A line
            `ok: <name> (Ns)` or `FAIL: <name> (exit X, Ns)` prints as each job ends; after the last, each job's
            output prints in list order under `== <name>: ok|FAIL`, then one summary line: `check: N jobs ok in Ms`,
            or `check: K of N jobs failed in Ms, first <name>: <names>`. Exit 1 when any job failed, 2 on bad input.
  selftest  planted jobs: three one-second sleeps overlap (each starts before any ends), --jobs 1 serializes, a planted failing job fails the
            run and is named first with its output kept, a missing command is a failure, not a crash.
"""
import argparse
import io
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor


def read_jobs(d):
    jobs = []
    for f in sorted(os.listdir(d)):
        with open(os.path.join(d, f), 'rb') as fh:
            fields = [x.decode() for x in fh.read().split(b'\0')[:-1]]
        if len(fields) < 2:
            raise ValueError(f'{f}: want a name and a command')
        jobs.append((fields[0], fields[1:]))
    return jobs


def run_one(job, out):
    name, argv = job
    t = time.monotonic()
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc, text = p.returncode, p.stdout.decode(errors='replace')
    except OSError as e:
        rc, text = 127, f'{argv[0]}: {e}\n'
    took = time.monotonic() - t
    print(f'ok: {name} ({took:.0f}s)' if rc == 0 else f'FAIL: {name} (exit {rc}, {took:.0f}s)', file=out, flush=True)
    return rc, text


def run_jobs(jobs, n, out=sys.stdout):
    t = time.monotonic()
    with ThreadPoolExecutor(max(1, n)) as ex:
        res = list(ex.map(lambda j: run_one(j, out), jobs))
    failed = []
    for (name, _), (rc, text) in zip(jobs, res):
        print(f'== {name}: {"ok" if rc == 0 else "FAIL"}', file=out)
        out.write(text if not text or text.endswith('\n') else text + '\n')
        if rc:
            failed.append(name)
    took = time.monotonic() - t
    if failed:
        print(f'check: {len(failed)} of {len(jobs)} jobs failed in {took:.0f}s, first {failed[0]}: {", ".join(failed)}', file=out)
        return 1
    print(f'check: {len(jobs)} jobs ok in {took:.0f}s', file=out)
    return 0


def selftest():
    misses = []

    def check(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    def timed(jobs, n):
        out = io.StringIO()
        t = time.monotonic()
        rc = run_jobs(jobs, n, out)
        return rc, out.getvalue(), time.monotonic() - t

    span = ['python3', '-c', 'import time; t = time.time(); time.sleep(1); print("span", t, time.time())']
    rc, text, _ = timed([(f's{i}', span) for i in range(3)], 3)
    spans = [tuple(map(float, ln.split()[1:])) for ln in text.splitlines() if ln.startswith('span ')]
    # Load-independent: every job started before the first one ended, however slow the interpreters start.
    check('three jobs overlap', rc == 0 and len(spans) == 3 and max(s for s, _ in spans) < min(e for _, e in spans))
    sleep = ['python3', '-c', 'import time; time.sleep(1)']
    rc, _, took = timed([(f's{i}', sleep) for i in range(2)], 1)
    check('--jobs 1 runs one at a time', rc == 0 and took >= 2.0)
    planted = [('pass', ['python3', '-c', 'print("fine")']),
               ('planted', ['python3', '-c', 'print("boom"); raise SystemExit(3)']),
               ('late', ['python3', '-c', 'raise SystemExit(1)'])]
    rc, text, _ = timed(planted, 3)
    check('a planted failing job fails the run', rc == 1)
    check('the first failure is named in list order', 'first planted: planted, late' in text)
    check("the failing job's output is kept under its name", '== planted: FAIL\nboom\n' in text)
    check('a passing job is reported ok', '== pass: ok\nfine\n' in text and 'ok: pass (' in text)
    rc, text, _ = timed([('gone', ['/nonexistent/sdlc-check-command'])], 1)
    check('a missing command is a failure, not a crash', rc == 1 and 'FAIL: gone (exit 127' in text)
    with tempfile.TemporaryDirectory() as d:
        for i, (name, argv) in enumerate(planted):
            with open(os.path.join(d, f'{i:03d}'), 'wb') as fh:
                fh.write(b''.join(x.encode() + b'\0' for x in [name, *argv]))
        check('job files read back as name and argv', read_jobs(d) == planted)
    if misses:
        for m in misses:
            print(f'FAIL: check_pool selftest: {m}')
        return 1
    print('ok: check_pool selftest')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='check_pool.py', description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('run', help='run the jobs in a dir in parallel')
    p.add_argument('dir', help='one job file per job, as check.sh writes them')
    p.add_argument('--jobs', type=int, default=0, help='jobs at once (default SDLC_CHECK_JOBS, else the core count)')
    sub.add_parser('selftest', help='planted jobs, no repo state')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    n = a.jobs or int(os.environ.get('SDLC_CHECK_JOBS') or 0) or os.cpu_count() or 1
    try:
        jobs = read_jobs(a.dir)
    except (OSError, ValueError) as e:
        print(f'check_pool.py: {e}', file=sys.stderr)
        return 2
    return run_jobs(jobs, n)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
