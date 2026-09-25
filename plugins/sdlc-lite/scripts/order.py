#!/usr/bin/env python3
"""Order role results (<role>-L*.md) in a step or task dir by recorded run order.

Usage: order.py newest <dir> <role>   print the newest result path for the role, or nothing
       order.py selftest              prove the ordering rule on temp fixtures

One rule, written once, read from <dir>/runs.jsonl (file order is run order). File times are
never read, so a fresh clone or a committed .sdlc/ trail orders the same as the machine that ran it.

Rank of a result file:
  1. A record with a "file" field (run.sh writes it) ranks that file by its line index.
  2. Records without "file" (legacy trail) group by (role, level) and pair with that role-level's
     canonical files not already ranked (^<role>-(L<n>)(-<k>)?.md, no suffix is k=1), from the
     end: the last record goes to the highest k. Legacy trails hold overwritten or renamed files.
  3. Anything else is unrecorded (non-canonical names, extra files, no runs.jsonl).
Sort key: unrecorded (0, level number, k, name), recorded (1, rank). Unrecorded sorts first.

Importable from the same scripts/ dir: records, ordered, newest, counts_after.
"""
import json, os, re, sys, tempfile

RESULT = re.compile(r'^([a-z]+)-L(\d+)(?:-(\d+))?\.md$')
LOOSE = re.compile(r'^([a-z]+)-L(\d+)')


def records(d):
    """(index, record) for each good JSON object line of d/runs.jsonl, in file order."""
    path = os.path.join(str(d), 'runs.jsonl')
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.read().splitlines()
    except OSError:
        return []
    out = []
    for i, line in enumerate(lines):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            out.append((i, rec))
    return out


def _results(d):
    """Names of <role>-L*.md files in d, sorted by name."""
    try:
        names = os.listdir(str(d))
    except OSError:
        return []
    return sorted(n for n in names if LOOSE.match(n) and n.endswith('.md')
                  and os.path.isfile(os.path.join(str(d), n)))


def _ranks(d):
    """{file name: rank} for every recorded result file in d."""
    names = set(_results(d))
    ranks = {}
    legacy = {}
    for i, rec in records(d):
        f = rec.get('file')
        if isinstance(f, str) and f:
            if f in names:
                ranks[f] = i
        else:
            legacy.setdefault((rec.get('role'), rec.get('level')), []).append(i)
    for (role, level), idxs in legacy.items():
        canon = []
        for n in names:
            m = RESULT.match(n)
            if m and n not in ranks and m.group(1) == role and f'L{m.group(2)}' == level:
                canon.append((int(m.group(3) or 1), n))
        canon.sort()
        for (_, n), i in zip(reversed(canon), reversed(idxs)):
            ranks[n] = i
    return ranks


def _key(name, ranks):
    if name in ranks:
        return (1, ranks[name])
    m = RESULT.match(name)
    if m:
        return (0, int(m.group(2)), int(m.group(3) or 1), name)
    m = LOOSE.match(name)
    return (0, int(m.group(2)) if m else 0, 1, name)


def ordered(d, role):
    """Paths of role's result files in d, oldest to newest."""
    ranks = _ranks(d)
    names = [n for n in _results(d) if LOOSE.match(n).group(1) == role]
    names.sort(key=lambda n: _key(n, ranks))
    return [os.path.join(str(d), n) for n in names]


def newest(d, role):
    """Path of role's newest result file in d, or None."""
    got = ordered(d, role)
    return got[-1] if got else None


def counts_after(later, earlier):
    """True when later ran at or after earlier, or when either one is unrecorded."""
    later, earlier = str(later), str(earlier)
    rl = _ranks(os.path.dirname(later)).get(os.path.basename(later))
    re_ = _ranks(os.path.dirname(earlier)).get(os.path.basename(earlier))
    if rl is None or re_ is None:
        return True
    return rl >= re_


def selftest():
    misses = []

    def check(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    def base(p):
        return os.path.basename(p) if p else None

    with tempfile.TemporaryDirectory() as tmp:
        count = [0]

        def fixture(files, lines=None, times=None):
            """files oldest-to-newest by creation; times: {name: epoch seconds}, else all equal."""
            count[0] += 1
            d = os.path.join(tmp, f'd{count[0]}')
            os.mkdir(d)
            for n in files:
                with open(os.path.join(d, n), 'w', encoding='utf-8') as f:
                    f.write(f'## {n}\n')
            if lines is not None:
                with open(os.path.join(d, 'runs.jsonl'), 'w', encoding='utf-8') as f:
                    f.write(''.join(line + '\n' for line in lines))
            for n in files:
                t = (times or {}).get(n, 1_700_000_000)
                os.utime(os.path.join(d, n), (t, t))
            return d

        def rec(role, level, file=None):
            r = {'role': role, 'level': level}
            if file:
                r['file'] = file
            return json.dumps(r)

        # (a) records with file; file times set inverse to the true order.
        d = fixture(['builder-L1.md', 'builder-L2.md', 'builder-L2-2.md'],
                    [rec('builder', 'L2', 'builder-L2.md'), rec('builder', 'L2', 'builder-L2-2.md'),
                     rec('builder', 'L1', 'builder-L1.md')],
                    times={'builder-L2.md': 1_700_000_300, 'builder-L2-2.md': 1_700_000_200,
                           'builder-L1.md': 1_700_000_100})
        check('(a) file records order by line, not by file time',
              [base(p) for p in ordered(d, 'builder')]
              == ['builder-L2.md', 'builder-L2-2.md', 'builder-L1.md'])
        check('(a) newest is the last recorded file', base(newest(d, 'builder')) == 'builder-L1.md')

        # (b) legacy trail from bench/results/2026-09-24-button-geometry-model/step-2.
        legacy = [rec('builder', 'L3'), rec('verifier', 'L2'), rec('builder', 'L2'),
                  rec('verifier', 'L1'), rec('builder', 'L3'), rec('verifier', 'L2')]
        files = ['builder-L2.md', 'builder-L3.md', 'verifier-L1.attempt2.md',
                 'verifier-L2.attempt1.md', 'verifier-L2.md']
        d = fixture(files, legacy)
        check('(b) legacy: verifier-L2.md is newest verifier',
              base(newest(d, 'verifier')) == 'verifier-L2.md')
        check('(b) legacy: builder-L3.md is newest builder',
              base(newest(d, 'builder')) == 'builder-L3.md')
        check('(b) legacy: non-canonical names are unrecorded and sort first',
              [base(p) for p in ordered(d, 'verifier')]
              == ['verifier-L1.attempt2.md', 'verifier-L2.attempt1.md', 'verifier-L2.md'])
        check('(b) legacy: builder-L3.md pairs with the last builder L3 record',
              _ranks(d).get('builder-L3.md') == 4 and _ranks(d).get('builder-L2.md') == 2)
        # Pairing from the end: two records, two files, times inverse.
        d = fixture(['builder-L3.md', 'builder-L3-2.md'],
                    [rec('builder', 'L3'), rec('builder', 'L3')],
                    times={'builder-L3.md': 1_700_000_900, 'builder-L3-2.md': 1_700_000_100})
        check('(b) legacy: highest k pairs with the last record',
              base(newest(d, 'builder')) == 'builder-L3-2.md')

        # (c) no runs.jsonl: level, then k, then name; file times inverse.
        d = fixture(['verifier-L2.md', 'verifier-L1-2.md', 'verifier-L1.md', 'verifier-L1.x.md'],
                    times={'verifier-L2.md': 1_700_000_100, 'verifier-L1-2.md': 1_700_000_200,
                           'verifier-L1.md': 1_700_000_400, 'verifier-L1.x.md': 1_700_000_300})
        check('(c) no runs.jsonl: level then k then name',
              [base(p) for p in ordered(d, 'verifier')]
              == ['verifier-L1.md', 'verifier-L1.x.md', 'verifier-L1-2.md', 'verifier-L2.md'])
        check('(c) no result files: newest is None', newest(d, 'builder') is None)

        # (d) counts_after.
        d = fixture(['builder-L3.md', 'verifier-L2.md', 'builder-L3-2.md', 'verifier-L9.x.md'],
                    [rec('builder', 'L3', 'builder-L3.md'), rec('verifier', 'L2', 'verifier-L2.md'),
                     rec('builder', 'L3', 'builder-L3-2.md')])
        j = lambda n: os.path.join(d, n)
        check('(d) counts_after true: verifier after first build',
              counts_after(j('verifier-L2.md'), j('builder-L3.md')) is True)
        check('(d) counts_after false: verifier before the rebuild',
              counts_after(j('verifier-L2.md'), j('builder-L3-2.md')) is False)
        check('(d) counts_after true: unrecorded verifier counts',
              counts_after(j('verifier-L9.x.md'), j('builder-L3-2.md')) is True)
        d2 = fixture(['builder-L1.md', 'verifier-L1.md'])
        check('(d) counts_after true: no runs.jsonl',
              counts_after(os.path.join(d2, 'verifier-L1.md'), os.path.join(d2, 'builder-L1.md')) is True)

        # (e) bad JSON lines are skipped, and the line index still counts them.
        d = fixture(['planner-L2.md', 'planner-L2-2.md'],
                    [rec('planner', 'L2', 'planner-L2-2.md'), '{not json', '', '[1, 2]',
                     rec('planner', 'L2', 'planner-L2.md')],
                    times={'planner-L2.md': 1_700_000_100, 'planner-L2-2.md': 1_700_000_900})
        check('(e) bad lines skipped', [i for i, _ in records(d)] == [0, 4])
        check('(e) newest after bad lines', base(newest(d, 'planner')) == 'planner-L2.md')

    if misses:
        print('order selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('order selftest: PASS')
    return 0


def main(argv):
    if argv == ['selftest']:
        return selftest()
    if len(argv) == 3 and argv[0] == 'newest':
        p = newest(argv[1], argv[2])
        if p:
            print(p)
        return 0
    print(__doc__.split('\n\n')[0].split('\n', 1)[1], file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
