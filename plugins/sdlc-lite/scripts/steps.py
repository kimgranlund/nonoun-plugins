#!/usr/bin/env python3
"""Split a planner result into one step handoff per step, so /chain never parses a plan by hand.

Usage: steps.py {split <planner.md | task dir> [--only N ...] | selftest}
  split     read the plan (a planner-*.md file, or the newest planner-*.md in a task dir,
            by recorded run order in its runs.jsonl, see order.py)
            and the task goal (the ## Goal section of <task dir>/handoff.md, front matter skipped),
            then write <task dir>/step-<n>/handoff.md as "## Task goal", the goal, a blank line,
            and the step block verbatim (## Step <n>: ... up to the next ## heading, trailing
            blank lines trimmed). Prints one line per file written.
            --only N (repeatable) writes only those steps; an N not in the plan is an error.
            Refuses a step whose step-<n>/ already holds builder-*.md or verifier-*.md: rename it
            to step-<n>.superseded-<k>/ first (/chain 4.2). This script never renames anything.
            Every check runs before any write: a failure prints on stderr, exits 1, writes nothing.
  selftest  build fixtures in a temp dir and prove every case and every failure fires
"""
import argparse
import contextlib
import io
import os
import pathlib
import re
import sys
import tempfile

import order

STEP_RE = re.compile(r'^## Step (\d+): (.+)$')
LEVEL_RE = re.compile(r'^level: L[1-5]\s*$')


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback."""


def find_plan(target):
    """Return (planner file, task dir) for a planner file or a task dir."""
    target = pathlib.Path(target)
    if target.is_dir():
        plan = order.newest(target, 'planner')
        if not plan:
            raise Fail(f'steps: no planner-*.md in {target}')
        return pathlib.Path(plan), target
    if target.is_file():
        return target, target.parent
    raise Fail(f'steps: no such file or directory: {target}')


def read_goal(task_dir):
    handoff = task_dir / 'handoff.md'
    if not handoff.is_file():
        raise Fail(f'steps: no task handoff at {handoff}; the goal comes from its ## Goal section')
    lines = handoff.read_text(encoding='utf-8').splitlines()
    i = 0
    if lines and lines[0].strip() == '---':
        end = next((j for j in range(1, len(lines)) if lines[j].strip() == '---'), None)
        if end is None:
            raise Fail(f'steps: {handoff} opens front matter with --- but never closes it')
        i = end + 1
    start = next((j for j in range(i, len(lines)) if lines[j].rstrip() == '## Goal'), None)
    if start is None:
        raise Fail(f'steps: {handoff} has no ## Goal section')
    body = []
    for line in lines[start + 1:]:
        if line.startswith('## '):
            break
        body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body:
        raise Fail(f'steps: the ## Goal section of {handoff} is empty')
    return '\n'.join(body)


def parse_steps(plan):
    """Return {n: block text} in plan order. A block runs from its ## Step line to the next ## line."""
    steps = {}
    cur = None
    for line in plan.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            cur = None
            m = STEP_RE.match(line)
            if m:
                n = int(m.group(1))
                if n in steps:
                    raise Fail(f'steps: {plan} has step {n} twice')
                steps[n] = cur = [line]
            continue
        if cur is not None:
            cur.append(line)
    if not steps:
        raise Fail(f'steps: {plan} has no "## Step <n>: <title>" blocks')
    out = {}
    for n, block in steps.items():
        while block and not block[-1].strip():
            block.pop()
        if not any(LEVEL_RE.match(line) for line in block):
            raise Fail(f'steps: step {n} in {plan} has no "level: L1".."level: L5" line')
        out[n] = '\n'.join(block)
    return out


def split(target, only=None):
    """Check everything, then write. Returns the paths written."""
    plan, task_dir = find_plan(target)
    goal = read_goal(task_dir)
    steps = parse_steps(plan)
    if only:
        missing = sorted(set(n for n in only if n not in steps))
        if missing:
            raise Fail(f'steps: --only {", ".join(map(str, missing))} not in {plan} '
                       f'(steps: {", ".join(map(str, steps))})')
        chosen = [n for n in steps if n in set(only)]
    else:
        chosen = list(steps)
    for n in chosen:
        d = task_dir / f'step-{n}'
        done = sorted(p.name for pat in ('builder-*.md', 'verifier-*.md') for p in d.glob(pat)) if d.is_dir() else []
        if done:
            raise Fail(f'steps: {d} already holds role output ({", ".join(done)}). Per /chain 4.2, rename it '
                       f'to step-{n}.superseded-<k>/ (next free k) first, then split again. Nothing was written.')
    written = []
    for n in chosen:
        d = task_dir / f'step-{n}'
        d.mkdir(parents=True, exist_ok=True)
        path = d / 'handoff.md'
        path.write_text(f'## Task goal\n{goal}\n\n{steps[n]}\n', encoding='utf-8')
        written.append(path)
    return written


def cmd_split(target, only):
    try:
        written = split(target, only)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    for p in written:
        print(p)
    return 0


# --- selftest ---------------------------------------------------------------

HANDOFF = """---
id: T-0001
title: "x"
---

## Goal

Ship the widget.
Second goal line.

## Intent
- not part of the goal
"""

GOAL = 'Ship the widget.\nSecond goal line.'

STEP1 = """## Step 1: First thing
level: L2
### Do
Do one.

### Acceptance criteria
- one works"""

STEP2 = """## Step 2: Second thing
level: L1
### Do
Do two.
### Acceptance criteria
- two works"""

PLAN = f"""# Plan
## Goal
plan goal, not the task goal

{STEP1}


{STEP2}

## Risks
- RISKTEXT must not leak
"""


def snapshot(root):
    """Every file under root: relative path -> (mtime_ns, bytes)."""
    snap = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = pathlib.Path(dirpath) / f
            snap[str(p.relative_to(root))] = (p.stat().st_mtime_ns, p.read_bytes())
    return snap


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def selftest():
    misses = []

    def check(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        count = [0]

        def task(plan=PLAN, handoff=HANDOFF, plan_name='planner-L2.md'):
            count[0] += 1
            d = tmp / f'task{count[0]}'
            d.mkdir()
            if handoff is not None:
                (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            if plan is not None:
                (d / plan_name).write_text(plan, encoding='utf-8')
            return d

        def refused(name, argv, root, needle=None):
            before = snapshot(root)
            rc, out, err = run_main(argv)
            check(name, rc != 0 and err.strip() != '' and out == '' and snapshot(root) == before
                  and (needle is None or needle in err))

        want1 = f'## Task goal\n{GOAL}\n\n{STEP1}\n'
        want2 = f'## Task goal\n{GOAL}\n\n{STEP2}\n'

        # (a) normal plan followed by ## Risks
        d = task()
        rc, out, _ = run_main(['split', str(d / 'planner-L2.md')])
        h1, h2 = d / 'step-1' / 'handoff.md', d / 'step-2' / 'handoff.md'
        got1 = h1.read_text(encoding='utf-8') if h1.is_file() else None
        got2 = h2.read_text(encoding='utf-8') if h2.is_file() else None
        check('(a) 2-step plan writes both handoffs exactly, Risks stays out',
              rc == 0 and got1 == want1 and got2 == want2 and got2 is not None and 'RISKTEXT' not in got2
              and out.split() == [str(h1), str(h2)])

        # (b) --only 2 writes only step-2; --only 9 fails and writes nothing
        d = task()
        rc, out, _ = run_main(['split', str(d), '--only', '2'])
        h2 = d / 'step-2' / 'handoff.md'
        check('(b) --only 2 writes only step-2',
              rc == 0 and not (d / 'step-1').exists() and h2.is_file()
              and h2.read_text(encoding='utf-8') == want2)
        d = task()
        refused('(b) --only 9 fails and writes nothing', ['split', str(d), '--only', '9'], d)

        # (c) task dir input picks the newest planner-*.md by recorded run order, never by file time
        def c_case(times, runs):
            d = task(plan=PLAN.replace('Do one.', 'L3 PLAN'), plan_name='planner-L3.md')
            (d / 'planner-L2.md').write_text(PLAN.replace('Do one.', 'L2 PLAN'), encoding='utf-8')
            for name, t in times.items():
                os.utime(d / name, (t, t))
            if runs is not None:
                (d / 'runs.jsonl').write_text(''.join(
                    f'{{"role": "planner", "level": "{n[8:10]}", "file": "{n}"}}\n' for n in runs), encoding='utf-8')
            rc, _, _ = run_main(['split', str(d)])
            h1 = d / 'step-1' / 'handoff.md'
            return rc, h1.read_text(encoding='utf-8') if h1.is_file() else ''

        def uses(res, want, other):
            rc, got = res
            return rc == 0 and f'{want} PLAN' in got and f'{other} PLAN' not in got

        recorded = ['planner-L3.md', 'planner-L2.md']
        check('(c) equal mtimes: runs.jsonl decides, the lower-named file recorded last is used',
              uses(c_case({'planner-L2.md': 1_000_000, 'planner-L3.md': 1_000_000}, recorded), 'L2', 'L3'))
        check('(c) inverse mtimes: runs.jsonl still decides, same result',
              uses(c_case({'planner-L2.md': 1_000_000, 'planner-L3.md': 2_000_000}, recorded), 'L2', 'L3'))
        check('(c) no runs.jsonl: level then k order, planner-L3.md beats a newer planner-L2.md',
              uses(c_case({'planner-L3.md': 1_000_000, 'planner-L2.md': 2_000_000}, None), 'L3', 'L2'))

        # (d) a step with no level line
        d = task(plan=PLAN.replace('level: L1\n', 'Level is L1\n'))
        refused('(d) missing level: fails and writes nothing', ['split', str(d)], d)

        # (e) duplicate step number
        d = task(plan=PLAN.replace('## Step 2:', '## Step 1:'))
        refused('(e) duplicate step number fails and writes nothing', ['split', str(d)], d)

        # (f) no steps
        d = task(plan='# Plan\n## Goal\nnothing\n## Risks\n- none\n')
        refused('(f) no steps fails and writes nothing', ['split', str(d)], d)

        # (g) step-1 holds builder output: refuse, step-1 and step-2 untouched
        d = task()
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text('old step 1\n', encoding='utf-8')
        (d / 'step-1' / 'builder-L2.md').write_text('## Status\ndone\n', encoding='utf-8')
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'handoff.md').write_text('old step 2\n', encoding='utf-8')
        refused('(g) step-1 with builder-L2.md refuses, names superseded, changes nothing',
                ['split', str(d)], d, needle='superseded')
        d = task()
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'verifier-L1.md').write_text('pass\n', encoding='utf-8')
        refused('(g) verifier-*.md output also refuses', ['split', str(d)], d, needle='superseded')

        # (h) handoff with no Goal section, and no handoff at all
        d = task(handoff='---\nid: T-0001\n---\n\n## Intent\n- x\n')
        refused('(h) handoff with no ## Goal fails and writes nothing', ['split', str(d)], d)
        d2 = task(handoff=None)
        refused('(h) missing handoff.md fails and writes nothing', ['split', str(d2)], d2)

        # re-split over a plain handoff.md with no role output overwrites it
        d = task()
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text('stale\n', encoding='utf-8')
        rc, _, _ = run_main(['split', str(d)])
        check('re-split overwrites a plain step-1/handoff.md with no role output',
              rc == 0 and (d / 'step-1' / 'handoff.md').read_text(encoding='utf-8') == want1)

    if misses:
        print('steps selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('steps selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='steps.py', description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('split', help='write step-<n>/handoff.md for each step of a plan')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    p.add_argument('--only', type=int, action='append', metavar='N', help='write only step N (repeatable)')
    sub.add_parser('selftest', help='prove every case and every refusal fires')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    return cmd_split(a.target, a.only)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
