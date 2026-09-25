#!/usr/bin/env python3
"""Render the sdlc status board from task dirs. Never compose the board by hand.

Usage: board.py [--root DIR] [--task SLUG] [--waiting LINE] [--summary] [selftest]
  --root     dir holding task dirs (default: .sdlc in the cwd; bench/results works too)
  --task     only this task
  --waiting  one line saying what the session waits on, printed above the table
  --summary  one compact line for the status line (newest task only; writes no state):
             "<task> <pct>% (<passed>/<steps>)", plus "🔴<n>" for blocked/failed steps and
             "⚠ L5" when a step is on the last builder level. Prints nothing if no tasks.
  selftest   render temp fixtures with and without ticket front matter; prove the column gate bites

A task dir is .sdlc/<task>/ with planner-L*.md and step-<n>/ subdirs (see skills/handoff-format).
Status is derived from files only: <role>-<level>.md (done), <role>-<level>.running (live),
the builder's "## Status", the verifier's "## Verdict", and runs.jsonl (cost).

Ticket columns: when at least one rendered task's handoff.md has ticket front matter (read with
tickets.py's parser, for display only), the table becomes | ID | Task | Ticket | Step | Status | % |,
where ID is the ticket id and Ticket its status; a task without front matter (or with an unreadable
handoff.md) gets empty cells there. With no front matter anywhere the table stays
| Task | Step | Status | % |. --summary never shows ticket fields.

% ladder: 0 queued, 10 building, 50 built, 70 verifying, 100 verifier pass.
A changed row ends with "· changed" (compared with a per-root state file in
$SDLC_BOARD_STATE_DIR, else ${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state;
never inside the repo).
"""
import argparse, hashlib, json, os, pathlib, re, subprocess, sys, tempfile

import tickets  # same scripts/ dir: the only front matter parser

LADDER = {'queued': 0, 'building': 10, 'built': 50, 'verifying': 70, 'verified': 100}


def section(md: pathlib.Path, heading: str) -> str:
    """First non-empty line under '## <heading>', lowercased."""
    lines = md.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.strip() == f'## {heading}':
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip().lower()
    return ''


def by_level(d: pathlib.Path, role: str, ext: str):
    return sorted(d.glob(f'{role}-L*.{ext}'), key=lambda p: p.stat().st_mtime)


def cost(d: pathlib.Path) -> float:
    total = 0.0
    for f in [d / 'runs.jsonl', *d.glob('step-*/runs.jsonl')]:
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    total += json.loads(line).get('cost_usd') or 0
                except json.JSONDecodeError:
                    pass
    return total


def level_of(p: pathlib.Path) -> str:
    return p.stem.split('-')[-1]


def step_row(step: pathlib.Path, title: str, planned_level: str):
    builds, verifies = by_level(step, 'builder', 'md'), by_level(step, 'verifier', 'md')
    attempts = len(json_lines(step / 'runs.jsonl', 'builder'))
    tries = f' · attempt {attempts}' if attempts > 1 else ''
    if by_level(step, 'builder', 'running'):
        lvl = level_of(by_level(step, 'builder', 'running')[-1])
        return '🟡', f'building · builder {lvl}{tries}', LADDER['building']
    if by_level(step, 'verifier', 'running'):
        lvl = level_of(by_level(step, 'verifier', 'running')[-1])
        return '🟡', f'verifying · verifier {lvl}{tries}', LADDER['verifying']
    if not builds:
        return '⏳', f'queued · planned {planned_level}', LADDER['queued']
    last_build = builds[-1]
    if section(last_build, 'Status').startswith('blocked'):
        return '🔴', f'blocked · builder {level_of(last_build)}{tries}', LADDER['building']
    if verifies and verifies[-1].stat().st_mtime >= last_build.stat().st_mtime:
        verdict = section(verifies[-1], 'Verdict')
        if verdict.startswith('pass'):
            return '🟢', f'pass · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}{tries}', LADDER['verified']
        return '🔴', f'fail · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}{tries}', LADDER['built']
    return '🟡', f'built · builder {level_of(last_build)}, awaiting verify{tries}', LADDER['built']


def json_lines(f: pathlib.Path, role: str):
    if not f.exists():
        return []
    out = []
    for line in f.read_text().splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get('role') == role:
            out.append(j)
    return out


def plan_steps(task: pathlib.Path):
    """Steps from step-<n>/handoff.md (rewritten by /chain on a replan), else from the newest plan."""
    dirs = sorted((d for d in task.glob('step-*') if (d / 'handoff.md').exists()),
                  key=lambda d: int(d.name.split('-')[1]) if d.name.split('-')[1].isdigit() else 0)
    if dirs:
        steps = []
        for d in dirs:
            text = (d / 'handoff.md').read_text()
            m = re.search(r'^## Step (\d+): (.+)$', text, re.M)
            lvl = re.search(r'^level:\s*(L\d)', text, re.M)
            n = int(d.name.split('-')[1])
            steps.append((n, m.group(2).strip() if m else d.name, lvl.group(1) if lvl else '?'))
        return steps
    plans = by_level(task, 'planner', 'md')
    if not plans:
        return []
    text = plans[-1].read_text()
    steps = []
    for m in re.finditer(r'^## Step (\d+): (.+)$', text, re.M):
        body = text[m.end():]
        lvl = re.search(r'^level:\s*(L\d)', body, re.M)
        steps.append((int(m.group(1)), m.group(2).strip(), lvl.group(1) if lvl else '?'))
    return steps


def task_rows(task: pathlib.Path):
    rows = []
    running = [p for p in task.glob('*.running')]
    steps = plan_steps(task)
    if running:
        role_lvl = running[-1].stem
        rows.append((task.name, 'task', '🟡', f'running · {role_lvl}', 0))
    elif not steps:
        rows.append((task.name, 'task', '⏳', 'not planned', 0))
    for n, title, lvl in steps:
        glyph, status, pct = step_row(task / f'step-{n}', title, lvl)
        rows.append((task.name, f'{n}. {title}', glyph, status, pct))
    grade = task / 'grade.md'
    if grade.exists():
        hidden = re.search(r'hidden_check:\s*(\w+)', grade.read_text())
        if hidden:
            ok = hidden.group(1) == 'pass'
            rows.append((task.name, 'hidden check', '🟢' if ok else '🔴', hidden.group(1), 100 if ok else 0))
    return rows, steps


def summary(root: pathlib.Path) -> str:
    if not root.is_dir():
        return ''
    tasks = [d for d in root.iterdir() if d.is_dir() and (d / 'handoff.md').exists()]
    if not tasks:
        return ''
    t = max(tasks, key=lambda d: max((p.stat().st_mtime for p in d.rglob('*')), default=0))
    rows, steps = task_rows(t)
    step_rows = [r for r in rows if r[1] not in ('task', 'hidden check')]
    if not step_rows:
        return f'{t.name} planning' if any(t.glob('*.running')) else f'{t.name} not planned'
    pct = sum(r[4] for r in step_rows) // len(step_rows)
    passed = sum(1 for r in step_rows if r[2] == '🟢')
    parts = [f'{t.name} {pct}% ({passed}/{len(step_rows)})']
    bad = sum(1 for r in step_rows if r[2] == '🔴')
    if bad:
        parts.append(f'🔴{bad}')
    if any(t.glob('step-*/builder-L5.*')):
        parts.append('⚠ L5')
    return ' · '.join(parts)


def ticket_of(task: pathlib.Path):
    """(id, status) from the task's ticket front matter, or None when it has none.
    Any read or parse error counts as no front matter: a bad file must not break the board."""
    try:
        meta = tickets.parse((task / 'handoff.md').read_text(encoding='utf-8'))
    except Exception:
        return None
    if not isinstance(meta, dict):
        return None
    return tuple(v if isinstance(v, str) else '' for v in (meta.get('id'), meta.get('status')))


def has_step_work(task: pathlib.Path) -> bool:
    """True when the task has any recorded step work: a planner-L*.md, a step-*/handoff.md,
    or a *.running file."""
    return bool(list(task.glob('planner-L*.md')) or list(task.glob('step-*/handoff.md'))
                or list(task.glob('*.running')))


# Board visibility per ticket status. A new status in tickets.ENUMS['status'] must be
# classified in exactly one of these sets; selftest() fails until it is.
ALWAYS_HIDDEN = frozenset({'dropped'})
HIDDEN_WITHOUT_STEP_WORK = frozenset({'done'})
ALWAYS_SHOWN = frozenset({'proposed', 'ready', 'blocked'})


def belongs_on_board(task: pathlib.Path) -> bool:
    """False only when the task has ticket front matter and is dropped, or done with no
    recorded step work. Everything else (no front matter, other statuses, or done with
    step work) stays visible."""
    front = ticket_of(task)
    if front is None:
        return True
    _, status = front
    if status in ALWAYS_HIDDEN:
        return False
    if status in HIDDEN_WITHOUT_STEP_WORK and not has_step_work(task):
        return False
    return True  # ALWAYS_SHOWN, and any unknown status, stays visible


def unclassified_statuses(known, sets=None):
    """Problems with the board visibility sets against `known` statuses: a known status in
    no set, a status in two sets, or a classified status not in `known`. Empty means OK."""
    if sets is None:
        sets = {'ALWAYS_HIDDEN': ALWAYS_HIDDEN,
                'HIDDEN_WITHOUT_STEP_WORK': HIDDEN_WITHOUT_STEP_WORK,
                'ALWAYS_SHOWN': ALWAYS_SHOWN}
    problems = []
    classified = frozenset().union(*sets.values())
    for s in sorted(set(known) - classified):
        problems.append(f'status {s!r} is not classified in any board visibility set')
    names = list(sets)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for s in sorted(sets[a] & sets[b]):
                problems.append(f'status {s!r} is in both {a} and {b}')
    for s in sorted(classified - set(known)):
        problems.append(f'status {s!r} is classified but not a known status')
    return problems


def sort_tasks(tasks, mode='recent'):
    """Order task dirs: 'recent' by mtime, 'name' by folder name, 'id' by the numeric part
    of the ticket id with tasks lacking an id after, by folder name. 'auto' (what main()
    uses with no --sort when any rendered task has a ticket) is 'id' except that tasks
    lacking an id follow by mtime."""
    if mode == 'name':
        return sorted(tasks, key=lambda t: t.name)
    if mode in ('id', 'auto'):
        def key(t):
            front = ticket_of(t)
            m = re.search(r'T-(\d+)', front[0]) if front else None
            if m:
                return (0, int(m.group(1)), 0, t.name)
            return (1, 0, t.stat().st_mtime if mode == 'auto' else 0, t.name)
        return sorted(tasks, key=key)
    return sorted(tasks, key=lambda d: d.stat().st_mtime)


def state_path(root: pathlib.Path) -> pathlib.Path:
    """Where render() keeps the last statuses for root: outside the working tree."""
    d = os.environ.get('SDLC_BOARD_STATE_DIR')
    if d:
        base = pathlib.Path(d)
    else:
        cache = os.environ.get('XDG_CACHE_HOME') or os.path.expanduser('~/.cache')
        base = pathlib.Path(cache) / 'sdlc-lite' / 'board-state'
    key = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16]
    return base / f'{key}.json'


def render(root: pathlib.Path, tasks, waiting=None) -> str:
    state_file = state_path(root)
    try:
        old = json.loads(state_file.read_text())
    except (OSError, json.JSONDecodeError):
        old = {}
    fronts = {t: ticket_of(t) for t in tasks}
    with_ticket = any(f is not None for f in fronts.values())
    new, out = {}, []
    if waiting:
        out.append(waiting)
        out.append('')
    if with_ticket:
        out.append('| ID | Task | Ticket | Step | Status | % |')
        out.append('|---|---|---|---|---|---|')
    else:
        out.append('| Task | Step | Status | % |')
        out.append('|---|---|---|---|')
    total_cost, pcts = 0.0, []
    for t in tasks:
        rows, steps = task_rows(t)
        total_cost += cost(t)
        tid, tstatus = fronts[t] or ('', '')
        for task, step, glyph, status, pct in rows:
            key = f'{task}/{step}'
            cell = f'{glyph} {status}'
            new[key] = cell
            changed = ' · changed' if old and old.get(key) != cell else ''
            if with_ticket:
                out.append(f'| {tid} | {task} | {tstatus} | {step} | {cell}{changed} | {pct} |')
            else:
                out.append(f'| {task} | {step} | {cell}{changed} | {pct} |')
            if step not in ('task', 'hidden check'):
                pcts.append(pct)
    if pcts:
        out.append('')
        out.append(f'{sum(pcts) // len(pcts)}% across {len(pcts)} steps · ${total_cost:.2f} spent')
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(new, indent=1))
    except OSError:
        pass
    return '\n'.join(out)


def selftest() -> int:
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    front = ('---\nid: T-0042\ntitle: "Fixture"\ntype: chore\nstatus: ready\nsize: S\n'
             'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n')

    def task_dir(root, name, content):
        d = root / name
        d.mkdir(parents=True)
        h = d / 'handoff.md'
        h.write_bytes(content) if isinstance(content, bytes) else h.write_text(content, encoding='utf-8')
        return d

    saved_state_dir = os.environ.get('SDLC_BOARD_STATE_DIR')
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state_tmp:
        tmp = pathlib.Path(tmp)
        state_dir = pathlib.Path(state_tmp)
        # Outside every fixture root; subprocess runs inherit it.
        os.environ['SDLC_BOARD_STATE_DIR'] = str(state_dir)

        def clear_state():
            for f in state_dir.glob('*.json'):
                f.unlink(missing_ok=True)

        # 1. No task has front matter: today's 4-column table, byte for byte.
        plain = tmp / 'plain'
        t = task_dir(plain, 'plain-task', '## Goal\nno front matter\n')
        got = render(plain, [t])
        want = '| Task | Step | Status | % |\n|---|---|---|---|\n| plain-task | task | ⏳ not planned | 0 |'
        expect(f'no front matter renders the 4-column table byte for byte, got {got!r}', got == want)

        # 2. Front matter mixed with no front matter and an undecodable handoff.md.
        mixed = tmp / 'mixed'
        ts = [task_dir(mixed, 'ticketed', front),
              task_dir(mixed, 'bare', '## Goal\nno front matter\n'),
              task_dir(mixed, 'broken', b'---\nid: \xff\xfe\n---\n')]
        try:
            got = render(mixed, ts)
        except Exception as e:
            got = ''
            expect(f'mixed render crashed: {e!r}', False)
        lines = got.splitlines()
        expect(f'mixed render has the 6-column header, got {lines[:1]}',
               lines[:2] == ['| ID | Task | Ticket | Step | Status | % |', '|---|---|---|---|---|---|'])
        expect('ticketed row shows its id and status',
               '| T-0042 | ticketed | ready | task | ⏳ not planned | 0 |' in lines)
        expect('bare row has empty ID and Ticket cells', '|  | bare |  | task | ⏳ not planned | 0 |' in lines)
        expect('undecodable handoff.md row has empty ID and Ticket cells',
               '|  | broken |  | task | ⏳ not planned | 0 |' in lines)

        # 3. tickets.parse raising counts as no front matter and does not crash.
        raising = tmp / 'raising'
        t = task_dir(raising, 'raises', front)
        real = tickets.parse

        def boom(text):
            raise ValueError('fixture parse failure')
        tickets.parse = boom
        try:
            got = render(raising, [t])
        except Exception as e:
            got = ''
            expect(f'render crashed when tickets.parse raised: {e!r}', False)
        finally:
            tickets.parse = real
        expect(f'tickets.parse raising falls back to the 4-column table, got {got!r}',
               got == '| Task | Step | Status | % |\n|---|---|---|---|\n| raises | task | ⏳ not planned | 0 |')

        # 4. --summary ignores front matter.
        solo = tmp / 'solo'
        task_dir(solo, 'ticketed', front)
        got = summary(solo)
        expect(f'summary unchanged by front matter, got {got!r}', got == 'ticketed not planned')

        # 5. Dropped/done filter: dropped is hidden regardless of steps; done is hidden only
        # without step work; other statuses (e.g. proposed) stay visible without over-filtering.
        gate = tmp / 'gate'

        def front_with(status):
            return ('---\nid: T-0099\ntitle: "Fixture"\ntype: chore\nstatus: %s\nsize: S\n'
                    'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n') % status

        dropped_no_steps = task_dir(gate, 'dropped-no-steps', front_with('dropped'))
        dropped_with_plan = task_dir(gate, 'dropped-with-plan', front_with('dropped'))
        (dropped_with_plan / 'planner-L1.md').write_text('## Plan\n')
        done_no_steps = task_dir(gate, 'done-no-steps', front_with('done'))
        done_with_plan = task_dir(gate, 'done-with-plan', front_with('done'))
        (done_with_plan / 'planner-L1.md').write_text('## Plan\n')
        done_with_step = task_dir(gate, 'done-with-step', front_with('done'))
        (done_with_step / 'step-1').mkdir()
        (done_with_step / 'step-1' / 'handoff.md').write_text('## Step 1: x\nlevel: L1\n')
        proposed_no_steps = task_dir(gate, 'proposed-no-steps', front_with('proposed'))

        expect('dropped ticket with no steps is hidden', not belongs_on_board(dropped_no_steps))
        expect('dropped ticket with a planner file is still hidden',
               not belongs_on_board(dropped_with_plan))
        expect('done ticket with no steps is hidden', not belongs_on_board(done_no_steps))
        expect('done ticket with a planner file is shown', belongs_on_board(done_with_plan))
        expect('done ticket with a step handoff is shown', belongs_on_board(done_with_step))
        expect('proposed ticket with no steps is still shown', belongs_on_board(proposed_no_steps))

        # 5b. Same gate fixture through main()'s actual task selection (subprocess), not just
        # belongs_on_board() in isolation: proves the filter is wired into main(), not just defined.
        proc = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), '--root', str(gate)],
                               capture_output=True, text=True)
        out = proc.stdout
        expect(f'main() subprocess exited 0, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 0)
        expect('main() output hides dropped-no-steps', 'dropped-no-steps' not in out)
        expect('main() output hides dropped-with-plan', 'dropped-with-plan' not in out)
        expect('main() output hides done-no-steps', 'done-no-steps' not in out)
        expect('main() output shows done-with-plan', 'done-with-plan' in out)
        expect('main() output shows done-with-step', 'done-with-step' in out)
        expect('main() output shows proposed-no-steps', 'proposed-no-steps' in out)

        # 6. --sort through main(): id ignores mtime, unticketed tasks follow by name,
        # name is alphabetical. With no flag, a root with tickets sorts by id with
        # unticketed tasks after by mtime; a root without tickets equals --sort recent.
        def ticket_front(tid):
            return front.replace('T-0042', tid)

        def run_main(root, *extra):
            proc = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                                   '--root', str(root), *extra], capture_output=True, text=True)
            expect(f'main() {extra} exited 0, got {proc.returncode} stderr={proc.stderr!r}',
                   proc.returncode == 0)
            return proc.stdout

        def order(out, names):
            return sorted((n for n in names if f'| {n} |' in out), key=lambda n: out.index(f'| {n} |'))

        srt = tmp / 'sort'
        made = [task_dir(srt, 'zulu-three', ticket_front('T-0003')),
                task_dir(srt, 'yankee-two', ticket_front('T-0002')),
                task_dir(srt, 'bravo', '## Goal\nno front matter\n'),
                task_dir(srt, 'alpha', '## Goal\nno front matter\n')]
        for i, d in enumerate(made):
            os.utime(d, (1_000_000 + i * 100, 1_000_000 + i * 100))
        names = [d.name for d in made]
        got = order(run_main(srt, '--sort', 'id'), names)
        expect(f'--sort id puts T-0002 before T-0003, then unticketed by name, got {got}',
               got == ['yankee-two', 'zulu-three', 'alpha', 'bravo'])
        got = order(run_main(srt, '--sort', 'name'), names)
        expect(f'--sort name is alphabetical, got {got}', got == sorted(names))
        got = order(run_main(srt, '--sort', 'recent'), names)
        expect(f'--sort recent is mtime order, got {got}', got == names)
        # Unticketed tasks follow by mtime: derive the expected order from the utime values.
        unticketed = sorted((d for d in made if d.name in ('alpha', 'bravo')),
                            key=lambda d: d.stat().st_mtime)
        want = ['yankee-two', 'zulu-three'] + [d.name for d in unticketed]
        got = order(run_main(srt), names)
        expect(f'no --sort with tickets is id then unticketed by mtime, want {want}, got {got}',
               got == want and want != ['yankee-two', 'zulu-three', 'alpha', 'bravo'])

        plain = tmp / 'sort-plain'
        pmade = [task_dir(plain, 'charlie', '## Goal\nno front matter\n'),
                 task_dir(plain, 'alpha', '## Goal\nno front matter\n'),
                 task_dir(plain, 'bravo', '## Goal\nno front matter\n')]
        for i, d in enumerate(pmade):
            os.utime(d, (1_000_000 + i * 100, 1_000_000 + i * 100))
        pnames = [d.name for d in pmade]
        got = order(run_main(plain), pnames)
        expect(f'no --sort without tickets is mtime order, got {got}', got == pnames)
        # The state file adds ' · changed' markers between runs; compare with it removed.
        clear_state()
        default = run_main(plain)
        clear_state()
        expect('no --sort without tickets equals --sort recent',
               default == run_main(plain, '--sort', 'recent'))

        # 5b. Renders write nothing under the root, and "· changed" still works.
        clean = tmp / 'clean'
        ct = task_dir(clean, 'clean-task', '## Goal\nx\n')
        before = sorted(p for p in clean.rglob('*'))
        first = render(clean, [ct])
        (ct / 'planner-L1.running').touch()
        second = render(clean, [ct])
        after = sorted(p for p in clean.rglob('*') if p.name != 'planner-L1.running')
        expect('render writes no .board-state.json under the root',
               not list(clean.rglob('.board-state.json')))
        expect(f'render creates no file under the root, got {set(after) - set(before)}',
               after == before)
        expect(f'first render has no changed marker, got {first!r}', '· changed' not in first)
        expect(f'a status change between renders shows "· changed", got {second!r}',
               '· changed' in second)
        expect('two roots get different state paths',
               state_path(clean) != state_path(plain) and state_path(clean).parent == state_dir)

    if saved_state_dir is None:
        os.environ.pop('SDLC_BOARD_STATE_DIR', None)
    else:
        os.environ['SDLC_BOARD_STATE_DIR'] = saved_state_dir

    # 6. Every ticket status is classified for board visibility, and the guard bites.
    known = set(tickets.ENUMS['status'])
    probs = unclassified_statuses(known)
    expect(f'every ticket status has a board visibility class, got {probs}', probs == [])
    probs = unclassified_statuses(known | {'zz-new-status'})
    expect('an unclassified status is reported',
           any('zz-new-status' in p for p in probs))
    probs = unclassified_statuses(known, {'ALWAYS_HIDDEN': ALWAYS_HIDDEN,
                                          'HIDDEN_WITHOUT_STEP_WORK': HIDDEN_WITHOUT_STEP_WORK,
                                          'ALWAYS_SHOWN': ALWAYS_SHOWN,
                                          'EXTRA': frozenset({'dropped'})})
    expect('a status in two visibility sets is reported',
           any("'dropped'" in p and 'both' in p for p in probs))

    if misses:
        print('board selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('board selftest: PASS')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', nargs='?', choices=['selftest'])
    ap.add_argument('--root', default='.sdlc')
    ap.add_argument('--task')
    ap.add_argument('--waiting')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--sort', choices=['recent', 'id', 'name'], default=None)
    a = ap.parse_args()
    if a.cmd == 'selftest':
        sys.exit(selftest())
    root = pathlib.Path(a.root)
    if a.summary:
        print(summary(root))
        return
    if not root.is_dir():
        print(f'no task dirs: {root} does not exist', file=sys.stderr)
        sys.exit(1)
    candidates = [d for d in root.iterdir() if d.is_dir() and (d / 'handoff.md').exists()]
    tasks = [t for t in candidates if belongs_on_board(t)]
    mode = a.sort or ('auto' if any(ticket_of(t) for t in tasks) else 'recent')
    tasks = sort_tasks(tasks, mode)
    if a.task:
        tasks = [t for t in tasks if t.name == a.task]
        if not tasks:
            print(f'no task named {a.task} in {root}', file=sys.stderr)
            sys.exit(1)
    print(render(root, tasks, a.waiting))


if __name__ == '__main__':
    main()
