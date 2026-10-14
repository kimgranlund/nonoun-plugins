#!/usr/bin/env python3
"""Order role results (<role>-L*.md, a role such as plan-reviewer may hold hyphens) in a step or task dir by recorded run order.

Usage: order.py newest <dir> <role>   print the newest result path for the role, or nothing
       order.py records-dir <dir>     print the records dir for a task or step dir (no create)
       order.py task-dir <path>       print the task folder for a records or step dir, else exit 1
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

Records dir (records_dir): role results, runs.jsonl and step dirs live in
<nearest .sdlc>/runtime/tasks/<folder name without leading dots>/, first match wins:
  1. a path already inside <base>/runtime/tasks/ is itself;
  2. a step-<n> dir (or step-<n>.superseded-<k>) is records_dir(parent)/<name>;
  3. an existing <base>/runtime/tasks/<key>;
  4. legacy: the dir holds runs.jsonl, a *.attempt.json, a role result, or a step-<n> dir that
     holds one of those; records stay in place;
  5. else <base>/runtime/tasks/<key>.
<base> is the nearest ancestor named .sdlc, else the dir's parent. skips.md is no marker.
scripts/records.sh holds the same rule for bash. task_dir maps a records dir back.

Importable from the same scripts/ dir: records, ordered, newest, counts_after, records_dir, task_dir.
"""
import json, os, pathlib, re, sys, tempfile

RESULT = re.compile(r'^([a-z][a-z-]*)-L(\d+)(?:-(\d+))?\.md$')
LOOSE = re.compile(r'^([a-z][a-z-]*)-L(\d+)')
STEP = re.compile(r'^step-\d+(?:\.superseded-\d+)?$')


def _base(p):
    """Nearest ancestor of p named .sdlc, else p's parent."""
    q = os.path.dirname(p)
    while True:
        if os.path.basename(q) == '.sdlc':
            return q
        up = os.path.dirname(q)
        if up == q:
            return os.path.dirname(p)
        q = up


def _holds_records(d):
    """True when d holds runs.jsonl, a *.attempt.json, or a role result file."""
    if os.path.exists(os.path.join(d, 'runs.jsonl')):
        return True
    try:
        names = os.listdir(d)
    except OSError:
        return False
    return any(os.path.isfile(os.path.join(d, n))
               and (n.endswith('.attempt.json') or (LOOSE.match(n) and n.endswith('.md')))
               for n in names)


def _legacy(d):
    """True when d records in place: it, or one of its step-<n> dirs, holds records."""
    if _holds_records(d):
        return True
    try:
        names = os.listdir(d)
    except OSError:
        return False
    return any(STEP.match(n) and os.path.isdir(os.path.join(d, n))
               and _holds_records(os.path.join(d, n)) for n in names)


def _resolve(p):
    """(records path, base) for absolute p; base is None for a legacy (in place) result."""
    name = os.path.basename(p)
    base = _base(p)
    tasks = os.path.join(base, 'runtime', 'tasks')
    if p.startswith(tasks + os.sep):
        return p, base
    if STEP.match(name):
        parent, pbase = _resolve(os.path.dirname(p))
        return os.path.join(parent, name), pbase
    key = name.lstrip('.')
    if os.path.isdir(os.path.join(tasks, key)):
        return os.path.join(tasks, key), base
    if _legacy(p):
        return p, None
    return os.path.join(tasks, key), base


def records_dir(task_dir, create=False):
    """The records dir for a task, step or records dir (rules in the module docstring).

    create=True makes a runtime result (parents too) and writes <base>/runtime/.gitignore ('*')
    when missing. A legacy result is returned as is and never created.
    """
    p, base = _resolve(os.path.abspath(os.fspath(task_dir)))
    if create and base is not None:
        os.makedirs(p, exist_ok=True)
        ignore = os.path.join(base, 'runtime', '.gitignore')
        if not os.path.exists(ignore):
            with open(ignore, 'w', encoding='utf-8') as f:
                f.write('*\n')
    return pathlib.Path(p)


def task_dir(path):
    """The task folder for a records dir under <base>/runtime/tasks/<key>, else None.

    Any other path: a step-<n> dir gives its parent, everything else itself.
    """
    p = os.path.abspath(os.fspath(path))
    base = _base(p)
    tasks = os.path.join(base, 'runtime', 'tasks')
    if p.startswith(tasks + os.sep):
        key = p[len(tasks) + 1:].split(os.sep, 1)[0]
        for c in (key, '.' + key, os.path.join('tickets', key), os.path.join('tickets', '.' + key),
                  os.path.join('work', key), os.path.join('work', '.' + key)):
            d = os.path.join(base, c)
            if os.path.isfile(os.path.join(d, 'handoff.md')):
                return pathlib.Path(d)
        return None
    if STEP.match(os.path.basename(p)):
        return pathlib.Path(os.path.dirname(p))
    return pathlib.Path(p)


def records(d):
    """(index, record) for each good JSON object line of d/runs.jsonl, in file order."""
    path = os.path.join(str(records_dir(d)), 'runs.jsonl')
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
    """Names of <role>-L*.md files in d's records dir, sorted by name."""
    d = records_dir(d)
    try:
        names = os.listdir(str(d))
    except OSError:
        return []
    return sorted(n for n in names if LOOSE.match(n) and n.endswith('.md')
                  and os.path.isfile(os.path.join(str(d), n)))


def _ranks(d):
    """{file name: rank} for every recorded result file in d's records dir."""
    d = records_dir(d)
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
    """Paths of role's result files in d's records dir, oldest to newest."""
    d = records_dir(d)
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

        # (f) hyphenated role: recorded order by runs.jsonl line, not file time; role 'plan' finds nothing.
        d = fixture(['plan-reviewer-L1.md', 'plan-reviewer-L1-2.md'],
                    [rec('plan-reviewer', 'L1', 'plan-reviewer-L1-2.md'),
                     rec('plan-reviewer', 'L1', 'plan-reviewer-L1.md')],
                    times={'plan-reviewer-L1.md': 1_700_000_100, 'plan-reviewer-L1-2.md': 1_700_000_900})
        check('(f) plan-reviewer results order by line, not by file time',
              [base(p) for p in ordered(d, 'plan-reviewer')]
              == ['plan-reviewer-L1-2.md', 'plan-reviewer-L1.md'])
        check('(f) newest plan-reviewer is the last recorded file',
              base(newest(d, 'plan-reviewer')) == 'plan-reviewer-L1.md')
        check('(f) role plan finds nothing', newest(d, 'plan') is None and ordered(d, 'plan') == [])

    with tempfile.TemporaryDirectory() as tmp:
        tmp = os.path.abspath(tmp)
        sd = os.path.join(tmp, '.sdlc')
        rt = os.path.join(sd, 'runtime', 'tasks')

        def mk(rel, files=()):
            d = os.path.join(sd, rel)
            os.makedirs(d, exist_ok=True)
            for n in files:
                with open(os.path.join(d, n), 'w', encoding='utf-8') as f:
                    f.write('x\n')
            return d

        rd = lambda p: str(records_dir(p))
        check('(g) records_dir: a new folder goes to runtime',
              rd(mk('0001-a')) == os.path.join(rt, '0001-a'))
        check('(g) records_dir: a dotted folder drops its leading dot',
              rd(mk('.0002-b')) == os.path.join(rt, '0002-b'))
        check('(g) records_dir: a step dir nests in its task records dir',
              rd(mk('.0002-b/step-2')) == os.path.join(rt, '0002-b', 'step-2')
              and rd(os.path.join(sd, '0001-a', 'step-1.superseded-1'))
              == os.path.join(rt, '0001-a', 'step-1.superseded-1'))
        legacy = [('0003-c', ['runs.jsonl']), ('0004-d', ['planner-L2.md']),
                  ('0005-e', ['builder-L2-2.md']), ('0006-f', ['builder-L3.attempt.json'])]
        check('(g) records_dir: legacy markers keep records in place',
              all(rd(mk(k, fs)) == os.path.join(sd, k) for k, fs in legacy)
              and rd(mk('0007-g/step-1', ['verifier-L1.md'])[:-len('/step-1')])
              == os.path.join(sd, '0007-g')
              and rd(os.path.join(sd, '0007-g', 'step-1')) == os.path.join(sd, '0007-g', 'step-1'))
        check('(g) records_dir: handoff.md and skips.md only goes to runtime',
              rd(mk('0008-h', ['handoff.md', 'skips.md'])) == os.path.join(rt, '0008-h'))
        mk('0009-i', ['runs.jsonl'])
        mk('runtime/tasks/0009-i')
        check('(g) records_dir: an existing runtime dir wins over legacy markers',
              rd(os.path.join(sd, '0009-i')) == os.path.join(rt, '0009-i')
              and rd(os.path.join(rt, '0009-i')) == os.path.join(rt, '0009-i'))
        ignore = os.path.join(sd, 'runtime', '.gitignore')
        no_side_effect = not os.path.exists(ignore)
        p = records_dir(os.path.join(sd, '0010-j'), create=True)
        with open(ignore, encoding='utf-8') as f:
            body = f.read()
        legacy_kept = str(records_dir(os.path.join(sd, '0003-c'), create=True)) == os.path.join(sd, '0003-c')
        check('(g) records_dir: create makes the dir and writes runtime/.gitignore',
              no_side_effect and p.is_dir() and body == '*\n' and legacy_kept)
        os.makedirs(os.path.join(sd, 'tickets', '.0011-k'))
        mk('tickets/.0011-k', ['handoff.md'])
        mk('0001-a', ['handoff.md'])
        check('(g) task_dir: a runtime step dir maps to its task folder',
              str(task_dir(os.path.join(rt, '0001-a', 'step-1'))) == os.path.join(sd, '0001-a')
              and str(task_dir(os.path.join(rt, '0011-k'))) == os.path.join(sd, 'tickets', '.0011-k'))
        check('(g) task_dir: no handoff gives None; a task-side step dir gives its parent',
              task_dir(os.path.join(rt, '0099-z')) is None
              and str(task_dir(os.path.join(sd, '0001-a', 'step-2'))) == os.path.join(sd, '0001-a')
              and str(task_dir(os.path.join(sd, '0001-a'))) == os.path.join(sd, '0001-a'))

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
    if len(argv) == 2 and argv[0] == 'records-dir':
        print(records_dir(argv[1]))
        return 0
    if len(argv) == 2 and argv[0] == 'task-dir':
        t = task_dir(argv[1])
        if t is None:
            return 1
        print(t)
        return 0
    usage = next(b for b in __doc__.split('\n\n') if b.startswith('Usage:'))
    print(usage, file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
