#!/usr/bin/env python3
"""The pre-launch half of run.sh for Claude sub-agent dispatch (Python 3.9+).

  dispatch.py prepare [--dry-run] <role> <level> <handoff.md>
  dispatch.py record [--agent-id ID] [--tokens N] [--tool-uses N] [--duration-ms N] <dispatch.json>
  dispatch.py prune [--root DIR] [--done NAME | --add NAME]   the queue of finished sub-agents to stop (T-0368)
  dispatch.py status <handoff dir>        each attempt: running, completed, failed, orphaned, or interrupted
  dispatch.py recover <handoff dir>       mark orphaned attempts interrupted (run_lifecycle.py's recovery text)
  dispatch.py resume [--root DIR] <name>  the ladder for an orphan: SendMessage by name, by id, then a new attempt
  dispatch.py selftest

prepare runs every gate and decision run.sh makes before it launches a role and prints a dispatch JSON the
conductor passes to the Agent tool (design: docs/sdlc-lite/subagent-mode.md sections 1 to 3). It launches
nothing and never edits run.sh. Order, as in run.sh: row lookup, preflight, family rules, mailbox notice,
goal precheck, link check, lane gate, spec gate, budget gate, then the one write section.

  row lookup   role:level must be a pipeline row of adapters/claude/levels.json (solo is dispatched by
               T-0284); agents/<role>-<level>.md must exist and every skill its role file declares must exist.
  preflight    the handoff exists and the current directory is a git work tree with a commit.
  family       a verifier never runs on the newest build's model family (a Fable or Sonnet build moves it to
               Opus, same effort); a plan-reviewer never on the newest planner's (an Opus planner moves it
               to Fable). Both read the first model=<[a-z]*> token of the newest result by order.py (a dir with no builder result reads its newest `role solo` runs.jsonl record: a Sonnet solo gets an Opus verifier); a
               verifier whose dir holds no builder result reads the highest-numbered live step-<n>/ that
               holds one (step-<n>.superseded-<k>/ is left out).
  goal         planner or plan-reviewer on a task handoff: steps.py precheck.        Refusal exit 2.
  links        builder or verifier on a step handoff: steps.py lint <step dir> (T-0379). Every cited .sdlc path
               must exist, and a report of the step's own prior attempt must name its step-<n>.superseded-<k>
               folder. Refusal exit 2.
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
Agent name is <ticket number>[-s<n>]-<role>-<level>[-<k>] (T-0363: what differs comes first, the attempt last; a
task with no ticket id uses its dir name, cut to fit 64 characters, in place of the number; s<n> marks a step dir).
The prompt's first line is a title of at most 50 characters (`T-0153 harness coverage | builder L3 | try 2`), line 2 is
the Handoff line, and the description is the ticket id, role, level and first title words (3 to 5 words), per
docs/references/subagent-list-style.md. Records are keyed by the stem: <stem>.attempt.json and <stem>.dispatch.json, beside the handoff.

Records. <stem>.attempt.json holds run_lifecycle.py's keys with status running, transport subagent, and
parent_pid (SDLC_DISPATCH_PARENT_PID, else the first ancestor process named claude, else the first ancestor
that is not a shell or python; never the short-lived tool shell). <stem>.dispatch.json holds subagent_type,
name, model, effort, prompt (the brief), result, tmp_prefix, base_sha, and what T-0278 needs to write the
runs.jsonl line (lane_override, specgate, handoff_sha256, routing_reason). A builder or verifier also writes
base-sha as run.sh does. --dry-run prints the JSON and writes nothing, takes no lock, and skips recovery.

Brief. The run.sh prompt (Handoff, Artifacts dir, the result and output-format sentence) plus a Tree line, a
throwaway-worktree prefix line (.worktrees/tmp/<Agent name>), and for builder and verifier a Base sha line,
since a sub-agent cannot read SDLC_BASE_SHA from its environment. A verifier brief also carries a Report file line:
the result path it writes with the Write tool before it ends (T-0330); record fails the run with a message naming that path when it is missing.

Exit codes as run.sh: 0 ok, 2 usage, preflight, goal, spec gate, or a running attempt, 4 budget, 5 lane.

record is the post-launch half (T-0278, design section 3). It takes <stem>.dispatch.json and the sub-agent's
result: the file the role wrote at the dispatch's result path, else stdin when that file is missing or empty,
else (with --transcript) the transcript's last assistant message; a max_tokens stop is refused as truncated (T-0343)
(stdin with a "## " heading line is a result, any other stdin is the sub-agent's error text). In run.sh's order
it then does the following.
  header       writes <!-- role= level= model= effort= --> from the dispatch over any header the role wrote, then
               the body, to the result path.
  cleanup      removes the worktrees and directory under the dispatch's tmp prefix (only a path under
               <tree>/.worktrees/tmp/), then reports strays: worktrees and local branches that appeared since
               prepare (its snapshot sits in the attempt record) under <tree>/.worktrees/tmp/ or on a branch named with the
               role's agent name, the own prefix left out; peers' worktrees and branches are not reported. Report only.
  stale        a handoff sha256 that differs from the one prepare stored prints "stale input: <handoff> changed
               while <role> ran" and sets stale_input. The exit code is unchanged by cleanup, strays, and stale.
  runs.jsonl   one line with the key set run.sh writes, plus agent_id and cost_reason, with transport subagent;
               loaded_context is {"status":"log absent"} (a sub-agent leaves no stream-json log).
               cost_usd is estimated from the notice tokens by cost_estimate.py (cost_estimated true, cost_basis
               "tokens x blended"); with no tokens it is null with cost_reason "subagent usage not priced", never zero;
               usage holds the notice's subagent_tokens and tool_uses when --tokens or --tool-uses is given; --transcript <jsonl>
               replaces the token count with the transcript's summed usage fields, priced per field (T-0328).
  validate     results.py validate --role <role>. A defect prints "dispatch.py: <role> result <reason>; see
               <file>", exit 3, and keeps the file and the line; the attempt is failed with exit_code 3.
  failed       no result file and no result on stdin: the stdin text is saved as <stem>.log, the attempt is failed
               with exit_code 1 and the text, and no runs.jsonl line is written, as run.sh. A 429 or session-limit
               text writes <role>-<level>.limit with the prepare command to resume; a later success removes it.
  success      the attempt is completed, the result path is printed, exit 0.
Prune (T-0368). The host keeps a finished sub-agent as an idle, addressable teammate until it is stopped. prepare writes
"prune": true into the dispatch for a one-shot role (scout, researcher, architect, archaeologist, planner, plan-reviewer,
verifier, filer) and false for builder, whose failed run may be resumed (solo and the messenger are false too); --prune and
--no-prune override it. record on exit 0 with prune true prints `prune: <agent name>` and appends {name, agent_id, role,
level, recorded_at} to <project>/.sdlc/runtime/prune.json, unless another attempt of that agent is still open or the
result's ## Follow-ups section is not None. `dispatch.py prune` lists the queue with the stop call per entry
(`TaskStop task_id=<name>`); `--done NAME` removes an entry once stopped; `--add NAME` queues a landed builder or solo
(`fanout.py land` does it for a merged solo).
Exit codes: 0 ok, 1 failed sub-agent, 2 unreadable dispatch or attempt, an attempt that is not running, or a result
path outside the artifacts dir, 3 invalid result.
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
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(HERE))
import budget  # noqa: E402
import claude_roles  # noqa: E402
import cost_estimate  # noqa: E402
import order  # noqa: E402
import results  # noqa: E402
import tickets  # noqa: E402
import run_lifecycle  # noqa: E402

SHELLS = ('sh', 'bash', 'zsh', 'dash', 'fish', 'ksh', 'env', 'sudo', 'timeout', 'tmux', 'login')
NAME_MAX = 64
GATES = ('preflight', 'goal', 'links', 'lane', 'specgate', 'budget', 'lock')
NAME_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
ID_RE = re.compile(r'[0-9]{8}T[0-9]{12}Z-[a-z0-9]+(-[a-z0-9]+)*')
PRUNE_ROLES = ('scout', 'researcher', 'architect', 'archaeologist', 'planner', 'plan-reviewer', 'verifier', 'filer')


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


def solo_model(directory):
    """The model of the newest `role solo` record in directory/runs.jsonl, else ''."""
    got = [r.get('model') for _, r in order.records(directory) if r.get('role') == 'solo']
    return got[-1] if got and isinstance(got[-1], str) else ''


AGENT_ALIASES = ('sonnet', 'opus', 'haiku', 'fable')


def agent_alias(model):
    """The Agent tool accepts only an alias; map a pinned id such as claude-haiku-5-5 to its family alias.
    On a Max login the alias haiku has resolved to Sonnet 5.5 (docs/reports/haiku-alias-2026-09-30.md), so the
    transcript model field, not this alias, says which model ran."""
    if model in AGENT_ALIASES:
        return model
    m = re.match(r'claude-(sonnet|opus|haiku|fable)(-|$)', model or '')
    return m.group(1) if m else model


def family(role, model, directory, solo=''):
    if role == 'verifier':
        built = order.newest(str(directory), 'builder') or step_build(directory)
        if built and model == model_of(built) and model in ('fable', 'sonnet'):
            return 'opus'
        if not built and model == (solo_model(directory) or solo) and model in ('fable', 'sonnet'):
            return 'opus'  # a solo ticket has no builder result: its newest runs.jsonl solo record holds the family (T-0284);
            # a sub-agent lane worktree holds none, so fanout.py prep passes --solo-model (T-0356)
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


def ticket_label(directory):
    """(id, title) of the ticket that owns directory, ('', '') when it has none (T-0363)."""
    folder = budget.ticket_of(directory)
    meta = (budget.front(folder / 'handoff.md') if folder else None) or {}
    return str(meta.get('id') or '').strip(), re.sub(r'\s+', ' ', str(meta.get('title') or '')).strip()


def agent_name(role, level, directory, k):
    """<ticket number>[-s<n>]-<role>-<level>[-<k>], or <slug>[-s<n>]-<role>-<level>[-<k>] with no ticket: what differs
    between rows comes first, the attempt last, where the host's 24-character cut keeps it (T-0363, subagent-list-style.md)."""
    slug, step = slug_of(directory)
    tid = ticket_label(directory)[0]
    tail = '-%s-%s' % (role, level) + ('-%d' % k if k > 1 else '')
    head = re.sub(r'[^0-9A-Za-z]+', '', tid[2:]) if tid.upper().startswith('T-') and tid[2:].isdigit() else ''
    if not head:
        head = slug[:max(1, NAME_MAX - len(tail) - len(step))].strip('-') or 'task'
    return head + step + tail


def list_title(directory, role, level, k, limit=50):
    """The first prompt line, at most limit characters: `T-0153 harness coverage | builder L3 | try 2`."""
    tid, title = ticket_label(directory)
    slug, step = slug_of(directory)
    head = ((tid or slug) + (' s' + step[2:] if step else ''))
    tail = ' | %s %s' % (role, level) + (' | try %d' % k if k > 1 else '')
    head = head[:max(1, limit - len(tail))].rstrip('-')
    room = limit - len(head) - len(tail) - 1
    cut = title[:room] if tid and room > 0 else ''
    if cut and len(title) > room and title[room] != ' ' and ' ' in cut:
        cut = cut.rsplit(' ', 1)[0]  # cut at a word, not inside one
    cut = cut.rstrip(' ,.;:-')
    return (head + (' ' + cut if cut else '') + tail)[:limit]


def list_description(directory, role, level):
    """Three to five words: the ticket id, the role and level, then the first title words."""
    tid, title = ticket_label(directory)
    return ' '.join(([tid or slug_of(directory)[0], role, level] + title.split())[:5])


def next_stem(directory, role, level):
    stem, k = '%s-%s' % (role, level), 1
    while any(Path(directory).glob(stem + '.*')):
        k += 1
        stem = '%s-%s-%d' % (role, level, k)
    return stem, k


def exec_tree(directory):
    """The tree a build runs in: the handoff dir, except a handoff in the main checkout dispatched from inside an
    owned linked (lane) worktree of the same repo, where it is that worktree (T-0381)."""
    def dirs(where):
        gd = git('rev-parse', '--git-dir', cwd=where).stdout.strip()
        common = git('rev-parse', '--git-common-dir', cwd=where).stdout.strip()
        if not gd or not common:
            return None
        return os.path.realpath(os.path.join(str(where), gd)), os.path.realpath(os.path.join(str(where), common))
    hd = dirs(directory)
    if not hd or hd[0] != hd[1]:
        return directory
    top = git('rev-parse', '--show-toplevel').stdout.strip()
    cd = dirs(top) if top else None
    return top if cd and cd[0] != cd[1] and cd[1] == hd[1] else directory


def fork_floor(directory):
    """In a linked (lane) worktree, the commit the lane forked from: git merge-base HEAD <main checkout HEAD>
    (SDLC_BASE_REF names another ref). '' in the main checkout or when git cannot say (T-0376)."""
    gd = git('rev-parse', '--git-dir', cwd=directory).stdout.strip()
    common = git('rev-parse', '--git-common-dir', cwd=directory).stdout.strip()
    if not gd or not common or os.path.realpath(os.path.join(str(directory), gd)) == os.path.realpath(os.path.join(str(directory), common)):
        return ''
    ref = os.environ.get('SDLC_BASE_REF', '').strip()
    if not ref:
        m = re.search(r'^HEAD ([0-9a-f]{7,64})$', git('worktree', 'list', '--porcelain', cwd=directory).stdout, re.M)
        ref = m.group(1) if m else ''
    return git('merge-base', 'HEAD', ref, cwd=directory).stdout.strip() if ref else ''


NAMED_BASE_RE = re.compile(r'^[ \t]*(?:-[ \t]+)?[Bb]ase:[ \t]*([0-9a-fA-F]{7,40})[ \t]*(?:#.*)?$', re.M)


def build_base(directory):
    """The build-start commit run.sh stores in base-sha (T-0381), in this order: (1) a base the handoff names (a line
    `base: <sha>`), else (2) the sha recorded at the step's first dispatch, kept valid, else (3) HEAD of the execution
    tree, never the main checkout's HEAD. A supplied SDLC_BASE_SHA that resolves to another commit is refused and the
    pick kept; a named base that is not an ancestor of HEAD raises Refuse. Git runs in the execution tree (the
    handoff's own tree, or the lane worktree a main-checkout handoff is run from), and in a lane worktree a recorded
    sha older than the lane's fork point is stale (T-0376). Returns (stored, base)."""
    stored = ''
    f = Path(directory) / 'base-sha'
    if f.is_file():
        lines = f.read_text(encoding='utf-8', errors='replace').splitlines()
        stored = re.sub(r'\s', '', lines[0]) if lines else ''
    if not stored:  # a solo lane has no run.sh: its dispatch file recorded the pre-build HEAD (T-0366)
        for df in sorted(Path(directory).glob('*.dispatch.json')):  # <ticket>-solo-<level> now, solo-<level>-<slug> before T-0363
            try:
                rec = json.loads(df.read_text(encoding='utf-8'))
                stored = str(rec.get('base_sha') or '').strip() if rec.get('role') == 'solo' else ''
            except (OSError, ValueError, AttributeError):
                stored = ''
            if stored:
                break
    cwd = exec_tree(directory)
    floor = fork_floor(cwd)

    def commit(sha):
        return git('rev-parse', '-q', '--verify', sha + '^{commit}', cwd=cwd).stdout.strip() if sha else ''

    def ancestor(sha):
        return bool(commit(sha)) and git('merge-base', '--is-ancestor', sha, 'HEAD', cwd=cwd).returncode == 0

    base, why = '', ''
    hf = Path(directory) / 'handoff.md'
    m = NAMED_BASE_RE.search(hf.read_text(encoding='utf-8', errors='replace')) if hf.is_file() else None
    if m:
        if not ancestor(m.group(1)):
            raise Refuse(2, 'dispatch.py: SDLC_BASE_SHA refused: %s names base %s, which is not a commit that is an ancestor of HEAD in %s'
                         % (hf, m.group(1), cwd))
        base, why = commit(m.group(1)), 'named in the handoff'
    if not base and ancestor(stored) and (not floor or git('merge-base', '--is-ancestor', floor, stored, cwd=cwd).returncode == 0):
        base, why = commit(stored), 'recorded at the first dispatch (base-sha)'
        merges = git('rev-list', '--first-parent', '--merges', base + '..HEAD', cwd=cwd).stdout.split()
        if merges:
            base, why = merges[0], 'newest resync merge since the recorded base-sha'
    if not base:
        base, why = git('rev-parse', 'HEAD', cwd=cwd).stdout.strip(), 'HEAD of the execution tree (nothing named or recorded)'
    supplied = re.sub(r'\s', '', os.environ.get('SDLC_BASE_SHA', ''))
    if supplied and commit(supplied) != base:
        say("SDLC_BASE_SHA refused: %s (supplied) differs from the step base %s (%s); name it in the handoff with a line 'base: <sha>' to use it"
            % (supplied, base[:12], why))
    return stored, base


def lane_gate(role, directory, plugin):
    """None to proceed, else the (lane_dir, level) of a solo-lane ticket that needs the solo agent: its size as a
    level (tickets.parse reads a deprecated alias size as its level), L2 when unreadable."""
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
    size = (tickets.parse(handoff.read_text(encoding='utf-8', errors='replace')) or {}).get('size')
    return lane_dir, size if size in ('L1', 'L2', 'L3') else 'L2'


def mailbox(role):
    total = 0
    for who in (role, 'claude'):
        p = script('messages.py', 'count', '--receiver', who)
        if p.returncode == 0 and p.stdout.strip().isdigit():
            total += int(p.stdout.strip())
    if total > 0:
        say('%d new message(s) for %s; read with messages.py' % (total, role))


RECOVERY = 'Owner lock released without a terminal record. Inspect artifacts and working tree before a new attempt.'


def read_attempt(path):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except ValueError:
        raise Refuse(2, 'dispatch.py: unreadable attempt record, inspect it first: ' + str(path))
    return data if isinstance(data, dict) else {}


def attempt_state(data):
    """running, completed, failed, or orphaned (running, claude backend, parent pid dead); else the recorded status."""
    status = data.get('status')
    if status != 'running':
        return status or 'unknown'
    pid = data.get('parent_pid') or data.get('owner_pid')
    if data.get('backend', 'claude') == 'claude' and isinstance(pid, int) and not pid_alive(pid):
        return 'orphaned'
    return 'running'


def recover_orphans(directory, dry_run=False, own=None):
    """Mark orphaned attempts interrupted with run_lifecycle.py's recovery text; return (recovered, live) names.
    A running attempt whose recorded pid is own (the calling session) is neither recovered nor live (T-0371)."""
    live, recovered = [], []
    for path in sorted(Path(directory).glob('*.attempt.json')):
        data = read_attempt(path)
        state = attempt_state(data)
        if state == 'orphaned':
            if not dry_run:
                data.update(status='interrupted', finished_at=run_lifecycle.now(), recovery=RECOVERY)
                run_lifecycle.write(path, data)
                (Path(directory) / ('%s-%s.running' % (data.get('role'), data.get('level')))).unlink(missing_ok=True)
            recovered.append(path.name)
        elif state == 'running' and (data.get('parent_pid') or data.get('owner_pid')) != own:
            live.append('%s (pid %s)' % (path.name, data.get('parent_pid') or data.get('owner_pid')))
    return recovered, live


def settle(directory, dry_run):
    """Refuse while a dispatched attempt in directory is alive; mark dead-parent ones interrupted."""
    recovered, live = recover_orphans(directory, dry_run, own=parent_pid()[0])
    if live:
        raise Refuse(2, 'dispatch.py: an attempt is still running in %s: %s; record it, or wait for it, before dispatching another role. If its spawn was denied or never started, recover it: python3 %s %s' % (directory, ', '.join(live), Path(run_lifecycle.__file__).resolve().with_name('run_lifecycle.py'), 'recover "%s"' % directory))
    return recovered


def status(directory, orphans_only=False):
    """One line per attempt: stem, state, role-level, parent pid; orphans_only keeps the orphaned ones."""
    lines = []
    for path in sorted(Path(directory).glob('*.attempt.json')):
        data = read_attempt(path)
        state = attempt_state(data)
        if orphans_only and state != 'orphaned':
            continue
        stem = path.name[:-len('.attempt.json')]
        line = '%s %s %s-%s parent_pid=%s' % (stem, state, data.get('role'), data.get('level'), data.get('parent_pid') or data.get('owner_pid'))
        report = Path(directory) / (stem + '.md')
        if state in ('running', 'orphaned') and report.is_file() and report.stat().st_size:
            line += ' report-written-unrecorded'  # T-0383: the role reported but nobody recorded it, so no verdict was delivered
        lines.append(line)
        sent = Path(directory) / (stem + '.delivery.json')
        if sent.is_file():
            try:
                dv = json.loads(sent.read_text(encoding='utf-8'))
            except ValueError:
                dv = {}
            if dv.get('state') != 'sent':
                lines.append('%s verdict-delivery-%s to %s%s' % (stem, dv.get('state', 'unreadable'), dv.get('receiver'), ': ' + dv['error'] if dv.get('error') else ''))
    return lines


def resume(name, root='.'):
    """The resume ladder for an orphaned or interrupted attempt found by stem or Agent name under root."""
    for path in sorted(Path(root).glob('**/*.attempt.json')):
        if '.git' in path.parts or '.worktrees' in path.parts:
            continue
        data = read_attempt(path)
        if name not in (data.get('name'), data.get('agent_name')):
            continue
        state = attempt_state(data)
        if state not in ('orphaned', 'interrupted'):
            raise Refuse(2, 'dispatch.py: %s is %s, not orphaned or interrupted; nothing to resume' % (name, state))
        agent = data.get('agent_name') or data.get('name')
        aid = data.get('agent_id') or 'unknown'
        transcript = data.get('transcript') or 'the sub-agent transcript for %s under ~/.claude/projects/' % (aid if aid != 'unknown' else agent)
        addendum = ('Resume note: attempt %s was interrupted before it reported. First step: run git status, then read its transcript at %s; '
                    'continue from what is on disk and never replay an old report.' % (data.get('name'), transcript))
        return ['1. SendMessage({to: "%s", message: "Continue your interrupted work."})   # by name' % agent,
                '2. SendMessage({to: "%s", message: "Continue your interrupted work."})   # by id' % aid,
                '3. python3 dispatch.py prepare %s %s %s   # new attempt; add to its brief: %s'
                % (data.get('role'), data.get('level'), data.get('handoff'), addendum)]
    raise Refuse(2, 'dispatch.py: no attempt named %s under %s' % (name, root))


def worktrees(tree):
    """[(path, branch)] of every registered worktree; branch is '' for a detached one."""
    out, found, path, branch = git('worktree', 'list', '--porcelain', cwd=tree).stdout, [], '', ''
    for line in out.splitlines() + ['']:
        if line.startswith('worktree '):
            path, branch = line[len('worktree '):], ''
        elif line.startswith('branch '):
            branch = line[len('branch '):]
            branch = branch[len('refs/heads/'):] if branch.startswith('refs/heads/') else branch
        elif not line and path:
            found.append((path, branch))
            path, branch = '', ''
    return found


def branches(tree):
    return git('for-each-ref', '--format=%(refname:short)', 'refs/heads', cwd=tree).stdout.split()


def under(path, prefix):
    """True when path is prefix or below it, by physical path (macOS reports /private/var for /var)."""
    real, base = os.path.realpath(path), os.path.realpath(prefix)
    return real == base or real.startswith(base + os.sep)


def prepare(role, level, handoff, plugin=PLUGIN, dry_run=False, skip=(), solo='', prune=None, notify='', notify_re=''):
    """Run the gates and write the records; returns the dispatch dict. skip names gates to disable (selftest only);
    solo is the model of a solo ticket whose runs.jsonl record is not in this tree (--solo-model); prune overrides the
    role's default prune flag (True, False, or None for the default); notify names the mailbox receiver that gets the
    verdict message when record closes the attempt (T-0383), notify_re the message id it answers."""
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
    if notify and not NAME_RE.fullmatch(notify) or notify_re and not (notify and ID_RE.fullmatch(notify_re)):
        raise Refuse(2, 'dispatch.py: --notify takes a receiver name (lowercase letters, digits, hyphens); --notify-re takes a message id and needs --notify')
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

    model = agent_alias(family(role, model, directory, solo))
    if not dry_run:
        mailbox(role)

    task_handoff = handoff.name == 'handoff.md' and not directory.name.startswith('step-')
    if 'goal' not in skip and role in ('planner', 'plan-reviewer') and task_handoff:
        p = script('steps.py', 'precheck', directory)
        if p.returncode != 0:
            raise Refuse(2, (p.stdout + p.stderr).rstrip('\n'),
                         'dispatch.py: steps.py precheck refused the task handoff in %s; add a ## Goal section' % directory)

    if 'links' not in skip and role in ('builder', 'verifier') and handoff.name == 'handoff.md' and re.fullmatch(r'step-\d+', directory.name):
        p = script('steps.py', 'lint', directory)
        if p.returncode != 0:
            raise Refuse(2, (p.stdout + p.stderr).rstrip('\n'),
                         'dispatch.py: steps.py lint refused the links in %s; fix the cited paths (rewrite them to the step-<n>.superseded-<k> folder) before dispatching' % handoff)

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
        toplevel = git('rev-parse', '--show-toplevel', cwd=directory).stdout.strip() or git('rev-parse', '--show-toplevel').stdout.strip() or os.getcwd()  # the handoff's own tree, so a lane worktree handoff gets the lane as Tree
        tmp_prefix = str(Path(toplevel) / '.worktrees' / 'tmp' / name)

        base = None
        if role in ('builder', 'verifier'):
            stored, base = build_base(directory)
            if not dry_run and base != stored:
                (directory / 'base-sha').write_text(base + '\n', encoding='utf-8')

        prompt = ('%s\nHandoff: %s\nArtifacts dir: %s\nYour final message is saved verbatim as %s. Make it exactly the output format your '
                  'instructions define: start with its first heading, with nothing before it and nothing after the last section.\n'
                  'Tree: %s (run every Bash call as cd %s && ...; the shell keeps no working directory between calls)\n'
                  'Throwaway worktrees only under %s (git worktree add --detach "%s/<name>" HEAD creates the parents); remove them when done.'
                  % (list_title(directory, role, level, k), handoff, directory, result, toplevel, toplevel, tmp_prefix, tmp_prefix))
        if role == 'verifier':
            prompt += ('\nReport file: %s (before you end, write your final report to exactly this path with the Write tool, the same text '
                       'as your final message; dispatch.py record reads the file, and a missing one fails the run)' % result)
        if base:
            prompt += '\nBase sha: %s (the commit this build started from; diff scope criteria against it)' % base

        sha = hashlib.sha256(handoff.read_bytes()).hexdigest()
        reason = os.environ.get('SDLC_ROUTING_REASON', '').strip()
        pid, source = parent_pid()
        dispatch = dict(subagent_type='sdlc-lite:%s-%s' % (role, level), name=name,
                        description=list_description(directory, role, level),
                        model=model, effort=effort, prompt=prompt,
                        run_in_background=os.environ.get('SDLC_HEADLESS') != '1',
                        prune=role in PRUNE_ROLES if prune is None else bool(prune),
                        role=role, level=level, result_name=stem, result=str(result), tmp_prefix=tmp_prefix,
                        base_sha=base, tree=toplevel, handoff=str(handoff), artifacts_dir=str(directory),
                        handoff_sha256=sha, shared_with_builder=False, lane_override=lane_override, specgate=specgate,
                        routing_reason=reason or 'Caller selected this role and level; no task-specific rationale supplied.',
                        attempt_file=str(directory / (stem + '.attempt.json')),
                        dispatch_file=str(directory / (stem + '.dispatch.json')), dry_run=dry_run)
        if notify:
            dispatch.update(notify=notify, notify_re=notify_re)
        if dry_run:
            return dispatch
        if notify:
            unregistered_receiver(notify, toplevel)
        if lane_override:
            skips, line = directory.parent if directory.name.startswith('step-') else directory, 'lane override: ' + lane_override
            skips = skips / 'skips.md'
            if line not in (skips.read_text(encoding='utf-8').splitlines() if skips.is_file() else []):
                with skips.open('a', encoding='utf-8') as f:
                    f.write(line + '\n')
        attempt = dict(attempt_id=uuid.uuid4().hex, name=stem, agent_name=name, role=role, level=level, backend='claude',
                       transport='subagent', model=model, effort=effort, routing_reason=dispatch['routing_reason'],
                       reason_source='caller' if reason else 'fallback', status='running', started_at=run_lifecycle.now(),
                       project=os.getcwd(), handoff=str(handoff), parent_pid=pid, parent_pid_source=source, handoff_sha256=sha,
                       worktrees_before=[p for p, _ in worktrees(toplevel)], branches_before=branches(toplevel))
        dispatch['attempt_id'] = attempt['attempt_id']
        run_lifecycle.write(Path(dispatch['attempt_file']), attempt)
        run_lifecycle.write(Path(dispatch['dispatch_file']), dispatch)
        return dispatch
    finally:
        if lock is not None:
            lock.close()


LIMIT_RE = re.compile(r'429|session limit|usage limit|hit your (session |usage )?limit|rate.?limit', re.I)
COST_REASON = 'subagent usage not priced'
RECORD_KEYS = ('role', 'level', 'model', 'effort', 'result', 'tmp_prefix', 'tree', 'handoff', 'artifacts_dir', 'handoff_sha256',
               'attempt_id', 'attempt_file', 'routing_reason')


def validate_result(role, path):
    """None when the result passes results.py validate --role, else the one reason string run.sh prints."""
    p = script('results.py', 'validate', path, '--role', role)
    if p.returncode == 0:
        return None
    msg = (p.stdout + p.stderr).strip()
    prefix = 'results.py: %s: ' % path
    return (msg[len(prefix):] if msg.startswith(prefix) else msg) or 'failed the result check'


def remove_tmp(tree, prefix):
    """Remove the worktrees and directory under the dispatch's tmp prefix, then the empty parents. Never raises."""
    root = os.path.realpath(os.path.join(tree, '.worktrees', 'tmp'))
    if not os.path.realpath(prefix).startswith(root + os.sep):
        say('refusing to remove %s: not under %s' % (prefix, root))
        return
    try:
        for path, _ in worktrees(tree):
            if under(path, prefix) or path == prefix:
                git('worktree', 'remove', '--force', '--force', path, cwd=tree)
        shutil.rmtree(prefix, ignore_errors=True)
        git('worktree', 'prune', cwd=tree)
        for parent in (root, os.path.dirname(root)):
            try:
                os.rmdir(parent)
            except OSError:
                pass
    except OSError as e:
        say('could not clean %s: %s' % (prefix, e))


def strays(tree, prefix, attempt):
    """(worktree [path, branch] pairs, branch names) that appeared since prepare and belong to this role: a worktree under
    <tree>/.worktrees/tmp/ (its own prefix left out) or on a branch named with the role's agent name, a branch with that
    name as prefix. Peers' worktrees and branches elsewhere are not this role's (T-0371)."""
    if 'worktrees_before' not in attempt:
        return [], []
    seen, known = set(attempt['worktrees_before']), set(attempt.get('branches_before', []))
    root, mine = os.path.join(tree, '.worktrees', 'tmp'), os.path.basename(prefix.rstrip('/'))
    own_br = lambda b: bool(b) and b.startswith(mine)
    wts = [(p, b) for p, b in worktrees(tree) if p not in seen and not under(p, prefix) and (under(p, root) or own_br(b))]
    return wts, [b for b in branches(tree) if b not in known and own_br(b)]


def limit_marker(d, error):
    """A 429 or session limit in the error text leaves <role>-<level>.limit and prints the resume command."""
    m = LIMIT_RE.search(error)
    if not m:
        return
    line = next((l for l in error.splitlines() if LIMIT_RE.search(l)), m.group(0))[:200]
    resume = 'python3 %s prepare %s %s %s' % (HERE / 'dispatch.py', d['role'], d['level'], d['handoff'])
    marker = Path(d['artifacts_dir']) / ('%s-%s.limit' % (d['role'], d['level']))
    marker.write_text(json.dumps(dict(ts=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), role=d['role'], level=d['level'],
                                      handoff=d['handoff'], resume=resume, evidence=line), separators=(',', ':')) + '\n', encoding='utf-8')
    say('session limit: resume with: ' + resume)


PRUNE_REL = Path('.sdlc') / 'runtime' / 'prune.json'
PRUNE_KEYS = ('name', 'agent_id', 'role', 'level', 'recorded_at')


def prune_path(root='.'):
    return Path(root) / PRUNE_REL


def prune_read(root='.'):
    """The queued entries (a list of dicts); a missing or unreadable file is an empty queue."""
    try:
        data = json.loads(prune_path(root).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return [e for e in data if isinstance(e, dict) and e.get('name')] if isinstance(data, list) else []


def prune_edit(root, change):
    """Read the queue under a file lock, let change(entries) return the new list, write it atomically; returns the list."""
    import fcntl
    path = prune_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not (path.parent / '.gitignore').exists():  # a consumer repo may not ignore .sdlc/runtime: the folder ignores itself
        (path.parent / '.gitignore').write_text('*\n', encoding='utf-8')
    with (path.parent / 'prune.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        entries = change(prune_read(root))
        temp = path.with_name(path.name + '.tmp-' + uuid.uuid4().hex)
        temp.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
        temp.replace(path)
    return entries


def prune_add(root, name, role='', level='', agent_id=None):
    """Queue an agent by name (one entry per name; a later add replaces the earlier one)."""
    entry = dict(name=name, agent_id=agent_id, role=role, level=level, recorded_at=run_lifecycle.now())
    prune_edit(root, lambda es: [e for e in es if e.get('name') != name] + [entry])
    return entry


def prune_done(root, name):
    """Remove an entry; True when it was queued."""
    found = []
    prune_edit(root, lambda es: [e for e in es if e.get('name') != name or found.append(1)])
    return bool(found)


def prune_lines(root='.'):
    entries = prune_read(root)
    if not entries:
        return ['prune: nothing queued']
    return ['TaskStop task_id=%s    # %s %s, recorded %s; then: dispatch.py prune --done %s'
            % (e['name'], e.get('role') or 'agent', e.get('level') or '', e.get('recorded_at') or '?', e['name']) for e in entries]


def follow_up_pending(text):
    """True when the result's ## Follow-ups section holds anything but None."""
    m = re.search(r'^## Follow-ups[ \t]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return bool(m) and m.group(1).strip().rstrip('.').lower() not in ('', 'none')


def attempt_open(directory, name, own):
    """True when another attempt record in the directory for the agent name is still running."""
    for f in Path(directory).glob('*.attempt.json'):
        try:
            a = json.loads(f.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if f != own and isinstance(a, dict) and a.get('agent_name') == name and a.get('status') == 'running':
            return True
    return False


def queue_prune(d, attempt, agent_id):
    """After a recorded success: queue a dispatch with prune true and print `prune: <name>`; skip an open attempt or a pending follow-up."""
    name = attempt.get('agent_name') or d.get('name')
    if not d.get('prune') or not name:
        return False
    if attempt.get('status') != 'completed' or attempt_open(d['artifacts_dir'], name, Path(d['attempt_file'])):
        return False
    try:
        if follow_up_pending(Path(d['result']).read_text(encoding='utf-8', errors='replace')):
            return False
    except OSError:
        return False
    prune_add(attempt.get('project') or d['tree'], name, d['role'], d['level'], agent_id or attempt.get('agent_id'))
    print('prune: ' + name)
    return True


def record(dispatch_file, stdin=None, agent_id=None, usage=None, duration_ms=None, validate=validate_result, resolved_model=None, transcript=None):
    """Validate, record, and close one dispatched role; returns the exit code (0 ok, 1 failed, 2 refused, 3 invalid result).

    The result is the file the role wrote at the dispatch's result path, else stdin() (a callable) when the file is
    missing or empty. stdin text with a ## heading line is a result unless it is a truncation of the transcript's final message (T-0349); any other text is the sub-agent's error text.
    validate(role, path) returns None or a reason; selftest passes an accept-all one as the negative control.
    With transcript (a jsonl path), a result missing from both the file and stdin is taken from the transcript's last
    assistant message; one that stopped on max_tokens is refused as truncated (T-0343)."""
    try:
        d = json.loads(Path(dispatch_file).read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        raise Refuse(2, 'dispatch.py: cannot read dispatch file %s: %s' % (dispatch_file, e))
    missing = [k for k in RECORD_KEYS if not isinstance(d, dict) or k not in d]
    if missing:
        raise Refuse(2, 'dispatch.py: %s is not a dispatch file (missing %s)' % (dispatch_file, ', '.join(missing)))
    role, level, tree, prefix = d['role'], d['level'], d['tree'], d['tmp_prefix']
    result, attempt_path = Path(d['result']), Path(d['attempt_file'])
    if result.parent != Path(d['artifacts_dir']) or attempt_path.parent != result.parent:
        raise Refuse(2, 'dispatch.py: result and attempt record must sit in the artifacts dir %s' % d['artifacts_dir'])
    try:
        attempt = json.loads(attempt_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        raise Refuse(2, 'dispatch.py: cannot read attempt record %s: %s' % (attempt_path, e))
    if attempt.get('attempt_id') != d['attempt_id']:
        raise Refuse(2, 'dispatch.py: %s belongs to another attempt than %s' % (attempt_path, dispatch_file))
    if attempt.get('status') != 'running':
        raise Refuse(2, 'dispatch.py: attempt %s is %s, not running; nothing to record' % (attempt_path.name, attempt.get('status')))

    def close(status, rc, **extra):
        attempt.update(status=status, exit_code=rc, finished_at=run_lifecycle.now(), **extra)
        if agent_id:
            attempt['agent_id'] = agent_id
        run_lifecycle.write(attempt_path, attempt)
        result.parent.joinpath('%s-%s.running' % (role, level)).unlink(missing_ok=True)

    def report_strays(found):
        for path, branch in found[0]:
            say('stray worktree appeared during this run: %s%s' % (path, ' [%s]' % branch if branch else ''))
        for branch in found[1]:
            say('stray branch appeared during this run: ' + branch)

    text = result.read_text(encoding='utf-8', errors='replace') if result.is_file() else ''
    error = ''
    if not text.strip():
        said = (stdin() if stdin else '') or ''
        has_head = bool(re.search(r'^## ', said, re.M))
        # T-0349: stdin that is an error stays a failure; stdin that is empty or a truncation of the transcript's final message yields to it.
        # T-0352: stdin with no heading is error text unless it is a truncation of the transcript's final message.
        cut = said.strip().rstrip('.\u2026').rstrip()
        fin = cost_estimate.transcript_final(transcript) if transcript else None
        is_err = bool(said.strip()) and not has_head and not (fin and fin[0].strip().startswith(cut))
        if is_err:
            fin = None
        if fin and has_head and not (len(fin[0].strip()) > len(cut) and fin[0].strip().startswith(cut)):
            fin = None  # complete stdin: it is the result
        if fin and fin[1] == 'max_tokens':
            text, error = '', 'the %s final message in the transcript is truncated (stop_reason max_tokens); rerun it or have it write %s' % (role, result)
        elif fin and re.search(r'^## ', fin[0], re.M):
            text = fin[0]
        elif has_head:
            text = said
        else:
            text, error = '', said.strip() or 'no result file at %s (the %s must write its report there before it ends)' % (result, role)
    if not text.strip():
        log = result.with_suffix('.log')
        log.write_text(error + '\n', encoding='utf-8')
        remove_tmp(tree, prefix)
        found = strays(tree, prefix, attempt)
        say('%s returned no result; see %s' % (role, log))
        limit_marker(d, error)
        report_strays(found)
        close('failed', 1, error=error[:500])
        deliver_quietly(dispatch_file)
        return 1

    lines = text.splitlines()
    skip = next((i for i, l in enumerate(lines) if l.strip()), 0)
    body = '\n'.join(lines[skip + 1:] if skip < len(lines) and results.HEADER.match(lines[skip].rstrip()) else lines)
    header = '<!-- role=%s level=%s model=%s effort=%s%s -->' % (
        role, level, d['model'], d['effort'], ' shared_with_builder=yes' if d.get('shared_with_builder') else '')
    result.write_text(header + '\n' + body + '\n', encoding='utf-8')
    remove_tmp(tree, prefix)
    found = strays(tree, prefix, attempt)
    stray_wt, stray_br = [p for p, _ in found[0]], found[1]
    handoff = Path(d['handoff'])
    now_sha = hashlib.sha256(handoff.read_bytes()).hexdigest() if handoff.is_file() else ''
    stale = bool(now_sha) and now_sha != d['handoff_sha256']
    est, basis, _ = cost_estimate.estimate(d['model'], usage)
    line = dict(ts=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), role=role, level=level, model=d['model'], effort=d['effort'],
                file=result.name, shared_with_builder=bool(d.get('shared_with_builder')), attempt_id=d['attempt_id'],
                handoff_sha256=d['handoff_sha256'], stale_input=stale, routing_reason=d['routing_reason'], backend='claude',
                transport='subagent', agent_id=agent_id, usage=usage, cost_usd=est, cost_reason=None if est is not None else COST_REASON,
                duration_ms=duration_ms, turns=None, stray_worktrees=stray_wt, stray_branches=stray_br,
                loaded_context={'status': 'log absent'})  # T-0252: a sub-agent leaves no stream-json log to read
    if est is not None:
        line.update(cost_estimated=True, cost_basis=basis)
    if resolved_model:  # T-0338: the model the transcript says ran, beside the alias in model
        line['resolved_model'] = resolved_model
    if d.get('specgate'):
        line['specgate'] = d['specgate']
    if d.get('lane_override'):
        line['lane_override'] = d['lane_override']
    with (result.parent / 'runs.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(line, separators=(',', ':')) + '\n')
    if stale:
        say('stale input: %s changed while %s ran' % (handoff, role))
    reason = validate(role, str(result))
    if reason is not None:
        say('%s result %s; see %s' % (role, reason, result))
        report_strays(found)
        close('failed', 3)
        deliver_quietly(dispatch_file)
        return 3
    (result.parent / ('%s-%s.limit' % (role, level))).unlink(missing_ok=True)
    if role == 'builder':  # T-0378: a completed build without its pre-edit (red) controls leaves a process deviation
        subprocess.run([sys.executable, str(HERE / 'redck.py'), 'audit', d['handoff'], '--attempt-id', d['attempt_id']],
                       stdout=subprocess.DEVNULL, check=False)
    report_strays(found)
    close('completed', 0)
    print(result)
    deliver_quietly(dispatch_file)
    queue_prune(d, attempt, agent_id)
    return 0


def delivery_path(d):
    return Path(d['artifacts_dir']) / (Path(d['result']).stem + '.delivery.json')


def unregistered_receiver(receiver, tree):
    """Warn at prepare when the notify receiver is not in the registry: the verdict would stay pending."""
    p = script('messages.py', 'list', '--receivers', cwd=tree)
    if p.returncode == 0 and not any(l.split('\t')[0] == receiver for l in p.stdout.splitlines()):
        say('verdict-delivery: receiver %s is not registered; register it (messages.py register --name %s --harness <h>) before the verdict is recorded' % (receiver, receiver))


def verdict_word(d, attempt):
    """pass or fail from a verifier or plan-reviewer report; completed for a role with no verdict; failed or invalid when no usable report."""
    code = attempt.get('exit_code')
    if code == 1:
        return 'failed'
    if code == 3:
        return 'invalid'
    return results.key_value(d['result'], d['role']) or 'completed'


def deliver(dispatch_file, quiet=False):
    """Send the verdict message a dispatch asked for (--notify), once. Returns 0 sent or nothing asked, 4 pending, 5 attempt not yet recorded.

    State lives in <stem>.delivery.json: sending (intent written before the send), sent, or pending (a send failed). A retry
    finds an earlier send by the attempt id in the topic, so a crash between send and mark cannot send twice. The message
    carries the verdict word, the role, the attempt id and the result path only, never result text. Delivery is
    result-recorded then message-delivered; a parent handling it is not tracked here (T-0383)."""
    d = json.loads(Path(dispatch_file).read_text(encoding='utf-8'))
    receiver = d.get('notify')
    if not receiver:
        return 0
    path = delivery_path(d)
    attempt = read_attempt(d['attempt_file'])
    if attempt.get('status') == 'running':
        if Path(d['result']).is_file() and Path(d['result']).stat().st_size:
            say('verdict-delivery: UNRECORDED report %s exists but attempt %s is still running; run: python3 %s record %s'
                % (d['result'], attempt.get('name'), HERE / 'dispatch.py', dispatch_file))
        else:
            say('verdict-delivery: attempt %s is still running; nothing to deliver yet' % attempt.get('name'))
        return 5
    state = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
    if state.get('state') == 'sent':
        if not quiet:
            say('verdict-delivery: already sent to %s (%s); nothing resent' % (receiver, state.get('message')))
        return 0
    word = verdict_word(d, attempt)
    aid = d['attempt_id']
    topic = 'verdict %s-%s %s attempt %s' % (d['role'], d['level'], word, aid)
    state = dict(attempt_id=aid, receiver=receiver, re=d.get('notify_re') or '', topic=topic, state='sending', verdict=word)
    run_lifecycle.write(path, state)
    tree = d['tree']
    found = script('messages.py', 'list', '--receiver', receiver, cwd=tree)
    prior = [l.split('\t')[2] for l in found.stdout.splitlines() if len(l.split('\t')) > 4 and ' attempt %s' % aid in l.split('\t')[4]] if found.returncode == 0 else []
    if prior:
        sent, how = prior[0], 'found'
    else:
        body = '\n'.join(['role: %s-%s' % (d['role'], d['level']), 'attempt: ' + aid, 'verdict: ' + word, 'result: ' + d['result'],
                          'handoff: ' + d['handoff'], 'This is a receipt: no reply is requested.'])
        args = ['send', '--receiver', receiver, '--topic', topic, '--follow-up', 'false']
        if d.get('notify_re'):
            args += ['--re', d['notify_re']]
        p = script('messages.py', *args, body, cwd=tree)
        if p.returncode != 0:
            state.update(state='pending', error=(p.stderr.strip() or p.stdout.strip())[:300])
            run_lifecycle.write(path, state)
            say('verdict-delivery: PENDING for %s (%s); once fixed run: python3 %s deliver %s' % (receiver, state['error'], HERE / 'dispatch.py', dispatch_file))
            return 4
        sent, how = os.path.basename(p.stdout.strip())[:-3], 'sent'
    st = script('messages.py', 'status', '--receiver', receiver, cwd=tree)
    poller = next((l.split(': ', 1)[1] for l in st.stdout.splitlines() if l.startswith('status: ')), 'unknown')
    state.update(state='sent', message=sent, poller=poller, sent_at=run_lifecycle.now())
    state.pop('error', None)
    run_lifecycle.write(path, state)
    say('verdict-delivery: %s %s to %s as %s' % (word, how, receiver, sent))
    if poller != 'listening':
        say('verdict-delivery: %s has no listening poller (status %s); the message waits in new/%s until something reads it. '
            'Watch new/%s from the conductor with a Monitor, or run: python3 %s wait --receiver %s'
            % (receiver, poller, receiver, receiver, HERE / 'messages.py', receiver))
    return 0


def deliver_quietly(dispatch_file):
    """deliver() for record: a delivery fault never changes the record's own exit code."""
    try:
        deliver(dispatch_file)
    except Exception as e:  # the pending file or the stderr line is the signal
        say('verdict-delivery: FAILED (%s); once fixed run: python3 %s deliver %s' % (e, HERE / 'dispatch.py', dispatch_file))


def solo_dispatch(path):
    """The dict of a solo_run.py dispatch file (role solo, an attempt_id, no attempt_file), else None."""
    try:
        d = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    ok = isinstance(d, dict) and d.get('role') == 'solo' and d.get('attempt_id') and d.get('artifacts_dir') and 'attempt_file' not in d
    return d if ok else None


def read_stdin():
    try:
        return '' if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read()
    except (OSError, ValueError):
        return ''


def main(argv):
    ap = argparse.ArgumentParser(prog='dispatch.py', description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    p = sub.add_parser('prepare', help='run the pre-launch gates and print the dispatch JSON')
    p.add_argument('--dry-run', action='store_true', help='print the JSON; write no record, take no lock')
    p.add_argument('--solo-model', default='', choices=('', 'sonnet', 'opus', 'fable', 'haiku'),
                   help="the solo ticket's model when its runs.jsonl record is not in this tree (a sub-agent lane worktree): the verifier family rule reads it")
    p.add_argument('--routing-reason', help='why this role and level; wins over SDLC_ROUTING_REASON (a command that starts with VAR=... misses a Bash(python3:*) allowlist)')
    pg = p.add_mutually_exclusive_group()
    pg.add_argument('--prune', dest='prune', action='store_true', default=None, help='queue this agent for pruning after a recorded result (the default for a one-shot role)')
    pg.add_argument('--no-prune', dest='prune', action='store_false', help='never queue this agent for pruning')
    p.add_argument('--notify', default='', metavar='RECEIVER', help='mailbox receiver that gets the verdict message when record closes the attempt (T-0383)')
    p.add_argument('--notify-re', default='', metavar='ID', help='with --notify: the message id the verdict answers')
    for key in ('role', 'level', 'handoff'):
        p.add_argument(key)
    r = sub.add_parser('record', help='validate and record a dispatched role, and close its attempt')
    r.add_argument('dispatch', help='the <stem>.dispatch.json prepare wrote')
    r.add_argument('--agent-id', help='the sub-agent id the Agent tool returned')
    r.add_argument('--tokens', type=int, help='subagent_tokens from the completion notice')
    r.add_argument('--tool-uses', type=int, help='tool_uses from the completion notice')
    r.add_argument('--transcript', help='the sub-agent transcript (jsonl); its usage (input, output, cache read and write) prices the run')
    r.add_argument('--duration-ms', type=int, help='duration_ms from the completion notice')
    dl = sub.add_parser('deliver', help='send (or confirm sent) the verdict message a dispatch asked for with --notify; idempotent')
    dl.add_argument('dispatch', help='the <stem>.dispatch.json prepare wrote')
    st = sub.add_parser('status', help='print each attempt in a handoff dir: running, completed, failed, orphaned, or interrupted')
    st.add_argument('directory')
    st.add_argument('--orphans', action='store_true', help='print only orphaned attempts')
    rc_ = sub.add_parser('recover', help='mark orphaned attempts interrupted')
    rc_.add_argument('directory')
    rs = sub.add_parser('resume', help='print the resume ladder for an orphaned attempt')
    rs.add_argument('name', help='the attempt stem or Agent name')
    rs.add_argument('--root', default='.', help='where to search for attempt records')
    pr = sub.add_parser('prune', help='list the finished sub-agents to stop, with the stop call for each')
    pr.add_argument('--root', default='.', help='the project root holding .sdlc/runtime/prune.json')
    pg2 = pr.add_mutually_exclusive_group()
    pg2.add_argument('--done', metavar='NAME', help='remove NAME from the queue once it is stopped')
    pg2.add_argument('--add', metavar='NAME', help='queue NAME (a landed builder or solo)')
    pr.add_argument('--role', default='', help='with --add: the agent role')
    pr.add_argument('--level', default='', help='with --add: the agent level')
    sub.add_parser('selftest', help='run the regression cases in temp repos')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    if args.cmd == 'prune':
        try:
            if args.done:
                print('pruned: ' + args.done if prune_done(args.root, args.done) else 'not queued: ' + args.done)
            elif args.add:
                prune_add(args.root, args.add, args.role, args.level)
                print('queued: ' + args.add)
            else:
                print('\n'.join(prune_lines(args.root)))
        except OSError as e:
            print('dispatch.py: ' + str(e), file=sys.stderr)
            return 2
        return 0
    if args.cmd == 'deliver':
        try:
            return deliver(args.dispatch)
        except (OSError, ValueError, KeyError) as e:
            print('dispatch.py: cannot deliver from %s: %s' % (args.dispatch, e), file=sys.stderr)
            return 2
    if args.cmd in ('status', 'recover', 'resume'):
        try:
            if args.cmd == 'status':
                out = status(args.directory, args.orphans)
            elif args.cmd == 'resume':
                out = resume(args.name, args.root)
            else:
                out = ['marked interrupted: ' + n for n in recover_orphans(args.directory)[0]] or ['no orphaned attempts']
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
        except OSError as e:
            print('dispatch.py: ' + str(e), file=sys.stderr)
            return 2
        print('\n'.join(out))
        return 0
    if args.cmd == 'record':
        used = {k: v for k, v in (('subagent_tokens', args.tokens), ('tool_uses', args.tool_uses)) if v is not None}
        if args.transcript:  # T-0328: the notice count excludes cache reads; the transcript usage does not
            used = {**(cost_estimate.transcript_usage(args.transcript) or {}), **{k: v for k, v in used.items() if k != 'subagent_tokens'}} \
                if cost_estimate.transcript_usage(args.transcript) else used
        try:
            sd = solo_dispatch(args.dispatch)
            if sd:  # T-0350: a solo_run.py dispatch has no attempt file; recording it prices the row and clears the live marker
                import solo_run
                cost = solo_run.complete(sd['artifacts_dir'], sd['attempt_id'], sd.get('tier') or 'L1', args.transcript, args.tokens,
                                         agent_id=args.agent_id, tool_uses=args.tool_uses, duration_ms=args.duration_ms)
                print('solo recorded%s; live marker cleared' % ('' if cost is None else ', cost_usd %s' % cost))
                return 0
            return record(args.dispatch, stdin=read_stdin, agent_id=args.agent_id, usage=used or None, duration_ms=args.duration_ms,
                          resolved_model=cost_estimate.transcript_model(args.transcript) if args.transcript else None,
                          transcript=args.transcript)
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
        except (OSError, ValueError) as e:
            print('dispatch.py: ' + str(e), file=sys.stderr)
            return 2
    if args.routing_reason is not None:
        os.environ['SDLC_ROUTING_REASON'] = args.routing_reason
    try:
        out = prepare(args.role, args.level, args.handoff, dry_run=args.dry_run, solo=args.solo_model, prune=args.prune,
                      notify=args.notify, notify_re=args.notify_re)
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
        with clean_env(SDLC_DRY_RUN='1', SDLC_CLAUDE_EXEC='1', **env):
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
        ok = rc == rrc and (rc != 0 or (got['model'], got['effort'], os.path.basename(got['result'])) == (agent_alias(model), effort, name))
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

        # 2b. A solo ticket has no builder result: the newest solo record in runs.jsonl holds the family (T-0284).
        so = sdlc / 'so'
        put(so / 'handoff.md')
        for smodel, level, want in (('sonnet', 'L2', 'opus'), ('sonnet', 'L1', 'opus'), ('opus', 'L2', 'sonnet'), ('sonnet', 'L3', 'fable')):
            (so / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'level': 'L2', 'model': smodel}) + '\n')
            rc, got, _ = prep(repo, 'verifier', level, '.sdlc/so/handoff.md', '--dry-run')
            case('verifier %s after a %s solo gets %s' % (level, smodel, want), rc == 0 and got['model'] == want)
        (so / 'runs.jsonl').unlink()
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run')
        case('verifier L2 with no solo record keeps sonnet', rc == 0 and got['model'] == 'sonnet')
        # T-0356: a sub-agent lane worktree holds no solo record, so fanout prep passes --solo-model
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run', '--solo-model', 'sonnet')
        case('verifier L2 with --solo-model sonnet and no record moves to opus, same effort', rc == 0 and (got['model'], got['effort']) == ('opus', 'high'))
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run', '--solo-model', 'opus')
        case('negative control: verifier L2 with --solo-model opus keeps sonnet', rc == 0 and got['model'] == 'sonnet')
        (so / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'level': 'L3', 'model': 'opus'}) + '\n')
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run', '--solo-model', 'sonnet')
        case('the runs.jsonl solo record wins over --solo-model: an opus record keeps verifier L2 on sonnet', rc == 0 and got['model'] == 'sonnet')
        (so / 'runs.jsonl').unlink()

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

        # link check (T-0379): a builder or verifier on a step handoff that cites a prior attempt's report at the live
        # step path, or a path that does not exist, is refused before any record; the superseded path passes
        lk = sdlc / 'lk'
        put(lk / 'step-3.superseded-1' / 'builder-L3.md', '## Status\ndone\n')
        for role in ('builder', 'verifier'):
            put(lk / 'step-3' / 'handoff.md', '## Task goal\ng\n\nPrior attempt: .sdlc/lk/step-3/builder-L3.md\n')
            err = refused('link check ' + role, 2, role, 'L1', '.sdlc/lk/step-3/handoff.md', 'links')
            case('link check %s names the path and the superseded fix' % role, 'step-3.superseded-1/builder-L3.md' in err)
            put(lk / 'step-3' / 'handoff.md', '## Task goal\ng\n\nPrior attempt: .sdlc/lk/step-3.superseded-1/builder-L3.md\n')
            case('link check %s passes once the link names the superseded folder' % role,
                 prep(repo, role, 'L1', '.sdlc/lk/step-3/handoff.md', '--dry-run')[0] == 0)
        put(lk / 'step-3' / 'handoff.md', '## Task goal\ng\n\nRead .sdlc/lk/step-3.superseded-1/builder-L9.md\n')
        err = refused('link check absent path', 2, 'builder', 'L1', '.sdlc/lk/step-3/handoff.md', 'links')
        case('link check names an absent path', 'does not exist' in err and 'builder-L9.md' in err)
        shutil.rmtree(lk)

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

        ticket(sdlc / 'ls', 'L1')  # lane gate
        for role in ('planner', 'builder', 'plan-reviewer'):
            err = refused('lane gate ' + role, 5, role, 'L1', '.sdlc/ls/handoff.md', 'lane')
        case('lane gate prints the solo command and the override', 'solo_run.py run --task-dir' in err and '--tier L1 ' in err and 'SDLC_LANE_OVERRIDE' in err)
        for alias, level in (('S', 'L1'), ('M', 'L2')):  # a deprecated alias size gets the level in the solo command
            ticket(sdlc / ('la' + alias), alias)
            err = refused('lane gate alias ' + alias, 5, 'planner', 'L1', '.sdlc/la%s/handoff.md' % alias, 'lane')
            case('lane gate on alias size %s prints --tier %s' % (alias, level), '--tier %s ' % level in err)
        ticket(sdlc / 'l2', 'L2')
        case('lane gate on size L2 prints --tier L2', '--tier L2 ' in refused('lane gate L2', 5, 'planner', 'L1', '.sdlc/l2/handoff.md', 'lane'))
        put(sdlc / 'ls' / 'step-1' / 'handoff.md', '## Step 1\n')
        refused('lane gate on a step', 5, 'builder', 'L1', '.sdlc/ls/step-1/handoff.md', 'lane')
        for role in ('verifier', 'filer', 'scout'):
            case('lane gate leaves %s alone' % role, prep(repo, role, 'L1', '.sdlc/ls/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'll', 'L3')
        case('lane gate leaves a size L3 ticket alone', prep(repo, 'planner', 'L1', '.sdlc/ll/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'lalias3', 'L')
        case('lane gate leaves an alias size L ticket alone', prep(repo, 'planner', 'L1', '.sdlc/lalias3/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'lk', 'L1')
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

        ticket(sdlc / 'bg', 'L2', budget_usd=10)  # budget gate (verifier: not lane gated)
        put(sdlc / 'bg' / 'runs.jsonl', json.dumps({'role': 'builder', 'cost_usd': 9, 'attempt_id': 'a1'}) + '\n')
        err = refused('budget gate', 4, 'verifier', 'L1', '.sdlc/bg/handoff.md', 'budget')
        case('budget gate names the percent and budget.py ack', '90%' in err and 'budget.py ack' in err)
        put(sdlc / 'bg' / 'budget-ack.md', '---\nusd: 30\nreason: selftest\n---\n')
        case('a budget ack raises the ceiling and it passes', prep(repo, 'verifier', 'L1', '.sdlc/bg/handoff.md', '--dry-run')[0] == 0)
        (sdlc / 'bg' / 'budget-ack.md').unlink()
        put(sdlc / 'bg' / 'runs.jsonl', json.dumps({'role': 'builder', 'cost_usd': 1, 'attempt_id': 'a1'}) + '\n')
        case('under 80 percent passes', prep(repo, 'verifier', 'L1', '.sdlc/bg/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'bn', 'L2')
        case('a ticket with no budget passes', prep(repo, 'verifier', 'L1', '.sdlc/bn/handoff.md', '--dry-run')[0] == 0)

        # preflight: handoff, row, git work tree, commit, generated definition, skills.
        case('preflight: a missing handoff exits 2 like run.sh', prep(repo, 'builder', 'L1', '.sdlc/none/handoff.md')[0] == 2
             == runsh(repo, 'builder', 'L1', '.sdlc/none/handoff.md')[0])
        case('preflight: an unknown row exits 2 like run.sh', prep(repo, 'builder', 'L9', '.sdlc/t/handoff.md')[0] == 2
             == runsh(repo, 'builder', 'L9', '.sdlc/t/handoff.md')[0])
        case('preflight: solo is not a pipeline row', prep(repo, 'solo', 'L2', '.sdlc/t/handoff.md')[0] == 2)
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
        case('subagent type, Agent name, and result path', got['subagent_type'] == 'sdlc-lite:builder-L1' and got['name'] == 'w-builder-L1'
             and got['result'] == str(w / 'builder-L1.md') and got['tmp_prefix'] == str(rr / '.worktrees' / 'tmp' / 'w-builder-L1'))
        head = subprocess.run(['git', '-C', str(rr), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        case('a builder gets its base sha, in the dispatch, base-sha, and the brief',
             got['base_sha'] == head and (w / 'base-sha').read_text() == head + '\n' and 'Base sha: ' + head in got['prompt'])
        case('the brief is the run.sh prompt plus the tree and tmp prefix lines',
             got['prompt'].startswith('w | builder L1\nHandoff: %s\nArtifacts dir: %s\nYour final message is saved verbatim as %s. Make it exactly the output format your instructions define: '
                                      'start with its first heading, with nothing before it and nothing after the last section.\n' % (w / 'handoff.md', w, w / 'builder-L1.md'))
             and 'Tree: %s' % rr in got['prompt'] and 'Throwaway worktrees only under %s' % got['tmp_prefix'] in got['prompt'])
        # T-0366: a solo dispatch's recorded base sha, not the later HEAD, is the verifier's Base sha.
        put(rr / '.sdlc' / 'sb' / 'handoff.md')
        pre = subprocess.run(['git', '-C', str(rr), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        (rr / '.sdlc' / 'sb' / 'solo-L1-sb.dispatch.json').write_text(json.dumps({'role': 'solo', 'base_sha': pre}))
        (rr / 'later.txt').write_text('x')
        subprocess.run(['git', '-C', str(rr), 'add', '-A'], capture_output=True)
        subprocess.run(['git', '-C', str(rr), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'later'], capture_output=True)
        rcs, ds, _ = prep(rr, 'verifier', 'L1', '.sdlc/sb/handoff.md', '--dry-run')
        case('prepare verifier prints the solo dispatch base sha, not the later HEAD',
             rcs == 0 and ds['base_sha'] == pre and 'Base sha: ' + pre in ds['prompt'])
        lw = rr.parent / (rr.name + '-lane')
        subprocess.run(['git', '-C', str(rr), 'worktree', 'add', '-q', '--detach', str(lw), 'HEAD'], capture_output=True)
        (lw / '.sdlc' / 'w').mkdir(parents=True, exist_ok=True)
        shutil.copy(rr / '.sdlc' / 'w' / 'handoff.md', lw / '.sdlc' / 'w' / 'handoff.md')
        rcl, dl, _ = prep(rr, 'verifier', 'L1', str(lw / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree',
             rcl == 0 and dl['tree'] == os.path.realpath(str(lw)) and 'Tree: %s ' % dl['tree'] in dl['prompt']
             and 'Tree: %s ' % rr not in dl['prompt'] and dl['tmp_prefix'].startswith(dl['tree'] + '/.worktrees/tmp/'))
        subprocess.run(['git', '-C', str(rr), 'worktree', 'remove', '--force', str(lw)], capture_output=True)
        # T-0376: a lane forked from a commit newer than a stale stored base records its fork point, so a scope guard lists only the lane.
        def gt(where, *a):
            return subprocess.run(['git', '-C', str(where), '-c', 'user.name=t', '-c', 'user.email=t@t', *a], capture_output=True, text=True).stdout.strip()
        stale = gt(rr, 'rev-parse', 'HEAD')
        (rr / 'main-new.txt').write_text('m')
        gt(rr, 'add', '-A')
        gt(rr, 'commit', '-qm', 'main moves on')
        fork = gt(rr, 'rev-parse', 'HEAD')
        lw2 = rr.parent / (rr.name + '-lane2')
        gt(rr, 'worktree', 'add', '-q', '-b', 'lane2', str(lw2), 'HEAD')
        (lw2 / '.sdlc' / 'w').mkdir(parents=True, exist_ok=True)
        shutil.copy(rr / '.sdlc' / 'w' / 'handoff.md', lw2 / '.sdlc' / 'w' / 'handoff.md')
        (lw2 / 'lane-only.txt').write_text('l')
        gt(lw2, 'add', '-A')
        gt(lw2, 'commit', '-qm', 'lane work')
        lane_head = gt(lw2, 'rev-parse', 'HEAD')
        (lw2 / '.sdlc' / 'w' / 'base-sha').write_text(stale + '\n')
        _, dstale, _ = prep(rr, 'builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a stale stored base older than the lane fork point is replaced by the lane HEAD (not the main checkout HEAD)',
             dstale['base_sha'] == lane_head != stale and lane_head != gt(rr, 'rev-parse', 'HEAD'))
        listed = gt(lw2, 'diff', '--name-only', dstale['base_sha'], '--', '.', ':(exclude).sdlc').split()
        case('the scope-guard diff against that base lists only the lane files', listed == [])
        (lw2 / 'later.txt').write_text('y')
        gt(lw2, 'add', '-A')
        gt(lw2, 'commit', '-qm', 'more lane work')
        listed = gt(lw2, 'diff', '--name-only', dstale['base_sha'], '--', '.', ':(exclude).sdlc').split()
        case('after more lane work the guard diff lists the lane files and not main\'s', listed == ['later.txt'])
        (lw2 / '.sdlc' / 'w' / 'base-sha').write_text(lane_head + '\n')
        _, dkeep, _ = prep(rr, 'builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a stored base at or after the fork point is kept', dkeep['base_sha'] == lane_head)
        (lw2 / '.sdlc' / 'w' / 'base-sha').write_text(fork + '\n')
        _, dfork, _ = prep(rr, 'builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a stored base equal to the fork point is kept', dfork['base_sha'] == fork)
        (lw2 / '.sdlc' / 'w' / 'base-sha').write_text(stale + '\n')
        with clean_env(), cwd(rr), contextlib.redirect_stderr(io.StringIO()):
            os.environ['SDLC_BASE_REF'] = 'HEAD~5000'  # an unresolvable ref gives no floor: the old, ancestor-only rule
            try:
                dnofloor = prepare('builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), dry_run=True)
            finally:
                os.environ.pop('SDLC_BASE_REF', None)
        case('negative control: with no fork floor the stale ancestor is kept', dnofloor['base_sha'] == stale)
        _, dbld, _ = prep(rr, 'builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        _, dver, _ = prep(rr, 'verifier', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('prepare verifier and prepare builder print the same base for the same lane',
             dver['base_sha'] == dbld['base_sha'] == gt(lw2, 'rev-parse', 'HEAD'))
        # T-0381: the handoff in the MAIN checkout, the owned lane worktree as the cwd. The base of a step is, in order,
        # a base the handoff names (a `base: <sha>` line), else the sha recorded at its first dispatch, else the
        # execution tree's HEAD (the lane), never the main checkout's HEAD; a differing supplied SDLC_BASE_SHA is refused.
        mhand, mbase = rr / '.sdlc' / 'w' / 'handoff.md', rr / '.sdlc' / 'w' / 'base-sha'
        mbase_was = mbase.read_text() if mbase.is_file() else None
        mhand_was = mhand.read_text()
        lane_tip2 = gt(lw2, 'rev-parse', 'HEAD')
        main_head = gt(rr, 'rev-parse', 'HEAD')
        orphan = gt(rr, 'commit-tree', gt(rr, 'rev-parse', 'HEAD^{tree}'), '-m', 'not on any branch')

        def shared(**env):
            err = io.StringIO()
            with clean_env(**env), cwd(lw2), contextlib.redirect_stderr(err):
                return prepare('builder', 'L1', str(mhand), dry_run=True)['base_sha'], err.getvalue()
        mbase.write_text(lane_head + '\n')
        got, _ = shared()
        case('a main-checkout handoff run from the lane: a rework keeps the base recorded at the first dispatch, which main does not contain',
             got == lane_head != lane_tip2 and lane_head not in gt(rr, 'rev-list', 'HEAD').split())
        mbase.unlink()
        got, _ = shared()
        case('a main-checkout handoff run from the lane with nothing recorded gets the lane HEAD, not the main checkout HEAD',
             got == lane_tip2 != main_head)
        mbase.write_text(lane_head + '\n')
        got, err = shared(SDLC_BASE_SHA=main_head)
        case('a main-checkout handoff run from the lane refuses a wrong but valid supplied base and keeps the recorded one',
             got == lane_head and 'SDLC_BASE_SHA refused: %s' % main_head in err)
        got, err = shared(SDLC_BASE_SHA=lane_head)
        case('a main-checkout handoff run from the lane accepts a supplied base equal to the pick', got == lane_head and 'refused' not in err)
        mbase.unlink()
        got, err = shared(SDLC_BASE_SHA=main_head)
        case('a main-checkout handoff run from the lane refuses a wrong supplied base on a first dispatch too',
             got == lane_tip2 and 'SDLC_BASE_SHA refused: %s' % main_head in err)
        mbase.write_text(lane_head + '\n')
        mhand.write_text(mhand_was + '\nbase: %s\n' % stale)
        got, _ = shared()
        case('a main-checkout handoff run from the lane: a base the handoff names wins over the recorded one, even older than the fork',
             got == stale != lane_head)
        got, err = shared(SDLC_BASE_SHA=lane_head)
        case('a main-checkout handoff run from the lane: a supplied base that differs from the named one is refused',
             got == stale and 'SDLC_BASE_SHA refused: %s' % lane_head in err)
        mhand.write_text(mhand_was + '\nbase: %s\n' % orphan)
        try:
            shared()
            refused = ''
        except Refuse as e:
            refused = str(e)
        case('a main-checkout handoff run from the lane stops on a named base that is not an ancestor of HEAD',
             'SDLC_BASE_SHA refused' in refused and orphan in refused)
        mhand.write_text(mhand_was)
        with clean_env(), cwd(rr), contextlib.redirect_stderr(io.StringIO()):
            case('negative control: the same main-checkout handoff run from the main checkout does not use the lane',
                 prepare('builder', 'L1', str(mhand), dry_run=True)['base_sha'] == main_head)
        if mbase_was is None:
            mbase.unlink(missing_ok=True)
        else:
            mbase.write_text(mbase_was)
        subprocess.run(['git', '-C', str(rr), 'worktree', 'remove', '--force', str(lw2)], capture_output=True)
        rc2, _, err2 = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', SDLC_DISPATCH_PARENT_PID=str(os.getppid()))
        case('a second prepare with a running attempt and a live parent refuses', rc2 == 2 and 'still running' in err2 and 'builder-L1.attempt.json' in err2
             and 'run_lifecycle.py recover "%s"' % w in err2)
        case('the refused prepare wrote no second record', sorted(p.name for p in w.glob('*.attempt.json')) == ['builder-L1.attempt.json'])
        rc3, d3, err3 = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', '--dry-run', SDLC_DISPATCH_PARENT_PID=str(live))
        with clean_env(SDLC_DISPATCH_PARENT_PID=str(live)), cwd(rr), contextlib.redirect_stderr(io.StringIO()):
            own_next = prepare('verifier', 'L1', '.sdlc/w/handoff.md')
        case('an attempt carrying the caller pid does not block the next prepare (T-0371)',
             own_next['result_name'] == 'verifier-L1' and len(list(w.glob('*.attempt.json'))) == 2)
        for f in list(w.glob('verifier-L1*')):
            f.unlink()
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
        st_dead = status(w)
        case('status: running attempt with a dead parent prints orphaned', st_dead == ['builder-L1 orphaned builder-L1 parent_pid=%d' % dead])
        case('status --orphans lists the orphan', status(w, True) == st_dead)
        a['parent_pid'] = live
        (w / 'builder-L1.attempt.json').write_text(json.dumps(a))
        case('negative control: status --orphans lists none for a live parent', status(w, True) == [])
        case('negative control: a live parent prints running', 'running' in status(w)[0] and 'orphaned' not in status(w)[0])
        a['parent_pid'] = dead
        (w / 'builder-L1.attempt.json').write_text(json.dumps(a))
        a['agent_id'] = 'ag-7'
        (w / 'builder-L1.attempt.json').write_text(json.dumps(a))
        ladder = resume('builder-L1', str(rr))
        case('resume prints SendMessage by name, by id, then the new attempt with the addendum',
             len(ladder) == 3 and 'SendMessage' in ladder[0] and 'w-builder-L1' in ladder[0] and 'SendMessage' in ladder[1] and 'ag-7' in ladder[1]
             and ladder[2].startswith('3. python3 dispatch.py prepare builder L1') and 'git status' in ladder[2] and 'transcript' in ladder[2])
        case('resume replays no old report', 'builder-L1.md' not in ' '.join(ladder))
        a.pop('agent_id')
        a['parent_pid'] = live
        (w / 'builder-L1.attempt.json').write_text(json.dumps(a))
        try:
            resume('builder-L1', str(rr))
            refused = False
        except Refuse:
            refused = True
        case('resume refuses a running attempt', refused)
        a['parent_pid'] = dead
        (w / 'builder-L1.attempt.json').write_text(json.dumps(a))
        rec, _ = recover_orphans(w)
        old_r = json.loads((w / 'builder-L1.attempt.json').read_text())
        case('recover marks it interrupted with run_lifecycle.py text', rec == ['builder-L1.attempt.json'] and old_r['status'] == 'interrupted'
             and old_r['recovery'] == RECOVERY and 'finished_at' in old_r)
        old_r['status'] = 'running'
        (w / 'builder-L1.attempt.json').write_text(json.dumps(old_r))
        (w / 'builder-L1.running').write_text('1\n')
        rc3, got3, err3 = prep(rr, 'builder', 'L1', '.sdlc/w/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live))
        old = json.loads((w / 'builder-L1.attempt.json').read_text())
        case('a dead-parent attempt is recovered first', rc3 == 0 and old['status'] == 'interrupted' and 'finished_at' in old and 'recovered' in err3
             and not (w / 'builder-L1.running').exists())
        case('the new attempt gets the next result name and Agent name', got3['result_name'] == 'builder-L1-2'
             and got3['result'] == str(w / 'builder-L1-2.md') and got3['name'] == 'w-builder-L1-2'
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
        case('the Agent name fits 64 characters and keeps the step and attempt suffix', len(long_name) <= NAME_MAX and long_name.endswith('-s12-plan-reviewer-L1-12')
             and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', long_name) is not None)

        # 7a. T-0363: the host's agent list cuts a name at 24 characters and a prompt's first line at 50
        # (docs/references/subagent-list-style.md): two attempts of two tickets stay apart in both columns.
        rows = []
        for tid, tslug, ttitle in (('T-0153', '0153-harness-coverage-for-the-spawn-gate', 'Harness coverage for the spawn gate and its retries'),
                                   ('T-0227', '0227-harness-coverage-for-the-verifier', 'Harness coverage for the verifier and its retries')):
            tdir = rr / '.sdlc' / tslug
            put(tdir / 'handoff.md', '\n'.join(['---', 'id: ' + tid, 'title: "%s"' % ttitle, 'type: chore', 'status: ready', 'size: L4',
                                                'priority: P2', 'depends: []', 'created: 2026-10-08', '---', '', '## Goal', 'x', '']))
            for _attempt in range(2):
                rcn, gn, errn = prep(rr, 'builder', 'L3', '.sdlc/%s/handoff.md' % tslug, SDLC_DISPATCH_PARENT_PID=str(live))
                if gn is None:
                    print(errn)
                    break
                af = Path(gn['attempt_file'])
                an = json.loads(af.read_text())
                an['status'] = 'interrupted'  # the retry: its predecessor ended without a report
                af.write_text(json.dumps(an))
                rows.append((gn['name'], gn['prompt'].splitlines()[0], gn['prompt'].splitlines()[1], gn['description']))
        for r_name, r_first, _, r_desc in rows:
            print('  list row: %-26s | %-50s | %s' % (r_name, r_first, r_desc))
        case('four attempts of two tickets print four names', len(rows) == 4 and all(r[0] for r in rows))
        case('the first 24 name characters differ across all attempts', len({r[0][:24] for r in rows}) == len(rows))
        case('each first prompt line is at most 50 characters and starts with the ticket id',
             all(len(r[1]) <= 50 and r[1].startswith(('T-0153 ', 'T-0227 ')) for r in rows))
        case('line 2 of the prompt is the Handoff line and the description is 3 to 5 words',
             all(r[2].startswith('Handoff: ') and 3 <= len(r[3].split()) <= 5 for r in rows))
        case('a retry adds its number last and keeps the ticket first',
             rows[0][0] == '0153-builder-L3' and rows[1][0] == '0153-builder-L3-2' and rows[2][0] == '0227-builder-L3'
             and 'try 2' in rows[1][1] and rows[1][1].startswith('T-0153 ') and 'try' not in rows[0][1])
        case('a name carries no date, sha, or absolute path', not any(re.search(r'\d{4}-\d\d-\d\d|[0-9a-f]{12}|/', r[0] + r[1]) for r in rows))

        # 7b. Every one of the 22 level-table rows (solo too) prints a model the Agent tool accepts.
        for r_role, r_levels in claude_roles.table(PLUGIN).items():
            for r_level, (r_model, _) in r_levels.items():
                if r_role == 'solo':
                    r_printed = agent_alias(r_model)
                else:
                    r_got = prep(repo, r_role, r_level, '.sdlc/t/handoff.md')[1]
                    r_printed = r_got['model'] if r_got else agent_alias(r_model)  # a lane gate refusal prints nothing
                case('row %s %s prints an Agent alias' % (r_role, r_level), r_printed in AGENT_ALIASES)
        case('a bad model is not an Agent alias (negative control)', agent_alias('gpt-9') not in AGENT_ALIASES
             and agent_alias('claude-haiku-5-5') == 'haiku')

        # 8. The CLI: stdout is the JSON alone, the exit code is the gate's.
        env = {k: v for k, v in os.environ.items() if not k.startswith('SDLC_')}
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', '--dry-run', 'scout', 'L1', '.sdlc/t/handoff.md'],
                           cwd=str(repo), capture_output=True, text=True, env=env)
        cli = json.loads(p.stdout) if p.returncode == 0 else {}
        case('CLI prints the dispatch JSON on stdout', p.returncode == 0 and cli.get('model') == 'haiku' and cli.get('subagent_type') == 'sdlc-lite:scout-L1')
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', '--dry-run', '--routing-reason', 'flag reason', 'scout', 'L1', '.sdlc/t/handoff.md'],
                           cwd=str(repo), capture_output=True, text=True, env=dict(env, SDLC_ROUTING_REASON='env reason'))
        case('--routing-reason is read like the env var and wins over it', p.returncode == 0 and json.loads(p.stdout).get('routing_reason') == 'flag reason')
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', '--dry-run', 'scout', 'L1', '.sdlc/t/handoff.md'],
                           cwd=str(repo), capture_output=True, text=True, env=dict(env, SDLC_ROUTING_REASON='env reason'))
        case('the env var stays a fallback', p.returncode == 0 and json.loads(p.stdout).get('routing_reason') == 'env reason')
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'prepare', 'planner', 'L1', '.sdlc/ls/handoff.md'],
                           cwd=str(repo), capture_output=True, text=True, env=env)
        case('CLI exits 5 for the lane gate with the JSON absent from stdout', p.returncode == 5 and p.stdout == '')

        # 9. record: the post-launch half. Parity with a real run.sh run (stub claude), then every refusal.
        stub = tmp / 'bin'
        stub.mkdir()
        (stub / 'claude').write_text('#!/usr/bin/env bash\ncat "$STUB_RESULT"\n')
        (stub / 'claude').chmod(0o755)
        BODY = {'builder': '## Status\ndone\n\n## Changes\nx\n\n## Checks\nx\n',
                'verifier': '## Verdict\npass\n\n## Criteria\n- x\n\n## Out of scope changes\nNone\n\n## For the next attempt\nNone\n',
                'planner': '## Goal\nx\n\n## Assumptions\nNone\n\n## Risks\nNone\n',
                'plan-reviewer': '## Verdict\npass\n\n## Findings\nNone\n'}
        live_pid = str(os.getpid())

        def mk(path):
            init_repo(path)
            put(path / '.sdlc' / 't' / 'handoff.md')
            put(path / '.sdlc' / 't' / 'step-1' / 'handoff.md', '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n')
            put(path / '.sdlc' / 'p' / 'handoff.md')
            return path

        def via_runsh(repo, role, level, rel, **env):
            event = tmp / 'stub-result.json'
            event.write_text(json.dumps({'type': 'result', 'is_error': False, 'result': BODY[role], 'total_cost_usd': 0.5,
                                         'duration_ms': 5, 'num_turns': 2, 'usage': {'input_tokens': 1}}) + '\n')
            with clean_env(PATH=str(stub) + os.pathsep + os.environ['PATH'], STUB_RESULT=str(event), SDLC_CLAUDE_EXEC='1', **env):
                p = subprocess.run(['bash', str(HERE / 'run.sh'), role, level, rel], cwd=str(repo), capture_output=True, text=True)
            return p.returncode, p.stdout.strip(), p.stderr

        def go(repo, role, level, rel, body=None, said=None, mutate=None, validate=validate_result, agent_id=None, **env):
            """prepare, let the role write body (or not), then record in process: (rc, dispatch, stderr, stdout)."""
            rc, got, err = prep(repo, role, level, rel, SDLC_DISPATCH_PARENT_PID=live_pid, **env)
            if rc != 0:
                raise AssertionError('prepare failed in the record selftest: ' + err)
            if body is not None:
                Path(got['result']).write_text(body, encoding='utf-8')
            if mutate:
                f = Path(got['dispatch_file'])
                data = json.loads(f.read_text())
                data.update(mutate)
                f.write_text(json.dumps(data))
            e, o = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
                try:
                    out = record(got['dispatch_file'], stdin=(lambda: said) if said is not None else None, agent_id=agent_id, validate=validate)
                except Refuse as r:
                    print('\n'.join(r.lines), file=sys.stderr)
                    out = r.rc
            return out, got, e.getvalue(), o.getvalue()

        def lines_of(directory):
            return [json.loads(l) for l in (Path(directory) / 'runs.jsonl').read_text().splitlines()] if (Path(directory) / 'runs.jsonl').is_file() else []

        def attempt_of(got):
            return json.loads(Path(got['attempt_file']).read_text())

        def next_out(repo, rel):
            p = script('steps.py', 'next', repo / rel)
            return p.returncode, p.stdout.replace(str(repo), '<repo>')

        ra, rb = mk(tmp / 'A'), mk(tmp / 'B')
        step = '.sdlc/t/step-1'
        for role, level, rel, env in (('builder', 'L2', step, {}), ('verifier', 'L1', step, {}), ('planner', 'L1', '.sdlc/p', {}),
                                      ('plan-reviewer', 'L1', '.sdlc/p', {'SDLC_SPECGATE': 'off'})):
            src, a_result, _ = via_runsh(ra, role, level, rel + '/handoff.md', **env)
            rc, got, err, out = go(rb, role, level, rel + '/handoff.md', body=BODY[role], agent_id='agent-' + role, **env)
            a_line, b_line = lines_of(ra / rel)[-1], lines_of(rb / rel)[-1]
            case('record parity %s: valid result exits 0 like run.sh and prints the result path' % role,
                 src == 0 and rc == 0 and out.strip().splitlines()[0] == got['result'])
            case('record parity %s: runs.jsonl key set is the run.sh set plus agent_id and cost_reason' % role,
                 set(b_line) == set(a_line) | {'agent_id', 'cost_reason'} and set(a_line) <= set(b_line))
            case('record parity %s: transport subagent, agent_id, null cost with its reason' % role,
                 (b_line['transport'], a_line['transport'], b_line['agent_id'], b_line['cost_usd'], b_line['cost_reason'])
                 == ('subagent', 'claude', 'agent-' + role, None, 'subagent usage not priced'))
            case('record parity %s: the shared fields equal the run.sh line shape' % role,
                 (b_line['role'], b_line['level'], b_line['model'], b_line['effort'], b_line['file'], b_line['backend'], b_line['stale_input'],
                  b_line['stray_worktrees'], b_line['stray_branches'], b_line['shared_with_builder'])
                 == (a_line['role'], a_line['level'], a_line['model'], a_line['effort'], a_line['file'], a_line['backend'], a_line['stale_input'],
                     a_line['stray_worktrees'], a_line['stray_branches'], a_line['shared_with_builder'])
                 and b_line['attempt_id'] == got['attempt_id'])
            case('record parity %s: the result header equals the run.sh header' % role,
                 Path(a_result).read_text().splitlines()[0] == Path(got['result']).read_text().splitlines()[0])
            case('record parity %s: specgate and lane_override are carried only when set' % role,
                 ('specgate' in b_line) == ('specgate' in a_line) == (role == 'plan-reviewer') and 'lane_override' not in b_line)
            att = attempt_of(got)
            case('record %s closes the attempt completed with exit_code 0 and the agent id' % role,
                 (att['status'], att['exit_code'], att['agent_id']) == ('completed', 0, 'agent-' + role) and 'finished_at' in att)
            if role in ('builder', 'verifier'):
                na, nb = next_out(ra, rel), next_out(rb, rel)
                want = 'verify L1' if role == 'builder' else 'done'
                case('steps.py next reads a recorded %s result exactly as a run.sh one (%s)' % (role, want),
                     na == nb and na[0] == 0 and na[1].splitlines()[0] == want)
                case('order.py reads a recorded %s result as a run.sh one' % role,
                     os.path.basename(order.newest(str(ra / rel), role)) == os.path.basename(order.newest(str(rb / rel), role)))

        # Invalid results: exit 3, the run.sh line shape, the file and record kept; the control accepts it with an accept-all validator.
        accept_all = lambda role, path: None  # noqa: E731
        for i, (label, role, bad, want) in enumerate((
                ('missing key section', 'builder', '## Changes\nx\n\n## Checks\ny\n', 'lacks ## Status'),
                ('disallowed first value', 'verifier', '## Verdict\nmaybe\n\n## Criteria\n- x\n', 'is not one of pass|fail'),
                ('section order', 'builder', '## Status\ndone\n\n## Checks\ny\n\n## Changes\nx\n', '## Checks comes before ## Changes'))):
            put(rb / '.sdlc' / ('bad%d' % i) / 'handoff.md')
            put(rb / '.sdlc' / ('ctl%d' % i) / 'handoff.md')
            rc, got, err, out = go(rb, role, 'L1', '.sdlc/bad%d/handoff.md' % i, body=bad)
            att, shown = attempt_of(got), err.strip().splitlines()[-1] if err.strip() else ''
            case('invalid result (%s) exits 3' % label, rc == 3 and out == '')
            case('invalid result (%s) prints dispatch.py: %s result <reason>; see <file>' % (label, role),
                 shown == 'dispatch.py: %s result %s; see %s' % (role, shown[len('dispatch.py: %s result ' % role):-len('; see ' + got['result'])], got['result'])
                 and want in shown)
            case('invalid result (%s) keeps the file, the runs.jsonl line, and a failed attempt with exit_code 3' % label,
                 Path(got['result']).read_text().startswith('<!-- role=') and lines_of(rb / '.sdlc' / ('bad%d' % i))[-1]['file'] == Path(got['result']).name
                 and (att['status'], att['exit_code']) == ('failed', 3))
            rc, cgot, err, out = go(rb, role, 'L1', '.sdlc/ctl%d/handoff.md' % i, body=bad, validate=accept_all)
            case('negative control (%s): an accept-all validator lets the same bad result pass' % label,
                 rc == 0 and attempt_of(cgot)['status'] == 'completed' and err == '')

        # A failed sub-agent: error text and no result; a limit text also leaves the resume marker.
        for name in ('f1', 'f2', 'f3'):
            put(rb / '.sdlc' / name / 'handoff.md')
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f1/handoff.md', said='API Error: connection reset by peer')
        f1 = rb / '.sdlc' / 'f1'
        att = attempt_of(got)
        case('a failed sub-agent exits 1 and records status failed with its text', rc == 1 and att['status'] == 'failed' and att['exit_code'] == 1
             and 'connection reset' in att['error'] and 'returned no result' in err)
        case('a failed sub-agent writes no result, no runs.jsonl line, and no limit marker, and keeps the error as a log',
             not Path(got['result']).exists() and lines_of(f1) == [] and not (f1 / 'builder-L1.limit').exists()
             and 'connection reset' in (f1 / 'builder-L1.log').read_text())
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f2/handoff.md')
        case('no result file and no stdin text is a failed sub-agent too', rc == 1 and 'no result file' in attempt_of(got)['error'])
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f3/handoff.md', said='API Error: 429 rate limit exceeded: session limit reached')
        f3 = rb / '.sdlc' / 'f3'
        marker = json.loads((f3 / 'builder-L1.limit').read_text()) if (f3 / 'builder-L1.limit').is_file() else {}
        case('a 429 or session-limit text exits 1 and writes <role>-<level>.limit with the resume command',
             rc == 1 and sorted(marker) == ['evidence', 'handoff', 'level', 'resume', 'role', 'ts'] and '429' in marker['evidence']
             and marker['resume'] == 'python3 %s prepare builder L1 %s' % (HERE / 'dispatch.py', got['handoff'])
             and 'session limit: resume with: ' + marker['resume'] in err)
        put(rb / '.sdlc' / 'v1' / 'handoff.md')
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/v1/handoff.md')
        case('a verifier prompt names the report path it must write before it ends',
             'Report file: %s' % got['result'] in got['prompt'] and 'before you end' in got['prompt'])
        case('a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line',
             rc == 1 and 'no result file at %s' % got['result'] in attempt_of(got)['error'] and 'must write its report there' in attempt_of(got)['error']
             and lines_of(rb / '.sdlc' / 'v1') == [])
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/v1/handoff.md', body=BODY['verifier'])
        case('a verifier with its report on disk is accepted', rc == 0 and attempt_of(got)['status'] == 'completed')
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f3/handoff.md', body=BODY['builder'])
        case('a later success in the same dir removes the limit marker', rc == 0 and not (f3 / 'builder-L1.limit').exists())

        # The CLI: stdin carries the error text; flags carry the notice's numbers.
        env_cli = {k: v for k, v in os.environ.items() if not k.startswith('SDLC_')}
        put(rb / '.sdlc' / 'c1' / 'handoff.md')
        put(rb / '.sdlc' / 'c2' / 'handoff.md')
        rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/c1/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', got['dispatch_file']], input='Error: session limit reached',
                           capture_output=True, text=True, env=env_cli)
        case('CLI record reads error text from stdin: exit 1 and the limit marker', p.returncode == 1 and (rb / '.sdlc' / 'c1' / 'builder-L1.limit').is_file())
        rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/c2/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        Path(got['result']).write_text(BODY['builder'])
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', '--agent-id', 'ag-9', '--tokens', '1234', '--tool-uses', '7',
                            '--duration-ms', '900', got['dispatch_file']], capture_output=True, text=True, env=env_cli, stdin=subprocess.DEVNULL)
        line = lines_of(rb / '.sdlc' / 'c2')[-1] if lines_of(rb / '.sdlc' / 'c2') else {}
        case('CLI record with a result file: exit 0, the path on stdout, the notice numbers in the line',
             p.returncode == 0 and p.stdout.strip() == got['result'] and line.get('agent_id') == 'ag-9' and line.get('duration_ms') == 900
             and line.get('usage') == {'subagent_tokens': 1234, 'tool_uses': 7})
        case('record with notice tokens estimates cost: cost_estimated, cost_basis, no cost_reason',
             line.get('cost_estimated') is True and line.get('cost_basis') == 'tokens x blended'
             and isinstance(line.get('cost_usd'), float) and line['cost_usd'] > 0 and line.get('cost_reason') is None)
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', str(rb / 'nope.dispatch.json')],
                           capture_output=True, text=True, env=env_cli, stdin=subprocess.DEVNULL)
        tr = rb / 'tr.jsonl'
        tr.write_text(json.dumps({'message': {'id': 'm1', 'role': 'assistant', 'model': 'claude-haiku-5-5', 'usage': {'output_tokens': 5}}}) + '\n')
        put(rb / '.sdlc' / 'c3' / 'handoff.md')
        put(rb / '.sdlc' / 'c4' / 'handoff.md')
        for nm, extra in (('c3', ['--transcript', str(tr)]), ('c4', [])):
            rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % nm, SDLC_DISPATCH_PARENT_PID=live_pid)
            Path(got['result']).write_text(BODY['builder'])
            subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record'] + extra + [got['dispatch_file']], capture_output=True, text=True,
                           env=env_cli, stdin=subprocess.DEVNULL)
        case('record with a transcript writes resolved_model beside the alias', lines_of(rb / '.sdlc' / 'c3')[-1].get('resolved_model') == 'claude-haiku-5-5')
        case('record with no transcript writes no resolved_model', 'resolved_model' not in lines_of(rb / '.sdlc' / 'c4')[-1])
        # T-0343: the artifact comes from the transcript when the file and stdin are empty.
        good = {'message': {'id': 'm2', 'role': 'assistant', 'stop_reason': 'end_turn', 'content': [{'type': 'text', 'text': BODY['builder']}]}}
        for nm, rec_ in (('c5', good), ('c6', {'message': {**good['message'], 'stop_reason': 'max_tokens'}})):
            put(rb / '.sdlc' / nm / 'handoff.md')
            rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % nm, SDLC_DISPATCH_PARENT_PID=live_pid)
            tf = rb / (nm + '.jsonl')
            tf.write_text(json.dumps(rec_) + '\n')
            q = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', '--transcript', str(tf), got['dispatch_file']],
                               capture_output=True, text=True, env=env_cli, stdin=subprocess.DEVNULL)
            if nm == 'c5':
                case('empty stdin plus a transcript writes a valid result from the last assistant message',
                     q.returncode == 0 and Path(got['result']).read_text().startswith('<!-- role=builder') and len(lines_of(rb / '.sdlc' / nm)) == 1)
            else:
                case('a truncated transcript message is rejected with a clear error and no result',
                     q.returncode == 1 and 'truncated' in attempt_of(got)['error'] and not Path(got['result']).exists())
        # T-0349: truncated stdin, error stdin beside an interim heading, tool-use turns before the final text.
        def amsg(text, stop='end_turn', tool=False):
            c = ([{'type': 'tool_use', 'id': 't', 'name': 'Bash', 'input': {}}] if tool else []) + ([{'type': 'text', 'text': text}] if text else [])
            return {'message': {'role': 'assistant', 'stop_reason': stop, 'content': c}}
        full = BODY['builder']
        head = full.splitlines()[0]
        interim = amsg('## Status\nworking')
        for nm, said_, recs, ok in (
                ('t1', head, [amsg('x', tool=True), amsg(full)], True),
                ('t2', 'Error: session limit reached', [interim], False),
                ('t3', '', [amsg(full), amsg('', tool=True), {'message': {'role': 'user', 'content': 'x'}}], True),
                ('t4', full, [interim], True),
                ('r6', 'Agent terminated unexpectedly', [amsg(full)], False),
                ('r6b', full[:2], [amsg(full)], True)):
            put(rb / '.sdlc' / nm / 'handoff.md')
            rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % nm, SDLC_DISPATCH_PARENT_PID=live_pid)
            tf = rb / (nm + '.jsonl')
            tf.write_text('\n'.join(json.dumps(r_) for r_ in recs) + '\n')
            q = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', '--transcript', str(tf), got['dispatch_file']],
                               capture_output=True, text=True, env=env_cli, input=said_)
            body_ = Path(got['result']).read_text() if Path(got['result']).is_file() else ''
            if ok:
                case('record %s: result is %s' % (nm, 'the transcript final message' if nm in ('t1', 't3', 'r6b') else 'complete stdin'),
                     q.returncode == 0 and (full.splitlines()[-1] in body_) and ('working' not in body_))
            else:
                if nm == 't2':
                    case('record t2: error stdin stays a failure with the limit marker despite an interim heading',
                         q.returncode == 1 and not Path(got['result']).exists() and (rb / '.sdlc' / nm / 'builder-L1.limit').is_file())
                else:
                    case('record %s: unmatched error stdin is a failure despite a complete transcript' % nm,
                         q.returncode == 1 and not Path(got['result']).exists())
        case('CLI record on a missing dispatch file exits 2', p.returncode == 2 and 'cannot read dispatch file' in p.stderr)
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/c2/handoff.md', body=BODY['builder'])
        case('a second attempt in a dir whose first was recorded is allowed and takes the next name', rc == 0 and got['result_name'] == 'builder-L1-2')
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', str(rb / '.sdlc' / 'c2' / 'builder-L1.dispatch.json')],
                           capture_output=True, text=True, env=env_cli, stdin=subprocess.DEVNULL)
        case('recording a closed attempt again exits 2 and changes nothing', p.returncode == 2 and 'not running' in p.stderr
             and len(lines_of(rb / '.sdlc' / 'c2')) == 2)

        # Stale handoff, strays, and the tmp prefix: reported, never an exit code.
        put(rb / '.sdlc' / 's1' / 'handoff.md')
        rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/s1/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        outside = tmp / 'outside-wt'
        own = Path(got['tmp_prefix']) / 'work'
        for cmd in (['worktree', 'add', '--detach', str(own), 'HEAD'], ['worktree', 'add', '-b', got['name'] + '-stray', str(outside), 'HEAD'],
                    ['worktree', 'add', '--detach', str(rb / '.worktrees' / 'tmp' / 'other-role'), 'HEAD'],
                    ['worktree', 'add', '-b', 'peer-br', str(tmp / 'peer-wt'), 'HEAD']):
            subprocess.run(['git', '-C', str(rb)] + cmd, check=True, capture_output=True)
        (rb / '.sdlc' / 's1' / 'handoff.md').write_text('## Goal\nchanged\n')
        Path(got['result']).write_text(BODY['builder'])
        e, o = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
            rc = record(got['dispatch_file'])
        err, line = e.getvalue(), lines_of(rb / '.sdlc' / 's1')[-1]
        listed = subprocess.run(['git', '-C', str(rb), 'worktree', 'list', '--porcelain'], capture_output=True, text=True).stdout
        case('a changed handoff is reported as stale input and flagged, with the exit code unchanged',
             rc == 0 and 'stale input: %s changed while builder ran' % got['handoff'] in err and line['stale_input'] is True)
        sb, other = got['name'] + '-stray', rb / '.worktrees' / 'tmp' / 'other-role'
        case('strays are reported with their branch, listed in the line, with the exit code unchanged',
             'stray worktree appeared during this run: %s [%s]' % (outside, sb) in err
             and 'stray worktree appeared during this run: %s\n' % other in err
             and 'stray branch appeared during this run: ' + sb in err
             and sorted(line['stray_worktrees']) == sorted([str(outside), str(other)]) and line['stray_branches'] == [sb])
        case('a peer worktree and branch outside the role prefixes are not reported (negative control: the role own strays are)',
             'peer-br' not in err and 'peer-wt' not in err and 'peer-br' not in line['stray_branches']
             and str(tmp / 'peer-wt') not in line['stray_worktrees'])
        case('the dispatch tmp prefix is removed, its worktree unregistered, and it is not reported as a stray',
             not Path(got['tmp_prefix']).exists() and str(own) not in listed and str(own) not in err)
        case('the outside worktrees are only reported, never removed', outside.is_dir() and str(outside) in listed)

        # Guards on a tampered dispatch file: nothing outside the tmp root is removed, nothing outside the artifacts dir is written.
        keep = tmp / 'keep-me'
        (keep / 'sub').mkdir(parents=True)
        for name in ('g1', 'g2', 'g3', 'g4'):
            put(rb / '.sdlc' / name / 'handoff.md')
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/g1/handoff.md', body=BODY['builder'], mutate={'tmp_prefix': str(keep)})
        case('a tmp prefix outside <tree>/.worktrees/tmp is refused, not removed', rc == 0 and keep.is_dir() and 'refusing to remove' in err)
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/g2/handoff.md', body=BODY['builder'], mutate={'result': str(tmp / 'elsewhere.md')})
        case('a result path outside the artifacts dir exits 2 and writes nothing', rc == 2 and not (tmp / 'elsewhere.md').exists()
             and attempt_of(got)['status'] == 'running')
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/g3/handoff.md', body=BODY['builder'], mutate={'attempt_id': 'not-this-one'})
        case('a dispatch file for another attempt exits 2', rc == 2 and 'another attempt' in err)
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/g4/handoff.md', body='<!-- role=builder level=L5 model=fable effort=max -->\n' + BODY['builder'],
                               mutate={'lane_override': 'chain needed'})
        head_lines = Path(got['result']).read_text().splitlines()
        case('a header the role wrote is replaced by the dispatch header, once', rc == 0 and head_lines[0] == '<!-- role=builder level=L1 model=sonnet effort=low -->'
             and not head_lines[1].startswith('<!--'))
        case('a lane_override carried by the dispatch reaches the runs.jsonl line', lines_of(rb / '.sdlc' / 'g4')[-1].get('lane_override') == 'chain needed')

        # T-0368 prune: prepare sets the flag per role; record queues exactly the pruneable agents; prune lists and clears the queue.
        for i, role in enumerate(PRUNE_ROLES + ('builder',)):
            put(rb / '.sdlc' / ('pf%d' % i) / 'handoff.md')
            rc, got, err = prep(rb, role, 'L1', '.sdlc/pf%d/handoff.md' % i, '--dry-run', SDLC_SPECGATE='off')
            case('prune flag: prepare sets prune %s for %s' % (role != 'builder', role), rc == 0 and got['prune'] is (role != 'builder'))
        rc, got, err = prep(rb, 'scout', 'L1', '.sdlc/pf0/handoff.md', '--dry-run', '--no-prune')
        case('prune flag: --no-prune turns a one-shot role off', rc == 0 and got['prune'] is False)
        rc, got, err = prep(rb, 'builder', 'L1', '.sdlc/pf8/handoff.md', '--dry-run', '--prune')
        case('prune flag: --prune turns a builder on', rc == 0 and got['prune'] is True)
        try:
            rc, got, err = prep(rb, 'scout', 'L1', '.sdlc/pf0/handoff.md', '--dry-run', '--prune', '--no-prune')
        except SystemExit as e:
            rc = e.code
        case('prune flag: --prune with --no-prune is a usage error', rc == 2)

        rp = mk(tmp / 'C')
        def queued(repo):
            return prune_read(str(repo))

        FILER = '## Warnings\nNone\n\n## PR title\nt\n\n## PR body\nb\n\n## Changelog entry\nc\n\n## Follow-ups\n%s\n'
        for name in ('q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7'):
            put(rp / '.sdlc' / name / 'handoff.md')
        rc, got, err, out = go(rp, 'verifier', 'L1', '.sdlc/q1/handoff.md', body=BODY['verifier'], agent_id='ag-v')
        q = queued(rp)
        case('prune record: a recorded verifier prints prune: <name> and is queued with id, role, level and time',
             rc == 0 and 'prune: %s' % got['name'] in out.splitlines() and len(q) == 1
             and (q[0]['name'], q[0]['agent_id'], q[0]['role'], q[0]['level']) == (got['name'], 'ag-v', 'verifier', 'L1') and q[0]['recorded_at'])
        rc, got, err, out = go(rp, 'builder', 'L1', '.sdlc/q2/handoff.md', body=BODY['builder'], agent_id='ag-b')
        case('prune record: a recorded builder prints no prune line and is not queued', rc == 0 and 'prune:' not in out and len(queued(rp)) == 1)
        rc, got, err, out = go(rp, 'scout', 'L1', '.sdlc/q3/handoff.md', body=None, said='boom no heading', agent_id='ag-f')
        case('prune record: a failed record (exit 1) is not queued', rc == 1 and 'prune:' not in out and len(queued(rp)) == 1)
        rc, got, err, out = go(rp, 'filer', 'L1', '.sdlc/q4/handoff.md', body=FILER % 'fix-now: tidy the thing', agent_id='ag-p')
        case('prune record: a result with a pending follow-up is not queued', rc == 0 and 'prune:' not in out and len(queued(rp)) == 1)
        rc, got, err, out = go(rp, 'filer', 'L1', '.sdlc/q5/handoff.md', body=FILER % 'None', agent_id='ag-n')
        case('prune record: a result whose follow-ups are None is queued', rc == 0 and 'prune: %s' % got['name'] in out and len(queued(rp)) == 2)
        rc, got, err, out = go(rp, 'planner', 'L1', '.sdlc/q6/handoff.md', body=BODY['planner'], agent_id='ag-x', mutate={'prune': False})
        case('prune record: a dispatch with prune false is not queued (negative control)', rc == 0 and 'prune:' not in out and len(queued(rp)) == 2)
        rc, got, err, out = go(rp, 'planner', 'L1', '.sdlc/q7/handoff.md', body=BODY['planner'], agent_id='ag-z')
        d7, a7 = json.loads(Path(got['dispatch_file']).read_text()), attempt_of(got)
        again = io.StringIO()
        sib = Path(got['artifacts_dir']) / 'planner-L1-9.attempt.json'
        sib.write_text(json.dumps({'agent_name': got['name'], 'status': 'running'}))
        with contextlib.redirect_stdout(again):
            requeued = queue_prune(d7, a7, 'ag-z')
        case('prune record: an agent with another attempt still open is not queued', requeued is False and again.getvalue() == '')
        sib.unlink()
        names = [e['name'] for e in queued(rp)]
        shown = prune_lines(str(rp))
        case('prune list: one TaskStop task_id=<name> line per queued agent', len(shown) == 3
             and all(l.startswith('TaskStop task_id=%s ' % n) for l, n in zip(shown, names)))
        listed = io.StringIO()
        with contextlib.redirect_stdout(listed):
            rc_list = main(['prune', '--root', str(rp)])
        case('prune command lists the queue', rc_list == 0 and listed.getvalue().count('TaskStop task_id=') == 3)
        out_done = io.StringIO()
        with contextlib.redirect_stdout(out_done):
            main(['prune', '--root', str(rp), '--done', names[0]])
            main(['prune', '--root', str(rp), '--done', 'nobody'])
            main(['prune', '--root', str(rp), '--add', 'T-0900-solo', '--role', 'solo', '--level', 'L2'])
        after = [e['name'] for e in queued(rp)]
        case('prune --done removes one entry, --add queues a landed solo, an unknown name changes nothing',
             after == names[1:] + ['T-0900-solo'] and 'not queued: nobody' in out_done.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            for n in after:
                main(['prune', '--root', str(rp), '--done', n])
        empty = io.StringIO()
        with contextlib.redirect_stdout(empty):
            main(['prune', '--root', str(rp)])
        case('prune on an empty queue says so', empty.getvalue().strip() == 'prune: nothing queued')

        # 11. T-0383: a recorded verdict reaches the requesting receiver with no manual conductor step, and a miss is observable.
        vr = mk(tmp / 'V')
        msgs = lambda recv, state='new': sorted((vr / '.sdlc' / 'messages' / state / recv).glob('*.md')) if (vr / '.sdlc' / 'messages' / state / recv).is_dir() else []
        mcmd = lambda *a: subprocess.run([sys.executable, str(HERE / 'messages.py')] + list(a), cwd=str(vr), capture_output=True, text=True)
        case('selftest setup: the receiver registers', mcmd('register', '--name', 'codex', '--harness', 'codex', '--reader', 'sess-1').returncode == 0)

        def notified(rel, *flags, body=BODY['verifier'], role='verifier', level='L1', record_it=True):
            """prepare with --notify, let the role write body, record in process: (rc, dispatch, stderr)."""
            put(vr / '.sdlc' / rel / 'handoff.md')
            try:
                rc, got, err = prep(vr, role, level, '.sdlc/%s/handoff.md' % rel, '--notify', 'codex', *flags, SDLC_DISPATCH_PARENT_PID=live_pid)
            except SystemExit:
                return 2, None, 'prepare does not take --notify'
            if rc != 0:
                return rc, got, err
            if body is not None:
                Path(got['result']).write_text(body, encoding='utf-8')
            if not record_it:
                return 0, got, err
            e, o = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
                out = record(got['dispatch_file'], validate=validate_result)
            return out, got, e.getvalue()

        rc, got, err = notified('n1')
        n1 = msgs('codex')
        body_n1 = n1[0].read_text() if n1 else ''
        case('record then verdict message: one message reaches the receiver at record, with the attempt id, pass, and the result path',
             rc == 0 and len(n1) == 1 and got['attempt_id'] in body_n1 and 'verdict: pass' in body_n1 and got['result'] in body_n1)
        case('the verdict message asks for no reply and carries no result text', 'follow_up_requested: false' in body_n1 and 'Criteria' not in body_n1)
        dl = json.loads((Path(got['artifacts_dir']) / 'verifier-L1.delivery.json').read_text()) if n1 else {}
        case('the delivery record is sent and names the message', dl.get('state') == 'sent' and dl.get('message') == n1[0].stem)
        t0 = time.mktime(time.strptime(attempt_of(got)['finished_at'][:19], '%Y-%m-%dT%H:%M:%S'))
        sent_at = re.search(r'^send_time: (\S+)', body_n1, re.M)
        gap = abs(time.mktime(time.strptime(sent_at.group(1)[:19], '%Y-%m-%dT%H:%M:%S')) - t0) if sent_at else 9999
        case('T-0297 fixture: the verdict is in the mailbox at the record moment, not minutes later (gap under 5 s, was about 7 minutes)', gap < 5)
        case('a poller that is not listening is named on stderr with the Monitor route', 'no listening poller' in err and 'Monitor' in err and 'new/codex' in err)
        case('the delivery record keeps the poller state', dl.get('poller') in ('none', 'stalled', 'expired', 'stopped', 'failed'))
        # Control: a dispatch without --notify sends nothing.
        put(vr / '.sdlc' / 'n0' / 'handoff.md')
        rc0, got0, _ = prep(vr, 'verifier', 'L1', '.sdlc/n0/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        Path(got0['result']).write_text(BODY['verifier'], encoding='utf-8')
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            record(got0['dispatch_file'])
        case('control: a dispatch with no --notify sends no message and writes no delivery record', len(msgs('codex')) == 1 and 'notify' not in got0
             and not (vr / '.sdlc' / 'n0' / 'verifier-L1.delivery.json').exists())

        # Duplicate delivery: a rerun after sent sends nothing; a crash between send and mark finds the earlier send by attempt id.
        e = io.StringIO()
        with contextlib.redirect_stderr(e):
            again = deliver(got['dispatch_file'])
        case('duplicate delivery: deliver after sent resends nothing', again == 0 and len(msgs('codex')) == 1 and 'nothing resent' in e.getvalue())
        dfile = Path(got['artifacts_dir']) / 'verifier-L1.delivery.json'
        dfile.write_text(json.dumps({'attempt_id': got['attempt_id'], 'receiver': 'codex', 'state': 'sending'}))
        with contextlib.redirect_stderr(io.StringIO()):
            again = deliver(got['dispatch_file'])
        case('duplicate delivery: a crash between send and mark (state sending) marks sent without a second message',
             again == 0 and len(msgs('codex')) == 1 and json.loads(dfile.read_text()).get('state') == 'sent')

        # A listening poller raises no warning.
        act = mcmd('activate', '--receiver', 'codex', '--worker', 'inbox-v-codex', '--kind', 'parent', '--stop', 'test', '--interval', '60', '--window', '600')
        rc, got2, err = notified('n2')
        case('selftest setup: the receiver gets a lease', act.returncode == 0)
        case('a listening poller: the message is delivered and no idle-poller warning is printed', rc == 0 and len(msgs('codex')) == 2 and 'no listening poller' not in err)

        # An attempt left running after the report was written is observable and delivers nothing until recorded.
        rc, got3, err = notified('n3', record_it=False)
        listed = status(got3['artifacts_dir'])
        case('attempt left running after a report: status names it report-written-unrecorded', any('report-written-unrecorded' in l for l in listed))
        e = io.StringIO()
        with contextlib.redirect_stderr(e):
            held = deliver(got3['dispatch_file'])
        case('deliver on that attempt exits 5, names the record command, and sends nothing',
             held == 5 and 'UNRECORDED' in e.getvalue() and 'dispatch.py record' in e.getvalue() and len(msgs('codex')) == 2)
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            record(got3['dispatch_file'])
        case('recording it later delivers the verdict once', len(msgs('codex')) == 3)

        # A send that fails leaves a pending delivery, visible in status and in stderr; fixing the cause and rerunning delivers once.
        put(vr / '.sdlc' / 'n4' / 'handoff.md')
        rc, got4, _ = prep(vr, 'verifier', 'L1', '.sdlc/n4/handoff.md', '--notify', 'ghost', SDLC_DISPATCH_PARENT_PID=live_pid)
        Path(got4['result']).write_text(BODY['verifier'], encoding='utf-8')
        e = io.StringIO()
        with contextlib.redirect_stderr(e), contextlib.redirect_stdout(io.StringIO()):
            record(got4['dispatch_file'])
        case('an unregistered receiver: PENDING on stderr, the record itself still completes', 'verdict-delivery: PENDING' in e.getvalue() and attempt_of(got4)['status'] == 'completed')
        case('a pending delivery shows in status', any('verdict-delivery-pending to ghost' in l for l in status(got4['artifacts_dir'])))
        mcmd('register', '--name', 'ghost', '--harness', 'claude', '--reader', 'sess-2')
        with contextlib.redirect_stderr(io.StringIO()):
            fixed = deliver(got4['dispatch_file'])
            deliver(got4['dispatch_file'])
        case('after registering, deliver sends the pending verdict exactly once', fixed == 0 and len(msgs('ghost')) == 1 and not any('verdict-delivery' in l for l in status(got4['artifacts_dir'])))

        # A failed or invalid report still tells the receiver, with the word failed or invalid.
        rc, got5, _ = notified('n5', body=None)
        rc6, got6, _ = notified('n6', body='not a report\n')
        words = [re.search(r'^verdict: (\S+)', m.read_text(), re.M).group(1) for m in msgs('codex')[3:]]
        case('a failed sub-agent and an invalid report each deliver failed and invalid', rc == 1 and rc6 == 3 and sorted(words) == ['failed', 'invalid'])
        rcx, _, errx = prep(vr, 'verifier', 'L1', '.sdlc/n1/handoff.md', '--notify', 'Bad Name', SDLC_DISPATCH_PARENT_PID=live_pid)
        case('prepare refuses a malformed receiver name', rcx == 2 and '--notify' in errx)
    print('dispatch selftest: %s' % ('FAIL' if failures else 'PASS'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
