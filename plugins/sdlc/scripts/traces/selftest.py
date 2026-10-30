"""Named selftest cases for traces.py, grouped by family (the text before the first colon).

run(family=None) runs every case (or one family's), prints "ok: <name>" or "skip: <name>: <why>"
per case, then "traces selftest: PASS" (exit 0), or the misses and "traces selftest: FAIL" on
stderr (exit 1). No matching case: "traces selftest: no selftest case matches <family>" (exit 1).
Each case builds its fixtures in a tempfile dir and never writes into the repo.
"""
import contextlib, json, os, sys, tempfile

from . import table

CASES = []


class Skip(Exception):
    """Raised by a case that cannot run on this host; the message says why."""


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def family_of(name):
    return name.split(':', 1)[0].strip()


def run(family=None):
    chosen = [(n, fn) for n, fn in CASES if family is None or family_of(n) == family]
    if not chosen:
        print(f'traces selftest: no selftest case matches {family}', file=sys.stderr)
        return 1
    misses = []
    for name, fn in chosen:
        try:
            fn()
        except Skip as e:
            print(f'skip: {name}: {e}')
            continue
        except AssertionError as e:
            misses.append(f'{name}: {e}' if str(e) else name)
            continue
        except Exception as e:  # a crashing case is a miss, not a traceback
            misses.append(f'{name}: {type(e).__name__}: {e}')
            continue
        print(f'ok: {name}')
    if misses:
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        print('traces selftest: FAIL', file=sys.stderr)
        return 1
    print('traces selftest: PASS')
    return 0


# --- fixtures ---------------------------------------------------------------------------------

def _write(repo, rel, text):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)


def _fixture(repo, dir_rel, attempts=(), runs=(), results=()):
    """Write one handoff dir under repo and read it back as the plain records join() takes.
    The read-back here is fixture plumbing only; the real readers come in later steps."""
    for a in attempts:
        _write(repo, f'{dir_rel}/{a["name"]}.attempt.json', json.dumps(a))
    if runs:
        _write(repo, f'{dir_rel}/runs.jsonl', ''.join(json.dumps(r) + '\n' for r in runs))
    for r in results:
        _write(repo, f'{dir_rel}/{r["name"]}.md', f'## Status\n{r.get("status") or "done"}\n')
    base = os.path.join(repo, dir_rel)
    att, rec = [], []
    for n in sorted(os.listdir(base)):
        if n.endswith('.attempt.json'):
            with open(os.path.join(base, n), encoding='utf-8') as f:
                d = json.load(f)
            d['path'] = f'{dir_rel}/{n}'
            att.append(d)
    if os.path.exists(os.path.join(base, 'runs.jsonl')):
        with open(os.path.join(base, 'runs.jsonl'), encoding='utf-8') as f:
            for i, line in enumerate(f.read().splitlines()):
                d = json.loads(line)
                d.update(index=i, path=f'{dir_rel}/runs.jsonl')
                rec.append(d)
    res = [dict(r, path=f'{dir_rel}/{r["name"]}.md') for r in results]
    return att, rec, res


def _attempt(name, aid, **kw):
    role, level, _ = table.name_parts(name)
    d = {'attempt_id': aid, 'name': name, 'role': role, 'level': level, 'status': 'completed',
         'exit_code': 0, 'started_at': '2026-09-30T06:00:00+00:00',
         'finished_at': '2026-09-30T06:01:30+00:00'}
    d.update(kw)
    return d


def _by_id(rows):
    return {r['attempt_id']: r for r in rows}


# --- join ---------------------------------------------------------------------------------------

@case('join: an attempt joins its run record by attempt_id')
def _join_by_id():
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t1/step-1'
        att, runs, res = _fixture(
            repo, d,
            attempts=[_attempt('builder-L2', 'a1'), _attempt('verifier-L1', 'a2')],
            runs=[{'role': 'verifier', 'level': 'L1', 'file': 'builder-L2.md', 'attempt_id': 'a2',
                   'turns': 5, 'cost_usd': 0.5, 'duration_ms': 2500},
                  {'role': 'builder', 'level': 'L2', 'file': 'builder-L2.md', 'attempt_id': 'a1',
                   'turns': 12, 'cost_usd': 1.25, 'duration_ms': 42000}],
            results=[{'name': 'builder-L2', 'status': 'done', 'verdict': None, 'plan_defect': False}])
        rows = table.join(d, att, runs, res, ticket='0007')
        assert len(rows) == 2, f'want 2 rows, got {len(rows)}'
        r = _by_id(rows)
        b, v = r['a1'], r['a2']
        # a1 joins by attempt_id even though a2's record names the same file
        assert (b['turns'], b['cost_usd'], b['secs']) == (12, 1.25, 42.0), b
        assert (v['turns'], v['cost_usd'], v['secs']) == (5, 0.5, 2.5), v
        assert b['status'] == 'completed' and b['exit_code'] == 0, b
        assert b['ticket'] == '0007' and b['task_dir'] == '.sdlc/t1', b
        assert b['sources'] == [f'{d}/builder-L2.attempt.json', f'{d}/runs.jsonl',
                                f'{d}/builder-L2.md'], b['sources']
        assert v['sources'] == [f'{d}/verifier-L1.attempt.json', f'{d}/runs.jsonl'], v['sources']
        # no run record: secs falls back to finished_at minus started_at
        rows = table.join(d, att, [], res)
        assert _by_id(rows)['a1']['secs'] == 90.0, _by_id(rows)['a1']['secs']
        assert _by_id(rows)['a1']['turns'] is None


@case('join: a legacy record joins by result name in the same dir')
def _join_legacy_by_name():
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t2/step-2'
        att, runs, res = _fixture(
            repo, d,
            attempts=[_attempt('builder-L3', 'b1')],
            runs=[{'role': 'builder', 'level': 'L3', 'file': 'builder-L3.md', 'turns': 7,
                   'cost_usd': 2.0, 'duration_ms': 1000}],
            results=[{'name': 'builder-L3', 'status': 'done', 'verdict': None, 'plan_defect': False},
                     {'name': 'verifier-L2', 'status': None, 'verdict': 'pass', 'plan_defect': False}])
        rows = table.join(d, att, runs, res)
        assert [r['attempt_id'] for r in rows] == ['b1'], [r['attempt_id'] for r in rows]
        b = rows[0]
        assert (b['turns'], b['cost_usd'], b['secs']) == (7, 2.0, 1.0), b
        assert f'{d}/builder-L3.md' in b['sources'], b['sources']
        # a legacy run record (no attempt_id, no attempt file) joins its result by name
        att2, runs2, res2 = _fixture(
            repo, '.sdlc/t2/step-3',
            runs=[{'role': 'verifier', 'level': 'L2', 'file': 'verifier-L2.md', 'turns': 3,
                   'cost_usd': 0.1, 'duration_ms': 500}],
            results=[{'name': 'verifier-L2', 'status': None, 'verdict': 'fail', 'plan_defect': True}])
        rows = table.join('.sdlc/t2/step-3', att2, runs2, res2)
        assert len(rows) == 1, rows
        v = rows[0]
        assert v['attempt_id'] == 'legacy:.sdlc/t2/step-3/verifier-L2.md', v['attempt_id']
        assert (v['verdict'], v['plan_defect']) == ('fail', True), v
        assert (v['status'], v['exit_code']) == ('completed', None), v
        assert (v['role'], v['level'], v['attempt_k']) == ('verifier', 'L2', 1), v
        assert v['sources'] == ['.sdlc/t2/step-3/runs.jsonl', '.sdlc/t2/step-3/verifier-L2.md'], \
            v['sources']


@case('join: an orphan record gets legacy:<relpath>')
def _join_orphan():
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t3'
        att, runs, res = _fixture(
            repo, d,
            attempts=[_attempt('planner-L2', 'p1')],
            runs=[{'role': 'scout', 'level': 'L1', 'turns': 2, 'cost_usd': 0.01},
                  {'role': 'planner', 'level': 'L2', 'file': 'planner-L2.md', 'attempt_id': 'p1'},
                  {'role': 'architect', 'level': 'L1', 'file': 'architect-L1-2.md'},
                  {'role': 'planner', 'level': 'L2', 'attempt_id': 'gone', 'file': 'planner-L2.md'}])
        rows = table.join(d, att, runs, res)
        ids = [r['attempt_id'] for r in rows]
        want = ['p1', 'legacy:.sdlc/t3/runs.jsonl#0', 'legacy:.sdlc/t3/architect-L1-2.md',
                'legacy:.sdlc/t3/planner-L2.md']
        assert ids == want, ids
        for r in rows[1:]:
            assert (r['status'], r['exit_code']) == ('completed', None), r
        s = rows[1]
        assert (s['role'], s['level'], s['turns'], s['secs']) == ('scout', 'L1', 2, None), s
        assert s['sources'] == ['.sdlc/t3/runs.jsonl'], s['sources']
        assert rows[2]['attempt_k'] == 2, rows[2]


@case('join: every row has every field of ROW_FIELDS')
def _join_fields():
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t4/step-1'
        att, runs, res = _fixture(
            repo, d,
            attempts=[_attempt('builder-L1', 'c1'), {'attempt_id': 'c2', 'name': 'odd'}],
            runs=[{'role': 'builder', 'level': 'L1', 'attempt_id': 'c1', 'tool_calls': 9},
                  {'foo': 1}])
        rows = table.join(d, att, runs, res)
        assert len(rows) == 3, rows
        for r in rows:
            assert list(r) == list(table.ROW_FIELDS), list(r)
        by = _by_id(rows)
        assert by['c1']['tool_calls'] == 9 and by['c1']['denials'] is None, by['c1']
        odd = by['c2']
        assert (odd['role'], odd['level'], odd['attempt_k'], odd['secs']) == (None, None, None, None), odd
        assert (odd['verdict'], odd['plan_defect'], odd['turns']) == (None, None, None), odd
        assert table.join(d, [], [], []) == []


@case('join: step, superseded, and attempt_k come from names')
def _join_names():
    with tempfile.TemporaryDirectory() as repo:
        cases = [('.sdlc/t5/step-12', 12, False, '.sdlc/t5'),
                 ('.sdlc/t5/step-3.superseded-2', 3, True, '.sdlc/t5'),
                 ('.sdlc/t5', None, False, '.sdlc/t5')]
        for d, step, sup, task in cases:
            att, runs, res = _fixture(repo, d, attempts=[_attempt('builder-L4-3', 'x-' + d),
                                                         _attempt('verifier-L2', 'y-' + d)])
            rows = table.join(d, att, runs, res)
            for r in rows:
                assert (r['step'], r['superseded'], r['task_dir']) == (step, sup, task), (d, r)
            k = {r['attempt_id'][0]: r['attempt_k'] for r in rows}
            assert k == {'x': 3, 'y': 1}, (d, k)
        assert table.dir_parts('step-7') == ('.', 7, False)
        assert table.dir_parts('.sdlc/t/step-7x') == ('.sdlc/t/step-7x', None, False)


# --- attempts -----------------------------------------------------------------------------------

def _attempts_fixture(repo, d):
    from .sources import attempts
    recs = [_attempt('builder-L1', 'k1'),
            _attempt('builder-L2', 'k2', status='failed', exit_code=1),
            _attempt('builder-L3', 'k3', status='interrupted', exit_code=130),
            _attempt('verifier-L1', 'k4', status='running', exit_code=None, finished_at=None)]
    for a in recs:
        _write(repo, f'{d}/{a["name"]}.attempt.json', json.dumps(a))
    _write(repo, f'{d}/verifier-L1.running', '')
    _write(repo, f'{d}/bad.attempt.json', '[1, 2]')
    _write(repo, f'{d}/broken.attempt.json', '{not json')
    return attempts.read(os.path.join(repo, d))


@case('attempts: one record per attempt file with its status and exit code')
def _attempts_status():
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t6/step-1'
        recs, problems = _attempts_fixture(repo, d)
        got = [(r['name'], r['status'], r['exit_code']) for r in recs]
        want = [('builder-L1', 'completed', 0), ('builder-L2', 'failed', 1),
                ('builder-L3', 'interrupted', 130), ('verifier-L1', 'running', None)]
        assert got == want, got
        base = os.path.join(repo, d)
        assert [r['path'] for r in recs] == [os.path.join(base, f'{n}.attempt.json')
                                             for n, _, _ in want], [r['path'] for r in recs]
        assert problems == [os.path.join(base, 'bad.attempt.json'),
                            os.path.join(base, 'broken.attempt.json')], problems


@case('attempts: a record with no run row still joins with an empty run list')
def _attempts_join():
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t6/step-2'
        recs, _ = _attempts_fixture(repo, d)
        rows = table.join(d, recs, [], [])
        assert [r['attempt_id'] for r in rows] == ['k1', 'k2', 'k3', 'k4'], rows
        by = _by_id(rows)
        assert (by['k4']['status'], by['k4']['exit_code'], by['k4']['turns']) == \
            ('running', None, None), by['k4']
        assert (by['k2']['status'], by['k2']['exit_code']) == ('failed', 1), by['k2']


@case('attempts: only the running record with a marker next to it reports marker True')
def _attempts_marker():
    with tempfile.TemporaryDirectory() as repo:
        recs, _ = _attempts_fixture(repo, '.sdlc/t6/step-3')
        got = {r['name']: r['marker'] for r in recs}
        assert got == {'builder-L1': False, 'builder-L2': False, 'builder-L3': False,
                       'verifier-L1': True}, got


# --- runs ---------------------------------------------------------------------------------------

@case('runs: legacy and full rows read with defaults; a malformed line is skipped')
def _runs_read():
    from .sources import runs
    with tempfile.TemporaryDirectory() as repo:
        d = '.sdlc/t7/step-1'
        legacy = {'role': 'scout', 'level': 'L1', 'turns': 2, 'cost_usd': 0.01}
        full = {'ts': '2026-09-30T06:00:00+00:00', 'role': 'builder', 'level': 'L2',
                'model': 'm', 'effort': 'low', 'file': 'builder-L2.md', 'attempt_id': 'r1',
                'backend': 'claude', 'cost_usd': 1.5, 'cost_estimated': True, 'duration_ms': 900, 'turns': 4,
                'stray_worktrees': ['w'], 'stray_branches': ['b'], 'routing_reason': 'why',
                'loaded_context': {'paths': ['/p'], 'source': 'stream-json'}, 'extra': 1}
        _write(repo, f'{d}/runs.jsonl',
               json.dumps(legacy) + '\n{not json\n' + json.dumps(full) + '\n')
        base = os.path.join(repo, d)
        recs, skipped = runs.read(base)
        assert skipped == 1, skipped
        assert len(recs) == 2, recs
        a, b = recs
        path = os.path.join(base, 'runs.jsonl')
        assert (a['index'], a['path'], b['index'], b['path']) == (0, path, 2, path), recs
        assert (a['file'], a['attempt_id'], a['ts'], a['routing_reason'], a['loaded_context']) == \
            (None, None, None, None, None), a
        assert (a['stray_worktrees'], a['stray_branches']) == ([], []), a
        assert (a['role'], a['turns']) == ('scout', 2), a
        want = dict(full, index=2, path=path)
        del want['extra']
        assert b == want, b
        assert set(a) == set(runs.FIELDS) | {'index', 'path'}, sorted(a)


@case('runs: a missing runs.jsonl reads as no records')
def _runs_missing():
    from .sources import runs
    with tempfile.TemporaryDirectory() as repo:
        assert runs.read(os.path.join(repo, 'nope')) == ([], 0)
        assert runs.read(repo) == ([], 0)


# --- results ------------------------------------------------------------------------------------

def _hd(name):
    return '#' * 2 + ' ' + name


_BUILDS = {'done': 'done', 'blocked': 'blocked', 'inherited red: x': 'inherited', None: None}
_VERDICTS = {'pass': 'pass', 'fail': 'fail', None: None}


def _builder_text(status):
    head = '<!-- role=builder level=L2 model=opus effort=high -->\n'
    body = f'{_hd("Status")}\n{status}\n\n' if status else 'no status here\n'
    return (head + body + f'{_hd("Changes")}\n- `a/b.py`: edit\n- `c.md` and `d.txt`\n\n'
            f'{_hd("Checks")}\nran\n\n{_hd("Notes")}\n\nfirst note\nsecond\n')


def _verifier_text(verdict, next_note='rebuild it'):
    body = f'{_hd("Verdict")}\n{verdict}\n\n' if verdict else 'no verdict\n'
    return body + f'{_hd("For the next attempt")}\n{next_note}\n'


@case('results: builder status, verifier verdict, and plan defect from steps.py helpers')
def _results_read():
    from .sources import results
    with tempfile.TemporaryDirectory() as repo:
        for i, (s, want) in enumerate(_BUILDS.items()):
            d = os.path.join(repo, f'b{i}')
            _write(d, 'builder-L2.md', _builder_text(s))
            recs, problems = results.read(d)
            assert problems == [] and len(recs) == 1, (recs, problems)
            r = recs[0]
            assert r['status'] == want and r['verdict'] is None, (s, r)
            assert (r['name'], r['role'], r['level']) == ('builder-L2', 'builder', 'L2'), r
            assert (r['model'], r['effort']) == ('opus', 'high'), r
            assert r['next_note'] == 'first note', r
            assert r['changes'] == ['a/b.py', 'c.md', 'd.txt'], r
            assert r['plan_defect'] is False and r['swap'] is False, r
        for i, (v, want) in enumerate(_VERDICTS.items()):
            d = os.path.join(repo, f'v{i}')
            _write(d, 'verifier-L1.md', _verifier_text(v))
            r = results.read(d)[0][0]
            assert r['verdict'] == want and r['status'] is None, (v, r)
            assert (r['model'], r['effort'], r['plan_defect']) == (None, None, False), r
            assert r['next_note'] == 'rebuild it', r
        d = os.path.join(repo, 'pd')
        _write(d, 'verifier-L1-2.md', _verifier_text(
            'fail', 'plan defect: x is wrong\nswap old: `a`\nswap new: b'))
        _write(d, 'notes.md', '')
        recs, _ = results.read(d)
        assert [r['name'] for r in recs] == ['verifier-L1-2'], recs
        r = recs[0]
        assert (r['plan_defect'], r['swap'], r['level']) == (True, True, 'L1'), r
        assert r['next_note'] == 'plan defect: x is wrong', r


_VERIFIER_HEAD = '<!-- role=verifier level=L1 model=sonnet effort=medium -->\n'


@case('results: on the same fixtures as step dirs, steps.next_action agrees')
def _results_next():
    import steps
    from .sources import results
    want_build = {'done': 'verify', 'blocked': 'replan', 'inherited red: x': 'inherited',
                  None: 'rebuild'}
    want_verify = {'pass': 'done', 'fail': 'rebuild', None: 'reverify'}
    with tempfile.TemporaryDirectory() as repo:
        for i, (s, act) in enumerate(want_build.items()):
            d = os.path.join(repo, f'step-{i}')
            _write(d, 'handoff.md', 'level: L2\n')
            _write(d, 'builder-L2.md', _builder_text(s))
            assert results.read(d)[0][0]['status'] == _BUILDS[s]
            got = steps.next_action(d)[0]
            assert got == act, (s, got)
        cases = [(v, _verifier_text(v), a, _VERDICTS[v], False) for v, a in want_verify.items()]
        cases.append(('pd', _verifier_text('fail', 'plan defect: bad'), 'replan', 'fail', True))
        for i, (tag, text, act, verdict, pd) in enumerate(cases):
            d = os.path.join(repo, f'step-v{i}')
            _write(d, 'handoff.md', 'level: L2\n')
            _write(d, 'builder-L2.md', _builder_text('done'))
            _write(d, 'verifier-L1.md', _VERIFIER_HEAD + text)
            v = [r for r in results.read(d)[0] if r['role'] == 'verifier'][0]
            assert (v['verdict'], v['plan_defect']) == (verdict, pd), (tag, v)
            got = steps.next_action(d)[0]
            assert got == act, (tag, got)
        d = os.path.join(repo, 'step-nohead')
        _write(d, 'handoff.md', 'level: L2\n')
        _write(d, 'builder-L2.md', _builder_text('done').split('\n', 1)[1])
        got = steps.next_action(d)[0]
        assert got == 'invalid result', got


# --- transcripts --------------------------------------------------------------------------------

def _transcript_log():
    ev = []
    for i in range(5):
        ev.append({'type': 'assistant', 'timestamp': f'2026-09-30T06:00:0{i}Z', 'message': {
            'content': [{'type': 'text', 'text': 'x'},
                        {'type': 'tool_use', 'name': 'Bash', 'input': {'command': f'echo {i}'}}]}})
    ev.append({'type': 'user', 'message': {'content': [
        {'type': 'tool_result', 'is_error': True}, {'type': 'tool_result', 'is_error': False}]}})
    ev.append({'type': 'system', 'subtype': 'hook_response', 'hook_name': 'PreToolUse:Bash',
               'exit_code': 2, 'stderr': 'blocked: run_in_background is not allowed'})
    ev.append({'type': 'system', 'subtype': 'hook_response', 'hook_name': 'ok', 'exit_code': 0})
    ev.append({'type': 'rate_limit_event'})
    ev.append({'type': 'result', 'total_cost_usd': 9.0, 'duration_ms': 1, 'num_turns': 1})
    ev.append({'type': 'result', 'total_cost_usd': 1.5, 'duration_ms': 4000, 'num_turns': 6})
    lines = [json.dumps(e) for e in ev]
    lines.insert(2, 'some prose the CLI printed')
    lines.insert(5, '[1, 2]')
    lines.append('{truncated')
    return '\n'.join(lines) + '\n'


@case('transcripts: tool calls, denials, rate limits, and result from a mixed log')
def _transcripts_read():
    from .sources import transcripts
    with tempfile.TemporaryDirectory() as repo:
        _write(repo, 'builder-L2.log', _transcript_log())
        r = transcripts.read(os.path.join(repo, 'builder-L2.log'))
        assert r['tool_calls'] == 5, r
        assert r['bash_calls'] == [(f'2026-09-30T06:00:0{i}Z', f'echo {i}') for i in range(5)], r
        assert r['tool_errors'] == 1, r
        assert len(r['denials']) == 1 and 'run_in_background' in r['denials'][0]['stderr'], r
        assert r['denials'][0]['hook_name'] == 'PreToolUse:Bash', r
        assert r['rate_limits'] == 1, r
        assert r['result'] == {'total_cost_usd': 1.5, 'duration_ms': 4000, 'num_turns': 6}, r


@case('transcripts: a missing path yields None fields')
def _transcripts_missing():
    from .sources import transcripts
    with tempfile.TemporaryDirectory() as repo:
        r = transcripts.read(os.path.join(repo, 'nope.log'))
        assert set(r) == set(transcripts.FIELDS) and all(v is None for v in r.values()), r


# --- context (T-0252) ----------------------------------------------------------------------------

def _read_event(*paths, tool='Read', key='file_path'):
    return json.dumps({'type': 'assistant', 'message': {'content': [
        {'type': 'tool_use', 'name': tool, 'input': {key: p}} for p in paths]}})


def _claude_log(*lines):
    return '\n'.join(lines) + '\n'


@case('context: the Claude arm lists Read paths once each; Bash and non-JSON lines add none')
def _context_claude():
    from .sources import context
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, 'a.log', _claude_log(
            _read_event('/r/AGENTS.md', '/r/docs/a.md'), 'prose the CLI printed',
            _read_event('/r/AGENTS.md'), _read_event('cat /r/CLAUDE.md', tool='Bash', key='command'),
            json.dumps({'type': 'user', 'message': {'content': [
                {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': '/r/user.md'}}]}}),
            '{truncated'))
        got = context.read(os.path.join(tmp, 'a.log'))
        assert got == {'source': 'stream-json', 'paths': ['/r/AGENTS.md', '/r/docs/a.md']}, got
        assert context.read(os.path.join(tmp, 'a.log'), backend='claude') == got


@case('context: a log with no Read says paths [] with a source, not a status')
def _context_claude_empty():
    from .sources import context
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, 'a.log', _claude_log(_read_event('echo 1', tool='Bash', key='command')))
        got = context.read(os.path.join(tmp, 'a.log'))
        assert got == {'source': 'stream-json', 'paths': []} and 'status' not in got, got


@case('context: a missing or unreadable log is a status with no paths key, never []')
def _context_log_status():
    from .sources import context
    with tempfile.TemporaryDirectory() as tmp:
        for backend in (None, 'claude', 'codex'):
            got = context.read(os.path.join(tmp, 'nope.log'), backend=backend)
            assert got == {'status': 'log absent'}, (backend, got)
        _write(tmp, 'locked.log', _claude_log(_read_event('/r/a.md')))
        os.chmod(os.path.join(tmp, 'locked.log'), 0)
        try:
            if os.access(os.path.join(tmp, 'locked.log'), os.R_OK):
                raise Skip('chmod 0 does not block this user (root)')
            got = context.read(os.path.join(tmp, 'locked.log'))
            assert got == {'status': 'log unreadable'}, got
        finally:
            os.chmod(os.path.join(tmp, 'locked.log'), 0o600)


def _codex_log(thread_id):
    ev = [{'type': 'codex_event', 'event': {'type': 'turn.started'}}]
    if thread_id:
        ev.insert(0, {'type': 'codex_event', 'event': {'type': 'thread.started', 'thread_id': thread_id}})
    return _claude_log(*[json.dumps(e) for e in ev], json.dumps({'type': 'result', 'backend': 'codex'}))


def _rollout_call(cmd, workdir):
    return json.dumps({'type': 'response_item', 'payload': {
        'type': 'function_call', 'name': 'exec_command',
        'arguments': json.dumps({'cmd': cmd, 'workdir': workdir})}})


@case('context: the Codex arm lists the files its rollout read, found by thread id')
def _context_codex():
    from .sources import context
    tid = '01a113e7-1ca9-7c62-8c76-9879b9631837'
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, 'work')
        _write(work, 'AGENTS.md', 'x\n')
        _write(work, 'docs/guide.md', 'x\n')
        _write(tmp, f'home/sessions/2026/10/06/rollout-2026-10-06T11-00-00-{tid}.jsonl', _claude_log(
            json.dumps({'type': 'session_meta', 'payload': {'id': tid}}),
            _rollout_call("sed -n '1,80p' AGENTS.md && cat docs/guide.md | head -5", work),
            _rollout_call('cat missing.md; rg -n foo AGENTS.md; ls docs', work),
            json.dumps({'type': 'response_item', 'payload': {
                'type': 'function_call', 'name': 'exec_command', 'arguments': '{not json'}}),
            json.dumps({'type': 'response_item', 'payload': {
                'type': 'function_call', 'name': 'shell', 'arguments': json.dumps(
                    {'command': ['bash', '-lc', 'tail -n 3 AGENTS.md'], 'workdir': work})}})))
        _write(tmp, 'a.log', _codex_log(tid))
        home = os.path.join(tmp, 'home')
        want = {'source': 'rollout', 'paths': [os.path.join(work, 'AGENTS.md'),
                                               os.path.join(work, 'docs/guide.md')]}
        got = context.read(os.path.join(tmp, 'a.log'), codex_home=home)
        assert got == want, got
        assert context.read(os.path.join(tmp, 'a.log'), backend='codex', codex_home=home) == want


@case('context: a Codex log with no rollout, or no thread id, says rollout absent')
def _context_codex_absent():
    from .sources import context
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, 'home/sessions/2026/10/06'))
        _write(tmp, 'a.log', _codex_log('01a113e7-1ca9-7c62-8c76-9879b9631837'))
        _write(tmp, 'b.log', _codex_log(None))
        _write(tmp, 'c.log', _codex_log('../../x'))
        for name in ('b.log', 'c.log'):
            got = context.read(os.path.join(tmp, name), codex_home=os.path.join(tmp, 'home'))
            assert got == {'status': 'rollout absent'}, (name, got)
        # A thread id with no rollout is a `codex exec --ephemeral` run (codex_exec.py): none is ever written.
        got = context.read(os.path.join(tmp, 'a.log'), codex_home=os.path.join(tmp, 'home'))
        assert got == {'status': 'exec ephemeral: no rollout written'}, got
        # The same log read as Claude has no thread lookup at all.
        assert context.read(os.path.join(tmp, 'a.log'), backend='claude')['source'] == 'stream-json'


@case('context: ingest gives a result with no log beside it status log absent, never []')
def _context_ingest():
    from . import ingest
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, 'repo')
        d = '.sdlc/0001-a'
        _write(repo, f'{d}/handoff.md', _ticket('T-0001', 'ready'))
        recorded = {'source': 'stream-json', 'paths': ['/recorded/by/run.sh']}
        lines = []
        for name, aid, ctx in (('builder-L2', 'a1', None), ('verifier-L1', 'a2', None),
                               ('scout-L1', 'a3', recorded), ('filer-L1', 'a4', None)):
            _write(repo, f'{d}/{name}.attempt.json', json.dumps(_attempt(name, aid)))
            _write(repo, f'{d}/{name}.md', _builder_text('done'))
            rec = {'role': name.split('-')[0], 'level': name.split('-')[1], 'file': name + '.md',
                   'attempt_id': aid}
            if ctx:
                rec['loaded_context'] = ctx
            lines.append(json.dumps(rec))
        _write(repo, f'{d}/runs.jsonl', '\n'.join(lines) + '\n')
        _write(repo, f'{d}/builder-L2.log', _claude_log(_read_event('/r/AGENTS.md')))
        _write(repo, f'{d}/scout-L1.log', _claude_log(_read_event('/r/derived.md')))
        _write(repo, f'{d}/verifier-L1.log', _codex_log('01a113e7-1ca9-7c62-8c76-9879b9631837'))
        out = ingest.run(repo, out=os.path.join(tmp, 'out'), bench_dir=os.path.join(tmp, 'nobench'))
        with open(os.path.join(out, 'events.jsonl'), encoding='utf-8') as f:
            rows = {r['attempt_id']: r for r in map(json.loads, f.read().splitlines())}
        assert rows['a1']['loaded_context'] == {'source': 'stream-json', 'paths': ['/r/AGENTS.md']}, rows['a1']
        assert rows['a3']['loaded_context'] == recorded, 'the run record wins over the log'
        assert rows['a4']['loaded_context'] == {'status': 'log absent'}, rows['a4']
        # a2 has a Codex log; its run record carries no backend, so the log's codex_event picks the arm.
        assert rows['a2']['loaded_context'] == {'status': 'exec ephemeral: no rollout written'}, rows['a2']


# --- fanout -------------------------------------------------------------------------------------

_R1, _R2 = 'fanout-0123456789ab', 'fanout-ba9876543210'


def _fanout_report(run_line, gates, extra, rows):
    head = ['# fanout report', ''] + ([run_line] if run_line else []) + [
        '- Integration branch: `fanout/x` at `abc` (from `def`)',
        '- Integration worktree: `/nowhere/lanes/integration`',
        '- Lane `alpha`: `/nowhere/lanes/alpha` (branch `fanout/x-alpha`)'] + extra
    head += [f'- Gate {k}: `{g}`' for k, g in enumerate(gates, 1)]
    head += ['- Logs: `/nowhere/lanes/logs`', '', '| Lane | Ticket | Outcome | Commit |',
             '|---|---|---|---|'] + rows
    return '\n'.join(head) + '\n'


def _fanout_legacy_files(lanes, extra=()):
    """The legacy lanes dir: no run ids, gate-alpha-T-0001-1.log, no fanout.log, no Run line."""
    _write(lanes, 'report.md', _fanout_report(None, ['test ! -e RED'], list(extra), [
        '| alpha | T-0001 | red: test ! -e RED rc=1 | 1234567 |',
        '| alpha | T-0002 | skipped | - |']))
    _write(lanes, 'logs/alpha-T-0001.log', 'driver one\ndriver two\n')
    _write(lanes, 'logs/gate-alpha-T-0001-1.log', 'gate output\n')
    _write(lanes, 'logs/notes.txt', 'not a log\n')


@case('fanout: a legacy lanes dir (no run ids, gate-<lane>-<id>-<k>.log, no fanout.log)')
def _fanout_legacy():
    from .sources import fanout
    with tempfile.TemporaryDirectory() as lanes:
        _fanout_legacy_files(lanes)
        f = fanout.read(lanes)
        rep = f['report']
        assert rep['run_id'] is None, rep
        got = [(r['lane'], r['ticket'], r['outcome'], r['commit']) for r in rep['rows']]
        assert got == [('alpha', 'T-0001', 'red: test ! -e RED rc=1', '1234567'),
                       ('alpha', 'T-0002', 'skipped', None)], got
        assert rep['gates'] == [{'k': 1, 'command': 'test ! -e RED'}], rep['gates']
        assert rep['integration_worktree'] == '/nowhere/lanes/integration', rep
        assert rep['external'] == [], rep
        assert f['fanout_log'] == [] and f['problems'] == [], f
        logs = os.path.join(lanes, 'logs')
        assert f['driver_logs'] == [{'lane': 'alpha', 'ticket': 'T-0001',
                                     'path': os.path.join(logs, 'alpha-T-0001.log'), 'lines': 2,
                                     'run_ids': [None], 'run_id_lines': [[None, 1]]}], f['driver_logs']
        g = f['gate_logs']
        assert len(g) == 1, g
        g = g[0]
        assert (g['lane'], g['ticket'], g['k'], g['attempt'], g['rc']) == \
            ('alpha', 'T-0001', 1, None, 1), g
        assert g['run_ids'] == [None] and g['path'] == os.path.join(logs, 'gate-alpha-T-0001-1.log'), g
        # negative control: an outcome with no rc leaves the gate's rc None
        _write(lanes, 'report.md', _fanout_report(None, ['test ! -e RED'], [], [
            '| alpha | T-0001 | merged | 1234567 |']))
        assert fanout.read(lanes)['gate_logs'][0]['rc'] is None
        # an empty or missing lanes dir reads as nothing
        f = fanout.read(os.path.join(lanes, 'nope'))
        assert (f['report'], f['fanout_log'], f['driver_logs'], f['gate_logs']) == (None, [], [], []), f


def _fanout_prefixed_files(lanes):
    """The prefixed lanes dir: run ids, fanout.log, gate attempts -a<n>, a Run line."""
    p1, p2 = f'[{_R1}] ', f'[{_R2}] '
    _write(lanes, 'report.md', _fanout_report(
        f'- Run: `{_R2}`', ['test -e OK', 'true | false'],
        ['- Lane `beta`: `/nowhere/lanes/beta` (branch `fanout/x-beta`)',
         '- Lane `ext`: external branch `codex/work` at `' + 'f' * 40 + '`'],
        ['| alpha | T-0001 | merged | abc1234 |',
         '| beta | T-0002 | red: true \\| false rc=1 | def5678 |']))
    _write(lanes, 'logs/fanout.log', '\n'.join([
        f'{p1}[alpha] T-0001 red: test -e OK rc=1',
        f'{p1}[alpha] T-0001 wip 1111111 on fanout/x-alpha',
        f'{p2}[alpha] T-0001 merged',
        f'{p2}[beta] T-0002 red: true | false rc=1', '']))
    _write(lanes, 'logs/alpha-T-0001.log', f'{p2}driver\n{p2}done')
    _write(lanes, 'logs/beta-T-0002.log', f'{p1}old\n{p2}new\n{p2}more\nbare\n')
    _write(lanes, 'logs/gate-alpha-T-0001-1-a1.log', f'{p1}attempt-one\n')
    _write(lanes, 'logs/gate-alpha-T-0001-1-a2.log', f'{p2}attempt-two\n')
    _write(lanes, 'logs/gate-beta-T-0002-1-a1.log', f'{p2}ok\n')
    _write(lanes, 'logs/gate-beta-T-0002-2-a1.log', f'{p2}red\n')


@case('fanout: a prefixed lanes dir (run ids, fanout.log, gate attempts -a<n>, a Run line)')
def _fanout_prefixed():
    from .sources import fanout
    with tempfile.TemporaryDirectory() as lanes:
        _fanout_prefixed_files(lanes)
        f = fanout.read(lanes)
        logs = os.path.join(lanes, 'logs')
        rep = f['report']
        assert rep['run_id'] == _R2, rep
        got = [(r['lane'], r['ticket'], r['outcome']) for r in rep['rows']]
        assert got == [('alpha', 'T-0001', 'merged'), ('beta', 'T-0002', 'red: true | false rc=1')], got
        assert rep['gates'] == [{'k': 1, 'command': 'test -e OK'},
                                {'k': 2, 'command': 'true | false'}], rep['gates']
        assert rep['external'] == [{'lane': 'ext', 'branch': 'codex/work', 'sha': 'f' * 40}], rep
        fl = [(e['line'], e['run_id'], e['lane'], e['ticket'], e['event']) for e in f['fanout_log']]
        assert fl == [(1, _R1, 'alpha', 'T-0001', 'red: test -e OK rc=1'),
                      (2, _R1, 'alpha', 'T-0001', 'wip 1111111 on fanout/x-alpha'),
                      (3, _R2, 'alpha', 'T-0001', 'merged'),
                      (4, _R2, 'beta', 'T-0002', 'red: true | false rc=1')], fl
        assert all(e['path'] == os.path.join(logs, 'fanout.log') for e in f['fanout_log'])
        d = {(x['lane'], x['ticket']): x for x in f['driver_logs']}
        assert (d[('alpha', 'T-0001')]['lines'], d[('alpha', 'T-0001')]['run_ids']) == (2, [_R2]), d
        b = d[('beta', 'T-0002')]
        assert (b['lines'], b['run_ids'], b['run_id_lines']) == \
            (4, [_R1, _R2, None], [[_R1, 1], [_R2, 2], [None, 4]]), b
        got = [(g['lane'], g['ticket'], g['k'], g['attempt'], g['run_ids'], g['rc'])
               for g in f['gate_logs']]
        assert got == [('alpha', 'T-0001', 1, 1, [_R1], 1),     # red in run 1 (fanout.log)
                       ('alpha', 'T-0001', 1, 2, [_R2], None),  # green rerun: no rc recorded
                       ('beta', 'T-0002', 1, 1, [_R2], None),   # green gate before the red one
                       ('beta', 'T-0002', 2, 1, [_R2], 1)], got  # k from the report's gate command
        assert f['problems'] == [], f['problems']
        # negative control: with no fanout.log, run 1's red is recorded nowhere, so no rc lands on a1
        os.remove(os.path.join(logs, 'fanout.log'))
        got = {(g['lane'], g['k'], g['attempt']): g['rc'] for g in fanout.read(lanes)['gate_logs']}
        assert got == {('alpha', 1, 1): None, ('alpha', 1, 2): None, ('beta', 1, 1): None,
                       ('beta', 2, 1): 1}, got


@case('fanout: a land red line with the log path and failing line still places its rc (T-0768)')
def _fanout_red_tail():
    from .sources import fanout
    from .detectors import hygiene
    tail1 = ' (log /nowhere/lanes/logs/gate-alpha-T-0001-1-a1.log): [fanout-x] FAIL project checks rc=3'
    tail2 = ' (log /nowhere/lanes/logs/gate-beta-T-0002-2-a1.log)'
    with tempfile.TemporaryDirectory() as lanes:
        _fanout_prefixed_files(lanes)
        for rel, old, new in (('logs/fanout.log', 'red: test -e OK rc=1', 'red: test -e OK rc=1' + tail1),
                              ('logs/fanout.log', 'red: true | false rc=1', 'red: true | false rc=1' + tail2),
                              ('report.md', 'red: true \\| false rc=1', 'red: true \\| false rc=1' + tail2)):
            path = os.path.join(lanes, rel)
            text = open(path, encoding='utf-8').read()
            assert old in text, (rel, old)
            open(path, 'w', encoding='utf-8').write(text.replace(old, new))
        got = [(g['lane'], g['ticket'], g['k'], g['attempt'], g['rc']) for g in fanout.read(lanes)['gate_logs']]
        assert got == [('alpha', 'T-0001', 1, 1, 1), ('alpha', 'T-0001', 1, 2, None),
                       ('beta', 'T-0002', 1, 1, None), ('beta', 'T-0002', 2, 1, 1)], got
    m = fanout.RED_RE.match('red: echo rc=5; false rc=1' + tail1)
    assert m and (m.group(1), m.group(2)) == ('echo rc=5; false', '1'), m
    assert hygiene._outcome_signal('red: false rc=1' + tail2) and hygiene._outcome_signal('red: false rc=1 (log /l) (no node_modules)')
    assert not hygiene._outcome_signal('merged (log /l)')


# --- git ----------------------------------------------------------------------------------------

_GIT_CFG = ('-c', 'user.name=traces', '-c', 'user.email=traces@example.invalid',
            '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
            '-c', 'init.defaultBranch=main')


def _g(repo, *args):
    """Run a fixture git command in repo (the reader's own helper is not reused, so the check is
    independent of it); returns stdout, raises AssertionError on failure."""
    import subprocess
    from .sources import git
    p = subprocess.run(['git', '-C', repo, *_GIT_CFG, *args], capture_output=True, text=True,
                       env=git._env(), stdin=subprocess.DEVNULL)
    assert p.returncode == 0, f'fixture git {" ".join(args)}: {p.stderr.strip()}'
    return p.stdout


def _need_git():
    import shutil
    if not shutil.which('git'):
        raise Skip('git is not installed')


def _git_repo(root):
    repo = os.path.join(root, 'repo')
    os.makedirs(repo)
    _g(repo, 'init', '-q')
    _write(repo, '.gitignore', '.worktrees/\n')
    _write(repo, 'foo.log', 'tracked log\n')
    _write(repo, 'notes.txt', 'not runtime\n')
    _write(repo, 'step-1/builder-L2.running', '')
    _g(repo, 'add', '-A')
    _g(repo, 'commit', '-q', '-m', 'fixture')
    _g(repo, 'commit', '-q', '--allow-empty', '-m', 'scratch')
    _g(repo, 'reset', '-q', '--hard', 'HEAD~1')
    for subj in ('wip(T-0001): driver failed rc=3', 'Merge fanout/x-alpha: T-0001', 'close T-0001',
                 'close T-0001 after the merge step', 'T-0001: a ticket title', 'wip: no id'):
        _g(repo, 'commit', '-q', '--allow-empty', '-m', subj)
    _g(repo, 'branch', 'fanout/x-alpha')
    return repo


def _git_state(repo):
    return (_g(repo, 'status', '--porcelain'), len(_g(repo, 'reflog', 'show', 'HEAD').splitlines()))


@case('git: worktrees, branches, tracked runtime, resets, and commits from a throwaway repo')
def _git_read():
    from .sources import git
    _need_git()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.realpath(tmp)
        repo = _git_repo(root)
        nest = os.path.join(repo, '.worktrees', 'x', '.worktrees', 'tmp', 'builder-1')
        lane = os.path.join(repo, '.worktrees', 'lane')
        added = []
        try:
            for wt in (nest, lane):
                _g(repo, 'worktree', 'add', '-q', '--detach', wt, 'HEAD')
                added.append(wt)
            _g(lane, 'reset', '-q', '--hard', 'HEAD~2')
            before, lane_before = _git_state(repo), _git_state(lane)
            r = git.read(repo)
            after, lane_after = _git_state(repo), _git_state(lane)
            assert before == after, ('read changed the repo', before, after)
            assert lane_before == lane_after, ('read changed the lane', lane_before, lane_after)
            assert set(r) == set(git.FIELDS) and r['problems'] == [], r
            wts = {w['path']: (w['branch'], w['nested']) for w in r['worktrees']}
            assert wts == {repo: ('main', False), nest: (None, True), lane: (None, False)}, wts
            assert sorted(r['branches']) == ['fanout/x-alpha', 'main'], r['branches']
            assert sorted(r['tracked_runtime']) == ['foo.log', 'step-1/builder-L2.running'], r
            assert [s for _, s in r['resets']] == ['reset: moving to HEAD~1'], r['resets']
            assert all(len(sha) == 40 for sha, _ in r['resets'] + r['commits']), r
            subj = [s for _, s in r['commits']]
            assert subj == ['close T-0001', 'Merge fanout/x-alpha: T-0001',
                            'wip(T-0001): driver failed rc=3'], subj
            # integration given: resets come from its reflog, not the repo's
            r2 = git.read(repo, integration=lane)
            assert [s for _, s in r2['resets']] == ['reset: moving to HEAD~2'], r2['resets']
            assert r2['commits'] == r['commits'], r2
            # limit bounds the log walk: the newest 5 commits stop short of the wip commit
            r3 = git.read(repo, limit=5)
            assert [s for _, s in r3['commits']] == ['close T-0001', 'Merge fanout/x-alpha: T-0001'], r3
        finally:
            for wt in reversed(added):
                _g(repo, 'worktree', 'remove', '--force', wt)


@case('git: a dir that is not a git work tree gives empty lists and a problem')
def _git_not_repo():
    from .sources import git
    _need_git()
    with tempfile.TemporaryDirectory() as tmp:
        plain = os.path.join(os.path.realpath(tmp), 'plain')
        os.makedirs(plain)
        r = git.read(plain)
        assert all(r[k] == [] for k in git.FIELDS if k != 'problems'), r
        assert len(r['problems']) == 1 and 'not a git work tree' in r['problems'][0], r
        r = git.read(os.path.join(plain, 'missing'))
        assert len(r['problems']) == 1 and r['worktrees'] == [], r
        # a real repo with a non-repo integration dir: repo facts stay, resets empty, one problem
        repo = _git_repo(os.path.realpath(tmp))
        r = git.read(repo, integration=plain)
        assert r['resets'] == [] and r['branches'] and len(r['problems']) == 1, r


@case('git: under the sibling root (wtroot.py root) a lane is not nested, its tmp/ tree and a lane-nested root are')
def _git_sibling_root():
    from .sources import git
    _need_git()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.realpath(tmp)
        repo = _git_repo(root)
        sib = os.path.join(root, 'repo.worktrees')  # T-0563: <parent>/<repo>.worktrees
        lane = os.path.join(sib, 'lane')
        tmpw = os.path.join(sib, 'tmp', 'builder-1', 'w')
        nest = os.path.join(sib, 'lane2', '.claude', 'worktrees', 'x')
        added = []
        try:
            for wt in (lane, tmpw, nest):
                _g(repo, 'worktree', 'add', '-q', '--detach', wt, 'HEAD')
                added.append(wt)
            wts = {w['path']: w['nested'] for w in git.read(repo)['worktrees']}
            assert wts == {repo: False, lane: False, tmpw: True, nest: True}, wts
        finally:
            for wt in reversed(added):
                _g(repo, 'worktree', 'remove', '--force', wt)


@case('ingest: lanes dirs come from the sibling root (wtroot.py root) and the legacy roots')
def _ingest_lanes_sibling():
    from . import ingest
    _need_git()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.realpath(tmp)
        repo = _git_repo(root)
        _write(root, 'repo.worktrees/fanout-a/report.md', '# report\n')
        _write(root, 'repo.worktrees/plain/notes.txt', 'no report, no logs\n')
        _write(repo, '.worktrees/fanout-old/report.md', '# report\n')
        got = ingest._lanes_dirs(repo, [])
        assert got == [os.path.join(root, 'repo.worktrees', 'fanout-a'),
                       os.path.join(repo, '.worktrees', 'fanout-old')], got


# --- tickets ------------------------------------------------------------------------------------

def _ticket(tid, status):
    return ('---\n'
            f'id: {tid}\ntitle: t\ntype: chore\nstatus: {status}\nsize: S\npriority: P2\n'
            'depends: []\ncreated: 2026-01-01\n'
            '---\n\nbody\n')


@case('tickets: slug to id and status for open and closed folders; a reused id is one problem')
def _tickets_read():
    from .sources import tickets as tr
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, '0001-a/handoff.md', _ticket('T-0001', 'ready'))
        _write(tmp, '.0002-b/handoff.md', _ticket('T-0002', 'done'))
        _write(tmp, '0003-c/handoff.md', _ticket('T-0001', 'ready'))
        r = tr.read(tmp)
        assert r['by_slug'] == {'0001-a': ('T-0001', 'ready'), '.0002-b': ('T-0002', 'done'),
                                '0003-c': ('T-0001', 'ready')}, r['by_slug']
        assert len(r['problems']) == 1 and 'duplicate id T-0001' in r['problems'][0], r['problems']
        assert r['notes'] is False, r
        _write(tmp, 'notes.md', 'n\n')
        assert tr.read(tmp)['notes'] is True


@case('tickets: a root without a config gives external empty')
def _tickets_no_config():
    from .sources import tickets as tr
    with tempfile.TemporaryDirectory() as tmp:
        assert tr.read(tmp)['external'] == []
        _write(tmp, 'config', 'external_branch: feat/x\n')
        assert tr.read(tmp)['external'] == ['feat/x'], tr.read(tmp)


# --- bench --------------------------------------------------------------------------------------

def _bench_step(root, rel, verdict, cost):
    _write(root, f'{rel}/verifier-L1.md', _verifier_text(verdict))
    _write(root, f'{rel}/runs.jsonl',
           json.dumps({'role': 'builder', 'cost_usd': cost / 2}) + '\n'
           + json.dumps({'role': 'verifier', 'cost_usd': cost / 2}) + '\n')


@case('bench: median cost per passed step over two result dirs; a failed step does not count')
def _bench_baseline():
    from .sources import bench
    with tempfile.TemporaryDirectory() as tmp:
        _bench_step(tmp, 'results/r1/step-1', 'pass', 1.0)
        _bench_step(tmp, 'results/r1/step-2', 'fail', 50.0)
        _bench_step(tmp, 'results/r1/step-2.superseded-1', 'pass', 99.0)
        _bench_step(tmp, 'results/r2/step-1', 'pass', 3.0)
        _bench_step(tmp, 'results/r2/step-2', 'pass', 8.0)
        _write(tmp, 'results/r1/grade.md', '# grade\nhidden_check: pass\n')
        b = bench.baseline(tmp)
        assert b['median_cost_per_passed_step'] == 3.0, b
        r1, r2 = os.path.join(tmp, 'results', 'r1'), os.path.join(tmp, 'results', 'r2')
        assert b['steps'] == [(r1, 1, 1.0), (r2, 1, 3.0), (r2, 2, 8.0)], b['steps']
        assert b['hidden'] == {r1: 'pass', r2: None}, b['hidden']


@case('bench: a missing results dir gives a None median and no steps')
def _bench_missing():
    from .sources import bench
    with tempfile.TemporaryDirectory() as tmp:
        b = bench.baseline(tmp)
        assert b['median_cost_per_passed_step'] is None and b['steps'] == [], b
    assert os.path.basename(bench.default_bench_dir()) == 'bench'


# --- store --------------------------------------------------------------------------------------

def _store_repo(root):
    """A throwaway git repo with two task dirs of attempt, runs, and result files, committed."""
    _need_git()
    repo = os.path.join(root, 'repo')
    os.makedirs(repo)
    _g(repo, 'init', '-q')
    _write(repo, '.gitignore', '*.log\n')
    _write(repo, '.sdlc/0001-a/handoff.md', _ticket('T-0001', 'ready'))
    _write(repo, '.sdlc/.0002-b/handoff.md', _ticket('T-0002', 'done'))
    _write(repo, '.sdlc/_templates/x/builder-L1.attempt.json', json.dumps(_attempt('builder-L1', 'tpl')))
    for task, tag in (('0001-a', 'a'), ('.0002-b', 'b')):
        d = f'.sdlc/{task}/step-1'
        _write(repo, f'{d}/builder-L2.attempt.json', json.dumps(_attempt('builder-L2', f'{tag}1')))
        _write(repo, f'{d}/verifier-L1.attempt.json', json.dumps(_attempt('verifier-L1', f'{tag}2')))
        _write(repo, f'{d}/runs.jsonl',
               json.dumps({'role': 'builder', 'level': 'L2', 'file': 'builder-L2.md',
                           'attempt_id': f'{tag}1', 'turns': 3, 'cost_usd': 0.25}) + '\n'
               + json.dumps({'role': 'verifier', 'level': 'L1', 'file': 'verifier-L1.md',
                             'attempt_id': f'{tag}2', 'turns': 2, 'cost_usd': 0.5}) + '\n')
        _write(repo, f'{d}/builder-L2.md', _builder_text('done'))
        _write(repo, f'{d}/verifier-L1.md', _verifier_text('pass'))
    _write(repo, '.sdlc/.0002-b/planner-L2.attempt.json', json.dumps(_attempt('planner-L2', 'bp')))
    _write(repo, '.sdlc/.0002-b/planner-L2.md', '## Steps\n1. x\n')
    _write(repo, '.sdlc/0001-a/step-1/builder-L2.log', _transcript_log())
    _g(repo, 'add', '-A')
    _g(repo, 'commit', '-q', '-m', 'fixture')
    return repo


def _files(dir):
    return sum(1 for n in os.listdir(dir) if os.path.isfile(os.path.join(dir, n)))


def _events(out):
    with open(os.path.join(out, 'events.jsonl'), 'rb') as f:
        return f.read()


@case('store: two ingests of an unchanged corpus are byte-identical; the second opens 0 files')
def _store_unchanged():
    from . import ingest, store
    with tempfile.TemporaryDirectory() as tmp:
        repo = _store_repo(tmp)
        out, nobench = os.path.join(tmp, 'out'), os.path.join(tmp, 'nobench')
        assert ingest.run(repo, out=out, bench_dir=nobench) == out
        first, reads1 = _events(out), store.READS
        sdlc = os.path.join(repo, '.sdlc')
        want = sum(_files(os.path.join(sdlc, t, s)) for t, s in
                   (('0001-a', ''), ('0001-a', 'step-1'), ('.0002-b', ''), ('.0002-b', 'step-1')))
        assert reads1 == want, f'first ingest READS {reads1}, want {want}'
        rows = [json.loads(l) for l in first.decode().splitlines()]
        assert [list(r) for r in rows] == [list(table.ROW_FIELDS)] * len(rows), 'key order'
        ids = [r['attempt_id'] for r in rows]
        assert ids == ['bp', 'b1', 'b2', 'a1', 'a2'], ids
        assert all(r['ticket'] == ('T-0001' if r['attempt_id'][0] == 'a' else 'T-0002')
                   for r in rows), rows
        a1 = next(r for r in rows if r['attempt_id'] == 'a1')
        assert (a1['tool_calls'], a1['denials'], a1['rate_limits']) == (5, 1, 1), a1
        assert '.sdlc/0001-a/step-1/builder-L2.log' in a1['sources'], a1['sources']
        assert not any('_templates' in s for r in rows for s in r['sources']), rows
        ingest.run(repo, out=out, bench_dir=nobench)
        assert _events(out) == first, 'second events.jsonl differs'
        assert store.READS == 0, f'second ingest READS {store.READS}, want 0'
        with open(os.path.join(out, 'aux.json'), encoding='utf-8') as f:
            aux = json.load(f)
        assert aux['repo'] == os.path.abspath(repo), aux['repo']
        for k in ('lanes', 'gates', 'git', 'tickets', 'baseline'):
            assert k in aux, k


@case('nested-runs')
def _nested_runs():
    from . import ingest
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, 'repo')
        _write(repo, '.sdlc/0003-c/handoff.md', _ticket('T-0003', 'ready'))
        _write(repo, '.sdlc/0003-c/verify/runs.jsonl',
               json.dumps({'role': 'verifier', 'level': 'L1', 'file': 'verifier-L1.md',
                           'attempt_id': 'n1', 'turns': 2, 'cost_usd': 0.5}) + '\n')
        out = os.path.join(tmp, 'out')
        ingest.run(repo, out=out, bench_dir=os.path.join(tmp, 'nobench'))
        rows = [json.loads(l) for l in _events(out).decode().splitlines()]
        hit = [r for r in rows if '.sdlc/0003-c/verify/runs.jsonl' in r['sources']]
        assert len(hit) == 1, rows
        assert hit[0]['step'] is None, hit[0]


@case('store: appending one attempt record to one dir re-reads only that dir')
def _store_append():
    from . import ingest, store
    with tempfile.TemporaryDirectory() as tmp:
        repo = _store_repo(tmp)
        out, nobench = os.path.join(tmp, 'out'), os.path.join(tmp, 'nobench')
        ingest.run(repo, out=out, bench_dir=nobench)
        d = os.path.join(repo, '.sdlc', '.0002-b', 'step-1')
        _write(d, 'builder-L3.attempt.json', json.dumps(_attempt('builder-L3', 'b3')))
        ingest.run(repo, out=out, bench_dir=nobench)
        assert store.READS == _files(d), f'READS {store.READS}, want {_files(d)}'
        rows = [json.loads(l) for l in _events(out).decode().splitlines()]
        assert [r['attempt_id'] for r in rows] == ['bp', 'b1', 'b3', 'b2', 'a1', 'a2'], rows


@case('store: with out outside the repo, git status stays empty after the ingest')
def _store_clean():
    from . import ingest
    with tempfile.TemporaryDirectory() as tmp:
        repo = _store_repo(tmp)
        assert _g(repo, 'status', '--porcelain') == '', 'fixture repo not clean'
        ingest.run(repo, out=os.path.join(tmp, 'out'), bench_dir=os.path.join(tmp, 'nobench'))
        status = _g(repo, 'status', '--porcelain', '--untracked-files=all')
        assert status == '', f'git status after ingest: {status!r}'


@case('store: with no out, the out dir lies under <cwd>/.sdlc/runtime/traces/')
def _store_default_out():
    import hashlib
    from . import ingest, store
    with tempfile.TemporaryDirectory() as tmp:
        repo = _store_repo(tmp)
        cwd = os.path.join(tmp, 'cwd')
        os.makedirs(cwd)
        here = os.getcwd()
        os.chdir(cwd)
        try:
            base = os.path.join(os.getcwd(), '.sdlc', 'runtime', 'traces')
            out = ingest.run(repo, bench_dir=os.path.join(tmp, 'nobench'))
        finally:
            os.chdir(here)
        key = 'repo-' + hashlib.sha256(os.path.abspath(repo).encode()).hexdigest()[:8]
        assert out == os.path.join(base, key), (out, base, key)
        assert store.out_dir(repo, '/x/y') == '/x/y'
        assert os.path.isfile(os.path.join(out, 'events.jsonl')), out
        assert os.path.isfile(os.path.join(out, 'cursor.json')), out


# --- findings -----------------------------------------------------------------------------------

def _three_findings():
    from . import findings
    return [
        findings.make('retry-loop', 'waste', 'high', 'sdlc', 'scripts/steps.py', 'rebuild cap',
                      [{'attempt_id': 'a1'}, {'attempt_id': 'a2', 'cost_usd': 1.5}],
                      'builder rebuilt twice on one criterion'),
        findings.make('stale-plan', 'bug', 2, 'sdlc', 'agents/planner.md', 'scope guard',
                      [{'path': '.sdlc/t1/planner-L3.md', 'line': 12}], 'guard omits .gitignore'),
        findings.make('slow-verify', 'waste', 'low', 'host', None, 'rate limit',
                      [{'path': '.sdlc/t1/step-1/verifier-L1.log', 'line': 3}], 'verifier waited'),
    ]


@case('findings: writing the same three findings twice keeps every id and changes only last_seen')
def _findings_rewrite():
    from . import findings
    a = _three_findings()
    b = _three_findings()
    assert [f['id'] for f in a] == [f['id'] for f in b], 'id not deterministic'
    assert len({f['id'] for f in a}) == 3, 'ids collide'
    assert all(len(f['id']) == 12 and int(f['id'], 16) >= 0 for f in a), a
    # the id ignores evidence key order and entry order, and depends on the detector
    ev = [{'attempt_id': 'a2', 'cost_usd': 1.5}, {'attempt_id': 'a1'}]
    swapped = findings.make('retry-loop', 'waste', 3, 'sdlc', 'scripts/steps.py', 'x',
                            [dict(reversed(list(e.items()))) for e in ev], 'other summary')
    assert swapped['id'] == a[0]['id'], 'id depends on evidence order or summary'
    other = findings.make('retry-loop-2', 'waste', 3, 'sdlc', 'scripts/steps.py', 'x', ev, 's')
    assert other['id'] != a[0]['id'], 'id ignores the detector'
    assert (a[0]['severity'], a[1]['severity'], a[2]['severity']) == (3, 2, 1), a
    assert a[2]['cause_hint'] == {'file': None, 'rule': 'rate limit'}, a[2]
    for bad in (dict(severity='urgent'), dict(layer='plugin'), dict(evidence=[{'line': 1}])):
        kw = dict(severity=1, layer='unknown', evidence=[{'attempt_id': 'z'}])
        kw.update(bad)
        try:
            findings.make('d', 'f', kw['severity'], kw['layer'], None, 'r', kw['evidence'], 's')
        except ValueError:
            continue
        raise AssertionError(f'make accepted {bad}')
    with tempfile.TemporaryDirectory() as out:
        findings.write(out, a, '2026-09-30T06:00:00+00:00')
        first = {d['id']: d for d in findings.load(out)}
        findings.write(out, b, '2026-09-30T07:00:00+00:00')
        second = {d['id']: d for d in findings.load(out)}
        assert set(first) == set(second) == {f['id'] for f in a}, (first, second)
        for fid in first:
            x, y = first[fid], second[fid]
            assert x['first_seen'] == x['last_seen'] == '2026-09-30T06:00:00+00:00', x
            assert y['last_seen'] == '2026-09-30T07:00:00+00:00', y
            assert {k: v for k, v in x.items() if k != 'last_seen'} == \
                {k: v for k, v in y.items() if k != 'last_seen'}, (x, y)
            assert x['stale'] is False and y['stale'] is False, (x, y)


@case('findings: a finding missing from the second run is kept and marked stale')
def _findings_stale():
    from . import findings
    a = _three_findings()
    with tempfile.TemporaryDirectory() as out:
        findings.write(out, a, '2026-09-30T06:00:00+00:00')
        findings.write(out, a[:2], '2026-09-30T07:00:00+00:00')
        rows = {d['id']: d for d in findings.load(out)}
        assert set(rows) == {f['id'] for f in a}, rows
        gone = rows[a[2]['id']]
        assert gone['stale'] is True, gone
        assert gone['first_seen'] == gone['last_seen'] == '2026-09-30T06:00:00+00:00', gone
        assert all(rows[f['id']]['stale'] is False for f in a[:2]), rows
        # seen again later, it is live once more and keeps its first_seen
        findings.write(out, a, '2026-09-30T08:00:00+00:00')
        back = {d['id']: d for d in findings.load(out)}[a[2]['id']]
        assert (back['stale'], back['first_seen'], back['last_seen']) == \
            (False, '2026-09-30T06:00:00+00:00', '2026-09-30T08:00:00+00:00'), back


@case('findings: clusters(out, 2) over three cause files returns the two highest-severity ones')
def _findings_clusters():
    from . import findings

    def f(det, sev, file, aid):
        return findings.make(det, 'waste', sev, 'sdlc', file, 'r', [{'attempt_id': aid}], det)

    a = [f('a', 3, 'agents/builder.md', 'a1')]
    b = [f('b1', 3, 'scripts/run.sh', 'b1'), f('b2', 1, 'scripts/run.sh', 'b2')]
    c = [f(f'c{i}', 1, 'skills/chain/SKILL.md', f'c{i}') for i in range(3)]
    c_old = f('c-old', 3, 'skills/chain/SKILL.md', 'c9')
    with tempfile.TemporaryDirectory() as out:
        findings.write(out, a + b + c + [c_old], '2026-09-30T06:00:00+00:00')
        findings.write(out, a + b + c, '2026-09-30T07:00:00+00:00')  # c_old goes stale
        got = findings.clusters(out, 2)
        want = [{'file': 'scripts/run.sh', 'severity': 3, 'count': 2,
                 'ids': sorted(x['id'] for x in b)},
                {'file': 'agents/builder.md', 'severity': 3, 'count': 1, 'ids': [a[0]['id']]}]
        assert got == want, got
        with open(os.path.join(out, 'clusters.json'), encoding='utf-8') as fh:
            assert json.load(fh) == want, 'clusters.json differs from the return value'
        every = findings.clusters(out, 10)
        assert [x['file'] for x in every] == ['scripts/run.sh', 'agents/builder.md',
                                              'skills/chain/SKILL.md'], every
        assert every[2]['count'] == 3 and every[2]['severity'] == 1, every[2]


# --- escalation ---------------------------------------------------------------------------------

_ESC_TASK = '.sdlc/0001-t'


def _e(name, aid, text=None, run=True, **kw):
    return {'name': name, 'aid': aid, 'text': text, 'run': run, 'kw': kw}


def _esc_repo(root, dirs, handoff='# task\n', files=None):
    """A repo with one task dir: {sub dir ('' for the task dir): [_e(...)]} in run order."""
    repo = os.path.join(root, 'repo')
    _write(repo, f'{_ESC_TASK}/handoff.md', handoff)
    for sub, entries in dirs.items():
        d = f'{_ESC_TASK}/{sub}' if sub else _ESC_TASK
        runs = []
        for e in entries:
            a = _attempt(e['name'], e['aid'], **e['kw'])
            _write(repo, f'{d}/{e["name"]}.attempt.json', json.dumps(a))
            if e['text'] is not None:
                _write(repo, f'{d}/{e["name"]}.md', e['text'])
            if e['run']:
                runs.append({'role': a['role'], 'level': a['level'], 'file': f'{e["name"]}.md',
                             'attempt_id': e['aid'], 'turns': 1, 'cost_usd': 0.1})
        if runs:
            _write(repo, f'{d}/runs.jsonl', ''.join(json.dumps(r) + '\n' for r in runs))
    for rel, text in (files or {}).items():
        _write(repo, f'{_ESC_TASK}/{rel}', text)
    return repo


def _esc_rows(repo):
    """The rows the ingest persists for repo, round-tripped through events.jsonl lines."""
    from . import ingest, store
    rows = []
    for t in ingest.task_dirs(os.path.join(repo, '.sdlc')):
        rel = f'.sdlc/{t}'
        rows += ingest.read_dir(repo, rel, None)
        for s in ingest.step_dirs(os.path.join(repo, rel)):
            rows += ingest.read_dir(repo, f'{rel}/{s}', None)
    return [json.loads(store.event_line(r)) for r in rows]


def _esc_detect(repo, detector):
    from .detectors import escalation
    return [f for f in escalation.detect(_esc_rows(repo), {'repo': repo}, None)
            if f['detector'] == detector]


def _esc_one(got, detector):
    assert len(got) == 1, f'{detector}: want 1 finding, got {len(got)}: {got}'
    f = got[0]
    assert any(('path' in e and 'line' in e) or 'attempt_id' in e for e in f['evidence']), f
    assert f['cause_hint']['file'], f
    assert f['family'] == 'escalation' and f['layer'] == 'sdlc', f
    return f


_PLANNED = '## Steps\n1. x\n'
_REVIEW = '# task\n\n## Plan review\n- swap applied: step 1: criterion 2 rewritten\n'


def _esc_passed_step():
    return [_e('builder-L2', 's1b', _builder_text('done')),
            _e('verifier-L1', 's1v', _verifier_text('pass'))]


def _fx_replan_loop(tmp, defect):
    dirs = {'': [_e('planner-L3', 'p1', _PLANNED)], 'step-1': _esc_passed_step()}
    if defect:
        dirs[''].append(_e('planner-L3-2', 'p2', _PLANNED))
        dirs['step-1.superseded-1'] = [_e('builder-L2', 'old', _builder_text('blocked'))]
    return _esc_repo(tmp, dirs)


def _ck_replan_loop(f):
    assert f['severity'] == 2, f
    paths = [e.get('path') for e in f['evidence']]
    assert f'{_ESC_TASK}/step-1.superseded-1/builder-L2.md' in paths, paths
    assert {e.get('attempt_id') for e in f['evidence']} >= {'p1', 'p2'}, f['evidence']


def _fx_recurring_finding(tmp, defect):
    handoff = _REVIEW + ('- recurring finding: step 1 verifier notes both say criterion 2 red\n'
                         if defect else '')
    return _esc_repo(tmp, {'step-1': _esc_passed_step()}, handoff=handoff)


def _ck_recurring_finding(f):
    assert f['evidence'] == [{'path': f'{_ESC_TASK}/handoff.md', 'line': 5}], f['evidence']


def _fx_unchanged_verdict_bump(tmp, defect):
    second = 'Criterion 2  is RED: `x.txt` missing' if defect else 'criterion 3 is red: y'
    return _esc_repo(tmp, {'step-1': [
        _e('builder-L2', 'b2', _builder_text('done')),
        _e('verifier-L1', 'v1', _verifier_text('fail', 'criterion 2 is red: `x.txt` missing')),
        _e('builder-L3', 'b3', _builder_text('done')),
        _e('verifier-L2', 'v2', _verifier_text('fail', second))]})


def _ck_unchanged_verdict_bump(f):
    d = f'{_ESC_TASK}/step-1'
    assert [e['path'] for e in f['evidence']] == [f'{d}/verifier-L1.md', f'{d}/verifier-L2.md'], f


def _fx_plan_defect_refusal(tmp, defect):
    handoff = _REVIEW + (
        '- split refusal of planner-L1.md: steps: planner-L1.md step 1: acceptance criterion '
        'pins a commit sha fixed at plan time: `git diff abc1234f`\n'
        '  plan defect: replan this step (/chain 3)\n' if defect else '')
    return _esc_repo(tmp, {'step-1': _esc_passed_step()}, handoff=handoff)


def _ck_plan_defect_refusal(f):
    assert f['cause_hint'] == {'file': 'scripts/steps.py', 'rule': 'pins a commit sha'}, f
    assert f['evidence'] == [{'path': f'{_ESC_TASK}/handoff.md', 'line': 5}], f['evidence']


def _fx_wrong_resume_order(tmp, defect):
    return _esc_repo(tmp, {
        'step-1': [_e('builder-L2', 'blk', _builder_text('blocked' if defect else 'done'))],
        'step-2': [_e('builder-L2', 'next', _builder_text('done'),
                      started_at='2026-09-30T06:05:00+00:00',
                      finished_at='2026-09-30T06:06:00+00:00'),
                   _e('verifier-L1', 'nextv', _verifier_text('pass'),
                      started_at='2026-09-30T06:07:00+00:00',
                      finished_at='2026-09-30T06:08:00+00:00')]})


def _ck_wrong_resume_order(f):
    assert f['evidence'] == [{'attempt_id': 'blk'}, {'attempt_id': 'next'}], f['evidence']


def _fx_exit_3_result(tmp, defect):
    return _esc_repo(tmp, {'step-1': [
        _e('builder-L2', 'x3', _builder_text('done'), exit_code=3 if defect else 0)]})


def _ck_exit_3_result(f):
    assert f['evidence'] == [{'attempt_id': 'x3'}], f
    assert f['cause_hint']['file'] == 'agents/builder.md', f


def _fx_statusless_builder(tmp, defect):
    return _esc_repo(tmp, {'step-1': [
        _e('builder-L2', 'sb', _builder_text(None if defect else 'done'))]})


def _ck_statusless_builder(f):
    assert f['evidence'] == [{'path': f'{_ESC_TASK}/step-1/builder-L2.md', 'line': 1}], f


def _fx_no_verdict_verifier(tmp, defect):
    return _esc_repo(tmp, {'step-1': [
        _e('builder-L2', 'nb', _builder_text('done')),
        _e('verifier-L1', 'nv', _verifier_text(None if defect else 'pass'))]})


def _ck_no_verdict_verifier(f):
    assert f['evidence'] == [{'path': f'{_ESC_TASK}/step-1/verifier-L1.md', 'line': 1}], f


def _fx_attempt_without_run_row(tmp, defect):
    return _esc_repo(tmp, {'step-1': [
        _e('builder-L2', 'ok1', _builder_text('done')),
        _e('builder-L3', 'lost', None, run=not defect, status='completed', exit_code=0)]})


def _ck_attempt_without_run_row(f):
    assert f['severity'] == 2, f
    assert f['evidence'] == [{'attempt_id': 'lost', 'status': 'completed'}], f


def _fx_stale_running_marker(tmp, defect):
    files = {'step-1/builder-L2.running': '1790000000\n'} if defect else {}
    return _esc_repo(tmp, {'step-1': [_e('builder-L2', 'mk', _builder_text('done'))]},
                     files=files)


def _ck_stale_running_marker(f):
    assert f['evidence'] == [{'path': f'{_ESC_TASK}/step-1/builder-L2.running', 'line': 1}], f


_ESC = (
    ('replan-loop', _fx_replan_loop, _ck_replan_loop),
    ('recurring-finding', _fx_recurring_finding, _ck_recurring_finding),
    ('unchanged-verdict-bump', _fx_unchanged_verdict_bump, _ck_unchanged_verdict_bump),
    ('plan-defect-refusal', _fx_plan_defect_refusal, _ck_plan_defect_refusal),
    ('wrong-resume-order', _fx_wrong_resume_order, _ck_wrong_resume_order),
    ('exit-3-result', _fx_exit_3_result, _ck_exit_3_result),
    ('statusless-builder', _fx_statusless_builder, _ck_statusless_builder),
    ('no-verdict-verifier', _fx_no_verdict_verifier, _ck_no_verdict_verifier),
    ('attempt-without-run-row', _fx_attempt_without_run_row, _ck_attempt_without_run_row),
    ('stale-running-marker', _fx_stale_running_marker, _ck_stale_running_marker),
)


def _esc_fires(detector, build, check):
    with tempfile.TemporaryDirectory() as tmp:
        check(_esc_one(_esc_detect(build(tmp, True), detector), detector))


def _esc_quiet(detector, build):
    with tempfile.TemporaryDirectory() as tmp:
        got = _esc_detect(build(tmp, False), detector)
        assert got == [], f'{detector} fired on the control: {got}'


for _det, _build, _check in _ESC:
    case(f'escalation: {_det} fires')(
        lambda d=_det, b=_build, c=_check: _esc_fires(d, b, c))
    case(f'escalation: {_det} quiet on control')(lambda d=_det, b=_build: _esc_quiet(d, b))


@case('escalation: replan-loop ignores a failed planner attempt')
def _esc_rpl_failed():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _esc_repo(tmp, {
            '': [_e('planner-L3', 'p1', _PLANNED),
                 _e('planner-L3-2', 'p2', None, status='failed', exit_code=1)],
            'step-1': _esc_passed_step()})
        got = _esc_detect(repo, 'replan-loop')
        assert got == [], f'replan-loop counted a failed planner attempt: {got}'


@case('escalation: wrong-resume-order quiet after a completed replan')
def _esc_wro_replan():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _esc_repo(tmp, {
            '': [_e('planner-L2', 'pl', _PLANNED, started_at='2026-09-30T06:02:00+00:00',
                    finished_at='2026-09-30T06:03:00+00:00')],
            'step-1': [_e('builder-L2', 'blk', _builder_text('blocked'))],
            'step-2': [_e('builder-L2', 'nx', _builder_text('done'),
                          started_at='2026-09-30T06:05:00+00:00',
                          finished_at='2026-09-30T06:06:00+00:00')]})
        got = _esc_detect(repo, 'wrong-resume-order')
        assert got == [], f'wrong-resume-order fired after a completed replan: {got}'


@case('escalation: wrong-resume-order fires once per blocked step')
def _esc_wro_once():
    def late(aid, m):
        return _e('builder-L2', aid, _builder_text('done'),
                  started_at=f'2026-09-30T06:0{m}:00+00:00',
                  finished_at=f'2026-09-30T06:0{m}:30+00:00')
    with tempfile.TemporaryDirectory() as tmp:
        repo = _esc_repo(tmp, {'step-1': [_e('builder-L2', 'blk', _builder_text('blocked'))],
                               'step-2': [late('n2', 5)], 'step-3': [late('n3', 7)]})
        got = _esc_detect(repo, 'wrong-resume-order')
        assert len(got) == 1, got
        assert got[0]['evidence'] == [{'attempt_id': 'blk'}, {'attempt_id': 'n2'}], got[0]


@case('escalation: plan-defect-refusal groups entries by rule and flags result plan defects')
def _esc_plan_defect_groups():
    handoff = ('# task\n\n## Plan review (factory)\n'
               'steps.py split refused planner-L1.md:\n'
               '```\nsteps: p step 1: acceptance criterion command does not parse: x\n'
               'plan defect: replan this step (/chain 3)\n```\n'
               'Cause: a stray quote.\n\n'
               '- plan defect: step 2 needs a new criterion\n'
               '- split refusal: acceptance criterion does not parse: y; plan defect: replan\n'
               '\n## Later\nplan defect: not under plan review\n')
    with tempfile.TemporaryDirectory() as tmp:
        repo = _esc_repo(tmp, {'step-1': [
            _e('builder-L2', 'g1', _builder_text('done')),
            _e('verifier-L1', 'g2', _verifier_text('fail', 'plan defect: criterion 2 is wrong'))]},
            handoff=handoff)
        got = _esc_detect(repo, 'plan-defect-refusal')
        by_rule = {f['cause_hint']['rule']: f for f in got}
        assert set(by_rule) == {'does not parse', 'other', 'verifier plan defect'}, by_rule
        h = f'{_ESC_TASK}/handoff.md'
        assert by_rule['does not parse']['evidence'] == [{'path': h, 'line': 4},
                                                         {'path': h, 'line': 12}], by_rule
        assert by_rule['other']['evidence'] == [{'path': h, 'line': 11}], by_rule
        v = by_rule['verifier plan defect']
        assert v['cause_hint']['file'] == 'agents/planner.md', v
        assert v['evidence'] == [{'path': f'{_ESC_TASK}/step-1/verifier-L1.md', 'line': 5}], v


@case('escalation: stale-running-marker fires on a dead owner_pid, not on a live one')
def _esc_stale_pid():
    import subprocess
    p = subprocess.Popen([sys.executable, '-c', 'pass'])
    p.wait()
    for pid, want in ((p.pid, 1), (os.getpid(), 0)):
        with tempfile.TemporaryDirectory() as tmp:
            repo = _esc_repo(tmp, {'step-1': [
                _e('builder-L2', 'run1', None, run=False, status='running', owner_pid=pid,
                   exit_code=None, finished_at=None)]},
                files={'step-1/builder-L2.running': '1790000000\n'})
            got = _esc_detect(repo, 'stale-running-marker')
            assert len(got) == want, (pid, got)
            if want:
                assert got[0]['evidence'] == [{'attempt_id': 'run1', 'owner_pid': pid}], got
            assert _esc_detect(repo, 'attempt-without-run-row') == [], 'a running attempt'


# --- plan ---------------------------------------------------------------------------------------

_STEP1 = f'{_ESC_TASK}/step-1'


def _plan_step_handoff(criterion, guard=None):
    return ('## Step 1: x\nlevel: L2\n### Do\nx\n### Acceptance criteria\n'
            f'- `{criterion}`\n' + (f'- (guard) scope: `{guard}`\n' if guard else ''))


def _plan_git_repo(tmp, criterion, guard=None):
    """A git repo whose step 1 passed, with README.md at base-sha and added.txt built after it."""
    _need_git()
    repo = _esc_repo(tmp, {'step-1': _esc_passed_step()},
                     files={'step-1/handoff.md': _plan_step_handoff(criterion, guard)})
    _write(repo, '.gitignore', '.sdlc/\n')
    _write(repo, 'README.md', 'base\n')
    _g(repo, 'init', '-q')
    _g(repo, 'add', '-A')
    _g(repo, 'commit', '-q', '-m', 'base')
    base = _g(repo, 'rev-parse', 'HEAD').strip()
    _write(repo, 'added.txt', 'built\n')
    _g(repo, 'add', '-A')
    _g(repo, 'commit', '-q', '-m', 'build')
    _write(repo, f'{_STEP1}/base-sha', base + '\n')
    return repo


def _plan_ingest(tmp, repo, flag, tag):
    """(findings of detector plan, aux) after an ingest of repo into a fresh out dir."""
    from . import ingest
    from .detectors import plan
    out = ingest.run(repo, out=os.path.join(tmp, f'out-{tag}'),
                     bench_dir=os.path.join(tmp, 'nobench'), rerun_criteria=flag)
    with open(os.path.join(out, 'events.jsonl'), encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    with open(os.path.join(out, 'aux.json'), encoding='utf-8') as f:
        aux = json.load(f)
    return plan.detect(rows, aux, None), aux


def _plan_detect(repo, detector):
    from .detectors import plan
    return [f for f in plan.detect(_esc_rows(repo), {'repo': repo}, None)
            if f['detector'] == detector]


def _plan_one(got, detector):
    assert len(got) == 1, f'{detector}: want 1 finding, got {len(got)}: {got}'
    f = got[0]
    assert f['family'] == 'plan' and f['layer'] == 'sdlc', f
    assert f['cause_hint']['file'], f
    return f


@case('plan: criteria-never-red fires')
def _plan_never_red_fires():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _plan_git_repo(tmp, 'test -f README.md')
        before = _g(repo, 'worktree', 'list', '--porcelain')
        got, aux = _plan_ingest(tmp, repo, True, 'on')
        after = _g(repo, 'worktree', 'list', '--porcelain')
        assert before == after, f'worktree list changed:\n{before}\n---\n{after}'
        recs = aux.get('criteria_reruns')
        assert isinstance(recs, list) and [r.get('exit_code') for r in recs] == [0], recs
        f = _plan_one([x for x in got if x['detector'] == 'criteria-never-red'],
                      'criteria-never-red')
        assert f['evidence'] == [{'path': f'{_STEP1}/handoff.md', 'line': 6}], f['evidence']
        assert f['cause_hint']['file'] == 'agents/planner.md', f
        got, aux = _plan_ingest(tmp, repo, False, 'off')
        assert 'criteria_reruns' not in aux, sorted(aux)
        assert [x for x in got if x['detector'] == 'criteria-never-red'] == [], got


@case('plan: criteria-never-red quiet on control')
def _plan_never_red_quiet():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _plan_git_repo(tmp, 'test -f added.txt', guard='test -f README.md')
        before = _g(repo, 'worktree', 'list', '--porcelain')
        got, aux = _plan_ingest(tmp, repo, True, 'on')
        assert _g(repo, 'worktree', 'list', '--porcelain') == before, 'worktree list changed'
        recs = aux.get('criteria_reruns')
        assert isinstance(recs, list) and [(r.get('span'), r.get('exit_code') != 0)
                                           for r in recs] == [('test -f added.txt', True)], recs
        got = [x for x in got if x['detector'] == 'criteria-never-red']
        assert got == [], f'criteria-never-red fired on the control: {got}'


def _fx_contract_dependents(tmp, defect):
    path = 'a/b.py' if defect else 'x/y.py'
    return _esc_repo(tmp, {
        'step-1': _esc_passed_step(),
        'step-2': [_e('builder-L2', 'c2b', _builder_text('done')),
                   _e('verifier-L1', 'c2v', _verifier_text(
                       'fail', f'criterion 1 is red: `{path}` lost its parse() export'))]})


def _ck_contract_dependents(f):
    assert f['evidence'] == [{'path': f'{_ESC_TASK}/step-2/verifier-L1.md', 'line': 5},
                             {'path': f'{_STEP1}/builder-L2.md', 'line': 6}], f['evidence']
    assert f['cause_hint']['file'] == 'agents/planner.md', f


def _blocked_text(note):
    return ('<!-- role=builder model=opus effort=high -->\n'
            f'{_hd("Status")}\nblocked\n\n{_hd("Changes")}\nNone\n\n{_hd("Checks")}\nnone\n\n'
            f'{_hd("Notes")}\n{note}\n')


def _fx_scope_prose(tmp, defect):
    handoff = _REVIEW + ('' if defect else '- scope widened: step 1: src/app.py\n')
    return _esc_repo(tmp, {'step-1': [
        _e('builder-L2', 'sp2', _blocked_text('needs `src/app.py`, outside the step scope')),
        _e('builder-L3', 'sp3', _blocked_text('still blocked: edit src/app.py, out of scope'))]},
        handoff=handoff)


def _ck_scope_prose(f):
    assert f['evidence'] == [{'path': f'{_STEP1}/builder-L2.md', 'line': 12},
                             {'path': f'{_STEP1}/builder-L3.md', 'line': 12}], f['evidence']
    assert f['cause_hint']['file'] == 'skills/chain/SKILL.md', f


_PLAN = (
    ('contract-dependents', _fx_contract_dependents, _ck_contract_dependents),
    ('scope-prose', _fx_scope_prose, _ck_scope_prose),
)


def _plan_fires(detector, build, check):
    with tempfile.TemporaryDirectory() as tmp:
        check(_plan_one(_plan_detect(build(tmp, True), detector), detector))


def _plan_quiet(detector, build):
    with tempfile.TemporaryDirectory() as tmp:
        got = _plan_detect(build(tmp, False), detector)
        assert got == [], f'{detector} fired on the control: {got}'


for _det, _build, _check in _PLAN:
    case(f'plan: {_det} fires')(lambda d=_det, b=_build, c=_check: _plan_fires(d, b, c))
    case(f'plan: {_det} quiet on control')(lambda d=_det, b=_build: _plan_quiet(d, b))


@case('plan: scope-prose quiet with a step ## Scope widened section, and on one blocked build')
def _plan_scope_step_section():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fx_scope_prose(tmp, True)
        _write(repo, f'{_STEP1}/handoff.md', f'# step\n\n{_hd("Scope widened")}\n- src/app.py\n')
        assert _plan_detect(repo, 'scope-prose') == [], 'fired despite ## Scope widened'
    with tempfile.TemporaryDirectory() as tmp:
        repo = _esc_repo(tmp, {'step-1': [
            _e('builder-L2', 'one', _blocked_text('needs `src/app.py`, outside the step scope'))]})
        assert _plan_detect(repo, 'scope-prose') == [], 'fired on a single blocked build'


def _ui_review(*gaps, findings_only=False):
    found = ''.join(f'- src/a.css:{i}: advisory: x: y. Rule: gap (proposed: "{g}")\n'
                    for i, g in enumerate(gaps, 1)) or 'None\n'
    listed = 'None\n' if findings_only or not gaps else ''.join(f'- {g}\n' for g in gaps)
    return (f'{_hd("Mode")}\nreview\n\n{_hd("Verdict")}\npass-with-notes\n\n'
            f'{_hd("Findings")}\n{found}\n{_hd("Guidance gaps")}\n{listed}')


_GAP = 'Every interactive state has a forced-colors style.'


def _gap_repo(root, texts):
    """A repo with one task dir per entry of texts, each with a ui-designer review result."""
    repo = os.path.join(root, 'repo')
    for n, text in enumerate(texts, 1):
        d = f'.sdlc/{n:04d}-ui'
        _write(repo, f'{d}/handoff.md', '# task\n')
        _write(repo, f'{d}/ui-designer-L1.attempt.json',
               json.dumps(_attempt('ui-designer-L1', f'u{n}')))
        _write(repo, f'{d}/ui-designer-L1.md', text)
        _write(repo, f'{d}/runs.jsonl', json.dumps(
            {'role': 'ui-designer', 'level': 'L1', 'file': 'ui-designer-L1.md',
             'attempt_id': f'u{n}', 'turns': 1, 'cost_usd': 0.1}) + '\n')
    return repo


@case('plan: guidance-gap fires on one proposed rule in three tickets')
def _plan_guidance_gap_fires():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _gap_repo(tmp, [_ui_review(_GAP, _GAP), _ui_review('  EVERY interactive  state has '
                                                                    'a forced-colors style'),
                               _ui_review(_GAP, findings_only=True)])
        got = _plan_detect(repo, 'guidance-gap')
        assert len(got) == 1, f'guidance-gap: want 1 finding, got {len(got)}: {got}'
        f = got[0]
        assert (f['family'], f['layer']) == ('plan', 'project'), f
        assert [e['path'] for e in f['evidence']] == [
            f'.sdlc/000{n}-ui/ui-designer-L1.md' for n in (1, 2, 3)], f['evidence']


@case('plan: guidance-gap quiet on two tickets')
def _plan_guidance_gap_quiet():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _gap_repo(tmp, [_ui_review(_GAP, _GAP), _ui_review(_GAP), _ui_review()])
        got = _plan_detect(repo, 'guidance-gap')
        assert got == [], f'guidance-gap fired on two tickets: {got}'


# --- hygiene ------------------------------------------------------------------------------------

_NEST = ('.worktrees', 'x', '.worktrees', 'tmp', 'builder-1')
_EXT_LINE = '- Lane `ext`: external branch `codex/work` at `' + 'f' * 40 + '`'
_NOWHERE = '/nowhere/lanes/integration'


def _hyg_point_integration(lanes, where):
    """Point the fixture report's Integration worktree line at where."""
    with open(os.path.join(lanes, 'report.md'), encoding='utf-8') as f:
        text = f.read()
    assert _NOWHERE in text, 'fixture report has no integration worktree line'
    _write(lanes, 'report.md', text.replace(_NOWHERE, where))


def _hyg_clean_repo(root):
    repo = os.path.join(root, 'repo')
    os.makedirs(repo)
    _g(repo, 'init', '-q')
    _write(repo, '.gitignore', '.worktrees/\n.sdlc/\n')
    _write(repo, 'README.md', 'clean\n')
    _g(repo, 'add', '-A')
    _g(repo, 'commit', '-q', '-m', 'fixture')
    _g(repo, 'branch', 'codex/work')
    return repo


@contextlib.contextmanager
def _hyg_fixture(defect, gone=False):
    """(root, repo, lanes). defect: the step 7 throwaway repo with its nested worktree, a reused
    ticket id, a registered external branch with no local branch, and the step 6 legacy lanes dir
    plus an unregistered external lane. Control: a clean repo (codex/work registered and present,
    two distinct ticket ids) and the step 6 prefixed lanes dir with its one mixed-id driver log
    (beta-T-0002.log, the stale-log-lines defect) rewritten to a single run id. The report's
    integration worktree is the repo, or with gone the fixture's missing /nowhere path."""
    _need_git()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.realpath(tmp)
        lanes = os.path.join(root, 'lanes')
        repo, added = None, []
        try:
            if defect:
                repo = _git_repo(root)
                wt = os.path.join(repo, *_NEST)
                _g(repo, 'worktree', 'add', '-q', '--detach', wt, 'HEAD')
                added.append(wt)
                _write(repo, '.sdlc/0001-a/handoff.md', _ticket('T-0001', 'ready'))
                _write(repo, '.sdlc/0002-b/handoff.md', _ticket('T-0001', 'ready'))
                _write(repo, '.sdlc/config', 'external_branch: feat/gone\n')
                _fanout_legacy_files(lanes, extra=[_EXT_LINE])
            else:
                repo = _hyg_clean_repo(root)
                _write(repo, '.sdlc/0001-a/handoff.md', _ticket('T-0001', 'ready'))
                _write(repo, '.sdlc/0002-b/handoff.md', _ticket('T-0002', 'ready'))
                _write(repo, '.sdlc/config', 'external_branch: codex/work\n')
                _fanout_prefixed_files(lanes)
                _write(lanes, 'logs/beta-T-0002.log', f'[{_R2}] new\n[{_R2}] more\n')
            if not gone:
                _hyg_point_integration(lanes, repo)
            yield root, repo, lanes
        finally:
            for wt in reversed(added):
                _g(repo, 'worktree', 'remove', '--force', wt)


def _hyg_detect(root, repo, lanes, tag='out'):
    """Every hygiene finding after an ingest of repo and lanes into a fresh out dir."""
    from . import ingest
    from .detectors import hygiene
    out = ingest.run(repo, lanes_dirs=[lanes], out=os.path.join(root, tag),
                     bench_dir=os.path.join(root, 'nobench'))
    with open(os.path.join(out, 'events.jsonl'), encoding='utf-8') as f:
        rows = [json.loads(line) for line in f if line.strip()]
    with open(os.path.join(out, 'aux.json'), encoding='utf-8') as f:
        aux = json.load(f)
    return hygiene.detect(rows, aux, None)


def _hyg_of(got, detector, n, cause):
    mine = [f for f in got if f['detector'] == detector]
    assert len(mine) == n, f'{detector}: want {n} findings, got {len(mine)}: {mine}'
    for f in mine:
        assert f['family'] == 'hygiene' and f['layer'] == 'sdlc', f
        assert f['cause_hint']['file'] == cause, f
    return sorted(mine, key=lambda f: json.dumps(f['evidence'], sort_keys=True))


def _hyg_line(path, needle):
    with open(path, encoding='utf-8') as f:
        return next(i for i, line in enumerate(f.read().splitlines(), 1) if needle in line)


def _ck_stray_worktree(got, repo, lanes):
    f, = _hyg_of(got, 'stray-worktree', 1, 'scripts/run.sh')
    assert f['evidence'] == [{'path': '/'.join(_NEST), 'line': None}], f['evidence']


def _ck_tracked_runtime_file(got, repo, lanes):
    fs = _hyg_of(got, 'tracked-runtime-file', 2, 'skills/handoff-format/SKILL.md')
    assert [f['evidence'] for f in fs] == [[{'path': 'foo.log', 'line': None}],
                                           [{'path': 'step-1/builder-L2.running', 'line': None}]], fs


def _ck_integration_reset(got, repo, lanes):
    f, = _hyg_of(got, 'integration-reset', 1, 'scripts/fanout.py')
    assert f['severity'] == 3, f
    reflog, lane = f['evidence']
    assert reflog['path'] == '.' and reflog['reflog'].endswith(' reset: moving to HEAD~1'), reflog
    report = os.path.join(lanes, 'report.md')
    assert lane == {'path': report, 'line': _hyg_line(report, 'red: test ! -e RED rc=1')}, lane
    _hyg_of(got, 'reflog-gone', 0, 'scripts/fanout.py')


def _ck_stale_log_lines(got, repo, lanes):
    fs = _hyg_of(got, 'stale-log-lines', 2, 'scripts/fanout.py')
    logs = os.path.join(lanes, 'logs')
    assert [f['evidence'] for f in fs] == [
        [{'path': os.path.join(logs, 'alpha-T-0001.log'), 'line': None}],
        [{'path': os.path.join(logs, 'gate-alpha-T-0001-1.log'), 'line': None}]], fs
    assert [f['severity'] for f in fs] == [1, 1], fs


def _ck_overwritten_gate_log(got, repo, lanes):
    f, = _hyg_of(got, 'overwritten-gate-log', 1, 'scripts/fanout.py')
    assert f['severity'] == 1, f
    assert f['evidence'] == [{'path': os.path.join(lanes, 'logs', 'gate-alpha-T-0001-1.log'),
                              'line': None}], f['evidence']


def _ck_ticket_id_collision(got, repo, lanes):
    f, = _hyg_of(got, 'ticket-id-collision', 1, 'scripts/tickets.py')
    e, = f['evidence']
    assert e['path'] == '.sdlc' and 'duplicate id T-0001' in e['problem'], e


def _ck_unregistered_external_branch(got, repo, lanes):
    fs = _hyg_of(got, 'unregistered-external-branch', 2, 'scripts/tickets.py')
    report = os.path.join(lanes, 'report.md')
    assert [f['evidence'] for f in fs] == [
        [{'path': report, 'line': _hyg_line(report, 'external branch `codex/work`'),
          'branch': 'codex/work'}],
        [{'path': '.sdlc/config', 'line': 1, 'branch': 'feat/gone'}]], fs


_HYG = (
    ('stray-worktree', _ck_stray_worktree),
    ('tracked-runtime-file', _ck_tracked_runtime_file),
    ('integration-reset', _ck_integration_reset),
    ('stale-log-lines', _ck_stale_log_lines),
    ('overwritten-gate-log', _ck_overwritten_gate_log),
    ('ticket-id-collision', _ck_ticket_id_collision),
    ('unregistered-external-branch', _ck_unregistered_external_branch),
)


def _hyg_fires(check):
    with _hyg_fixture(True) as (root, repo, lanes):
        check(_hyg_detect(root, repo, lanes), repo, lanes)


def _hyg_quiet(detector):
    with _hyg_fixture(False) as (root, repo, lanes):
        got = [f for f in _hyg_detect(root, repo, lanes) if f['detector'] == detector]
        assert got == [], f'{detector} fired on the control: {got}'


for _det, _check in _HYG:
    case(f'hygiene: {_det} fires')(lambda c=_check: _hyg_fires(c))
    case(f'hygiene: {_det} quiet on control')(lambda d=_det: _hyg_quiet(d))


@case('hygiene: the clean control fires no finding of any hygiene detector')
def _hyg_control_empty():
    with _hyg_fixture(False) as (root, repo, lanes):
        got = _hyg_detect(root, repo, lanes)
        assert got == [], f'the control fired: {got}'


@case('hygiene: reflog-gone (severity 1) replaces integration-reset when the worktree is gone')
def _hyg_reflog_gone():
    with _hyg_fixture(True, gone=True) as (root, repo, lanes):
        got = _hyg_detect(root, repo, lanes)
        _hyg_of(got, 'integration-reset', 0, 'scripts/fanout.py')
        f, = _hyg_of(got, 'reflog-gone', 1, 'scripts/fanout.py')
        assert f['severity'] == 1, f
        report = os.path.join(lanes, 'report.md')
        assert f['evidence'] == [
            {'path': report, 'line': _hyg_line(report, '- Integration worktree:'),
             'worktree': _NOWHERE},
            {'path': report, 'line': _hyg_line(report, 'red: test ! -e RED rc=1')}], f['evidence']


@case('hygiene: integration-reset needs a reset and a lost-edit signal together')
def _hyg_reset_pairing():
    with _hyg_fixture(False) as (root, repo, lanes):
        _g(repo, 'commit', '-q', '--allow-empty', '-m', 'scratch')
        _g(repo, 'reset', '-q', '--hard', 'HEAD~1')
        # the control lanes dir has red outcomes: with a reset now in the reflog, it fires
        f, = _hyg_of(_hyg_detect(root, repo, lanes, 'out-1'), 'integration-reset', 1,
                     'scripts/fanout.py')
        report = os.path.join(lanes, 'report.md')
        assert f['evidence'][1] == {'path': report,
                                    'line': _hyg_line(report, 'red: true \\| false rc=1')}, f
        # a lanes dir with only merged outcomes and no fanout.log is no signal, reset or not
        quiet = os.path.join(root, 'quiet')
        _write(quiet, 'report.md', _fanout_report(f'- Run: `{_R2}`', ['true'], [], [
            '| alpha | T-0001 | merged | abc1234 |']))
        _hyg_point_integration(quiet, repo)
        _hyg_of(_hyg_detect(root, repo, quiet, 'out-2'), 'integration-reset', 0,
                'scripts/fanout.py')


@case('hygiene: stale-log-lines on mixed run ids is severity 2 at the first line of the second id')
def _hyg_mixed_ids():
    from .detectors import hygiene
    from .sources import fanout
    with tempfile.TemporaryDirectory() as lanes:
        _fanout_prefixed_files(lanes)
        got = hygiene.detect([], {'repo': os.path.join(lanes, 'repo'),
                                  'lanes': [fanout.read(lanes)]}, None)
        f, = _hyg_of(got, 'stale-log-lines', 1, 'scripts/fanout.py')
        assert f['severity'] == 2, f
        assert f['evidence'] == [{'path': os.path.join(lanes, 'logs', 'beta-T-0002.log'),
                                  'line': 2}], f['evidence']


@case('hygiene: tracked evidence logs, landed or lane-recorded fanout lanes, and a kept worktree '
      'are no findings (T-0730)')
def _hyg_t0730_known():
    """Issue #53/#66 repro: a land-written `external branch ... at None` line (its branch in
    logs/land.jsonl), a lane whose worktree holds .lane.json, a tracked docs/evidence/*.log, and a
    preview worktree under .worktrees/tmp/ holding the keep marker. A tracked foo.log and an
    unregistered external lane with neither record still fire."""
    _need_git()
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.realpath(tmp)
        repo, lanes, added = _hyg_clean_repo(root), os.path.join(root, 'lanes'), []
        try:
            _write(repo, 'docs/evidence/run.stdout.log', 'kept\n')
            _write(repo, 'foo.log', 'stray\n')
            _g(repo, 'add', '-A')
            _g(repo, 'commit', '-q', '-m', 'evidence')
            for b in ('fanout/l-a', 'fanout/l-b', 'codex/other'):
                _g(repo, 'branch', b)
            preview = os.path.join(repo, '.worktrees', 'tmp', 'preview')
            lane_b = os.path.join(root, 'repo.worktrees', 'l-b')
            _g(repo, 'worktree', 'add', '-q', '--detach', preview, 'HEAD')
            added.append(preview)
            _g(repo, 'worktree', 'add', '-q', lane_b, 'fanout/l-b')
            added.append(lane_b)
            _write(preview, '.sdlc-keep', '')
            _write(lane_b, '.lane.json', '{}\n')
            _write(repo, '.sdlc/config', 'external_branch: codex/work\n')
            _write(lanes, 'report.md', _fanout_report(
                f'- Run: `{_R2}`', [],
                ['- Lane `t-0001-solo`: external branch `fanout/l-a` at `None`',
                 '- Lane `l-b`: external branch `fanout/l-b` at `' + 'e' * 40 + '`',
                 '- Lane `other`: external branch `codex/other` at `' + 'd' * 40 + '`'],
                ['| t-0001-solo | T-0001 | merged | abc1234 |']))
            _write(lanes, 'logs/land.jsonl', json.dumps({'lane': 't-0001-solo', 'branch': 'fanout/l-a',
                                                         'ticket': 'T-0001'}) + '\n')
            got = _hyg_detect(root, repo, lanes)
            assert [f['evidence'][0]['branch'] for f in got
                    if f['detector'] == 'unregistered-external-branch'] == ['codex/other'], got
            assert [f['evidence'][0]['path'] for f in got
                    if f['detector'] == 'tracked-runtime-file'] == ['foo.log'], got
            assert [f for f in got if f['detector'] == 'stray-worktree'] == [], got
        finally:
            for wt in reversed(added):
                _g(repo, 'worktree', 'remove', '--force', wt)


# --- cost ---------------------------------------------------------------------------------------

_T0 = '2026-09-30T06:00:00+00:00'


def _cost_log(cmds=(), gap=30, denials=(), rate_limits=0):
    """A stream-json log: one Bash call per command, gap seconds apart from _T0, then denials."""
    import datetime
    t0 = datetime.datetime.fromisoformat(_T0)
    ev = []
    for i, c in enumerate(cmds):
        ts = (t0 + datetime.timedelta(seconds=i * gap)).isoformat().replace('+00:00', 'Z')
        ev.append({'type': 'assistant', 'timestamp': ts, 'message': {'content': [
            {'type': 'tool_use', 'name': 'Bash', 'input': {'command': c}}]}})
    for stderr in denials:
        ev.append({'type': 'system', 'subtype': 'hook_response', 'hook_name': 'PreToolUse',
                   'exit_code': 2, 'stderr': stderr})
    ev += [{'type': 'rate_limit_event'}] * rate_limits
    ev.append({'type': 'result', 'total_cost_usd': 0.1, 'duration_ms': 1, 'num_turns': 1})
    return ''.join(json.dumps(e) + '\n' for e in ev)


def _cost_repo(tmp, entries, costs=None, logs=None):
    """One step-1 dir of entries; costs {attempt id: cost_usd}; logs {result name: log text}."""
    repo = _esc_repo(tmp, {'step-1': entries},
                     files={f'step-1/{n}.log': t for n, t in (logs or {}).items()})
    if costs:
        p = os.path.join(repo, _ESC_TASK, 'step-1', 'runs.jsonl')
        with open(p, encoding='utf-8') as f:
            recs = [json.loads(line) for line in f.read().splitlines()]
        for r in recs:
            r['cost_usd'] = costs.get(r['attempt_id'], r['cost_usd'])
        _write(repo, f'{_ESC_TASK}/step-1/runs.jsonl', ''.join(json.dumps(r) + '\n' for r in recs))
    return repo


def _cost_detect(repo, detector, aux=None):
    from .detectors import cost
    a = {'repo': repo, 'baseline': {'median_cost_per_passed_step': 2.0}}
    a.update(aux or {})
    got, notes = cost.detect(_esc_rows(repo), a, None)
    return [f for f in got if f['detector'] == detector], notes


def _cost_one(got, detector):
    assert len(got) == 1, f'{detector}: want 1 finding, got {len(got)}: {got}'
    f = got[0]
    assert f['family'] == 'cost', f
    assert all('attempt_id' in e for e in f['evidence']), f
    return f


def _fx_cost_over_baseline(tmp, defect):
    costs = {'cb': 2.5, 'cv': 3.5} if defect else {'cb': 1.0, 'cv': 1.0}
    return _cost_repo(tmp, [_e('builder-L2', 'cb', _builder_text('done')),
                            _e('verifier-L1', 'cv', _verifier_text('pass'))], costs=costs)


def _ck_cost_over_baseline(f):
    assert f['evidence'][0]['ratio'] == 3.0, f['evidence']
    assert [e['attempt_id'] for e in f['evidence']] == ['cb', 'cv'], f['evidence']
    assert f['cause_hint']['file'] == 'skills/level-rubric/SKILL.md', f
    assert f['layer'] == 'sdlc', f


def _fx_many_builder_attempts(tmp, defect):
    entries = [_e('builder-L2', 'm1', _builder_text('blocked')),
               _e('builder-L3', 'm2', _builder_text('blocked' if defect else 'done'))]
    if defect:
        entries.append(_e('builder-L4', 'm3', _builder_text('done')))
    return _cost_repo(tmp, entries)


def _ck_many_builder_attempts(f):
    assert [e['attempt_id'] for e in f['evidence']] == ['m1', 'm2', 'm3'], f['evidence']
    assert f['cause_hint']['file'] == 'skills/level-rubric/SKILL.md', f


def _polling_cmds(defect):
    return ['sleep  30'] * 3 + ['sleep 30'] * 3 if defect else [f'echo {i}' for i in range(6)]


def _fx_polling_loop(tmp, defect):
    return _cost_repo(tmp, [_e('builder-L2', 'pl', _builder_text('done'))],
                      logs={'builder-L2': _cost_log(_polling_cmds(defect))})


def _ck_polling_loop(f):
    assert f['evidence'] == [{'attempt_id': 'pl', 'calls': 6, 'secs': 150.0,
                              'load': 'unknown'}], f['evidence']
    assert f['cause_hint']['file'] == 'agents/factory.md', f


def _fx_background_denial(tmp, defect):
    stderr = ('blocked: run_in_background is not allowed in a role run' if defect
              else 'blocked: publishing is not allowed in a role run')
    return _cost_repo(tmp, [_e('builder-L2', 'bd', _builder_text('done'))],
                      logs={'builder-L2': _cost_log(denials=[stderr])})


def _ck_background_denial(f):
    assert f['evidence'] == [{'attempt_id': 'bd', 'count': 1}], f['evidence']
    assert f['cause_hint']['file'] == 'hooks/block-background.sh', f


def _fx_rate_limit(tmp, defect):
    return _cost_repo(tmp, [_e('builder-L2', 'rl', _builder_text('done'))],
                      logs={'builder-L2': _cost_log(['echo hi'], rate_limits=2 if defect else 0)})


def _ck_rate_limit(f):
    assert f['evidence'] == [{'attempt_id': 'rl', 'count': 2}], f['evidence']
    assert f['layer'] == 'host' and f['cause_hint']['file'] is None, f


_COST = (
    ('cost-over-baseline', _fx_cost_over_baseline, _ck_cost_over_baseline),
    ('many-builder-attempts', _fx_many_builder_attempts, _ck_many_builder_attempts),
    ('polling-loop', _fx_polling_loop, _ck_polling_loop),
    ('background-denial', _fx_background_denial, _ck_background_denial),
    ('rate-limit', _fx_rate_limit, _ck_rate_limit),
)


def _cost_fires(detector, build, check):
    with tempfile.TemporaryDirectory() as tmp:
        got, notes = _cost_detect(build(tmp, True), detector)
        check(_cost_one(got, detector))
        assert notes == [], notes


def _cost_quiet(detector, build):
    with tempfile.TemporaryDirectory() as tmp:
        got, notes = _cost_detect(build(tmp, False), detector)
        assert got == [], f'{detector} fired on the control: {got}'
        assert notes == [], notes


for _det, _build, _check in _COST:
    case(f'cost: {_det} fires')(lambda d=_det, b=_build, c=_check: _cost_fires(d, b, c))
    case(f'cost: {_det} quiet on control')(lambda d=_det, b=_build: _cost_quiet(d, b))


@case('cost: a None baseline gives the note "cost-over-baseline: no baseline" and no finding')
def _cost_no_baseline():
    from .detectors import cost
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fx_cost_over_baseline(tmp, True)
        got, notes = cost.detect(_esc_rows(repo), {'repo': repo, 'baseline': {
            'median_cost_per_passed_step': None, 'steps': [], 'hidden': {}}}, None)
        assert [f for f in got if f['detector'] == 'cost-over-baseline'] == [], got
        assert notes == ['cost-over-baseline: no baseline'], notes


@case('cost: cost-over-baseline skips a step whose newest verifier failed')
def _cost_failed_step():
    with tempfile.TemporaryDirectory() as tmp:
        repo = _cost_repo(tmp, [_e('builder-L2', 'fb', _builder_text('done')),
                                _e('verifier-L1', 'fv', _verifier_text('pass')),
                                _e('verifier-L2', 'fv2', _verifier_text('fail'))],
                          costs={'fb': 9.0, 'fv': 9.0, 'fv2': 9.0})
        got, _ = _cost_detect(repo, 'cost-over-baseline')
        assert got == [], got


@case('cost: polling-loop carries the load series value nearest the first call, via ingest')
def _cost_load_series():
    from . import ingest
    from .detectors import cost
    with tempfile.TemporaryDirectory() as tmp:
        repo = _fx_polling_loop(tmp, True)
        series = os.path.join(tmp, 'load.json')
        _write(tmp, 'load.json', json.dumps([
            ['2026-09-30T05:50:00+00:00', 9.9], ['2026-09-30T06:00:04Z', 4.2], ['bad', 1],
            ['2026-09-30T06:00:01Z', 'high'], ['2026-09-30T06:06:40+00:00', 1.0]]))
        out = ingest.run(repo, out=os.path.join(tmp, 'out'), bench_dir=os.path.join(tmp, 'nb'),
                         load_series=series)
        with open(os.path.join(out, 'aux.json'), encoding='utf-8') as f:
            aux = json.load(f)
        with open(os.path.join(out, 'events.jsonl'), encoding='utf-8') as f:
            rows = [json.loads(line) for line in f.read().splitlines()]
        assert len(aux['load_series']) == 4, aux['load_series']  # 'high' is dropped
        got, notes = cost.detect(rows, aux, None)
        f, = [x for x in got if x['detector'] == 'polling-loop']
        assert f['evidence'] == [{'attempt_id': 'pl', 'calls': 6, 'secs': 150.0,
                                  'load': 4.2}], f['evidence']
        assert notes == ['cost-over-baseline: no baseline'], notes


@case('cost: polling-loop counts polling-pattern calls that differ in text')
def _cost_poll_pattern():
    cmds = ['sleep 5', 'kill -0 123', 'ls .sdlc/t/step-1/*.running', 'sleep 10',
            'test -e .sdlc/t/step-1/builder-L2.running', 'git status']
    with tempfile.TemporaryDirectory() as tmp:
        repo = _cost_repo(tmp, [_e('builder-L2', 'pp', _builder_text('done'))],
                          logs={'builder-L2': _cost_log(cmds, gap=10)})
        f = _cost_one(_cost_detect(repo, 'polling-loop')[0], 'polling-loop')
        assert f['evidence'] == [{'attempt_id': 'pp', 'calls': 5, 'secs': 40.0,
                                  'load': 'unknown'}], f['evidence']
    with tempfile.TemporaryDirectory() as tmp:
        repo = _cost_repo(tmp, [_e('builder-L2', 'pp', _builder_text('done'))],
                          logs={'builder-L2': _cost_log(cmds[:4] + ['git status'] * 2)})
        assert _cost_detect(repo, 'polling-loop')[0] == [], 'four polls fired'


def _session(turns):
    """A factory session .jsonl: turns are (fired, [(tool name, command, result text)])."""
    ev = []
    for i, (fired, calls) in enumerate(turns):
        prompt = {'type': 'user', 'promptId': f'p{i}', 'message': {'content': 'check the wave'}}
        if fired:
            prompt['scheduledTaskId'] = 'loop-1'
        ev.append(prompt)
        for j, (name, cmd, text) in enumerate(calls):
            tid = f't{i}-{j}'
            ev.append({'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': tid, 'name': name, 'input': {'command': cmd}}]}})
            ev.append({'type': 'user', 'promptId': f'p{i}', 'message': {'content': [
                {'type': 'tool_result', 'tool_use_id': tid, 'content': text}]}})
    return ''.join(json.dumps(e) + '\n' for e in ev)


@case('cost: idle-wakes fires on two unchanged fired turns and is silent when a turn dispatches')
def _cost_idle_wakes():
    from .detectors import cost
    board = ('Bash', 'python3 scripts/board.py --summary', '3 running, 0 done')
    idle = [(False, [board]), (True, [board]), (True, [board]), (True, [])]
    with tempfile.TemporaryDirectory() as tmp:
        _write(tmp, 'idle.jsonl', _session(idle))
        _write(tmp, 'acts.jsonl', _session(
            idle[:2] + [(True, [board, ('Bash', 'python3 scripts/dispatch.py prepare solo L2 t', '{}')])]))
        _write(tmp, 'moved.jsonl', _session(
            idle[:2] + [(True, [('Bash', 'python3 scripts/board.py --summary', '2 running, 1 done')])]))
        aux = {'repo': tmp, 'factory_transcripts': ['idle.jsonl', 'acts.jsonl', 'moved.jsonl']}
        got = [f for f in cost.detect([], aux, None)[0] if f['detector'] == 'idle-wakes']
        assert len(got) == 1, got
        f = got[0]
        assert f['evidence'] == [{'path': 'idle.jsonl', 'line': 4}, {'path': 'idle.jsonl', 'line': 7},
                                 {'path': 'idle.jsonl', 'line': 10}], f['evidence']
        assert f['cause_hint']['file'] == 'skills/plan-loop/references/loop-rules.md', f
        assert cost.detect([], {'repo': tmp}, None)[0] == [], 'fired with no factory transcript'


# --- corpus regression ------------------------------------------------------------------------

_CORPUS = '.sdlc/.0109-make-the-fixed-count-lint'
# Three closed tickets' run records as they stood at 51cbf1ba, before T-0571 trimmed closed folders
# to handoff.md; the case copies them into a throwaway repo as its .sdlc.
_CORPUS_FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'corpus-sdlc')


def _toplevel():
    import subprocess
    p = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True,
                       cwd=os.path.dirname(os.path.abspath(__file__)))
    return p.stdout.strip() if p.returncode == 0 else None


def _corpus_run_rows(top, rows, rel, rec):
    """The rows of handoff dir rel that the runs.jsonl record rec joins (table.join's rules)."""
    runs_src = f'{rel}/runs.jsonl'
    here = [r for r in rows if runs_src in (r.get('sources') or [])]
    from . import store
    aid, file = rec.get('attempt_id'), rec.get('file')
    if aid:
        hit = [r for r in here if r['attempt_id'] == aid]
        if hit:
            return hit
    if file:
        hit = [r for r in here if r['attempt_id'] == f'legacy:{rel}/{file}'
               or (not str(r['attempt_id']).startswith('legacy:')
                   and store.attempt_name(r) + '.md' == file)]
        if hit:
            return hit
    return [r for r in here if r['attempt_id'] == f'legacy:{rel}/runs.jsonl#{rec["index"]}']


@case('corpus: three closed tickets\' .sdlc traces ingest whole and give the known findings')
def _corpus():
    import shutil
    real_top = _toplevel()
    logs = os.path.join(real_top or '', '.worktrees/fanout-night/logs')
    lanes = [os.path.dirname(logs)] if real_top and os.path.isdir(logs) else []
    with tempfile.TemporaryDirectory() as top:
        shutil.copytree(_CORPUS_FIXTURE, os.path.join(top, '.sdlc'))
        _corpus_in(top, lanes)


def _corpus_in(top, lanes):
    from . import ingest, store
    from .detectors import cost, escalation, hygiene, plan
    from .sources import runs
    with tempfile.TemporaryDirectory() as tmp:
        out = ingest.run(top, lanes_dirs=lanes, out=tmp, bench_dir=os.path.join(tmp, 'nb'))
        with open(os.path.join(out, store.EVENTS), encoding='utf-8') as f:
            rows = [json.loads(line) for line in f if line.strip()]
        with open(os.path.join(out, store.AUX), encoding='utf-8') as f:
            aux = json.load(f)
    sources = {s for r in rows for s in (r.get('sources') or [])}
    sdlc = os.path.join(top, '.sdlc')
    missing, bad_runs = [], []
    for d, _, files in os.walk(sdlc):
        rel = os.path.relpath(d, top).replace(os.sep, '/')
        for n in files:
            if n.endswith('.attempt.json') and f'{rel}/{n}' not in sources:
                missing.append(f'{rel}/{n}')
        walked = {rec for _t, rec, _f in ingest.records_tasks(top)}   # the records dirs ingest reads
        walked |= {f'{w}/{s}' for w in list(walked)
                   for s in ingest.step_dirs(os.path.join(top, w))}
        if 'runs.jsonl' in files and rel in walked:  # the handoff dirs ingest reads
            for rec in runs.read(d)[0]:
                got = _corpus_run_rows(top, rows, rel, rec)
                if len(got) != 1:
                    bad_runs.append(f'{rel}/runs.jsonl#{rec["index"]}: {len(got)} rows')
    assert not missing, f'attempts in no row: {missing[:5]} ({len(missing)})'
    assert not bad_runs, f'run lines not mapping to one row: {bad_runs[:5]} ({len(bad_runs)})'
    found, _ = cost.detect(rows, aux)
    found = list(found)
    for fam in (escalation, plan, hygiene):
        found.extend(fam.detect(rows, aux))

    def has(detector, **ev):
        return any(f['detector'] == detector and any(all(e.get(k) == v for k, v in ev.items())
                                                     for e in f['evidence']) for f in found)
    want = [('plan-defect-refusal', {'path': f'{_CORPUS}/handoff.md'}),
            ('plan-defect-refusal',
             {'path': '.sdlc/.0134-mirror-the-extended-planner-rules/step-1/verifier-L1.md'}),
            ('replan-loop',
             {'path': '.sdlc/.0113-close-rename-breaks-refs/step-2.superseded-1/builder-L2.md'})]
    if lanes:
        want.append(('overwritten-gate-log', {}))
    else:
        print('skip: corpus: overwritten-gate-log: .worktrees/fanout-night/logs is absent')
    for det, ev in want:
        if det == 'overwritten-gate-log':
            ok = any(f['detector'] == det and 'gate-steps-T-0148-1.log' in json.dumps(f)
                     for f in found)
        else:
            ok = has(det, **ev)
        assert ok, f'no {det} finding with evidence {ev}'


def _records_rows(repo, out):
    from . import ingest, store
    ingest.run(repo, out=out, bench_dir=os.path.join(out, 'nb'))
    with open(os.path.join(out, store.EVENTS), encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def _records_step(repo, d, aid, cost):
    _write(repo, f'{d}/builder-L2.attempt.json', json.dumps(_attempt('builder-L2', aid)))
    _write(repo, f'{d}/runs.jsonl', json.dumps({'attempt_id': aid, 'role': 'builder', 'level': 'L2',
                                                'cost_usd': cost, 'file': 'builder-L2.md'}) + '\n')
    _write(repo, f'{d}/builder-L2.md', '## Status\ndone\n')


@case('records dir: runtime-only fixture: a task folder with records only in runtime/tasks ingests '
      'priced rows under the folder ticket')
def _():
    from .sources import bench
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as out:
        _write(repo, '.sdlc/.0001-a/handoff.md', _TICKET_FM)
        _records_step(repo, '.sdlc/runtime/tasks/0001-a/step-1', 'r1', 1.5)
        _write(repo, '.sdlc/runtime/tasks/0009-z/runs.jsonl',
               json.dumps({'role': 'solo', 'level': 'L2', 'cost_usd': 2.0}) + '\n')
        rows = _records_rows(repo, out)
        got = [r for r in rows if r['attempt_id'] == 'r1']
        assert len(got) == 1, rows
        r = got[0]
        assert r['ticket'] == 'T-0001' and r['cost_usd'] == 1.5 and r['step'] == 1, r
        assert r['task_dir'] == '.sdlc/.0001-a', r['task_dir']
        assert r['sources'] and all(s.startswith('.sdlc/runtime/tasks/0001-a/step-1/') for s in r['sources']), r
        orphan = [r for r in rows if r['role'] == 'solo']
        assert len(orphan) == 1 and orphan[0]['ticket'] is None \
            and orphan[0]['task_dir'] == '.sdlc/runtime/tasks/0009-z', orphan
        # a new runtime record invalidates the cursor: the task fingerprint covers the records dir
        _write(repo, '.sdlc/runtime/tasks/0001-a/runs.jsonl',
               json.dumps({'role': 'planner', 'level': 'L3', 'cost_usd': 0.5}) + '\n')
        again = _records_rows(repo, out)
        assert any(r['role'] == 'planner' and r['ticket'] == 'T-0001' for r in again), again
        # bench: a result dir's step dirs come from results/runtime/tasks/<run>
        _write(repo, 'bench/results/run1/grade.md', '# grade\nhidden_check: pass\n')
        _bench_step(repo, 'bench/results/runtime/tasks/run1/step-1', 'pass', 4.0)
        b = bench.baseline(os.path.join(repo, 'bench'))
        assert b['steps'] == [(os.path.join(repo, 'bench', 'results', 'run1'), 1, 4.0)], b


@case('records dir: legacy fixture: a closed folder holding its records in place ingests as before')
def _():
    from .sources import bench
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as out:
        _write(repo, '.sdlc/.0001-a/handoff.md', _TICKET_FM)
        _records_step(repo, '.sdlc/.0001-a/step-1', 'r1', 1.5)
        rows = _records_rows(repo, out)
        assert [r['attempt_id'] for r in rows] == ['r1'], rows
        r = rows[0]
        assert r['ticket'] == 'T-0001' and r['cost_usd'] == 1.5 and r['task_dir'] == '.sdlc/.0001-a', r
        assert all(s.startswith('.sdlc/.0001-a/step-1/') for s in r['sources']), r
        assert not os.path.exists(os.path.join(repo, '.sdlc', 'runtime')), 'ingest created a records dir'
        _bench_step(repo, 'bench/results/run1/step-1', 'pass', 4.0)
        b = bench.baseline(os.path.join(repo, 'bench'))
        assert b['steps'] == [(os.path.join(repo, 'bench', 'results', 'run1'), 1, 4.0)], b


_TICKET_FM = ('---\nid: T-0001\ntitle: "A"\ntype: feature\nstatus: ready\nsize: S\npriority: P2\n'
              'depends: []\ncreated: 2026-09-30\n---\n')


@case('tickets: task_dirs lists tickets/<name> and root tasks under ticket_root: tickets')
def _():
    from . import ingest
    with tempfile.TemporaryDirectory() as repo:
        _write(repo, '.sdlc/config', 'ticket_root: tickets\n')
        _write(repo, '.sdlc/tickets/0001-a/handoff.md', _TICKET_FM)
        _write(repo, '.sdlc/side/handoff.md', '## Goal\nx\n')
        got = ingest.task_dirs(os.path.join(repo, '.sdlc'))
        assert got == ['side', 'tickets/0001-a'], got


@case('tickets: by_slug comes from the tickets/ dir under ticket_root: tickets')
def _():
    from .sources import tickets as reader
    with tempfile.TemporaryDirectory() as repo:
        _write(repo, '.sdlc/config', 'ticket_root: tickets\n')
        _write(repo, '.sdlc/tickets/0001-a/handoff.md', _TICKET_FM)
        got = reader.read(os.path.join(repo, '.sdlc'))['by_slug']
        assert got == {'0001-a': ('T-0001', 'ready')}, got


@case('tickets: layout: topics lists tickets/<name> and work/<name>, and work and notes are not tasks')
def _():
    from . import ingest
    with tempfile.TemporaryDirectory() as repo:
        _write(repo, '.sdlc/config', 'ticket_root: tickets\nlayout: topics\n')
        _write(repo, '.sdlc/tickets/0001-a/handoff.md', _TICKET_FM)
        _write(repo, '.sdlc/work/w1/handoff.md', '## Goal\nx\n')
        _write(repo, '.sdlc/notes/notes.md', 'n\n')
        _write(repo, '.sdlc/side/handoff.md', '## Goal\nx\n')
        got = ingest.task_dirs(os.path.join(repo, '.sdlc'))
        assert got == ['side', 'tickets/0001-a', 'work/w1'], got
        # Negative controls: without the layout line work and notes are plain dir names, and an
        # unsupported layout value falls back to the ticket_root listing without failing.
        _write(repo, '.sdlc/config', 'ticket_root: tickets\n')
        got = ingest.task_dirs(os.path.join(repo, '.sdlc'))
        assert got == ['notes', 'side', 'work', 'tickets/0001-a'], got
        _write(repo, '.sdlc/config', 'ticket_root: tickets\nlayout: nested\n')
        got = ingest.task_dirs(os.path.join(repo, '.sdlc'))
        assert got == ['notes', 'side', 'work', 'tickets/0001-a'], got


@case('tickets: layout: topics reads the notes file from notes/notes.md, not the root')
def _():
    from .sources import tickets as reader
    with tempfile.TemporaryDirectory() as repo:
        sdlc = os.path.join(repo, '.sdlc')
        _write(repo, '.sdlc/config', 'ticket_root: tickets\nlayout: topics\n')
        _write(repo, '.sdlc/tickets/0001-a/handoff.md', _TICKET_FM)
        assert reader.read(sdlc)['notes'] is False
        _write(repo, '.sdlc/notes.md', 'root notes\n')
        assert reader.read(sdlc)['notes'] is False, 'a root notes.md is not the topics notes file'
        _write(repo, '.sdlc/notes/notes.md', 'n\n')
        assert reader.read(sdlc)['notes'] is True
        _write(repo, '.sdlc/config', 'ticket_root: tickets\n')
        os.remove(os.path.join(sdlc, 'notes.md'))
        assert reader.read(sdlc)['notes'] is False, 'flat layout ignores notes/notes.md'


@case('tickets: ingest run on a layout: topics repo reads a work/ task into rows')
def _():
    from . import ingest
    with tempfile.TemporaryDirectory() as repo, tempfile.TemporaryDirectory() as out:
        _write(repo, '.sdlc/config', 'ticket_root: tickets\nlayout: topics\n')
        _write(repo, '.sdlc/work/w1/handoff.md', '## Goal\nx\n')
        _write(repo, '.sdlc/work/w1/runs.jsonl',
               json.dumps({'role': 'planner', 'level': 'L1', 'model': 'm', 'exit': 0,
                           'started': '2026-10-01T00:00:00Z', 'ended': '2026-10-01T00:01:00Z'}) + '\n')
        ingest.run(repo, out=out)
        cursor = json.load(open(os.path.join(out, 'cursor.json')))
        keys = sorted(cursor['keys'])
        assert '.sdlc/work/w1' in keys and '.sdlc/work' not in keys, keys


@case('tickets: with no ticket_root line a tickets dir is a plain task dir name')
def _():
    from . import ingest
    with tempfile.TemporaryDirectory() as repo:
        _write(repo, '.sdlc/config', '# no ticket_root\n')
        _write(repo, '.sdlc/tickets/0001-a/handoff.md', _TICKET_FM)
        _write(repo, '.sdlc/side/handoff.md', '## Goal\nx\n')
        got = ingest.task_dirs(os.path.join(repo, '.sdlc'))
        assert got == ['side', 'tickets'], got
