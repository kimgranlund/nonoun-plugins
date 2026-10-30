#!/usr/bin/env python3
"""Measure a ticket folder's footprint (files, bytes, steps, role runs) and gate on it.

Usage: footprint.py <ticket dir> [--session <transcript.jsonl>]      print the footprint
       footprint.py check <ticket dir> [--max-files N] [--max-bytes N]   exit 1 if a limit is exceeded
       footprint.py selftest                                         prove the counts on temp fixtures

Output of a measure, one `key: value` per line, in this order:
  ticket, files, bytes, md_bytes, steps, planner_bytes, role_runs,
  then `role_runs <role> <level>: N` per group, sorted by role then level.
Every count covers the ticket dir and, when it differs, its records dir (order.records_dir:
.sdlc/runtime/tasks/<folder name without leading dots>/); the ticket line stays the ticket dir's basename.
files/bytes/md_bytes cover every regular file under those dirs (symlinked dirs are not followed).
steps counts their immediate subdirs named exactly step-<n>; superseded dirs do not count.
planner_bytes sums their top-level planner-L<n>[-<k>].md files.
role_runs counts non-blank lines across every runs.jsonl; a line that is not a JSON object with
string role and level counts in group `unknown ?`.
With --session, four lines follow: role_cost_usd (sum of runs.jsonl cost_usd, `none` when no record
has one), then the factory session's session_input (input_tokens plus cache_creation_input_tokens),
session_cache_read (cache_read_input_tokens), and session_output (output_tokens), summed over the
transcript's message.usage objects; lines repeating a message.id count once. A transcript with no usage
object prints `none` for all three, never 0.
Read-only: nothing under the measured dir is written. Exit codes: 0 ok, 1 limit exceeded, 2 usage.
"""
import json, os, re, shutil, subprocess, sys, tempfile

import order  # same scripts/ dir: records_dir, where a ticket's runs.jsonl, results and step dirs live

STEP = re.compile(r'^step-\d+$')
PLANNER = re.compile(r'^planner-L\d+(-\d+)?\.md$')
USAGE = ('usage: footprint.py <ticket dir> [--session <transcript.jsonl>]\n'
         '       footprint.py check <ticket dir> [--max-files N] [--max-bytes N]\n'
         '       footprint.py selftest')


def dirs_of(d):
    """The ticket dir, then its records dir when that differs."""
    d = str(d)
    rd = str(order.records_dir(d))
    return [d] if os.path.abspath(rd) == os.path.abspath(d) else [d, rd]


def walk(d):
    """os.walk over the ticket dir and its records dir."""
    for x in dirs_of(d):
        yield from os.walk(x, followlinks=False)


def measure(d):
    """Footprint of d (and its records dir) as an ordered list of (key, value)."""
    d = str(d)
    files = size = md = runs = 0
    groups = {}
    for root, _dirs, names in walk(d):
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
    for e in (e for x in dirs_of(d) if os.path.isdir(x) for e in os.scandir(x)):
        if e.is_dir(follow_symlinks=False) and STEP.fullmatch(e.name):
            steps += 1
        elif e.is_file(follow_symlinks=False) and PLANNER.fullmatch(e.name):
            planner += e.stat(follow_symlinks=False).st_size
    out = [('ticket', os.path.basename(os.path.normpath(d))), ('files', files), ('bytes', size),
           ('md_bytes', md), ('steps', steps), ('planner_bytes', planner), ('role_runs', runs)]
    for (role, level) in sorted(groups):
        out.append((f'role_runs {role} {level}', groups[(role, level)]))
    return out


def role_cost(d):
    """Sum of cost_usd over every runs.jsonl record under d and its records dir, or None when no record has one."""
    total = None
    for root, _dirs, names in walk(d):
        if 'runs.jsonl' not in names:
            continue
        with open(os.path.join(root, 'runs.jsonl'), encoding='utf-8', errors='replace') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                c = rec.get('cost_usd') if isinstance(rec, dict) else None
                if isinstance(c, (int, float)) and not isinstance(c, bool):
                    total = (total or 0) + c
    return total


def session_usage(path):
    """(input, cache_read, output) token sums from a transcript, or None when it has no usage object."""
    seen = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f):
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get('message') if isinstance(rec, dict) else None
            u = msg.get('usage') if isinstance(msg, dict) else None
            if not isinstance(u, dict):
                continue
            mid = msg.get('id')
            seen[mid if isinstance(mid, str) else i] = u
    if not seen:
        return None

    def tok(u, k):
        v = u.get(k)
        return v if isinstance(v, int) and not isinstance(v, bool) else 0
    return (sum(tok(u, 'input_tokens') + tok(u, 'cache_creation_input_tokens') for u in seen.values()),
            sum(tok(u, 'cache_read_input_tokens') for u in seen.values()),
            sum(tok(u, 'output_tokens') for u in seen.values()))


def session_lines(d, transcript):
    cost, use = role_cost(d), session_usage(transcript)
    out = [('role_cost_usd', 'none' if cost is None else round(cost, 6))]
    for i, k in enumerate(('session_input', 'session_cache_read', 'session_output')):
        out.append((k, 'none' if use is None else use[i]))
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

        # --session: factory transcript usage next to role costs
        tr = os.path.join(tmp, 'session.jsonl')
        u1 = '{"input_tokens": 2, "cache_creation_input_tokens": 100, "cache_read_input_tokens": 1000, "output_tokens": 30}'
        u2 = '{"input_tokens": 5, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 2000, "output_tokens": 70}'
        write(tr, '{"type": "user", "message": {"role": "user"}}\nnot json\n'
                  '{"type": "assistant", "message": {"id": "m1", "usage": ' + u1 + '}}\n'
                  '{"type": "assistant", "message": {"id": "m1", "usage": ' + u1 + '}}\n'
                  '{"type": "assistant", "message": {"id": "m2", "usage": ' + u2 + '}}\n')
        ok('session sums usage, a repeated message id once', session_usage(tr) == (107, 3000, 100))
        costed = os.path.join(tmp, 'costed')
        write(os.path.join(costed, 'step-1', 'runs.jsonl'), '{"role": "builder", "level": "L1", "cost_usd": 0.5}\n'
              '{"role": "verifier", "level": "L1", "cost_usd": 0.25}\n')
        rc, out, _ = run(costed, '--session', tr)
        ok('cli --session prints role cost and session tokens', rc == 0 and out.startswith('ticket: costed\n')
           and out.endswith('role_cost_usd: 0.75\nsession_input: 107\nsession_cache_read: 3000\n'
                            'session_output: 100\n'))
        bare = os.path.join(tmp, 'bare.jsonl')
        write(bare, '{"type": "user", "message": {"role": "user", "content": "hi"}}\n')
        rc, out, _ = run(fix, '--session', bare)
        ok('negative control: no usage lines and no cost report none, not zero', rc == 0
           and out.endswith('role_cost_usd: none\nsession_input: none\nsession_cache_read: none\n'
                            'session_output: none\n'))
        zero = os.path.join(tmp, 'zero.jsonl')
        write(zero, '{"message": {"id": "z", "usage": {"input_tokens": 0, "output_tokens": 0}}}\n')
        ok('zero usage reports 0, not none', session_usage(zero) == (0, 0, 0))
        rc, _, err = run(fix, '--session', os.path.join(tmp, 'missing.jsonl'))
        ok('missing transcript exits 2', rc == 2 and 'usage' in err)

        ok('measuring writes nothing', snap(fix) == before_fix and snap(ch) == before_ch)

        # records dir (T-0541): a closed .NNNN ticket whose records sit in .sdlc/runtime/tasks/<key>/, and the same
        # records in place (legacy), count the same; the ticket line stays the ticket dir's name
        for label, runtime in (('records dir: runtime-only fixture', True), ('records dir: legacy fixture', False)):
            sd = os.path.join(tmp, 'rt' if runtime else 'lg', '.sdlc')
            td = os.path.join(sd, '.0001-a')
            rd = os.path.join(sd, 'runtime', 'tasks', '0001-a') if runtime else td
            write(os.path.join(td, 'handoff.md'), '## Goal\na\n')
            write(os.path.join(rd, 'planner-L2.md'), '## Plan\n')
            write(os.path.join(rd, 'runs.jsonl'), '{"role": "solo", "level": "L2", "cost_usd": 2.5}\n')
            write(os.path.join(rd, 'step-1', 'handoff.md'), 's1\n')
            m = dict(measure(td))
            ok(f'{label}: steps, planner_bytes, role_runs and cost under ticket .0001-a',
               m['ticket'] == '.0001-a' and m['files'] == 4 and m['steps'] == 1 and m['planner_bytes'] == 8
               and m['role_runs'] == 1 and m.get('role_runs solo L2') == 1 and role_cost(td) == 2.5
               and os.path.exists(os.path.join(td, 'runs.jsonl')) != runtime)

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
    transcript = None
    if len(argv) == 3 and argv[1] == '--session':
        transcript = argv[2]
        argv = argv[:1]
    if (len(argv) != 1 or not os.path.isdir(argv[0])
            or (transcript is not None and not os.path.isfile(transcript))):
        print(USAGE, file=sys.stderr)
        return 2
    m = measure(argv[0])
    if transcript is not None:
        m += session_lines(argv[0], transcript)
    sys.stdout.write(render(m))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
