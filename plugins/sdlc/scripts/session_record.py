#!/usr/bin/env python3
"""Append one row per Claude Code session to `.sdlc/runtime/sessions.jsonl`, so a retro can compare modes (T-0817).

Usage: session_record.py hook        (the SessionEnd hook: hook input JSON on stdin)
       session_record.py selftest

The row: mode (the session agent type, else the project's `.claude/settings.local.json` or `.claude/settings.json`
`agent` value, else `none`), session_id, started_at and ended_at (the first and last transcript timestamps),
cost_usd (cost_estimate.estimate over the transcript's usage, null when it has no price), commits (commits on the
current branch between started_at and ended_at, null when git fails), checks (Bash calls whose command looks like a
test or check run, best effort). The row lands in the git top level of the hook input's cwd, only when that
checkout has a `.sdlc` folder. A role run (`SDLC_ROLE` set) writes no row: it records itself in runs.jsonl.
The session transcript holds the main thread only, so cost_usd leaves out sub-agent spend.
Never fails the session: on any error it writes nothing and exits 0. Claude Code only; Codex runs no hooks.
"""
import datetime, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cost_estimate  # noqa: E402

GIT_TIMEOUT = 10
CHECK_RE = re.compile(r'(?<![\w-])(pytest|selftest|check\.sh|check\.py|check-packaging\.py|vitest|jest|playwright|'
                      r'tox|mypy|tsc|eslint|ruff|shellcheck|(npm|pnpm|yarn|bun)( run)? (test|check|lint)|'
                      r'(go|cargo|swift|mix|dotnet) test|make (test|check)|node --test|unittest)(?![\w-])')


def git(root, *args):
    p = subprocess.run(['git', '-C', root] + list(args), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       universal_newlines=True, timeout=GIT_TIMEOUT)
    return p.stdout.strip() if p.returncode == 0 else None


def settings_agent(root):
    for name in ('settings.local.json', 'settings.json'):
        try:
            with open(os.path.join(root, '.claude', name), encoding='utf-8') as f:
                a = json.load(f).get('agent')
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(a, str) and a.strip():
            return a.strip()
    return None


def scan(path):
    """(first timestamp, last timestamp, check count) over a transcript; raises OSError when unreadable."""
    first = last = None
    checks = 0
    with open(path, encoding='utf-8') as f:
        lines = f.read().splitlines()
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        ts = ev.get('timestamp')
        if isinstance(ts, str) and ts:
            first, last = first or ts, ts
        msg = ev.get('message')
        content = msg.get('content') if isinstance(msg, dict) else None
        for c in content if isinstance(content, list) else ():
            if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                cmd = (c.get('input') or {}).get('command')
                if isinstance(cmd, str) and CHECK_RE.search(cmd):
                    checks += 1
    return first, last, checks


def build_row(inp, env=None):
    """The row for one hook input, or None when nothing should be written."""
    env = os.environ if env is None else env
    if env.get('SDLC_ROLE'):
        return None, None
    root = git(inp.get('cwd') or os.getcwd(), 'rev-parse', '--show-toplevel')
    if not root or not os.path.isdir(os.path.join(root, '.sdlc')):
        return None, None
    t = inp.get('transcript_path')
    started, ended, checks = scan(t)
    if not started:
        return None, None
    cost, _basis, _reason = cost_estimate.estimate(cost_estimate.transcript_model(t), cost_estimate.transcript_usage(t))
    n = git(root, 'rev-list', '--count', '--since=' + started, '--until=' + ended, 'HEAD')
    mode = inp.get('agent_type') if isinstance(inp.get('agent_type'), str) and inp.get('agent_type') else None
    row = {'mode': mode or settings_agent(root) or 'none', 'session_id': inp.get('session_id'),
           'started_at': started, 'ended_at': ended, 'cost_usd': cost,
           'commits': int(n) if n and n.isdigit() else None, 'checks': checks}
    return root, row


def record(inp, env=None):
    root, row = build_row(inp, env)
    if row is None:
        return None
    d = os.path.join(root, '.sdlc', 'runtime')
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'sessions.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(row) + '\n')
    return row


def hook():
    try:
        record(json.loads(sys.stdin.read() or '{}'))
    except BaseException:  # noqa: B902  never fail the session
        pass
    return 0


# --- selftest ----------------------------------------------------------------

def selftest():
    misses = []

    def ok(name, cond):
        print(('ok: ' if cond else 'FAIL: ') + name)
        if not cond:
            misses.append(name)

    def run_hook(inp, env):
        p = subprocess.run([sys.executable, os.path.abspath(__file__), 'hook'], input=json.dumps(inp), env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return p.returncode

    def rows(repo):
        try:
            with open(os.path.join(repo, '.sdlc', 'runtime', 'sessions.jsonl'), encoding='utf-8') as f:
                return [json.loads(x) for x in f.read().splitlines()]
        except OSError:
            return []

    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, 'repo')
        os.makedirs(os.path.join(repo, '.sdlc'))
        os.makedirs(os.path.join(repo, '.claude'))
        with open(os.path.join(repo, '.claude', 'settings.json'), 'w') as f:
            json.dump({'agent': 'sdlc:live'}, f)
        env = dict(os.environ, GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@t', GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@t')
        env.pop('SDLC_ROLE', None)
        subprocess.run(['git', 'init', '-q', repo], check=True, env=env)
        for i, when in enumerate(('2026-10-01T09:00:00Z', '2026-10-01T10:10:00Z', '2026-10-01T10:20:00Z')):
            e = dict(env, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
            subprocess.run(['git', '-C', repo, 'commit', '-q', '--allow-empty', '-m', 'c%d' % i], check=True, env=e)

        def bash(cmd):
            return {'type': 'tool_use', 'name': 'Bash', 'input': {'command': cmd}}
        usage = {'input_tokens': 1000, 'output_tokens': 500, 'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}
        tr = os.path.join(tmp, 'session.jsonl')
        with open(tr, 'w') as f:
            for ev in ({'type': 'user', 'timestamp': '2026-10-01T10:00:00Z', 'message': {'role': 'user', 'content': 'go'}},
                       {'type': 'assistant', 'timestamp': '2026-10-01T10:05:00Z', 'message': {
                           'id': 'm1', 'role': 'assistant', 'model': 'claude-opus-5-5', 'usage': usage,
                           'content': [bash('python3 plugins/sdlc/scripts/check.py'), bash('git status'),
                                       bash('npm test -- a.test.ts')]}},
                       {'type': 'assistant', 'timestamp': '2026-10-01T10:30:00Z', 'message': {
                           'id': 'm2', 'role': 'assistant', 'model': 'claude-opus-5-5', 'usage': usage,
                           'content': [bash('python3 x.py selftest'), bash('echo testing')]}}):
                f.write(json.dumps(ev) + '\n')
            f.write('not json\n')
        inp = {'session_id': 'S1', 'transcript_path': tr, 'cwd': repo, 'hook_event_name': 'SessionEnd'}
        ok('hook: a fixture transcript exits 0', run_hook(inp, env) == 0)
        got = rows(repo)
        r = got[0] if len(got) == 1 else {}
        ok('hook: one row', len(got) == 1)
        ok('row: mode from project settings, session id, start and end from the transcript',
           (r.get('mode'), r.get('session_id'), r.get('started_at'), r.get('ended_at'))
           == ('sdlc:live', 'S1', '2026-10-01T10:00:00Z', '2026-10-01T10:30:00Z'))
        ok('row: commits between start and end on the branch', r.get('commits') == 2)
        ok('row: checks count test and check commands only', r.get('checks') == 3)
        ok('row: cost estimated from transcript usage', isinstance(r.get('cost_usd'), float) and r['cost_usd'] > 0)
        ok('row: the hook input agent_type wins over settings',
           build_row(dict(inp, agent_type='sdlc:hybrid'), env)[1]['mode'] == 'sdlc:hybrid')
        ok('negative control: a role run writes no row', build_row(inp, dict(env, SDLC_ROLE='solo')) == (None, None))
        ok('negative control: a checkout with no .sdlc writes no row',
           build_row(dict(inp, cwd=tmp), env) == (None, None))
        ok('hook: an unreadable transcript exits 0',
           run_hook(dict(inp, session_id='S2', transcript_path=os.path.join(tmp, 'missing.jsonl')), env) == 0)
        ok('hook: an unreadable transcript writes no row', len(rows(repo)) == 1)
        p = subprocess.run([sys.executable, os.path.abspath(__file__), 'hook'], input='{', env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        ok('hook: bad hook input exits 0 silently and writes no row', p.returncode == 0 and not p.stderr and len(rows(repo)) == 1)
    if misses:
        print('session_record selftest: %d failed: %s' % (len(misses), '; '.join(misses)), file=sys.stderr)
        return 1
    print('session_record selftest: ok')
    return 0


def main(argv):
    if argv == ['hook']:
        return hook()
    if argv == ['selftest']:
        return selftest()
    print(__doc__.split('\n\n')[1], file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
