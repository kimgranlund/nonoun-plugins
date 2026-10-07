"""Ingest: walk one repo's sdlc trace sources into <out>/events.jsonl, aux.json, and cursor.json.

run(repo, lanes_dirs=(), out=None, bench_dir=None, rerun_criteria=False, thresholds=None,
    load_series=None) returns the out dir (store.out_dir). It walks:
  handoff dirs  each task dir directly under <repo>/.sdlc/ (closed .NNNN-<slug> folders and
                other `.`-prefixed folders holding a handoff.md included; `_templates`,
                `runtime`, other `_`- or `.`-prefixed names, and plain files skipped; when
                <repo>/.sdlc/config sets `ticket_root: tickets`, the `tickets` dir itself is not a
                task and each task dir under it follows as tickets/<name>, by the same filter; with
                `layout: topics` too, the `work` and `notes` dirs are not tasks either and each task
                dir under `work` follows as work/<name>), then each step-<n> and step-<n>.superseded-<k> dir under it, then any
                other subdir holding a runs.jsonl (its rows keep step None). Per dir:
                the attempt, run, and result readers, the transcript reader on each <name>.log
                next to a result <name>.md (its tool_calls, denials count, and rate_limits go on
                the result record, and the log path joins the row's sources; its loaded_context
                comes from sources/context.py, {'status': 'log absent'} when no log sits beside the
                result, used by table.join only when the run record has none), then table.join
                with the ticket id from the task dir's handoff.md front matter (tickets.parse).
                Record paths are repo-relative, so row sources and legacy ids are too.
  lanes dirs    the fanout reader on every given lanes dir plus each <repo>/.worktrees/*/ that
                holds a report.md or a logs/ dir (deduplicated by real path, in sorted order).
  aux           the git reader on repo (integration = the first report's integration worktree
                that exists), the ticket reader on <repo>/.sdlc, and the bench baseline of
                bench_dir or bench.default_bench_dir().
Each handoff dir and lanes dir is a cursor key: when its store.fingerprint equals the cursor's
(and, for a handoff dir, the ticket id it was joined with is unchanged), its rows come from the
cursor and none of its files is opened. Nothing is written outside the out dir.
With rerun_criteria, aux also gets `criteria_reruns`: rerun.run(repo, rows, thresholds), which
runs each passed step's non-guard criteria at its base-sha in throwaway worktrees it removes
again (never cached; without the flag aux has no such key and no span runs).
With load_series (a path to a JSON list of [iso timestamp, load1] pairs, the CLI's
--load-series), aux also gets `load_series`: those pairs (a pair that is not a two-item list
with a string timestamp and a numeric load is dropped; an unreadable file gives []).
"""
import json, os, pathlib

import tickets  # same scripts/ dir

from . import rerun, store, table
from .sources import attempts, bench, context, fanout, git, results, runs, transcripts
from .sources import tickets as ticket_reader

SKIP_TASK = ('_templates', 'runtime')
LANES_SUBDIRS = ('logs',)


def _rel(path, repo):
    return os.path.relpath(path, repo).replace(os.sep, '/')


def _names(d):
    """Task dir names directly under d, by the task dir filter, sorted."""
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return []
    out = []
    for n in names:
        if n in SKIP_TASK or n.startswith('_'):
            continue
        if (n.startswith('.') and not tickets.DOT_RE.fullmatch(n)
                and not os.path.isfile(os.path.join(d, n, 'handoff.md'))):
            continue
        if os.path.isdir(os.path.join(d, n)):
            out.append(n)
    return out


def task_dirs(sdlc):
    root = pathlib.Path(sdlc)
    try:
        tdir = tickets.ticket_dir(root)
    except tickets.Fail:
        tdir = root
    out = _names(sdlc)
    if tdir == root:
        return out
    try:
        lp = tickets.layout_paths(root)
    except tickets.Fail:
        lp = None
    if lp is None or lp.layout != 'topics':
        return [n for n in out if n != 'tickets'] + ['tickets/' + n for n in _names(tdir)]
    # layout: topics: tickets/, work/ and notes/ are topic folders, not tasks; work/<name> are ticket-less tasks.
    topics = (tdir.name, lp.work.name, lp.notes.parent.name)
    return ([n for n in out if n not in topics] + ['tickets/' + n for n in _names(tdir)]
            + ['work/' + n for n in _names(lp.work)])


def step_dirs(task):
    try:
        names = os.listdir(task)
    except OSError:
        return []
    found = []
    for n in names:
        m = table.STEP_DIR.match(n)
        if m and os.path.isdir(os.path.join(task, n)):
            found.append((int(m.group(1)), n))
    return [n for _, n in sorted(found)]


def other_dirs(task):
    """Non-step subdirs of a task dir that hold a runs.jsonl (e.g. verify/, old-step-3/)."""
    try:
        names = sorted(os.listdir(task))
    except OSError:
        return []
    return [n for n in names if not table.STEP_DIR.match(n)
            and os.path.isfile(os.path.join(task, n, 'runs.jsonl'))]


def _ticket(task):
    try:
        with open(os.path.join(task, 'handoff.md'), encoding='utf-8') as f:
            meta = tickets.parse(f.read())
    except (OSError, UnicodeDecodeError):
        return None
    tid = (meta or {}).get('id')
    return tid if isinstance(tid, str) and tid else None


def read_dir(repo, rel, ticket):
    """Rows of one handoff dir (rel is repo-relative), read from its files."""
    d = os.path.join(repo, rel)
    att, _ = attempts.read(d)
    run_recs, _ = runs.read(d)
    res, _ = results.read(d)
    logs = {}
    backends = {rec.get('file'): rec.get('backend') for rec in run_recs}
    for r in res:
        log = os.path.join(d, r['name'] + '.log')
        # loaded_context: a result with no log beside it is reported as 'log absent', never as [].
        r['loaded_context'] = context.read(log, backend=backends.get(r['name'] + '.md'))
        if os.path.isfile(log):
            t = transcripts.read(log)
            r['tool_calls'], r['rate_limits'] = t['tool_calls'], t['rate_limits']
            r['denials'] = len(t['denials']) if isinstance(t['denials'], list) else None
            logs[r['name']] = _rel(log, repo)
    for rec in (*att, *run_recs, *res):
        if rec.get('path'):
            rec['path'] = _rel(rec['path'], repo)
    rows = table.join(rel, att, run_recs, res, ticket=ticket)
    for row in rows:
        name = store.attempt_name(row)
        if name in logs and logs[name] not in row['sources']:
            row['sources'].append(logs[name])
    return rows


def _lanes_dirs(repo, given):
    cands = [os.path.abspath(p) for p in given]
    wt = os.path.join(repo, '.worktrees')
    try:
        names = sorted(os.listdir(wt))
    except OSError:
        names = []
    for n in names:
        p = os.path.join(wt, n)
        if os.path.isdir(p) and (os.path.isfile(os.path.join(p, 'report.md'))
                                 or os.path.isdir(os.path.join(p, 'logs'))):
            cands.append(p)
    out, seen = [], set()
    for p in cands:
        real = os.path.realpath(p)
        if real not in seen:
            seen.add(real)
            out.append(p)
    return out


def _integration(repo, lanes):
    for lane in lanes:
        w = ((lane.get('report') or {}).get('integration_worktree'))
        if not w:
            continue
        p = w if os.path.isabs(w) else os.path.join(repo, w)
        if os.path.isdir(p):
            return p
    return None


def read_load_series(path):
    """The [iso timestamp, load1] pairs of a JSON file, bad pairs dropped; [] when unreadable."""
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    out = []
    for pair in data if isinstance(data, list) else []:
        if (isinstance(pair, list) and len(pair) == 2 and isinstance(pair[0], str)
                and isinstance(pair[1], (int, float)) and not isinstance(pair[1], bool)):
            out.append([pair[0], pair[1]])
    return out


def run(repo, lanes_dirs=(), out=None, bench_dir=None, rerun_criteria=False, thresholds=None,
        load_series=None):
    store.READS = 0
    repo = os.path.abspath(repo)
    out = store.out_dir(repo, out)
    old = store.load_cursor(out)
    cursor, rows = {}, []
    sdlc = os.path.join(repo, '.sdlc')
    for tname in task_dirs(sdlc):
        task_rel = _rel(os.path.join(sdlc, tname), repo)
        task_abs = os.path.join(repo, task_rel)
        fp = store.fingerprint(task_abs)
        prev = old.get(task_rel)
        if isinstance(prev, dict) and prev.get('fingerprint') == fp:
            ticket, task_rows = prev.get('ticket'), prev.get('rows') or []
        else:
            with store.reading(task_abs):
                ticket = _ticket(task_abs)
                task_rows = read_dir(repo, task_rel, ticket)
        cursor[task_rel] = {'fingerprint': fp, 'ticket': ticket, 'rows': task_rows}
        rows.extend(task_rows)
        for sname in (*step_dirs(task_abs), *other_dirs(task_abs)):
            rel = f'{task_rel}/{sname}'
            d = os.path.join(repo, rel)
            fp = store.fingerprint(d)
            prev = old.get(rel)
            if (isinstance(prev, dict) and prev.get('fingerprint') == fp
                    and prev.get('ticket') == ticket):
                step_rows = prev.get('rows') or []
            else:
                with store.reading(d):
                    step_rows = read_dir(repo, rel, ticket)
            cursor[rel] = {'fingerprint': fp, 'ticket': ticket, 'rows': step_rows}
            rows.extend(step_rows)
    lanes = []
    for ld in _lanes_dirs(repo, lanes_dirs):
        fp = store.fingerprint(ld, LANES_SUBDIRS)
        prev = old.get(ld)
        if isinstance(prev, dict) and prev.get('fingerprint') == fp and prev.get('rows'):
            facts = prev['rows']
        else:
            with store.reading(ld):
                facts = fanout.read(ld)
        cursor[ld] = {'fingerprint': fp, 'rows': facts}
        lanes.append(facts)
    gates = [dict(g, lanes_dir=lane['lanes_dir']) for lane in lanes for g in lane['gate_logs']]
    aux = {
        'repo': repo,
        'lanes': lanes,
        'gates': gates,
        'git': git.read(repo, integration=_integration(repo, lanes)),
        'tickets': ticket_reader.read(sdlc),
        'baseline': bench.baseline(bench_dir or bench.default_bench_dir()),
    }
    if rerun_criteria:
        aux['criteria_reruns'] = rerun.run(repo, rows, thresholds)
    if load_series:
        aux['load_series'] = read_load_series(load_series)
    store.write_events(out, rows)
    store.write_aux(out, aux)
    store.write_cursor(out, cursor)
    return out
