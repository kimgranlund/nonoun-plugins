#!/usr/bin/env python3
"""Per-ticket cost budget: meter spend from runs.jsonl and stop to ask at 80 percent.

Usage: budget.py status <path> | set <ticket dir|handoff.md> (--tier L1|L2|L3 | --usd N)
                 | ack <ticket dir> --usd N --reason TEXT | selftest

The budget is optional front matter `budget_usd: <number>` on a ticket's handoff.md (anything that is
not a positive number counts as no budget). By ticket level: L1 $5, L2 $30, L3 $60, L4 and L5 none (ask the
user). --tier takes the level; the deprecated 0.21.x size names are read as their level (tickets.SIZE_ALIASES).

  status  resolves the ticket from a ticket dir, a step dir, a superseded step dir, or a handoff.md
          (ticket_of walks up to the nearest handoff.md whose front matter has an `id`, stopping at the
          filesystem root or at a dir named .sdlc) and prints spend, budget (the ceiling), percent,
          state (ok, warn at 80 percent or more, over at 100 or more), and unmetered_runs.
          Exit 0 ok, 3 warn or over, 2 no budget or no ticket.
  set     writes or replaces one `budget_usd:` line in the front matter; refuses (exit 2) with none.
  ack     writes budget-ack.md (front matter usd, reason, ts) in the ticket's records dir (order.py records_dir;
          read there first, then the ticket folder); its usd must be
          greater than the current ceiling and becomes the ceiling. A second ack replaces the first.

Spend is cost_usd summed over every runs.jsonl under the ticket's records dir and the ticket folder, recursively (superseded step
dirs included), deduplicated by attempt_id; a record with no (or an empty) attempt_id counts every
time. A null or missing cost_usd counts 0 and is reported in unmetered_runs. A record with
cost_estimated true (cost_estimate.py, sub-agent runs) counts like any cost; status prints `estimated`, its percent of spend.
Codex runs record no cost (codex_exec.py), so the meter covers Claude roles only. Solo sessions started through solo_run.py add a role solo record with the session cost. Conductor and
background sessions are not in runs.jsonl, so the budget bounds the pipeline, not the session.
run.sh calls status before launching a role and exits 4 on exit 3; board.py renders a Budget column.
"""
import argparse, datetime, json, math, os, pathlib, re, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tickets  # same scripts/ dir: the only front matter parser
import order  # same scripts/ dir: the records dir rule (records_dir, task_dir)

TIERS = {'L1': 5, 'L2': 30, 'L3': 60}  # budget_usd by ticket level


def tier_usd(level):
    """The default budget for a ticket level, or for a deprecated alias of one; None for L4, L5, or anything else."""
    return TIERS.get(tickets.size_level(level))
WARN_PCT = 80
ACK = 'budget-ack.md'
FRONT_RE = re.compile(r'---\n(.*?)^---[ \t]*$', re.S | re.M)


def number(v):
    """A positive finite float from a front matter value, else None."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) and x > 0 else None


def fmt(x):
    return str(int(x)) if float(x).is_integer() else f'{x:.2f}'


def front(path):
    try:
        meta = tickets.parse(pathlib.Path(path).read_text(encoding='utf-8'))
    except Exception:
        return None
    return meta if isinstance(meta, dict) else None


def ticket_of(path):
    """The ticket folder for a ticket dir, step dir, superseded step dir, or handoff.md; None when none."""
    p = pathlib.Path(path).resolve()
    d = p.parent if p.is_file() else p
    parts = d.parts
    if any(parts[i:i + 3] == ('.sdlc', 'runtime', 'tasks') for i in range(len(parts) - 2)):
        t = order.task_dir(d)  # a records dir under runtime/tasks: walk from its task folder
        if t is None:
            return None
        d = pathlib.Path(t).resolve()
    while True:
        if d.name == '.sdlc':
            return None
        meta = front(d / 'handoff.md')
        if meta is not None and meta.get('id'):
            return d
        if d.parent == d:
            return None
        d = d.parent


def spend(ticket):
    """(spend, unmetered_runs, estimated_spend) over every runs.jsonl under the ticket's records dir and the ticket folder,
    each file read once, deduplicated by attempt_id."""
    total, unmetered, est, seen = 0.0, 0, 0.0, set()
    files = {f.resolve() for root in (order.records_dir(ticket), pathlib.Path(ticket)) for f in root.rglob('runs.jsonl')}
    for f in sorted(files):
        try:
            lines = f.read_text(encoding='utf-8').splitlines()
        except OSError:
            continue
        for line in lines:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            aid = rec.get('attempt_id')
            if isinstance(aid, str) and aid:
                if aid in seen:
                    continue
                seen.add(aid)
            c = rec.get('cost_usd')
            if isinstance(c, (int, float)) and not isinstance(c, bool) and math.isfinite(c):
                total += c
                if rec.get('cost_estimated') is True:
                    est += c
            else:
                unmetered += 1
    return total, unmetered, est


def ceiling(ticket):
    """(budget_usd, ceiling) for a ticket folder; (None, None) when it has no budget."""
    meta = front(pathlib.Path(ticket) / 'handoff.md') or {}
    budget = number(meta.get('budget_usd'))
    if budget is None:
        return None, None
    ack = front(order.records_dir(ticket) / ACK) or front(pathlib.Path(ticket) / ACK) or {}
    acked = number(ack.get('usd'))
    return budget, acked if acked is not None and acked > budget else budget


def report(ticket):
    """Budget state of a ticket folder (no walk-up), or None when it has no budget."""
    _, ceil = ceiling(ticket)
    if ceil is None:
        return None
    s, unmetered, est = spend(ticket)
    state = 'over' if s >= ceil else 'warn' if s * 100 >= ceil * WARN_PCT else 'ok'
    return {'spend': s, 'budget': ceil, 'percent': int(s * 100 / ceil + 1e-9), 'state': state,
            'unmetered_runs': unmetered, 'estimated': int(est * 100 / s + 0.5) if s else 0}


def cmd_status(path):
    t = ticket_of(path)
    if t is None:
        print('no ticket', file=sys.stderr)
        return 2
    r = report(t)
    if r is None:
        print('no budget', file=sys.stderr)
        return 2
    print(f"spend: {r['spend']:.2f}")
    print(f"budget: {fmt(r['budget'])}")
    print(f"percent: {r['percent']}")
    print(f"state: {r['state']}")
    print(f"unmetered_runs: {r['unmetered_runs']}")
    print(f"estimated: {r['estimated']}%")
    return 0 if r['state'] == 'ok' else 3


def cmd_set(path, usd):
    p = pathlib.Path(path)
    h = p / 'handoff.md' if p.is_dir() else p
    try:
        text = h.read_text(encoding='utf-8')
    except OSError as e:
        print(f'budget.py: cannot read {h}: {e}', file=sys.stderr)
        return 2
    m = FRONT_RE.match(text)
    if not m:
        print(f'budget.py: {h} has no front matter', file=sys.stderr)
        return 2
    lines = m.group(1).splitlines(keepends=True)
    new = f'budget_usd: {fmt(usd)}\n'
    out, done = [], False
    for line in lines:
        if re.match(r'budget_usd\s*:', line):
            if not done:
                out.append(new)
                done = True
            continue
        out.append(line)
    if not done:
        out.append(new)
    h.write_text('---\n' + ''.join(out) + text[m.end(1):], encoding='utf-8')
    print(f'{h}: budget_usd {fmt(usd)}')
    return 0


def cmd_ack(path, usd, reason):
    t = ticket_of(path)
    if t is None:
        print('budget.py: no ticket', file=sys.stderr)
        return 2
    _, ceil = ceiling(t)
    if ceil is None:
        print('budget.py: ticket has no budget; use set', file=sys.stderr)
        return 2
    if usd <= ceil:
        print(f'budget.py: ack usd {fmt(usd)} must be greater than the current ceiling {fmt(ceil)}', file=sys.stderr)
        return 2
    reason = ' '.join(reason.split()).replace('"', "'")
    ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    out = order.records_dir(t, create=True) / ACK
    out.write_text(f'---\nusd: {fmt(usd)}\nreason: "{reason}"\nts: {ts}\n---\n', encoding='utf-8')
    print(f'{out}: ceiling {fmt(usd)}')
    return 0


def selftest():
    misses, oks = [], []

    def expect(label, cond):
        (oks if cond else misses).append(label)

    def ticket(root, name, budget='10', **extra):
        d = root / name
        d.mkdir(parents=True)
        b = f'budget_usd: {budget}\n' if budget is not None else ''
        d.joinpath('handoff.md').write_text(
            f'---\nid: T-0900\ntitle: "x"\ntype: chore\nstatus: ready\nsize: S\npriority: P2\n'
            f'depends: []\ncreated: 2026-10-04\n{b}---\n\n## Goal\nx\n', encoding='utf-8')
        return d

    def runs(d, *recs):
        d.mkdir(parents=True, exist_ok=True)
        with (d / 'runs.jsonl').open('a', encoding='utf-8') as f:
            for r in recs:
                f.write(json.dumps(r) + '\n')

    def status(path):
        import contextlib, io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cmd_status(path)
        lines = dict(l.split(': ', 1) for l in out.getvalue().splitlines() if ': ' in l)
        return rc, lines

    def quiet(fn, *a):
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return fn(*a)

    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / '.sdlc'

        t = ticket(root, 'under')
        runs(t / 'step-1', {'role': 'builder', 'cost_usd': 7.9, 'attempt_id': 'a1'})
        rc, s = status(t / 'step-1')
        expect('status: under 80 percent is ok', rc == 0 and s.get('state') == 'ok' and s.get('percent') == '79')

        t = ticket(root, 'at80')
        runs(t, {'role': 'builder', 'cost_usd': 8, 'attempt_id': 'a1'})
        rc, s = status(t)
        expect('status: at 80 percent is warn with exit 3', rc == 3 and s.get('state') == 'warn' and s.get('percent') == '80')

        t = ticket(root, 'over')
        runs(t, {'role': 'builder', 'cost_usd': 6, 'attempt_id': 'a1'}, {'role': 'verifier', 'cost_usd': 5, 'attempt_id': 'a2'})
        rc, s = status(t / 'handoff.md')
        expect('status: over 100 percent is over with exit 3', rc == 3 and s.get('state') == 'over' and s.get('spend') == '11.00')

        t = ticket(root, 'dup')
        runs(t / 'step-1', {'role': 'builder', 'cost_usd': 3, 'attempt_id': 'x'})
        runs(t / 'step-1.superseded-1' / 'step-1', {'role': 'builder', 'cost_usd': 3, 'attempt_id': 'x'})
        runs(t, {'role': 'planner', 'cost_usd': 1, 'attempt_id': ''}, {'role': 'planner', 'cost_usd': 1})
        rc, s = status(t)
        expect('status: a duplicated attempt_id counts once', rc == 0 and s.get('spend') == '5.00')

        t = ticket(root, 'null')
        runs(t, {'role': 'builder', 'cost_usd': None, 'attempt_id': 'a1'}, {'role': 'scout', 'attempt_id': 'a2'},
             {'role': 'planner', 'cost_usd': 0, 'attempt_id': 'a3'}, {'role': 'verifier', 'cost_usd': 2, 'attempt_id': 'a4'})
        rc, s = status(t)
        expect('status: a null cost is unmetered',
               rc == 0 and s.get('spend') == '2.00' and s.get('unmetered_runs') == '2')

        t = ticket(root, 'sup')
        deep = t / 'step-2.superseded-1' / 'step-2'
        runs(deep, {'role': 'builder', 'cost_usd': 9, 'attempt_id': 's1'})
        (deep / 'handoff.md').write_text('## Goal\nstep\n', encoding='utf-8')
        rc, s = status(deep)
        expect('status: a superseded dir run counts', rc == 3 and s.get('spend') == '9.00' and s.get('state') == 'warn')

        t = ticket(root, 'nobudget', budget=None)
        runs(t, {'role': 'builder', 'cost_usd': 50, 'attempt_id': 'a1'})
        bad = ticket(root, 'badbudget', budget='lots')
        loose = pathlib.Path(tmp) / '.sdlc' / 'loose'
        loose.mkdir()
        loose.joinpath('handoff.md').write_text('## Goal\nno front matter\n', encoding='utf-8')
        expect('status: no budget exits 2',
               status(t)[0] == 2 and status(bad)[0] == 2 and status(loose)[0] == 2)

        t = ticket(root, 'acked')
        # Estimated cost counts: all-estimated runs at 85 percent exit 3; the same runs with null costs exit 0.
        te = ticket(root, 'est-pos')
        runs(te, {'role': 'builder', 'cost_usd': 8.5, 'cost_estimated': True, 'attempt_id': 'e1'})
        rc, out = status(te)
        expect('status: all-estimated runs at 85 percent exit 3 and print the estimated share',
               rc == 3 and out.get('estimated') == '100%')
        tn = ticket(root, 'est-null')
        runs(tn, {'role': 'builder', 'cost_usd': None, 'cost_reason': 'x', 'attempt_id': 'n1'})
        expect('status: the same ticket with null costs exits 0 (the gap this closes)', status(tn)[0] == 0)
        runs(t, {'role': 'builder', 'cost_usd': 8.5, 'attempt_id': 'a1'})
        rc0, _ = status(t)
        rc1 = quiet(cmd_ack, t, 20.0, 'scope grew: needs #2')
        rc, s = status(t)
        ack = front(t / ACK) or {}
        expect('ack: raising the ceiling clears warn',
               rc0 == 3 and rc1 == 0 and rc == 0 and s.get('budget') == '20' and s.get('percent') == '42'
               and ack.get('reason') == 'scope grew: needs #2' and bool(ack.get('ts')))

        rc2 = quiet(cmd_ack, t, 15.0, 'lower')
        rc3 = quiet(cmd_ack, t, 20.0, 'equal')
        expect('ack: a lower usd is refused',
               rc2 == 2 and rc3 == 2 and (front(t / ACK) or {}).get('usd') == '20')

        t = ticket(root, 'tier', budget=None)
        before = (t / 'handoff.md').read_text(encoding='utf-8')
        rc1 = quiet(cmd_set, t, TIERS['L1'])
        after1 = (t / 'handoff.md').read_text(encoding='utf-8')
        rc2 = quiet(cmd_set, t / 'handoff.md', 12.5)
        after2 = (t / 'handoff.md').read_text(encoding='utf-8')
        plain = root / 'plain.md'
        plain.write_text('## Goal\nno front matter\n', encoding='utf-8')
        rc3 = quiet(cmd_set, plain, 5)
        expect('set: level L1 writes budget_usd 5',
               rc1 == 0 and after1 == before.replace('---\n\n## Goal', 'budget_usd: 5\n---\n\n## Goal')
               and rc2 == 0 and after2 == before.replace('---\n\n## Goal', 'budget_usd: 12.50\n---\n\n## Goal')
               and after2.count('budget_usd') == 1 and rc3 == 2
               and plain.read_text(encoding='utf-8') == '## Goal\nno front matter\n')

        expect('tier_usd: levels L1 to L3, the aliases read as their level, none for L4',
               (tier_usd('L1'), tier_usd('L2'), tier_usd('L3'), tier_usd('S'), tier_usd('M'), tier_usd('L'), tier_usd('L4'), tier_usd('XL'))
               == (5, 30, 60, 5, 30, 60, None, None))

    for label in oks:
        print(f'ok: {label}')
    if misses:
        for label in misses:
            print(f'FAIL: {label}')
        print('budget selftest: FAIL')
        return 1
    print('budget selftest: PASS')
    return 0


def main():
    ap = argparse.ArgumentParser(description='Per-ticket cost budget.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('status')
    p.add_argument('path')
    p = sub.add_parser('set')
    p.add_argument('path')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--tier', choices=sorted(TIERS) + ['L', 'M', 'S'], help='the ticket level L1, L2, or L3 (S, M, L: deprecated aliases)')
    g.add_argument('--usd', type=float)
    p = sub.add_parser('ack')
    p.add_argument('path')
    p.add_argument('--usd', type=float, required=True)
    p.add_argument('--reason', required=True)
    sub.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'status':
        return cmd_status(a.path)
    if a.cmd == 'set':
        usd = tier_usd(a.tier) if a.tier else a.usd
        if number(usd) is None:
            print('budget.py: --usd must be a positive number', file=sys.stderr)
            return 2
        return cmd_set(a.path, usd)
    if number(a.usd) is None:
        print('budget.py: --usd must be a positive number', file=sys.stderr)
        return 2
    if not a.reason.strip():
        print('budget.py: --reason must not be empty', file=sys.stderr)
        return 2
    return cmd_ack(a.path, a.usd, a.reason)


if __name__ == '__main__':
    sys.exit(main())
