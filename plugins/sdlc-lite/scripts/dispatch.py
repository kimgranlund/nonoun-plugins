#!/usr/bin/env python3
"""The pre-launch half of run.sh for Claude sub-agent dispatch (Python 3.9+).

  dispatch.py prepare [--dry-run] [--approved "<who: why>"] <role> <level> <handoff.md>
  dispatch.py record [--no-result] [--agent-id ID] [--tokens N] [--tool-uses N] [--duration-ms N] <dispatch.json>
  dispatch.py advance [record flags] <dispatch.json>   record, then drop a pruned role from the queue (prints TaskStop task_id=<name>),
                                          then steps.py next on its step dir: prepare the next builder or verifier and print its
                                          dispatch JSON, or print `stop: <action> <reason>` (T-0645); a ticket-level completion (T-0688):
                                          an L2 or L3 solo prepares the ticket verifier and prints its JSON, an L1 solo or a verifier pass
                                          prints `next: close <task dir> (...)`, a verifier fail `stop: fail <result>; ...`, a ui-designer
                                          review `next: <verdict> <result>` or `stop: changes-required <result>`; any other role `next: <hint>`
  dispatch.py started --agent-id ID <dispatch.json>   store the spawned sub-agent's id in its running attempt, so status can show its last activity (T-0476)
  dispatch.py prune [--root DIR] [--done NAME | --add NAME | --forget-stale]   the queue of finished sub-agents to stop (T-0368); --done also closes the agent's host lane (T-0453)
  dispatch.py status <handoff dir>        each attempt: running, completed, failed, orphaned, or interrupted; a running one with a stored agent id and a
                                          transcript also shows `last activity <age>`, and `silent` after 30 minutes without a write (T-0476);
                                          a running one past its role's time budget ends `over-budget <age> (budget <n>m)` (T-0555)
  dispatch.py recover <handoff dir>       mark orphaned attempts interrupted (run_lifecycle.py's recovery text), then one `over-budget:` line per
                                          running attempt past its role's time budget, naming the check (a stdin wait, a stall) and the person
  dispatch.py recover --root DIR [--open] the same for every attempt under DIR/.sdlc, with each orphan's prepare command (T-0414);
                                          --open skips closed (done or dropped) ticket folders, so history is not rewritten (T-0438)
  dispatch.py resume [--root DIR] <name>  the ladder for an orphan: SendMessage by name, by id, then a new attempt
  dispatch.py resume --limit <name>       mark a running attempt that stopped on a spend or session limit `limit-stopped`, write
                                          <role>-<level>.limit with the resume call (SendMessage by name keeps its context) and the
                                          prepare command; refused for an attempt that is not running or has a result (T-0537).
                                          A limit-stopped attempt can still be recorded once the resumed agent reports.
  dispatch.py settle-held <verifier result> --by <owner> --evidence <repo-relative path> [--ref <ref>]...
                                          append `## Settled by owner` to a `deferred: <owner>` held fail, one line per held ref, so
                                          steps.py open, fanout.py land and tickets.py close read the refs as pass (T-0684); exit 2 and
                                          nothing written for any other result, another owner, a missing or absolute evidence path, or a
                                          review record whose Verdict is not pass or pass-with-notes
  dispatch.py selftest

prepare runs every gate and decision run.sh makes before it launches a role and prints a dispatch JSON the
conductor passes to the Agent tool (design: docs/sdlc-lite/subagent-mode.md sections 1 to 3). It launches
nothing and never edits run.sh. Order, as in run.sh: row lookup, preflight, family rules, mailbox notice,
goal precheck, unfilled-handoff gate, replan cap, link check, lane gate, spec gate, budget gate, time gate, lane guidance
check, then the one write section.
Records dir (T-0540): every record prepare and record write (result, attempt, dispatch record, .running, .limit,
base-sha, runs.jsonl) goes in order.records_dir of the handoff dir, <nearest .sdlc>/runtime/tasks/<task>/ (a legacy
task dir that already holds records keeps them in place); the brief's Artifacts dir line names it. The handoff gates
read the handoff dir, and skips.md stays in the task folder (order.task_dir). status and recover map a task or step
dir to its records dir.

  row lookup   role:level must be a pipeline row of adapters/claude/levels.json (solo is dispatched by
               T-0284); agents/<role>-<level>.md must exist and every skill its role file declares must exist.
  preflight    the handoff exists and the current directory is a git work tree with a commit.
  family       a verifier never runs on the newest build's model family (a Fable or Sonnet build moves it to
               Opus, an Opus build moves it to Sonnet, same effort); a plan-reviewer never on the newest
               planner's (an Opus planner moves it to Fable, a Fable planner to Opus, same effort; a Sonnet
               planner or none keeps the row, Fable high). Both read the first model=<[a-z]*> token of the newest result by order.py (a dir with no builder result reads its newest `role solo` runs.jsonl record: a Sonnet solo gets an Opus verifier, an Opus solo a Sonnet one); a
               verifier whose dir holds no builder result reads the highest-numbered live step-<n>/ that
               holds one (step-<n>.superseded-<k>/ is left out).
  row change   (T-0537) the row's model or effort differs from the last runs.jsonl line of the same role and
               level in the handoff dir: one stderr line `row changed: <role> <level> was <m>/<e>, now <m>/<e>`.
  goal         planner or plan-reviewer on a task handoff: steps.py precheck.        Refusal exit 2.
  unfilled     any role on a task handoff.md whose front matter type has a ticket template (T-0399): a line copied
               from that template (tickets.unfilled_line, the rule tickets.py check warns with), or the template's
               own Goal text under ## Goal, refuses with one line naming file:line. Exit 2. A handoff with no
               ticket front matter passes.
  replan       (T-0553) planner: when the records dir already holds two planner results (the first plan and the one
               replan), prepare refuses, exit 2, with two `dispatch.py: replan cap:` lines naming the count and
               --approved "<who: why>" (the person's call: split the ticket, approve one more replan, or drop scope).
               --approved, else SDLC_REPLAN_APPROVED, lets planner run <n+1> through and, once the attempt is written,
               appends `replan approved: planner run <n+1>: <who: why>` once to the task's skips.md; a dry run writes
               nothing. Each further planner run needs its own approval. Step handoffs are not planner results.
  links        builder or verifier on a step handoff: steps.py lint <step dir> (T-0379). Every cited .sdlc path
               must exist, and a report of the step's own prior attempt must name its step-<n>.superseded-<k>
               folder. Refusal exit 2.
  lane         planner, builder, plan-reviewer on a solo-lane ticket: steps.py lane --check, exit 5, unless
               SDLC_LANE_OVERRIDE="<reason>" (appended once to skips.md, carried as lane_override).
  specgate     plan-reviewer: specgate.py check, exit 2, unless SDLC_SPECGATE=off (carried as specgate).
  budget       budget.py report: warn or over with no ack, exit 4. No budget or no ticket proceeds.
  time         (T-0555) any role on a ticket whose `size:` has a time budget (TICKET_MINUTES: L1 60m, L2 120m, L3 420m,
               L4 840m, L5 1680m of agent time). Used time is each runs.jsonl row's duration_ms, else its closed attempt
               record's started_at to finished_at, over the ticket's records dir and folder, once per attempt_id. At or past
               the ceiling prepare refuses, exit 2, with two `dispatch.py: time budget:` lines (check the last role for a stdin
               wait or a stall, ask the person; a headless lane stops the ticket as blocked). --approved "<who: why>", else
               SDLC_TIME_APPROVED, lets the role through and appends `time budget approved: <used>m of <ceiling>m: <who: why>`
               to the ticket folder's skips.md; each such line raises the ceiling to <used> plus one budget. A dry run writes
               nothing. No ticket or no size proceeds.
  guidance     (T-0655) any role whose execution tree is a linked (lane) worktree: each backticked repo-relative path in the
               handoff that ends in SKILL.md, AGENTS.md or CLAUDE.md or starts with .agents/ or .claude/skills/ must exist in
               that tree but held by the main checkout or the lane's .lane.json `into` branch, else exit 5 with one `guidance
               missing in lane: <path> (present on <branch> at <sha7>)` line each; a path held nowhere does not refuse
               (T-0674); no record is written. An
               AGENTS.md or CLAUDE.md that differs from the main checkout's prints `lane guidance differs: <file>` on stderr
               and adds a Guidance line to the brief. The main checkout is never checked.
  lock         replaces run_lifecycle.py's directory lock. Under a brief file lock, every running attempt
               record in the records dir whose parent pid is dead is marked interrupted and recovered; one
               whose parent is alive refuses, exit 2. A second prepare therefore cannot start while a
               dispatched role is unrecorded. A refusal writes no new file (a dead-parent recovery
               before the refusal still marks that old record interrupted).

Names. The result stem is <role>-<level>, or <role>-<level>-<k> for the lowest free k >= 2, where a stem is
taken when any file <stem>.* sits in the records dir (run_lifecycle.py's rule, a superset of run.sh's
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
runs.jsonl line (lane_override, specgate, handoff_sha256, routing_reason). Both records carry plugin_version, the
running plugin manifest version (plugin_min.running, T-0678), which record compares. A builder or verifier also writes
base-sha as run.sh does. prepare also writes the running marker <role>-<level>.running (the epoch start in whole
seconds, as run.sh writes it) beside the handoff, so warn-handoff-edit.sh freezes the handoff while the attempt
runs; record clears it when it closes the attempt completed or failed (a no-result record leaves it), and recover
clears it when it marks the attempt interrupted (T-0505). --dry-run prints the JSON and writes nothing (no marker
either), takes no lock, and skips recovery.

Brief. The run.sh prompt (Handoff, Artifacts dir), then a Report file line and a one-line pointer line (T-0646), then a Tree line, a
throwaway-worktree prefix line (<worktree root>/tmp/<Agent name>, wtroot.py root), a scratch line
($TMPDIR/sdlc-lite/<repo key>/<Agent name>), the search scope line (SEARCH_SCOPE, T-0702), and for builder and verifier a Base sha line,
since a sub-agent cannot read SDLC_BASE_SHA from its environment. A verifier for a ticket with a ready ref
(refs/sdlc/ready/<id>, lanes.py ready, T-0590) also gets `Review sha: <its sha>`, stored as review_sha, and takes Base sha
from the `Lane-Base:` line of that snapshot commit when it is an ancestor; prepare says so on stderr when the tree has
moved since the pin (stale). A verifier whose records dir holds end-sha (written by record for a completed builder: the
tree's HEAD when clean, else a tree hash built with a temporary index, T-0661) also gets `Diff range: <base>..<end>`
(`git diff <base> <tree>` for a tree hash; base..Review sha when it has one), stored as diff_range. Every brief carries a Report file line (a verifier's since T-0330, every role's since T-0646):
the result path the role writes with the Write tool before it ends; record fails the run with a message naming that path when it is missing,
also when stdin is only the pointer. The line also says the file carries no header (record adds it, T-0538) and names
`results.py validate <file> --role <role> --headerless`. The pointer line asks for a final message of one line, `<role> <status> <path>`.
The prefix line says rm of scratch output under that prefix is allowed and refused elsewhere (hooks/block-role-rm.sh).
A builder whose step scope names a path an AGENTS.md routes to a repo skill (steps.routed_skills against Tree, T-0648) also
gets `Repo skills for this step: <path>, ...` (repo_skills_line; solo_run.py adds the same line to a solo brief); a repo with
no routing lines gets no such line.
A role whose Tree is a lane worktree whose AGENTS.md or CLAUDE.md differs from the main checkout's gets one line per file,
`Guidance: read <Tree>/<file>; it overrides the auto-attached main checkout copy` (T-0655), since the host auto-attaches
the main checkout copy.
The last line is the role's wall-clock budget (T-0555), `Time budget: <n>m wall clock for <role> <level>`, from ROLE_MINUTES
(3x the median recorded duration of that role and level, floor 10 minutes; 60 for a row with no record); prepare stores it
as time_budget_min in the dispatch and the attempt, and status and recover flag a running attempt past it. Nothing is killed.

Exit codes as run.sh: 0 ok, 2 usage, preflight, goal, replan cap, time budget, spec gate, or a running attempt, 4 budget, 5 lane.

record is the post-launch half (T-0278, design section 3). It takes <stem>.dispatch.json and the sub-agent's
result: the file the role wrote at the dispatch's result path, else stdin when that file is missing or empty,
else (with --transcript) the transcript's last assistant message; a max_tokens stop is refused as truncated (T-0343)
(stdin with a "## " heading line is a result, any other stdin is the sub-agent's error text, except a one-line placeholder under 40
characters with no error word, which yields to a complete transcript result, T-0685). In run.sh's order
it then does the following.
  header       writes <!-- role= level= model= effort= --> from the dispatch over any header the role wrote, then
               the body, to the result path.
  cleanup      removes the worktrees and directory under the dispatch's tmp prefix (only a path under
               the tmp root, <worktree root>/tmp/, or a legacy one: <main checkout>/.claude/worktrees/tmp/,
               <main checkout>/.worktrees/tmp/ or <tree>/.worktrees/tmp/), removes the
               scratch dir, runs the wtroot.py crash sweep (a dead owner past the limit goes, an unmarked folder is
               reported), then reports strays: worktrees and local branches that appeared since
               prepare (its snapshot sits in the attempt record) under a tmp root or on a branch named with the
               role's agent name, the own prefix left out; peers' worktrees and branches, and the
               host-owned trees (~/.codex/worktrees/*, Claude Code's .claude/worktrees/agent-*), are not reported. Report only.
  stale        a handoff sha256 that differs from the one prepare stored prints "stale input: <handoff> changed
               while <role> ran" and sets stale_input. The exit code is unchanged by cleanup, strays, and stale.
  result_sha256 (T-0388) the sha256 of the result file as accepted, after the header write, stored in the attempt
               record and the runs.jsonl line; a later edit no longer matches it. Old records lack the field.
  runs.jsonl   one line with the key set run.sh writes, plus agent_id and cost_reason, with transport subagent;
               loaded_context is {"status":"log absent"} (a sub-agent leaves no stream-json log).
               cost_usd is estimated from the notice tokens by cost_estimate.py (cost_estimated true, cost_basis
               "tokens x blended"); with no tokens it is null with cost_reason "subagent usage not priced", never zero, the row holds unpriced true and stderr
               says `unpriced: <name> has no cost row; pass --transcript <jsonl>` (T-0402);
               usage holds the notice's subagent_tokens and tool_uses when --tokens or --tool-uses is given; --transcript <jsonl>
               replaces the token count with the transcript's summed usage fields, priced per field (T-0328); with --agent-id and no
               --transcript, the one file <projects>/*/*/subagents/agent-<id>.jsonl is used (T-0446; none or several: unpriced as above).
  validate     results.py validate --role <role>. A defect prints "dispatch.py: <role> result <reason>; see
               <file>", exit 3, and keeps the file and the line; the attempt is failed with exit_code 3. A legacy
               result (T-0678) is the exception: when the attempt's plugin_version is missing or differs from the running
               version and the result has a "## " heading, the defect is a schema change between prepare and record, so
               record prints "legacy-format: <role> result <reason>; prepared under <version or an older plugin>,
               recorded as completed", stores legacy_format: <reason> in the attempt and the runs.jsonl line, and exits 0.
  no result yet  no result file, empty stdin, and no transcript result: record prints `no result yet at <path>; the
               attempt stays running` to stderr and exits 2, writing no log, runs.jsonl line, limit marker, or delivery
               and not closing the attempt; record again once the role writes the file, or pass --no-result (T-0412).
  failed       no result file and no result on stdin: the stdin text is saved as <stem>.log, the attempt is failed
               with exit_code 1 and the text, and no runs.jsonl line is written, as run.sh. --no-result closes an
               attempt with nothing at all this way, with the error `no result file at <path>`. A 429 or session-limit
               text writes <role>-<level>.limit with the prepare command to resume; a later success removes it.
  success      the attempt is completed, the result path is printed, exit 0.
Prune (T-0368). The host keeps a finished sub-agent as an idle, addressable teammate until it is stopped. prepare writes
"prune": true into the dispatch for a one-shot role (scout, researcher, architect, archaeologist, planner, plan-reviewer,
verifier, filer, ui-designer) and false for builder, whose failed run may be resumed (solo and the messenger are false too); --prune and
--no-prune override it. record on exit 0 with prune true prints `prune: <agent name>` and appends {name, agent_id, role,
level, recorded_at, session} to <project>/.sdlc/runtime/prune.json, unless another attempt of that agent is still open or the
result's ## Follow-ups section is not None (a filer is queued either way: its follow-ups are its output, which tickets.py
close consumes, T-0531). `dispatch.py prune` lists the queue with the stop call per entry
(`TaskStop task_id=<name>`); `--done NAME` removes an entry once stopped; `--add NAME` queues a landed builder or solo
(`fanout.py land` does it for a merged solo, under the `name` of its newest solo dispatch record, else `<id>-solo`). The queue
lives in the main checkout, also when the call runs in a linked worktree, and session is CLAUDE_CODE_SESSION_ID (a
sub-agent shares its parent's). In a Claude session the listing shows only that session's entries and ends with
`prune: <n> from other sessions not listed; drop them: dispatch.py prune --forget-stale` when others exist;
`--forget-stale` removes those and prints `forgot: <name>` per entry (T-0601). The listing adds `; lane open <path>` to an entry whose host lane (lanes.py) still
exists, and `--done NAME` then closes that lane through lanes.close_lane and prints `closed lane <path> (<reason>)` or
`lane still open: <path> (<reason>)` (T-0453); without a lane it prints nothing more.
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
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
sys.path.insert(0, str(HERE))
import budget  # noqa: E402
import claude_roles  # noqa: E402
import cost_estimate  # noqa: E402
import order  # noqa: E402
import plugin_min  # noqa: E402
import results  # noqa: E402
import tickets  # noqa: E402
import run_lifecycle  # noqa: E402
import wtroot  # noqa: E402

SHELLS = ('sh', 'bash', 'zsh', 'dash', 'fish', 'ksh', 'env', 'sudo', 'timeout', 'tmux', 'login')
NAME_MAX = 64
GATES = ('preflight', 'plugin_min', 'goal', 'replan', 'links', 'lane', 'specgate', 'budget', 'time', 'lock')
APPROVAL_RE = re.compile(r'[^:]*[^\s:][^:]*:\s*\S')  # "<who: why>", the rule steps.py lint --approved checks
NAME_RE = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
ID_RE = re.compile(r'[0-9]{8}T[0-9]{12}Z-[a-z0-9]+(-[a-z0-9]+)*')
PRUNE_ROLES = ('scout', 'researcher', 'architect', 'archaeologist', 'planner', 'plan-reviewer', 'verifier', 'filer', 'ui-designer')


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
    """Newest builder result of the highest-numbered live step-<n>/ under directory's records dir that holds one."""
    best, built = -1, None
    for sd in order.records_dir(directory).glob('step-*'):
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
        # a solo ticket has no builder result: its newest runs.jsonl solo record holds the family (T-0284);
        # a sub-agent lane worktree holds none, so fanout.py prep passes --solo-model (T-0356)
        other = model_of(built) if built else (solo_model(directory) or solo)
        if model == other and model in ('fable', 'sonnet'):
            return 'opus'
        if model == other and model == 'opus':
            return 'sonnet'  # T-0519: an Opus build gets a Sonnet verifier, same effort
    elif role == 'plan-reviewer':
        planned = order.newest(str(directory), 'planner')
        if planned and model == model_of(planned) and model == 'opus':
            return 'fable'
        if planned and model == model_of(planned) and model == 'fable':
            return 'opus'  # T-0519: the row is Fable high, so a Fable planner moves the review to Opus
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
    d = order.task_dir(d) or d  # a records dir under runtime/tasks names its task folder
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


def handoff_locator(path):
    """The value of a prompt's `Handoff:` line (T-0504). A path with whitespace is double-quoted so the spawn gate
    (hooks/block-role-spawn.sh) reads it whole; a plain path stays bare, and the gate then reads its first token."""
    path = str(path)
    return '"%s"' % path if re.search(r'\s', path) and '"' not in path else path


def ports_line(tree):
    """The brief's `Ports:` line, with a trailing newline, when tree is a lane that holds a port (lanes.port_of, T-0693); else ''."""
    try:
        import lanes  # local like host_lanes: lanes imports nothing from here
        port = lanes.port_of(tree)[0]
    except Exception:  # not a lane, or lanes unreadable: the brief stays as it was
        return ''
    return ('Ports: SDLC_LANE_PORT=%d (this lane\'s own port; start any server on it or on a port derived from it, never a fixed one)\n' % port
            if port else '')


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


def repo_skills_line(top, handoff):
    """T-0648: 'Repo skills for this step: <path>, ...' for the skills an AGENTS.md under top routes the handoff's file
    scope to (steps.routed_skills), else ''. The scope is a step handoff's scope_entries, else the existing repo-relative
    paths in code spans under a ticket handoff's ## Intent and ## Context."""
    import steps  # same scripts/ dir
    handoff = Path(handoff)
    paths = steps.scope_entries(handoff.read_text(encoding='utf-8'))
    if paths is None:
        paths = []
        for heading in ('Intent', 'Context'):
            for line in steps.section(handoff, heading) or []:
                for m in steps.SPAN_RE.finditer(line):
                    p = steps.trim_path_token(m.group(2).strip())
                    if p and not os.path.isabs(p) and '..' not in Path(p).parts and (Path(top) / p).exists():
                        paths.append(p)
    skills = steps.routed_skills(top, paths) if paths else []
    return 'Repo skills for this step: ' + ', '.join(skills) if skills else ''


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


def lane_start(tree, floor=''):
    """The commit a lane worktree started from: base_sha of its fanout record (.lane.json at its top), else the fork floor."""
    top = git('rev-parse', '--show-toplevel', cwd=tree).stdout.strip()
    try:
        rec = json.loads((Path(top) / '.lane.json').read_text(encoding='utf-8')) if top else {}
    except (OSError, ValueError):
        rec = {}
    sha = str(rec.get('base_sha') or '').strip() if isinstance(rec, dict) else ''
    return sha or floor


def build_base(directory, records=None, tree=None, role=None):
    """The build-start commit run.sh stores in base-sha (T-0381), in this order: (1) a base the handoff names (a line
    `base: <sha>`), else (2) the sha recorded at the step's first dispatch, kept valid, else (3) HEAD of the execution
    tree, never the main checkout's HEAD. A supplied SDLC_BASE_SHA that resolves to another commit is refused and the
    pick kept; a named base that is not an ancestor of HEAD raises Refuse. Git runs in the execution tree (tree when
    given, as prepare --tree settles it, else the handoff's own tree, or the lane worktree a main-checkout handoff is
    run from), and in a lane worktree a recorded sha older than the lane's fork point is stale (T-0376). Returns
    (stored, base). base-sha and the dispatch records are read in records (the records dir, default directory's). A verifier
    with nothing named or recorded in a lane gets the lane start (lane_start), not the lane HEAD, which after a resumed
    driver is its own WIP commit (T-0546). A solo dispatch's base_sha counts only in the tree it was recorded in (its
    tree, else the handoff's checkout): one recorded in the main checkout is not a lane tree's base (T-0578)."""
    records = Path(records) if records is not None else order.records_dir(directory)
    cwd = tree if tree else exec_tree(directory)
    stored = ''
    f = records / 'base-sha'
    if f.is_file():
        lines = f.read_text(encoding='utf-8', errors='replace').splitlines()
        stored = re.sub(r'\s', '', lines[0]) if lines else ''
    if not stored:  # a solo lane has no run.sh: its dispatch file recorded the pre-build HEAD (T-0366)
        here = os.path.realpath(git('rev-parse', '--show-toplevel', cwd=cwd).stdout.strip() or cwd)
        for df in sorted(records.glob('*.dispatch.json')):  # <ticket>-solo-<level> now, solo-<level>-<slug> before T-0363
            try:
                rec = json.loads(df.read_text(encoding='utf-8'))
                stored = str(rec.get('base_sha') or '').strip() if rec.get('role') == 'solo' else ''
                where = rec.get('tree') or git('rev-parse', '--show-toplevel', cwd=directory).stdout.strip() if stored else ''
            except (OSError, ValueError, AttributeError):
                stored = ''
            if stored and where and os.path.realpath(where) != here:
                say('solo base %s was recorded in %s, not this tree %s: not used as its base' % (stored[:12], where, here))
                stored = ''
            if stored:
                break
    floor = fork_floor(cwd)

    def commit(sha):
        return git('rev-parse', '-q', '--verify', sha + '^{commit}', cwd=cwd).stdout.strip() if sha else ''

    def ancestor(sha):
        return bool(commit(sha)) and git('merge-base', '--is-ancestor', sha, 'HEAD', cwd=cwd).returncode == 0

    base, why = '', ''
    hf = Path(directory) / 'handoff.md'
    m = NAMED_BASE_RE.search(hf.read_text(encoding='utf-8', errors='replace')) if hf.is_file() else None
    if not m:  # a step handoff in the records dir names none: the task handoff may
        task = order.task_dir(records)
        tf = task / 'handoff.md' if task is not None else None
        if tf is not None and tf.is_file() and tf.resolve() != hf.resolve():
            m = NAMED_BASE_RE.search(tf.read_text(encoding='utf-8', errors='replace'))
            hf = tf if m else hf
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
        start = lane_start(cwd, floor) if role == 'verifier' and not stored else ''
        if start and start != base and ancestor(start):  # a lane resumed after its driver died: HEAD is its WIP commit (T-0546)
            say('nothing recorded for this step: Base sha is the lane start %s, not its HEAD %s; name another with a line \'base: <sha>\''
                % (start[:12], base[:12]))
            base, why = commit(start), 'the lane start (nothing named or recorded)'
    supplied = re.sub(r'\s', '', os.environ.get('SDLC_BASE_SHA', ''))
    if supplied and commit(supplied) != base:
        say("SDLC_BASE_SHA refused: %s (supplied) differs from the step base %s (%s); name it in the handoff with a line 'base: <sha>' to use it"
            % (supplied, base[:12], why))
    return stored, base


READY_REFS = 'refs/sdlc/ready/'  # lanes.py READY_REFS
# T-0702: every role brief bounds its file searches; hooks/block-disk-scan.sh enforces it on Claude only
SEARCH_SCOPE = ('Search only inside Tree (the checkout you run in when the brief has no Tree line) and the Artifacts dir; never '
                'search /, a home folder, or the whole disk (find /, bfs /, mdfind without -onlyin), which can run for hours.')
LANE_BASE_RE = re.compile(r'^Lane-Base: ([0-9a-f]{40})$', re.M)


def ready_review(directory, tree, base):
    """(review sha, base) for a verifier (T-0590): when refs/sdlc/ready/<ticket> exists for the ticket that owns
    directory, review its sha, and take the base from the `Lane-Base:` line of its snapshot commit (lanes.py pin) when
    that is an ancestor of the sha, else keep base; says so when tree no longer holds the pinned state. ('', base)
    with no ready ref."""
    tid = ticket_label(directory)[0]
    sha = git('rev-parse', '-q', '--verify', READY_REFS + tid + '^{commit}', cwd=tree).stdout.strip() if tid else ''
    if not sha:
        return '', base
    m = LANE_BASE_RE.search(git('log', '-1', '--format=%B', sha, cwd=tree).stdout)
    if m and git('merge-base', '--is-ancestor', m.group(1), sha, cwd=tree).returncode == 0:
        base = m.group(1)
    import lanes  # local like host_lanes: lanes imports nothing from here
    try:
        stale = lanes.snapshot(tree) != lanes.ready_state(tree, sha)
    except lanes.LaneError:
        stale = True
    if stale:
        say('%s%s is stale: %s has moved since lanes.py ready pinned %s; the verifier reviews the pinned sha'
            % (READY_REFS, tid, tree, sha[:12]))
    return sha, base


def build_end(tree):
    """Where a build ended (T-0661): HEAD of tree when it is clean, else the hash of its working tree, built with a
    temporary index (GIT_INDEX_FILE), never git stash or the shared index. '' when git cannot say."""
    st = git('status', '--porcelain', cwd=tree)
    head = git('rev-parse', '-q', '--verify', 'HEAD^{commit}', cwd=tree).stdout.strip()
    if st.returncode != 0 or not head:
        return ''
    if not st.stdout.strip():
        return head
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, 'index'))
        for args in (['read-tree', 'HEAD'], ['add', '-A']):
            if subprocess.run(['git'] + args, cwd=tree, env=env, capture_output=True).returncode != 0:
                return ''
        p = subprocess.run(['git', 'write-tree'], cwd=tree, env=env, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ''


def step_end(records, tree):
    """(end, kind) from the end-sha a recorded builder left in records: kind is commit or tree; ('', '') when absent
    or when tree no longer holds the object."""
    f = Path(records) / 'end-sha'
    lines = f.read_text(encoding='utf-8', errors='replace').split() if f.is_file() else []
    end = lines[0] if lines else ''
    kind = git('cat-file', '-t', end, cwd=tree).stdout.strip() if re.fullmatch(r'[0-9a-f]{7,64}', end) else ''
    return (end, kind) if kind in ('commit', 'tree') else ('', '')


def lane_gate(role, directory, plugin):
    """None to proceed, else the (lane_dir, level) of a solo-lane ticket that needs the solo agent: its size as a
    level (tickets.parse reads a deprecated alias size as its level), L2 when unreadable."""
    lane_dir = order.task_dir(directory)
    handoff = lane_dir / 'handoff.md' if lane_dir is not None else None
    if handoff is None or not handoff.is_file() or not re.search(r'^id: *T-[0-9]+', handoff.read_text(encoding='utf-8', errors='replace'), re.M):
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


GUIDANCE_FILES = ('AGENTS.md', 'CLAUDE.md')


def lane_guidance(top, handoff):
    """T-0655: for a linked (lane) worktree top, (differing, missing): the GUIDANCE_FILES whose bytes differ from the main
    checkout's copy, and one refusal line per backticked repo-relative guidance path in the handoff (a SKILL.md, AGENTS.md
    or CLAUDE.md, or a path under .agents/ or .claude/skills/) absent from top but held by the main checkout or the lane's
    `into` branch (.lane.json), naming that branch; a path held nowhere is skipped. ([], []) in the main checkout."""
    gd = git('rev-parse', '--git-dir', cwd=top).stdout.strip()
    common = git('rev-parse', '--git-common-dir', cwd=top).stdout.strip()
    if not gd or not common:
        return [], []
    common = os.path.realpath(os.path.join(top, common))
    if os.path.realpath(os.path.join(top, gd)) == common:
        return [], []
    main_top = Path(os.path.dirname(common))
    top = Path(top)

    def read(p):
        try:
            return p.read_bytes()
        except OSError:
            return None
    differing = [f for f in GUIDANCE_FILES if read(top / f) != read(main_top / f)]
    import steps  # same scripts/ dir
    paths = []
    for m in steps.SPAN_RE.finditer(Path(handoff).read_text(encoding='utf-8', errors='replace')):
        p = re.sub(r'^(?:\./)+|:\d+$', '', m.group(2).strip())  # not steps.trim_path_token: it strips the leading dot
        if (p and not os.path.isabs(p) and '..' not in Path(p).parts and not re.search(r'[\s*<>?$]', p) and p not in paths
                and (p.rsplit('/', 1)[-1] in ('SKILL.md',) + GUIDANCE_FILES or p.startswith(('.agents/', '.claude/skills/')))):
            paths.append(p)
    try:
        into = json.loads((top / '.lane.json').read_text(encoding='utf-8')).get('into') or ''
    except (OSError, ValueError, AttributeError):
        into = ''
    missing = []
    for p in paths:
        if (top / p).exists():
            continue
        where = ''
        if (main_top / p).exists():
            branch = git('rev-parse', '--abbrev-ref', 'HEAD', cwd=main_top).stdout.strip()
            where = (branch, git('rev-parse', '--short=7', 'HEAD', cwd=main_top).stdout.strip())
        elif into and git('cat-file', '-e', '%s:%s' % (into, p), cwd=top).returncode == 0:
            where = (into, git('rev-parse', '--short=7', into, cwd=top).stdout.strip())
        if where:  # T-0674: a path held nowhere is not lane drift (a plugin-relative spelling), so it does not refuse
            missing.append('guidance missing in lane: %s (present on %s at %s)' % ((p,) + where))
    return differing, missing


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


def proc_start_epoch(pid):
    """Start time of pid in epoch seconds from `ps -o lstart=` (as fleet_status.py reads it), or None when it cannot be read."""
    try:
        out = subprocess.run(['env', 'LC_ALL=C', 'ps', '-o', 'lstart=', '-p', str(pid)], capture_output=True, text=True, timeout=5).stdout
        return time.mktime(time.strptime(' '.join(out.split()), '%a %b %d %H:%M:%S %Y'))
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def pid_reused(pid, started_at):
    """True when pid started after started_at (an ISO time): the host gave a dead parent's pid to a newer process.
    A start time that cannot be read on either side keeps today's answer (False)."""
    try:
        began = datetime.fromisoformat(started_at).timestamp()
    except (TypeError, ValueError):
        return False
    seen = proc_start_epoch(pid)
    return seen is not None and seen > began


def attempt_state(data):
    """running, completed, failed, or orphaned (running, claude backend, parent pid dead or reused); else the recorded status."""
    status = data.get('status')
    if status != 'running':
        return status or 'unknown'
    pid = data.get('parent_pid') or data.get('owner_pid')
    if data.get('backend', 'claude') == 'claude' and isinstance(pid, int) and (not pid_alive(pid) or pid_reused(pid, data.get('started_at'))):
        return 'orphaned'
    return 'running'


def recover_orphans(directory, dry_run=False, own=None):
    """Mark orphaned attempts interrupted with run_lifecycle.py's recovery text; return (recovered, live) names.
    A running attempt whose recorded pid is own (the calling session) is neither recovered nor live (T-0371)."""
    live, recovered = [], []
    for path in sorted(Path(directory).glob('*.attempt.json')):
        data = read_attempt(path)
        state = attempt_state(data)
        if state == 'orphaned' and results.attempt_reported(path, data.get('role')):
            continue  # T-0445: its result file holds a verdict; never mark it interrupted (status shows report-unrecorded)
        if state == 'orphaned':
            if not dry_run:
                data.update(status='interrupted', finished_at=run_lifecycle.now(), recovery=RECOVERY)
                run_lifecycle.write(path, data)
                (Path(directory) / ('%s-%s.running' % (data.get('role'), data.get('level')))).unlink(missing_ok=True)
            recovered.append(path.name)
        elif state == 'running' and (data.get('parent_pid') or data.get('owner_pid')) != own:
            live.append('%s (pid %s)' % (path.name, data.get('parent_pid') or data.get('owner_pid')))
    return recovered, live


SWEEP_SKIP = ('.git', '.worktrees', 'node_modules')


def ticket_closed(folder):
    """True when folder holds a handoff.md whose status is done or dropped (a closed ticket: its attempt files are history)."""
    try:
        meta = tickets.parse((Path(folder) / 'handoff.md').read_text(encoding='utf-8')) or {}
    except OSError:
        return False
    return meta.get('status') in ('done', 'dropped')


def attempt_dirs(root, open_only=False):
    """Every folder under root/.sdlc that holds a *.attempt.json, sorted; .git, .worktrees and node_modules are not entered.
    With open_only, a ticket folder whose status is done or dropped is not entered either (T-0438)."""
    found = []
    for here, dirs, files in os.walk(str(Path(root) / '.sdlc')):
        dirs[:] = sorted(d for d in dirs if d not in SWEEP_SKIP)
        if open_only and 'handoff.md' in files and ticket_closed(here):
            dirs[:] = []
            continue
        if open_only and 'handoff.md' not in files:  # a records dir under runtime/tasks: its task folder decides
            task = order.task_dir(here)
            if task is not None and Path(task).resolve() != Path(here).resolve() and ticket_closed(task):
                dirs[:] = []
                continue
        if any(f.endswith('.attempt.json') for f in files):
            found.append(here)
    return found


def recover_root(root, open_only=False):
    """Restart sweep (T-0414): mark every orphaned attempt under root/.sdlc interrupted. One 'recovered:' line and its
    'resume:' prepare command per orphan, one 'running:' line per live attempt, else 'no orphaned attempts'.
    With open_only, closed (done or dropped) ticket folders are left untouched: no rewrite of history (T-0438)."""
    lines, me = [], Path(__file__).resolve()
    for directory in attempt_dirs(root, open_only):
        before = {p.name: read_attempt(p) for p in Path(directory).glob('*.attempt.json')}
        recovered, live = recover_orphans(directory)
        for name in recovered:
            data = before[name]
            lines += ['recovered: %s' % (Path(directory) / name),
                      '  resume: python3 %s prepare %s %s %s' % (me, data.get('role'), data.get('level'), data.get('handoff'))]
        lines += ['running: %s' % (Path(directory) / entry) for entry in live]
        lines += over_budget_lines(directory)
    return lines or ['no orphaned attempts']


def running_attempt(root, name):
    """The path of an attempt record under root/.sdlc for agent name that attempt_state reads as running, else None."""
    for directory in attempt_dirs(root):
        for path in sorted(Path(directory).glob('*.attempt.json')):
            data = read_attempt(path)
            if name in (data.get('agent_name'), data.get('name')) and attempt_state(data) == 'running':
                return path
    return None


def handoff_records(directory):
    """The records dir for a status or recover argument that holds handoff.md or is a step-<n> dir; any other dir as given,
    so a dir with no .sdlc ancestor never maps outside the project."""
    d = Path(directory)
    if (d / 'handoff.md').is_file() or re.fullmatch(r'step-\d+(\.superseded-\d+)?', d.name):
        return str(order.records_dir(d))
    return directory


def settle(directory, dry_run):
    """Refuse while a dispatched attempt in directory is alive; mark dead-parent ones interrupted."""
    recovered, live = recover_orphans(directory, dry_run, own=parent_pid()[0])
    if live:
        raise Refuse(2, 'dispatch.py: an attempt is still running in %s: %s; record it, or wait for it, before dispatching another role. If its spawn was denied or never started, recover it: python3 %s %s' % (directory, ', '.join(live), Path(run_lifecycle.__file__).resolve().with_name('run_lifecycle.py'), 'recover "%s"' % directory))
    return recovered


SILENT_SECONDS = 30 * 60


def age_text(seconds):
    """Whole seconds as 45s, 12m, 2h, or 3d (the largest unit that fits)."""
    seconds = max(0, int(seconds))
    for unit, size in (('d', 86400), ('h', 3600), ('m', 60)):
        if seconds >= size:
            return '%d%s' % (seconds // size, unit)
    return '%ds' % seconds


# T-0555 wall-clock budgets, in minutes. A role row is 3x the median recorded duration_ms of that role and level in this
# repo's runs.jsonl records (2026-10-14, 128 timed runs), rounded up to 5 minutes, floor 10; a row with no record gets
# ROLE_MINUTES_DEFAULT. A ticket's budget is its total agent time by size (L2 median 0.4 h, L3 median 2.3 h on that date).
ROLE_MINUTES = {('architect', 'L1'): 40, ('builder', 'L1'): 10, ('builder', 'L2'): 15, ('builder', 'L3'): 45, ('builder', 'L4'): 240,
                ('filer', 'L1'): 10, ('plan-reviewer', 'L1'): 45, ('planner', 'L2'): 50, ('planner', 'L3'): 55, ('solo', 'L2'): 140,
                ('verifier', 'L1'): 10, ('verifier', 'L2'): 25, ('verifier', 'L3'): 50}
ROLE_MINUTES_DEFAULT = 60
TICKET_MINUTES = {'L1': 60, 'L2': 120, 'L3': 420, 'L4': 840, 'L5': 1680}
TIME_APPROVED_RE = re.compile(r'time budget approved: (\d+)m of \d+m: ')


def role_minutes(role, level):
    return ROLE_MINUTES.get((role, level), ROLE_MINUTES_DEFAULT)


def iso_epoch(text):
    """Epoch seconds of an ISO time (a trailing Z allowed), else None."""
    try:
        return datetime.fromisoformat(str(text).replace('Z', '+00:00')).timestamp()
    except (TypeError, ValueError):
        return None


def over_budget(data):
    """(elapsed seconds, budget minutes) of a running attempt past its role's wall-clock budget (the attempt's
    time_budget_min, else role_minutes), else None."""
    began = iso_epoch(data.get('started_at'))
    if began is None:
        return None
    budget = data.get('time_budget_min')
    budget = budget if isinstance(budget, int) and budget > 0 else role_minutes(data.get('role'), data.get('level'))
    elapsed = time.time() - began
    return (elapsed, budget) if elapsed >= budget * 60 else None


def over_budget_lines(directory):
    """One `over-budget:` line per running attempt in directory past its role's budget, with the check to make."""
    lines = []
    for path in sorted(Path(directory).glob('*.attempt.json')):
        data = read_attempt(path)
        hit = over_budget(data) if attempt_state(data) == 'running' else None
        if hit:
            lines.append('over-budget: %s running %s, budget %dm: check the role for a stdin wait or a stall, then ask the person (%s)'
                         % (path.name[:-len('.attempt.json')], age_text(hit[0]), hit[1], path))
    return lines


def ticket_minutes(ticket):
    """Agent minutes a ticket folder has used: each runs.jsonl row's duration_ms, else its closed (completed or failed)
    attempt record's started_at to finished_at, over the records dir and the ticket folder, once per attempt_id."""
    roots = {order.records_dir(ticket).resolve(), Path(ticket).resolve()}
    seen, total = set(), 0.0
    for f in sorted({f.resolve() for r in roots if r.is_dir() for f in r.rglob('runs.jsonl')}):
        for line in f.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            ms = rec.get('duration_ms') if isinstance(rec, dict) else None
            aid = rec.get('attempt_id') if isinstance(rec, dict) else None
            if not isinstance(ms, (int, float)) or isinstance(ms, bool) or ms <= 0 or aid in seen:
                continue
            total += ms / 60000
            if aid:
                seen.add(aid)
    for f in sorted({f.resolve() for r in roots if r.is_dir() for f in r.rglob('*.attempt.json')}):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict) or data.get('status') not in ('completed', 'failed') or data.get('attempt_id') in seen:
            continue
        began, ended = iso_epoch(data.get('started_at')), iso_epoch(data.get('finished_at'))
        if began is not None and ended is not None and ended > began:
            total += (ended - began) / 60
            if data.get('attempt_id'):
                seen.add(data['attempt_id'])
    return total


def ticket_time(ticket):
    """(used minutes, ceiling minutes, budget minutes, size) for a ticket folder with a size budget, else None. Each
    `time budget approved: <n>m of ...` line in its skips.md raises the ceiling to n plus one budget."""
    meta = budget.front(Path(ticket) / 'handoff.md') or {}
    size = tickets.size_level(meta.get('size', ''))
    if size not in TICKET_MINUTES:
        return None
    try:
        approved = [int(m.group(1)) for m in TIME_APPROVED_RE.finditer((Path(ticket) / 'skips.md').read_text(encoding='utf-8'))]
    except OSError:
        approved = []
    return ticket_minutes(ticket), max(approved, default=0) + TICKET_MINUTES[size], TICKET_MINUTES[size], size


def status(directory, orphans_only=False):
    """One line per attempt: stem, state, role-level, parent pid; orphans_only keeps the orphaned ones.
    Attempts in the dir's `step-*/` folders are listed too, stem prefixed `step-<n>/`; a dir with none prints `no attempts in <dir>` and its records dir when that differs (T-0690).
    `report-unrecorded` (one token, T-0705) is added when a report file exists and the attempt is running or orphaned (T-0383), or is any state but completed or failed with the report newer than its attempt record (T-0703).
    A running attempt with a stored agent id and one sub-agent transcript adds `last activity <age>` (the transcript's mtime) and `silent` at 30 minutes or more (T-0476)."""
    lines = []
    base = Path(directory)
    found = sorted(base.glob('*.attempt.json')) + sorted(base.glob('step-*/*.attempt.json'))  # T-0690: a task's step attempts too
    for path in found:
        data = read_attempt(path)
        state = attempt_state(data)
        if orphans_only and state != 'orphaned':
            continue
        sub = path.parent.name + '/' if path.parent != base else ''
        stem = sub + path.name[:-len('.attempt.json')]
        line = '%s %s %s-%s parent_pid=%s' % (stem, state, data.get('role'), data.get('level'), data.get('parent_pid') or data.get('owner_pid'))
        if state == 'running':
            transcript = find_subagent_transcript(data.get('agent_id'))
            try:
                idle = time.time() - Path(transcript).stat().st_mtime if transcript else None
            except OSError:
                idle = None
            if idle is not None:
                line += ' last activity %s' % age_text(idle) + (' silent' if idle >= SILENT_SECONDS else '')
            hit = over_budget(data)
            if hit:
                line += ' over-budget %s (budget %dm)' % (age_text(hit[0]), hit[1])
        report = path.parent / (path.name[:-len('.attempt.json')] + '.md')
        if report.is_file() and report.stat().st_size and (state in ('running', 'orphaned') or (state not in ('completed', 'failed') and report.stat().st_mtime > path.stat().st_mtime)):
            line += ' report-unrecorded'  # T-0383/T-0703/T-0705: a report exists and nobody recorded it, so no verdict was delivered; one token for a running or orphaned attempt (T-0383) and any unrecorded one with a newer report (T-0703)
        lines.append(line)
        sent = path.parent / (path.name[:-len('.attempt.json')] + '.delivery.json')
        if sent.is_file():
            try:
                dv = json.loads(sent.read_text(encoding='utf-8'))
            except ValueError:
                dv = {}
            if dv.get('state') != 'sent':
                lines.append('%s verdict-delivery-%s to %s%s' % (stem, dv.get('state', 'unreadable'), dv.get('receiver'), ': ' + dv['error'] if dv.get('error') else ''))
    if not found and not orphans_only:
        where = order.records_dir(base)
        lines.append('no attempts in %s' % directory + ('; try %s' % where if where != Path(os.path.abspath(directory)) else ''))
    return lines


def inner_loop(path):
    """True when the nearest .sdlc/config above path declares `profile: inner-loop` (T-0514); a repo without it sees no change."""
    for parent in Path(os.path.abspath(path)).parents:
        cfg = parent / '.sdlc' / 'config'
        if cfg.is_file():
            try:
                return any(re.fullmatch(r'profile:\s*inner-loop\s*(#.*)?', ln.strip()) for ln in cfg.read_text(encoding='utf-8').splitlines())
            except (OSError, ValueError):
                return False
    return False


def limit_stop(name, root='.'):
    """T-0537: a running attempt whose sub-agent ended on a spend or session limit becomes limit-stopped, with the
    <role>-<level>.limit marker naming the resume call. Refused (exit 2) for an attempt that is not running or has a result."""
    for path in sorted(Path(root).glob('**/*.attempt.json')):
        if '.git' in path.parts or '.worktrees' in path.parts:
            continue
        data = read_attempt(path)
        if name not in (data.get('name'), data.get('agent_name')):
            continue
        report = path.with_name(path.name[:-len('.attempt.json')] + '.md')
        if data.get('status') != 'running':
            raise Refuse(2, 'dispatch.py: %s is %s, not running; nothing to mark limit-stopped' % (name, data.get('status')))
        if report.is_file() and report.stat().st_size:
            raise Refuse(2, 'dispatch.py: %s has a result at %s; record it instead of marking it limit-stopped' % (name, report))
        agent = data.get('agent_name') or data.get('name')
        send = 'SendMessage({to: "%s", message: "The limit has reset; continue your work."})' % agent
        again = 'python3 %s prepare %s %s %s' % (HERE / 'dispatch.py', data.get('role'), data.get('level'), data.get('handoff'))
        data.update(status='limit-stopped', limit_stopped_at=run_lifecycle.now())
        run_lifecycle.write(path, data)
        path.parent.joinpath('%s-%s.running' % (data.get('role'), data.get('level'))).unlink(missing_ok=True)
        marker = path.parent / ('%s-%s.limit' % (data.get('role'), data.get('level')))
        marker.write_text(json.dumps(dict(ts=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), role=data.get('role'), level=data.get('level'),
                                          handoff=data.get('handoff'), resume=send, prepare=again, evidence='marked by resume --limit'),
                                     separators=(',', ':')) + '\n', encoding='utf-8')
        return ['limit-stopped: %s' % path,
                '1. %s   # by name, keeps its context; then record the dispatch as usual' % send,
                '2. %s   # new attempt, only if the agent is gone' % again]
    raise Refuse(2, 'dispatch.py: no attempt named %s under %s' % (name, root))


# T-0703: a resumed agent's idle notice may never reach the conductor, so the resume message asks it to report back itself.
RESUME_MESSAGE = ("Continue your interrupted work. When you finish, SendMessage to 'main' with your one-line pointer "
                  "('%s-%s <status> <path>') so the conductor records it.")


def resume(name, root='.'):
    """The resume ladder for an orphaned or interrupted attempt found by stem or Agent name under root.
    Under `profile: inner-loop` a running attempt with a stored agent id whose transcript is silent (SILENT_SECONDS) also gets it (T-0514)."""
    for path in sorted(Path(root).glob('**/*.attempt.json')):
        if '.git' in path.parts or '.worktrees' in path.parts:
            continue
        data = read_attempt(path)
        if name not in (data.get('name'), data.get('agent_name')):
            continue
        state = attempt_state(data)
        silent = False
        if state == 'running' and inner_loop(path):
            transcript = find_subagent_transcript(data.get('agent_id'))
            try:
                silent = bool(transcript) and time.time() - Path(transcript).stat().st_mtime >= SILENT_SECONDS
            except OSError:
                silent = False
        if state not in ('orphaned', 'interrupted', 'limit-stopped') and not silent:
            raise Refuse(2, 'dispatch.py: %s is %s, not orphaned, interrupted, or limit-stopped; nothing to resume' % (name, state))
        agent = data.get('agent_name') or data.get('name')
        aid = data.get('agent_id') or 'unknown'
        transcript = data.get('transcript') or 'the sub-agent transcript for %s under ~/.claude/projects/' % (aid if aid != 'unknown' else agent)
        addendum = ('Resume note: attempt %s was interrupted before it reported. First step: run git status, then read its transcript at %s; '
                    'continue from what is on disk and never replay an old report.' % (data.get('name'), transcript))
        nudge = RESUME_MESSAGE % (data.get('role'), data.get('level'))
        return ['1. SendMessage({to: "%s", message: "%s"})   # by name' % (agent, nudge),
                '2. SendMessage({to: "%s", message: "%s"})   # by id' % (aid, nudge),
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


def row_before(directory, role, level):
    """(model, effort) of the last runs.jsonl line for role and level in directory's records dir, else None (T-0537)."""
    for _, row in reversed(order.records(directory)):
        if isinstance(row, dict) and row.get('role') == role and row.get('level') == level and row.get('model'):
            return row.get('model'), row.get('effort')
    return None


def prepare(role, level, handoff, plugin=PLUGIN, dry_run=False, skip=(), solo='', prune=None, notify='', notify_re='', tree=''):
    """Run the gates and write the records; returns the dispatch dict. skip names gates to disable (selftest only);
    solo is the model of a solo ticket whose runs.jsonl record is not in this tree (--solo-model); prune overrides the
    role's default prune flag (True, False, or None for the default); notify names the mailbox receiver that gets the
    verdict message when record closes the attempt (T-0383), notify_re the message id it answers; tree (--tree) names
    the execution tree, a worktree of the handoff's repository, for a build run in a lane worktree whose handoff lives
    in the primary checkout (T-0413)."""
    plugin = Path(plugin)
    if os.environ.get('SDLC_BACKEND', 'claude') != 'claude':
        raise Refuse(2, 'dispatch.py prepare is the Claude host path; Codex dispatches through run.sh')
    try:
        rows = claude_roles.table(plugin)
    except claude_roles.TableError as e:
        raise Refuse(2, 'dispatch.py: ' + str(e))
    if role == 'solo' or level not in rows.get(role, {}):
        raise Refuse(2, 'usage: dispatch.py prepare <role> <level> <handoff.md>  (no pipeline row %s:%s in adapters/claude/levels.json)' % (role, level)
                     + ('\nsolo is not a pipeline row: start a solo ticket with python3 %s run --task-dir <dir> --tier L2 --no-worktree, or python3 %s prep for a lane'
                        % (HERE / 'solo_run.py', HERE / 'fanout.py') if role == 'solo' else ''))
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
    if 'plugin_min' not in skip:  # T-0593: the repo's plugin_min: line against this plugin's own manifest
        msg = plugin_min.refusal(directory, plugin, 'claude')
        if msg:
            raise Refuse(2, msg)
    if tree:  # T-0413: refused before the lock, so no record is written
        known = {os.path.realpath(p) for p, _ in worktrees(git('rev-parse', '--show-toplevel', cwd=directory).stdout.strip() or os.getcwd())}
        if os.path.realpath(tree) not in known:
            raise Refuse(2, 'dispatch.py: --tree %s is not a worktree of this repository' % tree)
    # The execution tree, settled once: Tree, the tmp prefix, the worktree and branch snapshot, and the Base sha all follow it.
    run_tree = os.path.realpath(tree) if tree else exec_tree(directory)
    definition = plugin / 'agents' / ('%s-%s.md' % (role, level))
    if not definition.is_file():
        raise Refuse(2, 'no generated definition %s; run: python3 %s generate' % (definition, HERE / 'claude_roles.py'))
    try:
        for sk in claude_roles.source(plugin, role)[1]:
            if not (plugin / 'skills' / sk / 'SKILL.md').is_file():
                raise Refuse(2, 'agent %s declares missing skill: %s' % (role, sk))
    except claude_roles.TableError as e:
        raise Refuse(2, 'dispatch.py: ' + str(e))

    # The records dir (order.records_dir): results, attempts, dispatch records, markers, base-sha and runs.jsonl. The
    # handoff gates above and below keep the handoff dir; skips.md stays in the task folder (order.task_dir).
    records = order.records_dir(directory)  # made (create=True) only once every gate has passed, just before the lock
    model = agent_alias(family(role, model, directory, solo))
    prev = row_before(records, role, level)
    if prev and prev != (model, effort):
        say('row changed: %s %s was %s/%s on the previous attempt, now %s/%s' % (role, level, prev[0], prev[1], model, effort))
    if not dry_run:
        mailbox(role)

    task_handoff = handoff.name == 'handoff.md' and not directory.name.startswith('step-')
    if 'goal' not in skip and role in ('planner', 'plan-reviewer') and task_handoff:
        p = script('steps.py', 'precheck', directory)
        if p.returncode != 0:
            raise Refuse(2, (p.stdout + p.stderr).rstrip('\n'),
                         'dispatch.py: steps.py precheck refused the task handoff in %s; add a ## Goal section' % directory)

    if 'unfilled' not in skip and task_handoff:
        root = directory.parent
        if not (root / '_templates').is_dir() and (root.parent / '_templates').is_dir():
            root = root.parent  # ticket_root: tickets layout
        try:
            hit = tickets.unfilled_line(root, handoff.read_text(encoding='utf-8'))
        except (OSError, UnicodeDecodeError):
            hit = None
        if hit:
            raise Refuse(2, 'dispatch.py: %s:%d is unfilled template text %r; fill in the ticket before dispatching %s'
                         % (handoff, hit[0], hit[1].strip()[:60], role))

    replan_approved = ''
    if 'replan' not in skip and role == 'planner':  # T-0553: the first plan and one replan, then the person decides
        n = len(order.ordered(records, 'planner'))
        if n >= 2:
            replan_approved = ' '.join(os.environ.get('SDLC_REPLAN_APPROVED', '').split())
            if not replan_approved:
                raise Refuse(2, 'dispatch.py: replan cap: %s already holds %d planner results (the first plan and the one replan); '
                                'planner run %d needs the person\'s approval' % (records, n, n + 1),
                             'dispatch.py: replan cap: ask the person (split the ticket, approve one more replan, or drop scope), '
                             'then rerun prepare with --approved "<who: why>"')
            if not APPROVAL_RE.match(replan_approved):
                raise Refuse(2, 'dispatch.py: replan cap: --approved takes "<who: why>": who approved, a colon, and why')
            replan_approved = 'replan approved: planner run %d: %s' % (n + 1, replan_approved)

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

    time_approved, time_ticket = '', None
    if 'time' not in skip:  # T-0555: a ticket past its agent-time budget waits for the person
        time_ticket = budget.ticket_of(handoff)
        tt = ticket_time(time_ticket) if time_ticket is not None else None
        if tt and tt[0] >= tt[1]:
            time_approved = ' '.join(os.environ.get('SDLC_TIME_APPROVED', '').split())
            if not time_approved:
                raise Refuse(2, 'dispatch.py: time budget: %s has used %dm of agent time, past its %dm (size %s, %dm per approval); %s %s needs the person\'s approval'
                                % (time_ticket, tt[0], tt[1], tt[3], tt[2], role, level),
                             'dispatch.py: time budget: check the last role (a stdin wait, a stall), ask the person (go on, split the ticket, or drop scope), '
                             'then rerun prepare with --approved "<who: why>"; a headless lane stops the ticket as blocked')
            if not APPROVAL_RE.match(time_approved):
                raise Refuse(2, 'dispatch.py: time budget: --approved takes "<who: why>": who approved, a colon, and why')
            time_approved = 'time budget approved: %dm of %dm: %s' % (tt[0], tt[1], time_approved)

    guidance_differs = []
    if 'guidance' not in skip:  # T-0655: a lane role reads the lane's guidance; refused before the lock, so no record is written
        lane_top = git('rev-parse', '--show-toplevel', cwd=run_tree).stdout.strip()
        guidance_differs, missing = lane_guidance(lane_top, handoff) if lane_top else ([], [])
        if missing:
            raise Refuse(5, *missing, 'dispatch.py: sync the guidance into the lane (fanout.py sync --paths) or fix the handoff, then rerun prepare')
        for f in guidance_differs:
            say('lane guidance differs: ' + f)

    lock = None
    try:
        if not dry_run:
            records = order.records_dir(directory, create=True)
            try:
                lock = run_lifecycle.lock(records)
            except ValueError as e:
                raise Refuse(2, 'dispatch.py: ' + str(e))
            if 'lock' not in skip:
                recovered = settle(records, dry_run)
                if recovered:
                    say('recovered stale attempt(s) before this dispatch: ' + ', '.join(recovered))
        stem, k = next_stem(records, role, level)
        name = agent_name(role, level, directory, k)
        result = records / (stem + '.md')
        # the execution tree's toplevel: a lane worktree handoff, a --tree lane, or a main-checkout handoff run from a lane all get the lane as Tree
        toplevel = git('rev-parse', '--show-toplevel', cwd=run_tree).stdout.strip() or git('rev-parse', '--show-toplevel').stdout.strip() or os.getcwd()
        # T-0550, T-0563: the prefix sits under <worktree root>/tmp (the sibling <main checkout>.worktrees), never nested in a
        # lane; scratch goes to $TMPDIR
        tmp_prefix = str((wtroot.tmp_root(toplevel) or wtroot.default_root(toplevel) / 'tmp') / name)
        scratch = str(wtroot.scratch_dir(name, toplevel))

        base, review, diff_range, range_line = None, '', None, ''
        if role in ('builder', 'verifier'):
            stored, base = build_base(directory, records, run_tree, role)
            if role == 'verifier':
                review, base = ready_review(directory, toplevel, base)
                # T-0661: the end a recorded builder left in end-sha bounds the diff, so later steps or merges stay out of it
                end, kind = step_end(records, toplevel)
                if review and end:
                    diff_range = '%s..%s' % (base, review)
                    range_line = ('Diff range: %s (the Review sha wins over the end this step\'s builder recorded, %s; '
                                  'later commits in Tree are not this step\'s)' % (diff_range, end))
                elif kind == 'commit' and git('merge-base', '--is-ancestor', base, end, cwd=toplevel).returncode == 0:
                    diff_range = '%s..%s' % (base, end)
                    range_line = ('Diff range: %s (where this step\'s build ended, recorded by its builder\'s record: '
                                  'git diff %s; later commits in Tree are not this step\'s)' % (diff_range, diff_range))
                elif kind == 'tree':
                    diff_range = '%s %s' % (base, end)
                    range_line = ('Diff range: git diff %s (the build ended uncommitted: %s is a tree hash of its working tree, '
                                  'recorded by its builder\'s record; later edits in Tree are not this step\'s)' % (diff_range, end))
                elif end:
                    say('end-sha %s is not a descendant of Base sha %s: no Diff range line' % (end[:12], base[:12]))
            elif not dry_run:
                (records / 'end-sha').unlink(missing_ok=True)  # a new build: the last attempt's end is stale
            if not dry_run and base != stored:
                (records / 'base-sha').write_text(base + '\n', encoding='utf-8')

        # T-0646: every role writes its result to the Report file and ends with a one-line pointer, so the completion notice stays short
        prompt = ('%s\nHandoff: %s\nArtifacts dir: %s\nReport file: %s (before you end, write your result to exactly this path with the Write '
                  'tool: exactly the output format your instructions define, starting with its first heading, with nothing before it and nothing '
                  'after the last section, and no <!-- role=... --> header line: dispatch.py record adds it, so check the file with results.py '
                  'validate <file> --role %s --headerless; dispatch.py record reads the file, and a missing one fails the run)\n'
                  'End with one line: `%s <status> %s` (status is your Status or Verdict value, else done), nothing else.\n'
                  'Tree: %s (run every Bash call as cd %s && ...; the shell keeps no working directory between calls)\n'
                  '%sThrowaway worktrees only under %s (git worktree add --detach "%s/<name>" HEAD creates the parents); remove them, and any '
                  'scratch output you wrote under that prefix (rm is allowed there and refused elsewhere), when done.\n'
                  'Scratch files that are not worktrees (probe files, mutated copies) only under %s, never in the repo (rm is allowed there too).\n%s'
                  % (list_title(directory, role, level, k), handoff_locator(handoff), handoff_locator(records), result, role, role, result,
                     toplevel, shlex.quote(toplevel), ports_line(toplevel), tmp_prefix, tmp_prefix, scratch, SEARCH_SCOPE))
        if role == 'verifier':
            # T-0591: run rules every verifier gets, so the conductor stops adding them by hand
            prompt += ('\n' + ('Diff only the Diff range below, not Base sha against HEAD.' if range_line else
                                'The build may be uncommitted: diff against Base sha, not HEAD.') + ' Run every command in the foreground with an explicit '
                       'Bash timeout under 600000 ms; never run_in_background or Monitor. Never run the full check.sh; run the checks the '
                       'criteria name. Never use git stash; the stash stack is shared across sessions.')
        if base:
            prompt += '\nBase sha: %s (the commit this build started from; diff scope criteria against it)' % base
        if range_line:
            prompt += '\n' + range_line
        if review:
            prompt += ('\nReview sha: %s (%s%s, the state the worker marked ready with lanes.py ready: review that commit; when Tree '
                       'no longer holds it, check it out under the throwaway prefix above)' % (review, READY_REFS, ticket_label(directory)[0]))
        skills = repo_skills_line(toplevel, handoff) if role == 'builder' else ''
        if skills:
            prompt += '\n' + skills
        for f in guidance_differs:
            prompt += '\nGuidance: read %s; it overrides the auto-attached main checkout copy' % os.path.join(toplevel, f)
        minutes = role_minutes(role, level)
        prompt += ('\nTime budget: %dm wall clock for %s %s; past it, dispatch.py status flags this attempt and the conductor checks on you'
                   % (minutes, role, level))

        sha = hashlib.sha256(handoff.read_bytes()).hexdigest()
        reason = os.environ.get('SDLC_ROUTING_REASON', '').strip()
        pid, source = parent_pid()
        dispatch = dict(subagent_type='sdlc-lite:%s-%s' % (role, level), name=name,
                        description=list_description(directory, role, level),
                        model=model, effort=effort, prompt=prompt,
                        run_in_background=os.environ.get('SDLC_HEADLESS') != '1',
                        prune=role in PRUNE_ROLES if prune is None else bool(prune),
                        role=role, level=level, result_name=stem, result=str(result), tmp_prefix=tmp_prefix, scratch=scratch,
                        base_sha=base, review_sha=review or None, diff_range=diff_range, tree=toplevel, handoff=str(handoff), artifacts_dir=str(records),
                        handoff_sha256=sha, shared_with_builder=False, lane_override=lane_override, specgate=specgate, time_budget_min=minutes,
                        routing_reason=reason or 'Caller selected this role and level; no task-specific rationale supplied.',
                        attempt_file=str(records / (stem + '.attempt.json')), plugin_version=plugin_min.running(PLUGIN, 'claude')[0],
                        dispatch_file=str(records / (stem + '.dispatch.json')), dry_run=dry_run)
        if notify:
            dispatch.update(notify=notify, notify_re=notify_re)
        if dry_run:
            return dispatch
        if notify:
            unregistered_receiver(notify, toplevel)
        for line in (['lane override: ' + lane_override] if lane_override else []) + ([replan_approved] if replan_approved else []):
            skips = Path(order.task_dir(directory) or directory) / 'skips.md'
            if line not in (skips.read_text(encoding='utf-8').splitlines() if skips.is_file() else []):
                with skips.open('a', encoding='utf-8') as f:
                    f.write(line + '\n')
        if time_approved:  # in the ticket folder, where ticket_time reads it
            with (Path(time_ticket) / 'skips.md').open('a', encoding='utf-8') as f:
                f.write(time_approved + '\n')
        attempt = dict(attempt_id=uuid.uuid4().hex, name=stem, agent_name=name, role=role, level=level, backend='claude',
                       transport='subagent', model=model, effort=effort, routing_reason=dispatch['routing_reason'],
                       reason_source='caller' if reason else 'fallback', status='running', started_at=run_lifecycle.now(),
                       project=os.getcwd(), handoff=str(handoff), plugin_version=dispatch['plugin_version'], parent_pid=pid, parent_pid_source=source, handoff_sha256=sha, time_budget_min=minutes,
                       worktrees_before=[p for p, _ in worktrees(toplevel)], branches_before=branches(toplevel))
        dispatch['attempt_id'] = attempt['attempt_id']
        run_lifecycle.write(Path(dispatch['attempt_file']), attempt)
        run_lifecycle.write(Path(dispatch['dispatch_file']), dispatch)
        # T-0505: the running marker warn-handoff-edit.sh, board.py and fleet_status.py read; keyed by role and level, as record and recover unlink it
        running = records / ('%s-%s.running' % (role, level))
        running.write_text('%d\n' % int(time.time()), encoding='utf-8')
        # T-0550: owner markers; the session pid or the running marker keeps a folder live for the sweep
        ticket = budget.ticket_of(handoff)
        for d in (tmp_prefix, scratch):
            wtroot.mark(d, pid or 0, role='%s-%s' % (role, level), ticket=ticket and Path(ticket).name, running=running)
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


def tmp_roots(tree):
    """The roots a dispatch tmp prefix may sit under: <worktree root>/tmp (T-0563), and for one release
    the legacy <main checkout>/.claude/worktrees/tmp (T-0550) and .worktrees/tmp, and <tree>/.worktrees/tmp of an attempt prepared
    before 0.23.0."""
    roots = [str(r) for r in wtroot.tmp_roots(tree)] + [os.path.join(tree, wtroot.LEGACY, 'tmp')]
    return list(dict.fromkeys(os.path.realpath(r) for r in roots))


def sweep_tmp(tree, scratch):
    """Remove this dispatch's scratch dir (only one under the repo's scratch root), then run the crash sweep (wtroot.sweep:
    a dead owner past the limit goes, a folder with no owner marker is reported, never deleted). Never raises."""
    try:
        if scratch and not os.path.islink(scratch) and under(scratch, str(wtroot.scratch_root(tree))) \
                and os.path.realpath(scratch) != os.path.realpath(str(wtroot.scratch_root(tree))):
            shutil.rmtree(scratch, ignore_errors=True)
        for v, p in wtroot.sweep(tree, apply=True):
            if v in ('removed', 'unmarked', 'failed'):
                say(wtroot.lines([(v, p)])[0])
    except OSError as e:
        say('could not sweep: %s' % e)


def remove_tmp(tree, prefix):
    """Remove the worktrees and directory under the dispatch's tmp prefix, then the empty parents, and say how many worktrees
    went (T-0426). The prefix must sit strictly under a tmp root (tmp_roots), hold no . or .. component, and not be a symlink, else nothing is removed. Never raises."""
    bare = prefix.rstrip('/')
    if not bare or any(part in ('.', '..') for part in bare.split(os.sep)):
        say('refusing to remove %s: it has a . or .. component' % prefix)
        return
    if os.path.islink(bare):
        say('refusing to remove %s: it is a symlink' % prefix)
        return
    real = os.path.join(os.path.realpath(os.path.dirname(bare)), os.path.basename(bare))
    roots = tmp_roots(tree)
    root = next((r for r in roots if real.startswith(r + os.sep)), None)
    if root is None:
        say('refusing to remove %s: not under %s' % (prefix, ' or '.join(roots)))
        return
    removed = 0
    try:
        for path, _ in worktrees(tree):
            if under(path, real):
                if git('worktree', 'remove', '--force', '--force', path, cwd=tree).returncode == 0:
                    removed += 1
        shutil.rmtree(real, ignore_errors=True)
        git('worktree', 'prune', cwd=tree)
        for parent in (root, os.path.dirname(root)):
            try:
                os.rmdir(parent)
            except OSError:
                pass
    except OSError as e:
        say('could not clean %s: %s' % (prefix, e))
    say('cleaned: %d tmp worktrees' % removed)


def strays(tree, prefix, attempt):
    """(worktree [path, branch] pairs, branch names) that appeared since prepare and belong to this role: a worktree under
    a tmp root (tmp_roots; its own prefix left out) or on a branch named with the role's agent name, a branch with that
    name as prefix. Peers' worktrees and branches elsewhere are not this role's (T-0371), nor is a host-owned tree
    (host-owned: ~/.codex/worktrees/*, .claude/worktrees/agent-*, wtroot.host_owned; T-0564)."""
    if 'worktrees_before' not in attempt:
        return [], []
    seen, known = set(attempt['worktrees_before']), set(attempt.get('branches_before', []))
    roots, mine = tmp_roots(tree), os.path.basename(prefix.rstrip('/'))
    own_br = lambda b: bool(b) and b.startswith(mine)
    wts = [(p, b) for p, b in worktrees(tree) if p not in seen and not under(p, prefix) and not wtroot.host_owned(p)
           and (any(under(p, r) for r in roots) or own_br(b))]
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
PRUNE_KEYS = ('name', 'agent_id', 'role', 'level', 'recorded_at', 'session')


def prune_session():
    """The current Claude session id (a sub-agent shares its parent's), or None outside a Claude session (T-0601)."""
    return os.environ.get('CLAUDE_CODE_SESSION_ID') or None


def prune_root(root='.'):
    """The main checkout when root is inside a linked worktree, since a lane's queue would die with its tree (T-0601);
    else root."""
    try:
        main_ = wtroot.main_top(root)
        top = git('rev-parse', '--show-toplevel', cwd=root).stdout.strip()
    except OSError:
        return root
    return main_ if main_ and top and os.path.realpath(main_) != os.path.realpath(top) else root


def prune_path(root='.'):
    return Path(prune_root(root)) / PRUNE_REL


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
    """Queue an agent by name (one entry per name; a later add replaces the earlier one), tagged with the current session."""
    entry = dict(name=name, agent_id=agent_id, role=role, level=level, recorded_at=run_lifecycle.now(), session=prune_session())
    prune_edit(root, lambda es: [e for e in es if e.get('name') != name] + [entry])
    return entry


def prune_done(root, name):
    """Remove an entry; True when it was queued."""
    found = []
    prune_edit(root, lambda es: [e for e in es if e.get('name') != name or found.append(1)])
    return bool(found)


def prune_forget_stale(root):
    """Remove the entries another session queued (or that carry no session); returns their names. No current session
    forgets nothing: every entry is then listed."""
    session, gone = prune_session(), []
    if session:
        prune_edit(root, lambda es: [e for e in es if e.get('session') == session or gone.append(e['name'])])
    return gone


def prune_solo_name(dirs, default):
    """The live Agent name of a landed solo: the name in the newest solo *.dispatch.json in a ticket folder or its records
    dir (fanout prep writes <id>-solo, solo_run.py <n>-solo-<level>), searched in the order given; default when none (T-0601)."""
    for d in dirs:
        found = []
        for where in {Path(d), Path(order.records_dir(d))}:
            for f in where.glob('*.dispatch.json'):
                try:
                    j = json.loads(f.read_text(encoding='utf-8'))
                    mtime = f.stat().st_mtime
                except (OSError, ValueError):
                    continue
                if isinstance(j, dict) and j.get('role') == 'solo' and j.get('name'):
                    found.append((mtime, j['name']))
        if found:
            return max(found)[1]
    return default


def host_lanes(root, names):
    """{name: lane dict} for each queued agent name that has a plugin host lane whose tree or branch still exists
    (lane lifecycle, T-0453). Advisory: a root outside a git work tree, or any lane error, finds none."""
    try:
        import lanes
        ctx = lanes.Ctx(root)
        found = {}
        for d in lanes.discover(ctx):
            if d['owner'] != 'host' or not (d['exists'] or (d['branch'] and lanes.has_ref(ctx.top, 'refs/heads/' + d['branch']))):
                continue
            for n in names:
                if n in (d['lane'], os.path.basename(d['path'])):
                    found.setdefault(n, d)
        return found
    except Exception:  # noqa: BLE001 - lane reporting never blocks the prune queue
        return {}


def prune_lane(root, name):
    """After the agent is stopped: close its host lane through lanes.close_lane and return `closed lane <path> (<reason>)`
    or `lane still open: <path> (<reason>)`; None when the agent has no open host lane."""
    d = host_lanes(root, [name]).get(name)
    if d is None:
        return None
    import lanes
    try:
        r = lanes.close_lane(d['lane'], cwd=root)
    except lanes.LaneError as e:
        return 'lane still open: %s (%s)' % (d['path'], e)
    first = (r['message'].splitlines() or [''])[0]
    if r['rc'] == 0:
        m = re.match(r'closed .*\((.*)\)$', first)
        return 'closed lane %s (%s)' % (d['path'], m.group(1) if m else first)
    return 'lane still open: %s (%s)' % (d['path'], first)


def prune_lines(root='.'):
    """One stop call per entry of the current session (every entry outside a Claude session), then one line counting
    the entries of other sessions, which no TaskStop here can reach (T-0601)."""
    session, entries = prune_session(), prune_read(root)
    stale = [e for e in entries if session and e.get('session') != session]
    entries = [e for e in entries if e not in stale]
    tail = (['prune: %d from other sessions not listed; drop them: dispatch.py prune --forget-stale' % len(stale)]
            if stale else [])
    if not entries:
        return ['prune: nothing queued'] + tail
    open_ = host_lanes(root, [e['name'] for e in entries])
    return ['TaskStop task_id=%s    # %s %s, recorded %s; then: dispatch.py prune --done %s%s'
            % (e['name'], e.get('role') or 'agent', e.get('level') or '', e.get('recorded_at') or '?', e['name'],
               '; lane open %s' % open_[e['name']]['path'] if e['name'] in open_ else '') for e in entries] + tail


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
    """After a recorded success: queue a dispatch with prune true and print `prune: <name>`; skip an open attempt or a pending
    follow-up, except a filer's: its follow-ups are its output and tickets.py close consumes them (T-0531)."""
    name = attempt.get('agent_name') or d.get('name')
    if not d.get('prune') or not name:
        return False
    if attempt.get('status') != 'completed' or attempt_open(d['artifacts_dir'], name, Path(d['attempt_file'])):
        return False
    try:
        if d.get('role') != 'filer' and follow_up_pending(Path(d['result']).read_text(encoding='utf-8', errors='replace')):
            return False
    except OSError:
        return False
    prune_add(attempt.get('project') or d['tree'], name, d['role'], d['level'], agent_id or attempt.get('agent_id'))
    print('prune: ' + name)
    return True


def find_subagent_transcript(agent_id):
    """T-0446: the host keeps a sub-agent's transcript at <projects>/<project>/<session>/subagents/agent-<agent id>.jsonl
    (projects: SDLC_CLAUDE_PROJECTS, else ~/.claude/projects). Returns its path when exactly one such file exists, else None:
    several matches are never guessed between, and an id that is not a plain file-name part reads nothing."""
    if not agent_id or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', agent_id):
        return None
    base = Path(os.environ.get('SDLC_CLAUDE_PROJECTS') or Path.home() / '.claude' / 'projects')
    try:
        hits = [p for p in base.glob('*/*/subagents/agent-%s.jsonl' % agent_id) if p.is_file() and not p.is_symlink()]
    except OSError:
        return None
    return str(hits[0]) if len(hits) == 1 else None


def started(dispatch_file, agent_id):
    """T-0476: store the spawned sub-agent's id in its running attempt record (today the id lands only at record); returns the exit code."""
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', agent_id or ''):
        raise Refuse(2, 'dispatch.py: --agent-id must be a plain id (letters, digits, - and _), got %r' % agent_id)
    try:
        d = json.loads(Path(dispatch_file).read_text(encoding='utf-8'))
        attempt_path = Path(d['attempt_file'])
        attempt = json.loads(attempt_path.read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Refuse(2, 'dispatch.py: cannot read the dispatch file or its attempt record %s: %s' % (dispatch_file, e))
    if not isinstance(attempt, dict) or attempt.get('attempt_id') != d.get('attempt_id'):
        raise Refuse(2, 'dispatch.py: %s belongs to another attempt than %s' % (attempt_path, dispatch_file))
    if attempt.get('status') != 'running':
        raise Refuse(2, 'dispatch.py: attempt %s is %s, not running; nothing to mark started' % (attempt_path.name, attempt.get('status')))
    attempt['agent_id'] = agent_id
    run_lifecycle.write(attempt_path, attempt)
    say('started: %s agent_id %s' % (attempt_path.name, agent_id))
    return 0


def record(dispatch_file, stdin=None, agent_id=None, usage=None, duration_ms=None, validate=validate_result, resolved_model=None, transcript=None, no_result=False):
    """Validate, record, and close one dispatched role; returns the exit code (0 ok, 1 failed, 2 refused or no result yet, 3 invalid result).

    The result is the file the role wrote at the dispatch's result path, else stdin() (a callable) when the file is
    missing or empty. stdin text with a ## heading line is a result unless it is a truncation of the transcript's final message (T-0349); any other text is the sub-agent's error text,
    except a one-line placeholder under 40 characters with no error word that is not a limit message, which yields to a complete transcript result with a ## heading (T-0685).
    validate(role, path) returns None or a reason; selftest passes an accept-all one as the negative control.
    With transcript (a jsonl path), a result missing from both the file and stdin is taken from the transcript's last
    assistant message; one that stopped on max_tokens is refused as truncated (T-0343).
    With no file, empty stdin, and no transcript result, the attempt stays running and the exit is 2 (T-0412); no_result=True closes it failed (exit 1) as before.
    A result that fails validate from an attempt prepared under another plugin version (plugin_version missing or different)
    with at least one ## heading is legacy (T-0678): closed completed (exit 0) with legacy_format, never failed."""
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
    if attempt.get('status') not in ('running', 'limit-stopped'):  # T-0537: a limit-stopped agent resumed by SendMessage is recorded as usual
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
        # T-0685: a short one-line placeholder (such as `echo x |`) is not error text when the transcript holds a complete result.
        if (is_err and fin and fin[1] != 'max_tokens' and re.search(r'^## ', fin[0], re.M) and '\n' not in said.strip() and len(said.strip()) < 40
                and not LIMIT_RE.search(said) and not re.search(r'error|terminated|fail|abort|killed|exception|timeout', said, re.I)):
            print('dispatch.py: ignored stdin "%s" (no heading, under 40 chars); recorded the transcript\'s final message' % said.strip(), file=sys.stderr)
            is_err = False
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
        elif not said.strip() and not no_result:  # T-0412: nothing yet, not a failure; the role may still write its report
            print('dispatch.py: no result yet at %s; the attempt stays running: record again once the %s writes it, or pass --no-result to close it failed'
                  % (result, role), file=sys.stderr)
            return 2
        elif said.strip() and '\n' not in said.strip() and said.split()[0] == role:  # T-0646: a pointer line with no file behind it
            text, error = '', 'no result file at %s (the %s ended with the pointer "%s" but must write its report there before it ends)' % (
                result, role, said.strip())
        else:
            text, error = '', said.strip() or 'no result file at %s (the %s must write its report there before it ends)' % (result, role)
    if not text.strip():
        log = result.with_suffix('.log')
        log.write_text(error + '\n', encoding='utf-8')
        remove_tmp(tree, prefix)
        sweep_tmp(tree, d.get('scratch'))
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
    result_sha = hashlib.sha256(result.read_bytes()).hexdigest()  # T-0388: the accepted bytes, after the header write
    remove_tmp(tree, prefix)
    sweep_tmp(tree, d.get('scratch'))
    found = strays(tree, prefix, attempt)
    stray_wt, stray_br = [p for p, _ in found[0]], found[1]
    handoff = Path(d['handoff'])
    now_sha = hashlib.sha256(handoff.read_bytes()).hexdigest() if handoff.is_file() else ''
    stale = bool(now_sha) and now_sha != d['handoff_sha256']
    est, basis, _ = cost_estimate.estimate(d['model'], usage)
    line = dict(ts=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), role=role, level=level, model=d['model'], effort=d['effort'],
                file=result.name, shared_with_builder=bool(d.get('shared_with_builder')), attempt_id=d['attempt_id'],
                handoff_sha256=d['handoff_sha256'], result_sha256=result_sha, stale_input=stale, routing_reason=d['routing_reason'], backend='claude',
                transport='subagent', agent_id=agent_id, usage=usage, cost_usd=est, cost_reason=None if est is not None else COST_REASON,
                duration_ms=duration_ms, turns=None, stray_worktrees=stray_wt, stray_branches=stray_br,
                loaded_context={'status': 'log absent'})  # T-0252: a sub-agent leaves no stream-json log to read
    reason = validate(role, str(result))
    legacy = None
    prepared = attempt.get('plugin_version')
    if reason is not None and prepared != plugin_min.running(PLUGIN, 'claude')[0] and re.search(r'^## ', body, re.M):
        legacy, reason = reason, None  # T-0678: the schema changed between prepare and record; not the role's failure
        line['legacy_format'] = legacy
    if est is not None:
        line.update(cost_estimated=True, cost_basis=basis)
    else:  # T-0402: no transcript and no tokens leaves no cost row; say so now and mark the row, never fail the record
        line['unpriced'] = True
        say('unpriced: %s has no cost row; pass --transcript <jsonl>' % d['name'])
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
    if legacy:
        say('legacy-format: %s result %s; prepared under %s, recorded as completed' % (role, legacy, prepared or 'an older plugin'))
    if reason is not None:
        say('%s result %s; see %s' % (role, reason, result))
        report_strays(found)
        close('failed', 3, result_sha256=result_sha)
        deliver_quietly(dispatch_file)
        return 3
    (result.parent / ('%s-%s.limit' % (role, level))).unlink(missing_ok=True)
    if role == 'builder':  # T-0378: a completed build without its pre-edit (red) controls leaves a process deviation
        subprocess.run([sys.executable, str(HERE / 'redck.py'), 'audit', d['handoff'], '--attempt-id', d['attempt_id']],
                       stdout=subprocess.DEVNULL, check=False)
        end = build_end(tree)  # T-0661: where this step's build ended, the verifier's Diff range end
        if end:
            (result.parent / 'end-sha').write_text(end + '\n', encoding='utf-8')
    report_strays(found)
    close('completed', 0, result_sha256=result_sha, **({'legacy_format': legacy} if legacy else {}))
    print(result)
    if role == 'ui-designer' and handoff.is_file() and re.search(r'^mode:\s*review\b', handoff.read_text(encoding='utf-8', errors='replace'), re.M):
        print(review_record_line(result, tree))
    deliver_quietly(dispatch_file)
    queue_prune(d, attempt, agent_id)
    return 0


def review_record_line(result, tree):
    """The repo-relative line a conductor pastes into a ticket handoff after a ui-designer review (T-0686): an absolute
    path there trips a repo's personal-path gate."""
    top = git('rev-parse', '--show-toplevel', cwd=result.parent).stdout.strip()
    rel = os.path.relpath(os.path.realpath(result), os.path.realpath(top)) if top else str(result)
    verdict = results._key_body_value(results._lines(str(result)), 'Verdict')[1] or 'no verdict'
    sha = git('rev-parse', '--short', 'HEAD', cwd=tree).stdout.strip() or 'no HEAD'
    return '- Review record: %s (%s at %s)' % (rel, verdict, sha)


HELD_NOTE_RE = re.compile(r'^(unmet-dependency|deferred):\s*(.*)$')  # steps.HELD_NOTE_RE
REF_ARG_RE = re.compile(r'^#?(?:(step-\d+|ticket)#)?(\d+)$')


def settle_held(result, by, evidence, refs=()):
    """Append `## Settled by owner` to a held verifier result (T-0684): one `- <ref> <owner>: <evidence> at <sha7>` line
    per `deferred <by>` criterion (or the --ref subset), so steps.held_items and fanout.py land read them as pass with no
    second verifier. Refuses (Refuse rc 2, file unchanged) a result that is not a `fail` whose ## For the next attempt
    first line is `deferred:` naming --by, a missing or absolute evidence path, and an evidence file with a ## Verdict
    (a review record) that is not pass or pass-with-notes. Returns the lines it added."""
    result = Path(result)
    if not result.is_file():
        raise Refuse(2, 'settle-held: no such verifier result: %s' % result)
    lines = results._lines(str(result))
    note = next((l.strip() for l in results._section_lines(lines, 'For the next attempt') if l.strip()), '')
    m = HELD_NOTE_RE.match(note)
    owners = [o.strip() for o in m.group(2).split(',')] if m else []
    if results.key_value(str(result), 'verifier') != 'fail' or not m or m.group(1) != 'deferred' or by not in owners:
        raise Refuse(2, 'settle-held: %s is not a held fail deferred to %s (its next-attempt line is %r); only a '
                        '`deferred: %s` hold is settled here, nothing written' % (result, by, note, by))
    default = result.parent.name if re.fullmatch(r'step-\d+', result.parent.name) else 'ticket'
    held = ['%s#%d' % (c['scope'] or default, c['k']) for c in results.criteria_states(str(result))
            if c['state'] == 'deferred' and c['who'] == by and c['k'] is not None]
    want = []
    for r in refs:
        rm = REF_ARG_RE.match(r.strip())
        ref = '%s#%s' % (rm.group(1) or default, rm.group(2)) if rm else r
        if ref not in held:
            raise Refuse(2, 'settle-held: %s is not a criterion deferred to %s in %s (held: %s); nothing written'
                         % (r, by, result, ', '.join(held) or 'none'))
        want.append(ref)
    want = want or held
    if not want:
        raise Refuse(2, 'settle-held: no criterion of %s is deferred to %s; nothing written' % (result, by))
    if os.path.isabs(evidence):
        raise Refuse(2, 'settle-held: --evidence must be repo-relative, got the absolute path %s; nothing written' % evidence)
    top = Path(git('rev-parse', '--show-toplevel', cwd=result.parent).stdout.strip() or '.')
    ev = top / evidence
    if not ev.is_file():
        raise Refuse(2, 'settle-held: no evidence file %s under %s; nothing written' % (evidence, top))
    has_verdict, verdict = results._key_body_value(results._lines(str(ev)), 'Verdict')
    if has_verdict and verdict.lower() not in ('pass', 'pass-with-notes'):
        raise Refuse(2, 'settle-held: the review record %s has Verdict %r, not pass or pass-with-notes; nothing written'
                     % (evidence, verdict or 'none'))
    sha = git('rev-parse', '--short=7', 'HEAD', cwd=top).stdout.strip() or '0000000'
    done = {'%s#%d' % (sc, k) for sc, k, who in results.owner_settled(str(result)) if who == by}
    add = ['- %s %s: %s at %s' % (ref, by, evidence, sha) for ref in want if ref not in done]
    if not add:
        return []
    text = result.read_text(encoding='utf-8')
    body = text.splitlines()
    i = results._first_heading(body, 'Settled by owner')
    if i is None:
        text = text.rstrip('\n') + '\n\n## Settled by owner\n' + '\n'.join(add) + '\n'
    else:
        end = next((j for j in range(i + 1, len(body)) if body[j].startswith('## ')), len(body))
        while end > i + 1 and not body[end - 1].strip():
            end -= 1
        body[end:end] = add
        text = '\n'.join(body) + '\n'
    result.write_text(text, encoding='utf-8')
    return add


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


def solo_report_file(sd, transcript=None):
    """The report of a recorded solo whose dispatch names a result (T-0682): the file when it holds text, else the
    transcript's final message written there (a lone `solo ...` pointer line is no report). Prints the path and returns
    0; with neither, returns 2 and changes nothing, so the row stays unpriced and the live marker stays."""
    result = Path(sd['result'])
    if result.is_file() and result.read_text(encoding='utf-8', errors='replace').strip():
        print('solo report: %s' % result)
        return 0
    fin = cost_estimate.transcript_final(transcript) if transcript else None
    text = fin[0].strip() if fin and fin[1] != 'max_tokens' else ''
    if text and not ('\n' not in text and text.split()[0] == 'solo'):
        result.write_text(text + '\n', encoding='utf-8')
        print('solo report: %s (from the transcript\'s final message)' % result)
        return 0
    print('dispatch.py: no solo report at %s and no transcript final message to take; the row and live marker are unchanged: '
          'record again once the solo writes it, or pass --transcript' % result, file=sys.stderr)
    return 2


ADVANCE_ROLE = {'build': 'builder', 'rebuild': 'builder', 'verify': 'verifier', 'reverify': 'verifier'}


def previous_attempt(steps, step_dir, handoff):
    """Before advance prepares a rebuild after a verifier fail: append that verifier's ## For the next attempt to the step
    handoff under ## Previous attempt (/chain 4.4), made when missing, earlier lines kept. Any other rebuild (no Status,
    an applied amend) has no newer verifier and adds nothing."""
    rd = steps.records_of(step_dir)
    v, b = order.newest(rd, 'verifier'), order.newest(rd, 'builder')
    if v is None or b is None or not order.counts_after(v, b) or steps.verdict_or_none(v) != 'fail':
        return
    notes = [l for l in (steps.section(v, 'For the next attempt') or []) if l.strip()]
    if not notes:
        return
    lines = handoff.read_text(encoding='utf-8').splitlines()
    at = next((i for i, l in enumerate(lines) if l.rstrip() == '## Previous attempt'), None)
    if at is None:
        lines += ([''] if lines and lines[-1].strip() else []) + ['## Previous attempt']
        end = len(lines)
    else:
        end = next((i for i in range(at + 1, len(lines)) if lines[i].startswith('## ')), len(lines))
        while end > at + 1 and not lines[end - 1].strip():
            end -= 1
    lines[end:end] = ['From %s:' % os.path.basename(v)] + notes
    handoff.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('previous attempt: %s' % handoff)


def advance(dispatch_file, rec):
    """One call per role completion (T-0645): rec() records the dispatch and returns its exit code; a non-zero record stops
    here with that code. Then a pruned role leaves the queue the way prune --done does and prints its TaskStop line, and
    steps.py next on the dispatch's step dir picks the next role: a builder or verifier action is prepared and its
    dispatch JSON printed, any other action prints `stop: <action> <reason>`. Outside a step dir a ticket-level completion
    moves the ticket on (T-0688): see advance_ticket."""
    rc = rec()
    if rc != 0:
        return rc
    d = json.loads(Path(dispatch_file).read_text(encoding='utf-8'))
    if solo_dispatch(dispatch_file):
        return advance_solo(d)
    attempt = read_attempt(d['attempt_file'])
    name, root = attempt.get('agent_name') or d.get('name'), attempt.get('project') or d['tree']
    if name and prune_done(root, name):
        print('TaskStop task_id=' + name)
        lane_line = prune_lane(root, name)
        if lane_line:
            print(lane_line)
    handoff = Path(d['handoff'])
    if not re.fullmatch(r'step-\d+', handoff.parent.name):
        return advance_ticket(d, attempt)
    import steps
    try:
        action, level, reason, _ = steps.next_action(handoff.parent)
    except steps.Fail as e:
        print(e, file=sys.stderr)
        return 1
    role = ADVANCE_ROLE.get(action)
    if role is None or level is None:
        print('stop: %s %s' % (action, reason))
        return 0
    if action == 'rebuild':
        previous_attempt(steps, handoff.parent, handoff)
    os.environ.setdefault('SDLC_ROUTING_REASON', 'dispatch.py advance: steps.py next %s L%d: %s' % (action, level, reason))
    top = git('rev-parse', '--show-toplevel', cwd=handoff.parent).stdout.strip()
    tree = d['tree'] if top and os.path.realpath(d['tree']) != os.path.realpath(top) else ''
    out = prepare(role, 'L%d' % level, str(handoff), tree=tree)
    print(json.dumps(out, indent=2))
    return 0


def close_line(task_dir):
    return 'next: close %s (python3 %s close %s)' % (task_dir, HERE / 'tickets.py', task_dir)


def advance_solo(d):
    """A recorded solo (T-0688): an L2 or L3 solo carries a `verifier` command, so prepare the ticket verifier at the
    steps.ticket_verifier level against the solo's tree and print its dispatch JSON; an L1 solo prints the close line."""
    handoff = Path(d['handoff'])
    if not d.get('verifier'):
        print(close_line(handoff.parent))
        return 0
    import steps
    level, reason = steps.ticket_verifier(handoff.read_text(encoding='utf-8'))
    os.environ.setdefault('SDLC_ROUTING_REASON', 'dispatch.py advance: solo %s done; ticket verifier %s: %s' % (d.get('tier') or d.get('level'), level, reason))
    top = git('rev-parse', '--show-toplevel', cwd=handoff.parent).stdout.strip()
    tree = d.get('tree') or ''
    if tree and top and os.path.realpath(tree) == os.path.realpath(top):
        tree = ''
    model = d.get('model') if d.get('model') in ('sonnet', 'opus', 'fable', 'haiku') else ''
    print(json.dumps(prepare('verifier', level, str(handoff), solo=model, tree=tree), indent=2))
    return 0


def advance_ticket(d, attempt):
    """A recorded role whose handoff is outside a step-<n>/ dir (T-0688): a ticket verifier pass prints the close line,
    a fail prints stop: fail; a ui-designer review prints its verdict; any other role keeps the next: <hint> line."""
    task, result = Path(d['handoff']).parent, d['result']
    word = verdict_word(d, attempt)
    if d['role'] == 'verifier' and word == 'pass':
        print(close_line(task))
    elif d['role'] == 'verifier' and word == 'fail':
        print('stop: fail %s; send its ## For the next attempt to the solo by name, then advance the solo\'s dispatch again' % result)
    elif d['role'] == 'ui-designer' and word == 'review':
        verdict = results._key_body_value(results._lines(result), 'Verdict')[1].lower()
        print('next: %s %s' % (verdict, result) if verdict in ('pass', 'pass-with-notes') else 'stop: changes-required %s' % result)
    else:
        print('next: %s is not a step dir; read %s and pick the next role' % (task, result))
    return 0


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
    p.add_argument('--approved', metavar='"WHO: WHY"',
                   help='the person\'s approval of a planner run past the replan cap (T-0553) or a role on a ticket past its time budget (T-0555); '
                        'wins over SDLC_REPLAN_APPROVED and SDLC_TIME_APPROVED, recorded in skips.md')
    p.add_argument('--routing-reason', help='why this role and level; wins over SDLC_ROUTING_REASON (a command that starts with VAR=... misses a Bash(python3:*) allowlist)')
    pg = p.add_mutually_exclusive_group()
    pg.add_argument('--prune', dest='prune', action='store_true', default=None, help='queue this agent for pruning after a recorded result (the default for a one-shot role)')
    pg.add_argument('--no-prune', dest='prune', action='store_false', help='never queue this agent for pruning')
    p.add_argument('--notify', default='', metavar='RECEIVER', help='mailbox receiver that gets the verdict message when record closes the attempt (T-0383)')
    p.add_argument('--notify-re', default='', metavar='ID', help='with --notify: the message id the verdict answers')
    p.add_argument('--tree', default='', metavar='PATH',
                   help='the lane worktree a build runs in when its handoff lives in the primary checkout: Tree, the tmp prefix, and the Base sha follow it; '
                        'it must be a worktree of this repository, else exit 2 (T-0413)')
    for key in ('role', 'level', 'handoff'):
        p.add_argument(key)
    for r in (sub.add_parser('record', help='validate and record a dispatched role, and close its attempt'),
              sub.add_parser('advance', help='record, drop the pruned role from the queue, run steps.py next, and prepare the next role (T-0645)')):
        r.add_argument('dispatch', help='the <stem>.dispatch.json prepare wrote')
        r.add_argument('--agent-id', help='the sub-agent id the Agent tool returned')
        r.add_argument('--tokens', type=int, help='subagent_tokens from the completion notice')
        r.add_argument('--tool-uses', type=int, help='tool_uses from the completion notice')
        r.add_argument('--transcript', help='the sub-agent transcript (jsonl); its usage (input, output, cache read and write) prices the run (default with --agent-id: found under ~/.claude/projects)')
        r.add_argument('--duration-ms', type=int, help='duration_ms from the completion notice')
        r.add_argument('--no-result', action='store_true', help='close the attempt failed when no result file, stdin, or transcript result exists (default: exit 2 and leave it running)')
    dl = sub.add_parser('deliver', help='send (or confirm sent) the verdict message a dispatch asked for with --notify; idempotent')
    dl.add_argument('dispatch', help='the <stem>.dispatch.json prepare wrote')
    sd = sub.add_parser('started', help='store the spawned sub-agent id in the running attempt, so status can show its last activity')
    sd.add_argument('--agent-id', required=True, help='the sub-agent id the Agent tool returned')
    sd.add_argument('dispatch', help='the <stem>.dispatch.json prepare wrote')
    st = sub.add_parser('status', help='print each attempt in a handoff dir: running, completed, failed, orphaned, or interrupted')
    st.add_argument('directory')
    st.add_argument('--orphans', action='store_true', help='print only orphaned attempts')
    rc_ = sub.add_parser('recover', help='mark orphaned attempts interrupted')
    rc_.add_argument('directory', nargs='?', help='the handoff dir to recover')
    rc_.add_argument('--root', metavar='DIR', help='instead of a handoff dir: sweep every attempt under DIR/.sdlc (run once after a host or session restart)')
    rc_.add_argument('--open', action='store_true', help='with --root: leave ticket folders whose status is done or dropped untouched (the driver\'s form)')
    rs = sub.add_parser('resume', help='print the resume ladder for an orphaned attempt')
    rs.add_argument('name', help='the attempt stem or Agent name')
    rs.add_argument('--limit', action='store_true', help='mark a running attempt stopped by a spend or session limit limit-stopped and write its .limit marker (T-0537)')
    rs.add_argument('--root', default='.', help='where to search for attempt records')
    pr = sub.add_parser('prune', help='list the finished sub-agents to stop, with the stop call for each')
    pr.add_argument('--root', default='.', help='the project root holding .sdlc/runtime/prune.json')
    pg2 = pr.add_mutually_exclusive_group()
    pg2.add_argument('--done', metavar='NAME', help='remove NAME from the queue once it is stopped')
    pg2.add_argument('--add', metavar='NAME', help='queue NAME (a landed builder or solo)')
    pg2.add_argument('--forget-stale', action='store_true', help='drop the entries another session queued (T-0601)')
    pr.add_argument('--role', default='', help='with --add: the agent role')
    pr.add_argument('--level', default='', help='with --add: the agent level')
    sh_ = sub.add_parser('settle-held', help='record that the owner of a `deferred:` held criterion settled it with evidence (T-0684)')
    sh_.add_argument('result', help='the verifier result holding the criteria (Verdict fail, `deferred: <owner>` note)')
    sh_.add_argument('--by', required=True, metavar='OWNER', help='the owner the criteria are deferred to, e.g. conductor')
    sh_.add_argument('--evidence', required=True, metavar='PATH', help='repo-relative evidence file; a review record needs Verdict pass or pass-with-notes')
    sh_.add_argument('--ref', action='append', default=[], metavar='REF', help='settle only this held ref (ticket#3, step-1#2, #3); repeatable; default every ref deferred to --by')
    sub.add_parser('selftest', help='run the regression cases in temp repos')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    plugin_min.warn_stale()  # T-0679: one stderr line when a newer plugin version is installed
    if args.cmd == 'settle-held':
        try:
            add = settle_held(args.result, args.by, args.evidence, args.ref)
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
        print('\n'.join(add) if add else 'settle-held: already settled, nothing written')
        return 0
    if args.cmd == 'prune':
        try:
            if args.done:
                print('pruned: ' + args.done if prune_done(args.root, args.done) else 'not queued: ' + args.done)
                lane_line = prune_lane(args.root, args.done)
                if lane_line:
                    print(lane_line)
            elif args.add:
                busy = running_attempt(args.root, args.add)
                if busy:
                    print('dispatch.py: %s has a running attempt %s; record it before queueing it for pruning' % (args.add, busy), file=sys.stderr)
                    return 2
                prune_add(args.root, args.add, args.role, args.level)
                print('queued: ' + args.add)
            elif args.forget_stale:
                gone = prune_forget_stale(args.root)
                print('\n'.join('forgot: ' + n for n in gone) if gone else 'forgot: nothing')
            else:
                print('\n'.join(prune_lines(args.root)))
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
        except OSError as e:
            print('dispatch.py: ' + str(e), file=sys.stderr)
            return 2
        return 0
    if args.cmd == 'started':
        try:
            return started(args.dispatch, args.agent_id)
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
    if args.cmd == 'deliver':
        try:
            return deliver(args.dispatch)
        except (OSError, ValueError, KeyError) as e:
            print('dispatch.py: cannot deliver from %s: %s' % (args.dispatch, e), file=sys.stderr)
            return 2
    if args.cmd in ('status', 'recover', 'resume'):
        try:
            if args.cmd in ('status', 'recover') and getattr(args, 'directory', None):
                args.directory = handoff_records(args.directory)
            if args.cmd == 'status':
                out = status(args.directory, args.orphans)
            elif args.cmd == 'resume':
                out = limit_stop(args.name, args.root) if args.limit else resume(args.name, args.root)
            elif args.cmd == 'recover' and args.root:
                if args.directory:
                    print('dispatch.py: recover takes a handoff dir or --root, not both', file=sys.stderr)
                    return 2
                out = recover_root(args.root, args.open)
            elif args.cmd == 'recover' and not args.directory:
                print('dispatch.py: recover needs a handoff dir or --root DIR', file=sys.stderr)
                return 2
            else:
                out = (['marked interrupted: ' + n for n in recover_orphans(args.directory)[0]] or ['no orphaned attempts']) + over_budget_lines(args.directory)
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
        except OSError as e:
            print('dispatch.py: ' + str(e), file=sys.stderr)
            return 2
        print('\n'.join(out))
        return 0
    if args.cmd in ('record', 'advance'):
        if args.agent_id and not args.transcript:  # T-0446: no flag, find the sub-agent's own transcript; none found keeps the unpriced line
            args.transcript = find_subagent_transcript(args.agent_id)
        used = {k: v for k, v in (('subagent_tokens', args.tokens), ('tool_uses', args.tool_uses)) if v is not None}
        if args.transcript:  # T-0328: the notice count excludes cache reads; the transcript usage does not
            used = {**(cost_estimate.transcript_usage(args.transcript) or {}), **{k: v for k, v in used.items() if k != 'subagent_tokens'}} \
                if cost_estimate.transcript_usage(args.transcript) else used
        def rec():
            sd = solo_dispatch(args.dispatch)
            if sd:  # T-0350: a solo_run.py dispatch has no attempt file; recording it prices the row and clears the live marker
                if sd.get('result') and solo_report_file(sd, args.transcript):
                    return 2
                import solo_run
                cost = solo_run.complete(sd['artifacts_dir'], sd['attempt_id'], sd.get('tier') or 'L1', args.transcript, args.tokens,
                                         agent_id=args.agent_id, tool_uses=args.tool_uses, duration_ms=args.duration_ms)
                print('solo recorded%s; live marker cleared' % ('' if cost is None else ', cost_usd %s' % cost))
                return 0
            return record(args.dispatch, stdin=read_stdin, agent_id=args.agent_id, usage=used or None, duration_ms=args.duration_ms,
                          resolved_model=cost_estimate.transcript_model(args.transcript) if args.transcript else None,
                          transcript=args.transcript, no_result=args.no_result)
        try:
            return advance(args.dispatch, rec) if args.cmd == 'advance' else rec()
        except Refuse as r:
            for line in r.lines:
                print(line, file=sys.stderr)
            return r.rc
        except (OSError, ValueError) as e:
            print('dispatch.py: ' + str(e), file=sys.stderr)
            return 2
    if args.routing_reason is not None:
        os.environ['SDLC_ROUTING_REASON'] = args.routing_reason
    if args.approved is not None:
        os.environ['SDLC_REPLAN_APPROVED'] = os.environ['SDLC_TIME_APPROVED'] = args.approved
    try:
        out = prepare(args.role, args.level, args.handoff, dry_run=args.dry_run, solo=args.solo_model, prune=args.prune,
                      notify=args.notify, notify_re=args.notify_re, tree=args.tree)
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


@contextlib.contextmanager
def private_tmpdir(base):
    """Point the system temp dir (tempfile and $TMPDIR, for child processes too) at <base>/tmp, so the scratch root and
    its crash sweep see only this run's folders, never another run's under the real $TMPDIR/sdlc-lite (T-0558)."""
    d = Path(base) / 'tmp'
    d.mkdir(parents=True, exist_ok=True)
    saved = tempfile.tempdir, os.environ.get('TMPDIR')
    tempfile.tempdir, os.environ['TMPDIR'] = str(d), str(d)
    try:
        yield d
    finally:
        tempfile.tempdir = saved[0]
        if saved[1] is None:
            os.environ.pop('TMPDIR', None)
        else:
            os.environ['TMPDIR'] = saved[1]


def selftest():
    # where prepare, record and run.sh write a task's records; made when missing, which never changes the answer
    R = lambda p: order.records_dir(p, create=True)
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

    with tempfile.TemporaryDirectory(prefix='dispatch-selftest.') as tmp, private_tmpdir(os.path.realpath(tmp)):
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
            (R(sw) / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'builder', 'level': l, 'file': 'builder-%s.md' % l}) + '\n' for l in others + [newest]))
            for vlevel in ('L1', 'L2', 'L3'):
                same('verifier after builder %s' % newest, repo, 'verifier', vlevel, '.sdlc/t/step-1/handoff.md')
        rc, got = same('verifier swap value', repo, 'verifier', 'L2', '.sdlc/t/step-1/handoff.md')
        case('verifier L2 after an opus build keeps sonnet', got['model'] == 'sonnet')
        (R(sw) / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'builder', 'level': l, 'file': 'builder-%s.md' % l}) + '\n' for l in ('L3', 'L1')))
        rc, got = same('verifier swap value', repo, 'verifier', 'L2', '.sdlc/t/step-1/handoff.md')
        case('verifier L2 after a sonnet build moves to opus, same effort', (got['model'], got['effort']) == ('opus', 'high'))
        rc, got = same('verifier swap value', repo, 'verifier', 'L3', '.sdlc/t/step-1/handoff.md')
        case('verifier L3 after a sonnet build keeps fable', got['model'] == 'fable')
        (R(sw) / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'builder', 'level': l, 'file': 'builder-%s.md' % l}) + '\n' for l in ('L1', 'L5')))
        rc, got = same('verifier swap value', repo, 'verifier', 'L3', '.sdlc/t/step-1/handoff.md')
        case('verifier L3 after a fable build moves to opus xhigh', (got['model'], got['effort']) == ('opus', 'xhigh'))
        # T-0519: verifier L1 is opus low, so an opus build moves it to sonnet at the same effort; no other row moves.
        for label, blvl, bmod, vlevel, want in (('verifier L1 after an opus builder L1 result runs sonnet low', 'L1', 'opus', 'L1', ('sonnet', 'low')),
                                                ('verifier L2 after an opus builder L3 result keeps sonnet high', 'L3', 'opus', 'L2', ('sonnet', 'high')),
                                                ('verifier L3 after an opus builder L4 result keeps fable xhigh', 'L4', 'opus', 'L3', ('fable', 'xhigh')),
                                                ('verifier L3 after an opus builder L5 result keeps fable xhigh', 'L5', 'opus', 'L3', ('fable', 'xhigh')),
                                                ('verifier L2 after a sonnet builder L2 result runs opus high', 'L2', 'sonnet', 'L2', ('opus', 'high')),
                                                ('negative control: verifier L1 after a sonnet builder L2 result keeps opus low', 'L2', 'sonnet', 'L1', ('opus', 'low'))):
            for old in sw.glob('builder-*.md'):
                old.unlink()
            put(sw / ('builder-%s.md' % blvl), '<!-- role=builder level=%s model=%s effort=x -->\n' % (blvl, bmod))
            (R(sw) / 'runs.jsonl').write_text(json.dumps({'role': 'builder', 'level': blvl, 'file': 'builder-%s.md' % blvl}) + '\n')
            rc, got = same('T-0519 %s builder %s' % (bmod, blvl), repo, 'verifier', vlevel, '.sdlc/t/step-1/handoff.md')
            case('T-0519: ' + label, rc == 0 and (got['model'], got['effort']) == want)
        shutil.rmtree(sw)

        # 2b. A solo ticket has no builder result: the newest solo record in runs.jsonl holds the family (T-0284).
        so = sdlc / 'so'
        put(so / 'handoff.md')
        for smodel, level, want in (('sonnet', 'L2', 'opus'), ('sonnet', 'L1', 'opus'), ('opus', 'L2', 'sonnet'), ('sonnet', 'L3', 'fable')):
            (R(so) / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'level': 'L2', 'model': smodel}) + '\n')
            rc, got, _ = prep(repo, 'verifier', level, '.sdlc/so/handoff.md', '--dry-run')
            case('verifier %s after a %s solo gets %s' % (level, smodel, want), rc == 0 and got['model'] == want)
        (R(so) / 'runs.jsonl').unlink()
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run')
        case('verifier L2 with no solo record keeps sonnet', rc == 0 and got['model'] == 'sonnet')
        # T-0356: a sub-agent lane worktree holds no solo record, so fanout prep passes --solo-model
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run', '--solo-model', 'sonnet')
        case('verifier L2 with --solo-model sonnet and no record moves to opus, same effort', rc == 0 and (got['model'], got['effort']) == ('opus', 'high'))
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run', '--solo-model', 'opus')
        case('negative control: verifier L2 with --solo-model opus keeps sonnet', rc == 0 and got['model'] == 'sonnet')
        (R(so) / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'level': 'L3', 'model': 'opus'}) + '\n')
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run', '--solo-model', 'sonnet')
        case('the runs.jsonl solo record wins over --solo-model: an opus record keeps verifier L2 on sonnet', rc == 0 and got['model'] == 'sonnet')
        (R(so) / 'runs.jsonl').unlink()
        # T-0516: the solo L2 row is Opus medium (the builder ladder shifted down one), so its record keeps verifier L2 on sonnet
        l2m, l2e = json.loads((PLUGIN / 'adapters' / 'claude' / 'levels.json').read_text())['solo']['L2']
        (R(so) / 'runs.jsonl').write_text(json.dumps({'role': 'solo', 'level': 'L2', 'model': l2m}) + '\n')
        rc, got, _ = prep(repo, 'verifier', 'L2', '.sdlc/so/handoff.md', '--dry-run')
        case('solo L2 is opus medium and its record keeps verifier L2 on sonnet', (l2m, l2e) == ('opus', 'medium') and rc == 0 and got['model'] == 'sonnet')
        (R(so) / 'runs.jsonl').unlink()

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
                             ('task dir build wins over step dirs', lambda: (put(R(td) / 'builder-L3.md', '<!-- role=builder level=L3 model=opus effort=x -->\n'), build('step-1', 'L1', 'sonnet'))),
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
            for child in list(pr.iterdir()) + list(R(pr).iterdir()):
                if child.name != 'handoff.md' and child.is_file():
                    child.unlink()
            for lvl, mod in pairs:
                put(R(pr) / ('planner-%s.md' % lvl), '<!-- role=planner level=%s model=%s effort=x -->\n' % (lvl, mod))
            (R(pr) / 'runs.jsonl').write_text(''.join(json.dumps({'role': 'planner', 'level': l, 'file': 'planner-%s.md' % l}) + '\n' for l, _ in pairs))
        planners()
        _, got = same('plan-reviewer, no planner', repo, 'plan-reviewer', 'L1', '.sdlc/pr/handoff.md')
        case('plan-reviewer with no planner keeps fable high', (got['model'], got['effort']) == ('fable', 'high'))
        for label, pairs, want in (('sonnet planner', [('L1', 'sonnet')], 'fable'), ('fable planner', [('L2', 'fable')], 'opus'),
                                   ('opus planner', [('L3', 'opus')], 'fable'),
                                   ('opus planner then fable planner', [('L2', 'opus'), ('L3', 'fable')], 'opus'),
                                   ('fable planner then opus planner', [('L3', 'fable'), ('L2', 'opus')], 'fable')):
            planners(*pairs)
            _, got = same(label, repo, 'plan-reviewer', 'L1', '.sdlc/pr/handoff.md')
            case('plan-reviewer after %s runs %s' % (label, want), got['model'] == want)
        # T-0519: the plan-reviewer row is fable high; a fable planner result moves it to opus, same effort.
        planners()
        rc, got = same('T-0519 plan-reviewer, no planner', repo, 'plan-reviewer', 'L1', '.sdlc/pr/handoff.md')
        case('T-0519: plan-reviewer with no planner result runs fable high', rc == 0 and (got['model'], got['effort']) == ('fable', 'high'))
        planners(('L2', 'fable'))
        rc, got = same('T-0519 plan-reviewer, fable planner', repo, 'plan-reviewer', 'L1', '.sdlc/pr/handoff.md')
        case('T-0519: plan-reviewer after a fable planner result runs opus high', rc == 0 and (got['model'], got['effort']) == ('opus', 'high'))
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
            _, got = same('naming ' + want, repo, 'planner', 'L3', '.sdlc/nm/handoff.md', SDLC_REPLAN_APPROVED='selftest: naming')
            case('result name is ' + want, os.path.basename(got['result']) == want)
        shutil.rmtree(nm)

        # 6. Refusals: the same exit code as run.sh, nothing written (the audit log refusals.jsonl, T-0415, is the one
        # allowed write), and a negative control that
        # disables the one gate and lets the bad input through.
        def refused(label, rc_want, role, level, rel, gate, **env):
            before = sorted(str(p) for p in repo.rglob('*') if '.git' not in p.parts and p.name != 'refusals.jsonl')
            rc, got, err = prep(repo, role, level, rel, **env)
            rrc = runsh(repo, role, level, rel, **env)[0]
            case('%s: prepare exits %d like run.sh (got %d, run.sh %d)' % (label, rc_want, rc, rrc), rc == rc_want == rrc)
            case('%s: a refusal wrote nothing' % label, before == sorted(str(p) for p in repo.rglob('*') if '.git' not in p.parts and p.name != 'refusals.jsonl'))
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

        # replan cap (T-0553): two planner results (the first plan and the one replan) stop a third planner run until the
        # person approves; --approved (or SDLC_REPLAN_APPROVED, run.sh's form) lets it through and records the approval.
        rp = sdlc / 'rp'
        put(rp / 'handoff.md', '## Goal\nx\n')
        put(rp / 'planner-L3.md', '## Goal\n')
        case('replan cap: a second planner run (one planner result) passes', prep(repo, 'planner', 'L3', '.sdlc/rp/handoff.md', '--dry-run')[0] == 0)
        put(rp / 'planner-L3-2.md', '## Goal\n')
        err = refused('replan cap: a third planner run', 2, 'planner', 'L3', '.sdlc/rp/handoff.md', 'replan')
        case('replan cap: the refusal names the count and the approval flag',
             'holds 2 planner results' in err and 'planner run 3' in err and '--approved "<who: why>"' in err)
        rc, _, err = prep(repo, 'planner', 'L3', '.sdlc/rp/handoff.md', '--dry-run', '--approved', 'yes')
        case('replan cap: --approved needs "<who: why>"', rc == 2 and '<who: why>' in err)
        rc, _, _ = prep(repo, 'planner', 'L3', '.sdlc/rp/handoff.md', '--dry-run', '--approved', 'maintainer: one more pass')
        case('replan cap: a dry run with --approved passes and records nothing', rc == 0 and not (rp / 'skips.md').exists())
        rrc = runsh(repo, 'planner', 'L3', '.sdlc/rp/handoff.md', SDLC_REPLAN_APPROVED='maintainer: one more pass')[0]
        case('replan cap: run.sh passes with SDLC_REPLAN_APPROVED like prepare --approved', rrc == 0)
        rc, got, _ = prep(repo, 'planner', 'L3', '.sdlc/rp/handoff.md', '--approved', 'maintainer: one more pass')
        case('replan cap: --approved lets planner run 3 through and records it in skips.md',
             rc == 0 and (rp / 'skips.md').is_file() and (rp / 'skips.md').read_text(encoding='utf-8') == 'replan approved: planner run 3: maintainer: one more pass\n')
        put(rp / 'planner-L3-3.md', '## Goal\n')
        case('replan cap: a fourth planner run needs its own approval', prep(repo, 'planner', 'L3', '.sdlc/rp/handoff.md', '--dry-run')[0] == 2)
        put(rp / 'step-1' / 'handoff.md', '## Task goal\nx\n')
        case('replan cap: step handoffs are not planner runs and other roles are not capped',
             prep(repo, 'plan-reviewer', 'L1', '.sdlc/rp/handoff.md', '--dry-run')[0] == 0)
        shutil.rmtree(rp)

        # unfilled handoff (T-0399): a ticket handoff still holding its type template's prompt text or Goal default is
        # refused before any verifier or planner runs on it; a filled one passes. run.sh has no such gate, so no parity.
        uf = sdlc / 'uf'
        for kind in ('bug', 'feature'):
            put(uf / 'handoff.md', (PLUGIN / 'skills' / 'ticket' / 'templates' / (kind + '.md')).read_text(encoding='utf-8'))
            for role in ('verifier', 'planner'):
                rc, _, err = prep(repo, role, 'L1', '.sdlc/uf/handoff.md', '--dry-run')
                case('unfilled %s template: prepare %s exits 2 naming the file and the placeholder' % (kind, role),
                     rc == 2 and '.sdlc/uf/handoff.md:' in err and 'unfilled template text' in err and len(err.strip().splitlines()) == 1)
            with clean_env(), cwd(repo), contextlib.redirect_stderr(io.StringIO()):
                passed = prepare('verifier', 'L1', '.sdlc/uf/handoff.md', dry_run=True, skip=('unfilled',))
            case('unfilled %s template: negative control, without the unfilled gate it goes through' % kind, bool(passed))
        ticket(uf, 'L2')
        case('a filled ticket handoff still passes prepare', prep(repo, 'verifier', 'L1', '.sdlc/uf/handoff.md', '--dry-run')[0] == 0)
        put(uf / 'handoff.md', (PLUGIN / 'skills' / 'ticket' / 'templates' / 'bug.md').read_text(encoding='utf-8')
            .replace('The bug is fixed and a test that failed before the fix passes after it.', 'prepare mislabels x.')
            .replace('1. Exact command or steps, from a clean checkout.', '1. run x').replace('Paste the output or error verbatim.', 'boom')
            .replace('Where it was found (file:line, story id, session). Suspected cause, marked as a guess.', 'here'))
        case('a bug ticket that keeps the Constraints default but fills the rest passes',
             prep(repo, 'verifier', 'L1', '.sdlc/uf/handoff.md', '--dry-run')[0] == 0)
        shutil.rmtree(uf)

        # link check (T-0379): a builder or verifier on a step handoff that cites a prior attempt's report at the live
        # step path, or a path that does not exist, is refused before any record; the superseded path passes
        lk = sdlc / 'lk'
        put(lk / 'step-3.superseded-1' / 'builder-L3.md', '## Status\ndone\n')  # the cited path steps.py lint checks
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

        # repo skills (T-0648): a builder whose step scope names a path an AGENTS.md routes to a repo skill gets the
        # Repo skills line; a step scoped to an unrouted path gets none
        rs = tmp / 'rs'
        init_repo(rs)
        put(rs / 'AGENTS.md', '# Repo\n\n- `src/styles/` uses `.agents/skills/recipe/SKILL.md`\n')
        put(rs / '.agents' / 'skills' / 'recipe' / 'SKILL.md', 'x\n')
        put(rs / '.sdlc' / 'rs' / 'handoff.md')
        for path, want in (('src/styles/a.css', True), ('src/other.css', False)):
            put(rs / '.sdlc' / 'rs' / 'step-1' / 'handoff.md',
                '## Task goal\ng\n\n## Step 1: First thing\nlevel: L2\n### Read first\n- `.agents/skills/recipe/SKILL.md`\n'
                '### Do\nDo one.\n\n### Acceptance criteria\n- `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; '
                'git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e %s | { ! grep -q .; }`\n' % path)
            rc, got, err = prep(rs, 'builder', 'L1', '.sdlc/rs/step-1/handoff.md', '--dry-run')
            line = '\nRepo skills for this step: .agents/skills/recipe/SKILL.md\n'
            case('repo skills: a builder scoped to %s %s the Repo skills line' % (path, 'gets' if want else 'does not get'),
                 rc == 0 and ((line in got['prompt']) if want else 'Repo skills for this step' not in got['prompt']))

        # lane guidance (T-0655): in a linked worktree, an AGENTS.md that differs from the main checkout's adds a Guidance
        # line, and a handoff naming a guidance path absent from the lane refuses, exit 5, before any record is written
        gm = tmp / 'gm'
        init_repo(gm)
        put(gm / 'AGENTS.md', '# Repo\n')
        subprocess.run(['git', '-C', str(gm), 'add', '-A'], check=True)
        subprocess.run(['git', '-C', str(gm), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                        'commit', '-qm', 'guidance'], check=True)
        gl = tmp / 'gm-lane'
        subprocess.run(['git', '-C', str(gm), 'worktree', 'add', '-q', '-b', 'lane-g', str(gl), 'HEAD'], check=True, capture_output=True)
        put(gm / '.agents' / 'skills' / 'x' / 'SKILL.md', 'x\n')
        put(gl / '.sdlc' / 'g' / 'handoff.md')
        rc, got, err = prep(gl, 'scout', 'L1', '.sdlc/g/handoff.md', '--dry-run')
        case('lane guidance: a lane whose AGENTS.md matches main gets no Guidance line and no differs line',
             rc == 0 and 'Guidance: ' not in got['prompt'] and 'lane guidance differs' not in err)
        put(gl / 'AGENTS.md', '# Repo\n\nlane rule\n')
        rc, got, err = prep(gl, 'scout', 'L1', '.sdlc/g/handoff.md', '--dry-run')
        case('lane guidance: a lane AGENTS.md that differs from main adds the Guidance line and says so on stderr',
             rc == 0 and '\nGuidance: read %s/AGENTS.md; it overrides the auto-attached main checkout copy' % os.path.realpath(str(gl)) in got['prompt']
             and 'lane guidance differs: AGENTS.md' in err and 'differs: CLAUDE.md' not in err)
        put(gl / '.sdlc' / 'g' / 'handoff.md', '## Goal\nx\n\n## Context\n- Read `.agents/skills/x/SKILL.md` first.\n')
        rc, _, err = prep(gl, 'scout', 'L1', '.sdlc/g/handoff.md')
        written = [p.name for p in (gl / '.sdlc').rglob('*') if p.name.endswith(('.attempt.json', '.dispatch.json', '.running'))]
        case('lane guidance: a handoff naming a skill on main but not in the lane refuses, exit 5, and writes no record',
             rc == 5 and 'guidance missing in lane: .agents/skills/x/SKILL.md (present on' in err and not written)
        put(gl / '.agents' / 'skills' / 'x' / 'SKILL.md', 'x\n')
        rc, _, err = prep(gl, 'scout', 'L1', '.sdlc/g/handoff.md', '--dry-run')
        case('lane guidance: the same handoff with the skill present in the lane passes', rc == 0 and 'guidance missing' not in err)
        put(gl / '.sdlc' / 'g' / 'handoff.md', '## Goal\nx\n\n## Context\n- Read `skills/nowhere/SKILL.md` first.\n')
        rc, _, err = prep(gl, 'scout', 'L1', '.sdlc/g/handoff.md', '--dry-run')
        case('lane guidance: a guidance path absent from the lane, main and into branch does not refuse (T-0674)',
             rc == 0 and 'guidance missing' not in err)
        put(gm / '.sdlc' / 'g' / 'handoff.md', '## Goal\nx\n\n## Context\n- Read `.claude/skills/none/SKILL.md` first.\n')
        rc, got, err = prep(gm, 'scout', 'L1', '.sdlc/g/handoff.md', '--dry-run')
        case('lane guidance: the main checkout is never checked', rc == 0 and 'Guidance: ' not in got['prompt'] and 'guidance' not in err)
        subprocess.run(['git', '-C', str(gm), 'worktree', 'remove', '--force', str(gl)], capture_output=True)

        put(sdlc / 'sg' / 'handoff.md')  # spec gate
        put(R(sdlc / 'sg') / 'planner-L1.md', SGPLAN)
        err = refused('spec gate', 2, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', 'specgate')
        case('spec gate names the finding and the way out', 'slow guard' in err and 'SDLC_SPECGATE=off' in err)
        rc, got, err = prep(repo, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', '--dry-run', SDLC_SPECGATE='off')
        case('SDLC_SPECGATE=off lets it through and is carried', rc == 0 and got['specgate'] == 'off' and 'spec gate skipped' in err)
        rc, got, err = prep(repo, 'plan-reviewer', 'L1', '.sdlc/sg/handoff.md', '--dry-run')
        case('without the knob the spec gate still refuses', rc == 2)
        put(R(sdlc / 'sg') / 'planner-L1.md', SGPLAN.replace('## Step 1: Gates', 'guard timeout: 900\n\n## Step 1: Gates'))
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
            (R(sdlc / 'ls') / f).unlink()
        prep(repo, 'planner', 'L1', '.sdlc/ls/handoff.md', SDLC_LANE_OVERRIDE='chain needs a merge step')
        case('the override line is appended once', skips.read_text().count('lane override:') == 1)
        for f in list((R(sdlc / 'ls')).glob('planner-L1*')):
            f.unlink()

        ticket(sdlc / 'bg', 'L2', budget_usd=10)  # budget gate (verifier: not lane gated)
        put(R(sdlc / 'bg') / 'runs.jsonl', json.dumps({'role': 'builder', 'cost_usd': 9, 'attempt_id': 'a1'}) + '\n')
        err = refused('budget gate', 4, 'verifier', 'L1', '.sdlc/bg/handoff.md', 'budget')
        case('budget gate names the percent and budget.py ack', '90%' in err and 'budget.py ack' in err)
        put(sdlc / 'bg' / 'budget-ack.md', '---\nusd: 30\nreason: selftest\n---\n')
        case('a budget ack raises the ceiling and it passes', prep(repo, 'verifier', 'L1', '.sdlc/bg/handoff.md', '--dry-run')[0] == 0)
        (sdlc / 'bg' / 'budget-ack.md').unlink()
        put(R(sdlc / 'bg') / 'runs.jsonl', json.dumps({'role': 'builder', 'cost_usd': 1, 'attempt_id': 'a1'}) + '\n')
        case('under 80 percent passes', prep(repo, 'verifier', 'L1', '.sdlc/bg/handoff.md', '--dry-run')[0] == 0)
        ticket(sdlc / 'bn', 'L2')
        case('a ticket with no budget passes', prep(repo, 'verifier', 'L1', '.sdlc/bn/handoff.md', '--dry-run')[0] == 0)

        # time budgets (T-0555). A ticket past its agent-time budget for its size refuses the next role until the person
        # approves; each approval allows one more budget. run.sh has no time gate, so no parity.
        tt = sdlc / 'tt'
        ticket(tt, 'L1')
        put(R(tt) / 'runs.jsonl', json.dumps({'role': 'solo', 'level': 'L1', 'duration_ms': 40 * 60000, 'attempt_id': 't1'}) + '\n')
        case('time budget: a ticket inside its budget passes', prep(repo, 'verifier', 'L1', '.sdlc/tt/handoff.md', '--dry-run')[0] == 0)
        put(R(tt) / 'verifier-L1.attempt.json', json.dumps({'attempt_id': 't2', 'status': 'completed', 'role': 'verifier', 'level': 'L1',
                                                             'started_at': '2026-10-14T10:00:00+00:00', 'finished_at': '2026-10-14T10:30:00+00:00'}))
        before = sorted(str(p) for p in repo.rglob('*') if '.git' not in p.parts)
        rc, _, err = prep(repo, 'verifier', 'L1', '.sdlc/tt/handoff.md')
        case('time budget: a ticket past its budget (a 40m run row and a 30m attempt) refuses the next role, exit 2, naming the minutes and --approved',
             rc == 2 and 'time budget:' in err and '70m' in err and '60m' in err and '--approved "<who: why>"' in err)
        case('time budget: the refusal wrote nothing', before == sorted(str(p) for p in repo.rglob('*') if '.git' not in p.parts))
        with clean_env(), cwd(repo), contextlib.redirect_stderr(io.StringIO()):
            try:
                passed = prepare('verifier', 'L1', '.sdlc/tt/handoff.md', dry_run=True, skip=('time',))
            except Refuse:
                passed = None
        case('time budget: negative control, without the time gate the ticket past its budget goes through', bool(passed))
        rc, _, err = prep(repo, 'verifier', 'L1', '.sdlc/tt/handoff.md', '--dry-run', '--approved', 'yes')
        case('time budget: --approved needs "<who: why>"', rc == 2 and '<who: why>' in err)
        rc, _, _ = prep(repo, 'verifier', 'L1', '.sdlc/tt/handoff.md', '--dry-run', '--approved', 'maintainer: finish the verify')
        case('time budget: a dry run with --approved passes and records nothing', rc == 0 and not (tt / 'skips.md').exists())
        rc, _, _ = prep(repo, 'verifier', 'L1', '.sdlc/tt/handoff.md', '--approved', 'maintainer: finish the verify')
        case('time budget: --approved lets the role through and records it once in skips.md',
             rc == 0 and (tt / 'skips.md').is_file() and (tt / 'skips.md').read_text(encoding='utf-8') == 'time budget approved: 70m of 60m: maintainer: finish the verify\n')
        case('time budget: after an approval the next role passes inside one more budget',
             prep(repo, 'scout', 'L1', '.sdlc/tt/handoff.md', '--dry-run')[0] == 0)
        with (R(tt) / 'runs.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps({'role': 'solo', 'level': 'L1', 'duration_ms': 60 * 60000, 'attempt_id': 't3'}) + '\n')
        rc, _, err = prep(repo, 'scout', 'L1', '.sdlc/tt/handoff.md', '--dry-run')
        case('time budget: past the approved budget too, the next role needs a new approval', rc == 2 and '130m' in err)
        shutil.rmtree(tt)
        shutil.rmtree(R(tt))

        # A running attempt past its role's wall-clock budget is flagged by status and recover; one inside it is not.
        def at(offset, fn, *a):
            real = time.time
            time.time = lambda: real() + offset
            try:
                return fn(*a)
            finally:
                time.time = real
        tr = tmp / 'tr'
        init_repo(tr)
        put(tr / '.sdlc' / 'ob' / 'handoff.md')
        rc, ob, _ = prep(tr, 'builder', 'L2', '.sdlc/ob/handoff.md', SDLC_DISPATCH_PARENT_PID=str(os.getpid()))
        case('time budget: the brief names the role budget and the attempt stores it',
             rc == 0 and '\nTime budget: 15m wall clock for builder L2' in ob['prompt']
             and json.loads(Path(ob['attempt_file']).read_text()).get('time_budget_min') == 15)
        late = at(16 * 60, status, R(tr / '.sdlc' / 'ob'))
        case('time budget: status flags a running attempt past its role budget', len(late) == 1 and ' running ' in late[0] and late[0].endswith(' over-budget 16m (budget 15m)'))
        case('negative control: status leaves a running attempt inside its budget unflagged', 'over-budget' not in status(R(tr / '.sdlc' / 'ob'))[0])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            at(16 * 60, main, ['recover', str(tr / '.sdlc' / 'ob')])
        case('time budget: recover names the attempt past its budget and the check to make',
             'over-budget: builder-L2 running 16m, budget 15m' in out.getvalue() and 'stdin' in out.getvalue())
        rec = at(16 * 60, recover_root, str(tr))
        case('time budget: recover --root names it too', any(l.startswith('over-budget: ') and 'builder-L2' in l for l in rec))
        case('negative control: recover --root flags nothing inside the budget', not any('over-budget' in l for l in recover_root(str(tr))))

        # T-0690: status from a task folder lists the step-<n> attempts in its records dir, and says so when a dir holds none.
        put(tr / '.sdlc' / 'sx' / 'handoff.md')
        put(R(tr / '.sdlc' / 'sx') / 'step-1' / 'verifier-L2.attempt.json', json.dumps({'attempt_id': 'sx1', 'status': 'completed', 'role': 'verifier', 'level': 'L2'}))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = main(['status', str(tr / '.sdlc' / 'sx')])
        case('status: a task folder lists the attempt in its records step-1 dir as step-1/<stem>',
             rc == 0 and out.getvalue().splitlines() == ['step-1/verifier-L2 completed verifier-L2 parent_pid=None'])
        (tr / '.sdlc' / 'none').mkdir()
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = main(['status', str(tr / '.sdlc' / 'none')])
        case('status: a dir with no attempts prints no attempts in <dir> and names the records dir',
             rc == 0 and out.getvalue().startswith('no attempts in %s; try %s' % (tr / '.sdlc' / 'none', R(tr / '.sdlc' / 'none'))))
        case('negative control: status --orphans on a dir with no attempts prints no such line', status(str(tr / '.sdlc' / 'none'), True) == [])

        # preflight: handoff, row, git work tree, commit, generated definition, skills.
        case('preflight: a missing handoff exits 2 like run.sh', prep(repo, 'builder', 'L1', '.sdlc/none/handoff.md')[0] == 2
             == runsh(repo, 'builder', 'L1', '.sdlc/none/handoff.md')[0])
        case('preflight: an unknown row exits 2 like run.sh', prep(repo, 'builder', 'L9', '.sdlc/t/handoff.md')[0] == 2
             == runsh(repo, 'builder', 'L9', '.sdlc/t/handoff.md')[0])
        case('preflight: solo is not a pipeline row', prep(repo, 'solo', 'L2', '.sdlc/t/handoff.md')[0] == 2)
        rc, _, err = prep(repo, 'solo', 'L2', '.sdlc/t/handoff.md')  # T-0394: the refusal names how to start a solo ticket
        case('preflight: the solo refusal names the solo_run.py and fanout.py prep paths', 'solo_run.py run --task-dir' in err and 'fanout.py prep' in err)
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
        case('prepare exits 0 and writes both records', rc == 0 and (R(w) / 'builder-L1.attempt.json').is_file() and (R(w) / 'builder-L1.dispatch.json').is_file())
        stamp = (R(w) / 'builder-L1.running').read_text() if (R(w) / 'builder-L1.running').is_file() else ''
        case('prepare writes the running marker with an epoch start (T-0505)',
             rc == 0 and re.fullmatch(r'[0-9]+\n', stamp) is not None and abs(int(stamp) - time.time()) < 600)
        att = json.loads((R(w) / 'builder-L1.attempt.json').read_text())
        case('attempt record: running, subagent transport, parent pid',(att['status'], att['transport'], att['parent_pid'], att['backend']) == ('running', 'subagent', live, 'claude'))
        case('attempt record carries the model, effort, handoff hash, and reason',
             (att['model'], att['effort'], att['routing_reason']) == ('opus', 'low', 'selftest reason')
             and att['handoff_sha256'] == hashlib.sha256((w / 'handoff.md').read_bytes()).hexdigest())
        disk = json.loads((R(w) / 'builder-L1.dispatch.json').read_text())
        case('dispatch file equals the printed JSON apart from dry_run', disk == got and got['dry_run'] is False)
        for key in ('subagent_type', 'model', 'effort', 'name', 'result', 'tmp_prefix', 'base_sha', 'prompt'):
            case('dispatch JSON has %s' % key, key in got and got[key] is not None)
        case('subagent type, Agent name, and result path', got['subagent_type'] == 'sdlc-lite:builder-L1' and got['name'] == 'w-builder-L1'
             and got['result'] == str(R(w) / 'builder-L1.md') and os.path.realpath(got['tmp_prefix']) == os.path.realpath(str(rr.parent / 'rr.worktrees' / 'tmp' / 'w-builder-L1')))
        head = subprocess.run(['git', '-C', str(rr), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        case('a builder gets its base sha, in the dispatch, base-sha, and the brief',
             got['base_sha'] == head and (R(w) / 'base-sha').read_text() == head + '\n' and 'Base sha: ' + head in got['prompt'])
        case('the brief is the run.sh Handoff and Artifacts dir lines, then the Report file and pointer lines (T-0646), then the tree and tmp prefix lines',
             got['prompt'].startswith('w | builder L1\nHandoff: %s\nArtifacts dir: %s\nReport file: %s (before you end, write your result to exactly this path '
                                      % (w / 'handoff.md', R(w), R(w) / 'builder-L1.md'))
             and '\nEnd with one line: `builder <status> %s` (status is your Status or Verdict value, else done), nothing else.\nTree: ' % (R(w) / 'builder-L1.md') in got['prompt']
             and 'Tree: %s' % rr in got['prompt'] and 'Throwaway worktrees only under %s' % got['tmp_prefix'] in got['prompt'])
        own = json.loads((Path(got['tmp_prefix']) / '.owner.json').read_text())
        case('T-0550 the tmp prefix and the scratch dir hold an owner marker: the session pid, the running marker, the role',
             own['pid'] == live and own['running'] == str(R(w) / 'builder-L1.running') and own['role'] == 'builder-L1'
             and (Path(got['scratch']) / '.owner.json').is_file())
        case('T-0550 scratch sits under the system temp dir, not the repo, and the brief names it',
             got['scratch'].startswith(tempfile.gettempdir()) and not under(got['scratch'], str(rr))
             and 'Scratch files that are not worktrees (probe files, mutated copies) only under %s' % got['scratch'] in got['prompt'])
        case('T-0702 the brief bounds file searches to Tree and the Artifacts dir, on its own line',
             ('\n' + SEARCH_SCOPE) in got['prompt'] and SEARCH_SCOPE.startswith('Search only inside Tree ') and 'Artifacts dir' in SEARCH_SCOPE)
        # T-0504: a repository and task path with spaces still passes the actual spawn hook; a missing record is still denied.
        if shutil.which('jq') and shutil.which('bash'):
            sp = tmp / 'with spaces' / 'repo sp'
            init_repo(sp)
            put(sp / '.sdlc' / 'a task' / 'handoff.md')
            rcp, gp, _ = prep(sp, 'builder', 'L1', '.sdlc/a task/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live))
            hook = str(PLUGIN / 'hooks' / 'block-role-spawn.sh')

            def spawn(d, prompt=None):
                payload = json.dumps({'tool_name': 'Agent', 'cwd': str(sp), 'agent_type': 'sdlc-lite:conductor', 'tool_input': {
                    'subagent_type': d['subagent_type'], 'name': d['name'], 'model': d['model'], 'prompt': prompt or d['prompt']}})
                h = subprocess.run(['bash', hook], input=payload, capture_output=True, text=True)
                return h.returncode, h.stderr
            hrc, herr = spawn(gp) if rcp == 0 else (None, '')
            case('a prepared payload for a path with spaces passes the spawn hook unchanged', rcp == 0 and ' ' in gp['handoff'] and hrc == 0)
            case('the Handoff line of a spaced path is one quoted locator', rcp == 0 and ('\nHandoff: "%s"\n' % gp['handoff']) in gp['prompt'])
            case('trailing explanation after the quoted locator is ignored',
                 rcp == 0 and spawn(gp, gp['prompt'].replace('"%s"' % gp['handoff'], '"%s" (frozen, see docs/a b.md)' % gp['handoff'], 1))[0] == 0)
            case('the execution-tree command quotes a path with spaces', rcp == 0 and 'cd %s && ' % shlex.quote(gp['tree']) in gp['prompt'] and "cd '" in gp['prompt'])
            (R(sp / '.sdlc' / 'a task') / 'builder-L1.dispatch.json').unlink()
            mrc, merr = spawn(gp) if rcp == 0 else (None, '')
            case('a spaced path with no dispatch record is denied with the missing-record diagnostic',
                 mrc == 2 and 'no dispatch record for' in merr and gp['handoff'] in merr)
        else:
            print('skip: no jq or bash for the spaced-path spawn hook cases')
        # T-0366: a solo dispatch's recorded base sha, not the later HEAD, is the verifier's Base sha.
        put(rr / '.sdlc' / 'sb' / 'handoff.md')
        pre = subprocess.run(['git', '-C', str(rr), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        (R(rr / '.sdlc' / 'sb') / 'solo-L1-sb.dispatch.json').write_text(json.dumps({'role': 'solo', 'base_sha': pre}))
        (rr / 'later.txt').write_text('x')
        subprocess.run(['git', '-C', str(rr), 'add', '-A'], capture_output=True)
        subprocess.run(['git', '-C', str(rr), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'later'], capture_output=True)
        rcs, ds, _ = prep(rr, 'verifier', 'L1', '.sdlc/sb/handoff.md', '--dry-run')
        case('prepare verifier prints the solo dispatch base sha, not the later HEAD',
             rcs == 0 and ds['base_sha'] == pre and 'Base sha: ' + pre in ds['prompt'])
        # T-0590: a ticket with a ready ref: the verifier gets Review sha (the ready sha) and Base sha from its snapshot's
        # Lane-Base: line, not the later HEAD; a tree edited after ready is flagged stale; no ref, neither.
        import lanes
        put(rr / '.sdlc' / 'rd' / 'handoff.md', '---\nid: T-0950\ntitle: "ready"\n---\n\n## Goal\nx\n')
        ci = ['git', '-C', str(rr), '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm']
        subprocess.run(['git', '-C', str(rr), 'add', '-A'], capture_output=True)
        subprocess.run(ci + ['rd start'], capture_output=True)
        start = subprocess.run(['git', '-C', str(rr), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        (rr / 'rd-done.txt').write_text('committed\n')
        subprocess.run(['git', '-C', str(rr), 'add', 'rd-done.txt'], capture_output=True)
        subprocess.run(ci + ['rd work'], capture_output=True)
        (rr / 'rd.txt').write_text('uncommitted\n')
        with clean_env():
            rsha = lanes.pin(rr, 'T-0950', 'rd', start)[0]
        subprocess.run(['git', '-C', str(rr), 'update-ref', READY_REFS + 'T-0950', rsha], capture_output=True)
        rcr, dr, er = prep(rr, 'verifier', 'L1', '.sdlc/rd/handoff.md', '--dry-run')
        case('prepare verifier for a ticket with a ready ref: Review sha is the ready sha, Base sha its Lane-Base start, not HEAD',
             rcr == 0 and dr['review_sha'] == rsha and 'Review sha: ' + rsha in dr['prompt'] and dr['base_sha'] == start
             and 'Base sha: ' + start in dr['prompt'] and 'is stale' not in er)
        (rr / 'rd.txt').write_text('edited after ready\n')
        rcr, dr, er = prep(rr, 'verifier', 'L1', '.sdlc/rd/handoff.md', '--dry-run')
        case('a tree edited after ready: prepare says the ready ref is stale and still names the ready sha',
             rcr == 0 and 'T-0950 is stale' in er and 'Review sha: ' + rsha in dr['prompt'])
        subprocess.run(['git', '-C', str(rr), 'update-ref', '-d', READY_REFS + 'T-0950'], capture_output=True)
        rcr, dr, er = prep(rr, 'verifier', 'L1', '.sdlc/rd/handoff.md', '--dry-run')
        case('negative control: with no ready ref there is no Review sha line and Base sha is not the Lane-Base start',
             rcr == 0 and 'Review sha' not in dr['prompt'] and dr['review_sha'] is None and dr['base_sha'] != start)
        # T-0591: the verifier brief carries the run rules the conductor used to add by hand.
        case('a prepared verifier prompt says the build may be uncommitted, foreground only with a timeout, no full check.sh, no git stash',
             rcr == 0 and all(s in dr['prompt'] for s in (
                 'The build may be uncommitted', 'Run every command in the foreground with an explicit Bash timeout under 600000 ms',
                 'never run_in_background or Monitor', 'Never run the full check.sh', 'Never use git stash')))
        (rr / 'rd.txt').unlink()
        lw = rr.parent / (rr.name + '-lane')
        subprocess.run(['git', '-C', str(rr), 'worktree', 'add', '-q', '--detach', str(lw), 'HEAD'], capture_output=True)
        (lw / '.sdlc' / 'w').mkdir(parents=True, exist_ok=True)
        shutil.copy(rr / '.sdlc' / 'w' / 'handoff.md', lw / '.sdlc' / 'w' / 'handoff.md')
        rcl, dl, _ = prep(rr, 'verifier', 'L1', str(lw / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree; its tmp prefix is under the sibling root of the main checkout (T-0550, T-0563)',
             rcl == 0 and dl['tree'] == os.path.realpath(str(lw)) and 'Tree: %s ' % dl['tree'] in dl['prompt']
             and 'Tree: %s ' % rr not in dl['prompt'] and dl['tmp_prefix'].startswith(os.path.realpath(str(rr)) + '.worktrees/tmp/'))
        subprocess.run(['git', '-C', str(rr), 'worktree', 'remove', '--force', str(lw)], capture_output=True)
        # T-0693: a lane tree holding a port gets a Ports line after Tree; a tree with no port, or a lane record without one, gets none.
        (rr / '.lane.json').write_text('{"lane": "x", "port": 47410}\n')
        rcp, dp, _ = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', '--dry-run')
        pl = [ln for ln in dp['prompt'].splitlines() if ln.startswith('Ports:')] if rcp == 0 else []
        case('a lane tree with port 47410 in .lane.json: the prompt carries one Ports line naming SDLC_LANE_PORT=47410, right after Tree (T-0693)',
             rcp == 0 and len(pl) == 1 and pl[0].startswith('Ports: SDLC_LANE_PORT=47410 (') and 'never a fixed one' in pl[0]
             and dp['prompt'].splitlines()[dp['prompt'].splitlines().index(pl[0]) - 1].startswith('Tree: '))
        (rr / '.lane.json').write_text('{"lane": "x"}\n')
        rcp, dp, _ = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', '--dry-run')
        (rr / '.lane.json').unlink()
        rcq, dq, _ = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', '--dry-run')
        case('negative control: a lane record with no port, and a tree with no .lane.json, get no Ports line (T-0693)',
             rcp == 0 and rcq == 0 and 'Ports:' not in dp['prompt'] and 'Ports:' not in dq['prompt'])
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
        (R(lw2 / '.sdlc' / 'w') / 'base-sha').write_text(stale + '\n')
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
        (R(lw2 / '.sdlc' / 'w') / 'base-sha').write_text(lane_head + '\n')
        _, dkeep, _ = prep(rr, 'builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a stored base at or after the fork point is kept', dkeep['base_sha'] == lane_head)
        (R(lw2 / '.sdlc' / 'w') / 'base-sha').write_text(fork + '\n')
        _, dfork, _ = prep(rr, 'builder', 'L1', str(lw2 / '.sdlc' / 'w' / 'handoff.md'), '--dry-run')
        case('a stored base equal to the fork point is kept', dfork['base_sha'] == fork)
        (R(lw2 / '.sdlc' / 'w') / 'base-sha').write_text(stale + '\n')
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
        mhand, mbase = rr / '.sdlc' / 'w' / 'handoff.md', R(rr / '.sdlc' / 'w') / 'base-sha'
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
        # T-0413: prepare settles the execution tree once (--tree, else exec_tree), and Tree, the tmp prefix and Base sha all name it.
        real_lane = os.path.realpath(str(lw2))

        def names_lane(d, want=lane_tip2, avoid=main_head):
            return (d['tree'] == real_lane and 'Tree: %s ' % real_lane in d['prompt'] and 'Tree: %s ' % rr not in d['prompt']
                    and d['tmp_prefix'].startswith(os.path.realpath(str(rr)) + '.worktrees/tmp/')
                    and not d['tmp_prefix'].startswith(real_lane + '/')  # T-0550: never nested in the lane
                    and d['base_sha'] == want != avoid and 'Base sha: ' + want in d['prompt'])
        with clean_env(), cwd(lw2), contextlib.redirect_stderr(io.StringIO()):
            from_lane = prepare('verifier', 'L1', str(mhand), dry_run=True)
        case('prepare from a lane worktree for a main-checkout handoff: Tree names the lane, Base sha its start (T-0546)',
             names_lane(from_lane, fork, lane_tip2))
        # T-0546: a lane resumed after its driver died has no base recorded and its HEAD is the driver's WIP commit; a verifier
        # gets the lane start (its .lane.json base_sha, else the fork point), never that HEAD, so its diff is not empty.
        verr = io.StringIO()
        with clean_env(), cwd(lw2), contextlib.redirect_stderr(verr):
            vres = prepare('verifier', 'L1', str(mhand), dry_run=True)['base_sha']
        case('a resumed lane with nothing recorded: the verifier base is the lane fork point, not its WIP HEAD, and it says so',
             vres == fork != lane_tip2 and 'lane start %s' % fork[:12] in verr.getvalue())
        (lw2 / '.lane.json').write_text(json.dumps({'lane': 'lane2', 'base_sha': lane_head}))
        with clean_env(), cwd(lw2), contextlib.redirect_stderr(io.StringIO()):
            vrec = prepare('verifier', 'L1', str(mhand), dry_run=True)['base_sha']
            bres = prepare('builder', 'L1', str(mhand), dry_run=True)['base_sha']
        (lw2 / '.lane.json').unlink()
        case('a resumed lane with a fanout record: the verifier base is the record base_sha', vrec == lane_head != fork)
        case('negative control: a builder with nothing recorded starts at the lane HEAD (the WIP commit)', bres == lane_tip2 != vrec)
        rct, dtree, _ = prep(rr, 'builder', 'L1', str(mhand), '--dry-run', '--tree', str(lw2))
        case('prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree', rct == 0 and names_lane(dtree))
        rcm, dmain, _ = prep(rr, 'builder', 'L1', str(mhand), '--dry-run')
        case('negative control: the same prepare from the main checkout without --tree names the main checkout as Tree',
             rcm == 0 and dmain['tree'] == os.path.realpath(str(rr)) and dmain['base_sha'] == main_head and not names_lane(dmain))
        # T-0578: a solo dispatch recorded in the main checkout holds main's HEAD; for a lane tree whose HEAD is ahead of it,
        # prepare --tree takes the lane's base (its HEAD for a builder, its .lane.json start for a verifier), not main's.
        solo_rec = R(rr / '.sdlc' / 'w') / 'solo-L2-w.dispatch.json'
        solo_rec.write_text(json.dumps({'role': 'solo', 'base_sha': main_head}))
        (lw2 / '.lane.json').write_text(json.dumps({'lane': 'lane2', 'base_sha': lane_head}))
        _, dsb, _ = prep(rr, 'builder', 'L1', str(mhand), '--dry-run', '--tree', str(lw2))
        _, dsv, _ = prep(rr, 'verifier', 'L1', str(mhand), '--dry-run', '--tree', str(lw2))
        _, dsm, _ = prep(rr, 'verifier', 'L1', str(mhand), '--dry-run')
        solo_rec.write_text(json.dumps({'role': 'solo', 'base_sha': lane_head, 'tree': real_lane}))
        _, dst, _ = prep(rr, 'verifier', 'L1', str(mhand), '--dry-run', '--tree', str(lw2))
        solo_rec.unlink()
        (lw2 / '.lane.json').unlink()
        case('prepare --tree for a lane ahead of main: a solo base recorded in the main checkout is not the lane base',
             subprocess.run(['git', '-C', str(rr), 'merge-base', '--is-ancestor', main_head, lane_tip2]).returncode == 0 and dsb.get('base_sha') == lane_tip2 != main_head
             and dsv.get('base_sha') == lane_head != main_head and 'Base sha: ' + lane_head in dsv.get('prompt', ''))
        case('negative control: from the main checkout the same solo record is the verifier base', dsm.get('base_sha') == main_head)
        case('a solo base recorded in the lane tree is kept for prepare --tree', dst.get('base_sha') == lane_head)
        sbd = rr / '.sdlc' / 'sb'
        sb_before = sorted(p.name for p in sbd.iterdir())
        refusals = [(bad,) + prep(rr, 'verifier', 'L1', '.sdlc/sb/handoff.md', '--tree', str(bad)) for bad in (repo, lw2 / '.sdlc')]
        case('prepare --tree: a path that is not a worktree of this repository is refused, exit 2',
             all(rcb == 2 and 'dispatch.py: --tree %s is not a worktree of this repository' % bad in errb for bad, rcb, _, errb in refusals)
             and sorted(p.name for p in sbd.iterdir()) == sb_before)
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
             and 'run_lifecycle.py recover "%s"' % R(w) in err2)
        case('the refused prepare wrote no second record', sorted(p.name for p in R(w).glob('*.attempt.json')) == ['builder-L1.attempt.json'])
        rc3, d3, err3 = prep(rr, 'verifier', 'L1', '.sdlc/w/handoff.md', '--dry-run', SDLC_DISPATCH_PARENT_PID=str(live))
        with clean_env(SDLC_DISPATCH_PARENT_PID=str(live)), cwd(rr), contextlib.redirect_stderr(io.StringIO()):
            own_next = prepare('verifier', 'L1', '.sdlc/w/handoff.md')
        case('an attempt carrying the caller pid does not block the next prepare (T-0371)',
             own_next['result_name'] == 'verifier-L1' and len(list(R(w).glob('*.attempt.json'))) == 2)
        for f in list(R(w).glob('verifier-L1*')):
            f.unlink()
        with clean_env(SDLC_DISPATCH_PARENT_PID=str(live)), cwd(rr), contextlib.redirect_stderr(io.StringIO()):
            doubled = prepare('verifier', 'L1', '.sdlc/w/handoff.md', skip=('lock',))
        case('negative control: without the lock gate a second running attempt starts', doubled['result_name'] == 'verifier-L1'
             and len(list(R(w).glob('*.attempt.json'))) == 2)
        for f in list(R(w).glob('verifier-L1*')):
            f.unlink()
        a = json.loads((R(w) / 'builder-L1.attempt.json').read_text())
        a['parent_pid'] = dead
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        (R(w) / 'builder-L1.running').write_text('1\n')
        st_dead = status(R(w))
        case('status: running attempt with a dead parent prints orphaned', st_dead == ['builder-L1 orphaned builder-L1 parent_pid=%d' % dead])
        case('status --orphans lists the orphan', status(R(w), True) == st_dead)
        a['parent_pid'] = live
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        case('negative control: status --orphans lists none for a live parent', status(R(w), True) == [])
        case('negative control: a live parent prints running', 'running' in status(R(w))[0] and 'orphaned' not in status(R(w))[0])
        a['parent_pid'] = dead
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        a['agent_id'] = 'ag-7'
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        ladder = resume('builder-L1', str(rr))
        case('resume prints SendMessage by name, by id, then the new attempt with the addendum',
             len(ladder) == 3 and 'SendMessage' in ladder[0] and 'w-builder-L1' in ladder[0] and 'SendMessage' in ladder[1] and 'ag-7' in ladder[1]
             and ladder[2].startswith('3. python3 dispatch.py prepare builder L1') and 'git status' in ladder[2] and 'transcript' in ladder[2])
        case('resume replays no old report', 'builder-L1.md' not in ' '.join(ladder))
        # T-0703: a resumed agent reports to main itself; status flags a report newer than its unrecorded attempt record
        case('T-0703 resume tells the agent to SendMessage main with its pointer line, by name and by id',
             all("SendMessage to 'main'" in ladder[i] and 'builder-L1 <status> <path>' in ladder[i] for i in (0, 1)))
        apath, rpath = R(w) / 'builder-L1.attempt.json', R(w) / 'builder-L1.md'
        rpath.write_text('builder done\n')
        os.utime(rpath, (time.time() - 60, time.time() - 60))
        os.utime(apath, None)
        case('T-0705 a running attempt with a report older than its record still prints report-unrecorded once (the T-0383 shape)',
             status(R(w))[0].split().count('report-unrecorded') == 1)
        a['status'] = 'interrupted'
        apath.write_text(json.dumps(a))
        os.utime(rpath, (time.time() - 60, time.time() - 60))
        os.utime(apath, None)
        case('T-0703 negative control: an interrupted attempt with a report older than its attempt record is not report-unrecorded',
             ' report-unrecorded' not in status(R(w))[0])
        a['status'] = 'running'
        apath.write_text(json.dumps(a))
        os.utime(rpath, (time.time() + 60, time.time() + 60))
        case('T-0703/T-0705 status prints exactly one report-unrecorded for a running attempt with a report newer than its record',
             status(R(w))[0].endswith(' report-unrecorded') and status(R(w))[0].count('report-') == 1)
        a['status'] = 'interrupted'
        apath.write_text(json.dumps(a))
        os.utime(rpath, (time.time() + 60, time.time() + 60))
        case('T-0703 status prints report-unrecorded for an interrupted attempt the resumed agent reported on',
             status(R(w))[0].split()[1] == 'interrupted' and status(R(w))[0].endswith(' report-unrecorded'))
        a['status'] = 'completed'
        apath.write_text(json.dumps(a))
        os.utime(rpath, (time.time() + 60, time.time() + 60))
        case('T-0703 negative control: a recorded attempt prints no report-unrecorded', 'report-unrecorded' not in status(R(w))[0])
        rpath.unlink()
        a['status'] = 'running'
        apath.write_text(json.dumps(a))
        a.pop('agent_id')
        a['parent_pid'] = live
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        try:
            resume('builder-L1', str(rr))
            refused = False
        except Refuse:
            refused = True
        case('resume refuses a running attempt', refused)
        # T-0514: a running attempt with a silent transcript gets the ladder under profile: inner-loop only
        proj = Path(tempfile.mkdtemp(prefix='b5-proj-'))
        tdir = proj / 'p' / 's' / 'subagents'
        tdir.mkdir(parents=True)
        tfile = tdir / 'agent-ag-7.jsonl'
        tfile.write_text('{}\n')
        os.utime(tfile, (time.time() - 7200, time.time() - 7200))
        a['agent_id'] = 'ag-7'
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        cfgdir = rr / '.sdlc'
        cfgdir.mkdir(exist_ok=True)
        cfgfile = cfgdir / 'config'
        had = cfgfile.read_text() if cfgfile.is_file() else None

        def silent_resume():
            try:
                return resume('builder-L1', str(rr))
            except Refuse:
                return None
        old_proj = os.environ.get('SDLC_CLAUDE_PROJECTS')
        os.environ['SDLC_CLAUDE_PROJECTS'] = str(proj)
        try:
            cfgfile.write_text((had or '') + '\nprofile: inner-loop\n')
            lad = silent_resume()
            case('resume under inner-loop prints the ladder for a running attempt silent for 2 hours',
                 lad is not None and len(lad) == 3 and 'ag-7' in lad[1] and lad[2].startswith('3. python3 dispatch.py prepare builder L1'))
            os.utime(tfile, None)
            case('negative control: inner-loop resume still refuses a running attempt written to just now', silent_resume() is None)
            os.utime(tfile, (time.time() - 7200, time.time() - 7200))
            cfgfile.write_text(had or '')
            case('negative control: without the inner-loop profile a silent running attempt is still refused', silent_resume() is None)
        finally:
            if old_proj is None:
                os.environ.pop('SDLC_CLAUDE_PROJECTS', None)
            else:
                os.environ['SDLC_CLAUDE_PROJECTS'] = old_proj
            if had is None:
                cfgfile.unlink()
            shutil.rmtree(proj, ignore_errors=True)
        a.pop('agent_id')
        a['parent_pid'] = dead
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(a))
        (R(w) / 'builder-L1.md').write_text('<!-- role=builder level=L1 model=sonnet effort=low -->\n## Status\ndone\n')
        rec_rep, _ = recover_orphans(R(w))
        rep_r = json.loads((R(w) / 'builder-L1.attempt.json').read_text())
        case('recover leaves a dead-parent attempt whose result holds a verdict alone (T-0445)',
             rec_rep == [] and rep_r['status'] == 'running' and 'recovery' not in rep_r)
        (R(w) / 'builder-L1.md').unlink()
        rec, _ = recover_orphans(R(w))
        old_r = json.loads((R(w) / 'builder-L1.attempt.json').read_text())
        case('recover marks it interrupted with run_lifecycle.py text', rec == ['builder-L1.attempt.json'] and old_r['status'] == 'interrupted'
             and old_r['recovery'] == RECOVERY and 'finished_at' in old_r)
        old_r['status'] = 'running'
        (R(w) / 'builder-L1.attempt.json').write_text(json.dumps(old_r))
        (R(w) / 'builder-L1.running').write_text('1\n')
        rc3, got3, err3 = prep(rr, 'builder', 'L1', '.sdlc/w/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live))
        old = json.loads((R(w) / 'builder-L1.attempt.json').read_text())
        # T-0505: the new attempt (builder-L1-2) writes builder-L1.running again, so the hand-written '1' is gone and an epoch start is there
        remade = (R(w) / 'builder-L1.running').read_text() if (R(w) / 'builder-L1.running').is_file() else ''
        case('a dead-parent attempt is recovered first', rc3 == 0 and old['status'] == 'interrupted' and 'finished_at' in old and 'recovered' in err3
             and remade != '1\n' and re.fullmatch(r'[0-9]+\n', remade) is not None)
        case('the new attempt gets the next result name and Agent name', got3['result_name'] == 'builder-L1-2'
             and got3['result'] == str(R(w) / 'builder-L1-2.md') and got3['name'] == 'w-builder-L1-2'
             and (R(w) / 'builder-L1-2.attempt.json').is_file())
        case('the interrupted attempt was not overwritten', old['attempt_id'] == att['attempt_id'])
        dryrc, drygot, _ = prep(rr, 'builder', 'L1', '.sdlc/w/handoff.md', '--dry-run')
        case('a dry run writes nothing and takes no lock', dryrc == 0 and drygot['dry_run'] is True and len(list(R(w).glob('*.attempt.json'))) == 2)
        case('a planner dispatch has no base sha', prep(rr, 'planner', 'L1', '.sdlc/w/handoff.md', '--dry-run')[1]['base_sha'] is None)
        # T-0505: the running marker follows the attempt. A dry run writes none; recover clears a dead-parent attempt's marker and
        # keeps the marker of an attempt another live session owns (recover_orphans, and settle inside a second prepare).
        for name in ('md', 'mr', 'ml'):
            put(rr / '.sdlc' / name / 'handoff.md')
        md, mr, ml = (rr / '.sdlc' / name for name in ('md', 'mr', 'ml'))
        md_before = sorted(p.name for p in md.iterdir())
        rcd, gd, _ = prep(rr, 'builder', 'L1', '.sdlc/md/handoff.md', '--dry-run', SDLC_DISPATCH_PARENT_PID=str(live))
        case('prepare --dry-run writes no running marker (T-0505)',
             rcd == 0 and gd['dry_run'] is True and list(R(md).glob('*.running')) == [] and sorted(p.name for p in md.iterdir()) == md_before)
        rcr, _, _ = prep(rr, 'builder', 'L1', '.sdlc/mr/handoff.md', SDLC_DISPATCH_PARENT_PID=str(dead))
        mr_had = (R(mr) / 'builder-L1.running').is_file()
        mr_rec, _ = recover_orphans(R(mr))
        case('recover removes the running marker of a dead-parent attempt (T-0505)',
             rcr == 0 and mr_had and mr_rec == ['builder-L1.attempt.json'] and not (R(mr) / 'builder-L1.running').exists()
             and json.loads((R(mr) / 'builder-L1.attempt.json').read_text())['status'] == 'interrupted')
        other = os.getppid()  # alive and older than the attempt, and not this process: another run's session
        rcl, _, _ = prep(rr, 'builder', 'L1', '.sdlc/ml/handoff.md', SDLC_DISPATCH_PARENT_PID=str(other))
        ml_stamp = (R(ml) / 'builder-L1.running').read_text() if (R(ml) / 'builder-L1.running').is_file() else None
        ml_rec, ml_live = recover_orphans(R(ml))
        rcl2, _, errl2 = prep(rr, 'verifier', 'L1', '.sdlc/ml/handoff.md', SDLC_DISPATCH_PARENT_PID=str(live))
        ml_att = json.loads((R(ml) / 'builder-L1.attempt.json').read_text())
        case('recover keeps a live attempt of another run and its running marker (T-0505)',
             rcl == 0 and ml_stamp is not None and ml_rec == [] and len(ml_live) == 1 and rcl2 == 2 and 'still running' in errl2
             and (ml_att['status'], ml_att['parent_pid']) == ('running', other) and 'recovery' not in ml_att
             and sorted(p.name for p in R(ml).glob('*.running')) == ['builder-L1.running'] and (R(ml) / 'builder-L1.running').read_text() == ml_stamp
             and sorted(p.name for p in R(ml).glob('*.attempt.json')) == ['builder-L1.attempt.json'])
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
        case('CLI prints the dispatch JSON on stdout', p.returncode == 0 and cli.get('model') == 'sonnet' and cli.get('subagent_type') == 'sdlc-lite:scout-L1')
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

        def go(repo, role, level, rel, body=None, said=None, mutate=None, validate=validate_result, agent_id=None, no_result=False, attempt_mutate=None, **env):
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
            if attempt_mutate:
                f = Path(got['attempt_file'])
                f.write_text(json.dumps(dict(json.loads(f.read_text()), **attempt_mutate)))
            e, o = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
                try:
                    out = record(got['dispatch_file'], stdin=(lambda: said) if said is not None else None, agent_id=agent_id, validate=validate, no_result=no_result)
                except Refuse as r:
                    print('\n'.join(r.lines), file=sys.stderr)
                    out = r.rc
            return out, got, e.getvalue(), o.getvalue()

        def lines_of(directory):
            f = R(directory) / 'runs.jsonl'
            return [json.loads(l) for l in f.read_text().splitlines()] if f.is_file() else []

        def attempt_of(got):
            return json.loads(Path(got['attempt_file']).read_text())

        def next_out(repo, rel):
            p = script('steps.py', 'next', repo / rel)
            return p.returncode, p.stdout.replace(str(repo), '<repo>')

        # records dir (T-0540): prepare plus record write the result, attempt, dispatch record and runs.jsonl under
        # .sdlc/runtime/tasks/<name>/, so git sees only handoff.md in the task folder; a legacy task dir (runs.jsonl beside
        # its handoff) keeps recording in place and gets no runtime dir.
        scout_body = '## Map\nNone\n\n## Entry points\nNone\n\n## Not found\nNone\n\n## Carry forward\nNone\n'
        rdr = tmp / 'records-dir'
        init_repo(rdr)
        put(rdr / '.sdlc' / 'task' / 'handoff.md', '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n')
        rrc, rgot, _, _ = go(rdr, 'scout', 'L1', '.sdlc/task/handoff.md', body=scout_body)
        rtd = rdr / '.sdlc' / 'runtime' / 'tasks' / 'task'
        seen = git('status', '--porcelain', '-uall', '--', '.sdlc/task', cwd=rdr).stdout.splitlines()
        case('records dir: prepare plus record leaves only handoff.md in the task dir',
             rrc == 0 and seen == ['?? .sdlc/task/handoff.md'] and rgot['artifacts_dir'] == str(rtd)
             and all((rtd / n).is_file() for n in ('scout-L1.md', 'scout-L1.attempt.json', 'scout-L1.dispatch.json', 'runs.jsonl'))
             and git('check-ignore', '-q', '.sdlc/runtime/tasks/task/runs.jsonl', cwd=rdr).returncode == 0)
        put(rdr / '.sdlc' / 'old' / 'handoff.md', '## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n')
        put(rdr / '.sdlc' / 'old' / 'runs.jsonl', '{}\n')
        lrc, lgot, _, _ = go(rdr, 'scout', 'L1', '.sdlc/old/handoff.md', body=scout_body)
        old = rdr / '.sdlc' / 'old'
        case('records dir: a legacy task dir with runs.jsonl keeps recording in place',
             lrc == 0 and lgot['artifacts_dir'] == str(old) and (old / 'scout-L1.md').is_file() and (old / 'scout-L1.attempt.json').is_file()
             and len((old / 'runs.jsonl').read_text().splitlines()) == 2 and not (rdr / '.sdlc' / 'runtime' / 'tasks' / 'old').exists())

        ra, rb = mk(tmp / 'A'), mk(tmp / 'B')
        step = '.sdlc/t/step-1'
        for role, level, rel, env in (('builder', 'L2', step, {}), ('verifier', 'L1', step, {}), ('planner', 'L1', '.sdlc/p', {}),
                                      ('plan-reviewer', 'L1', '.sdlc/p', {'SDLC_SPECGATE': 'off'})):
            src, a_result, _ = via_runsh(ra, role, level, rel + '/handoff.md', **env)
            rc, got, err, out = go(rb, role, level, rel + '/handoff.md', body=BODY[role], agent_id='agent-' + role, **env)
            a_line, b_line = lines_of(ra / rel)[-1], lines_of(rb / rel)[-1]
            case('record parity %s: valid result exits 0 like run.sh and prints the result path' % role,
                 src == 0 and rc == 0 and out.strip().splitlines()[0] == got['result'])
            case('record parity %s: runs.jsonl key set is the run.sh set plus agent_id, cost_reason, result_sha256, and unpriced' % role,
                 set(b_line) == set(a_line) | {'agent_id', 'cost_reason', 'result_sha256', 'unpriced'} and set(a_line) <= set(b_line))
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
            rsha = hashlib.sha256(Path(got['result']).read_bytes()).hexdigest()
            case('record %s stores result_sha256 in the attempt and the runs row, equal to the result file sha256' % role,
                 att.get('result_sha256') == rsha and b_line.get('result_sha256') == rsha)
            Path(got['result']).write_text(Path(got['result']).read_text() + 'edited\n')
            case('record %s: editing the result afterwards no longer matches result_sha256' % role,
                 hashlib.sha256(Path(got['result']).read_bytes()).hexdigest() != att['result_sha256'])
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
                 rc == 0 and attempt_of(cgot)['status'] == 'completed'
                 and all(l.startswith(('dispatch.py: unpriced: ', 'dispatch.py: cleaned: ')) for l in err.splitlines()))  # T-0402: only the unpriced note; T-0426: and the cleanup count

        # T-0678: an attempt prepared under an older plugin whose result fails a newer schema is recorded completed as legacy.
        running_version = plugin_min.running(PLUGIN, 'claude')[0]
        old_review = '## Mode\nreview\n\n## Decisions\nd\n\n## Findings\nNone\n\nVerdict: pass (0 blocking, 3 advisory)\n'
        for name in ('lg1', 'lg2', 'lg3'):
            put(rb / '.sdlc' / name / 'handoff.md')
        rc, got, err, out = go(rb, 'ui-designer', 'L1', '.sdlc/lg1/handoff.md', body=old_review, attempt_mutate={'plugin_version': '0.0.1'})
        att = attempt_of(got)
        case('legacy format: a result failing validation from an attempt prepared under 0.0.1 exits 0 with legacy-format on stderr',
             rc == 0 and 'legacy-format: ui-designer result review mode lacks ## Verdict' in err and 'prepared under 0.0.1, recorded as completed' in err
             and att['status'] == 'completed' and 'lacks ## Verdict' in att.get('legacy_format', '')
             and 'lacks ## Verdict' in lines_of(rb / '.sdlc' / 'lg1')[-1].get('legacy_format', ''))
        rc, lg2, err, out = go(rb, 'ui-designer', 'L1', '.sdlc/lg2/handoff.md', body=old_review)
        att = attempt_of(lg2)
        case('legacy format: the same result prepared under the running version exits 3 and the attempt reads failed',
             rc == 3 and (att['status'], att['exit_code']) == ('failed', 3) and 'legacy_format' not in att and 'legacy-format' not in err)
        rc, got, err, out = go(rb, 'ui-designer', 'L1', '.sdlc/lg3/handoff.md', body='Verdict: pass\n', attempt_mutate={'plugin_version': '0.0.1'})
        case('legacy format: a result with no ## heading from an older version is never legacy',
             rc != 0 and attempt_of(got)['status'] == 'failed' and 'legacy-format' not in err)
        # T-0686: a completed ui-designer review prints a repo-relative Review record line; a plan-mode run prints none.
        review = '## Mode\nreview\n\n## Verdict\npass-with-notes\n\n## Decisions\nd\n\n## Findings\nNone\n'
        put(rb / '.sdlc' / 'rr1' / 'handoff.md', '## Goal\nx\n\nmode: review\n')
        put(rb / '.sdlc' / 'rr2' / 'handoff.md', '## Goal\nx\n\nmode: plan\n')
        head = git('rev-parse', '--short', 'HEAD', cwd=str(rb)).stdout.strip()
        rc, got, err, out = go(rb, 'ui-designer', 'L1', '.sdlc/rr1/handoff.md', body=review)
        rel = os.path.relpath(os.path.realpath(got['result']), os.path.realpath(str(rb)))
        case('record of a ui-designer review prints - Review record: <repo-relative result> (<verdict> at <short HEAD>)',
             rc == 0 and out.splitlines()[1:2] == ['- Review record: %s (pass-with-notes at %s)' % (rel, head)] and not rel.startswith(('/', '..')))
        rc, got, err, out = go(rb, 'ui-designer', 'L1', '.sdlc/rr2/handoff.md', body=review.replace('review\n\n## Verdict\npass-with-notes\n', 'plan\n'))
        case('negative control: a mode: plan ui-designer record prints no Review record line', rc == 0 and out.strip() and 'Review record' not in out)
        case('prepare writes plugin_version equal to the manifest version in the dispatch and the attempt',
             running_version is not None and json.loads(Path(lg2['dispatch_file']).read_text())['plugin_version'] == running_version
             and attempt_of(lg2)['plugin_version'] == running_version)

        # A failed sub-agent: error text and no result; a limit text also leaves the resume marker.
        for name in ('f1', 'f2', 'f3'):
            put(rb / '.sdlc' / name / 'handoff.md')
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f1/handoff.md', said='API Error: connection reset by peer')
        f1 = rb / '.sdlc' / 'f1'
        att = attempt_of(got)
        case('a failed sub-agent exits 1 and records status failed with its text', rc == 1 and att['status'] == 'failed' and att['exit_code'] == 1
             and 'connection reset' in att['error'] and 'returned no result' in err)
        case('a failed sub-agent writes no result, no runs.jsonl line, and no limit marker, and keeps the error as a log',
             not Path(got['result']).exists() and lines_of(f1) == [] and not (R(f1) / 'builder-L1.limit').exists()
             and 'connection reset' in (R(f1) / 'builder-L1.log').read_text())
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f2/handoff.md', no_result=True)
        case('no result file and no stdin text is a failed sub-agent too', rc == 1 and 'no result file' in attempt_of(got)['error'])
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f3/handoff.md', said='API Error: 429 rate limit exceeded: session limit reached')
        f3 = rb / '.sdlc' / 'f3'
        marker = json.loads((R(f3) / 'builder-L1.limit').read_text()) if (R(f3) / 'builder-L1.limit').is_file() else {}
        case('a 429 or session-limit text exits 1 and writes <role>-<level>.limit with the resume command',
             rc == 1 and sorted(marker) == ['evidence', 'handoff', 'level', 'resume', 'role', 'ts'] and '429' in marker['evidence']
             and marker['resume'] == 'python3 %s prepare builder L1 %s' % (HERE / 'dispatch.py', got['handoff'])
             and 'session limit: resume with: ' + marker['resume'] in err)
        put(rb / '.sdlc' / 'v1' / 'handoff.md')
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/v1/handoff.md', no_result=True)
        case('a verifier prompt names the report path it must write before it ends',
             'Report file: %s' % got['result'] in got['prompt'] and 'before you end' in got['prompt']
             and 'dispatch.py record adds it' in got['prompt'] and '--role verifier --headerless' in got['prompt'])
        case('every brief says rm under the tmp prefix is allowed and elsewhere refused, once',
             got['prompt'].count('rm is allowed there and refused elsewhere') == 1)
        # T-0646: every role writes its result to the Report file and ends with a one-line pointer; record reads the file.
        for name, role, rel in (('pb', 'builder', '.sdlc/pb/handoff.md'), ('pp', 'planner', '.sdlc/pp/handoff.md'), ('ps', 'scout', '.sdlc/ps/handoff.md')):
            put(rb / '.sdlc' / name / 'handoff.md')
            prc, pgot, _ = prep(rb, role, 'L1', rel, '--dry-run')
            case('T-0646 a prepared %s brief carries Report file: <its result path> and the one-line pointer instruction' % role,
                 prc == 0 and '\nReport file: %s (before you end' % pgot['result'] in pgot['prompt']
                 and '--role %s --headerless' % role in pgot['prompt']
                 and '\nEnd with one line: `%s <status> %s`' % (role, pgot['result']) in pgot['prompt'] and 'saved verbatim' not in pgot['prompt'])
        put(rb / '.sdlc' / 'pr' / 'handoff.md')
        rc, pgot, err, out = go(rb, 'builder', 'L1', '.sdlc/pr/handoff.md', body=BODY['builder'], said='builder done %s' % (R(rb / '.sdlc' / 'pr') / 'builder-L1.md'))
        case('T-0646 record with the result file written and a one-line stdin pointer exits 0 and validates the file',
             rc == 0 and out.strip().splitlines()[0] == pgot['result'] and validate_result('builder', pgot['result']) is None
             and Path(pgot['result']).read_text().splitlines()[1:4] == ['## Status', 'done', ''])
        put(rb / '.sdlc' / 'pn' / 'handoff.md')
        rc, pgot, err, out = go(rb, 'scout', 'L1', '.sdlc/pn/handoff.md', said='scout done %s' % (R(rb / '.sdlc' / 'pn') / 'scout-L1.md'))
        case('T-0646 record with no file and a one-line stdin pointer exits non-zero naming the result path',
             rc == 1 and 'no result file at %s' % pgot['result'] in attempt_of(pgot)['error'] and 'pointer' in attempt_of(pgot)['error']
             and lines_of(rb / '.sdlc' / 'pn') == [])
        case('a verifier with no report on disk is rejected: exit 1, a message naming the path, no runs.jsonl line',
             rc == 1 and 'no result file at %s' % got['result'] in attempt_of(got)['error'] and 'must write its report there' in attempt_of(got)['error']
             and lines_of(rb / '.sdlc' / 'v1') == [])
        # T-0412: no result yet is not a failure; the attempt stays running until the role writes its report or --no-result closes it.
        for name in ('r1', 'r2', 'r3'):
            put(rb / '.sdlc' / name / 'handoff.md')
        r1 = rb / '.sdlc' / 'r1'
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/r1/handoff.md')
        case('record with no result file and empty stdin exits 2 and leaves the attempt running',
             rc == 2 and 'no result yet at %s; the attempt stays running' % got['result'] in err and '--no-result' in err
             and attempt_of(got)['status'] == 'running' and not (R(r1) / 'verifier-L1.log').exists() and lines_of(r1) == []
             and not (R(r1) / 'verifier-L1.limit').exists() and not (R(r1) / 'verifier-L1.delivery.json').exists())
        case('a no-result record keeps the running marker (T-0505)',
             rc == 2 and attempt_of(got)['status'] == 'running' and (R(r1) / 'verifier-L1.running').is_file())
        # T-0505: a record that closes the attempt (completed, or failed on error text) clears the marker prepare wrote.
        cleared = []
        for name, body, said, want in (('m1', BODY['builder'], None, ('completed', 0)), ('m2', None, 'API Error: connection reset by peer', ('failed', 1))):
            put(rb / '.sdlc' / name / 'handoff.md')
            _, gm, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % name, SDLC_DISPATCH_PARENT_PID=live_pid)
            mark = R(rb / '.sdlc' / name) / 'builder-L1.running'
            had = mark.is_file()
            if body is not None:
                Path(gm['result']).write_text(body, encoding='utf-8')
            with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                rcm = record(gm['dispatch_file'], stdin=(lambda text=said: text) if said is not None else None)
            cleared.append(had and (attempt_of(gm)['status'], rcm) == want and not mark.exists())
        case('record removes the running marker on completed and on failed (T-0505)', cleared == [True, True])
        Path(got['result']).write_text(BODY['verifier'], encoding='utf-8')
        e, o = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
            rc = record(got['dispatch_file'])
        case('record after the late result file appears completes the attempt',
             rc == 0 and attempt_of(got)['status'] == 'completed' and len(lines_of(r1)) == 1)
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/r2/handoff.md', no_result=True)
        r2 = rb / '.sdlc' / 'r2'
        case('record --no-result closes an attempt with no result file as failed, exit 1',
             rc == 1 and (attempt_of(got)['status'], attempt_of(got)['exit_code']) == ('failed', 1)
             and 'no result file at %s' % got['result'] in attempt_of(got)['error'] and lines_of(r2) == [])
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/r3/handoff.md', said='API Error: connection reset by peer')
        case('negative control: error text on stdin with no result file still closes the attempt failed',
             rc == 1 and attempt_of(got)['status'] == 'failed' and 'connection reset' in attempt_of(got)['error'])
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/v1/handoff.md', body=BODY['verifier'])
        case('a verifier with its report on disk is accepted', rc == 0 and attempt_of(got)['status'] == 'completed')
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/f3/handoff.md', body=BODY['builder'])
        case('a later success in the same dir removes the limit marker', rc == 0 and not (R(f3) / 'builder-L1.limit').exists())

        # T-0537: a sub-agent stopped by a spend limit with no record: resume --limit marks it limit-stopped and names the resume call.
        def cli(*argv):
            e, o = io.StringIO(), io.StringIO()
            with cwd(rb), contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
                rc = main(list(argv))
            return rc, o.getvalue(), e.getvalue()
        for name in ('lm1', 'lm2'):
            put(rb / '.sdlc' / name / 'handoff.md')
        lm1 = rb / '.sdlc' / 'lm1'
        _, gl, _ = prep(rb, 'builder', 'L1', '.sdlc/lm1/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        rc, out, err = cli('resume', '--limit', gl['name'], '--root', str(rb))
        lmark = json.loads((R(lm1) / 'builder-L1.limit').read_text()) if (R(lm1) / 'builder-L1.limit').is_file() else {}
        case('resume --limit marks a running attempt limit-stopped, clears its running marker, and writes the .limit marker with SendMessage by name',
             rc == 0 and attempt_of(gl)['status'] == 'limit-stopped' and not (R(lm1) / 'builder-L1.running').exists()
             and lmark.get('resume', '').startswith('SendMessage({to: "%s"' % gl['name']) and 'prepare builder L1' in lmark.get('prepare', '')
             and 'SendMessage({to: "%s"' % gl['name'] in out)
        case('status shows limit-stopped and resume prints the ladder for it',
             status(R(lm1))[0].split()[1] == 'limit-stopped' and 'SendMessage' in resume(gl['name'], str(rb))[0])
        Path(gl['result']).write_text(BODY['builder'], encoding='utf-8')
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            rc = record(gl['dispatch_file'])
        case('a limit-stopped attempt resumed by SendMessage records as usual and the success removes the marker',
             rc == 0 and attempt_of(gl)['status'] == 'completed' and not (R(lm1) / 'builder-L1.limit').exists())
        rc, out, err = cli('resume', '--limit', gl['name'], '--root', str(rb))
        case('negative control: resume --limit refuses a completed attempt', rc == 2 and 'completed, not running' in err)
        _, gl2, _ = prep(rb, 'builder', 'L1', '.sdlc/lm2/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        Path(gl2['result']).write_text(BODY['builder'], encoding='utf-8')
        rc, out, err = cli('resume', '--limit', gl2['name'], '--root', str(rb))
        case('negative control: resume --limit refuses a running attempt that has a result, writes no marker, and keeps it running',
             rc == 2 and 'has a result' in err and attempt_of(gl2)['status'] == 'running' and not (R(rb / '.sdlc' / 'lm2') / 'builder-L1.limit').exists())
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            record(gl2['dispatch_file'])
        # T-0537: prepare notes a model or effort that differs from the last recorded attempt of the same role and level.
        rc, gr, err = prep(rb, 'builder', 'L1', '.sdlc/lm2/handoff.md', '--dry-run')
        case('negative control: prepare is silent when the row matches the previous attempt', rc == 0 and 'row changed' not in err)
        with (R(rb / '.sdlc' / 'lm2') / 'runs.jsonl').open('a') as f:
            f.write(json.dumps(dict(role='builder', level='L1', model='fable', effort='max')) + '\n')
        rc, gr, err = prep(rb, 'builder', 'L1', '.sdlc/lm2/handoff.md', '--dry-run')
        case('prepare prints one row-changed line when the model or effort differs from the previous attempt',
             rc == 0 and err.count('row changed: builder L1 was fable/max on the previous attempt, now %s/%s' % (gr['model'], gr['effort'])) == 1)

        # The CLI: stdin carries the error text; flags carry the notice's numbers.
        env_cli = {k: v for k, v in os.environ.items() if not k.startswith('SDLC_')}
        put(rb / '.sdlc' / 'c1' / 'handoff.md')
        put(rb / '.sdlc' / 'c2' / 'handoff.md')
        rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/c1/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', got['dispatch_file']], input='Error: session limit reached',
                           capture_output=True, text=True, env=env_cli)
        case('CLI record reads error text from stdin: exit 1 and the limit marker', p.returncode == 1 and (R(rb / '.sdlc' / 'c1') / 'builder-L1.limit').is_file())
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
        unpriced_err = {}
        for nm, extra in (('c3', ['--transcript', str(tr)]), ('c4', [])):
            rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % nm, SDLC_DISPATCH_PARENT_PID=live_pid)
            Path(got['result']).write_text(BODY['builder'])
            up = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record'] + extra + [got['dispatch_file']], capture_output=True, text=True,
                                env=env_cli, stdin=subprocess.DEVNULL)
            unpriced_err[nm] = (up.returncode, up.stderr, got['name'])
        # T-0402: a record with no transcript and no tokens says it cannot price the run; a priced one is silent.
        c3row, c4row = lines_of(rb / '.sdlc' / 'c3')[-1], lines_of(rb / '.sdlc' / 'c4')[-1]
        case('record with no --transcript and no --tokens prints the unpriced line and the row holds unpriced true',
             unpriced_err['c4'][0] == 0 and ('unpriced: %s has no cost row; pass --transcript <jsonl>' % unpriced_err['c4'][2]) in unpriced_err['c4'][1]
             and c4row.get('unpriced') is True and c4row.get('cost_usd') is None)
        case('record with --transcript prints no unpriced line and the row is priced',
             'unpriced' not in unpriced_err['c3'][1] and 'unpriced' not in c3row and isinstance(c3row.get('cost_usd'), float))
        case('record with notice tokens writes no unpriced field', 'unpriced' not in line)
        case('record with a transcript writes resolved_model beside the alias', lines_of(rb / '.sdlc' / 'c3')[-1].get('resolved_model') == 'claude-haiku-5-5')
        case('record with no transcript writes no resolved_model', 'resolved_model' not in lines_of(rb / '.sdlc' / 'c4')[-1])
        # T-0446: --agent-id alone finds subagents/agent-<id>.jsonl under the Claude projects folder and prices as --transcript does.
        proj = rb / 'claude-projects'
        for d in ('-p1/s1/subagents', '-p2/s2/subagents'):
            (proj / d).mkdir(parents=True, exist_ok=True)
        (proj / '-p1/s1/subagents/agent-ag-find.jsonl').write_text(tr.read_text())
        (proj / '-p1/s1/subagents/agent-ag-two.jsonl').write_text(tr.read_text())
        (proj / '-p2/s2/subagents/agent-ag-two.jsonl').write_text(tr.read_text())
        env_find = {**env_cli, 'SDLC_CLAUDE_PROJECTS': str(proj)}
        found = {}
        for nm, aid in (('f1', 'ag-find'), ('f2', 'ag-none'), ('f3', 'ag-two'), ('f4', '../ag-find')):
            put(rb / '.sdlc' / nm / 'handoff.md')
            rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % nm, SDLC_DISPATCH_PARENT_PID=live_pid)
            Path(got['result']).write_text(BODY['builder'])
            up = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', '--agent-id', aid, got['dispatch_file']],
                                capture_output=True, text=True, env=env_find, stdin=subprocess.DEVNULL)
            found[nm] = (up.returncode, up.stderr, got['name'], lines_of(rb / '.sdlc' / nm)[-1])
        case('record with --agent-id and no --transcript finds the sub-agent transcript: priced row, resolved_model, no unpriced line',
             found['f1'][0] == 0 and 'unpriced' not in found['f1'][1] and 'unpriced' not in found['f1'][3]
             and isinstance(found['f1'][3].get('cost_usd'), float) and found['f1'][3].get('resolved_model') == 'claude-haiku-5-5')
        case('record with an --agent-id that has no transcript still prints the unpriced line, exit 0, and the row holds unpriced true',
             found['f2'][0] == 0 and ('unpriced: %s has no cost row; pass --transcript <jsonl>' % found['f2'][2]) in found['f2'][1]
             and found['f2'][3].get('unpriced') is True and found['f2'][3].get('cost_usd') is None)
        case('record with an --agent-id matching two transcripts takes none: unpriced',
             found['f3'][0] == 0 and 'unpriced:' in found['f3'][1] and found['f3'][3].get('unpriced') is True)
        case('record with a path-shaped --agent-id reads no transcript: unpriced',
             found['f4'][0] == 0 and 'unpriced:' in found['f4'][1] and found['f4'][3].get('unpriced') is True)
        # T-0476: `started` stores the agent id in the running attempt at spawn; status shows the transcript's last-activity age and `silent` after 30 minutes.
        def started(dfile, aid, projects=None):
            return subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'started', '--agent-id', aid, dfile],
                                  capture_output=True, text=True, env={**env_cli, 'SDLC_CLAUDE_PROJECTS': str(projects or proj)}, stdin=subprocess.DEVNULL)

        def aged_status(seconds, aid, art):
            tp = proj / '-p1/s1/subagents' / ('agent-%s.jsonl' % aid)
            tp.write_text('{}\n')
            os.utime(tp, (time.time() - seconds, time.time() - seconds))
            was = os.environ.get('SDLC_CLAUDE_PROJECTS')
            os.environ['SDLC_CLAUDE_PROJECTS'] = str(proj)
            try:
                return status(R(art))[0]
            finally:
                if was is None:
                    os.environ.pop('SDLC_CLAUDE_PROJECTS', None)
                else:
                    os.environ['SDLC_CLAUDE_PROJECTS'] = was
        put(rb / '.sdlc' / 'lv' / 'handoff.md')
        rc, lv, _ = prep(rb, 'builder', 'L1', '.sdlc/lv/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        sp = started(lv['dispatch_file'], 'ag-quiet')
        lv_att = json.loads(Path(lv['attempt_file']).read_text())
        case('started writes the agent id into the running attempt and leaves it running',
             sp.returncode == 0 and lv_att.get('agent_id') == 'ag-quiet' and lv_att['status'] == 'running')
        silent_line = aged_status(7200, 'ag-quiet', lv['artifacts_dir'])
        case('status of a running attempt whose transcript is 2 h old: running, last activity 2h, silent',
             ' running ' in silent_line and 'last activity 2h' in silent_line and silent_line.endswith(' silent'))
        live_line = aged_status(120, 'ag-quiet', lv['artifacts_dir'])
        case('negative control: a transcript written 2 minutes ago shows its age and no silent', 'last activity 2m' in live_line and 'silent' not in live_line)
        edge_line = aged_status(1750, 'ag-quiet', lv['artifacts_dir'])
        case('negative control: a transcript just under 30 minutes old is not silent', 'last activity 29m' in edge_line and 'silent' not in edge_line)
        (proj / '-p1/s1/subagents/agent-ag-quiet.jsonl').unlink()
        gone_line = status(lv['artifacts_dir'])[0]
        case('negative control: no transcript found prints neither last activity nor silent', 'last activity' not in gone_line and 'silent' not in gone_line)
        case('started refuses a path-shaped agent id and an unreadable dispatch file',
             started(lv['dispatch_file'], '../x').returncode == 2 and started(str(rb / 'no-such.dispatch.json'), 'ag-1').returncode == 2
             and json.loads(Path(lv['attempt_file']).read_text()).get('agent_id') == 'ag-quiet')
        Path(lv['result']).write_text(BODY['builder'])
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            record(lv['dispatch_file'])
        case('started refuses an attempt that is already recorded', started(lv['dispatch_file'], 'ag-quiet').returncode == 2)
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
        # T-0667: --agent-id alone (no result file, no stdin, no --transcript) reads the result from the found transcript; an id with none exits 2.
        (proj / '-p1/s1/subagents/agent-ag-solo.jsonl').write_text(json.dumps(good) + '\n')
        alone = {}
        for nm, aid in (('a1', 'ag-solo'), ('a2', 'ag-missing')):
            put(rb / '.sdlc' / nm / 'handoff.md')
            rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/%s/handoff.md' % nm, SDLC_DISPATCH_PARENT_PID=live_pid)
            q = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', '--agent-id', aid, got['dispatch_file']],
                               capture_output=True, text=True, env=env_find, stdin=subprocess.DEVNULL)
            alone[nm] = (q, got)
        case('record --agent-id alone reads the result from the found transcript',
             alone['a1'][0].returncode == 0 and Path(alone['a1'][1]['result']).read_text().startswith('<!-- role=builder')
             and len(lines_of(rb / '.sdlc' / 'a1')) == 1)
        case('negative control: record --agent-id with an id that has no transcript exits 2 no result yet and writes no result',
             alone['a2'][0].returncode == 2 and 'no result yet' in alone['a2'][0].stderr and not Path(alone['a2'][1]['result']).exists()
             and lines_of(rb / '.sdlc' / 'a2') == [])
        # T-0685: --agent-id with a short placeholder stdin (`echo x |`) and a complete transcript ignores the stdin with a warning; the transcript is the result.
        put(rb / '.sdlc' / 'a3' / 'handoff.md')
        rc, got, _ = prep(rb, 'builder', 'L1', '.sdlc/a3/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        q = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', '--agent-id', 'ag-solo', got['dispatch_file']],
                           capture_output=True, text=True, env=env_find, input='x\n')
        case('record --agent-id with placeholder stdin x and a complete transcript ignores the stdin and records the transcript',
             q.returncode == 0 and 'ignored stdin' in q.stderr and Path(got['result']).read_text().startswith('<!-- role=builder')
             and len(lines_of(rb / '.sdlc' / 'a3')) == 1)
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
                         q.returncode == 1 and not Path(got['result']).exists() and (R(rb / '.sdlc' / nm) / 'builder-L1.limit').is_file())
                else:
                    case('record %s: unmatched error stdin is a failure despite a complete transcript' % nm,
                         q.returncode == 1 and not Path(got['result']).exists())
        case('CLI record on a missing dispatch file exits 2', p.returncode == 2 and 'cannot read dispatch file' in p.stderr)
        rc, got, err, out = go(rb, 'builder', 'L1', '.sdlc/c2/handoff.md', body=BODY['builder'])
        case('a second attempt in a dir whose first was recorded is allowed and takes the next name', rc == 0 and got['result_name'] == 'builder-L1-2')
        p = subprocess.run([sys.executable, str(HERE / 'dispatch.py'), 'record', str(R(rb / '.sdlc' / 'c2') / 'builder-L1.dispatch.json')],
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

        # T-0661: a recorded builder leaves end-sha; the verifier's Diff range ends there, not at a later HEAD.
        re_ = mk(tmp / 'E')
        for name in ('e1', 'e2', 'e3'):
            put(re_ / '.sdlc' / name / 'handoff.md')
        eci = ['-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm']
        git('add', '-A', cwd=re_)
        git(*eci, 'handoffs', cwd=re_)
        ebase = git('rev-parse', 'HEAD', cwd=re_).stdout.strip()
        ends = lambda name: (lambda f: f.read_text() if f.is_file() else '')(R(re_ / '.sdlc' / name) / 'end-sha')

        def built(rel):
            """prepare a builder on rel; the caller edits the tree, then calls the returned record."""
            rc, got, err = prep(re_, 'builder', 'L1', rel, SDLC_DISPATCH_PARENT_PID=live_pid)
            if rc != 0:
                raise AssertionError('prepare failed in the end-sha selftest: ' + err)

            def rec():
                Path(got['result']).write_text(BODY['builder'], encoding='utf-8')
                with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                    return record(got['dispatch_file'])
            return rec
        rec = built('.sdlc/e1/handoff.md')
        (re_ / 'step1.txt').write_text('one\n')
        git('add', 'step1.txt', cwd=re_)
        git(*eci, 'step 1', cwd=re_)
        end1 = git('rev-parse', 'HEAD', cwd=re_).stdout.strip()
        erc = rec()
        (re_ / 'step2.txt').write_text('two\n')
        git('add', 'step2.txt', cwd=re_)
        git(*eci, 'step 2', cwd=re_)
        head2 = git('rev-parse', 'HEAD', cwd=re_).stdout.strip()
        vrc, dv, _ = prep(re_, 'verifier', 'L1', '.sdlc/e1/handoff.md', '--dry-run')
        case('(a) a builder recorded on a committed step writes end-sha equal to the tree HEAD',
             erc == 0 and ends('e1') == end1 + '\n')
        case('(a) a verifier prepared after a later commit gets Diff range base..that end sha, not the new HEAD',
             vrc == 0 and dv['diff_range'] == '%s..%s' % (ebase, end1) and 'Diff range: %s..%s' % (ebase, end1) in dv['prompt']
             and head2 not in dv['prompt'] and 'Diff only the Diff range below' in dv['prompt'] and 'Base sha: ' + ebase in dv['prompt'])
        stash = lambda: (git('stash', 'list', cwd=re_).stdout, git('rev-parse', '-q', '--verify', 'refs/stash', cwd=re_).stdout)
        rec = built('.sdlc/e2/handoff.md')
        (re_ / 'step3.txt').write_text('uncommitted\n')
        (re_ / 'f.txt').write_text('edited\n')
        before, staged = stash(), git('diff', '--cached', '--name-only', cwd=re_).stdout
        erc = rec()
        after = stash()
        tree2 = ends('e2').strip() or 'none'
        vrc, dv, _ = prep(re_, 'verifier', 'L1', '.sdlc/e2/handoff.md', '--dry-run')
        case('(b) an uncommitted build writes a tree hash holding its edits, and the brief names git diff <base> <tree>',
             erc == 0 and git('cat-file', '-t', tree2, cwd=re_).stdout.strip() == 'tree'
             and git('diff', '--name-only', head2, tree2, cwd=re_).stdout.split() == ['f.txt', 'step3.txt']
             and vrc == 0 and 'git diff %s %s' % (head2, tree2) in dv['prompt'] and dv['diff_range'] == '%s %s' % (head2, tree2))
        case('(b) the stash stack and the shared index are unchanged by the tree hash',
             before == after and git('diff', '--cached', '--name-only', cwd=re_).stdout == staged
             and git('status', '--porcelain', '--', 'step3.txt', cwd=re_).stdout.startswith('??'))
        vrc, dv, _ = prep(re_, 'verifier', 'L1', '.sdlc/e3/handoff.md', '--dry-run')
        case('(c) a verifier with no end-sha gets no Diff range line and keeps the Base sha rule',
             vrc == 0 and 'Diff range' not in dv['prompt'] and dv['diff_range'] is None
             and 'diff against Base sha, not HEAD' in dv['prompt'])

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
        case('a header the role wrote is replaced by the dispatch header, once', rc == 0 and head_lines[0] == '<!-- role=builder level=L1 model=opus effort=low -->'
             and not head_lines[1].startswith('<!--'))
        case('a lane_override carried by the dispatch reaches the runs.jsonl line', lines_of(rb / '.sdlc' / 'g4')[-1].get('lane_override') == 'chain needed')

        # T-0426: record removes every detached worktree under the role's own prefix and says how many; nothing else.
        for name in ('k1', 'k2', 'k3', 'k4'):
            put(rb / '.sdlc' / name / 'handoff.md')
        tmp_root = rb / '.worktrees' / 'tmp'
        rc, got, _ = prep(rb, 'verifier', 'L1', '.sdlc/k1/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        mine = [Path(got['tmp_prefix']) / 'a', Path(got['tmp_prefix']) / 'b']
        sibling, away = tmp_root / 'sibling-role' / 'wt', tmp / 'away-wt'
        for path in mine + [sibling, away]:
            subprocess.run(['git', '-C', str(rb), 'worktree', 'add', '--detach', str(path), 'HEAD'], check=True, capture_output=True)
        Path(got['result']).write_text(BODY['builder'])
        e, o = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
            rc = record(got['dispatch_file'], validate=lambda role, path: None)
        listed = subprocess.run(['git', '-C', str(rb), 'worktree', 'list', '--porcelain'], capture_output=True, text=True).stdout
        case('T-0426 a recorded role with two detached worktrees under its prefix leaves none and says cleaned: 2 tmp worktrees',
             rc == 0 and not Path(got['tmp_prefix']).exists() and not any(str(p) in listed for p in mine)
             and 'cleaned: 2 tmp worktrees' in e.getvalue())
        case('T-0426 a sibling role prefix and a worktree outside .worktrees/tmp are untouched',
             sibling.is_dir() and str(sibling) in listed and away.is_dir() and str(away) in listed)
        link, target = tmp_root / 'link-role', tmp_root / 'link-target'
        subprocess.run(['git', '-C', str(rb), 'worktree', 'add', '--detach', str(target / 'wt'), 'HEAD'], check=True, capture_output=True)
        link.symlink_to(target)
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/k2/handoff.md', body=BODY['builder'], validate=lambda role, path: None, mutate={'tmp_prefix': str(link)})
        listed = subprocess.run(['git', '-C', str(rb), 'worktree', 'list', '--porcelain'], capture_output=True, text=True).stdout
        case('T-0426 a symlinked tmp_prefix is refused with a message and nothing under it is removed',
             rc == 0 and 'refusing to remove' in err and 'symlink' in err and link.is_symlink() and (target / 'wt').is_dir()
             and str(target / 'wt') in listed and 'cleaned:' not in err)
        rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/k3/handoff.md', body=BODY['builder'], validate=lambda role, path: None, mutate={'tmp_prefix': str(tmp_root)})
        case('T-0426 a tmp_prefix equal to .worktrees/tmp itself is refused and the sibling survives',
             rc == 0 and 'refusing to remove' in err and sibling.is_dir())
        for name, bits in (('k5', ('sibling-role', 'x', '..')), ('k6', ('.',)), ('k7', ('sibling-role', 'x', '..', 'y'))):
            put(rb / '.sdlc' / name / 'handoff.md')
            (tmp_root / 'sibling-role' / 'x').mkdir(parents=True, exist_ok=True)
            odd = os.path.join(str(tmp_root), *bits)
            rc, got, err, out = go(rb, 'verifier', 'L1', '.sdlc/%s/handoff.md' % name, body=BODY['builder'], validate=lambda role, path: None, mutate={'tmp_prefix': odd})
            listed = subprocess.run(['git', '-C', str(rb), 'worktree', 'list', '--porcelain'], capture_output=True, text=True).stdout
            case('T-0426 a tmp_prefix of %s (a . or .. component) is refused and the sibling survives' % '/'.join(bits),
                 rc == 0 and 'refusing to remove' in err and 'cleaned:' not in err and sibling.is_dir() and str(sibling) in listed)
        rc, got, _ = prep(rb, 'verifier', 'L1', '.sdlc/k4/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
        failed_wt = Path(got['tmp_prefix']) / 'f'
        subprocess.run(['git', '-C', str(rb), 'worktree', 'add', '--detach', str(failed_wt), 'HEAD'], check=True, capture_output=True)
        e, o = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
            rc = record(got['dispatch_file'], no_result=True)
        case('T-0426 a failed attempt also cleans its prefix and says cleaned: 1 tmp worktrees',
             rc == 1 and not Path(got['tmp_prefix']).exists() and 'cleaned: 1 tmp worktrees' in e.getvalue())

        # T-0368 prune: prepare sets the flag per role; record queues exactly the pruneable agents; prune lists and clears the queue.
        for i, role in enumerate(PRUNE_ROLES + ('builder',)):
            put(rb / '.sdlc' / ('pf%d' % i) / 'handoff.md')
            rc, got, err = prep(rb, role, 'L1', '.sdlc/pf%d/handoff.md' % i, '--dry-run', SDLC_SPECGATE='off')
            case('prune flag: prepare sets prune %s for %s' % (role != 'builder', role), rc == 0 and got['prune'] is (role != 'builder'))
        rc, got, err = prep(rb, 'scout', 'L1', '.sdlc/pf0/handoff.md', '--dry-run', '--no-prune')
        case('prune flag: --no-prune turns a one-shot role off', rc == 0 and got['prune'] is False)
        rc, got, err = prep(rb, 'builder', 'L1', '.sdlc/pf9/handoff.md', '--dry-run', '--prune')
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
        for name in ('q1', 'q2', 'q3', 'q4', 'q4b', 'q5', 'q6', 'q7'):
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
        case('prune record: a filer whose ## Follow-ups is not None still prints prune: <name> and is queued (T-0531)',
             rc == 0 and 'prune: %s' % got['name'] in out.splitlines() and len(queued(rp)) == 2)
        rc, got, err, out = go(rp, 'verifier', 'L1', '.sdlc/q4b/handoff.md', body=BODY['verifier'] + '\n## Follow-ups\nfix-now: tidy the thing\n', agent_id='ag-w')
        case('prune record: a non-filer result with a pending follow-up is not queued (negative control)',
             rc == 0 and 'prune:' not in out and len(queued(rp)) == 2)
        rc, got, err, out = go(rp, 'filer', 'L1', '.sdlc/q5/handoff.md', body=FILER % 'None', agent_id='ag-n')
        case('prune record: a result whose follow-ups are None is queued', rc == 0 and 'prune: %s' % got['name'] in out and len(queued(rp)) == 3)
        rc, got, err, out = go(rp, 'planner', 'L1', '.sdlc/q6/handoff.md', body=BODY['planner'], agent_id='ag-x', mutate={'prune': False})
        case('prune record: a dispatch with prune false is not queued (negative control)', rc == 0 and 'prune:' not in out and len(queued(rp)) == 3)
        rc, got, err, out = go(rp, 'planner', 'L1', '.sdlc/q7/handoff.md', body=BODY['planner'], agent_id='ag-z')
        d7, a7 = json.loads(Path(got['dispatch_file']).read_text()), attempt_of(got)
        again = io.StringIO()
        sib = Path(got['artifacts_dir']) / 'planner-L1-9.attempt.json'
        sib.write_text(json.dumps({'agent_name': got['name'], 'status': 'running'}))
        with contextlib.redirect_stdout(again):
            requeued = queue_prune(d7, a7, 'ag-z')
        case('prune record: an agent with another attempt still open is not queued', requeued is False and again.getvalue() == '')
        sib.unlink()

        # T-0645 advance: record, drop the pruned verifier, steps.py next, then prepare the next role or print stop.
        def adv(tag, vbody):
            repo = mk(tmp / ('adv-' + tag))
            go(repo, 'builder', 'L2', step + '/handoff.md', body=BODY['builder'], agent_id='ag-b')
            rc, vgot, err = prep(repo, 'verifier', 'L1', step + '/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
            Path(vgot['result']).write_text(vbody, encoding='utf-8')
            before = sorted(Path(vgot['artifacts_dir']).glob('*.dispatch.json'))
            e, o = io.StringIO(), io.StringIO()
            with clean_env(SDLC_DISPATCH_PARENT_PID=live_pid), cwd(repo), contextlib.redirect_stderr(e), contextlib.redirect_stdout(o):
                try:
                    rc = main(['advance', vgot['dispatch_file'], '--agent-id', 'ag-v'])
                except SystemExit as x:  # no advance subcommand: a usage error, so each case fails rather than the run
                    rc = x.code
            after = sorted(Path(vgot['artifacts_dir']).glob('*.dispatch.json'))
            js = o.getvalue()[o.getvalue().find('\n{') + 1:] if '\n{' in o.getvalue() else ''
            return rc, vgot, o.getvalue(), json.loads(js) if js else None, before, after, prune_read(str(repo))
        def section_of(path, heading):
            import steps
            return [l for l in (steps.section(path, heading) or []) if l.strip()]
        fail_body = BODY['verifier'].replace('## Verdict\npass', '## Verdict\nfail').replace('## For the next attempt\nNone', '## For the next attempt\nfix x')
        rc, vgot, out, nxt, before, after, q = adv('fail', fail_body)
        case('T-0645 advance on a verifier fail records, prints TaskStop task_id=<verifier>, drops it from prune.json, and prints a builder dispatch JSON whose file exists',
             rc == 0 and 'TaskStop task_id=%s' % vgot['name'] in out.splitlines() and vgot['name'] not in [x['name'] for x in q]
             and attempt_of(vgot)['status'] == 'completed' and nxt is not None and nxt['role'] == 'builder' and nxt['level'] == 'L2'
             and Path(nxt['dispatch_file']).is_file() and len(after) == len(before) + 1
             and section_of(Path(vgot['handoff']), 'Previous attempt') == ['From %s:' % Path(vgot['result']).name, 'fix x'])
        rc, vgot, out, nxt, before, after, q = adv('pass', BODY['verifier'])
        case('T-0645 advance on a verifier pass prints stop: done and writes no new dispatch file',
             rc == 0 and any(l.startswith('stop: done') for l in out.splitlines()) and nxt is None and after == before
             and '## Previous attempt' not in Path(vgot['handoff']).read_text()
             and attempt_of(vgot)['status'] == 'completed')
        rc, vgot, out, nxt, before, after, q = adv('invalid', 'not a report\n')
        case('T-0645 advance on an invalid result exits 3 and prepares nothing',
             rc == 3 and nxt is None and after == before and 'TaskStop' not in out and 'stop:' not in out)
        # T-0688 advance on a ticket-level completion: an L2 solo prepares the ticket verifier, a ticket verifier pass or fail
        # prints the close or stop line.
        def adv_ticket(tag, dispatch_file, repo):
            ad = Path(json.loads(Path(dispatch_file).read_text())['artifacts_dir'])
            before = sorted(ad.glob('*.dispatch.json'))
            o = io.StringIO()
            with clean_env(SDLC_DISPATCH_PARENT_PID=live_pid), cwd(repo), contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(o):
                rc = main(['advance', dispatch_file])
            js = o.getvalue()[o.getvalue().find('{'):] if '{' in o.getvalue() else ''
            return rc, o.getvalue(), json.loads(js) if js else None, before, sorted(ad.glob('*.dispatch.json'))
        sr = mk(tmp / 'adv-solo')
        sh = (sr / '.sdlc' / 't' / 'handoff.md').resolve()
        srd = order.records_dir(sh.parent)
        srd.mkdir(parents=True, exist_ok=True)
        sdf = srd / 'solo-L2-t.dispatch.json'
        sdf.write_text(json.dumps(dict(role='solo', tier='L2', level='L2', model='opus', name='solo-L2-t', attempt_id='a' * 32,
                                       artifacts_dir=str(srd), handoff=str(sh), verifier='python3 dispatch.py prepare verifier L2 %s' % sh)))
        rc, out, nxt, before, after = adv_ticket('solo', str(sdf), sr)
        case('T-0688 advance on an L2 solo dispatch prints a ticket verifier dispatch JSON whose dispatch_file exists',
             rc == 0 and nxt is not None and nxt['role'] == 'verifier' and nxt['level'] == 'L2' and Path(nxt['dispatch_file']).is_file()
             and len(after) == len(before) + 1)
        # T-0682: record on a solo dispatch reads the report file its brief names: present, it prints the path; missing with
        # no transcript, exit 2 with the row unrecorded; missing with a transcript, the final message is written there.
        import solo_run
        def solo_rec(tag, *extra):
            sdir = tmp / ('solo-report-' + tag)
            sdir.mkdir()
            (sdir / 'handoff.md').write_text('x\n', encoding='utf-8')
            with clean_env(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                sdisp = solo_run.dispatch_json(str(sdir), 'L1', 'brief')[1]
            def go():
                o = io.StringIO()
                with clean_env(), contextlib.redirect_stdout(o), contextlib.redirect_stderr(io.StringIO()):
                    rc = main(['record', str(order.records_dir(sdir) / ('%s.dispatch.json' % sdisp['name']))] + list(extra))
                rows = [json.loads(l) for l in (order.records_dir(sdir) / 'runs.jsonl').read_text().splitlines()]
                return rc, o.getvalue(), rows[-1]
            return sdisp, go
        sdisp, go = solo_rec('file', '--tokens', '5000')
        rc0, _, row0 = go()
        Path(sdisp['result']).write_text('## Report\ndone\n', encoding='utf-8')
        rc1, out1, row1 = go()
        case('T-0682 record on a solo dispatch: no report file exits 2 with the row unpriced; with the file it prints its path, '
             'prices the row, and the runs row file names it', rc0 == 2 and row0['cost_usd'] is None and row1['cost_usd']
             and rc1 == 0 and ('solo report: %s\n' % sdisp['result']) in out1 and 'live marker cleared' in out1
             and row1['file'] == Path(sdisp['result']).name)
        stx = tmp / 'solo-report.jsonl'
        stx.write_text(json.dumps({'message': {'role': 'assistant', 'stop_reason': 'end_turn',
                                               'content': [{'type': 'text', 'text': '## Report\nfrom the transcript'}]}}) + '\n', encoding='utf-8')
        sdisp, go = solo_rec('transcript', '--transcript', str(stx))
        rc2, out2, _ = go()
        case('T-0682 record on a solo dispatch with no report file takes the transcript final message and writes it there',
             rc2 == 0 and Path(sdisp['result']).is_file() and Path(sdisp['result']).read_text() == '## Report\nfrom the transcript\n' and 'solo report: ' in out2)
        for tag, vbody, want in (('pass', BODY['verifier'], 'next: close'), ('fail', fail_body, 'stop: fail')):
            vr = mk(tmp / ('adv-t-' + tag))
            _, vgot, _ = prep(vr, 'verifier', 'L2', '.sdlc/t/handoff.md', SDLC_DISPATCH_PARENT_PID=live_pid)
            Path(vgot['result']).write_text(vbody, encoding='utf-8')
            rc, out, nxt, before, after = adv_ticket(tag, vgot['dispatch_file'], vr)
            case('T-0688 advance on a ticket-level verifier %s prints a line starting %s and writes no new dispatch file' % (tag, want),
                 rc == 0 and any(l.startswith(want) for l in out.splitlines()) and nxt is None and after == before)
        names = [e['name'] for e in queued(rp)]
        shown = prune_lines(str(rp))
        case('prune list: one TaskStop task_id=<name> line per queued agent', len(shown) == 4
             and all(l.startswith('TaskStop task_id=%s ' % n) for l, n in zip(shown, names)))
        listed = io.StringIO()
        with contextlib.redirect_stdout(listed):
            rc_list = main(['prune', '--root', str(rp)])
        case('prune command lists the queue', rc_list == 0 and listed.getvalue().count('TaskStop task_id=') == 4)
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
        # T-0601: a landed solo is queued under its dispatch name, entries carry their session, and the listing shows
        # only the current session's.
        import fanout, types
        sq = init_repo(tmp / 'solo-queue') or tmp / 'solo-queue'
        sq_lane = tmp / 'solo-queue-lane'
        subprocess.run(['git', '-C', str(sq), 'worktree', 'add', '-q', '-b', 'lane-sq', str(sq_lane)], check=True)
        put(sq_lane / '.sdlc' / 'sq1' / 'handoff.md')
        put(order.records_dir(sq_lane / '.sdlc' / 'sq1', create=True) / '0901-solo-L2.dispatch.json',
            json.dumps(dict(name='0901-solo-L2', role='solo', level='L2')))
        put(sq_lane / '.sdlc' / 'sq3' / 'T-0903-solo.dispatch.json', json.dumps(dict(name='T-0903-solo', role='solo', level='L1')))
        put(sq_lane / '.sdlc' / 'sq2' / 'handoff.md')
        sq_ctx = dict(top=sq, trel=Path('.sdlc'), lane_wt=str(sq_lane), run_id='fanout-t', logs=tmp)
        with contextlib.redirect_stdout(io.StringIO()):
            for tid, slug in (('T-0901', 'sq1'), ('T-0902', 'sq2'), ('T-0903', 'sq3')):
                fanout.queue_prune(sq_ctx, types.SimpleNamespace(name='lane-sq'), types.SimpleNamespace(id=tid, slug=slug), 'L2')
        case('T-0601 a solo landed through finish or fanout land is queued under its dispatch name (0901-solo-L2), '
             'a fanout prep dispatch keeps T-0903-solo, and no dispatch record falls back to T-0902-solo',
             [e['name'] for e in prune_read(str(sq))] == ['0901-solo-L2', 'T-0902-solo', 'T-0903-solo'])
        put(tmp / 'sq-verifier.md', '## Verdict\npass\n')
        with contextlib.redirect_stdout(io.StringIO()):
            queue_prune(dict(prune=True, name='0901-verifier-L2', role='verifier', level='L2', artifacts_dir=str(tmp),
                             attempt_file=str(tmp / 'none.attempt.json'), result=str(tmp / 'sq-verifier.md'), tree=str(sq_lane)),
                        dict(status='completed', project=str(sq_lane)), 'ag-sq')
        case('T-0601 a verifier recorded from a lane worktree is queued in the main checkout, not the lane tree',
             '0901-verifier-L2' in [e['name'] for e in prune_read(str(sq))] and not (sq_lane / PRUNE_REL).exists())
        saved_sid = os.environ.get('CLAUDE_CODE_SESSION_ID')
        try:
            ss = tmp / 'session-queue'
            put(ss / PRUNE_REL, json.dumps([dict(name='0440-architect-L1', role='architect', level='L1', recorded_at='2026-10-11'),
                                            dict(name='0500-verifier-L2', role='verifier', level='L2', session='sess-old')]))
            os.environ['CLAUDE_CODE_SESSION_ID'] = 'sess-now'
            prune_add(str(ss), '0565-solo-L2', 'solo', 'L2')
            listing = prune_lines(str(ss))
            case('T-0601 prune lists only the current session\'s entries and names --forget-stale for the 2 others',
                 len(listing) == 2 and listing[0].startswith('TaskStop task_id=0565-solo-L2 ') and 'sess-now' not in listing[0]
                 and '2 from other sessions' in listing[1] and 'dispatch.py prune --forget-stale' in listing[1]
                 and prune_read(str(ss))[-1].get('session') == 'sess-now')
            forgot = io.StringIO()
            try:
                with contextlib.redirect_stdout(forgot), contextlib.redirect_stderr(io.StringIO()):
                    rc_f = main(['prune', '--root', str(ss), '--forget-stale'])
            except SystemExit as e:
                rc_f = e.code
            case('T-0601 prune --forget-stale removes the other sessions\' entries and keeps the current one',
                 rc_f == 0 and [e['name'] for e in prune_read(str(ss))] == ['0565-solo-L2']
                 and 'forgot: 0440-architect-L1' in forgot.getvalue() and 'forgot: 0500-verifier-L2' in forgot.getvalue())
            case('T-0601 after --forget-stale the listing has no stale line (negative control)',
                 [l.split()[1] for l in prune_lines(str(ss))] == ['task_id=0565-solo-L2'])
        finally:
            if saved_sid is None:
                os.environ.pop('CLAUDE_CODE_SESSION_ID', None)
            else:
                os.environ['CLAUDE_CODE_SESSION_ID'] = saved_sid
        # T-0453: the listing names an open host lane; --done closes it through lanes.close_lane and says so.
        lr = tmp / 'lane-prune'
        init_repo(lr)
        branch = subprocess.run(['git', '-C', str(lr), 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True).stdout.strip()

        def host_lane(name, work=False):
            tree = lr / '.claude' / 'worktrees' / name
            subprocess.run(['git', '-C', str(lr), 'worktree', 'add', '-q', '-b', 'worktree-' + name, str(tree)], check=True)
            put(lr / '.worktrees' / 'host' / (name + '.lane.json'), json.dumps(dict(lane=name, kind='host', branch='worktree-' + name, into=branch)))
            if work:
                (tree / 'new.txt').write_text('w\n')
                subprocess.run(['git', '-C', str(tree), 'add', '-A'], check=True)
                subprocess.run(['git', '-C', str(tree), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
                                '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'work'], check=True)
            return os.path.realpath(str(tree))

        def run_prune(*a):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_p = main(['prune', '--root', str(lr)] + list(a))
            return rc_p, buf.getvalue().splitlines()

        landed_tree, kept_tree = host_lane('T-0901-solo'), host_lane('T-0902-solo', work=True)
        for n in ('T-0901-solo', 'T-0902-solo', 'T-0903-solo'):
            run_prune('--add', n)
        rc_l, listing = run_prune()
        case('T-0453 prune listing adds "; lane open <path>" to an entry with a host lane and not to one without',
             rc_l == 0 and listing[0].endswith('; lane open ' + landed_tree) and listing[1].endswith('; lane open ' + kept_tree)
             and 'lane open' not in listing[2])
        rc_d, done = run_prune('--done', 'T-0901-solo')
        case('T-0453 prune --done closes a landed host lane: "closed lane <path> (ancestor)", tree and branch gone',
             rc_d == 0 and done == ['pruned: T-0901-solo', 'closed lane %s (ancestor)' % landed_tree] and not Path(landed_tree).exists()
             and subprocess.run(['git', '-C', str(lr), 'rev-parse', '-q', '--verify', 'refs/heads/worktree-T-0901-solo'], capture_output=True).returncode != 0)
        rc_d, kept = run_prune('--done', 'T-0902-solo')
        case('T-0453 prune --done keeps an unlanded host lane and prints "lane still open: <path> (<reason>)" (exit unchanged)',
             rc_d == 0 and len(kept) == 2 and kept[1].startswith('lane still open: %s (not landed in %s: first new.txt' % (kept_tree, branch))
             and Path(kept_tree).is_dir())
        rc_d, none_ = run_prune('--done', 'T-0903-solo')
        case('T-0453 prune --done for an agent with no host lane prints nothing more (negative control)',
             rc_d == 0 and none_ == ['pruned: T-0903-solo'])

        # 10b. T-0414: the restart sweep, reused parent pids, and a safe prune --add.
        sw = tmp / 'sw'
        init_repo(sw)
        long_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        def attempt(rel, stem, pid, status='running', started=None, agent=None):
            path = sw / '.sdlc' / rel / (stem + '.attempt.json')
            put(path, json.dumps(dict(name=stem, agent_name=agent or stem, role='builder', level='L1', backend='claude', status=status,
                                      started_at=started or run_lifecycle.now(), parent_pid=pid, handoff=str(sw / '.sdlc' / rel / 'handoff.md'))))
            return path
        orphan_a, orphan_b = attempt('t1', 'builder-L1', dead), attempt('t2/step-1', 'builder-L1', dead)
        skipped = attempt('.worktrees/x', 'builder-L1', dead)
        liv = attempt('t3', 'verifier-L1', live)
        out_sw = io.StringIO()
        with contextlib.redirect_stdout(out_sw):
            rc_sw = main(['recover', '--root', str(sw)])
        lines_sw = out_sw.getvalue().splitlines()
        state_of = lambda path: json.loads(path.read_text(encoding='utf-8')).get('status')
        case('recover --root marks every orphan under the root interrupted and prints its prepare command',
             rc_sw == 0 and state_of(orphan_a) == state_of(orphan_b) == 'interrupted' and state_of(skipped) == 'running'
             and all(('recovered: %s' % o) in lines_sw and lines_sw[lines_sw.index('recovered: %s' % o) + 1]
                     == '  resume: python3 %s prepare builder L1 %s' % (HERE / 'dispatch.py', o.parent / 'handoff.md') for o in (orphan_a, orphan_b)))
        case('negative control: recover --root leaves a live-parent attempt running',
             state_of(liv) == 'running' and 'running: %s (pid %d)' % (liv, live) in lines_sw and 'recovered: %s' % liv not in lines_sw)
        again_sw = io.StringIO()
        with contextlib.redirect_stdout(again_sw):
            main(['recover', '--root', str(sw)])
        case('recover --root a second time recovers nothing more', again_sw.getvalue().splitlines() == ['running: %s (pid %d)' % (liv, live)])
        # T-0438: recover --open leaves a closed ticket's attempt files alone; the plain sweep still rewrites them (control)
        put(sw / '.sdlc' / 'c1' / 'handoff.md', '---\nid: T-9001\nstatus: done\n---\n')
        put(sw / '.sdlc' / 'o1' / 'handoff.md', '---\nid: T-9002\nstatus: ready\n---\n')
        closed_o, open_o = attempt('c1', 'builder-L1', dead), attempt('o1', 'builder-L1', dead)
        scoped_sw = io.StringIO()
        with contextlib.redirect_stdout(scoped_sw):
            rc_open = main(['recover', '--root', str(sw), '--open'])
        case('recover --root --open recovers an open ticket\'s orphan and leaves a closed ticket\'s attempt running',
             rc_open == 0 and state_of(open_o) == 'interrupted' and state_of(closed_o) == 'running' and 'recovered: %s' % closed_o not in scoped_sw.getvalue().splitlines())
        main(['recover', '--root', str(sw)])
        case('negative control: recover --root without --open rewrites the closed ticket\'s attempt', state_of(closed_o) == 'interrupted')
        case('orphaned: a parent pid that started after the attempt is read as dead (reused)',
             attempt_state(dict(status='running', backend='claude', parent_pid=live, started_at=long_ago)) == 'orphaned'
             and attempt_state(dict(status='running', backend='claude', parent_pid=live, started_at=run_lifecycle.now())) == 'running'
             and attempt_state(dict(status='running', backend='claude', parent_pid=live, started_at='not a time')) == 'running')
        busy = attempt('t4', 'solo-T-0414', live, agent='busy-agent')
        done = attempt('t5', 'solo-T-0415', live, status='completed', agent='done-agent')
        gone = attempt('t6', 'solo-T-0416', dead, agent='gone-agent')
        pr_err, pr_out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(pr_err), contextlib.redirect_stdout(pr_out):
            rc_busy = main(['prune', '--root', str(sw), '--add', 'busy-agent'])
            rc_done = main(['prune', '--root', str(sw), '--add', 'done-agent'])
            rc_gone = main(['prune', '--root', str(sw), '--add', 'gone-agent'])
        queued_sw = [e['name'] for e in prune_read(str(sw))]
        case('prune --add refuses an agent whose attempt is still running, exit 2',
             rc_busy == 2 and 'dispatch.py: busy-agent has a running attempt %s; record it before queueing it for pruning' % busy in pr_err.getvalue()
             and 'busy-agent' not in queued_sw)
        case('negative control: prune --add queues an agent whose attempt is completed',
             rc_done == 0 and queued_sw == ['done-agent', 'gone-agent'] and rc_gone == 0 and 'queued: done-agent' in pr_out.getvalue())

        # 11. T-0383: a recorded verdict reaches the requesting receiver with no manual conductor step, and a miss is observable.
        vr = mk(tmp / 'V')
        msgs = lambda recv, state='new': sorted((vr / '.sdlc' / 'messages' / state / recv).glob('*.md')) if (vr / '.sdlc' / 'messages' / state / recv).is_dir() else []
        mcmd = lambda *a: subprocess.run([sys.executable, str(HERE / 'messages.py')] + list(a), cwd=str(vr), capture_output=True, text=True)
        case('selftest setup: the receiver registers', mcmd('register', '--name', 'codex', '--harness', 'codex', '--reader', 'sess-1').returncode == 0)

        def notified(rel, *flags, body=BODY['verifier'], role='verifier', level='L1', record_it=True, no_result=False):
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
                out = record(got['dispatch_file'], validate=validate_result, no_result=no_result)
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
             and not (R(vr / '.sdlc' / 'n0') / 'verifier-L1.delivery.json').exists())

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
        case('attempt left running after a report: status names it report-unrecorded', any('report-unrecorded' in l for l in listed))
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
        rc, got5, _ = notified('n5', body=None, no_result=True)
        rc6, got6, _ = notified('n6', body='not a report\n')
        words = [re.search(r'^verdict: (\S+)', m.read_text(), re.M).group(1) for m in msgs('codex')[3:]]
        case('a failed sub-agent and an invalid report each deliver failed and invalid', rc == 1 and rc6 == 3 and sorted(words) == ['failed', 'invalid'])
        rcx, _, errx = prep(vr, 'verifier', 'L1', '.sdlc/n1/handoff.md', '--notify', 'Bad Name', SDLC_DISPATCH_PARENT_PID=live_pid)
        case('prepare refuses a malformed receiver name', rcx == 2 and '--notify' in errx)

        # T-0593: a plugin_min: line above the running manifest refuses with exit 2 naming both versions and the update
        # command; an equal version passes; no line means no check; the comparison is numeric per part.
        pm = tmp / 'pmin'
        nohooks = dict(CLAUDE_PLUGIN_ROOT='', SDLC_PLUGIN_CACHE=str(tmp / 'no-cache'))  # T-0596: no installed plugin in these cases
        init_repo(pm)
        put(pm / '.sdlc' / 't' / 'handoff.md')
        have = json.loads((PLUGIN / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))['version']
        parts = have.split('.')
        need = '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])
        (pm / '.sdlc' / 'config').write_text('plugin_min: %s  # the repo needs this\n' % need, encoding='utf-8')
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **nohooks)
        case('plugin_min above the manifest version: exit 2 naming %s, %s and claude plugin update' % (need, have),
             rc == 2 and need in err and have in err and 'claude plugin update' in err)
        (pm / '.sdlc' / 'config').write_text('plugin_min: %s\n' % have, encoding='utf-8')
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **nohooks)
        case('plugin_min equal to the manifest version passes', rc == 0 and 'plugin_min' not in err)
        (pm / '.sdlc' / 'config').write_text('plugin_min: 0.x\n', encoding='utf-8')
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **nohooks)
        case('a malformed plugin_min refuses with exit 2 naming it', rc == 2 and '0.x' in err)
        (pm / '.sdlc' / 'config').unlink()
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **nohooks)
        case('no plugin_min line: no check', rc == 0 and 'plugin_min' not in err)
        # T-0596: the hook plugin (CLAUDE_PLUGIN_ROOT, what the session's hooks run) below plugin_min refuses even when
        # this plugin's own manifest meets it, and the line names the hook plugin; the newest plugin cache folder stands
        # in when CLAUDE_PLUGIN_ROOT is unset.
        old = '.'.join(parts[:-1] + [str(int(parts[-1]) - 1)]) if int(parts[-1]) else '0.0.1'
        hooks = tmp / 'hooks-plugin'
        (hooks / '.claude-plugin').mkdir(parents=True)
        (hooks / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'name': 'sdlc-lite', 'version': old}), encoding='utf-8')
        (pm / '.sdlc' / 'config').write_text('plugin_min: %s\n' % have, encoding='utf-8')
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **dict(nohooks, CLAUDE_PLUGIN_ROOT=str(hooks)))
        case('plugin_min: CLAUDE_PLUGIN_ROOT at %s below plugin_min %s refuses naming the hook plugin' % (old, have),
             rc == 2 and 'hook plugin (CLAUDE_PLUGIN_ROOT)' in err and old in err and have in err and 'claude plugin update' in err)
        cache = tmp / 'cache'
        for v in (old, '0.0.1'):
            (cache / v / '.claude-plugin').mkdir(parents=True, exist_ok=True)
            (cache / v / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'version': v}), encoding='utf-8')
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **dict(nohooks, SDLC_PLUGIN_CACHE=str(cache)))
        case('plugin_min: with no CLAUDE_PLUGIN_ROOT the newest plugin cache folder below plugin_min refuses naming it',
             rc == 2 and 'hook plugin (plugin cache)' in err and old in err)
        (hooks / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'version': have}), encoding='utf-8')
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **dict(nohooks, CLAUDE_PLUGIN_ROOT=str(hooks)))
        case('plugin_min: a hook plugin that meets plugin_min passes', rc == 0 and 'plugin_min' not in err)
        # T-0679: a newer, non-orphaned version folder in the plugin cache prints one stderr line naming both versions and the
        # scripts path to re-resolve; an equal or older folder and an orphaned newer one print nothing.
        sk = tmp / 'stale-cache'
        nxt = '.'.join(parts[:-1] + [str(int(parts[-1]) + 1)])

        def stale_case(label, versions, want, orphaned=()):
            shutil.rmtree(sk, ignore_errors=True)
            for v in versions:
                (sk / v / '.claude-plugin').mkdir(parents=True, exist_ok=True)  # old is 0.0.1 at an x.y.0 release
                (sk / v / '.claude-plugin' / 'plugin.json').write_text(json.dumps({'version': v}), encoding='utf-8')
            for v in orphaned:
                (sk / v / '.orphaned_at').write_text('2026-10-21T00:50:00Z\n', encoding='utf-8')
            rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **dict(nohooks, SDLC_PLUGIN_CACHE=str(sk)))
            line = 'sdlc-lite %s in use; %s installed: re-resolve the scripts path (%s/scripts)' % (have, nxt, sk / nxt)
            case(label, rc == 0 and (err.count(line) == 1 if want else 'in use;' not in err))
        (pm / '.sdlc' / 'config').unlink()
        stale_case('stale: a newer version folder in the cache prints the one re-resolve line', (have, nxt), True)
        stale_case('stale: an equal version folder prints nothing', (have,), False)
        stale_case('stale: an older version folder prints nothing', (old, '0.0.1'), False)
        stale_case('stale: a newer version folder holding .orphaned_at prints nothing', (have, nxt), False, orphaned=(nxt,))
        rc, _, err = prep(pm, 'scout', 'L1', '.sdlc/t/handoff.md', '--dry-run', **dict(nohooks, SDLC_PLUGIN_CACHE=str(tmp / 'no-cache')))
        case('stale: no cache prints nothing', rc == 0 and 'in use;' not in err)
        case('plugin_min compares numerically per part', plugin_min.below('0.9.0', '0.10.0') and not plugin_min.below('0.10.0', '0.9.0')
             and plugin_min.below('0.23.1', '0.24') and not plugin_min.below('1.0', '1.0.0'))

        # T-0684: settle-held records an owner's settle of a `deferred: <owner>` hold; every refusal leaves the file unchanged
        sr = tmp / 'settle'
        init_repo(sr)
        put(sr / 'docs' / 'review.md', '<!-- role=ui-designer level=L1 model=opus effort=high -->\n## Verdict\npass\n')
        put(sr / 'docs' / 'review-bad.md', '## Verdict\nchanges-required\n')
        held = ('<!-- role=verifier level=L2 model=opus effort=medium -->\n## Verdict\nfail\n\n## Criteria\n'
                '- #1 `true`: pass. Evidence: ok\n- #2 the ui-designer review passes: deferred conductor. Evidence: owner stage\n\n'
                '## For the next attempt\ndeferred: conductor\n- #2 deferred\n')
        vr = sr / '.sdlc' / 't' / 'verifier-L2.md'

        def settle(text, *flags):
            put(vr, text)
            err, out = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                rc = main(['settle-held', str(vr)] + list(flags))
            return rc, vr.read_text(encoding='utf-8'), err.getvalue()
        rc, after, err = settle(held, '--by', 'conductor', '--evidence', 'docs/review.md')
        sha7 = git('rev-parse', '--short=7', 'HEAD', cwd=sr).stdout.strip()
        case('settle-held: a deferred: conductor result with a pass review record exits 0 and appends the section, got rc=%s %r'
             % (rc, after[len(held):]), rc == 0 and after == held + '\n## Settled by owner\n- ticket#2 conductor: docs/review.md at %s\n' % sha7)
        case('settle-held: the settled result still validates as a verifier result', validate_result('verifier', str(vr)) is None)
        for label, text, flags in (
                ('--by naming another owner', held, ('--by', 'integration', '--evidence', 'docs/review.md')),
                ('a missing evidence file', held, ('--by', 'conductor', '--evidence', 'docs/none.md')),
                ('an absolute evidence path', held, ('--by', 'conductor', '--evidence', str(sr / 'docs' / 'review.md'))),
                ('a review record whose Verdict is changes-required', held, ('--by', 'conductor', '--evidence', 'docs/review-bad.md')),
                ('a non-held fail', held.replace('deferred conductor', 'fail').replace('deferred: conductor', 'rebuild'),
                 ('--by', 'conductor', '--evidence', 'docs/review.md')),
                ('an unmet-dependency hold', held.replace('deferred conductor', 'unmet-dependency T-0307')
                 .replace('deferred: conductor', 'unmet-dependency: T-0307'), ('--by', 'conductor', '--evidence', 'docs/review.md'))):
            rc, after, err = settle(text, *flags)
            case('settle-held: %s exits 2 and leaves the file unchanged, got rc=%s err=%r' % (label, rc, err),
                 rc == 2 and after == text and 'nothing written' in err)
    print('dispatch selftest: %s' % ('FAIL' if failures else 'PASS'))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
