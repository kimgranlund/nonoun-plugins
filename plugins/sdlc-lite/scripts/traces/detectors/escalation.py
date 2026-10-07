"""Escalation detectors: replans, recurring findings, bumps, plan-defect refusals, resume order,
and run records that do not add up.

detect(rows, aux, thresholds) returns a list of findings (findings.make, family "escalation")
over the persisted rows (events.jsonl dicts). Paths in rows are relative to aux["repo"]; the
only raw files opened are the task <task_dir>/handoff.md and the files a row's `sources` names
(result .md files and .attempt.json records). A dir listing is used for .running markers and
for order.py's result ordering (which reads the dir's runs.jsonl, itself a row source).

Row fields used: a row's `status` is the attempt lifecycle status (running, completed, failed);
a builder's Status (done, blocked, inherited) is read from the result file its sources name,
through steps.build_status_or_none, and a verifier's verdict is the row's `verdict`.

Detectors (cause_hint files are plugin-relative):
  replan-loop            a task dir with thresholds' replan_loop_planners planner rows or more,
                         or any superseded row; evidence each superseded dir's newest builder
                         (else verifier) result (order.newest) and the planner attempt ids;
                         high severity at replan_loop_high_replans replans (max of planners - 1
                         and superseded dirs). Cause agents/planner.md.
  recurring-finding      a `recurring finding:` line under `## Plan review` in the task handoff;
                         evidence that line. Cause agents/planner.md.
  unchanged-verdict-bump in one step dir: a verifier fail after a build at level n, a build at
                         level n + bump_levels, then a verifier fail whose next note (first line
                         of For the next attempt, lowercased, whitespace collapsed) equals the
                         earlier one; evidence both verifier results. Cause
                         skills/level-rubric/SKILL.md.
  plan-defect-refusal    each `## Plan review` entry (a bullet, or a paragraph with its fenced
                         blocks) holding "plan defect", grouped per handoff by each lint rule
                         its text names (RULES, else "other"): one finding per group, evidence
                         each entry's first line, cause scripts/steps.py with the rule name; and
                         each builder or verifier row with plan_defect True, evidence its result
                         file at its `plan defect:` line, cause agents/planner.md.
  wrong-resume-order     a live step n whose newest builder is blocked while a higher live step m
                         holds a builder attempt started after that blocked attempt finished;
                         evidence both attempt ids (the earliest such attempt per step m). Cause
                         skills/chain/SKILL.md.
  exit-3-result          an attempt with exit code exit_code_missing_section; evidence its id.
                         Cause agents/<role>.md.
  statusless-builder     a builder row whose result file has no Status; evidence the result.
                         Cause agents/builder.md.
  no-verdict-verifier    a verifier row with a result file and verdict None; evidence the
                         result. Cause agents/verifier.md.
  attempt-without-run-row
                         an attempt record (not legacy) whose status is not running, failed, or
                         interrupted (run.sh appends a row only after a successful result) and
                         that no runs.jsonl record joined; evidence its id and status. Cause scripts/run.sh.
  stale-running-marker   a <role>-<level>.running marker in a row's dir where that role-level has
                         attempt records and none is running (evidence the marker), or a running
                         record whose owner_pid is not alive here (os.kill(pid, 0) raises
                         ProcessLookupError; evidence its id). Cause scripts/run_lifecycle.py.
"""
import json, os, re

import order  # same scripts/ dir: newest-result ordering
import steps  # same scripts/ dir: section and status helpers

from .. import findings, table
from . import thresholds as _thresholds

FAMILY = 'escalation'
LAYER = 'sdlc-lite'

RULES = ('compares a count over a changing set', 'pins a commit sha', 'joins two checks with ||',
         'clean porcelain status', 'clean whole-tree diff', 'does not parse',
         'Read first lists a path')
PLAN_REVIEW_RE = re.compile(r'^## Plan review\b')
BULLET_RE = re.compile(r'^\s*(?:[-*+]|\d+[.)])\s+')
RECURRING_RE = re.compile(r'^\s*(?:[-*+]\s+)?recurring finding:', re.IGNORECASE)
FENCE_RE = re.compile(r'^\s*(```|~~~)')


# --- helpers -----------------------------------------------------------------------------------

class _Ctx:
    def __init__(self, rows, aux, thresholds):
        self.rows = [r for r in rows or [] if isinstance(r, dict)]
        repo = (aux or {}).get('repo') if isinstance(aux, dict) else None
        self.repo = repo if isinstance(repo, str) and repo else None
        self.t = _thresholds.merged(thresholds)
        self._json = {}
        self._lines = {}

    def sev(self, key):
        return self.t['severity'][key]

    def abs(self, rel):
        if rel is None or self.repo is None:
            return None
        return rel if os.path.isabs(rel) else os.path.join(self.repo, rel)

    def rel(self, path):
        return os.path.relpath(path, self.repo).replace(os.sep, '/')

    def attempt(self, row):
        """The parsed .attempt.json a row's sources name, else {}."""
        src = _source(row, lambda s: s.endswith('.attempt.json'))
        p = self.abs(src)
        if p is None:
            return {}
        if p not in self._json:
            try:
                with open(p, encoding='utf-8') as f:
                    d = json.load(f)
            except (OSError, ValueError):
                d = None
            self._json[p] = d if isinstance(d, dict) else {}
        return self._json[p]

    def lines(self, rel):
        p = self.abs(rel)
        if p is None:
            return []
        if p not in self._lines:
            try:
                with open(p, encoding='utf-8') as f:
                    self._lines[p] = f.read().splitlines()
            except (OSError, UnicodeDecodeError):
                self._lines[p] = []
        return self._lines[p]


def _source(row, pred):
    for s in row.get('sources') or []:
        if isinstance(s, str) and pred(s):
            return s
    return None


def _result(row):
    return _source(row, lambda s: bool(order.RESULT.match(os.path.basename(s))))


def _has_run(row):
    return _source(row, lambda s: os.path.basename(s) == 'runs.jsonl') is not None


def _row_dir(row):
    srcs = [s for s in row.get('sources') or [] if isinstance(s, str) and s]
    return os.path.dirname(srcs[0]).replace(os.sep, '/') if srcs else None


def _level(value):
    m = re.match(r'^L(\d+)$', value or '')
    return int(m.group(1)) if m else None


def _line_of(lines, pred, default=1):
    for i, line in enumerate(lines, 1):
        if pred(line):
            return i
    return default


def _norm(text):
    return ' '.join((text or '').lower().split())


def _next_note(path):
    try:
        body = steps.section(path, 'For the next attempt') or []
    except (OSError, UnicodeDecodeError):
        return ''
    return next((line.strip() for line in body if line.strip()), '')


def _build_status(ctx, row):
    p = ctx.abs(_result(row))
    return steps.build_status_or_none(p) if p and os.path.isfile(p) else None


def _by_task(rows):
    out = {}
    for r in rows:
        if r.get('task_dir'):
            out.setdefault(r['task_dir'], []).append(r)
    return dict(sorted(out.items()))


def _by_dir(rows):
    out = {}
    for r in rows:
        d = _row_dir(r)
        if d:
            out.setdefault(d, []).append(r)
    return dict(sorted(out.items()))


def _make(ctx, detector, sev_key, cause, rule, evidence, summary):
    return findings.make(detector, FAMILY, ctx.sev(sev_key), LAYER, cause, rule, evidence, summary)


def plan_review_entries(lines):
    """[(first line number, [entry lines])] for every entry under a `## Plan review` heading.
    A bullet starts an entry; a blank line ends one; a fenced block belongs to the entry it
    follows (or starts one); a non-bullet line continues the open entry or starts a new one."""
    entries, in_sec, fence, cur = [], False, False, None
    for i, line in enumerate(lines, 1):
        if not fence and line.startswith('## '):
            in_sec, cur = bool(PLAN_REVIEW_RE.match(line)), None
            continue
        if not in_sec:
            continue
        if FENCE_RE.match(line):
            fence = not fence
            if cur is None:
                cur = [i, []]
                entries.append(cur)
            cur[1].append(line)
            continue
        if fence:
            cur[1].append(line)
            continue
        if not line.strip():
            cur = None
            continue
        if cur is None or BULLET_RE.match(line):
            cur = [i, []]
            entries.append(cur)
        cur[1].append(line)
    return [(n, body) for n, body in entries]


def rules_named(text):
    low = text.lower()
    got = [r for r in RULES if r.lower() in low]
    return got or ['other']


# --- detectors ---------------------------------------------------------------------------------

def replan_loop(ctx):
    out = []
    for task, rows in _by_task(ctx.rows).items():
        planners = sorted((r for r in rows if r.get('role') == 'planner' and r.get('step') is None),
                          key=lambda r: (r.get('attempt_k') or 1, str(r.get('attempt_id'))))
        sup = sorted({_row_dir(r) for r in rows if r.get('superseded') and _row_dir(r)})
        if len(planners) < ctx.t['replan_loop_planners'] and not sup:
            continue
        evidence = []
        for d in sup:
            p = ctx.abs(d)
            newest = (order.newest(p, 'builder') or order.newest(p, 'verifier')) if p else None
            if newest:
                rel = ctx.rel(newest)
                evidence.append({'path': rel, 'line': _line_of(
                    ctx.lines(rel), lambda l: l.rstrip() in ('## Status', '## Verdict'))})
        evidence += [{'attempt_id': r['attempt_id']} for r in planners if r.get('attempt_id')]
        if not evidence:
            evidence = [{'attempt_id': r['attempt_id']} for r in rows
                        if r.get('superseded') and r.get('attempt_id')]
        if not evidence:
            continue
        replans = max(len(planners) - 1, len(sup))
        high = replans >= ctx.t['replan_loop_high_replans']
        out.append(_make(ctx, 'replan-loop', 'replan-loop-high' if high else 'replan-loop',
                         'agents/planner.md', 'replan', evidence,
                         f'{task}: {replans} replan(s): {len(planners)} planner run(s), '
                         f'{len(sup)} superseded step dir(s)'))
    return out


def recurring_finding(ctx):
    out = []
    for task in _by_task(ctx.rows):
        rel = f'{task}/handoff.md'
        for n, body in plan_review_entries(ctx.lines(rel)):
            for k, line in enumerate(body):
                if RECURRING_RE.match(line):
                    out.append(_make(ctx, 'recurring-finding', 'recurring-finding',
                                     'agents/planner.md', 'recurring finding',
                                     [{'path': rel, 'line': n + k}],
                                     f'{rel}:{n + k}: {line.strip()[:160]}'))
    return out


def _timeline(d):
    """Builder and verifier result paths of d, merged in run order (order.counts_after)."""
    bs, vs = order.ordered(d, 'builder'), order.ordered(d, 'verifier')
    out, i, j = [], 0, 0
    while i < len(bs) or j < len(vs):
        if j >= len(vs):
            take_b = True
        elif i >= len(bs):
            take_b = False
        else:
            b, v = bs[i], vs[j]
            take_b = not (order.counts_after(b, v) and not order.counts_after(v, b))
        if take_b:
            out.append(('builder', bs[i]))
            i += 1
        else:
            out.append(('verifier', vs[j]))
            j += 1
    return out


def unchanged_verdict_bump(ctx):
    out = []
    step_rows = [r for r in ctx.rows if r.get('step') is not None]
    for d, rows in _by_dir(step_rows).items():
        p = ctx.abs(d)
        if not p or not os.path.isdir(p):
            continue
        by_result = {_result(r): r for r in rows if _result(r)}
        level, prev = None, None
        for kind, path in _timeline(p):
            rel = ctx.rel(path)
            if kind == 'builder':
                level = _level(table.name_parts(os.path.basename(path))[1])
                continue
            row = by_result.get(rel)
            if row is None or row.get('verdict') != 'fail' or level is None:
                continue
            note = _norm(_next_note(path))
            if (prev and note and note == prev[2]
                    and level == prev[1] + ctx.t['bump_levels']):
                out.append(_make(
                    ctx, 'unchanged-verdict-bump', 'unchanged-verdict-bump',
                    'skills/level-rubric/SKILL.md', 'bump on a recurring finding',
                    [{'path': prev[0], 'line': _line_of(
                        ctx.lines(prev[0]), lambda l: l.rstrip() == '## For the next attempt')},
                     {'path': rel, 'line': _line_of(
                         ctx.lines(rel), lambda l: l.rstrip() == '## For the next attempt')}],
                    f'{d}: the L{level} build failed with the same note as the '
                    f'L{prev[1]} build: {note[:120]}'))
            prev = (rel, level, note)
    return out


def plan_defect_refusal(ctx):
    out = []
    for task in _by_task(ctx.rows):
        rel = f'{task}/handoff.md'
        groups = {}
        for n, body in plan_review_entries(ctx.lines(rel)):
            text = '\n'.join(body)
            if 'plan defect' not in text.lower():
                continue
            for rule in rules_named(text):
                groups.setdefault(rule, []).append(n)
        for rule, lines in groups.items():
            out.append(_make(ctx, 'plan-defect-refusal', 'plan-defect-refusal', 'scripts/steps.py',
                             rule, [{'path': rel, 'line': n} for n in lines],
                             f'{rel}: {len(lines)} plan review entr'
                             f'{"y" if len(lines) == 1 else "ies"} with a plan defect ({rule})'))
    for r in ctx.rows:
        if r.get('role') not in ('builder', 'verifier') or r.get('plan_defect') is not True:
            continue
        rel = _result(r)
        if not rel:
            continue
        line = _line_of(ctx.lines(rel), lambda l: l.strip().lower().startswith('plan defect:'))
        out.append(_make(ctx, 'plan-defect-refusal', 'plan-defect-refusal', 'agents/planner.md',
                         f'{r["role"]} plan defect', [{'path': rel, 'line': line}],
                         f'{rel}: the {r["role"]} reported a plan defect'))
    return out


def wrong_resume_order(ctx):
    out = []
    for task, rows in _by_task(ctx.rows).items():
        live = [r for r in rows if r.get('step') is not None and not r.get('superseded')]
        dirs = {}
        for r in live:
            d = _row_dir(r)
            if d:
                dirs.setdefault(r['step'], (d, []))[1].append(r)
        for n, (d, nrows) in sorted(dirs.items()):
            p = ctx.abs(d)
            newest = order.newest(p, 'builder') if p and os.path.isdir(p) else None
            if not newest:
                continue
            blocked = next((r for r in nrows if r.get('role') == 'builder'
                            and _result(r) == ctx.rel(newest)), None)
            if blocked is None or not blocked.get('attempt_id') \
                    or _build_status(ctx, blocked) != 'blocked':
                continue
            done = table._stamp(ctx.attempt(blocked).get('finished_at'))
            if done is None:
                continue
            for m, (_, mrows) in sorted(dirs.items()):
                if m <= n:
                    continue
                later = []
                for r in mrows:
                    if r.get('role') != 'builder' or not r.get('attempt_id'):
                        continue
                    start = table._stamp(ctx.attempt(r).get('started_at'))
                    try:
                        if start is not None and start > done:
                            later.append((start, r['attempt_id']))
                    except TypeError:  # naive against aware
                        continue
                if not later:
                    continue
                first = min(later)[1]
                out.append(_make(ctx, 'wrong-resume-order', 'wrong-resume-order',
                                 'skills/chain/SKILL.md', 'resume from the blocked step',
                                 [{'attempt_id': blocked['attempt_id']}, {'attempt_id': first}],
                                 f'{task}: step {m} built after step {n} blocked, '
                                 f'with no replan in between'))
    return out


def exit_3_result(ctx):
    code = ctx.t['exit_code_missing_section']
    out = []
    for r in ctx.rows:
        if r.get('exit_code') == code and r.get('attempt_id'):
            role = r.get('role')
            out.append(_make(ctx, 'exit-3-result', 'exit-3-result',
                             f'agents/{role}.md' if role else None, 'required output section',
                             [{'attempt_id': r['attempt_id']}],
                             f'{r["attempt_id"]}: {role or "a role"} exited {code}: its result '
                             'lacks a required section'))
    return out


def statusless_builder(ctx):
    out = []
    for r in ctx.rows:
        rel = _result(r)
        if r.get('role') != 'builder' or not rel or not os.path.isfile(ctx.abs(rel) or ''):
            continue
        if _build_status(ctx, r) is None:
            out.append(_make(ctx, 'statusless-builder', 'statusless-builder', 'agents/builder.md',
                             '## Status', [{'path': rel, 'line': 1}],
                             f'{rel}: builder result has no Status'))
    return out


def no_verdict_verifier(ctx):
    out = []
    for r in ctx.rows:
        rel = _result(r)
        if r.get('role') != 'verifier' or not rel or r.get('verdict') is not None:
            continue
        out.append(_make(ctx, 'no-verdict-verifier', 'no-verdict-verifier', 'agents/verifier.md',
                         '## Verdict', [{'path': rel, 'line': 1}],
                         f'{rel}: verifier result has no verdict'))
    return out


def attempt_without_run_row(ctx):
    out = []
    for r in ctx.rows:
        aid = r.get('attempt_id')
        if not isinstance(aid, str) or not aid or aid.startswith('legacy:'):
            continue
        if not _source(r, lambda s: s.endswith('.attempt.json')) or _has_run(r):
            continue
        status = r.get('status')
        if status in ('running', 'failed', 'interrupted'):
            continue
        out.append(_make(ctx, 'attempt-without-run-row', 'attempt-without-run-row', 'scripts/run.sh', 'runs.jsonl row',
                         [{'attempt_id': aid, 'status': status}],
                         f'{aid}: attempt {status or "with no status"} has no runs.jsonl row'))
    return out


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (OSError, OverflowError, ValueError, TypeError):
        return True  # exists under another user, or not checkable: never a finding
    return True


def stale_running_marker(ctx):
    out = []
    for d, rows in _by_dir(ctx.rows).items():
        p = ctx.abs(d)
        try:
            names = sorted(os.listdir(p)) if p else []
        except OSError:
            names = []
        for name in names:
            if not name.endswith('.running'):
                continue
            role, level, _ = table.name_parts(name[:-len('.running')])
            recs = [r for r in rows if (r.get('role'), r.get('level')) == (role, level)
                    and _source(r, lambda s: s.endswith('.attempt.json'))]
            if not recs or any(r.get('status') == 'running' for r in recs):
                continue
            rel = f'{d}/{name}'
            out.append(_make(ctx, 'stale-running-marker', 'stale-running-marker',
                             'scripts/run_lifecycle.py', '.running marker',
                             [{'path': rel, 'line': 1}],
                             f'{rel}: marker left behind; no {role}-{level} attempt is running'))
    for r in ctx.rows:
        if r.get('status') != 'running' or not r.get('attempt_id'):
            continue
        pid = ctx.attempt(r).get('owner_pid')
        if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 or _alive(pid):
            continue
        out.append(_make(ctx, 'stale-running-marker', 'stale-running-marker',
                         'scripts/run_lifecycle.py', 'owner_pid',
                         [{'attempt_id': r['attempt_id'], 'owner_pid': pid}],
                         f'{r["attempt_id"]}: running record whose owner pid {pid} is gone'))
    return out


DETECTORS = (
    ('replan-loop', replan_loop),
    ('recurring-finding', recurring_finding),
    ('unchanged-verdict-bump', unchanged_verdict_bump),
    ('plan-defect-refusal', plan_defect_refusal),
    ('wrong-resume-order', wrong_resume_order),
    ('exit-3-result', exit_3_result),
    ('statusless-builder', statusless_builder),
    ('no-verdict-verifier', no_verdict_verifier),
    ('attempt-without-run-row', attempt_without_run_row),
    ('stale-running-marker', stale_running_marker),
)


def detect(rows, aux, thresholds=None):
    ctx = _Ctx(rows, aux, thresholds)
    out = []
    for _, fn in DETECTORS:
        out.extend(fn(ctx))
    return out
