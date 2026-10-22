"""Hygiene detectors: stray worktrees, tracked runtime files, reset integration trees, stale or
overwritten fanout logs, ticket id collisions, and external branches nobody registered.

detect(rows, aux, thresholds) returns a list of findings (findings.make, family "hygiene") over
the git, lanes, and ticket facts in aux.json (ingest.run): aux["git"] (sources/git.read),
aux["lanes"] (one sources/fanout.read per lanes dir), and aux["tickets"] (sources/tickets.read of
<repo>/.sdlc). rows is unused. Evidence paths under aux["repo"] are repo-relative, others stay
absolute; an evidence entry with no line number in a file carries line None. The only raw files
opened are a report.md and <repo>/.sdlc/config, to find the line an external branch sits on, and
<repo>/docs/layout.md, for the reports homes; the only other filesystem reads are whether a report's
integration worktree still exists and whether a worktree holds a KEEP_MARKER or a .lane.json.

A lost-edit signal of a lanes dir: a report row or fanout.log line whose outcome is `red: ... rc=<n>`
or starts `integration dirty`, a report Commit cell or fanout.log line starting `wip `, and (for
the lanes dir whose integration worktree git.read took the reflog from) a `wip(<id>): ...` commit
in aux["git"]["commits"].

Detectors (cause_hint files are plugin-relative):
  stray-worktree       a worktree whose path holds a legacy worktree root (`.claude/worktrees/` or `.worktrees/`)
                       twice or lies under its `tmp/`, and holds no KEEP_MARKER file at its root (a
                       repo's opt-out for an intentional worktree); evidence the path. Cause scripts/run.sh.
  tracked-runtime-file each git tracked_runtime path outside the evidence dirs (docs/evidence/ and
                       docs/<home>/ for each home of kind `reports` in docs/layout.md, where dated
                       evidence logs are tracked on purpose); evidence the path. Cause
                       skills/handoff-format/SKILL.md.
  integration-reset    per `reset: moving to` reflog entry, when the first lanes dir whose report
                       names an integration worktree that exists (the one ingest read the reflog
                       from) has a lost-edit signal; evidence the reflog entry and the first signal.
                       Cause scripts/fanout.py.
  reflog-gone          (severity 1, instead of integration-reset) per lanes dir whose report names
                       an integration worktree that no longer exists and that has a lost-edit
                       signal; evidence the report's Integration worktree line and the signal.
                       Cause scripts/fanout.py.
  stale-log-lines      a driver or gate log whose lines carry two or more distinct run ids
                       (evidence the log at the first line of the second id), or whose lines
                       carry no run id at all (legacy, severity 1; evidence the log). Cause
                       scripts/fanout.py.
  overwritten-gate-log a legacy gate-<lane>-<id>-<k>.log name with no -a<n> (severity 1);
                       evidence the log. Cause scripts/fanout.py.
  ticket-id-collision  each `duplicate id` ticket problem line; evidence the ticket root and the
                       line. Cause scripts/tickets.py.
  unregistered-external-branch
                       a report's external lane branch absent from the registered
                       `external_branch` names, unless its lanes dir's land.jsonl names it (a lane
                       `fanout.py land` merged) or a worktree on it holds a .lane.json (evidence the
                       report line), and a registered name
                       with no local branch (evidence the config line). Cause scripts/tickets.py.
"""
import os

import docs_check  # same scripts/ dir: the docs layout's reports homes
import tickets  # same scripts/ dir: the external_branch config line

from .. import findings
from ..sources import fanout as fanout_src
from ..sources import git as git_src
from . import thresholds as _thresholds

FAMILY = 'hygiene'
LAYER = 'sdlc-lite'

DIRTY = 'integration dirty'
WIP_COMMIT = 'wip('
WIP_CELL = 'wip '
DUPLICATE = 'duplicate id'
KEEP_MARKER = '.sdlc-keep'  # at a worktree's root: the worktree is intentional, never a stray
EVIDENCE_DIRS = ('docs/evidence/',)

DETECTORS = ('stray-worktree', 'tracked-runtime-file', 'integration-reset', 'reflog-gone',
             'stale-log-lines', 'overwritten-gate-log', 'ticket-id-collision',
             'unregistered-external-branch')


class _Ctx:
    def __init__(self, aux, thresholds):
        aux = aux if isinstance(aux, dict) else {}
        repo = aux.get('repo')
        self.repo = repo if isinstance(repo, str) and repo else None
        self.t = _thresholds.merged(thresholds)
        self.git = aux.get('git') if isinstance(aux.get('git'), dict) else {}
        self.lanes = [x for x in aux.get('lanes') or [] if isinstance(x, dict)]
        self.tickets = aux.get('tickets') if isinstance(aux.get('tickets'), dict) else {}
        self._lines = {}

    def sev(self, key):
        return self.t['severity'][key]

    def abs(self, path):
        if not isinstance(path, str) or not path:
            return None
        if os.path.isabs(path) or self.repo is None:
            return path
        return os.path.join(self.repo, path)

    def rel(self, path):
        """path relative to the repo when it lies inside it, else as given."""
        if self.repo is None or not isinstance(path, str) or not os.path.isabs(path):
            return path
        r = os.path.relpath(path, self.repo)
        return path if r == '..' or r.startswith('..' + os.sep) else r.replace(os.sep, '/')

    def lines(self, path):
        p = self.abs(path)
        if p is None:
            return []
        if p not in self._lines:
            try:
                with open(p, encoding='utf-8', errors='replace') as f:
                    self._lines[p] = f.read().splitlines()
            except OSError:
                self._lines[p] = []
        return self._lines[p]


def _make(ctx, detector, cause, rule, evidence, summary, sev_key=None):
    return findings.make(detector, FAMILY, ctx.sev(sev_key or detector), LAYER, cause, rule,
                         evidence, summary)


def _ev(ctx, path, line=None, **extra):
    return dict({'path': ctx.rel(path), 'line': line}, **extra)


# --- detectors ---------------------------------------------------------------------------------

def stray_worktree(ctx):
    out = []
    for w in ctx.git.get('worktrees') or []:
        path = w.get('path') if isinstance(w, dict) else None
        if not isinstance(path, str) or not path:
            continue
        if not (w.get('nested') or git_src.nested(path)):
            continue
        if os.path.isfile(os.path.join(ctx.abs(path), KEEP_MARKER)):
            continue
        rel = ctx.rel(path)
        out.append(_make(ctx, 'stray-worktree', 'scripts/run.sh',
                         'runner temporary worktrees live under SDLC_TMP_WORKTREES and are removed',
                         [_ev(ctx, path)], f'{rel}: nested or leftover temporary worktree'))
    return out


def _evidence_dirs(ctx):
    dirs = list(EVIDENCE_DIRS)
    if ctx.repo:
        try:
            kinds, _ = docs_check.home_kinds(docs_check.load_layout(ctx.repo))
        except Exception:  # a malformed layout leaves the default dir only
            kinds = {}
        dirs += [f'docs/{h}/' for h, kind in kinds.items() if kind == 'reports']
    return dirs


def tracked_runtime_file(ctx):
    out = []
    evidence = _evidence_dirs(ctx)
    for path in ctx.git.get('tracked_runtime') or []:
        if not isinstance(path, str) or not path or path.startswith(tuple(evidence)):
            continue
        out.append(_make(ctx, 'tracked-runtime-file', 'skills/handoff-format/SKILL.md',
                         'runtime files (.log, .running, .run.lock, .board-state.json) are ignored',
                         [{'path': path, 'line': None}], f'{path}: runtime file is tracked by git'))
    return out


def _outcome_signal(text):
    text = text or ''
    return bool(fanout_src.RED_RE.match(text)) or text.startswith(DIRTY) \
        or text.startswith(WIP_CELL)


def _line_signals(ctx, lane):
    """[(evidence, text)] of the lost-edit signals in one lanes dir's report rows and fanout.log."""
    out = []
    rep = lane.get('report') if isinstance(lane.get('report'), dict) else None
    for r in (rep or {}).get('rows') or []:
        commit = r.get('commit') or ''
        if _outcome_signal(r.get('outcome')) or commit.startswith(WIP_CELL):
            out.append((_ev(ctx, rep['path'], r.get('line')),
                        f'{r.get("lane")} {r.get("ticket")} {r.get("outcome")} {commit}'.strip()))
    for e in lane.get('fanout_log') or []:
        if e.get('lane') and _outcome_signal(e.get('event')):
            out.append((_ev(ctx, e['path'], e.get('line')),
                        f'{e.get("lane")} {e.get("ticket")} {e.get("event")}'))
    return out


def _wip_commits(ctx):
    out = []
    for c in ctx.git.get('commits') or []:
        if isinstance(c, (list, tuple)) and len(c) == 2 and str(c[1]).startswith(WIP_COMMIT):
            where = ctx.repo or '.'
            out.append((_ev(ctx, where, None, commit=f'{c[0]} {c[1]}'), c[1]))
    return out


def _integration(ctx, lane):
    """(named path, exists) of a lanes dir's integration worktree; (None, False) if none named."""
    w = ((lane.get('report') or {}).get('integration_worktree'))
    if not isinstance(w, str) or not w:
        return None, False
    p = ctx.abs(w)
    return p, bool(p) and os.path.isdir(p)


def _report_line(ctx, rep, prefix, needle=''):
    for i, line in enumerate(ctx.lines(rep.get('path')), 1):
        s = line.strip()
        if s.startswith(prefix) and needle in s:
            return i
    return None


def integration_reset(ctx):
    out = []
    live_done = False
    resets = [r for r in ctx.git.get('resets') or [] if isinstance(r, (list, tuple)) and len(r) == 2]
    for lane in ctx.lanes:
        where, exists = _integration(ctx, lane)
        if where is None:
            continue
        signals = _line_signals(ctx, lane)
        if exists:
            if live_done:  # git.read took the reflog from the first existing one only
                continue
            live_done = True
            signals += _wip_commits(ctx)
            if not signals:
                continue
            sig_ev, sig_text = signals[0]
            for sha, subject in resets:
                out.append(_make(ctx, 'integration-reset', 'scripts/fanout.py',
                                 'a gate reset must not discard a lane edit',
                                 [_ev(ctx, where, None, reflog=f'{sha} {subject}'), sig_ev],
                                 f'{ctx.rel(where)}: {subject} with a lost-edit signal: '
                                 f'{sig_text}'))
        elif signals:
            rep = lane['report']
            sig_ev, sig_text = signals[0]
            line = _report_line(ctx, rep, '- Integration worktree:')
            out.append(_make(ctx, 'reflog-gone', 'scripts/fanout.py',
                             'the integration reflog is gone, so a reset cannot be checked',
                             [_ev(ctx, rep['path'], line, worktree=where), sig_ev],
                             f'{where}: integration worktree is gone; a lost-edit signal '
                             f'({sig_text}) cannot be checked against its reflog'))
    return out


def stale_log_lines(ctx):
    out = []
    for lane in ctx.lanes:
        for log in list(lane.get('driver_logs') or []) + list(lane.get('gate_logs') or []):
            path, ids = log.get('path'), log.get('run_ids') or []
            if not path or not ids:
                continue
            named = [i for i in ids if i]
            if len(named) >= 2:
                second = named[1]
                line = next((ln for rid, ln in log.get('run_id_lines') or [] if rid == second),
                            None)
                out.append(_make(ctx, 'stale-log-lines', 'scripts/fanout.py',
                                 'a log holds the lines of one run only',
                                 [_ev(ctx, path, line)],
                                 f'{ctx.rel(path)}: lines from {len(named)} runs '
                                 f'({", ".join(named)})'))
            elif not named:
                out.append(_make(ctx, 'stale-log-lines', 'scripts/fanout.py',
                                 'log lines carry the run id prefix',
                                 [_ev(ctx, path)],
                                 f'{ctx.rel(path)}: legacy log, no line carries a run id',
                                 sev_key='stale-log-lines-legacy'))
    return out


def overwritten_gate_log(ctx):
    out = []
    for lane in ctx.lanes:
        for g in lane.get('gate_logs') or []:
            if g.get('path') and g.get('attempt') is None:
                out.append(_make(ctx, 'overwritten-gate-log', 'scripts/fanout.py',
                                 'one gate log per attempt (gate-<lane>-<id>-<k>-a<n>.log)',
                                 [_ev(ctx, g['path'])],
                                 f'{ctx.rel(g["path"])}: legacy gate log name, overwritten '
                                 'on every run'))
    return out


def _ticket_root(ctx):
    root = ctx.tickets.get('root')
    if isinstance(root, str) and root:
        return root
    return os.path.join(ctx.repo, '.sdlc') if ctx.repo else '.sdlc'


def ticket_id_collision(ctx):
    out = []
    root = _ticket_root(ctx)
    for p in ctx.tickets.get('problems') or []:
        if isinstance(p, str) and DUPLICATE in p:
            out.append(_make(ctx, 'ticket-id-collision', 'scripts/tickets.py',
                             'ticket ids are unique across worktrees',
                             [_ev(ctx, root, None, problem=p)], f'{ctx.rel(root)}: {p}'))
    return out


def _config_line(ctx, config, name):
    for i, line in enumerate(ctx.lines(config), 1):
        m = tickets.EXTERNAL_RE.fullmatch(line)
        if m and m.group(1) == name:
            return i
    return None


def unregistered_external_branch(ctx):
    out = []
    registered = [b for b in ctx.tickets.get('external') or [] if isinstance(b, str)]
    recorded = {w.get('branch') for w in ctx.git.get('worktrees') or [] if isinstance(w, dict)
                and isinstance(w.get('path'), str) and w.get('branch')
                and os.path.isfile(os.path.join(ctx.abs(w['path']), '.lane.json'))}
    for lane in ctx.lanes:
        rep = lane.get('report') if isinstance(lane.get('report'), dict) else None
        landed = lane.get('landed') or []
        for x in (rep or {}).get('external') or []:
            branch = x.get('branch')
            if not branch or branch in registered or branch in landed or branch in recorded:
                continue
            line = _report_line(ctx, rep, f'- Lane `{x.get("lane")}`:', 'external branch')
            out.append(_make(ctx, 'unregistered-external-branch', 'scripts/tickets.py',
                             'an external lane branch is registered with external_branch:',
                             [_ev(ctx, rep['path'], line, branch=branch)],
                             f'{ctx.rel(rep["path"])}: external branch {branch} is not '
                             'registered in the ticket config'))
    branches = ctx.git.get('branches') or []
    if branches:  # an empty list means git.read failed, not that every branch is gone
        config = os.path.join(_ticket_root(ctx), 'config')
        for name in registered:
            if name in branches:
                continue
            out.append(_make(ctx, 'unregistered-external-branch', 'scripts/tickets.py',
                             'a registered external branch exists locally',
                             [_ev(ctx, config, _config_line(ctx, config, name), branch=name)],
                             f'{ctx.rel(config)}: registered external branch {name} has no '
                             'local branch'))
    return out


def detect(rows, aux, thresholds=None):
    ctx = _Ctx(aux, thresholds)
    out = stray_worktree(ctx)
    out += tracked_runtime_file(ctx)
    out += integration_reset(ctx)
    out += stale_log_lines(ctx)
    out += overwritten_gate_log(ctx)
    out += ticket_id_collision(ctx)
    out += unregistered_external_branch(ctx)
    return out
