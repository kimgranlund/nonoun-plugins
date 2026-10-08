#!/usr/bin/env python3
"""Start the solo agent for one ticket and record its cost, so the default lane is metered.

  solo_run.py run (--task-dir DIR | --new-task [SLUG]) --tier L1|L2|L3 (--brief TEXT | --brief-file FILE | --brief -)
                  [--backend claude|codex] [--exec] [--cwd DIR] [--worktree NAME | --no-worktree] [--timeout SECONDS] [--raw-out FILE]
  solo_run.py selftest

Claude (T-0284): run checks the budget gate, appends one `role solo` record (transport subagent, cost null) so the
verifier's family rule sees the solo's model, and prints the dispatch JSON for the parent to spawn as a background
sub-agent (`subagent_type sdlc-lite:solo-<level>`, model, effort, prompt = the brief). It starts no `claude -p`. The
parent then runs one `dispatch.py prepare verifier <level> <task dir>/handoff.md` for levels L2 and L3 (L2, or L3 where
`steps.py verifier-level` says so, T-0356). `--exec` is the legacy
headless start that the next paragraphs describe (`fanout.py run` lanes use it until T-0288; sub-agent lanes use `fanout.py prep` and `land`, T-0285); Codex always executes.

With --exec (or Codex), run starts the session at the level's model and effort (agents/solo.md), prints the agent's report on
stdout, and appends one line to <task-dir>/runs.jsonl in the record shape run.sh writes for roles
(ts, role solo, level L1..L3, model, effort, cost_usd, usage, duration_ms, turns, attempt_id,
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

T-0345: when another solo is live in the checkout (a sub-agent dispatch marker under the git dir, fresh and not yet
priced by `complete`, or a live --exec lock), run defaults to --worktree solo-<task>, prints the choice, and the dispatch
JSON carries `worktree`. --worktree and --no-worktree win.

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
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

SCRIPTS = pathlib.Path(__file__).resolve().parent
PLUGIN = SCRIPTS.parent
# Solo levels (agents/solo.md): level -> (Claude model, Claude effort, level). The same table as fanout.SOLO_TIERS;
# check.py guards that solo.md, fanout.py and this table agree.
TIERS = {'L1': ('sonnet', 'low', 'L1'), 'L2': ('sonnet', 'high', 'L2'), 'L3': ('opus', 'xhigh', 'L3')}
# Deprecated 0.21.x tier names, accepted by --tier for one release and normalized to the level. ALIAS_OK
TIER_ALIASES = {'S': 'L1', 'M': 'L2', 'L': 'L3'}  # ALIAS_OK


def tier_of(tier):
    """The solo level for a --tier value: L1, L2, L3, or a deprecated alias of one; else the value unchanged."""
    return TIER_ALIASES.get(tier, tier)
CODEX_MODELS = {'L1': ('gpt-6.1-sol', 'low'), 'L2': ('gpt-6.1-sol', 'high'), 'L3': ('gpt-6.1-sol', 'xhigh')}


class Refuse(Exception):
    pass


def command(tier, brief, backend):
    """(argv, model, effort) that starts solo at the level."""
    tier = tier_of(tier)
    if tier not in TIERS:
        raise Refuse(f'no solo level {tier!r}: want L1, L2, or L3')
    model, effort, level = TIERS[tier]
    if backend == 'codex':
        exe = os.environ.get('SOLO_CODEX_EXEC') or str(SCRIPTS / 'codex_exec.py')
        m, e = CODEX_MODELS[level]
        return [sys.executable, exe, 'solo', level, brief], m, e
    if backend != 'claude':
        raise Refuse('unknown backend: ' + backend)
    return ['claude', '-p', '--plugin-dir', str(PLUGIN), '--agent', 'sdlc-lite:solo', '--model', model,
            '--effort', effort, '--dangerously-skip-permissions', '--output-format', 'json', '--', brief], model, effort


def dispatch_json(task_dir, tier, brief, worktree=None):
    """(rc, dispatch dict or None): the budget gate, then the sub-agent dispatch for the Claude backend (T-0284)."""
    tier = tier_of(tier)
    if tier not in TIERS:
        raise Refuse(f'no solo level {tier!r}: want L1, L2, or L3')
    handoff = pathlib.Path(task_dir) / 'handoff.md'
    if not handoff.is_file():
        raise Refuse(f'{task_dir}: no handoff.md; --task-dir is the ticket or task folder')
    hold = budget_hold(task_dir)
    if hold:
        print(f"solo_run.py: budget {hold['percent']}%: ask the user; budget.py ack", file=sys.stderr)
        return 4, None
    model, effort, level = TIERS[tier]
    import steps  # same scripts/ dir: the one rule for the verifier level (T-0356)
    vlevel = steps.ticket_verifier(handoff.read_text(encoding='utf-8'))[0]
    attempt = uuid.uuid4().hex
    slug = re.sub(r'[^a-z0-9]+', '-', pathlib.Path(task_dir).resolve().name.lower()).strip('-')[:40] or 'task'
    d = dict(subagent_type=f'sdlc-lite:solo-{tier}', name=f'solo-{tier}-{slug}', description=f'solo {tier}: {slug}',
             model=model, effort=effort, prompt=brief, run_in_background=os.environ.get('SDLC_HEADLESS') != '1',
             role='solo', level=level, tier=tier, handoff=str(handoff.resolve()), artifacts_dir=str(pathlib.Path(task_dir).resolve()),
             attempt_id=attempt, verifier='python3 %s prepare verifier %s %s' % (SCRIPTS / 'dispatch.py', vlevel, handoff.resolve()) if tier != 'L1' else None)
    # The spawn gate (hooks/block-role-spawn.sh) finds the dispatch record from the prompt's Handoff line.
    d['prompt'] = f'Handoff: {d["handoff"]}\nArtifacts dir: {d["artifacts_dir"]}\n{brief}'
    if worktree:
        d['worktree'] = worktree
        d['prompt'] = f'Worktree: {worktree} (work and commit there, not in the main checkout)\n' + d['prompt']
    else:
        mark_live(task_dir, attempt)
    (pathlib.Path(task_dir) / f'{d["name"]}.dispatch.json').write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
    rec = build_record(tier, 'claude', model, effort, None, attempt, time.monotonic(), 0)
    rec.update(transport='subagent', cost_reason='subagent usage not priced', duration_ms=None, turns=None)
    append(task_dir, rec)
    return 0, d


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
    tier = tier_of(tier)
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
           'routing_reason': reason or f'solo lane, level {tier}',
           'backend': backend, 'transport': 'exec' if backend == 'codex' else 'claude',
           'usage': (result or {}).get('usage'), 'cost_usd': cost, 'duration_ms': duration,
           'turns': number((result or {}).get('num_turns')), 'exit_code': rc,
           'stray_worktrees': [], 'stray_branches': []}
    if cost_reason:
        rec['cost_reason'] = cost_reason
    return rec


LIMIT_RE = re.compile(r'429|session limit|usage limit|hit your (session |usage )?limit|rate.?limit', re.I)


RESET_RE = re.compile(r'resets +(\d{1,2}(?::\d{2})? *[ap]m)', re.I)


def limit_hint(task_dir, tier, text):
    """On a 429 or session-limit stop, write <task dir>/solo.limit (one JSON line) and print the resume hint."""
    m = LIMIT_RE.search(text or '')
    if not m:
        return
    tier = tier_of(tier)
    resume = f'python3 {pathlib.Path(__file__).resolve()} run --task-dir {task_dir} --tier {tier} --brief <the same brief>'
    rec = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'task_dir': str(task_dir), 'tier': tier,
           'resume': resume, 'evidence': (text or '')[max(0, m.start() - 40):m.end() + 80].strip()[:200]}
    rm = RESET_RE.search(text or '')
    if rm:
        rec['reset'] = rm.group(1)
    try:
        (pathlib.Path(task_dir) / 'solo.limit').write_text(json.dumps(rec, separators=(',', ':')) + '\n', encoding='utf-8')
    except OSError:
        pass
    print('solo_run.py: session limit: the work is in the tree (fanout keeps it in the lane WIP commit); '
          f'resume after the limit resets: {resume}' + (f' (resets {rm.group(1)})' if rm else ''), file=sys.stderr)


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


def complete(task_dir, attempt, model_tier, transcript=None, tokens=None, agent_id=None, tool_uses=None, duration_ms=None):
    """Price the solo row dispatch_json wrote (usage null) from the sub-agent transcript or the notice token count (T-0328).
    Rewrites that row in place so budget.py does not count the run twice. Returns the priced cost, or None with the row untouched."""
    sys.path.insert(0, str(SCRIPTS))
    import cost_estimate
    usage = cost_estimate.transcript_usage(transcript) if transcript else None
    if usage is None and tokens is not None:
        usage = {'subagent_tokens': tokens}
    if usage is not None and tool_uses is not None:
        usage = {**usage, 'tool_uses': tool_uses}
    f = pathlib.Path(task_dir) / 'runs.jsonl'
    if not f.is_file():
        unmark_live(task_dir, attempt)
        return None
    rows, cost, touched = [], None, False
    for line in f.read_text(encoding='utf-8').splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            rows.append(line)
            continue
        if isinstance(r, dict) and r.get('role') == 'solo' and r.get('attempt_id', '').startswith(attempt) and r.get('usage') is None:
            if agent_id:  # T-0355: the agent id and duration land even when nothing prices the row
                r['agent_id'], touched = agent_id, True
            if duration_ms is not None:
                r['duration_ms'], touched = duration_ms, True
            est, basis, _ = cost_estimate.estimate(r.get('model') or TIERS[tier_of(model_tier)][0], usage) if usage is not None else (None, None, None)
            if est is not None:
                r.update(usage=usage, cost_usd=est, cost_estimated=True, cost_basis=basis)
                r.pop('cost_reason', None)
                cost = est
                touched = True
        rows.append(json.dumps(r, separators=(',', ':')) if isinstance(r, dict) else line)
    if touched:
        f.write_text('\n'.join(rows) + '\n', encoding='utf-8')
    unmark_live(task_dir, attempt)
    return cost


class Stopped(Exception):
    """The wrapper got SIGTERM, SIGINT or SIGHUP (T-0293)."""

    def __init__(self, sig):
        super().__init__(sig)
        self.sig = sig


def _sig_group(pgid, sig):
    try:
        os.killpg(pgid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def _group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def kill_group(p):
    """End the child's whole process group: TERM, then KILL after 2 s (T-0293). Returns the child's captured stdout."""
    pgid = p.pid
    _sig_group(pgid, signal.SIGTERM)
    end = time.monotonic() + 2
    while time.monotonic() < end:
        p.poll()
        if not _group_alive(pgid):
            break
        time.sleep(0.05)
    _sig_group(pgid, signal.SIGKILL)
    try:
        out, _ = p.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        out = ''
    p.poll()
    return out or ''


def lock_path(where):
    """<git dir of the worktree holding where>/solo_run.lock, or None outside a git repository."""
    try:
        r = subprocess.run(['git', 'rev-parse', '--absolute-git-dir'], cwd=str(where), capture_output=True,
                           text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    return pathlib.Path(r.stdout.strip()) / 'solo_run.lock' if r.returncode == 0 and r.stdout.strip() else None


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def take_lock(path):
    """Write this wrapper's pid to the lock; Refuse when the pid already there is alive, clear it when dead."""
    for _ in range(3):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            try:
                pid = int(path.read_text().strip())
            except (OSError, ValueError):
                pid = 0
            if pid > 0 and _pid_alive(pid):
                raise Refuse(f'another solo run is live (pid {pid})')
            path.unlink(missing_ok=True)
            continue
        with os.fdopen(fd, 'w') as f:
            f.write(str(os.getpid()) + '\n')
        return
    raise Refuse('could not take the solo run lock ' + str(path))


def drop_lock(path):
    try:
        if path.read_text().strip() == str(os.getpid()):
            path.unlink()
    except (OSError, ValueError):
        pass


LIVE_TTL = 6 * 3600  # a sub-agent solo leaves no pid; its marker counts as live this long unless complete removes it


def _live_dir(where):
    lp = lock_path(where)
    return lp.parent / 'solo_live' if lp else None


def mark_live(where, attempt):
    d = _live_dir(where)
    if d is not None:
        d.mkdir(exist_ok=True)
        (d / attempt).write_text(str(time.time()), encoding='utf-8')


def unmark_live(where, attempt):
    d = _live_dir(where)
    if d is not None and d.is_dir():
        for f in d.glob(attempt + '*'):
            f.unlink(missing_ok=True)


def live_solos(where):
    """Count other solos live in the checkout holding where: a fresh sub-agent marker or a live exec lock (T-0345)."""
    n = 0
    d = _live_dir(where)
    if d is not None and d.is_dir():
        n += sum(1 for f in d.iterdir() if time.time() - f.stat().st_mtime < LIVE_TTL)
    lp = lock_path(where)
    if lp is not None and lp.exists():
        try:
            n += 1 if _pid_alive(int(lp.read_text().strip())) else 0
        except (OSError, ValueError):
            pass
    return n


def auto_worktree(task_dir, cwd):
    """The worktree name to default to when another solo is live in this checkout, else None."""
    if not live_solos(cwd or task_dir):
        return None
    slug = re.sub(r'[^a-z0-9]+', '-', pathlib.Path(task_dir).resolve().name.lower()).strip('-')[:40] or 'task'
    return 'solo-' + slug


def ensure_worktree(name, base=None):
    """Create <repo>/.worktrees/<name> on a new branch <name> when missing; return its path. The role cannot do
    this itself: block-stray-worktree.sh denies a role creating worktrees or branches, so the launcher does."""
    def git(*a):
        return subprocess.run(['git', *a], cwd=str(base or '.'), capture_output=True, text=True)
    top = git('rev-parse', '--show-toplevel')
    if top.returncode:
        raise Refuse('--worktree needs a git repository')
    wt = pathlib.Path(top.stdout.strip()) / '.worktrees' / name
    if wt.is_dir():
        return str(wt)
    exists = git('rev-parse', '--verify', '-q', f'refs/heads/{name}').returncode == 0
    r = git('worktree', 'add', str(wt), name) if exists else git('worktree', 'add', '-b', name, str(wt))
    if r.returncode:
        raise Refuse(f'git worktree add failed: {r.stderr.strip()}')
    return str(wt)


def run(task_dir, tier, brief, backend='claude', cwd=None, timeout=None, raw_out=None):
    tier = tier_of(tier)
    argv, model, effort = command(tier, brief, backend)
    if not (pathlib.Path(task_dir) / 'handoff.md').is_file():
        raise Refuse(f'{task_dir}: no handoff.md; --task-dir is the ticket or task folder')
    lock = lock_path(cwd or task_dir)
    if lock is not None:
        take_lock(lock)
    old_handlers = {}
    try:
        def on_signal(signum, _frame):
            raise Stopped(signum)
        try:
            for sg in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
                old_handlers[sg] = signal.signal(sg, on_signal)
        except ValueError:  # not the main thread: no handlers
            pass
        return _run_locked(task_dir, tier, brief, backend, cwd, timeout, raw_out, argv, model, effort)
    finally:
        for sg, h in old_handlers.items():
            signal.signal(sg, h)
        if lock is not None:
            drop_lock(lock)


def _run_locked(task_dir, tier, brief, backend, cwd, timeout, raw_out, argv, model, effort):
    hold = budget_hold(task_dir)
    if hold:
        print(f"solo_run.py: budget {hold['percent']}%: ask the user; budget.py ack", file=sys.stderr)
        return 4
    # Always mint a fresh id: an inherited SDLC_ATTEMPT_ID belongs to a role attempt (fanout.py does the same), and
    # budget.py skips a second record with a repeated attempt_id, so reusing it would undercount spend.
    attempt = uuid.uuid4().hex
    env = dict(os.environ, SDLC_ROLE='solo', SDLC_ATTEMPT_ID=attempt)
    started = time.monotonic()
    p = None
    try:
        p = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             text=True, start_new_session=True)
        out, _ = p.communicate(timeout=timeout)
        rc = p.returncode
    except FileNotFoundError as exc:
        out, rc = '', 127
        print(f'solo_run.py: {exc}', file=sys.stderr)
    except subprocess.TimeoutExpired:
        out, rc = kill_group(p), 124
        print(f'solo_run.py: timed out after {timeout}s', file=sys.stderr)
    except Stopped as exc:
        out, rc = (kill_group(p) if p else ''), 128 + exc.sig
        print(f'solo_run.py: stopped by signal {exc.sig}; process group ended', file=sys.stderr)
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
    if rc == 0 and result is None:
        # T-0346: an unreadable stream (no result event) is a failure, said on stdout with the raw first line and the log path.
        log = pathlib.Path(raw_out) if raw_out else pathlib.Path(task_dir) / 'solo.stream.log'
        if not raw_out:
            log.write_text(out or '', encoding='utf-8')
        first = (out or '').strip().splitlines()[:1]
        print(f'solo_run.py: FAILED: session stream has no readable result event (JSON parse failure); '
              f'first line: {first[0][:200] if first else "(empty)"}; raw stream log: {log}')
        failed = 1
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
            expect('record model and effort', rec.get('model') == 'sonnet' and rec.get('effort') == 'high')
            expect('cost matches the result event', rec.get('cost_usd') == 3.25)
            expect('usage, turns, duration copied', rec.get('usage', {}).get('output_tokens') == 20
                   and rec.get('turns') == 7 and rec.get('duration_ms') == 4321)
            expect('attempt id set', isinstance(rec.get('attempt_id'), str) and len(rec['attempt_id']) >= 8)
            expect('exit status 0', rc == 0)
            s, un, _est = budget.spend(d)
            expect('budget counts the solo cost', abs(s - 3.25) < 1e-9 and un == 0)

            shim("printf '%s\\n' 'not json {broken'\n")
            d = ticket('bad')
            out_bad = io.StringIO()
            with contextlib.redirect_stdout(out_bad), contextlib.redirect_stderr(io.StringIO()):
                rc_bad = run(str(d), 'S', 'b', cwd=str(tmp))
            expect('malformed stream: non-zero exit and stdout names the log path (T-0346)',
                   rc_bad != 0 and str(d / 'solo.stream.log') in out_bad.getvalue() and 'not json' in out_bad.getvalue()
                   and (d / 'solo.stream.log').is_file())

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
            s, un, _est = budget.spend(d)
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
            tmp_limit = d
            got = json.loads(mk.read_text()) if mk.is_file() else {}
            expect('limit stop: exits 1, solo.limit has the resume command and evidence',
                   rc == 1 and '--task-dir' in got.get('resume', '') and '429' in got.get('evidence', ''))
            expect('limit stop: stderr prints the resume hint', 'session limit' in err.getvalue() and 'resume' in err.getvalue())

            # T-0298: a reset time in the output lands in the marker and the hint.
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":true,\"result\":\"API Error: 429 session limit reached, resets 1:40pm\"}'\n")
            d = ticket('limitreset')
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = run(d, 'M', 'b')
            mk = d / 'solo.limit'
            got = json.loads(mk.read_text()) if mk.is_file() else {}
            expect('limit stop with a reset: marker reset is 1:40pm and the hint says so',
                   rc == 1 and got.get('reset') == '1:40pm' and 'resets 1:40pm' in err.getvalue())
            expect('limit stop without a reset: no reset field (T-0298 control)', 'reset' not in json.loads((tmp_limit / 'solo.limit').read_text()))

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
            # T-0284: the Claude default prints the dispatch JSON for a sub-agent and starts no claude -p.
            def pj(*a):
                with contextlib.redirect_stderr(io.StringIO()):
                    return dispatch_json(*a)
            rc4, none = pj(d, 'M', 'b')
            expect('subagent: the budget gate exits 4 with no dispatch and no record', rc4 == 4 and none is None and len(lines(d)) == 1)
            dsub = ticket('subagent', budget_usd=10)
            seed(dsub, 1.0)
            rcd, dd = pj(dsub, 'L2', 'the brief')
            recs = lines(dsub)
            expect('subagent: level L2 dispatch names solo-L2, sonnet high, the brief, and the verifier command',
                   rcd == 0 and dd['subagent_type'] == 'sdlc-lite:solo-L2' and dd['name'] == 'solo-L2-subagent' and dd['tier'] == 'L2'
                   and (dd['model'], dd['effort']) == ('sonnet', 'high')
                   and dd['prompt'].endswith('the brief') and dd['prompt'].startswith('Handoff: ') and (dsub / 'solo-L2-subagent.dispatch.json').is_file() and 'prepare verifier L2' in dd['verifier'])
            dmark = ticket('subagent-mark', budget_usd=10)
            (dmark / 'handoff.md').write_text((dmark / 'handoff.md').read_text(encoding='utf-8') + '\nverifier: L3\n', encoding='utf-8')
            rcv, dv = pj(dmark, 'L2', 'the brief')
            expect('subagent: a handoff with a verifier: L3 line prints prepare verifier L3 (T-0356 positive control); the plain ticket above printed L2',
                   rcv == 0 and 'prepare verifier L3' in dv['verifier'] and 'prepare verifier L2' in dd['verifier'])
            expect('subagent: one solo record with transport subagent and cost null, and no session started',
                   len(recs) == 2 and recs[1]['role'] == 'solo' and recs[1]['model'] == 'sonnet' and recs[1]['transport'] == 'subagent'
                   and recs[1]['cost_usd'] is None and not mark.exists())
            expect('subagent: level L1 has no verifier command', pj(dsub, 'L1', 'b')[1]['verifier'] is None)
            # The deprecated 0.21.x tier names are aliases: each dispatches as its level (same model and effort).
            for alias, level, me in (('S', 'L1', ('sonnet', 'low')), ('M', 'L2', ('sonnet', 'high')), ('L', 'L3', ('opus', 'xhigh'))):
                _, da = pj(dsub, alias, 'b')
                expect(f'subagent: alias {alias} dispatches as solo-{level} at {me}',
                       da['subagent_type'] == f'sdlc-lite:solo-{level}' and da['tier'] == level and da['level'] == level
                       and (da['model'], da['effort']) == me and da['name'].startswith(f'solo-{level}-'))
            _, d3 = pj(dsub, 'L3', 'b')
            expect('subagent: level L3 is opus xhigh with a verifier command',
                   d3['subagent_type'] == 'sdlc-lite:solo-L3' and (d3['model'], d3['effort']) == ('opus', 'xhigh') and d3['verifier'])
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
                                 '--tier', 'L1', '--brief', 'cli brief'], cwd=str(pr), capture_output=True, text=True,
                                env=dict(os.environ), timeout=60)
            recs = [json.loads(x) for x in (pr / '.sdlc' / 'cli-task' / 'runs.jsonl').read_text().splitlines()] \
                if (pr / '.sdlc' / 'cli-task' / 'runs.jsonl').is_file() else []
            expect(f'new task CLI: rc 0 and one solo record, got rc={cp.returncode} err={cp.stderr[-200:]!r}',
                   cp.returncode == 0 and [x.get('role') for x in recs] == ['solo'] and recs[0].get('level') == 'L1')
            cp = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), 'run', '--new-task', 'cli-alias',
                                 '--tier', 'S', '--brief', 'cli brief'], cwd=str(pr), capture_output=True, text=True,
                                env=dict(os.environ), timeout=60)
            recs = [json.loads(x) for x in (pr / '.sdlc' / 'cli-alias' / 'runs.jsonl').read_text().splitlines()] \
                if (pr / '.sdlc' / 'cli-alias' / 'runs.jsonl').is_file() else []
            expect(f'CLI: the deprecated --tier S is accepted as L1 with a notice, got rc={cp.returncode} err={cp.stderr[-200:]!r}',  # ALIAS_OK
                   cp.returncode == 0 and '--tier S is deprecated; use --tier L1' in cp.stderr  # ALIAS_OK
                   and [x.get('level') for x in recs] == ['L1'] and recs[0].get('effort') == 'low')
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
            q(d, 'L3', 'b', backend='codex')
            q(d, 'L', 'b', backend='codex')
            rec = lines(d)[0]
            expect('codex: alias L runs as level L3 too', lines(d)[1].get('level') == 'L3' and lines(d)[1].get('effort') == 'xhigh')
            expect('codex: level L3, null cost with reason', rec.get('level') == 'L3' and rec.get('cost_usd') is None
                   and rec.get('cost_reason') == 'codex reports no cost' and rec.get('turns') == 2
                   and rec.get('model') == 'gpt-6.1-sol' and rec.get('effort') == 'xhigh')
            del os.environ['SOLO_CODEX_EXEC']

            # Refusals write nothing.
            d = ticket('refuse')
            for name, fn in (('bad tier', lambda: q(d, 'XL', 'b')), ('bad level', lambda: q(d, 'L4', 'b')), ('bad backend', lambda: q(d, 'M', 'b', backend='x')),
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
            q(d, 'L2', 'b')
            q(d, 'M', 'b')
            ids = [x['attempt_id'] for x in lines(d)]
            expect('distinct attempt ids, both counted', len(set(ids)) == 2 and abs(budget.spend(d)[0] - 2) < 1e-9)
            expect('inherited SDLC_ATTEMPT_ID is not reused', 'inherited-role-attempt' not in ids)
            expect('inherited SDLC_ROUTING_REASON is not copied', all(x.get('routing_reason') == 'solo lane, level L2' for x in lines(d)))

            # find_result shapes.
            expect('find_result: none on empty', find_result('') is None and find_result('not json') is None)
            expect('find_result: json lines', (find_result('{"type":"x"}\n{"type":"result","total_cost_usd":2}\n') or {}).get('total_cost_usd') == 2)

            # T-0293: a real child (a stub claude that spawns sleep): the whole group is gone after a timeout and after
            # SIGTERM to the wrapper; a second run in a live worktree is refused; a dead pid's lock is cleared.
            me = pathlib.Path(__file__).resolve()
            repo = tmp / 'grprepo'
            repo.mkdir()
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            dg = ticket('grp')
            shutil.move(str(dg), str(repo / 'grp'))
            dg = repo / 'grp'
            pidf = tmp / 'child.pid'
            errf = tmp / 'wrapper.err'
            shim(f'sleep 300 >/dev/null 2>&1 &\necho $! > "{pidf}"\nwait\n')

            def gone(pid, wait=4.0):
                end = time.monotonic() + wait
                while time.monotonic() < end:
                    try:
                        os.kill(pid, 0)
                    except ProcessLookupError:
                        return True
                    time.sleep(0.05)
                return False

            def child_pid():
                end = time.monotonic() + 10
                while time.monotonic() < end:
                    if pidf.is_file() and pidf.read_text().strip():
                        return int(pidf.read_text().strip())
                    time.sleep(0.05)
                return None

            def wrapper(script, *extra):
                pidf.unlink(missing_ok=True)
                return subprocess.Popen([sys.executable, str(script), 'run', '--exec', '--task-dir', str(dg), '--tier', 'L1',
                                         '--brief', 'b', '--cwd', str(repo), *extra], stdout=subprocess.DEVNULL,
                                        stderr=open(errf, 'w'))

            def kill_leftover():
                if pidf.is_file() and pidf.read_text().strip():
                    try:
                        os.kill(int(pidf.read_text().strip()), signal.SIGKILL)
                    except ProcessLookupError:
                        pass

            def group_case(script, how):
                w = wrapper(script, *(['--timeout', '1'] if how == 'timeout' else []))
                cp = child_pid()
                if cp is None:
                    w.kill()
                    return None, None, ''
                if how == 'sigterm':
                    time.sleep(0.3)
                    w.send_signal(signal.SIGTERM)
                try:
                    w.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    w.kill()
                    w.wait()
                return w.returncode, gone(cp), errf.read_text()

            for how in ('timeout', 'sigterm'):
                rc_w, child_gone, err = group_case(me, how)
                expect(f'group kill after {how}: wrapper exits nonzero and the child is gone', bool(rc_w) and child_gone)
                expect(f'group kill after {how}: lock removed', not (repo / '.git' / 'solo_run.lock').exists())
                kill_leftover()
            ctl = tmp / 'solo_run_nokill.py'
            src = me.read_text()
            body = '    try:\n        os.killpg(pgid, sig)\n    except (ProcessLookupError, PermissionError):\n        pass\n'
            assert body in src
            src = src.replace(body, '    pass\n', 1).replace(
                'SCRIPTS = pathlib.Path(__file__).resolve().parent', f'SCRIPTS = pathlib.Path({str(SCRIPTS)!r})', 1)
            ctl.write_text(src)
            for how in ('timeout', 'sigterm'):
                res = group_case(ctl, how)
                survived = res[1] is False
                kill_leftover()
                expect(f'negative control: a copy without the group kill leaves the child alive after {how}', survived)

            # Second run while a live pid holds the lock: refused, one line, no session, no record.
            lock = repo / '.git' / 'solo_run.lock'
            live = subprocess.Popen(['sleep', '60'])
            try:
                lock.write_text(f'{live.pid}\n')
                pidf.unlink(missing_ok=True)
                before = len(lines(dg))
                cp = subprocess.run([sys.executable, str(me), 'run', '--exec', '--task-dir', str(dg), '--tier', 'L1', '--brief', 'b',
                                     '--cwd', str(repo), '--no-worktree'], capture_output=True, text=True, timeout=60)
                msg = cp.stderr.strip().splitlines()
                expect('second run: refused with the one-line message, nonzero',
                       cp.returncode != 0 and msg == [f'solo_run.py: another solo run is live (pid {live.pid})'])
                expect('second run: no session and no record', not pidf.exists() and len(lines(dg)) == before)
                expect('second run: the first run keeps its lock', lock.read_text().strip() == str(live.pid))
            finally:
                live.kill()
                live.wait()
            # Stale lock: a dead pid is cleared and the run proceeds.
            dead = subprocess.Popen(['true'])
            dead.wait()
            lock.write_text(f'{dead.pid}\n')
            shim("printf '%s' '{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\",\"total_cost_usd\":1}'\n")
            before = len(lines(dg))
            cp = subprocess.run([sys.executable, str(me), 'run', '--exec', '--task-dir', str(dg), '--tier', 'L1', '--brief', 'b',
                                 '--cwd', str(repo)], capture_output=True, text=True, timeout=60)
            expect('stale lock: a dead pid proceeds and records', cp.returncode == 0 and len(lines(dg)) == before + 1)
            expect('stale lock: removed on exit', not lock.exists())
            # T-0313: --worktree creates the lane worktree on a new branch and the session runs inside it.
            wrepo = tmp / 'wtrepo'
            wrepo.mkdir()
            for c in (['init', '-q'], ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'i']):
                subprocess.run(['git', *c], cwd=str(wrepo), check=True)
            dw = ticket('wt')
            shutil.move(str(dw), str(wrepo / 'wt'))
            dw = wrepo / 'wt'
            pwdf = tmp / 'pwd.out'
            shim(f"pwd -P > {pwdf}\nprintf '%s' '{{\"type\":\"result\",\"is_error\":false,\"result\":\"ok\",\"total_cost_usd\":1}}'\n")
            cp = subprocess.run([sys.executable, str(me), 'run', '--exec', '--task-dir', str(dw), '--tier', 'L1', '--brief', 'b',
                                 '--cwd', str(wrepo), '--worktree', 'lane-x'], capture_output=True, text=True, timeout=60)
            want = (wrepo / '.worktrees' / 'lane-x').resolve()
            br = subprocess.run(['git', 'branch', '--list', 'lane-x'], cwd=str(wrepo), capture_output=True, text=True).stdout
            expect('--worktree: run succeeds', cp.returncode == 0)
            expect('--worktree: worktree on a new branch', want.is_dir() and 'lane-x' in br)
            expect('--worktree: session cwd is the worktree', pwdf.exists() and pathlib.Path(pwdf.read_text().strip()) == want)
            # T-0345: a second dispatch while a first solo is live defaults to a worktree; a single run keeps today's behavior.
            wr2 = tmp / 'dfrepo'
            wr2.mkdir()
            for c in (['init', '-q'], ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'i']):
                subprocess.run(['git', *c], cwd=str(wr2), check=True)
            def disp(name, *extra):
                d_ = ticket(name)
                shutil.move(str(d_), str(wr2 / name))
                cp_ = subprocess.run([sys.executable, str(me), 'run', '--task-dir', str(wr2 / name), '--tier', 'L1', '--brief', 'b',
                                      '--cwd', str(wr2), *extra], capture_output=True, text=True, timeout=60)
                return cp_, (json.loads(cp_.stdout) if cp_.stdout.strip() else {})
            c1, j1 = disp('par1')
            expect('default worktree: a single run keeps the checkout', c1.returncode == 0 and 'worktree' not in j1)
            c2, j2 = disp('par2')
            expect('default worktree: the second live solo gets a worktree', c2.returncode == 0 and j2.get('worktree')
                   and pathlib.Path(j2['worktree']).is_dir() and 'solo-par2' in c2.stderr)
            c3, j3 = disp('par3', '--no-worktree')
            expect('default worktree: --no-worktree wins', c3.returncode == 0 and 'worktree' not in j3)
            unmark_live(wr2, j1['attempt_id'])
            for f in (wr2 / '.git' / 'solo_live').glob('*'):
                f.unlink()
            c4, j4 = disp('par4')
            expect('default worktree: none live again keeps the checkout', c4.returncode == 0 and 'worktree' not in j4)
            # T-0350: recording a finished sub-agent solo (dispatch.py record) clears its marker, so the next solo stays here.
            c5, j5 = disp('par5')
            expect('recorded solo: before the record, a live marker forces the next solo into a worktree', c5.returncode == 0 and j5.get('worktree'))
            rp = subprocess.run([sys.executable, str(SCRIPTS / 'dispatch.py'), 'record', str(wr2 / 'par4' / f'{j4["name"]}.dispatch.json')],
                                capture_output=True, text=True, timeout=60)
            c6, j6 = disp('par6')
            expect('recorded solo: record exits 0 and clears the marker, the next solo keeps the checkout',
                   rp.returncode == 0 and c6.returncode == 0 and 'worktree' not in j6)
        finally:
            os.environ['PATH'] = old_path
            for k, v in old_env.items():
                if v is None: os.environ.pop(k, None)
                else: os.environ[k] = v
    with tempfile.TemporaryDirectory() as tmp:
        d = pathlib.Path(tmp)
        (d / 'handoff.md').write_text('x\n')
        rc, disp = dispatch_json(str(d), 'M', 'brief')
        tr = d / 't.jsonl'
        tr.write_text(json.dumps({'message': {'id': 'm1', 'usage': {'input_tokens': 10, 'output_tokens': 1000,
                                                                      'cache_read_input_tokens': 500000}}}) + '\n')
        row = lambda: [json.loads(l) for l in (d / 'runs.jsonl').read_text().splitlines()]
        expect('solo row starts unpriced', row()[0]['cost_usd'] is None)
        expect('complete: unknown attempt prices nothing', complete(d, 'zzzz', 'M', str(tr)) is None and row()[0]['cost_usd'] is None)
        got = complete(d, disp['attempt_id'], 'M', str(tr))
        r0 = row()
        expect('complete: solo row priced in place, one row', got and len(r0) == 1 and r0[0]['cost_usd'] == got and got > 0
               and r0[0].get('cost_estimated') and 'cost_reason' not in r0[0] and r0[0]['usage']['output_tokens'] == 1000)
    with tempfile.TemporaryDirectory() as tmp:  # T-0352: the notice's agent id, tool uses and duration reach the row
        d = pathlib.Path(tmp)
        (d / 'handoff.md').write_text('x\n')
        rc, disp = dispatch_json(str(d), 'M', 'brief')
        got = complete(d, disp['attempt_id'], 'M', None, 1234, agent_id='ag-3', tool_uses=7, duration_ms=900)
        r0 = [json.loads(l) for l in (d / 'runs.jsonl').read_text().splitlines()][0]
        expect('complete: row carries agent_id, duration_ms and tool_uses', got is not None and r0.get('agent_id') == 'ag-3'
               and r0.get('duration_ms') == 900 and r0['usage'].get('tool_uses') == 7)
    with tempfile.TemporaryDirectory() as tmp:  # T-0355: dispatch.py record takes the solo_run.py dispatch file end to end
        d = pathlib.Path(tmp)
        (d / 'handoff.md').write_text('x\n')
        rc, disp = dispatch_json(str(d), 'M', 'brief')
        rp = subprocess.run([sys.executable, str(SCRIPTS / 'dispatch.py'), 'record', str(d / f'{disp["name"]}.dispatch.json'),
                             '--tokens', '5000', '--agent-id', 'ag-9', '--duration-ms', '4321'], capture_output=True, text=True, timeout=60)
        r0 = [json.loads(l) for l in (d / 'runs.jsonl').read_text().splitlines()]
        expect('record: a solo dispatch file records end to end with cost, agent_id and duration', rp.returncode == 0 and len(r0) == 1
               and r0[0]['cost_usd'] and r0[0].get('agent_id') == 'ag-9' and r0[0].get('duration_ms') == 4321)
        (d / 'runs.jsonl').unlink()
        rc, disp = dispatch_json(str(d), 'M', 'brief')
        complete(d, disp['attempt_id'], 'M', None, None, agent_id='ag-8', duration_ms=77)
        r1 = [json.loads(l) for l in (d / 'runs.jsonl').read_text().splitlines()][0]
        expect('complete: with nothing to price, agent_id and duration still land', r1.get('agent_id') == 'ag-8' and r1.get('duration_ms') == 77
               and r1['cost_usd'] is None)
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
    r.add_argument('--tier', required=True, choices=sorted(TIERS) + sorted(TIER_ALIASES),
                   help='L1, L2, or L3 (S, M, L: deprecated aliases)')  # ALIAS_OK
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument('--brief')
    g.add_argument('--brief-file')
    r.add_argument('--backend', default=os.environ.get('SDLC_BACKEND', 'claude'))
    r.add_argument('--exec', action='store_true', help='Claude: start the headless session instead of printing the dispatch JSON')
    r.add_argument('--cwd')
    r.add_argument('--worktree', metavar='NAME', help='create .worktrees/NAME on a new branch NAME first '
                   '(unless it exists) and run the session there')
    r.add_argument('--no-worktree', action='store_true', help='stay in this checkout even when another solo is live')
    r.add_argument('--timeout', type=float)
    r.add_argument('--raw-out', help='also save the session stdout (the result JSON) to this file')
    c = sub.add_parser('complete', help='price a finished solo sub-agent row from its transcript usage or notice tokens')
    c.add_argument('--task-dir', required=True)
    c.add_argument('--attempt', required=True, help='attempt_id (or a prefix) from the dispatch JSON')
    c.add_argument('--tier', required=True, choices=sorted(TIERS) + sorted(TIER_ALIASES))
    c.add_argument('--transcript')
    c.add_argument('--tokens', type=int)
    sub.add_parser('selftest')
    a = p.parse_args()
    if a.cmd == 'selftest':
        return selftest()
    if a.tier in TIER_ALIASES:
        print(f'solo_run.py: --tier {a.tier} is deprecated; use --tier {tier_of(a.tier)}', file=sys.stderr)
        a.tier = tier_of(a.tier)
    if a.cmd == 'complete':
        cost = complete(a.task_dir, a.attempt, a.tier, a.transcript, a.tokens)
        print('solo_run.py: no row priced (no usage, or no unpriced solo row for that attempt)' if cost is None else 'priced $%.4f' % cost)
        return 0 if cost is not None else 2
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
        wt = a.worktree
        if not wt and not a.no_worktree:
            wt = auto_worktree(task_dir, a.cwd)
            if wt:
                print(f'solo_run.py: another solo is live in this checkout; using worktree {wt} (--no-worktree to stay)', file=sys.stderr)
        if a.backend == 'claude' and not a.exec:
            path = ensure_worktree(wt, a.cwd) if wt else None
            rc, d = dispatch_json(task_dir, a.tier, brief, path)
            if d:
                print(json.dumps(d, indent=2))
            return rc
        cwd = ensure_worktree(wt, a.cwd) if wt else a.cwd
        return run(task_dir, a.tier, brief, a.backend, cwd, a.timeout, a.raw_out)
    except Refuse as exc:
        print(f'solo_run.py: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
