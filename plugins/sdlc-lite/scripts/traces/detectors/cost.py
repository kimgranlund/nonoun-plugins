"""Cost and transcript detectors: expensive steps, repeated builds, polling loops, idle loop
wakes, background denials, and rate limits.

detect(rows, aux, thresholds) returns (findings, notes): a list of findings (findings.make,
family "cost") over the persisted rows (events.jsonl dicts) and aux.json, and a list of note
strings for what could not be judged. Paths in rows are relative to aux["repo"]; the only raw
files opened are the transcript .log files a row's sources names (sources/transcripts.read) and
the runs.jsonl order.newest reads to find a step dir's newest verifier.

A step here is one handoff dir (step-<n> or step-<n>.superseded-<k>); its rows are the rows whose
sources lie in that dir.

Detectors (cause_hint files are plugin-relative):
  cost-over-baseline    a live step dir whose newest verifier (order.newest) has verdict pass,
                        when the sum of cost_usd over its rows divided by
                        aux["baseline"]["median_cost_per_passed_step"] is at least
                        cost_over_baseline_ratio; evidence each row's attempt id, the first
                        entry also carrying ratio (2 decimals), cost_usd, and baseline. With no
                        positive baseline there is no finding and the note
                        `cost-over-baseline: no baseline`. Cause skills/level-rubric/SKILL.md.
  many-builder-attempts a step dir with at least many_builder_attempts builder rows; evidence
                        their attempt ids. Cause skills/level-rubric/SKILL.md.
  polling-loop          a transcript with at least polling_loop_calls Bash calls whose
                        whitespace-collapsed command is identical, or that all match POLL_RE (the
                        larger such group counts); evidence {attempt_id, calls, secs, load}:
                        secs is the seconds between the group's first and last call timestamps
                        (None when either does not parse), load the load1 value of
                        aux["load_series"] (a list of [iso timestamp, load1] pairs, ingest's
                        load_series) nearest the first call, else "unknown". Cause
                        agents/conductor.md.
  idle-wakes            a conductor session transcript (a Claude Code session .jsonl named in
                        aux["conductor_transcripts"], ingest's --conductor-transcript) with at
                        least idle_wakes_turns idle fired turns. A turn starts at a user event
                        whose promptId differs from the current turn's; it is fired when that
                        event carries scheduledTaskId (a /loop or cron fire). A fired turn is
                        idle when it makes no Agent call and no Bash call matching ACTION_RE
                        (dispatch, record, land, close), and its board output (the tool results
                        of Bash calls matching BOARD_RE) is absent or equals the last board
                        output seen. Evidence one {path, line} per idle turn, line the 1-based
                        line of its fired event. Cause skills/plan-loop/references/loop-rules.md.
  background-denial     a transcript with hook denials whose stderr names run_in_background,
                        Agent, or Monitor; evidence {attempt_id, count}. Cause
                        hooks/block-background.sh.
  rate-limit            a row with rate_limits of at least 1; evidence {attempt_id, count}.
                        Layer host, cause file None.
"""
import datetime, json, os, re

import order  # same scripts/ dir: newest-result ordering

from .. import findings
from ..sources import transcripts
from .escalation import _Ctx, _result, _row_dir, _source

FAMILY = 'cost'
LAYER = 'sdlc-lite'

POLL_RE = re.compile(r'^(sleep|kill -0|ls .*\.running|test -e .*\.running)')
ACTION_RE = re.compile(r'\b(dispatch\.py\s+(prepare|record)|solo_run\.py|fanout\.py\s+(prep|land|run)'
                       r'|lanes\.py\s+(open|land|ready)|tickets\.py\s+close)\b')
BOARD_RE = re.compile(r'\b(rag)?board\.py\b')
BACKGROUND_RE = re.compile(r'\b(run_in_background|Agent|Monitor)\b')
NO_BASELINE = 'cost-over-baseline: no baseline'


def _make(ctx, detector, layer, cause, rule, evidence, summary):
    return findings.make(detector, FAMILY, ctx.sev(detector), layer, cause, rule, evidence,
                         summary)


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _stamp(value):
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + '+00:00' if value.endswith('Z') else value
    try:
        t = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


def _step_dirs(rows):
    """{step dir: [rows]} for rows in a step-<n> handoff dir, in row order."""
    out = {}
    for r in rows:
        d = _row_dir(r)
        if r.get('step') is not None and d:
            out.setdefault(d, []).append(r)
    return out


def _transcript(ctx, row):
    log = _source(row, lambda s: s.endswith('.log'))
    p = ctx.abs(log)
    return transcripts.read(p) if p else None


# --- detectors ---------------------------------------------------------------------------------

def _baseline(aux):
    b = aux.get('baseline') if isinstance(aux, dict) else None
    v = b.get('median_cost_per_passed_step') if isinstance(b, dict) else None
    return v if _num(v) and v > 0 else None


def _passed(ctx, d, rows):
    p = ctx.abs(d)
    newest = order.newest(p, 'verifier') if p else None
    if not newest:
        return False
    name = os.path.basename(newest)
    return any(r.get('role') == 'verifier' and r.get('verdict') == 'pass'
               and os.path.basename(_result(r) or '') == name for r in rows)


def cost_over_baseline(ctx, aux, notes):
    base = _baseline(aux)
    if base is None:
        notes.append(NO_BASELINE)
        return []
    out = []
    for d, rows in sorted(_step_dirs(ctx.rows).items()):
        if rows[0].get('superseded') or not _passed(ctx, d, rows):
            continue
        costs = [r['cost_usd'] for r in rows if _num(r.get('cost_usd'))]
        if not costs:
            continue
        total = sum(costs)
        ratio = round(total / base, 2)
        if ratio < ctx.t['cost_over_baseline_ratio']:
            continue
        ids = [r['attempt_id'] for r in rows if r.get('attempt_id')]
        if not ids:
            continue
        ev = [{'attempt_id': ids[0], 'ratio': ratio, 'cost_usd': round(total, 4),
               'baseline': base, 'estimated': any(r.get('cost_estimated') is True for r in rows)}] + [{'attempt_id': a} for a in ids[1:]]
        out.append(_make(ctx, 'cost-over-baseline', LAYER, 'skills/level-rubric/SKILL.md',
                         'pick the lowest level that passes',
                         ev, f'{d}: passed step cost ${total:.2f}, {ratio}x the bench median '
                             f'${base:.2f}'))
    return out


def many_builder_attempts(ctx):
    out = []
    for d, rows in sorted(_step_dirs(ctx.rows).items()):
        ids = [r['attempt_id'] for r in rows if r.get('role') == 'builder' and r.get('attempt_id')]
        if len(ids) < ctx.t['many_builder_attempts']:
            continue
        out.append(_make(ctx, 'many-builder-attempts', LAYER, 'skills/level-rubric/SKILL.md',
                         'start the step at a level that can pass it',
                         [{'attempt_id': a} for a in ids],
                         f'{d}: {len(ids)} builder attempts'))
    return out


def _poll_group(calls):
    """The larger group of (timestamp, command) calls: one identical command, or POLL_RE."""
    by_cmd, poll = {}, []
    for ts, cmd in calls or []:
        if not isinstance(cmd, str):
            continue
        c = ' '.join(cmd.split())
        by_cmd.setdefault(c, []).append(ts)
        if POLL_RE.match(c):
            poll.append(ts)
    best = poll
    for c in sorted(by_cmd):
        if len(by_cmd[c]) > len(best):
            best = by_cmd[c]
    return best


def _load(aux, first):
    series = aux.get('load_series') if isinstance(aux, dict) else None
    if first is None or not isinstance(series, list):
        return 'unknown'
    best = None
    for pair in series:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2 or not _num(pair[1]):
            continue
        t = _stamp(pair[0])
        if t is None:
            continue
        gap = abs((t - first).total_seconds())
        if best is None or gap < best[0]:
            best = (gap, pair[1])
    return best[1] if best else 'unknown'


def transcript_detectors(ctx, aux):
    out = []
    for r in ctx.rows:
        aid = r.get('attempt_id')
        if not aid:
            continue
        t = _transcript(ctx, r)
        if not t:
            continue
        group = _poll_group(t.get('bash_calls'))
        if len(group) >= ctx.t['polling_loop_calls']:
            first, last = _stamp(group[0]), _stamp(group[-1])
            secs = (last - first).total_seconds() if first and last else None
            load = _load(aux, first)
            out.append(_make(ctx, 'polling-loop', LAYER, 'agents/conductor.md',
                             'wait on the notification, never poll',
                             [{'attempt_id': aid, 'calls': len(group), 'secs': secs,
                               'load': load}],
                             f'{aid}: {len(group)} polling Bash calls over {secs}s, '
                             f'load {load}'))
        denied = [d for d in t.get('denials') or []
                  if isinstance(d, dict) and BACKGROUND_RE.search(str(d.get('stderr') or ''))]
        if denied:
            out.append(_make(ctx, 'background-denial', LAYER, 'hooks/block-background.sh',
                             'role runs never background work',
                             [{'attempt_id': aid, 'count': len(denied)}],
                             f'{aid}: {len(denied)} background tool calls denied'))
    return out


def _result_text(block):
    c = block.get('content')
    if isinstance(c, list):
        return '\n'.join(b.get('text', '') for b in c if isinstance(b, dict))
    return c if isinstance(c, str) else ''


def _conductor_turns(path):
    """The turns of a session .jsonl: {line, fired, acted, board}; [] when unreadable."""
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()
    except (OSError, TypeError):
        return []
    turns, board_ids, cur = [], set(), None
    for n, line in enumerate(lines, 1):
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict) or ev.get('type') not in ('user', 'assistant'):
            continue
        msg = ev.get('message')
        content = msg.get('content') if isinstance(msg, dict) else None
        blocks = [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []
        if ev['type'] == 'user':
            pid = ev.get('promptId')
            if pid and (cur is None or pid != cur['pid']):
                cur = {'pid': pid, 'line': n, 'fired': bool(ev.get('scheduledTaskId')),
                       'acted': False, 'board': []}
                turns.append(cur)
            for b in blocks:
                if cur and b.get('type') == 'tool_result' and b.get('tool_use_id') in board_ids:
                    cur['board'].append(_result_text(b))
            continue
        for b in blocks:
            if cur is None or b.get('type') != 'tool_use':
                continue
            inp = b.get('input') if isinstance(b.get('input'), dict) else {}
            cmd = inp.get('command') if b.get('name') == 'Bash' else None
            if b.get('name') == 'Agent' or (isinstance(cmd, str) and ACTION_RE.search(cmd)):
                cur['acted'] = True
            if isinstance(cmd, str) and BOARD_RE.search(cmd):
                board_ids.add(b.get('id'))
    return turns


def idle_wakes(ctx, aux):
    out = []
    paths = aux.get('conductor_transcripts') if isinstance(aux, dict) else None
    for path in paths if isinstance(paths, list) else []:
        idle, last, fired = [], None, 0
        for turn in _conductor_turns(ctx.abs(path)):
            board = '\n'.join(turn['board']) or None
            changed = board is not None and board != last
            if board is not None:
                last = board
            if not turn['fired']:
                continue
            fired += 1
            if not turn['acted'] and not changed:
                idle.append(turn['line'])
        if len(idle) >= ctx.t['idle_wakes_turns']:
            out.append(_make(ctx, 'idle-wakes', LAYER, 'skills/plan-loop/references/loop-rules.md',
                             'wake on role completion, never on a clock',
                             [{'path': path, 'line': n} for n in idle],
                             f'{path}: {len(idle)} of {fired} fired turns changed nothing'))
    return out


def rate_limit(ctx):
    out = []
    for r in ctx.rows:
        n, aid = r.get('rate_limits'), r.get('attempt_id')
        if aid and _num(n) and n >= 1:
            out.append(_make(ctx, 'rate-limit', 'host', None, 'host rate limit',
                             [{'attempt_id': aid, 'count': n}],
                             f'{aid}: {n} rate limit events'))
    return out


DETECTORS = ('cost-over-baseline', 'many-builder-attempts', 'polling-loop', 'idle-wakes',
             'background-denial', 'rate-limit')


def detect(rows, aux, thresholds=None):
    ctx = _Ctx(rows, aux, thresholds)
    notes = []
    out = cost_over_baseline(ctx, aux, notes)
    out += many_builder_attempts(ctx)
    out += transcript_detectors(ctx, aux)
    out += idle_wakes(ctx, aux)
    out += rate_limit(ctx)
    return out, notes
