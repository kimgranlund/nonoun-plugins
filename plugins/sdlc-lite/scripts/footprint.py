#!/usr/bin/env python3
"""Measure a ticket folder's footprint (files, bytes, steps, role runs) and gate on it.

Usage: footprint.py <ticket dir>                                     print the footprint
       footprint.py check <ticket dir> [--max-files N] [--max-bytes N]   exit 1 if a limit is exceeded
       footprint.py selftest                                         prove the counts on temp fixtures

Output of a measure, one `key: value` per line, in this order:
  ticket, files, bytes, md_bytes, steps, planner_bytes, role_runs,
  then `role_runs <role> <level>: N` per group, sorted by role then level.
files/bytes/md_bytes cover every regular file under the dir (symlinked dirs are not followed).
steps counts immediate subdirs named exactly step-<n>; superseded dirs do not count.
planner_bytes sums top-level planner-L<n>[-<k>].md files.
role_runs counts non-blank lines across every runs.jsonl; a line that is not a JSON object with
string role and level counts in group `unknown ?`.
Read-only: nothing under the measured dir is written. Exit codes: 0 ok, 1 limit exceeded, 2 usage.
"""
import json, os, re, shutil, subprocess, sys, tempfile

STEP = re.compile(r'^step-\d+$')
PLANNER = re.compile(r'^planner-L\d+(-\d+)?\.md$')
USAGE = ('usage: footprint.py <ticket dir>\n'
         '       footprint.py check <ticket dir> [--max-files N] [--max-bytes N]\n'
         '       footprint.py selftest')


def measure(d):
    """Footprint of d as an ordered list of (key, value)."""
    d = str(d)
    files = size = md = runs = 0
    groups = {}
    for root, _dirs, names in os.walk(d, followlinks=False):
        for n in names:
            p = os.path.join(root, n)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            s = os.path.getsize(p)
            files += 1
            size += s
            if n.endswith('.md'):
                md += s
            if n == 'runs.jsonl':
                with open(p, encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        runs += 1
                        key = ('unknown', '?')
                        try:
                            rec = json.loads(line)
                        except ValueError:
                            rec = None
                        if (isinstance(rec, dict) and isinstance(rec.get('role'), str)
                                and isinstance(rec.get('level'), str)):
                            key = (rec['role'], rec['level'])
                        groups[key] = groups.get(key, 0) + 1
    steps = planner = 0
    for e in os.scandir(d):
        if e.is_dir(follow_symlinks=False) and STEP.fullmatch(e.name):
            steps += 1
        elif e.is_file(follow_symlinks=False) and PLANNER.fullmatch(e.name):
            planner += e.stat(follow_symlinks=False).st_size
    out = [('ticket', os.path.basename(os.path.normpath(d))), ('files', files), ('bytes', size),
           ('md_bytes', md), ('steps', steps), ('planner_bytes', planner), ('role_runs', runs)]
    for (role, level) in sorted(groups):
        out.append((f'role_runs {role} {level}', groups[(role, level)]))
    return out


def render(m):
    return ''.join(f'{k}: {v}\n' for k, v in m)


def check(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    d, rest = argv[0], argv[1:]
    limits = {}
    i = 0
    while i < len(rest):
        flag = rest[i]
        if flag not in ('--max-files', '--max-bytes') or i + 1 >= len(rest) or flag in limits:
            print(USAGE, file=sys.stderr)
            return 2
        try:
            limits[flag] = int(rest[i + 1])
        except ValueError:
            print(USAGE, file=sys.stderr)
            return 2
        if limits[flag] < 0:
            print(USAGE, file=sys.stderr)
            return 2
        i += 2
    if not limits or not os.path.isdir(d):
        print(USAGE, file=sys.stderr)
        return 2
    m = dict(measure(d))
    bad = 0
    for flag, key in (('--max-files', 'files'), ('--max-bytes', 'bytes')):
        if flag in limits and m[key] > limits[flag]:
            print(f'footprint: {key} {m[key]} exceeds {flag} {limits[flag]}', file=sys.stderr)
            bad = 1
    if bad:
        return 1
    print('ok')
    return 0


def selftest():
    misses = []

    def ok(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    def write(path, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        return len(data.encode('utf-8'))

    def snap(d):
        return sorted((os.path.relpath(os.path.join(r, n), d), os.path.getsize(os.path.join(r, n)))
                      for r, _ds, ns in os.walk(d) for n in ns)

    me = os.path.abspath(__file__)

    def run(*args):
        p = subprocess.run([sys.executable, me, *args], capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    with tempfile.TemporaryDirectory() as tmp:
        # fix-lane dir: 8 files
        fix = os.path.join(tmp, 'fix-lane')
        fb = fm = 0
        for rel, data in [('handoff.md', '# fix handoff\n'),
                          ('step-1/handoff.md', '## Step 1\nDo a thing.\n'),
                          ('step-1/base-sha', 'abc123\n'),
                          ('step-1/builder-L1.md', '## Status\ndone\n'),
                          ('step-1/builder-L1.attempt.json', '{"n": 1}\n'),
                          ('step-1/verifier-L1.md', '## Verdict\npass\n'),
                          ('step-1/verifier-L1.attempt.json', '{"n": 1}\n'),
                          ('step-1/runs.jsonl', '{"role": "builder", "level": "L1"}\n'
                                                '{"role": "verifier", "level": "L1"}\n')]:
            n = write(os.path.join(fix, rel), data)
            fb += n
            if rel.endswith('.md'):
                fm += n
        before_fix = snap(fix)
        m = dict(measure(fix))
        ok('fix-lane counts', m['ticket'] == 'fix-lane' and m['files'] == 8 and m['bytes'] == fb
           and m['md_bytes'] == fm and m['steps'] == 1 and m['planner_bytes'] == 0
           and m['role_runs'] == 2 and m.get('role_runs builder L1') == 1
           and m.get('role_runs verifier L1') == 1 and len(m) == 9)

        # chained dir
        ch = os.path.join(tmp, 'chained')
        cb = cm = cp = 0
        rows = [('handoff.md', '# chained handoff\n'),
                ('planner-L2.md', '## Plan\nfirst\n'),
                ('planner-L3-2.md', '## Plan\nsecond, longer\n'),
                ('plan-reviewer-L1.md', '## Verdict\npass\n'),
                ('runs.jsonl', '{"role": "planner", "level": "L2"}\nnot json\n\n'
                               '{"role": "planner", "level": "L3"}\n'),
                ('step-1/handoff.md', 's1\n'),
                ('step-1/builder-L2.md', 'b\n'),
                ('step-1/verifier-L1.md', 'v\n'),
                ('step-1/runs.jsonl', '{"role": "builder", "level": "L2"}\n'
                                      '{"role": "verifier", "level": "L1"}\n'),
                ('step-2/handoff.md', 's2\n'),
                ('step-2/builder-L3.md', 'b3\n'),
                ('step-2/verifier-L1.md', 'v1\n'),
                ('step-2/runs.jsonl', '{"role": "builder", "level": "L3"}\n'
                                      '{"role": "verifier", "level": "L1"}\n'
                                      '["role", "level"]\n'),
                ('step-2.superseded-1/builder-L2.md', 'old\n')]
        for rel, data in rows:
            n = write(os.path.join(ch, rel), data)
            cb += n
            if rel.endswith('.md'):
                cm += n
            if PLANNER.fullmatch(rel):
                cp += n
        before_ch = snap(ch)
        m = dict(measure(ch))
        ok('chained counts', m['files'] == len(rows) and m['bytes'] == cb and m['md_bytes'] == cm
           and m['planner_bytes'] == cp and cp > 0 and m['role_runs'] == 8)
        ok('chained steps exclude superseded dir', m['steps'] == 2)
        ok('chained groups', m.get('role_runs planner L2') == 1 and m.get('role_runs planner L3') == 1
           and m.get('role_runs unknown ?') == 2 and m.get('role_runs builder L2') == 1
           and m.get('role_runs builder L3') == 1 and m.get('role_runs verifier L1') == 2)
        keys = [k for k, _ in measure(ch)]
        groups = keys[7:]
        ok('output order', keys[:7] == ['ticket', 'files', 'bytes', 'md_bytes', 'steps',
                                         'planner_bytes', 'role_runs']
           and groups == sorted(groups, key=lambda k: tuple(k.split()[1:])))

        rc, out, _ = run(fix)
        ok('cli measure prints fixed lines', rc == 0 and 'files: 8\n' in out
           and out.startswith('ticket: fix-lane\n'))
        rc, out, _ = run('check', fix, '--max-files', '8')
        ok('check passes at limit', rc == 0 and out.strip() == 'ok')

        extra = os.path.join(tmp, 'fix-extra')
        shutil.copytree(fix, extra)
        write(os.path.join(extra, 'step-1', 'extra.md'), 'x\n')
        rc, _, err = run('check', extra, '--max-files', '8')
        ok('negative control: extra file fails check --max-files', rc == 1 and '--max-files' in err)

        rc, _, err = run('check', fix)
        ok('check with no limit exits 2', rc == 2 and 'usage' in err)
        rc, _, _ = run('check', os.path.join(tmp, 'missing'), '--max-files', '8')
        ok('check on missing dir exits 2', rc == 2)

        ok('measuring writes nothing', snap(fix) == before_fix and snap(ch) == before_ch)

    if misses:
        print('footprint selftest: FAIL, these did not hold:', file=sys.stderr)
        for n in misses:
            print(f'  {n}', file=sys.stderr)
        return 1
    print('footprint selftest: PASS')
    return 0


def main(argv):
    if argv == ['selftest']:
        return selftest()
    if argv and argv[0] == 'check':
        return check(argv[1:])
    if len(argv) != 1 or not os.path.isdir(argv[0]):
        print(USAGE, file=sys.stderr)
        return 2
    sys.stdout.write(render(measure(argv[0])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
