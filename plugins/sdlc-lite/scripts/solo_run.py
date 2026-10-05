#!/usr/bin/env python3
"""Start the solo agent for one ticket and record its cost, so the default lane is metered.

  solo_run.py run --task-dir DIR --tier S|M|L (--brief TEXT | --brief-file FILE | --brief -)
                  [--backend claude|codex] [--cwd DIR] [--timeout SECONDS] [--raw-out FILE]
  solo_run.py selftest

run starts the session at the tier's model and effort (agents/solo.md), prints the agent's report on
stdout, and appends one line to <task-dir>/runs.jsonl in the record shape run.sh writes for roles
(ts, role solo, level L1..L3 for tier S..L, model, effort, cost_usd, usage, duration_ms, turns, attempt_id,
backend, transport, routing_reason). --task-dir is the ticket or task folder, the one holding handoff.md.
budget.py sums cost_usd over every runs.jsonl under the ticket and counts a record with no numeric cost
as unmetered, so this record is all the budget gate and the board need.

Cost is never guessed. A result with no total_cost_usd (a crash, a missing result event, Codex, which
reports none) records cost_usd null with a cost_reason, and the budget reports that run as unmetered.

Claude: `SDLC_ROLE=solo claude -p --plugin-dir <plugin> --agent sdlc-lite:solo --model M --effort E
--dangerously-skip-permissions --output-format json -- <brief>`. Codex: `codex_exec.py solo L1..L3 <brief>`.
Exit status is the session's own, or 1 when it reported an error.
"""
import argparse
import contextlib
import io
import json
import math
import os
import pathlib
import shlex
import subprocess
import sys
import tempfile
import time
import uuid

SCRIPTS = pathlib.Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
# Solo tiers (agents/solo.md): tier -> (Claude model, Claude effort, level). The same table as fanout.SOLO_TIERS;
# check.py guards that solo.md, fanout.py and this table agree.
TIERS = {'S': ('sonnet', 'low', 'L1'), 'M': ('sonnet', 'xhigh', 'L2'), 'L': ('opus', 'xhigh', 'L3')}
CODEX_MODELS = {'L1': ('gpt-6.1-sol', 'low'), 'L2': ('gpt-6.1-sol', 'high'), 'L3': ('gpt-6.1-sol', 'xhigh')}


class Refuse(Exception):
    pass


def command(tier, brief, backend):
    """(argv, model, effort) that starts solo at the tier."""
    if tier not in TIERS:
        raise Refuse(f'no solo tier {tier!r}: want S, M, or L')
    model, effort, level = TIERS[tier]
    if backend == 'codex':
        exe = os.environ.get('SOLO_CODEX_EXEC') or str(SCRIPTS / 'codex_exec.py')
        m, e = CODEX_MODELS[level]
        return [sys.executable, exe, 'solo', level, brief], m, e
    if backend != 'claude':
        raise Refuse('unknown backend: ' + backend)
    return ['claude', '-p', '--plugin-dir', str(PLUGIN), '--agent', 'sdlc-lite:solo', '--model', model,
            '--effort', effort, '--dangerously-skip-permissions', '--output-format', 'json', '--', brief], model, effort


def find_result(text):
    """The result event in a session's stdout: one JSON object, a JSON array of events, or JSON lines."""
    text = (text or '').strip()
    if not text:
        return None

    def pick(obj):
        if isinstance(obj, dict) and obj.get('type') == 'result':
            return obj
        if isinstance(obj, list):
            for ev in reversed(obj):
                got = pick(ev)
                if got is not None:
                    return got
        return None

    try:
        got = pick(json.loads(text))
        if got is not None:
            return got
    except ValueError:
        pass
    for line in reversed(text.splitlines()):
        try:
            got = pick(json.loads(line))
        except ValueError:
            continue
        if got is not None:
            return got
    return None


def number(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None


def build_record(tier, backend, model, effort, result, attempt, started, rc, reason=None):
    """One runs.jsonl line. cost_usd is the result's total_cost_usd, else null with cost_reason: never zero."""
    level = TIERS[tier][2]
    cost = number((result or {}).get('total_cost_usd'))
    cost_reason = None
    if cost is None:
        cost_reason = ('no result event' if result is None else
                       'codex reports no cost' if backend == 'codex' else 'result has no total_cost_usd')
    duration = number((result or {}).get('duration_ms'))
    if duration is None:
        duration = round((time.monotonic() - started) * 1000)
    rec = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'role': 'solo', 'level': level,
           'model': model, 'effort': effort, 'file': '', 'shared_with_builder': False, 'attempt_id': attempt,
           'routing_reason': reason or os.environ.get('SDLC_ROUTING_REASON') or f'solo lane, tier {tier}',
           'backend': backend, 'transport': 'exec' if backend == 'codex' else 'claude',
           'usage': (result or {}).get('usage'), 'cost_usd': cost, 'duration_ms': duration,
           'turns': number((result or {}).get('num_turns')), 'exit_code': rc,
           'stray_worktrees': [], 'stray_branches': []}
    if cost_reason:
        rec['cost_reason'] = cost_reason
    return rec


def append(task_dir, rec):
    task_dir = pathlib.Path(task_dir)
    if not (task_dir / 'handoff.md').is_file():
        raise Refuse(f'{task_dir}: no handoff.md; --task-dir is the ticket or task folder')
    with (task_dir / 'runs.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(rec, separators=(',', ':')) + '\n')


def run(task_dir, tier, brief, backend='claude', cwd=None, timeout=None, raw_out=None):
    argv, model, effort = command(tier, brief, backend)
    if not (pathlib.Path(task_dir) / 'handoff.md').is_file():
        raise Refuse(f'{task_dir}: no handoff.md; --task-dir is the ticket or task folder')
    attempt = os.environ.get('SDLC_ATTEMPT_ID') or uuid.uuid4().hex
    env = dict(os.environ, SDLC_ROLE='solo', SDLC_ATTEMPT_ID=attempt)
    started = time.monotonic()
    try:
        p = subprocess.run(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           text=True, timeout=timeout)
        out, rc = p.stdout, p.returncode
    except FileNotFoundError as exc:
        out, rc = '', 127
        print(f'solo_run.py: {exc}', file=sys.stderr)
    except subprocess.TimeoutExpired as exc:
        out, rc = (exc.stdout.decode() if isinstance(exc.stdout, bytes) else exc.stdout) or '', 124
        print(f'solo_run.py: timed out after {timeout}s', file=sys.stderr)
    if raw_out:
        pathlib.Path(raw_out).write_text(out or '', encoding='utf-8')
    result = find_result(out)
    rec = build_record(tier, backend, model, effort, result, attempt, started, rc)
    append(task_dir, rec)
    text = (result or {}).get('result')
    if isinstance(text, str) and text:
        print(text)
    elif out and result is None:
        print(out, end='')
    cost = rec['cost_usd']
    print('solo_run.py: recorded solo %s attempt %s cost %s' % (
        rec['level'], attempt[:8], f'${cost:.4f}' if cost is not None else f"none ({rec['cost_reason']})"),
        file=sys.stderr)
    return 1 if rc == 0 and (result or {}).get('is_error') else rc


def selftest():
    sys.path.insert(0, str(SCRIPTS))
    import budget
    fails = []

    def q(*a, **k):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return run(*a, **k)

    def expect(name, ok):
        if not ok:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        bin_dir = tmp / 'bin'
        bin_dir.mkdir()

        def shim(body):
            f = bin_dir / 'claude'
            f.write_text('#!/bin/sh\n' + body)
            f.chmod(0o755)

        def ticket(name, budget_usd=None):
            d = tmp / name
            d.mkdir()
            fm = f'---\nid: T-0001\ntitle: t\ntype: chore\nstatus: ready\nsize: M\n'
            if budget_usd is not None:
                fm += f'budget_usd: {budget_usd}\n'
            (d / 'handoff.md').write_text(fm + '---\n\n## Goal\ng\n')
            return d

        def lines(d):
            f = d / 'runs.jsonl'
            return [json.loads(x) for x in f.read_text().splitlines()] if f.is_file() else []

        old_path = os.environ['PATH']
        os.environ['PATH'] = f'{bin_dir}{os.pathsep}{old_path}'
        try:
            usage = '{"input_tokens":10,"output_tokens":20,"cache_read_input_tokens":300}'
            ok_json = ('{"type":"result","subtype":"success","is_error":false,"result":"done report",'
                       '"total_cost_usd":3.25,"duration_ms":4321,"num_turns":7,"usage":' + usage + '}')
            shim(f"printf '%s' '{ok_json}'\n")
            d = ticket('a')
            rc = q(d, 'M', 'the brief', cwd=str(tmp))
            r = lines(d)
            expect('one record', len(r) == 1)
            rec = r[0] if r else {}
            expect('record role and level', rec.get('role') == 'solo' and rec.get('level') == 'L2')
            expect('record model and effort', rec.get('model') == 'sonnet' and rec.get('effort') == 'xhigh')
            expect('cost matches the result event', rec.get('cost_usd') == 3.25)
            expect('usage, turns, duration copied', rec.get('usage', {}).get('output_tokens') == 20
                   and rec.get('turns') == 7 and rec.get('duration_ms') == 4321)
            expect('attempt id set', isinstance(rec.get('attempt_id'), str) and len(rec['attempt_id']) >= 8)
            expect('exit status 0', rc == 0)
            s, un = budget.spend(d)
            expect('budget counts the solo cost', abs(s - 3.25) < 1e-9 and un == 0)

            shim(f"printf '%s\\n' '[{{\"type\":\"system\"}},{ok_json}]'\n")
            d = ticket('arr')
            q(d, 'S', 'b')
            expect('array output parsed', lines(d)[0].get('cost_usd') == 3.25 and lines(d)[0].get('level') == 'L1')

            # Negative control: no usage in the result records cost null with a reason, never zero.
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\"}'\n")
            d = ticket('nousage')
            q(d, 'M', 'b')
            rec = lines(d)[0]
            expect('no usage: cost null, not zero', rec.get('cost_usd') is None and 'cost_reason' in rec)
            s, un = budget.spend(d)
            expect('no usage: budget reports unmetered', s == 0 and un == 1)

            shim('exit 3\n')
            d = ticket('crash')
            rc = q(d, 'M', 'b')
            rec = (lines(d) or [{}])[0]
            expect('crash: record written with null cost', rec.get('cost_usd') is None
                   and rec.get('cost_reason') == 'no result event' and rec.get('exit_code') == 3 and rc == 3)

            shim("printf '%s' '{\"type\":\"result\",\"is_error\":true,\"result\":\"e\",\"total_cost_usd\":1}'\n")
            d = ticket('err')
            expect('is_error result exits 1', q(d, 'M', 'b') == 1 and lines(d)[0].get('cost_usd') == 1)

            # A ticket over 80 percent through solo cost alone trips the budget stop.
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\",\"total_cost_usd\":8.5}'\n")
            d = ticket('over', budget_usd=10)
            q(d, 'M', 'b')
            rep = budget.report(d)
            expect('over 80 percent via solo cost warns', rep is not None and rep['state'] == 'warn' and rep['percent'] == 85)
            q(d, 'M', 'b')
            rep = budget.report(d)
            expect('two solo runs exceed the ceiling', rep is not None and rep['state'] == 'over')

            # Codex: codex_exec.py reports no cost; the record says so. A stub stands in for it.
            stub = tmp / 'codex_stub.py'
            stub.write_text('import json\nprint(json.dumps({"type":"codex_event","event":{}}))\n'
                            'print(json.dumps({"type":"result","backend":"codex","is_error":False,"result":"cx",'
                            '"total_cost_usd":None,"duration_ms":5,"num_turns":2,"usage":{"input_tokens":9}}))\n')
            os.environ['SOLO_CODEX_EXEC'] = str(stub)
            d = ticket('codex')
            q(d, 'L', 'b', backend='codex')
            rec = lines(d)[0]
            expect('codex: level L3, null cost with reason', rec.get('level') == 'L3' and rec.get('cost_usd') is None
                   and rec.get('cost_reason') == 'codex reports no cost' and rec.get('turns') == 2
                   and rec.get('model') == 'gpt-6.1-sol' and rec.get('effort') == 'xhigh')
            del os.environ['SOLO_CODEX_EXEC']

            # Refusals write nothing.
            d = ticket('refuse')
            for name, fn in (('bad tier', lambda: q(d, 'XL', 'b')), ('bad backend', lambda: q(d, 'M', 'b', backend='x')),
                             ('no handoff', lambda: q(tmp / 'nowhere', 'M', 'b'))):
                try:
                    fn()
                    expect(name + ' refused', False)
                except Refuse:
                    expect(name + ' refused', True)
            expect('refusals wrote no record', not (d / 'runs.jsonl').exists())

            # Two runs get two attempt ids.
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\",\"total_cost_usd\":1}'\n")
            d = ticket('two')
            q(d, 'M', 'b')
            q(d, 'M', 'b')
            ids = [x['attempt_id'] for x in lines(d)]
            expect('distinct attempt ids, both counted', len(set(ids)) == 2 and abs(budget.spend(d)[0] - 2) < 1e-9)

            # find_result shapes.
            expect('find_result: none on empty', find_result('') is None and find_result('not json') is None)
            expect('find_result: json lines', (find_result('{"type":"x"}\n{"type":"result","total_cost_usd":2}\n') or {}).get('total_cost_usd') == 2)
        finally:
            os.environ['PATH'] = old_path
    if fails:
        for f in fails:
            print('solo_run selftest FAIL: ' + f)
        return 1
    print('solo_run selftest: PASS')
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--task-dir', required=True)
    r.add_argument('--tier', required=True, choices=sorted(TIERS))
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument('--brief')
    g.add_argument('--brief-file')
    r.add_argument('--backend', default=os.environ.get('SDLC_BACKEND', 'claude'))
    r.add_argument('--cwd')
    r.add_argument('--timeout', type=float)
    r.add_argument('--raw-out', help='also save the session stdout (the result JSON) to this file')
    sub.add_parser('selftest')
    a = p.parse_args()
    if a.cmd == 'selftest':
        return selftest()
    brief = a.brief
    if a.brief_file:
        brief = sys.stdin.read() if a.brief_file == '-' else pathlib.Path(a.brief_file).read_text(encoding='utf-8')
    if brief == '-':
        brief = sys.stdin.read()
    if not brief or not brief.strip():
        print('solo_run.py: empty brief', file=sys.stderr)
        return 2
    try:
        return run(a.task_dir, a.tier, brief, a.backend, a.cwd, a.timeout, a.raw_out)
    except Refuse as exc:
        print(f'solo_run.py: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
