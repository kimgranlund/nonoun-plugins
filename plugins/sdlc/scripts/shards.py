#!/usr/bin/env python3
"""Selftest shards: split one long selftest into named cases that check.sh runs as separate pool jobs.

Usage: shards.py {check <check.sh> | selftest}
  A selftest registers each case with `cases = shards.Cases('fanout')` and `@cases(weight)` on a nested function
  (weight: rough seconds alone), then calls `cases.run()` where its cases used to run. `<script> selftest` runs every
  case in source order. `selftest --shard i/n` runs shard i of n: the cases are packed into n shards by weight (the
  heaviest first, each onto the lightest shard so far, ties to the lower index), so every case is in exactly one
  shard, and run in source order. `selftest --list [--shard i/n]` prints `case <name>` per case and runs nothing.
  Each run ends with `cases: K of N run (shard i/n)`.
  check     reads the `job` lines of <check.sh> that run `<script> selftest --shard i/n`. Per script: one n, the
            indices exactly 1..n, and the shards' `--list` names pairwise disjoint with their union equal to the
            unsharded `--list`, so a dropped job line or a case in no shard fails. Prints one `shards:` line per
            script with the per-shard counts summing to the total; exit 1 on a miss, 2 on bad input.
  selftest  a fixture check.sh and a fixture script: the closure passes, a missing shard line, a pick that drops a
            case, a duplicated case, and mixed n each fail (observed red); pack() puts every case in one shard.
"""
import os
import re
import subprocess
import sys
import tempfile

SPEC_RE = re.compile(r'^([1-9]\d*)/([1-9]\d*)$')
JOB_RE = re.compile(r'^job\s+(?:fast|full)\s+(\S+)\s+python3\s+"\$root/([^"]+\.py)"\s+selftest\s+--shard\s+(\S+)\s*$')


def parse_spec(spec):
    """'i/n' -> (i, n) with 1 <= i <= n, else ValueError."""
    m = SPEC_RE.match(spec or '')
    if not m or not 1 <= int(m.group(1)) <= int(m.group(2)):
        raise ValueError(f'want --shard i/n with 1 <= i <= n, got {spec!r}')
    return int(m.group(1)), int(m.group(2))


def pack(weights, n):
    """Shard index (0-based) per case: heaviest first onto the lightest shard so far, ties to the lower index."""
    load, where = [0.0] * n, [0] * len(weights)
    for k in sorted(range(len(weights)), key=lambda k: (-weights[k], k)):
        s = min(range(n), key=lambda s: (load[s], s))
        where[k] = s
        load[s] += weights[k]
    return where


def selftest_args(argv):
    """(shard spec or None, list_only) from the words after `selftest`; ValueError on anything else."""
    spec, listing, rest = None, False, list(argv)
    while rest:
        a = rest.pop(0)
        if a == '--list':
            listing = True
        elif a == '--shard' and rest:
            spec = rest.pop(0)
            parse_spec(spec)
        else:
            raise ValueError(f'selftest takes [--shard i/n] [--list], got {a!r}')
    return spec, listing


class Cases:
    """The named cases of one selftest, in source order."""

    def __init__(self, prog, spec=None):
        self.prog, self.spec, self.items = prog, spec, []

    def __call__(self, weight):
        def register(fn):
            if any(name == fn.__name__ for name, _, _ in self.items):
                raise ValueError(f'{self.prog} selftest: case {fn.__name__} registered twice')
            self.items.append((fn.__name__, weight, fn))
            return fn
        return register

    def picked(self):
        if not self.spec:
            return list(self.items)
        i, n = parse_spec(self.spec)
        where = pack([w for _, w, _ in self.items], n)
        return [c for k, c in enumerate(self.items) if where[k] == i - 1]

    def tail(self, k):
        return f'cases: {k} of {len(self.items)} run' + (f' (shard {self.spec})' if self.spec else '')

    def list(self, out=sys.stdout):
        got = self.picked()
        for name, _, _ in got:
            print(f'case {name}', file=out)
        print(f'cases: {len(got)} of {len(self.items)}' + (f' (shard {self.spec})' if self.spec else ''), file=out)
        return 0

    def run(self):
        got = self.picked()
        for _, _, fn in got:
            fn()
        print(self.tail(len(got)))
        return len(got)


def listed(script, spec=None):
    """The case names `<script> selftest --list [--shard spec]` prints, else RuntimeError."""
    argv = [sys.executable, script, 'selftest', '--list'] + (['--shard', spec] if spec else [])
    p = subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if p.returncode != 0:
        raise RuntimeError(f'{" ".join(argv[1:])} exited {p.returncode}: {p.stderr.strip()[-300:]}')
    return [ln[5:] for ln in p.stdout.splitlines() if ln.startswith('case ')]


def check(check_sh, out=sys.stdout):
    root = os.path.dirname(os.path.dirname(os.path.abspath(check_sh)))
    try:
        with open(check_sh, encoding='utf-8') as fh:
            text = fh.read()
    except OSError as e:
        print(f'shards.py: {e}', file=sys.stderr)
        return 2
    by_script = {}
    for line in text.splitlines():
        m = JOB_RE.match(line.strip())
        if m:
            by_script.setdefault(m.group(2), []).append((m.group(1), m.group(3)))
    if not by_script:
        print(f'shards: no `selftest --shard` job lines in {check_sh}', file=out)
        return 1
    misses = []
    for rel, jobs in sorted(by_script.items()):
        script = os.path.join(root, rel)
        try:
            specs = [parse_spec(spec) for _, spec in jobs]
            full = listed(script)
            per = {i: listed(script, f'{i}/{n}') for i, n in specs}
        except (ValueError, RuntimeError) as e:
            misses.append(f'{rel}: {e}')
            continue
        ns = sorted({n for _, n in specs})
        idx = sorted(i for i, _ in specs)
        if len(ns) != 1:
            misses.append(f'{rel}: the shard job lines mix n values {ns}')
            continue
        n = ns[0]
        if idx != list(range(1, n + 1)):
            misses.append(f'{rel}: shard job lines {idx} are not exactly 1..{n} (missing '
                          f'{sorted(set(range(1, n + 1)) - set(idx))}, repeated {sorted({i for i in idx if idx.count(i) > 1})})')
        seen = {}
        for i in sorted(per):
            for name in per[i]:
                if name in seen:
                    misses.append(f'{rel}: case {name} is in shard {seen[name]}/{n} and shard {i}/{n}')
                seen.setdefault(name, i)
        lost = [name for name in full if name not in seen]
        extra = [name for name in seen if name not in full]
        if lost:
            misses.append(f'{rel}: {len(lost)} case(s) in no listed shard: {", ".join(lost)}')
        if extra:
            misses.append(f'{rel}: shard case(s) not in the unsharded list: {", ".join(extra)}')
        counts = [len(per[i]) for i in sorted(per)]
        print(f'shards: {rel} {len(counts)} of {n} shards, {"+".join(map(str, counts))} = {sum(counts)} cases, '
              f'unsharded {len(full)}', file=out)
    for m in misses:
        print(f'FAIL: shards: {m}', file=out)
    if misses:
        return 1
    print(f'ok: shards: every case of {len(by_script)} sharded selftest(s) runs in exactly one shard job', file=out)
    return 0


FIXTURE = r'''import os, sys
sys.path.insert(0, {scripts!r})
import shards
def selftest(spec, listing):
    cases = shards.Cases('fake', spec)
    for k, w in enumerate((5, 1, 3, 2, 4)):
        cases(w)(type(lambda: 0)((lambda: None).__code__, {{}}, 'c%d' % k))
    if os.environ.get('FAKE_DROP') and spec:
        keep = cases.picked
        cases.picked = lambda: [c for c in keep() if c[0] != os.environ['FAKE_DROP']]
    if os.environ.get('FAKE_DUP') and spec:
        cases.picked = lambda: list(cases.items)
    return cases.list() if listing else (cases.run() and 0)
spec, listing = shards.selftest_args(sys.argv[2:])
sys.exit(selftest(spec, listing))
'''


def selftest():
    import io
    misses = []

    def expect(label, cond):
        print(f'{"ok" if cond else "FAIL"}: {label}')
        if not cond:
            misses.append(label)

    where = pack([5, 1, 3, 2, 4], 3)
    expect('pack: every case lands in one of the n shards', sorted(set(where)) == [0, 1, 2] and len(where) == 5)
    expect('pack: heaviest first onto the lightest shard (5 | 4+1 | 3+2)', where == [0, 1, 2, 2, 1])
    expect('parse_spec refuses 0/2, 3/2 and a bare 2', all(_raises(parse_spec, s) for s in ('0/2', '3/2', '2', '')))
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'scripts'))
        with open(os.path.join(d, 'scripts', 'fake.py'), 'w', encoding='utf-8') as fh:
            fh.write(FIXTURE.format(scripts=os.path.dirname(os.path.abspath(__file__))))
        sh = os.path.join(d, 'scripts', 'check.sh')

        def run(lines, **env):
            with open(sh, 'w', encoding='utf-8') as fh:
                fh.write(''.join(f'job full fake-{s.replace("/", "-")} python3 "$root/scripts/fake.py" selftest --shard {s}\n'
                                 for s in lines))
            old = {k: os.environ.get(k) for k in env}
            os.environ.update(env)
            try:
                out = io.StringIO()
                rc = check(sh, out)
            finally:
                for k, v in old.items():
                    os.environ.pop(k) if v is None else os.environ.__setitem__(k, v)
            return rc, out.getvalue()

        rc, text = run(['1/3', '2/3', '3/3'])
        expect(f'closure: three shard lines cover the five cases once, got rc={rc} {text!r}',
               rc == 0 and 'scripts/fake.py 3 of 3 shards, 1+2+2 = 5 cases, unsharded 5' in text)
        rc, text = run(['1/3', '3/3'])
        expect(f'negative control: a missing shard job line fails naming it and the lost cases, got rc={rc} {text!r}',
               rc == 1 and 'missing [2]' in text and 'case(s) in no listed shard: c1, c4' in text)
        rc, text = run(['1/3', '2/3', '3/3'], FAKE_DROP='c2')
        expect(f'negative control: a pick that drops a case fails naming it, got rc={rc} {text!r}',
               rc == 1 and 'in no listed shard: c2' in text)
        rc, text = run(['1/2', '2/2'], FAKE_DUP='1')
        expect(f'negative control: a case in two shards fails, got rc={rc} {text!r}',
               rc == 1 and 'case c0 is in shard 1/2 and shard 2/2' in text)
        rc, text = run(['1/2', '2/3', '3/3'])
        expect(f'negative control: mixed n fails, got rc={rc} {text!r}', rc == 1 and 'mix n values [2, 3]' in text)
        p = subprocess.run([sys.executable, os.path.join(d, 'scripts', 'fake.py'), 'selftest', '--shard', '2/3'],
                           capture_output=True, text=True)
        expect(f'a shard run prints how many cases it ran, got {p.stdout!r}', 'cases: 2 of 5 run (shard 2/3)' in p.stdout)
    if misses:
        print(f'shards selftest: FAIL ({len(misses)})')
        return 1
    print('shards selftest: PASS')
    return 0


def _raises(fn, *a):
    try:
        fn(*a)
    except ValueError:
        return True
    return False


def main(argv):
    if argv[:1] == ['selftest'] and len(argv) == 1:
        return selftest()
    if argv[:1] == ['check'] and len(argv) == 2:
        return check(argv[1])
    print(__doc__.split('\n\n')[0] + '\nusage: shards.py {check <check.sh> | selftest}', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
