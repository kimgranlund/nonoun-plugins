#!/usr/bin/env python3
"""Start the solo agent for one ticket and record its cost, so the default lane is metered.

  solo_run.py run (--task-dir DIR | --new-task [SLUG]) --tier S|M|L (--brief TEXT | --brief-file FILE | --brief -)
                  [--backend claude|codex] [--cwd DIR] [--timeout SECONDS] [--raw-out FILE]
  solo_run.py selftest

run starts the session at the tier's model and effort (agents/solo.md), prints the agent's report on
stdout, and appends one line to <task-dir>/runs.jsonl in the record shape run.sh writes for roles
(ts, role solo, level L1..L3 for tier S..L, model, effort, cost_usd, usage, duration_ms, turns, attempt_id,
backend, transport, routing_reason). --task-dir is the ticket or task folder, the one holding handoff.md.
budget.py sums cost_usd over every runs.jsonl under the ticket and counts a record with no numeric cost
as unmetered, so this record is all the budget gate and the board need.

Budget gate (T-0229): before it starts anything, run checks the ticket's budget the way run.sh does for roles.
A ticket at 80 percent of its budget or more with no ack prints `solo_run.py: budget <pct>%: ask the user;
budget.py ack` on stderr and exits 4 with no session, no record; `budget.py ack` raises the ceiling and the next
start goes. A ticket with no budget (or a task folder with no ticket id) is never blocked. fanout.py starts its solo
lanes through this wrapper, so the gate covers them too.

--new-task [SLUG] is for a solo run that names no ticket (`/agent solo <instructions>`): it creates
<ticket root>/<SLUG>/handoff.md from the brief (SLUG defaults to solo-YYYYMMDD-HHMMSS; refused when the folder
exists), then runs there, so the session's cost is recorded like any other. A task folder without an `id` is not
a ticket and has no budget.

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
import re
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
           'routing_reason': reason or f'solo lane, tier {tier}',
           'backend': backend, 'transport': 'exec' if backend == 'codex' else 'claude',
           'usage': (result or {}).get('usage'), 'cost_usd': cost, 'duration_ms': duration,
           'turns': number((result or {}).get('num_turns')), 'exit_code': rc,
           'stray_worktrees': [], 'stray_branches': []}
    if cost_reason:
        rec['cost_reason'] = cost_reason
    return rec


LIMIT_RE = re.compile(r'429|session limit|usage limit|hit your (session |usage )?limit|rate.?limit', re.I)


def limit_hint(task_dir, tier, text):
    """On a 429 or session-limit stop, write <task dir>/solo.limit (one JSON line) and print the resume hint."""
    m = LIMIT_RE.search(text or '')
    if not m:
        return
    resume = f'python3 {pathlib.Path(__file__).resolve()} run --task-dir {task_dir} --tier {tier} --brief <the same brief>'
    rec = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'task_dir': str(task_dir), 'tier': tier,
           'resume': resume, 'evidence': (text or '')[max(0, m.start() - 40):m.end() + 80].strip()[:200]}
    try:
        (pathlib.Path(task_dir) / 'solo.limit').write_text(json.dumps(rec, separators=(',', ':')) + '\n', encoding='utf-8')
    except OSError:
        pass
    print('solo_run.py: session limit: the work is in the tree (fanout keeps it in the lane WIP commit); '
          f'resume after the limit resets: {resume}', file=sys.stderr)


def budget_hold(task_dir):
    """The budget report when the ticket holding task_dir is at 80 percent or more with no ack, else None."""
    sys.path.insert(0, str(SCRIPTS))
    import budget
    ticket = budget.ticket_of(task_dir)
    rep = budget.report(ticket) if ticket is not None else None
    return rep if rep and rep['state'] != 'ok' else None


def new_task(slug, brief, root='.sdlc'):
    """Create <ticket root>/<slug>/handoff.md from the brief and return the folder (a task, not a ticket)."""
    sys.path.insert(0, str(SCRIPTS))
    import re
    import tickets
    slug = slug or time.strftime('solo-%Y%m%d-%H%M%S')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug):
        raise Refuse(f'bad task slug {slug!r}: lowercase letters, digits and single hyphens')
    try:
        base = tickets.ticket_dir(pathlib.Path(root))
    except tickets.Fail as exc:
        raise Refuse(str(exc))
    d = base / slug
    if d.exists():
        raise Refuse(f'{d}: already exists; pick another slug')
    d.mkdir(parents=True)
    first = next((ln.strip() for ln in brief.splitlines() if ln.strip()), 'solo task')[:100]
    (d / 'handoff.md').write_text(f'## Goal\n{first}\n\n## Brief\n{brief.strip()}\n', encoding='utf-8')
    return d


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
    hold = budget_hold(task_dir)
    if hold:
        print(f"solo_run.py: budget {hold['percent']}%: ask the user; budget.py ack", file=sys.stderr)
        return 4
    # Always mint a fresh id: an inherited SDLC_ATTEMPT_ID belongs to a role attempt (fanout.py does the same), and
    # budget.py skips a second record with a repeated attempt_id, so reusing it would undercount spend.
    attempt = uuid.uuid4().hex
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
    failed = 1 if rc == 0 and (result or {}).get('is_error') else rc
    if failed:
        limit_hint(task_dir, tier, text if isinstance(text, str) and text else out)
    else:
        (pathlib.Path(task_dir) / 'solo.limit').unlink(missing_ok=True)
    return failed


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
        old_env = {k: os.environ.get(k) for k in ('SDLC_ATTEMPT_ID', 'SDLC_ROUTING_REASON')}
        os.environ['SDLC_ATTEMPT_ID'] = 'inherited-role-attempt'
        os.environ['SDLC_ROUTING_REASON'] = 'a role routing reason'
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
            expect('a plain failure leaves no resume marker (T-0260 control)', not (d / 'solo.limit').exists())

            # T-0260: a 429 session-limit stop leaves solo.limit and prints the resume hint.
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":true,\"result\":\"API Error: 429 session limit reached\"}'\n")
            d = ticket('limit')
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = run(d, 'M', 'b')
            mk = d / 'solo.limit'
            got = json.loads(mk.read_text()) if mk.is_file() else {}
            expect('limit stop: exits 1, solo.limit has the resume command and evidence',
                   rc == 1 and '--task-dir' in got.get('resume', '') and '429' in got.get('evidence', ''))
            expect('limit stop: stderr prints the resume hint', 'session limit' in err.getvalue() and 'resume' in err.getvalue())

            # A ticket over 80 percent through solo cost alone trips the budget stop.
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\",\"total_cost_usd\":8.5}'\n")
            d = ticket('over', budget_usd=10)
            q(d, 'M', 'b')
            rep = budget.report(d)
            expect('over 80 percent via solo cost warns', rep is not None and rep['state'] == 'warn' and rep['percent'] == 85)
            expect('a second solo start at 85 percent is refused by the gate (T-0229)', q(d, 'M', 'b') == 4)
            rep = budget.report(d)
            expect('the refused start added no spend', rep is not None and rep['state'] == 'warn' and rep['percent'] == 85)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                budget.cmd_ack(str(d), 20, 'selftest')
            q(d, 'M', 'b')
            rep = budget.report(d)
            expect('an acked ticket keeps metering', rep is not None and rep['percent'] == 85 and rep['budget'] == 20 and rep['state'] == 'warn')

            # Budget gate (T-0229): a ticket at 80 percent or more with no ack does not start a session.
            mark = tmp / 'started.txt'
            os.environ['SOLO_MARK'] = str(mark)
            shim("touch \"$SOLO_MARK\"\nprintf '%s' '{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\",\"total_cost_usd\":1}'\n")

            def seed(d, usd):
                (d / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'attempt_id': 'seed' + str(usd),
                                                          'cost_usd': usd}) + '\n')

            d = ticket('gate', budget_usd=10)
            seed(d, 8.0)  # exactly 80 percent
            rc = q(d, 'M', 'b')
            expect('gate: 80 percent with no ack exits 4', rc == 4)
            expect('gate: no session started at 80 percent', not mark.exists())
            expect('gate: no record written when refused', len(lines(d)) == 1)
            d79 = ticket('gate79', budget_usd=10)
            seed(d79, 7.9)
            expect('gate: 79 percent starts (boundary control)', q(d79, 'M', 'b') == 0 and mark.exists() and len(lines(d79)) == 2)
            mark.unlink()
            dov = ticket('gateover', budget_usd=10)
            seed(dov, 12.0)
            expect('gate: over budget exits 4', q(dov, 'M', 'b') == 4 and not mark.exists())
            # Ack raises the ceiling: the same ticket then starts.
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc_ack = budget.cmd_ack(str(d), 20, 'selftest')
            expect('gate: ack accepted', rc_ack == 0)
            expect('gate: acked ticket starts and records', q(d, 'M', 'b') == 0 and mark.exists() and len(lines(d)) == 2)
            mark.unlink()
            # No budget field, or a task folder with no ticket id, is never blocked.
            dn = ticket('gatenone')
            seed(dn, 999.0)
            expect('gate: a ticket with no budget starts', q(dn, 'M', 'b') == 0 and mark.exists())
            mark.unlink()
            dt = tmp / 'plain-task'
            dt.mkdir()
            (dt / 'handoff.md').write_text('## Goal\ng\n')
            expect('gate: a task folder without a ticket id starts', q(dt, 'S', 'b') == 0 and mark.exists())
            mark.unlink()
            # The gate runs before the brief reaches the model: stderr says to ack.
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                run(dov, 'M', 'b')
            expect('gate: message names budget.py ack', 'budget.py ack' in err.getvalue() and 'budget 120%' in err.getvalue())

            # --new-task: /agent solo with no ticket still leaves a `role solo` record.
            root = tmp / 'proj' / '.sdlc'
            root.mkdir(parents=True)
            td = new_task('quick-fix', 'Fix the typo\nin README', root=str(root))
            expect('new task: folder and handoff written', (td / 'handoff.md').is_file()
                   and '## Goal\nFix the typo' in (td / 'handoff.md').read_text())
            expect('new task: runs and records a solo run', q(td, 'S', 'Fix the typo') == 0
                   and [x.get('role') for x in lines(td)] == ['solo'])
            for name, fn in (('existing slug', lambda: new_task('quick-fix', 'x', root=str(root))),
                             ('bad slug', lambda: new_task('Bad Slug', 'x', root=str(root)))):
                try:
                    fn()
                    expect('new task: ' + name + ' refused', False)
                except Refuse:
                    expect('new task: ' + name + ' refused', True)
            (root / 'config').write_text('ticket_root: tickets\n')
            td2 = new_task('', 'In the ticket root', root=str(root))
            expect('new task: default slug under ticket_root', td2.parent == root / 'tickets' and td2.name.startswith('solo-'))
            # The CLI path end to end: no ticket, a shim claude, cwd is the project.
            pr = tmp / 'cliproj'
            (pr / '.sdlc').mkdir(parents=True)
            cp = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', '--new-task', 'cli-task',
                                 '--tier', 'S', '--brief', 'cli brief'], cwd=str(pr), capture_output=True, text=True,
                                env=dict(os.environ), timeout=60)
            recs = [json.loads(x) for x in (pr / '.sdlc' / 'cli-task' / 'runs.jsonl').read_text().splitlines()] \
                if (pr / '.sdlc' / 'cli-task' / 'runs.jsonl').is_file() else []
            expect(f'new task CLI: rc 0 and one solo record, got rc={cp.returncode} err={cp.stderr[-200:]!r}',
                   cp.returncode == 0 and [x.get('role') for x in recs] == ['solo'])
            cp = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', '--tier', 'S',
                                 '--brief', 'x'], cwd=str(pr), capture_output=True, text=True, timeout=60)
            expect('CLI: neither --task-dir nor --new-task exits 2', cp.returncode == 2)
            os.environ.pop('SOLO_MARK', None)

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
            expect('inherited SDLC_ATTEMPT_ID is not reused', 'inherited-role-attempt' not in ids)
            expect('inherited SDLC_ROUTING_REASON is not copied', all(x.get('routing_reason') == 'solo lane, tier M' for x in lines(d)))

            # find_result shapes.
            expect('find_result: none on empty', find_result('') is None and find_result('not json') is None)
            expect('find_result: json lines', (find_result('{"type":"x"}\n{"type":"result","total_cost_usd":2}\n') or {}).get('total_cost_usd') == 2)
        finally:
            os.environ['PATH'] = old_path
            for k, v in old_env.items():
                if v is None: os.environ.pop(k, None)
                else: os.environ[k] = v
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
    r.add_argument('--task-dir', help='the ticket or task folder holding handoff.md')
    r.add_argument('--new-task', nargs='?', const='', metavar='SLUG', help='no ticket: create '
                   '<ticket root>/<SLUG>/handoff.md from the brief and run there (default slug solo-<timestamp>)')
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
    if bool(a.task_dir) == (a.new_task is not None):
        print('solo_run.py: give exactly one of --task-dir or --new-task', file=sys.stderr)
        return 2
    try:
        task_dir = a.task_dir if a.task_dir else new_task(a.new_task, brief)
        if a.new_task is not None:
            print(f'solo_run.py: task folder {task_dir}', file=sys.stderr)
        return run(task_dir, a.tier, brief, a.backend, a.cwd, a.timeout, a.raw_out)
    except Refuse as exc:
        print(f'solo_run.py: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
