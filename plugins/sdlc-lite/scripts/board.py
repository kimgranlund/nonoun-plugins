#!/usr/bin/env python3
"""Render the sdlc status board from task dirs. Never compose the board by hand.

Usage: board.py [--root DIR] [--task SLUG] [--waiting LINE]
  --root     dir holding task dirs (default: .sdlc in the cwd; bench/results works too)
  --task     only this task
  --waiting  one line saying what the session waits on, printed above the table
  --summary  one compact line for the status line (newest task only; writes no state):
             "<task> <pct>% (<passed>/<steps>)", plus "🔴<n>" for blocked/failed steps and
             "⚠ L5" when a step is on the last builder level. Prints nothing if no tasks.

A task dir is .sdlc/<task>/ with planner-L*.md and step-<n>/ subdirs (see skills/handoff-format).
Status is derived from files only: <role>-<level>.md (done), <role>-<level>.running (live),
the builder's "## Status", the verifier's "## Verdict", and runs.jsonl (cost).

% ladder: 0 queued, 10 building, 50 built, 70 verifying, 100 verifier pass.
A changed row ends with "· changed" (compared with <root>/.board-state.json).
"""
import argparse, json, pathlib, re, sys

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.sdlc')
    ap.add_argument('--task')
    ap.add_argument('--waiting')
    ap.add_argument('--summary', action='store_true')
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    if a.summary:
        print(summary(root))
        return
    if not root.is_dir():
        print(f'no task dirs: {root} does not exist', file=sys.stderr)
        sys.exit(1)
    tasks = sorted((d for d in root.iterdir() if d.is_dir() and (d / 'handoff.md').exists()),
                   key=lambda d: d.stat().st_mtime)
    if a.task:
        tasks = [t for t in tasks if t.name == a.task]
        if not tasks:
            print(f'no task named {a.task} in {root}', file=sys.stderr)
            sys.exit(1)

    state_file = root / '.board-state.json'
    try:
        old = json.loads(state_file.read_text())
    except (OSError, json.JSONDecodeError):
        old = {}
    new, out = {}, []
    if a.waiting:
        out.append(a.waiting)
        out.append('')
    out.append('| Task | Step | Status | % |')
    out.append('|---|---|---|---|')
    total_cost, pcts = 0.0, []
    for t in tasks:
        rows, steps = task_rows(t)
        total_cost += cost(t)
        for task, step, glyph, status, pct in rows:
            key = f'{task}/{step}'
            cell = f'{glyph} {status}'
            new[key] = cell
            changed = ' · changed' if old and old.get(key) != cell else ''
            out.append(f'| {task} | {step} | {cell}{changed} | {pct} |')
            if step not in ('task', 'hidden check'):
                pcts.append(pct)
    if pcts:
        out.append('')
        out.append(f'{sum(pcts) // len(pcts)}% across {len(pcts)} steps · ${total_cost:.2f} spent')
    try:
        state_file.write_text(json.dumps(new, indent=1))
    except OSError:
        pass
    print('\n'.join(out))


if __name__ == '__main__':
    main()
