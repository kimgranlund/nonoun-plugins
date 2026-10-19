#!/usr/bin/env python3
"""Is a plan doc finished? The condition a /goal stop hook evaluates (docs/specs/sdlc-lite/plan-doc-executor.md section 4).

  plan_done.py <plan-doc> [--root .sdlc] [--records-only] [--json]
  plan_done.py stop <plan-doc> --reason R [--resume CMD] [--root .sdlc]
  plan_done.py replan <plan-doc> --reason R [--root .sdlc]
  plan_done.py resume <plan-doc> [--root .sdlc]
  plan_done.py selftest

Deterministic: no model call. It reads the plan (through plan_doc.py, after the plan_check.py `plan` shape rules), each step's ticket,
verifier result and held criteria, the `now` measures (it runs only their backticked commands) and the Upserts rows, and re-derives
five conditions from those records, never from the executor's notes:
  C1 every step ticket is closed (status done)     C2 every step that needs one has an independent verifier pass
  C3 no held criterion (steps.held_items)          C4 every `now` KPI is readable and on the right side of its target
  C5 every Upserts row holds                       S  plan-state.json records a stop
Exit codes and the last line printed:
  0 `plan done`; 1 `open: ...`, `held: ...`, `kpi ...` or `upsert: ...` (the item that decides the row, by C1 to C5 order); 2
  `plan defect: <rule>` (a plan_check.py plan rule, or `ticket-absent`: a step names a ticket id no ticket has); 3 `records ok; measures
  not read` (only with --records-only, which can never exit 0); 4 `stopped: <reason>; resume: <command>` (a stop record and at least one
  open item). Every open item is also printed first, one line each, in step order; the last line repeats the one that decides the row.
  Later measures print as `later: K-004 (owner, date)` and never change the exit code. A stop record with everything green exits 0.
A step `ticket: new <type> <slug>` is its ticket once a folder named <NNNN>-<slug> exists, and an open item until then. A measure's `read`
cell is a dotted path into the JSON the command prints (`runs.interrupted.lost_min_median`), or ignored when the command prints one bare
number; anything else, a failing command or a timeout reads `unreadable`, never green. The comparison uses the operator in `target`
(`<= 15`), else the direction (down `<=`, up `>=`, hold `=`).
`stop` writes plan-state.json into the plan dir's records dir (order.records_dir: .sdlc/runtime/tasks/<plan dir name>/, or
the plan dir itself when it already holds records; a legacy plan-state.json beside the plan is still read) and one line to the notes file the plan names, exit 0. `replan` counts in the same file:
the first call exits 0, the second refuses (exit 2), writes the stop record and prints `replan cap reached: stopped`. plan-state.json
holds `replans` and `stopped` and nothing else, and never contributes to done. `resume` clears the stop record (keeps `replans`) and
writes one notes line, exit 0: the step after the cause of a stop is fixed, so a stop record never needs hand removal.
"""
import argparse, json, os, pathlib, re, subprocess, sys, tempfile, time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dispatch, order, plan_check, plan_doc, results, steps, tickets  # noqa: E402
import roots  # noqa: E402  (work_root: the notes path)

STATE = 'plan-state.json'
REPLAN_CAP = 1
MEASURE_TIMEOUT = 120
CLASSES = ('C1', 'C2', 'C3', 'C4', 'C5')
TARGET_RE = re.compile(r'^\s*(<=|>=|==|=|<|>)?\s*(-?\d+(?:\.\d+)?)\s*%?\s*$')
NUM_RE = re.compile(r'^-?\d+(?:\.\d+)?$')
NOTES_RE = re.compile(r'\.sdlc/(notes/notes\.md|notes\.md)')


# ---- records -------------------------------------------------------------------------------------------------
def ticket_index(root):
    """(by id {id: (folder, meta)}, folders [(folder, meta)]) for every ticket under root, live or archived."""
    tdir = tickets.layout_paths(pathlib.Path(root)).tickets
    by_id, folders = {}, []
    for slug, meta in tickets.load(tdir):
        item = (tdir / slug, meta)
        folders.append((slug, item))
        if meta.get('id') and meta['id'] not in by_id:
            by_id[meta['id']] = item
    return by_id, folders


def find_ticket(ref, by_id, folders):
    """(folder, meta) for a step's `ticket:` value, or None. `new <type> <slug>` matches a folder named [.]NNNN-<slug>."""
    if re.fullmatch(r'T-\d+', ref):
        return by_id.get(ref)
    m = re.fullmatch(r'new\s+\S+\s+(\S+)', ref)
    if not m:
        return None
    for slug, item in folders:
        if re.sub(r'^\.?(?:\d+-)?', '', slug) == m.group(1):
            return item
    return None


def level_num(value):
    m = re.fullmatch(r'L([1-5])', str(value or '').strip())
    return int(m.group(1)) if m else None


def header_model(path):
    m = re.search(r'model=(\S+)', pathlib.Path(path).read_text(encoding='utf-8', errors='replace').splitlines()[0] if path else '')
    return dispatch.agent_alias(m.group(1)) if m else ''


def worker_model(folder):
    """The family alias of the model that did the work: the newest solo record in runs.jsonl, else the newest builder result header."""
    solo = dispatch.solo_model(str(folder))
    if solo:
        return dispatch.agent_alias(solo)
    built = order.newest(str(folder), 'builder') or dispatch.step_build(folder)
    return header_model(built) if built else ''


def verifier_problem(folder):
    """None when the ticket's newest verifier result is an independent pass (or a verified hold, which C3 then lists), else the reason."""
    v = order.newest(str(folder), 'verifier')
    if not v:
        return 'no verifier result; fanout.py land carries a lane\'s record onto this checkout, a hand merge or cherry-pick leaves it on the lane branch'
    err = results.validate(v, 'verifier')
    if err:
        return f'{os.path.basename(v)} is invalid: {err}'
    verdict = results.key_value(v, 'verifier')
    held = verdict == 'fail' and steps.HELD_NOTE_RE.match(steps.next_note(v)) and steps.held_items(folder)
    if verdict != 'pass' and not held:
        return f'Verdict: {verdict or "?"}'
    wm, vm = worker_model(folder), header_model(v)
    if not wm:
        return 'the worker model is not recorded (no solo or builder record)'
    if wm == vm:
        return f'the verifier model {vm} equals the worker model {wm}'
    recs = order.records(str(folder))
    vi = next((i for i, r in recs if r.get('role') == 'verifier' and r.get('file') == os.path.basename(v)), -1)
    if any(i > vi and r.get('role') in ('solo', 'builder') for i, r in recs):
        return 'a solo or builder result is newer than the verifier pass'
    return None


def walk(data, expr):
    """The value at the dotted path expr in parsed JSON, or None. A key holding dots wins over splitting."""
    if isinstance(data, dict) and expr in data:
        return data[expr]
    cur = data
    for part in expr.split('.'):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and NUM_RE.match(value.strip()):
        return float(value)
    return None


def read_measure(row, repo):
    """(value, None) or (None, why unreadable) for one Measures row."""
    cmd = row.get('command', '').strip('`')
    try:
        p = subprocess.run(cmd, shell=True, cwd=str(repo), capture_output=True, text=True, timeout=MEASURE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, f'the command timed out after {MEASURE_TIMEOUT}s'
    except OSError as e:
        return None, f'the command did not start: {e}'
    if p.returncode != 0:
        return None, f'the command exited {p.returncode}'
    out = p.stdout.strip()
    if not out:
        return None, 'the command printed nothing'
    try:
        data = json.loads(out)
    except ValueError:
        data = None
    if isinstance(data, (dict, list)):
        val = number(walk(data, row.get('read', '')))
        return (val, None) if val is not None else (None, f'`{row.get("read", "")}` is not a number in the output')
    val = number(data if data is not None else out.splitlines()[-1])
    return (val, None) if val is not None else (None, 'the output is not a number')


def on_target(value, row):
    m = TARGET_RE.match(row.get('target', ''))
    if not m:
        return None
    op = m.group(1) or {'down': '<=', 'up': '>=', 'hold': '=='}.get(row.get('direction', ''), '==')
    tgt = float(m.group(2))
    return {'<=': value <= tgt, '>=': value >= tgt, '<': value < tgt, '>': value > tgt, '==': value == tgt, '=': value == tgt}[op]


def later_lines(doc):
    out, seen = [], set()
    _, mrows = plan_doc.rows_as_dicts(doc.section('Measures'))
    for r in mrows:
        w = r.get('when', 'now')
        if w.startswith('later'):
            rest = w.partition(':')[2].strip()
            who, _, date = rest.partition(',')
            out.append((r.get('id', '?'), who.strip() or '?', date.strip() or '?'))
    _, lrows = plan_doc.rows_as_dicts(doc.section('Later measures'))
    for r in lrows:
        out.append((r.get('id', '?'), r.get('owner', '?') or '?', r.get('date', '?') or '?'))
    lines = []
    for i, who, date in out:
        if i not in seen:
            seen.add(i)
            lines.append(f'later: {i} ({who}, {date})')
    return lines


def state_path(plan, create=False):
    """plan-state.json in the plan dir's records dir (order.records_dir)."""
    return order.records_dir(pathlib.Path(plan).parent, create=create) / STATE


def read_state(plan):
    """The records-dir plan-state.json, else the legacy one beside the plan, else {}."""
    for path in (state_path(plan), pathlib.Path(plan).parent / STATE):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        return data if isinstance(data, dict) else {}
    return {}


# ---- the verdict ---------------------------------------------------------------------------------------------
def assess(plan, root='.sdlc', records_only=False):
    """{code, last, items [(class, step, text)], later [text]} for a plan doc; see the module docstring for the rows."""
    plan, rootp = pathlib.Path(plan), pathlib.Path(root)
    try:
        text = plan.read_text(encoding='utf-8')
    except OSError as e:
        return {'code': 2, 'last': f'plan defect: unreadable: {e.strerror}', 'items': [], 'later': [], 'defects': [f'plan defect: unreadable: {e.strerror}']}
    fails, _ = plan_check.check_plan(text, root=str(rootp), run=False, path=str(plan))
    defects = [f'plan defect: {rule}: {why}' for rule, why in fails]
    doc = plan_doc.parse(text)
    by_id, folders = ticket_index(rootp)
    found = {}
    for n, st in sorted(doc.steps.items()):
        ref = st.keys.get('ticket', '')
        got = find_ticket(ref, by_id, folders)
        if got:
            found[n] = got
        elif re.fullmatch(r'T-\d+', ref):
            defects.append(f'plan defect: ticket-absent: step {n} names {ref}, which no ticket has')
    if defects:
        return {'code': 2, 'last': defects[0], 'items': [], 'later': [], 'defects': defects}
    repo = rootp.resolve().parent
    items = []

    def add(cls, n, line):
        items.append((cls, n, line))
    for n, st in sorted(doc.steps.items()):
        got = found.get(n)
        if not got:
            add('C1', n, f'open: step {n}: ticket not created ({st.keys.get("ticket")})')
            continue
        folder, meta = got
        if meta.get('status') != 'done':
            add('C1', n, f'open: step {n}: ticket {meta.get("id")} status {meta.get("status", "?")}')
            continue
        lvl = level_num(meta.get('size')) or level_num(st.level) or 1
        need = st.keys.get('verify', 'auto') == 'required' or lvl >= 2
        why = verifier_problem(folder) if need else None
        if why:
            add('C2', n, f'open: step {n}: no independent verifier pass ({why})')
        for h in steps.held_items(folder, rootp):
            extra = f' ({h["reason"]})' if h.get('reason') else ''
            add('C3', n, f'held: step {n}: #{h["ref"]} {h["state"]} {h["who"]}'.rstrip() + extra)
    if not records_only and not any(c in ('C1', 'C2', 'C3') for c, _, _ in items):
        _, mrows = plan_doc.rows_as_dicts(doc.section('Measures'))
        for r in mrows:
            if r.get('when', 'now') != 'now':
                continue
            val, why = read_measure(r, repo)
            if val is None:
                add('C4', 0, f'kpi {r.get("id")} unreadable: {why}')
                continue
            ok = on_target(val, r)
            if ok is None:
                add('C4', 0, f'kpi {r.get("id")} unreadable: target `{r.get("target")}` is not a number')
            elif not ok:
                add('C4', 0, f'kpi {r.get("id")} reads {val:g}, target {r.get("target")}')
    _, urows = plan_doc.rows_as_dicts(doc.section('Upserts'))
    for r in urows:
        p, mode = r.get('path', '').strip('`'), r.get('mode', '')
        here = (repo / p).exists()
        archived = 'archive' in pathlib.PurePosixPath(p).parts
        if (mode in ('create', 'edit') and not here) or (mode == 'retire' and here and not archived):
            add('C5', int(r['step']) if r.get('step', '').isdigit() else 0, f'upsert: {p} {mode} not satisfied')
    later = later_lines(doc)
    stopped = read_state(plan).get('stopped')
    if items and isinstance(stopped, dict):
        last = f'stopped: {stopped.get("reason", "")}; resume: {stopped.get("resume", "")}'
        code = 4
    elif items:
        last = min(items, key=lambda i: (CLASSES.index(i[0]), i[1]))[2]
        code = 1
    elif records_only:
        last, code = 'records ok; measures not read', 3
    else:
        last, code = 'plan done', 0
    items.sort(key=lambda i: (i[1], CLASSES.index(i[0])))
    return {'code': code, 'last': last, 'items': items, 'later': later, 'defects': []}


def render(res, as_json=False):
    """The lines printed for an assess() result."""
    if as_json:
        return [json.dumps({'exit': res['code'], 'last': res['last'], 'open': [{'class': c, 'step': n, 'text': t} for c, n, t in res['items']],
                            'later': res['later'], 'defects': res['defects']})]
    if res['code'] == 2:
        return res['defects'][1:] + res['defects'][:1]
    return [t for _, _, t in res['items']] + res['later'] + [res['last']]


# ---- writers -------------------------------------------------------------------------------------------------
def notes_path(plan, root):
    try:
        text = pathlib.Path(plan).read_text(encoding='utf-8')
    except OSError:
        return None
    budget = plan_doc.parse(text).section('Budget and stop rules') or ''
    rel = plan_check.notes_rel(root)  # work_root: the plan names the work root's NOTES.md
    if rel:
        return roots.resolve(pathlib.Path(root)).notes if rel in budget else None
    m = NOTES_RE.search(budget)
    return pathlib.Path(root) / m.group(1) if m else None


def write_state(plan, state):
    path = state_path(plan, create=True)
    keep = {k: state[k] for k in ('replans', 'stopped') if k in state}
    tmp = path.with_name(STATE + '.tmp')
    tmp.write_text(json.dumps(keep, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def note(plan, root, line):
    path = notes_path(plan, root)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def default_resume(plan):
    return f'python3 plugins/sdlc-lite/scripts/plan_done.py resume {plan}'


def do_resume(plan, root):
    """Clear the stop record, keep the replan count; returns the cleared stop's reason, or None when none was recorded."""
    state = read_state(plan)
    stopped = state.pop('stopped', None)
    if not isinstance(stopped, dict):
        return None
    state['replans'] = int(state.get('replans', 0) or 0)
    write_state(plan, state)
    note(plan, root, f'- {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} plan {pathlib.Path(plan).parent.name} resumed after: {stopped.get("reason", "")}')
    return str(stopped.get('reason', ''))


def do_stop(plan, root, reason, resume=None):
    state = read_state(plan)
    state['replans'] = int(state.get('replans', 0) or 0)
    when = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    state['stopped'] = {'reason': reason, 'time': when, 'resume': resume or default_resume(plan)}
    write_state(plan, state)
    note(plan, root, f'- {when} plan {pathlib.Path(plan).parent.name} stopped: {reason}; resume: {state["stopped"]["resume"]}')


def do_replan(plan, root, reason):
    """0 and the counter at 1 on the first call; the second call refuses (2), writes the stop record itself."""
    state = read_state(plan)
    n = int(state.get('replans', 0) or 0)
    if n >= REPLAN_CAP:
        do_stop(plan, root, f'replan cap reached: {reason}')
        print('replan cap reached: stopped')
        return 2
    state['replans'] = n + 1
    write_state(plan, state)
    note(plan, root, f'- {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} plan {pathlib.Path(plan).parent.name} replan {n + 1} of {REPLAN_CAP}: {reason}')
    print(f'replan {n + 1} of {REPLAN_CAP}: {reason}')
    return 0


# ---- selftest ------------------------------------------------------------------------------------------------
FM = '---\nid: {id}\ntitle: "x"\ntype: feature\nstatus: {status}\nsize: {size}\npriority: P2\ndepends: []\ncreated: 2026-10-10\n---\n\n## Goal\nx\n{extra}'
VERIFIER = '<!-- role=verifier level=L2 model={model} effort=high -->\n## Verdict\n{verdict}\n\n{rest}'
TICKETS = (('0413-resume', 'T-0413', 'L2'), ('0414-sweep', 'T-0414', 'L3'), ('0901-collector-fields', 'T-0901', 'L2'), ('0902-close-out', 'T-0902', 'L1'))
NOW = '`python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d`'


def build(tmp, now='`printf 12`'):
    """An all-green fixture: <tmp>/.sdlc with the four step tickets done and independently verified, the plan, the upsert file."""
    root = pathlib.Path(tmp) / '.sdlc'
    for folder, tid, size in TICKETS:
        d = root / folder
        d.mkdir(parents=True)
        (d / 'handoff.md').write_text(FM.format(id=tid, status='done', size=size, extra=''), encoding='utf-8')
        (d / 'verifier-L2.md').write_text(VERIFIER.format(model='opus', verdict='pass', rest='## Criteria\n- #1 `x`: pass. Evidence: ok\n'), encoding='utf-8')
        (d / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'level': 'L2', 'model': 'sonnet', 'file': ''}) + '\n'
                                      + json.dumps({'role': 'verifier', 'level': 'L2', 'model': 'opus', 'file': 'verifier-L2.md'}) + '\n', encoding='utf-8')
    plan = root / 'demo' / 'plan-doc.md'
    plan.parent.mkdir(parents=True)
    text = plan_check.GOOD_PLAN
    assert f'| K-002 | {NOW} |' in text and f'| K-003 | {NOW} |' in text, 'GOOD_PLAN measures changed'
    plan.write_text(text.replace(f'| K-002 | {NOW} |', f'| K-002 | {now} |').replace(f'| K-003 | {NOW} |', '| K-003 | `printf 0` |'), encoding='utf-8')
    up = pathlib.Path(tmp) / 'docs' / 'references' / 'sdlc-internals.md'
    up.parent.mkdir(parents=True)
    up.write_text('x\n', encoding='utf-8')
    return root, plan


def selftest():
    bad, n = [], [0]

    def expect(label, cond, got=None):
        n[0] += 1
        print(('ok: ' if cond else 'FAIL: ') + label)
        if not cond:
            bad.append(label)
            if got is not None:
                print('  got', got)

    def row(label, res, code, prefix):
        expect(f'plan_done: {label}', res['code'] == code and res['last'].startswith(prefix), (res['code'], res['last'], res['items']))
    tmpdirs = []

    def fresh(**kw):
        d = tempfile.TemporaryDirectory()
        tmpdirs.append(d)
        return (pathlib.Path(d.name), *build(d.name, **kw))

    def run_all(root, plan, **kw):
        return assess(plan, root, **kw)

    def cli(plan, root, *args):
        p = subprocess.run([sys.executable, str(HERE / 'plan_done.py'), *args, '--root', str(root)] if args[:1] in (('stop',), ('replan',), ('resume',)) else
                           [sys.executable, str(HERE / 'plan_done.py'), str(plan), '--root', str(root), *args], capture_output=True, text=True)
        return p.returncode, p.stdout.strip().splitlines()

    def ed(path, old, new):
        t = pathlib.Path(path).read_text(encoding='utf-8')
        assert old in t, old
        pathlib.Path(path).write_text(t.replace(old, new, 1), encoding='utf-8')
    # all green
    tmp, root, plan = fresh()
    res = run_all(root, plan)
    row('all green exits 0 and prints plan done', res, 0, 'plan done')
    expect('plan_done: a later measure is printed and never changes the exit code', 'later: K-004 (maintainer, 2026-11-09)' in res['later'] and res['code'] == 0)
    expect('plan_done: the all-green fixture passes the plan_check.py plan rules', not plan_check.check_plan(plan.read_text(encoding='utf-8'), root=str(root), path=str(plan))[0])
    for i in range(1, 5):
        expect(f'plan_done: fixture verifier result {i} validates with results.py',
               results.validate(str(root / TICKETS[i - 1][0] / 'verifier-L2.md'), 'verifier') is None)
    # C1
    tmp, root, plan = fresh()
    ed(root / '0413-resume' / 'handoff.md', 'status: done', 'status: ready')
    row('C1 a step ticket at status ready exits 1 naming that step', run_all(root, plan), 1, 'open: step 2: ticket T-0413 status ready')
    ed(root / '0413-resume' / 'handoff.md', 'status: ready', 'status: done')
    row('C1 control: closing it turns the row green', run_all(root, plan), 0, 'plan done')
    tmp, root, plan = fresh()
    import shutil
    shutil.rmtree(root / '0901-collector-fields')
    res = run_all(root, plan)
    row('C1 a ticket: new step with no ticket yet is an open item, not a plan defect', res, 1, 'open: step 1: ticket not created (new feature collector-fields)')
    # C2
    for label, mut in (
            ('the verifier header model equals the worker model', lambda r: ed(r / '0413-resume' / 'verifier-L2.md', 'model=opus', 'model=sonnet')),
            ('a Verdict: fail', lambda r: (r / '0413-resume' / 'verifier-L2.md').write_text(
                VERIFIER.format(model='opus', verdict='fail', rest='## Criteria\n- #1 `x`: fail. Evidence: no\n'), encoding='utf-8')),
            ('a solo result newer than the pass', lambda r: (r / '0413-resume' / 'runs.jsonl').open('a').write(json.dumps({'role': 'solo', 'model': 'sonnet'}) + '\n')),
            ('no verifier result at all', lambda r: (r / '0413-resume' / 'verifier-L2.md').unlink()),
            ('a result that fails results.py validate', lambda r: ed(r / '0413-resume' / 'verifier-L2.md', '<!-- role=verifier', '<!-- x=verifier')),
            ('no recorded worker model', lambda r: (r / '0413-resume' / 'runs.jsonl').write_text(json.dumps({'role': 'verifier', 'file': 'verifier-L2.md'}) + '\n'))):
        tmp, root, plan = fresh()
        mut(root)
        row(f'C2 {label}: exit 1 with its own reason', run_all(root, plan), 1, 'open: step 2: no independent verifier pass (')
    tmp, root, plan = fresh()
    ed(root / '0413-resume' / 'verifier-L2.md', 'model=opus', 'model=sonnet')
    expect('plan_done: C2 the equal-model reason names the models', 'equals the worker model sonnet' in run_all(root, plan)['last'])
    tmp, root, plan = fresh()
    (root / '0902-close-out' / 'verifier-L2.md').unlink()
    row('C2 a verify: required L1 step with no verifier exits 1', run_all(root, plan), 1, 'open: step 4: no independent verifier pass (no verifier result')
    expect('plan_done: C2 the no-record reason names fanout.py land (T-0438: the record stays on the lane after a hand merge)', 'fanout.py land' in run_all(root, plan)['last'])
    tmp, root, plan = fresh()
    ed(plan, 'verify: required\ncap: $10', 'verify: auto\ncap: $10')
    (root / '0902-close-out' / 'verifier-L2.md').unlink()
    row('C2 control: an L1 step with verify: auto needs no verifier', run_all(root, plan), 0, 'plan done')
    # C3
    held_ac = '\n## Acceptance criteria\n- ships it [owner: integration]\n'
    held_ver = '## Criteria\n- #1 ships it: deferred integration. Evidence: no\n\n## For the next attempt\ndeferred: integration\n'
    settle = '## Criteria\n- #ticket#1 ships it: pass. Evidence: yes\n\n## For the next attempt\nNone\n\n## Settles\n- ticket#1\n'
    tmp, root, plan = fresh()
    d = root / '0413-resume'
    (d / 'handoff.md').write_text(FM.format(id='T-0413', status='done', size='L2', extra=held_ac), encoding='utf-8')
    (d / 'verifier-L2.md').write_text(VERIFIER.format(model='opus', verdict='fail', rest=held_ver), encoding='utf-8')
    row('C3 one deferred criterion exits 1 with a held line', run_all(root, plan), 1, 'held: step 2: #ticket#1 deferred integration')
    (d / 'verifier-L2-2.md').write_text(VERIFIER.format(model='opus', verdict='pass', rest=settle), encoding='utf-8')
    with open(d / 'runs.jsonl', 'a') as f:
        f.write(json.dumps({'role': 'verifier', 'level': 'L2', 'model': 'opus', 'file': 'verifier-L2-2.md'}) + '\n')
    row('C3 control: a later verifier pass that settles the ref turns it green', run_all(root, plan), 0, 'plan done')
    # C4
    tmp, root, plan = fresh(now='`printf 34.3`')
    row('C4 a measure printing 34.3 against <= 15 exits 1', run_all(root, plan), 1, 'kpi K-002 reads 34.3, target <= 15')
    tmp, root, plan = fresh(now='`printf 12`')
    row('C4 control: a measure printing 12 exits 0', run_all(root, plan), 0, 'plan done')
    tmp, root, plan = fresh(now='`printf hello`')
    row('C4 a measure printing text is unreadable, never 0', run_all(root, plan), 1, 'kpi K-002 unreadable')
    tmp, root, plan = fresh(now='`false`')
    row('C4 a failing command is unreadable, never 0', run_all(root, plan), 1, 'kpi K-002 unreadable')
    js = '`printf \'{"runs":{"interrupted":{"lost_min_median":12}}}\'`'
    tmp, root, plan = fresh(now=js)
    row('C4 a dotted read path into JSON output reads 12 and exits 0', run_all(root, plan), 0, 'plan done')
    ed(plan, 'runs.interrupted.lost_min_median', 'runs.interrupted.missing')
    row('C4 a read path absent from the JSON output is unreadable', run_all(root, plan), 1, 'kpi K-002 unreadable')
    tmp, root, plan = fresh(now='`printf 34.3`')
    ed(root / '0413-resume' / 'handoff.md', 'status: done', 'status: ready')
    expect('plan_done: C4 measures are not run while a ticket is open', not any(c == 'C4' for c, _, _ in run_all(root, plan)['items']))
    # C5
    tmp, root, plan = fresh()
    (tmp / 'docs' / 'references' / 'sdlc-internals.md').unlink()
    row('C5 an edit path that is missing exits 1', run_all(root, plan), 1, 'upsert: docs/references/sdlc-internals.md edit not satisfied')
    tmp, root, plan = fresh()
    ed(plan, '| docs/references/sdlc-internals.md | edit | 3 |', '| docs/references/sdlc-internals.md | edit | 3 |\n| docs/specs/old.md | retire | 3 |')
    (tmp / 'docs' / 'specs').mkdir()
    (tmp / 'docs' / 'specs' / 'old.md').write_text('x\n', encoding='utf-8')
    row('C5 a retire path still present exits 1', run_all(root, plan), 1, 'upsert: docs/specs/old.md retire not satisfied')
    (tmp / 'docs' / 'specs' / 'old.md').unlink()
    row('C5 control: a retire path that is gone is green', run_all(root, plan), 0, 'plan done')
    tmp, root, plan = fresh()
    ed(plan, '| docs/references/sdlc-internals.md | edit | 3 |', '| docs/references/sdlc-internals.md | edit | 3 |\n| docs/specs/new.md | create | 3 |')
    row('C5 a create path that is missing exits 1', run_all(root, plan), 1, 'upsert: docs/specs/new.md create not satisfied')
    # S
    tmp, root, plan = fresh()
    ed(root / '0413-resume' / 'handoff.md', 'status: done', 'status: ready')
    rc, out = cli(plan, root, 'stop', str(plan), '--reason', 'weekly limit', '--resume', 'rerun it')
    expect('plan_done: stop exits 0 and writes plan-state.json', rc == 0 and state_path(plan).is_file(), (rc, out))
    row('S a stop record plus one open item exits 4 with the resume command', run_all(root, plan), 4, 'stopped: weekly limit; resume: rerun it')
    ed(root / '0413-resume' / 'handoff.md', 'status: ready', 'status: done')
    row('S contrast: a stop record with everything green exits 0', run_all(root, plan), 0, 'plan done')
    state = json.loads(state_path(plan).read_text(encoding='utf-8'))
    expect('plan_done: plan-state.json holds replans and stopped and nothing else', sorted(state) == ['replans', 'stopped'] and state['replans'] == 0, state)
    expect('plan_done: stop appended one line to the notes file the plan names', (root / 'notes.md').read_text(encoding='utf-8').count('stopped: weekly limit') == 1)
    # work_root: the plan names docs/work/NOTES.md and stop writes it there
    tmp, root, plan = fresh()
    (root / 'config').write_text('work_root: docs/work\n', encoding='utf-8')
    plan.write_text(plan.read_text(encoding='utf-8').replace('.sdlc/notes.md', 'docs/work/NOTES.md'), encoding='utf-8')
    expect('plan_done: under work_root: docs/work a Budget naming docs/work/NOTES.md is no stop-rules defect',
           not any('stop-rules' in x for x in run_all(root, plan)['defects']), run_all(root, plan)['defects'])
    rc, out = cli(plan, root, 'stop', str(plan), '--reason', 'weekly limit')
    wn = tmp / 'docs' / 'work' / 'NOTES.md'
    expect('plan_done: under work_root stop appends to docs/work/NOTES.md and writes no .sdlc/notes.md',
           rc == 0 and wn.is_file() and 'stopped: weekly limit' in wn.read_text(encoding='utf-8') and not (root / 'notes.md').exists(), (rc, out))
    # resume (T-0438): the stop record clears without hand removal; the replan count survives
    tmp, root, plan = fresh()
    ed(root / '0413-resume' / 'handoff.md', 'status: done', 'status: ready')
    cli(plan, root, 'replan', str(plan), '--reason', 'defect')
    cli(plan, root, 'stop', str(plan), '--reason', 'merge conflict')
    expect('plan_done: the default resume command names the resume subcommand', f'plan_done.py resume {plan}' in run_all(root, plan)['last'], run_all(root, plan)['last'])
    rc, out = cli(plan, root, 'resume', str(plan))
    expect('plan_done: resume exits 0 and prints what it cleared', rc == 0 and out == ['resumed: cleared stop "merge conflict"'], (rc, out))
    st = json.loads(state_path(plan).read_text(encoding='utf-8'))
    row('resume: the open item is exit 1 again, no longer the sticky exit 4', run_all(root, plan), 1, 'open: step 2')
    expect('plan_done: resume keeps the replan count and holds no stop', st == {'replans': 1}, st)
    expect('plan_done: resume appended one notes line', (root / 'notes.md').read_text(encoding='utf-8').count('resumed after: merge conflict') == 1)
    rc, out = cli(plan, root, 'resume', str(plan))
    expect('plan_done: resume with no stop record exits 0 and says so', rc == 0 and out == ['resumed: no stop record'], (rc, out))
    # records only
    tmp, root, plan = fresh()
    row('records-only an all-green fixture exits 3 and never 0', run_all(root, plan, records_only=True), 3, 'records ok; measures not read')
    tmp, root, plan = fresh(now='`printf 34.3`')
    row('records-only does not read the measures: a red KPI still exits 3', run_all(root, plan, records_only=True), 3, 'records ok; measures not read')
    ed(root / '0413-resume' / 'handoff.md', 'status: done', 'status: ready')
    row('records-only with an open item exits 1', run_all(root, plan, records_only=True), 1, 'open: step 2')
    # plan defect
    tmp, root, plan = fresh()
    ed(plan, 'executor: solo-L2\nverify: auto\ncap: $12', 'executor: solo-L2\nverify: auto')
    row('defect a plan_check.py plan mutant (cap deleted) exits 2 with plan defect: step-shape', run_all(root, plan), 2, 'plan defect: step-shape')
    tmp, root, plan = fresh()
    ed(plan, 'ticket: T-0413', 'ticket: T-9999')
    row('defect a step naming ticket T-9999 that does not exist exits 2', run_all(root, plan), 2, 'plan defect: ticket-absent')
    tmp, root, plan = fresh()
    row('defect a plan file that does not exist exits 2', run_all(root, root / 'nope.md'), 2, 'plan defect: unreadable')
    # unstarted goal 002 plan
    tmp, root, plan = fresh()
    for folder, tid, size in TICKETS[:2]:
        ed(root / folder / 'handoff.md', 'status: done', 'status: ready')
    for folder in ('0901-collector-fields', '0902-close-out'):
        shutil.rmtree(root / folder)
    res = run_all(root, plan)
    row('unstarted the goal 002 shaped plan exits 1', res, 1, 'open: step 1')
    expect('plan_done: unstarted lists every step open', [i[1] for i in res['items'] if i[0] == 'C1'] == [1, 2, 3, 4] and not state_path(plan).exists(), res['items'])
    # replan cap, stop on the second call
    tmp, root, plan = fresh()
    rc1, out1 = cli(plan, root, 'replan', str(plan), '--reason', 'plan defect in step 2')
    expect('plan_done: the first replan exits 0 and counts', rc1 == 0 and json.loads(state_path(plan).read_text())['replans'] == 1, (rc1, out1))
    rc2, out2 = cli(plan, root, 'replan', str(plan), '--reason', 'again')
    st = json.loads(state_path(plan).read_text(encoding='utf-8'))
    expect('plan_done: a second replan refuses (exit 2), prints replan cap reached: stopped and writes the stop record',
           rc2 == 2 and out2 == ['replan cap reached: stopped'] and st['replans'] == 1 and st['stopped']['reason'].startswith('replan cap reached'), (rc2, out2, st))
    expect('plan_done: the refusal also wrote the notes line', 'replan cap reached' in (root / 'notes.md').read_text(encoding='utf-8'))
    ed(root / '0413-resume' / 'handoff.md', 'status: done', 'status: ready')
    row('replan cap: the stop the refusal wrote ends the run with exit 4 while an item is open', run_all(root, plan), 4, 'stopped: replan cap reached')
    # records dir (T-0541): solo runs.jsonl and the verifier pass only in .sdlc/runtime/tasks/<folder>/, or in place (legacy)
    for label, runtime in (('records dir: runtime-only fixture', True), ('records dir: legacy fixture', False)):
        tmp, root, plan = fresh()
        if runtime:
            for folder, _, _ in TICKETS:
                rd = root / 'runtime' / 'tasks' / folder
                rd.mkdir(parents=True)
                for name in ('verifier-L2.md', 'runs.jsonl'):
                    os.replace(root / folder / name, rd / name)
        moved = all((root / f / 'runs.jsonl').exists() != runtime for f, _, _ in TICKETS)
        res = run_all(root, plan)
        expect(f'plan_done: {label}: prints plan done', moved and res['code'] == 0 and res['last'] == 'plan done', (moved, res['code'], res['last'], res['items']))
    # the command line
    tmp, root, plan = fresh()
    rc, out = cli(plan, root)
    expect('plan_done: the command line exits 0 and prints plan done last', rc == 0 and out[-1] == 'plan done', (rc, out))
    rc, out = cli(plan, root, '--records-only')
    expect('plan_done: the command line --records-only exits 3', rc == 3 and out[-1] == 'records ok; measures not read', (rc, out))
    rc, out = cli(plan, root, '--json')
    expect('plan_done: --json prints one object with the exit code', rc == 0 and json.loads(out[-1])['exit'] == 0 and json.loads(out[-1])['last'] == 'plan done', (rc, out))
    p = subprocess.run([sys.executable, str(HERE / 'plan_done.py')], capture_output=True, text=True)
    expect('plan_done: no arguments is a usage error (exit 2)', p.returncode == 2)
    for d in tmpdirs:
        d.cleanup()
    print(f'plan_done selftest: {"FAIL" if bad else "PASS"} ({n[0]} checks)')
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    ap = argparse.ArgumentParser(prog='plan_done.py', description=__doc__.split('\n')[0])
    sub = None
    if argv[:1] in (['stop'], ['replan'], ['resume']):
        sub, argv = argv[0], argv[1:]
    ap.add_argument('plan')
    ap.add_argument('--root', default='.sdlc')
    if sub in ('stop', 'replan'):
        ap.add_argument('--reason', required=True)
    if sub == 'stop':
        ap.add_argument('--resume')
    if not sub:
        ap.add_argument('--records-only', action='store_true', help='skip the measures; exits 3 instead of 0')
        ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if sub:
        if not pathlib.Path(a.plan).is_file():
            print(f'plan defect: unreadable: {a.plan}', file=sys.stderr)
            return 2
        if sub == 'resume':
            why = do_resume(a.plan, a.root)
            print(f'resumed: cleared stop "{why}"' if why is not None else 'resumed: no stop record')
            return 0
        if sub == 'replan':
            return do_replan(a.plan, a.root, a.reason)
        do_stop(a.plan, a.root, a.reason, a.resume)
        print(f'stopped: {a.reason}; resume: {read_state(a.plan)["stopped"]["resume"]}')
        return 0
    res = assess(a.plan, a.root, a.records_only)
    for line in render(res, a.json):
        print(line)
    return res['code']


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
