#!/usr/bin/env python3
"""The pre-launch half of run.sh for Claude sub-agent dispatch (Python 3.9+).

  dispatch.py prepare [--dry-run] <role> <level> <handoff.md>
  dispatch.py selftest

prepare runs every gate and decision run.sh makes before it launches a role and prints a dispatch JSON the
conductor passes to the Agent tool (design: docs/lean-sdlc/subagent-mode.md sections 1 to 3). It launches
nothing and never edits run.sh. Order, as in run.sh: row lookup, preflight, family rules, mailbox notice,
goal precheck, lane gate, spec gate, budget gate, then the one write section.

  row lookup   role:level must be a pipeline row of adapters/claude/levels.json (solo is dispatched by
               T-0284); agents/<role>-<level>.md must exist and every skill its role file declares must exist.
  preflight    the handoff exists and the current directory is a git work tree with a commit.
  family       a verifier never runs on the newest build's model family (a Fable or Sonnet build moves it to
               Opus, same effort); a plan-reviewer never on the newest planner's (an Opus planner moves it
               to Fable). Both read the first model=<[a-z]*> token of the newest result by order.py; a
               verifier whose dir holds no builder result reads the highest-numbered live step-<n>/ that
               holds one (step-<n>.superseded-<k>/ is left out).
  goal         planner or plan-reviewer on a task handoff: steps.py precheck.        Refusal exit 2.
  lane         planner, builder, plan-reviewer on a solo-lane ticket: steps.py lane --check, exit 5, unless
               SDLC_LANE_OVERRIDE="<reason>" (appended once to skips.md, carried as lane_override).
  specgate     plan-reviewer: specgate.py check, exit 2, unless SDLC_SPECGATE=off (carried as specgate).
  budget       budget.py report: warn or over with no ack, exit 4. No budget or no ticket proceeds.
  lock         replaces run_lifecycle.py's directory lock. Under a brief file lock, every running attempt
               record in the handoff dir whose parent pid is dead is marked interrupted and recovered; one
               whose parent is alive refuses, exit 2. A second prepare therefore cannot start while a
               dispatched role is unrecorded. A refusal writes no new file (a dead-parent recovery
               before the refusal still marks that old record interrupted).

Names. The result stem is <role>-<level>, or <role>-<level>-<k> for the lowest free k >= 2, where a stem is
taken when any file <stem>.* sits in the handoff dir (run_lifecycle.py's rule, a superset of run.sh's
.md and .request.json check, so an interrupted attempt's record bumps k and is never overwritten). The
Agent name is <role>-<level>-<slug>[-<k>] (slug: the task dir name, plus -s<n> for a step dir, cut to fit 64
characters). Records are keyed by the stem: <stem>.attempt.json and <stem>.dispatch.json, beside the handoff.

Records. <stem>.attempt.json holds run_lifecycle.py's keys with status running, transport subagent, and
parent_pid (SDLC_DISPATCH_PARENT_PID, else the first ancestor process named claude, else the first ancestor
that is not a shell or python; never the short-lived tool shell). <stem>.dispatch.json holds subagent_type,
name, model, effort, prompt (the brief), result, tmp_prefix, base_sha, and what T-0278 needs to write the
runs.jsonl line (lane_override, specgate, handoff_sha256, routing_reason). A builder or verifier also writes
base-sha as run.sh does. --dry-run prints the JSON and writes nothing, takes no lock, and skips recovery.

Brief. The run.sh prompt (Handoff, Artifacts dir, the result and output-format sentence) plus a Tree line, a
throwaway-worktree prefix line (.worktrees/tmp/<Agent name>), and for builder and verifier a Base sha line,
since a sub-agent cannot read SDLC_BASE_SHA from its environment.

Exit codes as run.sh: 0 ok, 2 usage, preflight, goal, spec gate, or a running attempt, 4 budget, 5 lane.
Not carried over: the .nvmrc PATH change (a sub-agent inherits the parent's environment) and the skill
appending (the generated definition's skills: list loads them).
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(HERE))
import budget  # noqa: E402
import claude_roles  # noqa: E402
import order  # noqa: E402
import run_lifecycle  # noqa: E402

SHELLS = ('sh', 'bash', 'zsh', 'dash', 'fish', 'ksh', 'env', 'sudo', 'timeout', 'tmux', 'login')
NAME_MAX = 64
GATES = ('preflight', 'goal', 'lane', 'specgate', 'budget', 'lock')


class Refuse(Exception):
    """A gate refused; rc is the run.sh exit code and lines go to stderr."""

    def __init__(self, rc, *lines):
        super().__init__('\n'.join(lines))
        self.rc = rc
        self.lines = lines


def say(msg):
    print('dispatch.py: ' + msg, file=sys.stderr)


def script(name, *args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / name)] + [str(a) for a in args],
                          capture_output=True, text=True, cwd=cwd)


def git(*args, cwd=None):
    return subprocess.run(['git'] + list(args), capture_output=True, text=True, cwd=cwd)


def model_of(path):
    """The first model=<[a-z]*> token of a result file, as run.sh's grep -o does."""
    m = re.search(r'model=([a-z]*)', Path(path).read_text(encoding='utf-8', errors='replace'))
    return m.group(1) if m else ''


def step_build(directory):
    """Newest builder result of the highest-numbered live step-<n>/ under directory that holds one."""
    best, built = -1, None
    for sd in Path(directory).glob('step-*'):
        m = re.fullmatch(r'step-(\d+)', sd.name)
        if not m or not sd.is_dir() or int(m.group(1)) <= best:
            continue
        found = order.newest(str(sd), 'builder')
        if found:
            best, built = int(m.group(1)), found
    return built


def family(role, model, directory):
    if role == 'verifier':
        built = order.newest(str(directory), 'builder') or step_build(directory)
        if built and model == model_of(built) and model in ('fable', 'sonnet'):
            return 'opus'
    elif role == 'plan-reviewer':
        planned = order.newest(str(directory), 'planner')
        if planned and model == model_of(planned) and model == 'opus':
            return 'fable'
    return model


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def parent_pid():
    """(pid, source): the session that owns this dispatch, so a dead one marks the attempt orphaned."""
    forced = os.environ.get('SDLC_DISPATCH_PARENT_PID', '')
    if forced.isdigit():
        return int(forced), 'env'
    pid, seen, fallback = os.getppid(), 0, None
    while pid > 1 and seen < 32:
        out = subprocess.run(['ps', '-o', 'ppid=,comm=', '-p', str(pid)], capture_output=True, text=True).stdout.strip()
        if not out:
            break
        ppid, _, comm = out.partition(' ')
        name = os.path.basename(comm.strip())
        if 'claude' in comm.lower():
            return pid, 'claude'
        if fallback is None and name and not name.startswith('python') and name.lstrip('-') not in SHELLS:
            fallback = pid
        pid, seen = int(ppid) if ppid.strip().isdigit() else 0, seen + 1
    if fallback:
        return fallback, 'ancestor'
    return os.getppid(), 'ppid'


def slug_of(directory):
    d, step = Path(directory), ''
    m = re.fullmatch(r'step-(\d+)', d.name)
    if m:
        step, d = '-s' + m.group(1), d.parent
    return (re.sub(r'[^a-z0-9]+', '-', d.name.lower()).strip('-') or 'task'), step


def agent_name(role, level, directory, k):
    slug, step = slug_of(directory)
    head, tail = '%s-%s-' % (role, level), step + ('-%d' % k if k > 1 else '')
    return head + slug[:max(1, NAME_MAX - len(head) - len(tail))].strip('-') + tail


def next_stem(directory, role, level):
    stem, k = '%s-%s' % (role, level), 1
    while any(Path(directory).glob(stem + '.*')):
        k += 1
        stem = '%s-%s-%d' % (role, level, k)
    return stem, k


def build_base(directory):
    """The build-start commit run.sh stores in base-sha: HEAD, or the stored sha kept valid."""
    stored = ''
    f = Path(directory) / 'base-sha'
    if f.is_file():
        lines = f.read_text(encoding='utf-8', errors='replace').splitlines()
        stored = re.sub(r'\s', '', lines[0]) if lines else ''
    base = ''
    if stored and git('rev-parse', '-q', '--verify', stored + '^{commit}').returncode == 0 \
            and git('merge-base', '--is-ancestor', stored, 'HEAD').returncode == 0:
        base = git('rev-parse', stored + '^{commit}').stdout.strip()
        merges = git('rev-list', '--first-parent', '--merges', base + '..HEAD').stdout.split()
        if merges:
            base = merges[0]
    return stored, base or git('rev-parse', 'HEAD').stdout.strip()


def lane_gate(role, directory, plugin):
    """None to proceed, else the (lane_dir, size) of a solo-lane ticket that needs the solo agent."""
    lane_dir = Path(directory).parent if Path(directory).name.startswith('step-') else Path(directory)
    handoff = lane_dir / 'handoff.md'
    if not handoff.is_file() or not re.search(r'^id: *T-[0-9]+', handoff.read_text(encoding='utf-8', errors='replace'), re.M):
        return None
    skips = lane_dir / 'skips.md'
    if skips.is_file():
        recorded = [l for l in skips.read_text(encoding='utf-8', errors='replace').splitlines() if re.match(r'(- )?lane: ', l, re.I)]
        if recorded and not re.match(r'(- )?lane: *solo', recorded[-1], re.I):
            return None
    lane = (script('steps.py', 'lane', '--check', lane_dir).stdout.splitlines() or [''])[0]
    if lane != 'solo':
        return None
    m = re.search(r'^size: *([SMLX]*)', handoff.read_text(encoding='utf-8', errors='replace'), re.M)
    return lane_dir, (m.group(1) if m else '') or 'M'


def mailbox(role):
    total = 0
    for who in (role, 'claude'):
        p = script('messages.py', 'count', '--receiver', who)
        if p.returncode == 0 and p.stdout.strip().isdigit():
            total += int(p.stdout.strip())
    if total > 0:
        say('%d new message(s) for %s; read with messages.py' % (total, role))


def settle(directory, dry_run):
    """Refuse while a dispatched attempt in directory is alive; mark dead-parent ones interrupted."""
    live, recovered = [], []
    for path in sorted(Path(directory).glob('*.attempt.json')):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except ValueError:
            raise Refuse(2, 'dispatch.py: unreadable attempt record, inspect it first: ' + str(path))
        if not isinstance(data, dict) or data.get('status') != 'running':
            continue
        pid = data.get('parent_pid') or data.get('owner_pid')
        if data.get('backend', 'claude') == 'claude' and isinstance(pid, int) and not pid_alive(pid):
            if not dry_run:
                data.update(status='interrupted', finished_at=run_lifecycle.now(),
                            recovery='Parent session ended with no terminal record. Inspect git status and the artifacts dir before a new attempt; never replay an old report.')
                run_lifecycle.write(path, data)
                (Path(directory) / ('%s-%s.running' % (data.get('role'), data.get('level')))).unlink(missing_ok=True)
            recovered.append(path.name)
        else:
            live.append('%s (pid %s)' % (path.name, pid))
    if live:
        raise Refuse(2, 'dispatch.py: an attempt is still running in %s: %s; record it, or wait for it, before dispatching another role' % (directory, ', '.join(live)))
    return recovered


def prepare(role, level, handoff, plugin=PLUGIN, dry_run=False, skip=()):
    """Run the gates and write the records; returns the dispatch dict. skip names gates to disable (selftest only)."""
    plugin = Path(plugin)
    if os.environ.get('SDLC_BACKEND', 'claude') != 'claude':
        raise Refuse(2, 'dispatch.py prepare is the Claude host path; Codex dispatches through run.sh')
    try:
        rows = claude_roles.table(plugin)
    except claude_roles.TableError as e:
        raise Refuse(2, 'dispatch.py: ' + str(e))
    if role == 'solo' or level not in rows.get(role, {}):
        raise Refuse(2, 'usage: dispatch.py prepare <role> <level> <handoff.md>  (no pipeline row %s:%s in adapters/claude/levels.json)' % (role, level))
    model, effort = rows[role][level]
    handoff = Path(os.path.abspath(handoff))
    directory = handoff.parent
    if 'preflight' not in skip:
        if not handoff.is_file():
            raise Refuse(2, 'handoff not found: ' + str(handoff))
        if git('rev-parse', '--is-inside-work-tree').returncode != 0:
            raise Refuse(2, 'not a git repo: run git init and commit first')
        if git('rev-parse', '--verify', '-q', 'HEAD').returncode != 0:
            raise Refuse(2, 'git repo has no commit: commit first')
    definition = plugin / 'agents' / ('%s-%s.md' % (role, level))
    if not definition.is_file():
        raise Refuse(2, 'no generated definition %s; run: python3 %s generate' % (definition, HERE / 'claude_roles.py'))
    try:
        for sk in claude_roles.source(plugin, role)[1]:
            if not (plugin / 'skills' / sk / 'SKILL.md').is_file():
                raise Refuse(2, 'agent %s declares missing skill: %s' % (role, sk))
    except claude_roles.TableError as e:
        raise Refuse(2, 'dispatch.py: ' + str(e))

    model = family(role, model, directory)
    if not dry_run:
        mailbox(role)

    task_handoff = handoff.name == 'handoff.md' and not directory.name.startswith('step-')
    if 'goal' not in skip and role in ('planner', 'plan-reviewer') and task_handoff:
        p = script('steps.py', 'precheck', directory)
        if p.returncode != 0:
            raise Refuse(2, (p.stdout + p.stderr).rstrip('\n'),
                         'dispatch.py: steps.py precheck refused the task handoff in %s; add a ## Goal section' % directory)

    lane_override = ''
    if 'lane' not in skip and role in ('planner', 'builder', 'plan-reviewer'):
        solo = lane_gate(role, directory, plugin)
        if solo:
            lane_dir, size = solo
            lane_override = os.environ.get('SDLC_LANE_OVERRIDE', '')
            if not lane_override:
                raise Refuse(5, 'dispatch.py: lane solo for %s: use the solo agent: python3 %s run --task-dir %s --tier %s --brief "<brief>"'
                             % (lane_dir, HERE / 'solo_run.py', lane_dir, size),
                             'dispatch.py: or set SDLC_LANE_OVERRIDE="<reason the chain is needed>" to dispatch %s anyway (recorded in skips.md)' % role)

    specgate = ''
    if role == 'plan-reviewer' and 'specgate' not in skip:
        if os.environ.get('SDLC_SPECGATE') == 'off':
            say('SDLC_SPECGATE=off: spec gate skipped')
            specgate = 'off'
        else:
            p = script('specgate.py', 'check', directory)
            if p.returncode != 0:
                out = (p.stdout + p.stderr).rstrip('\n')
                raise Refuse(2, *([out] if out else []),
                             'dispatch.py: specgate.py check refused the plan in %s; replan, or set SDLC_SPECGATE=off' % directory)

    if 'budget' not in skip:
        ticket = budget.ticket_of(handoff)
        rep = budget.report(ticket) if ticket is not None else None
        if rep and rep['state'] != 'ok':
            raise Refuse(4, 'dispatch.py: budget %s%%: ask the user; budget.py ack' % rep['percent'])

    lock = None
    try:
        if not dry_run:
            try:
                lock = run_lifecycle.lock(directory)
            except ValueError as e:
                raise Refuse(2, 'dispatch.py: ' + str(e))
            if 'lock' not in skip:
                recovered = settle(directory, dry_run)
                if recovered:
                    say('recovered stale attempt(s) before this dispatch: ' + ', '.join(recovered))
        stem, k = next_stem(directory, role, level)
        name = agent_name(role, level, directory, k)
        result = directory / (stem + '.md')
        toplevel = git('rev-parse', '--show-toplevel').stdout.strip() or os.getcwd()
        tmp_prefix = str(Path(toplevel) / '.worktrees' / 'tmp' / name)

        base = None
        if role in ('builder', 'verifier'):
            stored, base = build_base(directory)
            if not dry_run and base != stored:
                (directory / 'base-sha').write_text(base + '\n', encoding='utf-8')

        prompt = ('Handoff: %s\nArtifacts dir: %s\nYour final message is saved verbatim as %s. Make it exactly the output format your '
                  'instructions define: start with its first heading, with nothing before it and nothing after the last section.\n'
                  'Tree: %s (run every Bash call as cd %s && ...; the shell keeps no working directory between calls)\n'
                  'Throwaway worktrees only under %s (git worktree add --detach "%s/<name>" HEAD creates the parents); remove them when done.'
                  % (handoff, directory, result, toplevel, toplevel, tmp_prefix, tmp_prefix))
        if base:
            prompt += '\nBase sha: %s (the commit this build started from; diff scope criteria against it)' % base

        sha = hashlib.sha256(handoff.read_bytes()).hexdigest()
        reason = os.environ.get('SDLC_ROUTING_REASON', '').strip()
        pid, source = parent_pid()
        dispatch = dict(subagent_type='sdlc-lite:%s-%s' % (role, level), name=name,
                        description='%s %s: %s' % (role, level, slug_of(directory)[0]),
                        model=model, effort=effort, prompt=prompt,
                        run_in_background=os.environ.get('SDLC_HEADLESS') != '1',
                        role=role, level=level, result_name=stem, result=str(result), tmp_prefix=tmp_prefix,
                        base_sha=base, tree=toplevel, handoff=str(handoff), artifacts_dir=str(directory),
                        handoff_sha256=sha, shared_with_builder=False, lane_override=lane_override, specgate=specgate,
                        routing_reason=reason or 'Caller selected this role and level; no task-specific rationale supplied.',
                        attempt_file=str(directory / (stem + '.attempt.json')),
                        dispatch_file=str(directory / (stem + '.dispatch.json')), dry_run=dry_run)
        if dry_run:
            return dispatch
        if lane_override:
            skips, line = directory.parent if directory.name.startswith('step-') else directory, 'lane override: ' + lane_override
            skips = skips / 'skips.md'
            if line not in (skips.read_text(encoding='utf-8').splitlines() if skips.is_file() else []):
                with skips.open('a', encoding='utf-8') as f:
                    f.write(line + '\n')
        attempt = dict(attempt_id=uuid.uuid4().hex, name=stem, agent_name=name, role=role, level=level, backend='claude',
                       transport='subagent', model=model, effort=effort, routing_reason=dispatch['routing_reason'],
                       reason_source='caller' if reason else 'fallback', status='running', started_at=run_lifecycle.now(),
                       project=os.getcwd(), handoff=str(handoff), parent_pid=pid, parent_pid_source=source, handoff_sha256=sha)
        dispatch['attempt_id'] = attempt['attempt_id']
        run_lifecycle.write(Path(dispatch['attempt_file']), attempt)
        run_lifecycle.write(Path(dispatch['dispatch_file']), dispatch)
        return dispatch
    finally:
        if lock is not None:
            lock.close()


def main(argv):
    ap = argparse.ArgumentParser(prog='dispatch.py', description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    p = sub.add_parser('prepare', help='run the pre-launch gates and print the dispatch JSON')
    p.add_argument('--dry-run', action='store_true', help='print the JSON; write no record, take no lock')
    for key in ('role', 'level', 'handoff'):
        p.add_argument(key)
    sub.add_parser('selftest', help='run the regression cases in temp repos')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    try:
        out = prepare(args.role, args.level, args.handoff, dry_run=args.dry_run)
    except Refuse as r:
        for line in r.lines:
            print(line, file=sys.stderr)
        return r.rc
    except (OSError, ValueError) as e:
        print('dispatch.py: ' + str(e), file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2))
    return 0


# ---- selftest ----

SGPLAN = ('<!-- role=planner level=L1 model=sonnet effort=medium -->\n## Goal\nx\n\n## Step 1: Gates\nlevel: L1\n### Do\nx\n'
          '### Acceptance criteria\n- (guard) `bash plugins/sdlc-lite/scripts/check.sh`\n\n## Assumptions\nNone\n\n## Risks\nNone\n')


@contextlib.contextmanager
def clean_env(**extra):
    saved = dict(os.environ)
    for k in [k for k in os.environ if k.startswith('SDLC_')]:
        del os.environ[k]
    os.environ.update(extra)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(saved)


@contextlib.contextmanager
def cwd(path):
    old = os.getcwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(old)


def selftest():
    failures = []

    def case(label, ok):
        print('%s: %s' % ('ok' if ok else 'FAIL', label))
        if not ok:
            failures.append(label)

    def init_repo(path, commit=True):
        path.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(path)], check=True)
        if commit:
            (path / 'f.txt').write_text('x\n')
            subprocess.run(['git', '-C', str(path), 'add', '-A'], check=True)
            subprocess.run(['git', '-C', str(path), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
                            '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'init'], check=True)

    def put(path, text='## Goal\nx\n'):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def ticket(path, size, budget_usd=None):
        extra = ['budget_usd: %s' % budget_usd] if budget_usd else []
        put(path / 'handoff.md', '\n'.join(['---', 'id: T-0900', 'title: "x"', 'type: chore', 'status: ready', 'size: ' + size,
                                            'priority: P2', 'depends: []', 'created: 2026-10-05'] + extra + ['---', '', '## Goal', 'x', '']))

    def prep(repo, role, level, rel, *flags, **env):
        """(rc, dispatch dict or None, stderr) of an in-process prepare."""
        err, out = io.StringIO(), io.StringIO()
        with clean_env(**env), cwd(repo), contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            rc = main(['prepare'] + list(flags) + [role, level, rel])
        return rc, (json.loads(out.getvalue()) if rc == 0 else None), err.getvalue()

    def runsh(repo, role, level, rel, **env):
        """(rc, model, effort, result name, stderr) of SDLC_DRY_RUN=1 run.sh, its argv decoded through bash."""
        with clean_env(SDLC_DRY_RUN='1', **env):
            p = subprocess.run(['bash', str(HERE / 'run.sh'), role, level, rel], cwd=str(repo), capture_output=True, text=True)
        if p.returncode != 0:
            return p.returncode, None, None, None, p.stderr
        argv = subprocess.run(['bash', '-c', 'eval "set -- $1"; printf "%s\\0" "$@"', 'x', p.stdout.strip()],
                              capture_output=True).stdout.decode().split('\0')
        m = re.search(r'saved verbatim as (.+?\.md)\. Make', argv[-2])
        return 0, argv[argv.index('--model') + 1], argv[argv.index('--effort') + 1], os.path.basename(m.group(1)) if m else None, p.stderr

    def same(label, repo, role, level, rel, **env):
        """prepare --dry-run and run.sh dry run agree on model, effort, result name, and exit code."""
        rc, got, _ = prep(repo, role, level, rel, '--dry-run', **env)
        rrc, model, effort, name, _ = runsh(repo, role, level, rel, **env)
        ok = rc == rrc and (rc != 0 or (got['model'], got['effort'], os.path.basename(got['result'])) == (model, effort, name))
        case('parity %s: %s %s -> %s' % (label, role, level, ('exit %d' % rc) if rc else '%s %s %s' % (got['model'], got['effort'], os.path.basename(got['result']))), ok)
        return rc, got

    with tempfile.TemporaryDirectory(prefix='dispatch-selftest.') as tmp:
        tmp = Path(os.path.realpath(tmp))
        repo = tmp / 'repo'
        init_repo(repo)
        sdlc = repo / '.sdlc'
        rows = [(r, l) for r, ls in claude_roles.table(PLUGIN).items() if r != 'solo' for l in ls]

        # 1. Every level-table row, plain task handoff, no build or plan around.
        put(sdlc / 't' / 'handoff.md')
        for role, level in rows:
            same('row', repo, role, level, '.sdlc/t/handoff.md')

        # 2. Verifier family rule: newest build in the step dir, by runs.jsonl order.
        sw = sdlc / 't' / 'step-1'
        put(sw / 'handoff.md', '## Step 1\n')
        for lvl, mod in (('L5', 'fable'), ('L1', 'sonnet'), ('L3', 'opus')):
            put(sw / ('builder-%s.md' % lvl), '<!-- role=builder level=%s model=%s effort=x -->\n' % (lvl, mod))
        for newest in ('L5', 'L1', 'L3'):
            others = [l for l in ('L5', 'L1', 'L3') if l != newest]
            (sw / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'builder', 'level': l, 'file': 'builder-%s.md' % l}) + '\n' for l in others + [newest]))
            for vlevel in ('L1', 'L2', 'L3'):
                same('verifier after builder %s' % newest, repo, 'verifier', vlevel, '.sdlc/t/step-1/handoff.md')
        rc, got = same('verifier swap value', repo, 'verifier', 'L2', '.sdlc/t/step-1/handoff.md')
        case('verifier L2 after an opus build keeps sonnet', got['model'] == 'sonnet')
        (sw / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'builder', 'level': l, 'file': 'builder-%s.md' % l}) + '\n' for l in ('L3', 'L1')))
        rc, got = same('verifier swap value', repo, 'verifier', 'L2', '.sdlc/t/step-1/handoff.md')
        case('verifier L2 after a sonnet build moves to opus, same effort', (got['model'], got['effort']) == ('opus', 'high'))
        rc, got = same('verifier swap value', repo, 'verifier', 'L3', '.sdlc/t/step-1/handoff.md')
        case('verifier L3 after a sonnet build keeps fable', got['model'] == 'fable')
        (sw / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'builder', 'level': l, 'file': 'builder-%s.md' % l}) + '\n' for l in ('L1', 'L5')))
        rc, got = same('verifier swap value', repo, 'verifier', 'L3', '.sdlc/t/step-1/handoff.md')
        case('verifier L3 after a fable build moves to opus xhigh', (got['model'], got['effort']) == ('opus', 'xhigh'))
        shutil.rmtree(sw)

        # 3. Verifier at a task dir: the highest live step holds the build; superseded dirs are left out.
        td = sdlc / 'td'
        put(td / 'handoff.md')

        def build(step, lvl, mod):
            put(td / step / ('builder-%s.md' % lvl), '<!-- role=builder level=%s model=%s effort=x -->\n' % (lvl, mod))
        for label, setup in (('sonnet step build', lambda: build('step-1', 'L1', 'sonnet')),
                             ('fable step build', lambda: build('step-1', 'L5', 'fable')),
                             ('superseded opus ignored', lambda: (build('step-1', 'L1', 'sonnet'), build('step-2.superseded-1', 'L3', 'opus'))),
                             ('superseded sonnet ignored', lambda: (build('step-1', 'L3', 'opus'), build('step-2.superseded-1', 'L1', 'sonnet'))),
                             ('step-10 sonnet beats step-2 opus', lambda: (build('step-2', 'L3', 'opus'), build('step-10', 'L1', 'sonnet'))),
                             ('step-10 opus beats step-2 sonnet', lambda: (build('step-2', 'L1', 'sonnet'), build('step-10', 'L3', 'opus'))),
                             ('task dir build wins over step dirs', lambda: (put(td / 'builder-L3.md', '<!-- role=builder level=L3 model=opus effort=x -->\n'), build('step-1', 'L1', 'sonnet'))),
                             ('no build anywhere', lambda: put(td / 'step-1' / 'handoff.md', '## Step 1\n'))):
            for child in list(td.iterdir()):
                if child.name != 'handoff.md':
                    shutil.rmtree(child) if child.is_dir() else child.unlink()
            setup()
            for vlevel in ('L1', 'L3'):
                same('task dir, ' + label, repo, 'verifier', vlevel, '.sdlc/td/handoff.md')
        shutil.rmtree(td)

        # 4. Plan-reviewer family rule after planners of each family.
        pr = sdlc / 'pr'
        put(pr / 'handoff.md')

        def planners(*pairs):
            for child in list(pr.iterdir()):
                if child.name != 'handoff.md':
                    child.unlink()
            for lvl, mod in pairs:
                put(pr / ('planner-%s.md' % lvl), '<!-- role=planner level=%s model=%s effort=x -->\n' % (lvl, mod))
            (pr / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'planner', 'level': l, 'file': 'planner-%s.md' % l}) + '\n' for l, _ in pairs))
        planners()
        _, got = same('plan-reviewer, no planner', repo, 'plan-reviewer', 'L1', '.sdlc/pr/handoff.md')
        case('plan-reviewer with no planner keeps opus high', (got['model'], got['effort']) == ('opus', 'high'))
        for label, pairs, want in (('sonnet planner', [('L1', 'sonnet')], 'opus'), ('fable planner', [('L2', 'fable')], 'opus'),
                                   ('opus planner', [('L3', 'opus')], 'fable'),
                                   ('opus planner then fable planner', [('L2', 'opus'), ('L3', 'fable')], 'opus'),
                                   ('fable planner then opus planner', [('L3', 'fable'), ('L2', 'opus')], 'fable')):
            planners(*pairs)
            _, got = same(label, repo, 'plan-reviewer', 'L1', '.sdlc/pr/handoff.md')
            case('plan-reviewer after %s runs %s' % (label, want), got['model'] == want)
        shutil.rmtree(pr)

        # 5. Result naming: the lowest free k, as run.sh and run_lifecycle.py.
        nm = sdlc / 'nm'
        put(nm / 'handoff.md')
        for taken, want in (([], 'planner-L3.md'), (['planner-L3.md'], 'planner-L3-2.md'),
                            (['planner-L3.md', 'planner-L3-2.md'], 'planner-L3-3.md')):
            for child in list(nm.iterdir()):
                if child.name != 'handoff.md':
                    child.unlink()
            for t in taken:
                put(nm / t, '## Goal\n')
            _, got = same('naming ' + want, repo, 'planner', 'L3', '.sdlc/nm/handoff.md')
            case('result name is ' + want, os.path.basename(got['result']) == want)
        shutil.rmtree(nm)

        # 6. Refusals: the same exit code as run.sh, nothing written, and a negative control that
        # disables the one gate and lets the bad input through.
        def refused(label, rc_want, role, level, rel, gate, **env):
            before = sorted(str(p) for p in repo.rglob('*') if '.git' not in p.parts)
            rc, got, err = prep(repo, role, level, rel, **env)
            rrc = runsh(repo, role, level, rel, **env)[0]
            case('%s: prepare exits %d like run.sh (got %d, run.sh %d)' % (label, rc_want, rc, rrc), rc == rc_want == rrc)
            case('%s: a refusal wrote nothing' % label, before == sorted(str(p) for p in repo.rglob('*') if '.git' not in p.parts))
            if gate:
                with clean_env(**env), cwd(repo), contextlib.redirect_stderr(io.StringIO()):
                    try:
                        passed = prepare(role, level, rel, dry_run=True, skip=(gate,))
                    except Refuse as r:
                        passed = None
                case('%s: negative control, without the %s gate the bad input goes through' % (label, gate), bool(passed))
            return err

        for role in ('planner', 'plan-reviewer'):  # goal precheck
            put(sdlc / 'gp' / 'handoff.md', '## Task goal\nx\n')
            err = refused('goal precheck ' + role, 2, role, 'L1', '.sdlc/gp/handoff.md', 'goal')
            case('goal precheck %s names ## Goal' % role, '## Goal' in err)
        put(sdlc / 'gp' / 'handoff.md', '## Goal\nx\n')
        case('goal precheck passes with a ## Goal section', prep(repo, 'planner', 'L1', '.sdlc/gp/handoff.md', '--dry-run')[0] == 0)

        put(sdlc / 'sg' / 'handoff.md')  # spec gate
        put(sdlc / 'sg' / 'planner-L1.md', SGPLAN)
        err = refused('spec gate', 2, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', 'specgate')
        case('spec gate names the finding and the way out', 'slow guard' in err and 'SDLC_SPECGATE=off' in err)
        rc, got, err = prep(repo, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', '--dry-run', SDLC_SPECGATE='off')
        case('SDLC_SPECGATE=off lets it through and is carried', rc == 0 and got['specgate'] == 'off' and 'spec gate skipped' in err)
        rc, got, err = prep(repo, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', '--dry-run')
        case('without the knob the spec gate still refuses', rc == 2)
        put(sdlc / 'sg' / 'planner-L1.md', SGPLAN.replace('## Step 1: Gates', 'guard timeout: 900\n\n## Step 1: Gates'))
        case('a plan with a guard timeout passes the spec gate', prep(repo, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', '--dry-run')[0] == 0)

        ticket(sdlc / 'ls', 'S')  # lane gate
        for role in ('planner', 'builder', 'plan-reviewer'):
            err = refused('lane gate ' + role, 5, role, 'L1', '.sdlc/ls/handoff.md', 'lane')
        case('lane gate prints the solo command and the override', 'solo_run.py run --task-dir' in err and '--tier S' in err and 'SDLC_LANE_OVERRIDE' in err)
        put(sdlc / 'ls' / 'step-1' / 'handoff.md', '## Step 1\n')
        refused('lane gate on a step', 5, 'builder', 'L1', '.sdlc/ls/step-1/handoff.md', 'lane')
        for role in ('verifier', 'filer', 'scout'):
            case('lane gate leaves %s alone' % role, prep(repo, role, 'L1', '.sdlc/ls/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'll', 'L')
        case('lane gate leaves a size L ticket alone', prep(repo, 'planner', 'L1', '.sdlc/ll/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'lk', 'S')
        put(sdlc / 'lk' / 'skips.md', '- lane: full\n')
        case('lane gate leaves a recorded non-solo lane alone', prep(repo, 'planner', 'L1', '.sdlc/lk/handoff.md', '--dry-run')[0] == 0)
        rc, got, err = prep(repo, 'planner', 'L1', '.sdlc/ls/handoff.md', SDLC_LANE_OVERRIDE='chain needs a merge step')
        case('SDLC_LANE_OVERRIDE proceeds and is carried', rc == 0 and got['lane_override'] == 'chain needs a merge step')
        skips = sdlc / 'ls' / 'skips.md'
        case('the override is appended to skips.md', skips.read_text() == 'lane override: chain needs a merge step\n')
        for f in ('planner-L1.attempt.json', 'planner-L1.dispatch.json'):
            (sdlc / 'ls' / f).unlink()
        prep(repo, 'planner', 'L1', '.sdlc/ls/handoff.md', SDLC_LANE_OVERRIDE='chain needs a merge step')
        case('the override line is appended once', skips.read_text().count('lane override:') == 1)
        for f in list((sdlc / 'ls').glob('planner-L1*')):
            f.unlink()

        ticket(sdlc / 'bg', 'M', budget_usd=10)  # budget gate (verifier: not lane gated)
        put(sdlc / 'bg' / 'runs.jsonl', json.dumps({'role': 'builder', 'cost_usd': 9, 'attempt_id': 'a1'}) + '\n')
        err = refused('budget gate', 4, 'verifier', 'L1', '.sdlc/bg/handoff.md', 'budget')
        case('budget gate names the percent and budget.py ack', '90%' in err and 'budget.py ack' in err)
        put(sdlc / 'bg' / 'budget-ack.md', '---\nusd: 30\nreason: selftest\n---\n')
        case('a budget ack raises the ceiling and it passes', prep(repo, 'verifier', 'L1', '.sdlc/bg/handoff.md', '--dry-run')[0] == 0)
        (sdlc / 'bg' / 'budget-ack.md').unlink()
        put(sdlc / 'bg' / 'runs.jsonl', json.dumps({'role': 'builder', 'cost_usd': 1, 'attempt_id': 'a1'}) + '\n')
        case('under 80 percent passes', prep(repo, 'verifier', 'L1', '.sdlc/bg/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'bn', 'M')
        case('a ticket with no budget passes', prep(repo, 'verifier', 'L1', '.sdlc/bn/handoff.md', '--dry-run')[0] == 0)

        # preflight: handoff, row, git work tree, commit, generated definition, skills.
        case('preflight: a missing handoff exits 2 like run.sh', prep(repo, 'builder', 'L1', '.sdlc/none/handoff.md')[0] == 2
             == runsh(repo, 'builder', 'L1', '.sdlc/none/handoff.md')[0])
        case('preflight: an unknown row exits 2 like run.sh', prep(repo, 'builder', 'L9', '.sdlc/t/handoff.md')[0] == 2
             == runsh(repo, 'builder', 'L9', '.sdlc/t/handoff.md')[0])
        case('preflight: solo is not a pipeline row', prep(repo, 'solo', 'M', '.sdlc/t/handoff.md')[0] == 2)
        nogit = tmp / 'nogit'
        put(nogit / 'h.md')
        case('preflight: a directory outside a git work tree exits 2 like run.sh',
             prep(nogit, 'scout', 'L1', 'h.md')[0] == 2 == runsh(nogit, 'scout', 'L1', 'h.md')[0])
        nocommit = tmp / 'nocommit'
        init_repo(nocommit, commit=False)
        put(nocommit / 'h.md')
        case('preflight: a repo with no commit exits 2 like run.sh', prep(nocommit, 'scout', 'L1', 'h.md')[0] == 2 == runsh(nocommit, 'scout', 'L1', 'h.md')[0])
        with clean_env(), cwd(nocommit), contextlib.redirect_stderr(io.StringIO()):
            passed = prepare('scout', 'L1', 'h.md', dry_run=True, skip=('preflight',))
        case('preflight: negative control, without the gate a repo with no commit goes through', bool(passed))
        case('SDLC_BACKEND=codex is refused', prep(repo, 'scout', 'L1', '.sdlc/t/handoff.md', SDLC_BACKEND='codex')[0] == 2)
        lite = tmp / 'plugin'
        (lite / 'adapters').mkdir(parents=True)
        shutil.copytree(str(PLUGIN / 'adapters' / 'claude'), str(lite / 'adapters' / 'claude'))
        shutil.copytree(str(PLUGIN / 'agents'), str(lite / 'agents'))

        def with_plugin(role, level):
            try:
                with clean_env(), cwd(repo), contextlib.redirect_stderr(io.StringIO()):
                    return prepare(role, level, '.sdlc/t/handoff.md', plugin=lite, dry_run=True)
            except Refuse as r:
                return r.rc
        case('a role whose skills are missing exits 2', with_plugin('verifier', 'L1') == 2)
        shutil.copytree(str(PLUGIN / 'skills'), str(lite / 'skills'))
        case('the same role passes once its skills exist', isinstance(with_plugin('verifier', 'L1'), dict))
        (lite / 'agents' / 'scout-L1.md').unlink()
        case('a row with no generated definition exits 2', with_plugin('scout', 'L1') == 2)

        # 7. Records and the lock.
        rr = tmp / 'rr'
        init_repo(rr)
        put(rr / '.sdlc' / 'w' / 'handoff.md')
        live, sub = os.getpid(), subprocess.Popen([sys.executable, '-c', 'pass'])
        sub.wait()
        dead = sub.pid
        rc, got, err = prep(rr, 'builder', 'L1', '.sdlc/w/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live), SDLC_ROUTING_REASON='selftest reason')
        w = rr / '.sdlc' / 'w'
        case('prepare exits 0 and writes both records', rc == 0 and (w / 'builder-L1.attempt.json').is_file() and (w / 'builder-L1.dispatch.json').is_file())
        att = json.loads((w / 'builder-L1.attempt.json').read_text())
        case('attempt record: running, subagent transport, parent pid', (att['status'], att['transport'], att['parent_pid'], att['backend']) == ('running', 'subagent', live, 'claude'))
        case('attempt record carries the model, effort, handoff hash, and reason',
             (att['model'], att['effort'], att['routing_reason']) == ('sonnet', 'low', 'selftest reason')
             and att['handoff_sha256'] == hashlib.sha256((w / 'handoff.md').read_bytes()).hexdigest())
        disk = json.loads((w / 'builder-L1.dispatch.json').read_text())
        case('dispatch file equals the printed JSON apart from dry_run', disk == got and got['dry_run'] is False)
        for key in ('subagent_type', 'model', 'effort', 'name', 'result', 'tmp_prefix', 'base_sha', 'prompt'):
            case('dispatch JSON has %s' % key, key in got and got[key] is not None)
        case('subagent type, Agent name, and result path', got['subagent_type'] == 'sdlc-lite:builder-L1' and got['name'] == 'builder-L1-w'
             and got['result'] == str(w / 'builder-L1.md') and got['tmp_prefix'] == str(rr / '.worktrees' / 'tmp' / 'builder-L1-w'))
        head = subprocess.run(['git', '-C', str(rr), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        case('a builder gets its base sha, in the dispatch, base-sha, and the brief',
             got['base_sha'] == head and (w / 'base-sha').read_text() == head + '\n' and 'Base sha: ' + head in got['prompt'])
        case('the brief is the run.sh prompt plus the tree and tmp prefix lines',
             got['prompt'].startswith('Handoff: %s\nArtifacts dir: %s\nYour final message is saved verbatim as %s. Make it exactly the output format your instructions define: '
                                      'start with its first heading, with nothing before it and nothing after the last section.\n' % (w / 'handoff.md', w, w / 'builder-L1.md'))
             and 'Tree: %s' % rr in got['prompt'] and 'Throwaway worktrees only under %s' % got['tmp_prefix'] in got['prompt'])
        rc2, _, err2 = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live))
        case('a second prepare with a running attempt and a live parent refuses', rc2 == 2 and 'still running' in err2 and 'builder-L1.attempt.json' in err2)
        case('the refused prepare wrote no second record', sorted(p.name for p in w.glob('*.attempt.json')) == ['builder-L1.attempt.json'])
        with clean_env(SDLC_DISPATCH_PARENT_PID=str(live)), cwd(rr), contextlib.redirect_stderr(io.StringIO()):
            doubled = prepare('verifier', 'L1', '.sdlc/w/handoff.md', skip=('lock',))
        case('negative control: without the lock gate a second running attempt starts', doubled['result_name'] == 'verifier-L1'
             and len(list(w.glob('*.attempt.json'))) == 2)
        for f in list(w.glob('verifier-L1*')):
            f.unlink()
        a = json.loads((w / 'builder-L1.attempt.json').read_text())
        a['parent_pid'] = dead
        (w / 'builder-L1.attempt.json').write_text(json.dumps(a))
        (w / 'builder-L1.running').write_text('1\n')
        rc3, got3, err3 = prep(rr, 'builder', 'L1', '.sdlc/w/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live))
        old = json.loads((w / 'builder-L1.attempt.json').read_text())
        case('a dead-parent attempt is recovered first', rc3 == 0 and old['status'] == 'interrupted' and 'finished_at' in old and 'recovered' in err3
             and not (w / 'builder-L1.running').exists())
        case('the new attempt gets the next result name and Agent name', got3['result_name'] == 'builder-L1-2'
             and got3['result'] == str(w / 'builder-L1-2.md') and got3['name'] == 'builder-L1-w-2'
             and (w / 'builder-L1-2.attempt.json').is_file())
        case('the interrupted attempt was not overwritten', old['attempt_id'] == att['attempt_id'])
        dryrc, drygot, _ = prep(rr, 'builder', 'L1', '.sdlc/w/handoff.md', '--dry-run')
        case('a dry run writes nothing and takes no lock', dryrc == 0 and drygot['dry_run'] is True and len(list(w.glob('*.attempt.json'))) == 2)
        case('a planner dispatch has no base sha', prep(rr, 'planner', 'L1', '.sdlc/w/handoff.md', '--dry-run')[1]['base_sha'] is None)
        pid, _ = parent_pid()
        case('parent_pid finds a live ancestor process', pid_alive(pid))
        long_dir = rr / '.sdlc' / ('x' * 100) / 'step-12'
        put(long_dir / 'handoff.md', '## Step 12\n')
        long_name = agent_name('plan-reviewer', 'L1', long_dir, 12)
        case('the Agent name fits 64 characters and keeps the step and attempt suffix', len(long_name) <= NAME_MAX and long_name.endswith('-s12-12')
             and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', long_name) is not None)

        # 8. The CLI: stdout is the JSON alone, the exit code is the gate's.
        env = {k: v for k, v in os.environ.items() if not k.startswith('SDLC_')}
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', '--dry-run', 'scout', 'L1', '.sdlc/t/handoff.md'],
                           cwd=str(repo), capture_output=True, text=True, env=env)
        cli = json.loads(p.stdout) if p.returncode == 0 else {}
        case('CLI prints the dispatch JSON on stdout', p.returncode == 0 and cli.get('model') == 'claude-haiku-4-5' and cli.get('subagent_type') == 'sdlc-lite:scout-L1')
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', 'planner', 'L1', '.sdlc/ls/handoff.md'],
                           cwd=str(repo), capture_output=True, text=True, env=env)
        case('CLI exits 5 for the lane gate with the JSON absent from stdout', p.returncode == 5 and p.stdout == '')
    print('dispatch selftest: %s' % ('FAIL' if failures else 'PASS'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
