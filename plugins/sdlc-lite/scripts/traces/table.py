"""Row schema and the per-dir join of attempt records, run records, and result records.

join(dir_rel, attempts, runs, results, ticket=None) turns the already parsed records of one
handoff dir into one row per attempt:
  attempt  the <name>.attempt.json dict plus "path"
  run      one runs.jsonl dict plus "index" (its line number) and "path"
  result   {name, status, verdict, plan_defect, ...} for one result file (name without .md)

Join rules:
  - a run record joins the attempt with the same attempt_id;
  - a run record with no attempt_id but with "file" joins the attempt whose name + ".md" is file;
  - a run record that joins nothing becomes its own row: attempt_id "legacy:<dir_rel>/<file>",
    or "legacy:<dir_rel>/runs.jsonl#<index>" with no file, status "completed", exit_code None;
  - a result record joins the row whose name matches (an unmatched result makes no row);
  - loaded_context (T-0252) is the run record's, else the result record's, else None.
Row order: attempt rows in input order, then the orphan run rows in runs.jsonl order.
Every row holds every field of ROW_FIELDS (None when unknown).
"""
import datetime, re

import order  # same scripts/ dir: RESULT is the one <role>-L<n>(-<k>).md name rule

ROW_FIELDS = ('attempt_id', 'ticket', 'task_dir', 'step', 'superseded', 'role', 'level',
              'attempt_k', 'status', 'verdict', 'plan_defect', 'turns', 'cost_usd', 'cost_estimated', 'secs',
              'tool_calls', 'denials', 'rate_limits', 'exit_code', 'loaded_context', 'sources')

STEP_DIR = re.compile(r'^step-(\d+)(\.superseded-\d+)?$')
# Counters a later reader may put on any record; the first record that has one wins.
COUNTERS = ('tool_calls', 'denials', 'rate_limits')


def _norm(dir_rel):
    return str(dir_rel).replace('\\', '/').rstrip('/') or '.'


def dir_parts(dir_rel):
    """(task_dir, step, superseded) for a handoff dir path relative to the analyzed repo."""
    d = _norm(dir_rel)
    parent, _, base = d.rpartition('/')
    m = STEP_DIR.match(base)
    if not m:
        return d, None, False
    return (parent or '.'), int(m.group(1)), bool(m.group(2))


def name_parts(name):
    """(role, level, k) from a result name like builder-L3-2 (with or without .md), else Nones."""
    if not isinstance(name, str) or not name:
        return None, None, None
    m = order.RESULT.match(name if name.endswith('.md') else name + '.md')
    if not m:
        return None, None, None
    return m.group(1), 'L' + m.group(2), int(m.group(3) or 1)


def _stamp(value):
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + '+00:00' if value.endswith('Z') else value
    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        return None


def _secs(run, attempt):
    if run is not None:
        ms = run.get('duration_ms')
        if isinstance(ms, (int, float)) and not isinstance(ms, bool):
            return ms / 1000
    if attempt is not None:
        start, end = _stamp(attempt.get('started_at')), _stamp(attempt.get('finished_at'))
        if start is not None and end is not None:
            try:
                return (end - start).total_seconds()
            except TypeError:  # naive minus aware
                return None
    return None


def _first(key, *recs):
    for rec in recs:
        if rec is not None and rec.get(key) is not None:
            return rec.get(key)
    return None


def _source(rec, fallback):
    p = rec.get('path') if rec is not None else None
    return str(p) if p else fallback


def _row(dir_rel, ticket, attempt_id, name, attempt, run, result, legacy):
    d = _norm(dir_rel)
    task_dir, step, superseded = dir_parts(d)
    n_role, n_level, k = name_parts(name)
    row = dict.fromkeys(ROW_FIELDS)
    row.update(attempt_id=attempt_id, ticket=ticket, task_dir=task_dir, step=step,
               superseded=superseded, attempt_k=k)
    row['role'] = _first('role', attempt, run) or n_role
    row['level'] = _first('level', attempt, run) or n_level
    if legacy:
        row['status'], row['exit_code'] = 'completed', None
    else:
        row['status'], row['exit_code'] = attempt.get('status'), attempt.get('exit_code')
    if result is not None:
        row['verdict'], row['plan_defect'] = result.get('verdict'), result.get('plan_defect')
    if run is not None:
        row['turns'], row['cost_usd'] = run.get('turns'), run.get('cost_usd')
        row['cost_estimated'] = run.get('cost_estimated') is True
    row['secs'] = _secs(run, attempt)
    for key in COUNTERS:
        row[key] = _first(key, run, attempt, result)
    # The run record's own list (written by run.sh) wins over the one ingest derived from the log.
    row['loaded_context'] = _first('loaded_context', run, result)
    sources = []
    if attempt is not None:
        sources.append(_source(attempt, f'{d}/{name}.attempt.json'))
    if run is not None:
        sources.append(_source(run, f'{d}/runs.jsonl'))
    if result is not None:
        sources.append(_source(result, f'{d}/{result.get("name")}.md'))
    row['sources'] = list(dict.fromkeys(sources))
    return row


def join(dir_rel, attempts, runs, results, ticket=None):
    """One row dict per attempt (and per orphan run record) for one handoff dir."""
    d = _norm(dir_rel)
    attempts = list(attempts or [])
    by_id, by_name = {}, {}
    for i, a in enumerate(attempts):
        if a.get('attempt_id'):
            by_id.setdefault(a['attempt_id'], i)
        if a.get('name'):
            by_name.setdefault(a['name'] + '.md', i)
    joined = {}  # attempt position -> run record (the last one in runs order wins)
    orphans = []
    for run in sorted(runs or [], key=lambda r: (r.get('index') is None, r.get('index') or 0)):
        aid, f = run.get('attempt_id'), run.get('file')
        if aid:
            pos = by_id.get(aid)
        elif isinstance(f, str) and f:
            pos = by_name.get(f)
        else:
            pos = None
        if pos is None:
            orphans.append(run)
        else:
            joined[pos] = run
    res = {}
    for r in results or []:
        if r.get('name'):
            res[r['name']] = r
    rows = []
    for i, a in enumerate(attempts):
        name = a.get('name')
        rows.append(_row(d, ticket, a.get('attempt_id'), name, a, joined.get(i),
                         res.get(name), legacy=False))
    for run in orphans:
        f = run.get('file')
        if isinstance(f, str) and f:
            aid, name = f'legacy:{d}/{f}', (f[:-3] if f.endswith('.md') else f)
        else:
            aid, name = f'legacy:{d}/runs.jsonl#{run.get("index")}', None
        rows.append(_row(d, ticket, aid, name, None, run, res.get(name) if name else None,
                         legacy=True))
    return rows
