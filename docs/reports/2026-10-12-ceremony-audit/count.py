#!/usr/bin/env python3
"""Counts behind docs/reports/2026-10-12-ceremony-audit.md (T-0464).

Read-only. Run from the repository root:
    python3 docs/reports/2026-10-12-ceremony-audit/count.py > docs/reports/2026-10-12-ceremony-audit/counts.txt

Sets:
  WINDOW = closed ticket folders .sdlc/.0431-* to .sdlc/.0459-* in this tree (closed since T-0431).
  ALL    = every closed .sdlc/.0NNN-* folder in this tree.
Other repos are read, never written. /tmp/fanout-f5N.log files are read when present.
"""
import glob
import json
import os
import re
import statistics
import subprocess
import sys

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, 'plugins', 'sdlc-lite', 'scripts'))
import order as run_order  # noqa: E402

OTHER = [
    '/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets',
    '/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc',
    '/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc',
]


def read(p):
    try:
        with open(p, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def section(text, name):
    m = re.search(r'^## ' + re.escape(name) + r'[^\n]*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
    return m.group(1).strip() if m else None


def first_line(text, name):
    s = section(text, name)
    if not s:
        return ''
    return next((l.strip() for l in s.splitlines() if l.strip()), '')


def num(d):
    m = re.match(r'\.(\d{4})-', os.path.basename(d))
    return int(m.group(1)) if m else -1


ALL = sorted(d for d in glob.glob('.sdlc/.0[0-9][0-9][0-9]-*') if os.path.isdir(d))
WINDOW = [d for d in ALL if 431 <= num(d) <= 459]


def runs(d):
    out = []
    for p in glob.glob(os.path.join(d, '**', 'runs.jsonl'), recursive=True):
        for line in read(p).splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            r['_dir'] = os.path.dirname(p)
            out.append(r)
    return out


def is_chain(d):
    return bool(glob.glob(os.path.join(d, 'planner-L*.md')) or glob.glob(os.path.join(d, 'step-*')))


def size(d):
    m = re.search(r'^size:\s*(L\d)', read(os.path.join(d, 'handoff.md')), re.M)
    return m.group(1) if m else '?'


def filers(d):
    fs = [os.path.join(d, f) for f in os.listdir(d) if re.match(r'filer-L\d.*\.md$', f)]
    return sorted(fs, key=lambda p: (len(p), p))


def kind(bullet):
    b = bullet.lower()
    if 'red-checkpoint' in b and 'process deviation' in b:
        return 'red-checkpoint: retrospective' if 'retrospective' in b else 'red-checkpoint: missing'
    if re.search(r'flake|flaked|contention|rerun passed|second run exited 0|a rerun passed|full rerun exited 0', b):
        return 'flake'
    if re.search(r'unverified|claim|not independently|rests on|did not run|never ran|proves less|could not|not run', b):
        return 'unverified claim'
    return 'other'


def warning_bullets(text):
    w = section(text, 'Warnings')
    if w is None:
        return None
    if re.match(r'^none\b', w.strip(), re.I) or not w.strip():
        return []
    items = [l[2:] for l in w.splitlines() if l.startswith('- ')]
    return items if items else [w.splitlines()[0]]


def close_mode(d):
    c = first_line(read(os.path.join(d, 'handoff.md')), 'Closed')
    if not c:
        return 'no ## Closed line', c
    if 'warnings acknowledged' in c:
        return '--ack-warnings', c
    if not filers(d):
        return '--reason (no filer)', c
    if 'force' in c.lower():
        return '--force?', c
    return 'plain or --reason', c


def fanout_refusals():
    refused = {}
    for p in sorted(glob.glob('/tmp/fanout-f5[0-9].log')):
        for line in read(p).splitlines():
            m = re.match(r'\[fanout-\w+\] \[\w\] (T-\d{4}) merged, close refused: (\S+): (.*)', line)
            if m:
                why = 'filer warnings open' if 'filer warnings are open' in m.group(3) else 'other: ' + m.group(3)[:60]
                refused.setdefault(m.group(1), []).append((os.path.basename(p), why))
    return refused


def git_close_time(d):
    try:
        out = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%cI', '--', os.path.join(d, 'handoff.md')],
                             capture_output=True, text=True, timeout=60).stdout.split()
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out[-1] if out else None


def iso_min(a, b):
    from datetime import datetime
    fa = datetime.fromisoformat(a.replace('Z', '+00:00'))
    fb = datetime.fromisoformat(b.replace('Z', '+00:00'))
    return round((fb - fa).total_seconds() / 60)


def money(rs):
    return round(sum((r.get('cost_usd') or 0) for r in rs), 2)


def minutes(rs):
    return round(sum((r.get('duration_ms') or 0) for r in rs) / 60000)


def verdict(p):
    v = first_line(read(p), 'Verdict').lower()
    return v.split()[0] if v else '?'


def status(p):
    return first_line(read(p), 'Status').lower()


print('# T-0464 ceremony audit counts')
print(f'WINDOW folders (.sdlc/.0431 to .0459): {len(WINDOW)}; ALL closed folders: {len(ALL)}')

# A. First case, this repo, per ticket
print('\n## A. First case: closed tickets since T-0431 in this tree, one row per ticket')
refused = fanout_refusals()
print('ticket | lane | size | filer files | warning entries by kind (latest filer) | close mode | refused in fanout log | '
      'last run ts | close commit | window min [U]')
tot = {'with_filer': 0, 'retro': 0, 'kinds': {}}
for d in WINDOW:
    t = 'T-' + os.path.basename(d)[1:5]
    fs = filers(d)
    kinds = {}
    if fs:
        tot['with_filer'] += 1
        for b in (warning_bullets(read(fs[-1])) or []):
            k = kind(b)
            kinds[k] = kinds.get(k, 0) + 1
            tot['kinds'][k] = tot['kinds'].get(k, 0) + 1
        if any(kind(b) == 'red-checkpoint: retrospective'
               for f in fs for b in (warning_bullets(read(f)) or [])):
            tot['retro'] += 1
    mode, _ = close_mode(d)
    rs = sorted(runs(d), key=lambda r: r.get('ts', ''))
    last = rs[-1]['ts'] if rs else '-'
    ref = refused.get(t)
    ct = git_close_time(d) if ref else None
    window = iso_min(last, ct) if (ref and ct and last != '-') else '-'
    kd = ', '.join(f'{k} {v}' for k, v in sorted(kinds.items())) or ('None' if fs else 'no filer')
    print(f'{t} | {"chain" if is_chain(d) else "solo"} | {size(d)} | {len(fs)} | {kd} | {mode} | '
          f'{";".join(f"{a} {b}" for a, b in ref) if ref else "no"} | {last} | {ct or "-"} | {window}')
print(f'tickets with a filer: {tot["with_filer"]}; tickets whose filer files carry a retrospective red-checkpoint: '
      f'{tot["retro"]}')
print('entries by kind (latest filer per ticket): ' + ', '.join(f'{k} {v}' for k, v in sorted(tot['kinds'].items())))
print('filer files under .sdlc/.04* (find .sdlc -maxdepth 2 -path ".sdlc/.04*" -name "filer-L1*.md"): '
      + str(len(glob.glob('.sdlc/.04*/filer-L1*.md'))))
print('distinct tickets refused for open filer warnings in /tmp/fanout-f5N.log: '
      + str(sorted(k for k, v in refused.items() if any(w == 'filer warnings open' for _, w in v))))
print('refused for another reason: ' + str(sorted(k for k, v in refused.items()
                                                   if not any(w == 'filer warnings open' for _, w in v))))

# A2. Other repos
print('\n## A2. Filer files in the three other repos (find <root> -maxdepth 2 -name "filer-L1*.md")')
for root in OTHER:
    fs = sorted(os.path.join(root, d, f) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))
                for f in os.listdir(os.path.join(root, d)) if re.match(r'filer-L1.*\.md$', f))
    folders = sorted({os.path.dirname(f) for f in fs})
    kinds, modes, nonempty = {}, {}, 0
    for f in folders:
        latest = filers(f)[-1]
        bs = warning_bullets(read(latest))
        if bs:
            nonempty += 1
        for b in (bs or []):
            k = kind(b)
            kinds[k] = kinds.get(k, 0) + 1
        m, _ = close_mode(f)
        modes[m] = modes.get(m, 0) + 1
        closed = sum(1 for f in folders if os.path.basename(f).startswith('.'))
    print(f'{root}: closed (dot) folders {closed}, filer files {len(fs)}, task folders {len(folders)}, folders whose latest filer has warnings '
          f'{nonempty}; entries by kind {dict(sorted(kinds.items()))}; close modes {dict(sorted(modes.items()))}')

# B. Cost by role and level
print('\n## B. runs.jsonl cost by role and level (dollars, model minutes, runs)')
for label, ds in (('WINDOW', WINDOW), ('ALL', ALL)):
    agg = {}
    for d in ds:
        for r in runs(d):
            k = (r.get('role', '?'), r.get('level', '?'))
            a = agg.setdefault(k, [])
            a.append(r)
    tot_usd = sum(money(v) for v in agg.values())
    print(f'{label}: total ${round(tot_usd, 2)}, {sum(minutes(v) for v in agg.values())} min, '
          f'{sum(len(v) for v in agg.values())} runs')
    for k in sorted(agg):
        print(f'  {label} {k[0]} {k[1]}: runs {len(agg[k])}, ${money(agg[k])}, {minutes(agg[k])} min')

# C. Filer on solo versus chain tickets
print('\n## C. Filer runs on solo versus chain tickets (ALL)')
for lane in ('solo', 'chain'):
    ds = [d for d in ALL if is_chain(d) == (lane == 'chain')]
    fr = [r for d in ds for r in runs(d) if r.get('role') == 'filer']
    with_f = [d for d in ds if filers(d)]
    print(f'{lane}: tickets {len(ds)}, tickets with a filer file {len(with_f)}, filer runs {len(fr)}, '
          f'${money(fr)}, {minutes(fr)} min')

# D. Verifier verdicts and second rounds
print('\n## D. Verifier results (ALL): verdicts, and directories with two or more verifier results')
vf = sorted(p for d in ALL for p in glob.glob(os.path.join(d, '**', 'verifier-L*.md'), recursive=True)
            if re.search(r'verifier-L\d(-\d+)?\.md$', p))
vc = {}
for p in vf:
    vc[verdict(p)] = vc.get(verdict(p), 0) + 1
print(f'verifier result files {len(vf)}; verdicts {dict(sorted(vc.items()))}')
bydir = {}
for p in vf:
    bydir.setdefault(os.path.dirname(p), []).append(p)


def order(dirpath, paths):
    """Oldest to newest by the plugin's own ordering (scripts/order.py), never by mtime."""
    got = run_order.ordered(dirpath, 'verifier')
    return [p for p in got if p in paths] + [p for p in paths if p not in got]


multi = {k: order(k, v) for k, v in bydir.items() if len(v) >= 2}
later = [p for v in multi.values() for p in v[1:]]
later_fail = [p for p in later if verdict(p) == 'fail']
first_fail = [order(k, v)[0] for k, v in bydir.items() if verdict(order(k, v)[0]) == 'fail']
later_after_pass = [v[i] for v in multi.values() for i in range(1, len(v)) if verdict(v[i - 1]) == 'pass']
print(f'directories with >=2 verifier results: {len(multi)}; later-round results {len(later)}; '
      f'later-round fails {len(later_fail)}; later rounds that followed a pass {len(later_after_pass)}')
print(f'first-round verifier fails: {len(first_fail)}')
for p in later_fail:
    print(f'  later-round fail: {p}')
for p in later_after_pass:
    print(f'  round after a pass: {p} -> {verdict(p)}')

# E. Plan-reviewer by level
print('\n## E. Plan-reviewer results (ALL) by level and verdict')
pr = sorted(p for d in ALL for p in glob.glob(os.path.join(d, '**', 'plan-reviewer-L*.md'), recursive=True))
pc = {}
for p in pr:
    lv = re.search(r'plan-reviewer-(L\d)', p).group(1)
    pc.setdefault(lv, {}).setdefault(verdict(p), []).append(p)
for lv in sorted(pc):
    print(f'{lv}: ' + ', '.join(f'{v} {len(ps)}' for v, ps in sorted(pc[lv].items())))
    for v, ps in sorted(pc[lv].items()):
        if v != 'pass':
            for p in ps:
                print(f'  {v}: {p}')
prr = [r for d in ALL for r in runs(d) if r.get('role') == 'plan-reviewer']
print(f'plan-reviewer runs in runs.jsonl (ALL): {len(prr)}, ${money(prr)}, {minutes(prr)} min; '
      f'tickets with a plan-reviewer result: {len({p.split(os.sep)[1] for p in pr})}')
print(f'plan-reviewer results in WINDOW: {sum(1 for p in pr if any(p.startswith(d + os.sep) for d in WINDOW))}')

# F. Full chain for L3 versus solo
print('\n## F. Full chain versus solo by ticket size (ALL, tickets with runs.jsonl spend)')
for sz in ('L1', 'L2', 'L3', 'L4'):
    for lane in ('chain', 'solo'):
        ds = [d for d in ALL if size(d) == sz and is_chain(d) == (lane == 'chain')]
        per = [money(runs(d)) for d in ds if runs(d)]
        mins = [minutes(runs(d)) for d in ds if runs(d)]
        vfail = sum(1 for d in ds for p in glob.glob(os.path.join(d, '**', 'verifier-L*.md'), recursive=True)
                    if verdict(p) == 'fail')
        if ds:
            med = round(statistics.median(per), 2) if per else '-'
            mmed = statistics.median(mins) if mins else '-'
            print(f'{sz} {lane}: tickets {len(ds)}, with spend {len(per)}, total ${round(sum(per), 2)}, '
                  f'median ${med}/ticket, median {mmed} min/ticket, verifier fails {vfail}')

# G. Builder status, inherited red, questions
print('\n## G. Builder and solo result status (ALL)')
bf = sorted(p for d in ALL for p in glob.glob(os.path.join(d, '**', 'builder-L*.md'), recursive=True))
sc = {}
for p in bf:
    s = status(p)
    key = 'inherited red' if s.startswith('inherited red') else (s.split()[0] if s else '?')
    sc[key] = sc.get(key, 0) + 1
    if key == 'inherited red':
        print(f'  inherited red: {p}: {s[:120]}')
print(f'builder results {len(bf)}; status {dict(sorted(sc.items()))}')
qs = [p for p in bf if re.match(r'question:', first_line(read(p), 'Notes'), re.I)]
print(f'builder results whose Notes open with "question:": {len(qs)}')
for p in qs:
    print(f'  question: {p}')

# H. Replans
print('\n## H. Replans (ALL)')
sup = sorted(glob.glob('.sdlc/.0*/step-*.superseded-*'))
print(f'superseded step dirs: {len(sup)} in {len({p.split(os.sep)[1] for p in sup})} tickets')
two_planners = [d for d in ALL if len(glob.glob(os.path.join(d, 'planner-L*.md'))) >= 2]
print(f'tickets with two or more planner results: {len(two_planners)}')
ref = {}
for p in glob.glob('.sdlc/.0*/refusals.jsonl'):
    for line in read(p).splitlines():
        try:
            ref[json.loads(line).get('tool', '?')] = ref.get(json.loads(line).get('tool', '?'), 0) + 1
        except ValueError:
            pass
print(f'refusals.jsonl lines by tool: {dict(sorted(ref.items()))}')
pl = [r for d in ALL for r in runs(d) if r.get('role') == 'planner']
pl2 = [r for d in two_planners for r in runs(d) if r.get('role') == 'planner']
print(f'planner runs (ALL) {len(pl)}, ${money(pl)}, {minutes(pl)} min; planner runs in tickets with >=2 planner '
      f'results {len(pl2)}, ${money(pl2)}, {minutes(pl2)} min')
print('WINDOW tickets with >=2 planner results: ' + ', '.join(os.path.basename(d) for d in two_planners
                                                               if d in WINDOW))

# I. Gate-lock reds
print('\n## I. Gate-lock red or flake mentions in closed records')
gl = []
for d in ALL:
    for p in glob.glob(os.path.join(d, '**', '*.md'), recursive=True):
        t = read(p).lower()
        if re.search(r'gate.lock', t) and re.search(r'flak|contention|timed out|timeout', t):
            gl.append(p)
print(f'files mentioning gate-lock with flake, contention or timeout (ALL): {len(gl)} in '
      f'{len({p.split(os.sep)[1] for p in gl})} tickets')
for p in gl:
    if any(p.startswith(d + os.sep) for d in WINDOW):
        print(f'  WINDOW: {p}')
fl = sum(len(re.findall(r'(?i)gate.*(timed out|timeout)', read(p))) for p in glob.glob('/tmp/fanout-f5[0-9].log'))
print(f'gate timeout lines in /tmp/fanout-f5N.log: {fl}')

# J. Per-ticket spend in WINDOW by role
print('\n## J. WINDOW spend per ticket by role (dollars / model minutes)')
for d in WINDOW:
    rs = runs(d)
    by = {}
    for r in rs:
        by.setdefault(r.get('role', '?') + '-' + str(r.get('level', '?')), []).append(r)
    parts = ', '.join(f'{k} ${money(v)}/{minutes(v)}m' for k, v in sorted(by.items()))
    print(f'{os.path.basename(d)} | {"chain" if is_chain(d) else "solo"} | ${money(rs)} | {minutes(rs)} min | {parts}')
for lane in ('chain', 'solo'):
    ds = [d for d in WINDOW if is_chain(d) == (lane == 'chain')]
    rs = [r for d in ds for r in runs(d)]
    pl = [r for r in rs if r.get('role') in ('planner', 'plan-reviewer', 'filer')]
    print(f'WINDOW {lane}: tickets {len(ds)}, ${money(rs)}, {minutes(rs)} min; planner+plan-reviewer+filer '
          f'${money(pl)}, {minutes(pl)} min')
