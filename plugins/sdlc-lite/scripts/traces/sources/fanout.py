"""Fanout reader: the facts of one fanout lanes dir (report.md and logs/), in both layouts.

scripts/fanout.py documents the layout. The current one prefixes every log line with the run id
`[fanout-<12 hex>] `, names gate logs gate-<lane>-<id>-<k>-a<n>.log (one file per attempt),
appends to logs/fanout.log, and writes a `- Run:` line in report.md. The pre-T-0155 layout has no
prefixes, gate-<lane>-<id>-<k>.log names (overwritten per run), no fanout.log, and no Run line.

read(lanes_dir) returns one dict:
  report       None when report.md is absent, else {path, run_id (the `- Run:` id or None),
               rows (one {line, lane, ticket, outcome, commit} per `| Lane | Ticket | Outcome |
               Commit |` row, `\\|` unescaped), gates (one {k, command} per `- Gate <k>:` line),
               integration_worktree (or None), external (one {lane, branch, sha} per external
               lane line)};
  fanout_log   one {path, line, run_id, lane, ticket, event} per non-empty line of
               logs/fanout.log (line is 1-based; lane, ticket None when the line does not parse);
  driver_logs  one {lane, ticket, path, lines, run_ids} per logs/<lane>-<id>.log;
  gate_logs    one {lane, ticket, k, attempt, path, lines, run_ids, rc} per
               logs/gate-<lane>-<id>-<k>[-a<n>].log (attempt None for the legacy name);
  landed       the branch of every logs/land.jsonl line, in first-seen order: the lanes
               `fanout.py land` merged, which a pre-T-0730 report.md wrote as external lanes;
  problems     the paths of files that could not be read, which are skipped.
A line's run id is its `[fanout-<12 hex>] ` prefix, None without one; run_ids lists the distinct
ids of a log's lines in first-seen order (None included), and run_id_lines pairs each with the
1-based number of its first line. A gate log's rc is the n of a `red: <gate> rc=<n>` outcome that
a fanout.log line or report row records for that lane, ticket, and gate (the gate k is found from
the report's gate commands, else it is the highest k logged in that run), placed on the newest
attempt that carries the recording run's id (a legacy record, with no id, on the legacy log);
a gate no line records a rc for (a green gate included) keeps rc None.
"""
import json, os, re

RUN_ID = r'fanout-[0-9a-f]{12}'
PREFIX_RE = re.compile(r'^\[(' + RUN_ID + r')\] ')
LANE = r'[a-z0-9]+(?:-[a-z0-9]+)*'
TICKET = r'T-\d{4}'
EVENT_RE = re.compile(r'^\[(' + LANE + r')\] (' + TICKET + r') (.*)$')
GATE_RE = re.compile(r'^gate-(' + LANE + r')-(' + TICKET + r')-(\d+)(?:-a(\d+))?\.log$')
DRIVER_RE = re.compile(r'^(' + LANE + r')-(' + TICKET + r')\.log$')
RED_RE = re.compile(r'^red: (.*) rc=(-?\d+)$')
ROW_RE = re.compile(r'^\|(.*)\|\s*$')
TICK_RE = re.compile(r'`([^`]*)`')


def run_id_of(line):
    m = PREFIX_RE.match(line)
    return m.group(1) if m else None


def _lines(path, problems):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read().splitlines()
    except OSError:
        problems.append(path)
        return None


def _cells(line):
    inner = ROW_RE.match(line).group(1)
    parts = re.split(r'(?<!\\)\|', inner)
    return [p.strip().replace('\\|', '|') for p in parts]


def _report(lanes_dir, problems):
    path = os.path.join(lanes_dir, 'report.md')
    if not os.path.isfile(path):
        return None
    lines = _lines(path, problems)
    if lines is None:
        return None
    rep = {'path': path, 'run_id': None, 'rows': [], 'gates': [], 'integration_worktree': None,
           'external': []}
    in_table = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        ticks = TICK_RE.findall(s)
        if s.startswith('- Run:') and ticks:
            rep['run_id'] = ticks[0]
        elif s.startswith('- Integration worktree:') and ticks:
            rep['integration_worktree'] = ticks[0]
        elif re.match(r'^- Gate \d+:', s) and ticks:
            k = int(re.match(r'^- Gate (\d+):', s).group(1))
            rep['gates'].append({'k': k, 'command': s.split('`', 1)[1].rsplit('`', 1)[0]})
        elif s.startswith('- Lane ') and ': external branch ' in s and len(ticks) >= 2:
            rep['external'].append({'lane': ticks[0], 'branch': ticks[1],
                                    'sha': ticks[2] if len(ticks) > 2 else None})
        elif ROW_RE.match(s):
            c = _cells(s)
            if c[:4] == ['Lane', 'Ticket', 'Outcome', 'Commit']:
                in_table = True
            elif in_table and len(c) == 4 and re.fullmatch(TICKET, c[1]):
                rep['rows'].append({'line': i, 'lane': c[0], 'ticket': c[1], 'outcome': c[2],
                                    'commit': None if c[3] in ('', '-') else c[3]})
        elif in_table and s:
            in_table = False
    return rep


def _fanout_log(logs, problems):
    path = os.path.join(logs, 'fanout.log')
    if not os.path.isfile(path):
        return []
    lines = _lines(path, problems) or []
    out = []
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        rid = run_id_of(line)
        rest = line[len(rid) + 3:] if rid else line
        m = EVENT_RE.match(rest)
        out.append({'path': path, 'line': i, 'run_id': rid,
                    'lane': m.group(1) if m else None, 'ticket': m.group(2) if m else None,
                    'event': m.group(3) if m else rest})
    return out


def _ids(lines):
    ids, first = [], []
    for i, line in enumerate(lines, 1):
        rid = run_id_of(line)
        if rid not in ids:
            ids.append(rid)
            first.append([rid, i])
    return ids, first


def _logs(logs, problems):
    drivers, gates = [], []
    try:
        names = sorted(os.listdir(logs))
    except OSError:
        return drivers, gates
    for name in names:
        path = os.path.join(logs, name)
        g, d = GATE_RE.match(name), DRIVER_RE.match(name)
        if not (g or d) or not os.path.isfile(path):
            continue
        lines = _lines(path, problems)
        if lines is None:
            continue
        ids, first = _ids(lines)
        if g:
            gates.append({'lane': g.group(1), 'ticket': g.group(2), 'k': int(g.group(3)),
                          'attempt': int(g.group(4)) if g.group(4) else None, 'path': path,
                          'lines': len(lines), 'run_ids': ids, 'run_id_lines': first, 'rc': None})
        else:
            drivers.append({'lane': d.group(1), 'ticket': d.group(2), 'path': path,
                            'lines': len(lines), 'run_ids': ids, 'run_id_lines': first})
    drivers.sort(key=lambda r: (r['lane'], r['ticket']))
    gates.sort(key=lambda r: (r['lane'], r['ticket'], r['k'], r['attempt'] or 0))
    return drivers, gates


def _norm(cmd):
    return ' '.join(cmd.split())


def _place_rc(gates, report, run_id, lane, ticket, outcome):
    m = RED_RE.match(outcome or '')
    if not m:
        return
    cmd, rc = _norm(m.group(1)), int(m.group(2))
    mine = [g for g in gates if (g['lane'], g['ticket']) == (lane, ticket)
            and (run_id in g['run_ids'] if run_id else g['attempt'] is None)]
    if not mine and run_id is None:  # a record with no id and no legacy log: the only candidate
        mine = [g for g in gates if (g['lane'], g['ticket']) == (lane, ticket)]
    if not mine:
        return
    ks = [x['k'] for x in (report or {}).get('gates', []) if _norm(x['command']) == cmd]
    k = ks[0] if len(ks) == 1 else max(g['k'] for g in mine)
    hits = [g for g in mine if g['k'] == k]
    if hits:
        max(hits, key=lambda g: g['attempt'] or 0)['rc'] = rc


def _landed(logs, problems):
    path = os.path.join(logs, 'land.jsonl')
    if not os.path.isfile(path):
        return []
    out = []
    for line in _lines(path, problems) or []:
        try:
            branch = json.loads(line).get('branch')
        except (ValueError, AttributeError):
            continue
        if isinstance(branch, str) and branch and branch not in out:
            out.append(branch)
    return out


def read(lanes_dir):
    problems = []
    report = _report(lanes_dir, problems)
    logs = os.path.join(lanes_dir, 'logs')
    flog = _fanout_log(logs, problems)
    drivers, gates = _logs(logs, problems)
    for e in flog:
        if e['lane']:
            _place_rc(gates, report, e['run_id'], e['lane'], e['ticket'], e['event'])
    for r in (report or {}).get('rows', []):
        _place_rc(gates, report, report['run_id'], r['lane'], r['ticket'], r['outcome'])
    return {'lanes_dir': lanes_dir, 'report': report, 'fanout_log': flog, 'driver_logs': drivers,
            'gate_logs': gates, 'landed': _landed(logs, problems), 'problems': problems}
