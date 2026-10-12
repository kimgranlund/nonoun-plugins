#!/usr/bin/env python3
"""Report the state of one agent thread from records and its transcript, with no model call (T-0460, Python 3.9+).

  report.py collect                      print the session-status/1 JSON record
  report.py render [view...] [options]   print the views (none: the executive summary, at most 8 lines)
  report.py selftest                     run every control: red without its rule, green with it

Views: summary full tasks signals needs context cost children identity evidence lanes waves (lanes and waves read lanes.py, git and
the fanout land journals, not the thread).
Options: --since T, --last N, --next N, --only G,..., --severity problem|likely|all, --format text|md|json,
--evidence, --compare last, --explain, --no-snapshot. --session is reserved and refused.
Exit 2: an unknown view or option, --session, or an unreadable record (.sdlc/config, the --compare snapshot).

Sources: .sdlc tickets, attempts, results and runs.jsonl; git; steps.py next, budget.py status and
gate_lock.py status --json, called read-only with a timeout; the session transcript (stage 2). A value the
collector cannot read is listed in `unknown` by its dotted path and never shown as 0. render stores the record
under .sdlc/runtime/report/<UTC %Y%m%dT%H%M%SZ>.json unless --no-snapshot. Thresholds are `report.<key>: <n>`
lines in .sdlc/config; every flag prints [U] until calibrated. Contract: the /sdlc-lite:report skill and its
references (views.md, record-schema.md); verbs and tense: docs/specs/doc-standards/core.md, Status verbs."""
import datetime as dt
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCHEMA = 'session-status/1'
VERBS = ('built', 'verified', 'merged', 'closed', 'filed', 'released', 'blocked', 'deferred', 'stopped', 'queued', 'waiting')
_NOW_FORM = {'built': 'building', 'verified': 'verifying', 'merged': 'merging', 'closed': 'closing', 'filed': 'filing',
             'released': 'releasing', 'blocked': 'is blocked', 'deferred': 'is deferred', 'stopped': 'is stopping',
             'queued': 'is queued', 'waiting': 'waiting'}
_NEXT_FORM = {'built': 'will build', 'verified': 'will verify', 'merged': 'will merge', 'closed': 'will close',
              'filed': 'will file', 'released': 'will release', 'blocked': 'will be blocked', 'deferred': 'will be deferred',
              'stopped': 'will stop', 'queued': 'will be queued', 'waiting': 'will wait'}
TENSES = ('recent', 'now', 'next')
VIEWS = ('summary', 'full', 'tasks', 'signals', 'needs', 'context', 'cost', 'children', 'identity', 'evidence', 'lanes', 'waves')
FULL_ORDER = ('summary', 'tasks', 'signals', 'context', 'cost', 'children', 'identity', 'evidence')
OPTIONS = ('--since', '--last', '--next', '--only', '--severity', '--format', '--evidence', '--compare', '--explain', '--no-snapshot')
VALUED = ('--since', '--last', '--next', '--only', '--severity', '--format', '--compare')
RESERVED = ('--session',)
GROUPS = ('identity', 'state', 'work', 'timeline', 'health', 'cost', 'needs', 'outcome', 'unknown')
CONTEXT_KEYS = ('peak_context_fill', 'compactions', 're_reads', 'read_to_use', 'exploration', 'workaround_chains', 'noisy_output')
VIEW_GROUPS = {'tasks': ('work', 'timeline'), 'signals': ('health',), 'needs': ('needs',), 'context': ('health',),
               'cost': ('cost',), 'children': ('work',), 'identity': ('identity',), 'evidence': GROUPS, 'summary': GROUPS,
               'explain': ('health',), 'compare': GROUPS}
THRESHOLDS = {
    'late_failure_ratio': 0.8, 'late_failure_min_minutes': 15, 'trivial_failure_minutes': 20, 'rework_rounds': 1,
    'peak_context_pct': 70, 'context_window_tokens': 200000, 'compactions': 2, 're_reads': 3, 'read_to_use': 15,
    'exploration': 25, 'workaround_chain': 2, 'retries': 3, 'noisy_output_tokens': 20000, 'stall_minutes': 15,
    'gate_wait_minutes': 5,
}
PROBLEM = 'problem'
LIKELY = 'likely'
EDIT_TOOLS = ('Edit', 'Write', 'MultiEdit', 'NotebookEdit')
TRIVIAL_RE = re.compile(r'\bgrep\b|\bformat\b|missing result|no result file|stale path|not found|no such file', re.I)
ROLE_VERB = {'builder': 'built', 'solo': 'built', 'verifier': 'verified', 'filer': 'filed'}


class CollectorError(Exception):
    """A record the collector built breaks the contract (a verb outside VERBS, a next entry with no trigger)."""


class Refuse(Exception):
    def __init__(self, code, message):
        Exception.__init__(self, message)
        self.code, self.message = code, message


# ---------------------------------------------------------------- small helpers

def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def parse_ts(v):
    if isinstance(v, (int, float)):
        return dt.datetime.fromtimestamp(v, dt.timezone.utc)
    if not isinstance(v, str) or not v:
        return None
    s = v.strip().replace('Z', '+00:00')
    m = re.match(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d+)?(.*)$', s)
    if m:
        frac = (m.group(2) or '')[:7].ljust(7, '0') if m.group(2) else ''
        s = m.group(1) + frac + (m.group(3) or '')
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if t else None


def short_time(v):
    t = parse_ts(v) if not isinstance(v, dt.datetime) else v
    return t.astimezone(dt.timezone.utc).strftime('%Y-%m-%d %H:%MZ') if t else '-'


def minutes(a, b):
    return (b - a).total_seconds() / 60.0


def fmt_min(m):
    if m is None:
        return '?'
    return '%dm' % round(m) if m < 120 else '%.1fh' % (m / 60.0)


def rel(root, p):
    try:
        return str(Path(p).resolve().relative_to(Path(root).resolve()))
    except (ValueError, OSError):
        return str(p)


def read_json(p):
    try:
        d = json.loads(Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def read_text(p):
    try:
        return Path(p).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None


def front_matter(text):
    fm = {}
    if not text or not text.startswith('---'):
        return fm
    for line in text.splitlines()[1:40]:
        if line.strip() == '---':
            break
        k, sep, v = line.partition(':')
        if sep and re.match(r'^[a-z_]+$', k.strip()):
            fm[k.strip()] = re.sub(r'\s+#.*$', '', v).strip().strip('"')
    return fm


def section(text, *names, **kw):
    """The lines under the first heading (`## `, or `### ` with level=3) named in names, up to the next heading of that level or higher."""
    if not text:
        return []
    level = kw.get('level', 2)
    out, on = [], False
    for line in text.splitlines():
        m = re.match(r'^(#{1,6}) (.+)$', line)
        if m and len(m.group(1)) <= level:
            if on:
                break
            on = len(m.group(1)) == level and m.group(2).strip() in names
            continue
        if on:
            out.append(line)
    return out


def result_value(text, heading):
    for line in section(text, heading):
        if line.strip():
            return line.strip().lower()
    return None


def run(cmd, cwd, timeout=15):
    """Run one read-only command; (rc, stdout, stderr) or None on any failure to run."""
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return p.returncode, p.stdout, p.stderr


RUNNER = run   # selftest swaps this to keep sibling calls off machine-wide state


def sibling(name, args, cwd, timeout=15):
    return RUNNER([sys.executable, str(HERE / name)] + list(args), cwd, timeout)


def git(root, *args):
    r = RUNNER(['git', '-C', str(root)] + list(args), root, 10)
    return r[1] if r and r[0] == 0 else None


# ---------------------------------------------------------------- rules (selftest swaps each for a no-op)

def _verb_check(verb):
    if verb not in VERBS:
        raise CollectorError('verb %r is outside the closed list: %s' % (verb, ', '.join(VERBS)))


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except (OSError, OverflowError, ValueError):
        return False
    return True


def _check_view(v):
    if v not in VIEWS:
        raise Refuse(2, 'report.py: unknown view %r' % v)


def _refuse_session(value):
    raise Refuse(2, 'report.py: --session %s is reserved and refused until the cross-session read exists' % value)


def _read_runs(path):
    """Every runs.jsonl record, or None when the file cannot be read or a line is not a JSON object."""
    text = read_text(path)
    if text is None:
        return None
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except ValueError:
            return None
        if not isinstance(d, dict):
            return None
        out.append(d)
    return out


def _next_mark(item):
    return 'planned' if item.get('ticket') or item.get('step') else 'intended'


def _write_snapshot(root, record, now):
    d = Path(root) / '.sdlc' / 'runtime' / 'report'
    d.mkdir(parents=True, exist_ok=True)
    p = d / (now.astimezone(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.json')
    p.write_text(json.dumps(record, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    return p


def _newest_snapshot(d):
    """The newest snapshot by file name (UTC stamp), never by mtime: plugin AGENTS.md gives ordering to names."""
    try:
        names = sorted(p.name for p in Path(d).glob('*.json') if re.match(r'^\d{8}T\d{6}Z\.json$', p.name))
    except OSError:
        return None
    return Path(d) / names[-1] if names else None


def _explain(signals):
    return ['%s: rule %s; value %s; threshold %s %s; %s [U]' % (
        s['name'], s['rule'], fmt_value(s['value']), s['op'], s['threshold'], 'flagged %s' % s['severity'] if s['flagged'] else 'clear')
        for s in signals]


# signal metrics: each takes (facts, thresholds) and returns a number, or None when it cannot be judged

def _m_late_failure(f, th):
    vals = []
    tx = f.get('tx')
    if tx and tx.get('start') and tx.get('end'):
        fails = [r['ts'] for r in bash_calls(tx) if r['failed'] and r['ts']]
        if fails:
            vals.append((tx['start'], tx['end'], min(fails)))
    if f.get('run_start') and f.get('run_end'):
        fails = [t for t, failed in f.get('checks', []) if failed and t]
        if fails:
            vals.append((f['run_start'], f['run_end'], min(fails)))
    best = None
    for start, end, first in vals:
        total = minutes(start, end)
        if total <= th['late_failure_min_minutes'] or total <= 0:
            continue
        ratio = round(max(0.0, minutes(start, first)) / total, 2)
        best = ratio if best is None else max(best, ratio)
    return best


def _m_trivial_last_failure(f, th):
    lf = f.get('last_failure')
    if not lf or lf.get('minutes') is None or not TRIVIAL_RE.search(lf.get('text') or ''):
        return None
    return round(lf['minutes'], 1)


def _m_check_first_run_late(f, th):
    tx, crit = f.get('tx'), f.get('criteria') or []
    if not tx or not crit or not tx.get('start') or not tx.get('end'):
        return None
    span = (tx['end'] - tx['start']).total_seconds()
    if span <= 0:
        return None
    worst = None
    for c in crit:
        key = criterion_key(c)
        if not key:
            continue
        for u in tx['uses']:
            if u['name'] == 'Bash' and u['ts'] and key in criterion_key(str(u['input'].get('command', ''))):
                pos = round((u['ts'] - tx['start']).total_seconds() / span, 2)
                worst = pos if worst is None else max(worst, pos)
                break
    return worst


def _m_rework(f, th):
    return f.get('verifier_rounds')


def _m_peak_context(f, th):
    tx = f.get('tx')
    if not tx:
        return None
    return round(100.0 * peak_tokens(tx) / float(th['context_window_tokens']), 1)


def _m_compactions(f, th):
    return f['tx']['compactions'] if f.get('tx') else None


def _m_re_reads(f, th):
    return re_reads(f['tx'])[0] if f.get('tx') else None


def _m_read_to_use(f, th):
    return read_to_use(f['tx']) if f.get('tx') else None


def _m_exploration(f, th):
    return exploration(f['tx']) if f.get('tx') else None


def _m_workaround(f, th):
    return workaround_chains(f['tx']) if f.get('tx') else None


def _m_retries(f, th):
    vals = [v for v in (f.get('attempt_retries'), same_call_failures(f['tx']) if f.get('tx') else None) if v is not None]
    return max(vals) if vals else None


def _m_dead_end(f, th):
    return f.get('reverts')


def _m_noisy(f, th):
    return noisy_output(f['tx']) if f.get('tx') else None


def _m_stall(f, th):
    if f.get('waiting') or f.get('idle_minutes') is None:
        return None
    return round(f['idle_minutes'], 1)


def _m_gate_wait(f, th):
    w = f.get('gate_wait_s')
    return None if w is None else round(w / 60.0, 1)


def _m_dead(f, th):
    return 1 if f.get('pid_alive') is False else 0


RULES = {
    'verb_check': _verb_check, 'pid_alive': _pid_alive, 'check_view': _check_view, 'refuse_session': _refuse_session,
    'collect_fleet': lambda root, env=None: collect_fleet(root, env), 'read_runs': _read_runs, 'next_mark': _next_mark, 'write_snapshot': _write_snapshot,
    'newest_snapshot': _newest_snapshot, 'explain': _explain,
    'late failure': _m_late_failure, 'trivial last failure': _m_trivial_last_failure,
    'check first run late': _m_check_first_run_late, 'rework': _m_rework, 'peak context fill': _m_peak_context,
    'compactions': _m_compactions, 're-reads': _m_re_reads, 'read-to-use': _m_read_to_use,
    'exploration': _m_exploration, 'workaround chain': _m_workaround, 'retries': _m_retries,
    'dead-end work': _m_dead_end, 'noisy output': _m_noisy, 'stall': _m_stall, 'gate wait': _m_gate_wait,
    'dead': _m_dead,
}

# name, severity, threshold key (or a fixed number), op, rule text. Records-only signals first, then transcript ones.
SIGNALS = (
    ('dead', PROBLEM, 0, '>', 'the session pid (CLAUDE_PID) is not alive'),
    ('late failure', PROBLEM, 'late_failure_ratio', '>', 'minutes before the first failing check / total minutes, on a run over late_failure_min_minutes'),
    ('trivial last failure', PROBLEM, 'trivial_failure_minutes', '>=', 'minutes of work before a last failure that is a grep, a format line, a missing result file or a stale path'),
    ('rework', PROBLEM, 'rework_rounds', '>', 'verifier rounds on one step'),
    ('dead-end work', PROBLEM, 0, '>', 'revert commits in the lane inside the window'),
    ('stall', PROBLEM, 'stall_minutes', '>', 'minutes since the last tool call or file change, with no child running and no open question'),
    ('retries', LIKELY, 'retries', '>=', 'the same tool call failing, or attempts of one role on one step'),
    ('gate wait', LIKELY, 'gate_wait_minutes', '>', 'minutes queued in the gate lock'),
    ('check first run late', LIKELY, 0.9, '>', 'position of the first run of a (red) or guard criterion in the transcript span'),
    ('peak context fill', LIKELY, 'peak_context_pct', '>', 'percent of context_window_tokens in the fullest turn (input plus cache tokens)'),
    ('compactions', LIKELY, 'compactions', '>=', 'compactions in the transcript'),
    ('re-reads', LIKELY, 're_reads', '>=', 'reads of one file with no edit between'),
    ('read-to-use', LIKELY, 'read_to_use', '>', 'files read / files edited'),
    ('exploration', LIKELY, 'exploration', '>', 'grep and glob calls before the first edit'),
    ('workaround chain', LIKELY, 'workaround_chain', '>=', 'failed commands followed by a rewritten command'),
    ('noisy output', LIKELY, 'noisy_output_tokens', '>', 'tokens in the largest single tool result'),
)


def fmt_value(v):
    if v is None:
        return 'n/a'
    if isinstance(v, float):
        return ('%.2f' % v).rstrip('0').rstrip('.')
    return str(v)


def evaluate(facts, th):
    out = []
    for name, sev, key, op, rule in SIGNALS:
        limit = th[key] if isinstance(key, str) else key
        value = RULES[name](facts, th)
        flagged = value is not None and (value > limit if op == '>' else value >= limit)
        out.append({'name': name, 'severity': sev, 'value': value, 'threshold': limit, 'op': op, 'rule': rule,
                    'flagged': bool(flagged), 'mark': '[U]', 'evidence': facts.get('evidence', {}).get(name, '')})
    return out


def grade(signals):
    flags = [s for s in signals if s['flagged']]
    names = [s['name'] for s in flags]
    if any(s['severity'] == PROBLEM for s in flags):
        g = 'D'
    elif len(flags) >= 2:
        g = 'C'
    elif len(flags) == 1:
        g = 'B'
    else:
        g = 'A'
    return g, names


# ---------------------------------------------------------------- transcript (stage 2)

def transcript_path(root, env):
    if env.get('SDLC_REPORT_TRANSCRIPT'):
        return Path(env['SDLC_REPORT_TRANSCRIPT'])
    sid = env.get('CLAUDE_CODE_SESSION_ID')
    if not sid or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', sid):
        return None
    base = Path(env.get('SDLC_CLAUDE_PROJECTS') or Path.home() / '.claude' / 'projects')
    slug = re.sub(r'[/.]', '-', str(Path(root).resolve()))
    return base / slug / ('%s.jsonl' % sid)


def _chars(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(_chars(b.get('text', '')) if isinstance(b, dict) else 0 for b in content)
    return 0


def parse_transcript(path):
    """The tool calls, results, usage and tail of one session transcript; None when it cannot be read."""
    if path is None:
        return None
    try:
        lines = Path(path).read_text(encoding='utf-8', errors='replace').splitlines()
    except OSError:
        return None
    tx = {'path': str(path), 'start': None, 'end': None, 'usage': {}, 'uses': [], 'results': {}, 'compactions': 0,
          'model': None, 'effort': None, 'agent': None, 'last_tool': None, 'last_kind': None, 'last_text': '', 'lines': len(lines)}
    for n, line in enumerate(lines, 1):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if not isinstance(d, dict):
            continue
        if d.get('type') == 'agent-setting' and d.get('agentSetting'):
            tx['agent'] = d['agentSetting']
        if d.get('isSidechain'):
            continue
        ts = parse_ts(d.get('timestamp'))
        if ts:
            tx['start'] = ts if tx['start'] is None or ts < tx['start'] else tx['start']
            tx['end'] = ts if tx['end'] is None or ts > tx['end'] else tx['end']
        if (d.get('type') == 'system' and d.get('subtype') == 'compact_boundary') or d.get('isCompactSummary'):
            tx['compactions'] += 1
            continue
        m = d.get('message')
        if not isinstance(m, dict):
            continue
        kind = d.get('type')
        if kind == 'assistant':
            if d.get('effort'):
                tx['effort'] = d['effort']
            if m.get('model'):
                tx['model'] = m['model']
            u = m.get('usage')
            if isinstance(u, dict):
                tok = sum(u.get(k) or 0 for k in ('input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')
                          if isinstance(u.get(k) or 0, (int, float)))
                tx['usage'][m.get('id') or 'line%d' % n] = tok
        content = m.get('content')
        blocks = content if isinstance(content, list) else [{'type': 'text', 'text': content}] if isinstance(content, str) else []
        for b in blocks:
            if not isinstance(b, dict):
                continue
            t = b.get('type')
            if t == 'tool_use':
                tx['uses'].append({'ts': ts, 'id': b.get('id'), 'name': b.get('name') or '', 'input': b.get('input') if isinstance(b.get('input'), dict) else {}, 'line': n})
                tx['last_tool'] = ts or tx['last_tool']
                tx['last_kind'] = 'tool'
            elif t == 'tool_result':
                tx['results'][b.get('tool_use_id')] = {'ts': ts, 'is_error': bool(b.get('is_error')), 'chars': _chars(b.get('content')), 'line': n}
            elif t == 'text' and not d.get('isMeta') and kind in ('user', 'assistant') and (b.get('text') or '').strip():
                tx['last_kind'], tx['last_text'] = kind, b.get('text') or ''
    return tx


def bash_calls(tx):
    out = []
    for u in tx['uses']:
        if u['name'] != 'Bash':
            continue
        r = tx['results'].get(u['id']) or {}
        out.append({'ts': r.get('ts') or u['ts'], 'cmd': str(u['input'].get('command', '')), 'failed': bool(r.get('is_error')), 'line': u['line']})
    return out


def peak_tokens(tx):
    return max(tx['usage'].values()) if tx['usage'] else 0


def re_reads(tx):
    counts, best, where = {}, 0, ''
    for u in tx['uses']:
        p = u['input'].get('file_path') or u['input'].get('notebook_path')
        if not p:
            continue
        if u['name'] == 'Read':
            counts[p] = counts.get(p, 0) + 1
            if counts[p] > best:
                best, where = counts[p], p
        elif u['name'] in EDIT_TOOLS:
            counts[p] = 0
    return best, where


def read_to_use(tx):
    reads = {u['input'].get('file_path') for u in tx['uses'] if u['name'] == 'Read' and u['input'].get('file_path')}
    edits = {u['input'].get('file_path') or u['input'].get('notebook_path') for u in tx['uses'] if u['name'] in EDIT_TOOLS}
    edits.discard(None)
    return round(len(reads) / float(max(1, len(edits))), 1) if reads else 0


_SEARCH_RE = re.compile(r'(^|&&|;|\||\()\s*(grep|rg|find|fd|ag)\s')


def exploration(tx):
    n = 0
    for u in tx['uses']:
        if u['name'] in EDIT_TOOLS:
            break
        if u['name'] in ('Grep', 'Glob') or (u['name'] == 'Bash' and _SEARCH_RE.search(str(u['input'].get('command', '')))):
            n += 1
    return n


def workaround_chains(tx):
    n, prev = 0, None
    for c in bash_calls(tx):
        if prev is not None and prev['failed'] and c['cmd'].strip() != prev['cmd'].strip():
            n += 1
        prev = c
    return n


def same_call_failures(tx):
    counts = {}
    for u in tx['uses']:
        r = tx['results'].get(u['id'])
        if r and r['is_error']:
            k = u['name'] + json.dumps(u['input'], sort_keys=True)
            counts[k] = counts.get(k, 0) + 1
    return max(counts.values()) if counts else 0


def noisy_output(tx):
    return max([r['chars'] for r in tx['results'].values()] or [0]) // 4


def criterion_key(cmd):
    s = re.sub(r'^\s*set -o pipefail;\s*', '', cmd or '')
    return re.sub(r'\s+', ' ', s).strip()[:40]


def open_question(tx):
    answered = set(tx['results'])
    for u in reversed(tx['uses']):
        if u['name'] == 'AskUserQuestion' and u['id'] not in answered:
            qs = u['input'].get('questions')
            q = qs[0].get('question') if isinstance(qs, list) and qs and isinstance(qs[0], dict) else None
            return {'text': q or 'an AskUserQuestion is open', 'line': u['line']}
    if tx['last_kind'] == 'assistant' and tx['last_text'].rstrip().endswith('?'):
        return {'text': tx['last_text'].strip().splitlines()[-1][:160], 'line': tx['lines']}
    return None


# ---------------------------------------------------------------- records (stage 1)

def entry(verb, tense, subject, ident='', outcome='', when=None, evidence='', trigger='', **extra):
    """One timeline entry. The only builder of entries: a verb outside VERBS raises CollectorError."""
    RULES['verb_check'](verb)
    if tense not in TENSES:
        raise CollectorError('tense %r is not one of %s' % (tense, ', '.join(TENSES)))
    if tense == 'next' and not trigger:
        raise CollectorError('a next entry needs a trigger: %s %s' % (verb, subject))
    form = verb if tense == 'recent' else _NOW_FORM.get(verb, verb) if tense == 'now' else _NEXT_FORM.get(verb, 'will ' + verb)
    text = ' '.join(x for x in (form, subject, ident, trigger if tense == 'next' else '') if x)
    e = {'verb': verb, 'tense': tense, 'text': text, 'outcome': outcome or '', 'time': iso(when) if isinstance(when, dt.datetime) else when,
         'evidence': evidence or ''}
    e.update(extra)
    return e


def task_dirs(sdlc):
    try:
        return sorted(d for d in sdlc.iterdir() if d.is_dir() and not d.name.startswith('.') and (d / 'handoff.md').is_file())
    except OSError:
        return []


def step_dirs(task):
    try:
        ds = [d for d in task.iterdir() if d.is_dir() and re.fullmatch(r'step-\d+', d.name)]
    except OSError:
        return []
    return sorted(ds, key=lambda d: int(d.name.split('-')[1]))


def attempts(d):
    out = []
    for p in sorted(Path(d).glob('*.attempt.json')):
        a = read_json(p)
        if a is not None:
            a['_path'] = p
            out.append(a)
    return out


def all_attempts(task):
    out = attempts(task)
    for s in step_dirs(task):
        for a in attempts(s):
            a['_step'] = s
            out.append(a)
    return out


def results_in(d, role):
    out = []
    for p in sorted(Path(d).glob('%s-*.md' % role)):
        if '.attempt' in p.name or '.dispatch' in p.name:
            continue
        text = read_text(p) or ''
        a = read_json(p.with_name(p.stem + '.attempt.json')) or {}
        when = parse_ts(a.get('finished_at')) or parse_ts(a.get('started_at'))
        out.append({'path': p, 'text': text, 'when': when,
                    'verdict': result_value(text, 'Verdict'), 'status': result_value(text, 'Status')})
    return out


def ticket_id(task, fm):
    return fm.get('id') or ''


def read_thresholds(root):
    th = dict(THRESHOLDS)
    p = Path(root) / '.sdlc' / 'config'
    if not p.exists():
        return th
    text = read_text(p)
    if text is None:
        raise Refuse(2, 'report.py: cannot read %s' % p)
    for n, line in enumerate(text.splitlines(), 1):
        m = re.match(r'^\s*report\.([a-z_]+)\s*:\s*(.*?)\s*$', line)
        if not m:
            continue
        if m.group(1) not in th:
            continue
        try:
            th[m.group(1)] = float(m.group(2)) if '.' in m.group(2) else int(m.group(2))
        except ValueError:
            raise Refuse(2, 'report.py: %s:%d: report.%s is not a number: %r' % (p, n, m.group(1), m.group(2)))
    return th


def parse_since(value, root, now):
    if value in (None, 'last-report'):
        snap = RULES['newest_snapshot'](Path(root) / '.sdlc' / 'runtime' / 'report')
        d = read_json(snap) if snap else None
        t = parse_ts(d.get('generated_at')) if d else None
        return t or now - dt.timedelta(hours=4)
    m = re.fullmatch(r'(\d+)([mhd])', value)
    if m:
        return now - dt.timedelta(**{{'m': 'minutes', 'h': 'hours', 'd': 'days'}[m.group(2)]: int(m.group(1))})
    if value == 'today':
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    t = parse_ts(value if 'T' in value else value + 'T00:00:00+00:00')
    if t is None:
        raise Refuse(2, 'report.py: --since %r is not 2h, 30m, 1d, today, a date or last-report' % value)
    return t


def collect(root, env, now=None, th=None, since=None, last=5, nxt=3):
    """The session-status/1 record for the thread whose pid is env CLAUDE_PID. Never raises on a missing source."""
    root = Path(root)
    now = now or utcnow()
    th = th or read_thresholds(root)
    since_t = since if isinstance(since, dt.datetime) else parse_since(since, root, now)
    sdlc = root / '.sdlc'
    unknown = []
    facts = {'evidence': {}}
    ev = {}

    # identity
    pid = None
    try:
        pid = int(env.get('CLAUDE_PID') or '')
    except ValueError:
        pid = None
    alive = RULES['pid_alive'](pid) if pid else None
    facts['pid_alive'] = alive
    sid = env.get('CLAUDE_CODE_SESSION_ID') or None
    tpath = transcript_path(root, env)
    tx = parse_transcript(tpath)
    facts['tx'] = tx
    branch = (git(root, 'rev-parse', '--abbrev-ref', 'HEAD') or '').strip() or None
    host = 'claude' if (env.get('CLAUDE_PID') or env.get('CLAUDE_CODE_SESSION_ID')) else 'codex' if env.get('CODEX_HOME') or env.get('CODEX_SANDBOX') else None
    identity = {'session_id': sid, 'name': None, 'role': (tx or {}).get('agent'), 'level': None,
                'model': (tx or {}).get('model'), 'effort': (tx or {}).get('effort'), 'host': host, 'repo': str(root),
                'branch': branch, 'parent': None, 'started_at': iso((tx or {}).get('start')), 'pid': pid}
    for k, v in identity.items():
        if v is None:
            unknown.append('identity.' + k)
    ev['identity'] = 'env CLAUDE_PID, CLAUDE_CODE_SESSION_ID; transcript %s; git' % (tpath if tx else 'unreadable')

    # the thread's task: the .sdlc/*/ dir with a running attempt whose parent_pid is this pid
    task, running = None, []
    tasks = task_dirs(sdlc)
    if pid:
        for d in tasks:
            mine = [a for a in all_attempts(d) if a.get('status') == 'running' and a.get('parent_pid') == pid]
            if mine:
                task, running = d, mine
                break
    hand = read_text(task / 'handoff.md') if task else None
    fm = front_matter(hand)
    tid = ticket_id(task, fm) if task else ''
    steps = step_dirs(task) if task else []
    cur_step = None
    for a in running:
        if a.get('_step'):
            cur_step = a['_step']
    if task and cur_step is None:
        for s in steps:
            if not any(r['verdict'] == 'pass' for r in results_in(s, 'verifier')):
                cur_step = s
                break
        cur_step = cur_step or (steps[-1] if steps else None)
    goal = None
    for line in section(hand, 'Task goal', 'Goal'):
        if line.strip():
            goal = line.strip()
            break
    children = []
    task_attempts = all_attempts(task) if task else []
    for a in task_attempts:
        st = parse_ts(a.get('started_at'))
        fin = parse_ts(a.get('finished_at'))
        children.append({'name': a.get('name'), 'role': a.get('role'), 'level': a.get('level'), 'status': a.get('status'),
                         'step': a['_step'].name if a.get('_step') else None, 'started_at': iso(st),
                         'elapsed_minutes': round(minutes(st, fin or now), 1) if st else None,
                         'evidence': rel(root, a['_path'])})
    work = {'goal': goal, 'ticket': tid or None, 'ticket_status': fm.get('status') if task else None,
            'task': rel(root, task) if task else None,
            'step': int(cur_step.name.split('-')[1]) if cur_step else None, 'steps': len(steps) if task else None,
            'children': children, 'waits_on': [c['name'] for c in children if c['status'] == 'running']}
    if not task:
        unknown.extend(['work.task', 'work.goal', 'work.ticket', 'work.step'])
    ev['work'] = rel(root, task / 'handoff.md') if task else 'no running attempt with parent_pid %s' % (pid or '?')

    # checks for late failure, rework, retries, trivial last failure
    scope_dirs = ([task] + steps) if task else []
    checks, rounds, retries_n, last_fail = [], 0, 0, None
    starts = [parse_ts(a.get('started_at')) for a in task_attempts]
    starts = [s for s in starts if s]
    run_start = min(starts) if starts else None
    run_end = None
    for a in task_attempts:
        fin = parse_ts(a.get('finished_at'))
        if a.get('status') == 'running':
            fin = now
        if fin and (run_end is None or fin > run_end):
            run_end = fin
        if a.get('status') in ('failed', 'interrupted') and fin:
            checks.append((fin, True))
    for d in scope_dirs:
        names = {}
        for a in attempts(d):
            names[a.get('role')] = names.get(a.get('role'), 0) + 1
        retries_n = max([retries_n] + list(names.values()))
        rs = results_in(d, 'verifier')
        runs_v = [r for r in (RULES['read_runs'](d / 'runs.jsonl') or []) if r.get('role') == 'verifier']
        rounds = max(rounds, len(runs_v), len(rs))
        for r in rs:
            if r['verdict'] and r['when']:
                failed = r['verdict'] != 'pass'
                checks.append((r['when'], failed))
                if failed and (last_fail is None or r['when'] > last_fail['when']):
                    crit = [l for l in r['text'].splitlines() if re.search(r':\s*fail\b', l)]
                    last_fail = {'when': r['when'], 'text': ' '.join(crit) or r['text'][:400], 'path': r['path']}
    facts.update({'checks': checks, 'run_start': run_start, 'run_end': run_end, 'verifier_rounds': rounds if task else None,
                  'attempt_retries': retries_n if task else None})
    if last_fail and run_start:
        facts['last_failure'] = {'text': last_fail['text'], 'minutes': minutes(run_start, last_fail['when'])}
        facts['evidence']['trivial last failure'] = rel(root, last_fail['path'])
    crit = []
    if cur_step is not None:
        for line in section(read_text(cur_step / 'handoff.md'), 'Acceptance criteria', level=3):
            m = re.match(r'^\s*-\s*\((?:red|guard)\)\s*`(.+)`\s*$', line)
            if m:
                crit.append(m.group(1))
    facts['criteria'] = crit

    # state
    last_tool = (tx or {}).get('last_tool')
    file_change = None
    if task:
        try:
            for p in task.rglob('*'):
                if p.is_file():
                    t = dt.datetime.fromtimestamp(p.stat().st_mtime, dt.timezone.utc)
                    file_change = t if file_change is None or t > file_change else file_change
        except OSError:
            pass
    porcelain = git(root, 'status', '--porcelain', '--untracked-files=all')
    dirty = None
    if porcelain is not None:
        files = [l[3:].split(' -> ')[-1].strip('"') for l in porcelain.splitlines() if len(l) > 3]
        dirty = len(files)
        for f in files[:200]:
            try:
                t = dt.datetime.fromtimestamp((root / f).stat().st_mtime, dt.timezone.utc)
            except OSError:
                continue
            file_change = t if file_change is None or t > file_change else file_change
    acts = [t for t in (last_tool, file_change) if t]
    last_act = max(acts) if acts else None
    question = open_question(tx) if tx else None
    facts['idle_minutes'] = minutes(last_act, now) if last_act else None
    facts['waiting'] = bool(work['waits_on'] or question)
    stall = RULES['stall'](facts, th)
    if alive is False:
        state = 'dead'
    elif question:
        state = 'waiting-on-user'
    elif work['waits_on']:
        state = 'waiting-on-role'
    elif stall is not None and stall > th['stall_minutes']:
        state = 'stalled'
    elif fm.get('status') == 'blocked':
        state = 'blocked'
    elif task or tx:
        state = 'working'
    else:
        state = 'idle'
    facts['state'] = state
    st_rec = {'state': state, 'since': iso(last_act), 'last_activity': iso(last_act), 'last_tool_call': iso(last_tool),
              'pid_alive': alive,
              'evidence': 'pid %s %s; %s' % (pid or '?', 'alive' if alive else 'dead' if alive is False else 'unknown',
                                              'transcript %s:%s' % (tpath, tx['lines']) if tx else 'no transcript')}
    if pid is None:
        unknown.append('state.pid_alive')
    if last_act is None:
        unknown.append('state.last_activity')
    if last_tool is None:
        unknown.append('state.last_tool_call')
    facts['evidence']['stall'] = st_rec['evidence']
    facts['evidence']['dead'] = 'env CLAUDE_PID=%s' % (pid or '?')

    # timeline: recent
    recent = []
    for d in sorted(sdlc.glob('.[0-9]*')) if sdlc.is_dir() else []:
        if not d.is_dir():
            continue
        cfm = front_matter((read_text(d / 'handoff.md') or '')[:2000])
        if cfm.get('status') not in ('done', 'dropped'):
            continue
        times = [parse_ts(a.get('finished_at')) for a in all_attempts(d)]
        times = [t for t in times if t]
        if not times:
            rs = RULES['read_runs'](d / 'runs.jsonl') or []
            times = [t for t in (parse_ts(r.get('ts')) for r in rs) if t]
        if not times or max(times) < since_t:
            continue
        recent.append(entry('closed', 'recent', 'ticket', cfm.get('id', d.name), cfm.get('status'), max(times), rel(root, d / 'handoff.md')))
    for d in tasks if not task else [task]:
        dfm = front_matter((read_text(d / 'handoff.md') or '')[:2000])
        did = dfm.get('id') or d.name
        for s in step_dirs(d) or [d]:
            label = s.name.replace('-', ' ') if s != d else 'task'
            for r in results_in(s, 'builder'):
                if r['status'] == 'done' and r['when'] and r['when'] >= since_t:
                    recent.append(entry('built', 'recent', label, did, 'done', r['when'], rel(root, r['path'])))
            for r in results_in(s, 'verifier'):
                if r['verdict'] == 'pass' and r['when'] and r['when'] >= since_t:
                    recent.append(entry('verified', 'recent', label, did, 'pass', r['when'], rel(root, r['path'])))
    recent.sort(key=lambda e: e['time'] or '', reverse=True)
    recent = recent[:max(0, last)]

    # timeline: now
    now_e = []
    for a in running:
        verb = ROLE_VERB.get(a.get('role'), 'waiting')
        subj = a['_step'].name.replace('-', ' ') if a.get('_step') else 'task'
        if verb == 'waiting':
            subj = 'on %s %s for %s' % (a.get('role'), a.get('level'), subj)
        st = parse_ts(a.get('started_at'))
        now_e.append(entry(verb, 'now', subj, tid, '%s %s, %s' % (a.get('role'), a.get('level'), fmt_min(minutes(st, now) if st else None)),
                           st, rel(root, a['_path'])))
    if task and not running and cur_step is not None:
        r = sibling('steps.py', ['next', str(cur_step)], root)
        if r and r[0] == 0 and r[1].strip():
            action = r[1].strip().splitlines()[0]
            now_e.append(entry('waiting', 'now', 'on ' + cur_step.name.replace('-', ' '), tid, 'next action: ' + action, now,
                               'steps.py next %s' % rel(root, cur_step)))
        else:
            unknown.append('timeline.now')
    if not task:
        unknown.append('timeline.now')

    # timeline: next
    items = []
    if task and cur_step is not None:
        n0 = int(cur_step.name.split('-')[1])
        for s in steps:
            k = int(s.name.split('-')[1])
            if k > n0 and not results_in(s, 'builder'):
                items.append({'verb': 'built', 'subject': s.name.replace('-', ' '), 'ticket': tid, 'step': k,
                              'trigger': 'after step %d verifies' % (k - 1), 'evidence': rel(root, s / 'handoff.md')})
    for d in tasks:
        dfm = front_matter((read_text(d / 'handoff.md') or '')[:2000])
        deps = re.findall(r'T-\d{4}', dfm.get('depends', ''))
        if tid and tid in deps and dfm.get('status') in ('proposed', 'ready'):
            items.append({'verb': 'built', 'subject': 'ticket', 'ticket': dfm.get('id'), 'trigger': 'after %s closes' % tid,
                          'evidence': rel(root, d / 'handoff.md')})
    for d in tasks:
        dfm = front_matter((read_text(d / 'handoff.md') or '')[:2000])
        if dfm.get('status') == 'ready' and d != task:
            items.append({'verb': 'queued', 'subject': 'ticket', 'ticket': dfm.get('id') or d.name, 'trigger': 'when a lane frees',
                          'evidence': rel(root, d / 'handoff.md')})
    for line in section(hand, 'Next'):
        m = re.match(r'^\s*[-*]\s+(.+)$', line)
        if m:
            t = re.search(r'T-\d{4}', m.group(1))
            sm = re.search(r'\bstep[- ](\d+)\b', m.group(1))
            items.append({'verb': 'built', 'subject': m.group(1).strip(), 'ticket': t.group(0) if t else None,
                          'step': int(sm.group(1)) if sm else None, 'trigger': 'when %s' % (tid or 'the thread') + ' gets to it',
                          'evidence': rel(root, task / 'handoff.md') + ' ## Next'})
    next_e = []
    for it in items[:max(0, nxt)]:
        mark = RULES['next_mark'](it)
        ident = it['ticket'] if it.get('ticket') and it['subject'] in ('ticket',) or (it.get('step') and it.get('ticket')) else ''
        next_e.append(entry(it['verb'], 'next', it['subject'], ident or '', mark, None, it['evidence'], trigger=it['trigger'], mark=mark))

    # health: records-only facts from git and the gate lock
    since_arg = since_t.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    reverts = git(root, 'log', '--oneline', '-E', '--grep=^Revert', '--since=' + since_arg)
    facts['reverts'] = len(reverts.splitlines()) if reverts is not None else None
    facts['evidence']['dead-end work'] = 'git log --grep=^Revert --since=%s' % since_arg
    unpushed_out = git(root, 'rev-list', '--count', '@{u}..HEAD')
    unpushed = int(unpushed_out.strip()) if unpushed_out and unpushed_out.strip().isdigit() else None
    g = sibling('gate_lock.py', ['status', '--json'], root, 10)
    gate = None
    if g and g[0] == 0:
        try:
            gd = json.loads(g[1])
            mine = [q for q in gd.get('queue', []) if str(q.get('repo')) in (str(root), str(root.resolve()))]
            gate = {'position': min([q.get('position', 0) for q in mine]) if mine else None,
                    'waited_s': max([q.get('waited_s', 0) for q in mine]) if mine else 0}
        except (ValueError, AttributeError, TypeError):
            gate = None
    facts['gate_wait_s'] = gate['waited_s'] if gate else None
    facts['evidence']['gate wait'] = 'gate_lock.py status --json'
    if tx:
        rr, rr_path = re_reads(tx)
        facts['evidence'].update({k: 'transcript %s' % tpath for k in ('late failure', 'check first run late', 'peak context fill', 'compactions',
                                                                         'read-to-use', 'exploration', 'workaround chain', 'retries', 'noisy output')})
        facts['evidence']['re-reads'] = 'transcript %s: %s' % (tpath, rr_path)
    elif run_start:
        facts['evidence']['late failure'] = rel(root, task)
    signals = evaluate(facts, th)
    g_letter, g_flags = grade(signals)
    context = {}
    if tx:
        context = {'peak_context_fill': round(peak_tokens(tx) / float(th['context_window_tokens']), 3),
                   'compactions': tx['compactions'], 're_reads': re_reads(tx)[0], 'read_to_use': read_to_use(tx),
                   'exploration': exploration(tx), 'workaround_chains': workaround_chains(tx), 'noisy_output': noisy_output(tx)}
    else:
        unknown.extend('health.context.' + k for k in CONTEXT_KEYS)
    blocked_attempts = [c['name'] for c in children if c['status'] in ('interrupted', 'orphaned')]
    health = {'signals': signals, 'flags': g_flags, 'grade': g_letter,
              'grade_reason': ', '.join(g_flags) if g_flags else 'no flags', 'context': context,
              'gate_lock': gate, 'dirty_files': dirty, 'unpushed_commits': unpushed, 'blocked_attempts': blocked_attempts,
              'transcript': str(tpath) if tx else None}
    if gate is None:
        unknown.append('health.gate_wait_minutes')
    if dirty is None:
        unknown.append('health.dirty_files')
    if unpushed is None:
        unknown.append('health.unpushed_commits')
    if facts['reverts'] is None:
        unknown.append('health.dead_end_work')

    # cost
    cost = {'dollars': None, 'tokens': None, 'active_minutes': None, 'priced_runs': None, 'unpriced_runs': None,
            'budget': None, 'budget_percent': None, 'evidence': ''}
    if task:
        runs, readable = [], True
        for p in sorted([task / 'runs.jsonl'] + [s / 'runs.jsonl' for s in steps]):
            if not p.exists():
                continue
            rs = RULES['read_runs'](p)
            if rs is None:
                readable = False
                break
            runs.extend(rs)
        cost['evidence'] = rel(root, task) + '/**/runs.jsonl'
        if readable:
            priced = [r for r in runs if isinstance(r.get('cost_usd'), (int, float)) and not isinstance(r.get('cost_usd'), bool)]
            unpriced = len(runs) - len(priced)
            cost['priced_runs'], cost['unpriced_runs'] = len(priced), unpriced
            if priced or not unpriced:
                cost['dollars'] = round(sum(r['cost_usd'] for r in priced), 4)
            toks = 0
            for r in runs:
                u = r.get('usage') if isinstance(r.get('usage'), dict) else {}
                toks += sum(v for k, v in u.items() if k.endswith('tokens') and isinstance(v, (int, float)))
            cost['tokens'] = toks
            cost['active_minutes'] = round(sum(r.get('duration_ms') or 0 for r in runs if isinstance(r.get('duration_ms'), (int, float))) / 60000.0, 1)
        b = sibling('budget.py', ['status', str(task)], root)
        if b and b[0] in (0, 3):
            kv = dict(l.split(': ', 1) for l in b[1].splitlines() if ': ' in l)
            try:
                cost['budget'] = float(kv.get('budget')) if kv.get('budget') not in (None, 'none', '') else None
            except ValueError:
                cost['budget'] = None
            cost['budget_percent'] = int(kv['percent']) if (kv.get('percent') or '').isdigit() else None
        elif b and b[0] == 2 and 'no budget' in (b[2] or ''):
            cost['budget'] = 'none'
        else:
            unknown.extend(['cost.budget', 'cost.budget_percent'])
    for k in ('dollars', 'tokens', 'active_minutes', 'priced_runs', 'unpriced_runs'):
        if cost[k] is None:
            unknown.append('cost.' + k)

    # needs
    needs = []
    if question:
        needs.append({'kind': 'decision', 'text': question['text'], 'source': 'transcript %s:%s' % (tpath, question['line'])})
    for n, line in enumerate((hand or '').splitlines(), 1):
        m = re.match(r'^\s*[-*]\s*decide:\s*(.+)$', line)
        if m:
            needs.append({'kind': 'decision', 'text': m.group(1).strip(), 'source': '%s:%d' % (rel(root, task / 'handoff.md'), n)})
    for s in scope_dirs:
        for r in results_in(s, 'builder'):
            if r['status'] and r['status'].startswith('blocked'):
                notes = [l.strip() for l in section(r['text'], 'Notes') if l.strip()]
                kind = 'merge' if notes and 'merge' in notes[0].lower() else 'decision'
                needs.append({'kind': kind, 'text': notes[0] if notes else 'builder blocked', 'source': rel(root, r['path'])})

    # outcome
    done_when, kpi = None, None
    for line in (hand or '').splitlines():
        m = re.match(r'^\s*[-*]\s*Done when:\s*(.+)$', line)
        if m and not done_when:
            done_when = m.group(1).strip()
        m = re.match(r'^\s*[-*]\s*outcome metric:\s*(.+)$', line)
        if m and not kpi:
            kpi = m.group(1).strip()
    outcome = {'done_when': done_when, 'last_result': None, 'kpi': kpi}
    unknown.append('outcome.last_result')
    if not done_when:
        unknown.append('outcome.done_when')

    return {'schema': SCHEMA, 'generated_at': iso(now), 'since': iso(since_t), 'identity': identity, 'state': st_rec,
            'work': work, 'timeline': {'recent': recent, 'now': now_e, 'next': next_e}, 'health': health, 'cost': cost,
            'needs': needs, 'outcome': outcome, 'unknown': sorted(set(unknown)), 'evidence': ev}


# ---------------------------------------------------------------- lanes and waves (T-0483)

FLEET_KINDS = ('fanout', 'solo', 'integration')


def _main_branch(root):
    out = git(root, 'worktree', 'list', '--porcelain')
    for line in (out or '').splitlines():
        if not line.strip():
            break
        if line.startswith('branch '):
            return line[len('branch '):].replace('refs/heads/', '', 1)
    return None


def _count(root, spec):
    out = git(root, 'rev-list', '--count', spec)
    return int(out.strip()) if out and out.strip().isdigit() else None


def _ps_lines():
    r = RUNNER(['ps', '-axo', 'pid=,command='], '/', 15)
    return r[1].splitlines() if r and r[0] == 0 else None


def _driver(lines, path):
    """`yes (pid N)` when a process other than this report names the lane path, `no` when none does, `unknown` with no ps."""
    if lines is None:
        return 'unknown'
    variants = {str(path), os.path.realpath(str(path))}
    variants |= {v[len('/private'):] for v in list(variants) if v.startswith('/private/')}
    pat = re.compile('|'.join(re.escape(v) + r'(?=$|[/\s\'"])' for v in variants))
    for line in lines:
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[0].isdigit() and int(parts[0]) != os.getpid() and 'report.py' not in parts[1] and pat.search(parts[1]):
            return 'yes (pid %s)' % parts[0]
    return 'no'


def _journal(lanes_dir):
    """{ticket: (outcome, lane)} for one lanes dir: logs/land.jsonl (newest line per ticket), else the merged lines of logs/fanout.log."""
    out = {}
    text = read_text(Path(lanes_dir) / 'logs' / 'land.jsonl')
    if text is not None:
        for line in text.splitlines():
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if isinstance(j, dict) and j.get('ticket'):
                out[str(j['ticket'])] = (str(j.get('outcome') or ''), str(j.get('lane') or ''))
        return out
    text = read_text(Path(lanes_dir) / 'logs' / 'fanout.log')
    for m in re.finditer(r'^\[[^\]]*\] \[([^\]]+)\] (T-\d+) merged\b', text or '', re.M):
        out[m.group(2)] = ('merged', m.group(1))
    return out


def _find_ticket(sdlc, tid):
    try:
        ds = sorted(sdlc.iterdir())
    except OSError:
        return None, {}
    for d in ds:
        if d.is_dir() and (d / 'handoff.md').is_file():
            fm = front_matter(read_text(d / 'handoff.md'))
            if fm.get('id') == tid:
                return d, fm
    return None, {}


def _ticket_state(trees, tid, outcome, driver, since):
    """(stage, percent or None) for one ticket. trees: the repo roots to read it from, the lane tree first.
    closed 100 (ticket status done); merged 90 (the land journal says merged); a plan: the mean of the board step
    percents (board.py LADDER, the one derivation) with the weakest step's word; no plan: building 10 (a live driver),
    built 50 (commits since base), queued 0 (none); an unreadable ticket: unknown."""
    task, fm = None, {}
    for t in trees:
        task, fm = _find_ticket(Path(t) / '.sdlc', tid)
        if task:
            break
    if fm.get('status') == 'done':
        return 'closed', 100
    if outcome == 'merged':
        return 'merged', 90
    if task is not None:
        try:
            if str(HERE) not in sys.path:
                sys.path.insert(0, str(HERE))
            import board
            rows, _ = board.task_rows(task)
        except Exception:
            rows = None
        steps = [r for r in (rows or []) if r[1] not in ('task', 'hidden check')]
        if steps:
            low = min(steps, key=lambda r: r[4])
            word = 'verified' if low[4] == 100 else low[3].split(' ·')[0]
            return word, sum(r[4] for r in steps) // len(steps)
    if driver.startswith('yes'):
        return 'building', 10
    if since is None:
        return 'unknown', None
    return ('built', 50) if since > 0 else ('queued', 0)


def collect_fleet(root, env=None):
    """{lanes, waves, unknown} from lanes.py list, git, the land journals and the ticket folders; no model call."""
    root = Path(root)
    r = sibling('lanes.py', ['list', '--all', '--json'], root, 120)
    try:
        rows = json.loads(r[1]) if r and r[0] == 0 else None
    except ValueError:
        rows = None
    if not isinstance(rows, list):
        return {'lanes': [], 'waves': [], 'unknown': ['lanes.list']}
    main = _main_branch(root)
    ps = _ps_lines()
    lanes, journals = [], {}
    for d in rows:
        if not isinstance(d, dict) or d.get('kind') not in FLEET_KINDS or d.get('owner') == 'manual':
            continue
        path, branch = d.get('path') or '', d.get('branch') or ''
        ldir = str(Path(path).parent) if path else ''
        if ldir and ldir not in journals:
            journals[ldir] = _journal(ldir)
        jr = {t: v[0] for t, v in journals.get(ldir, {}).items()}
        into = d.get('into') or ''
        wave = branch if d['kind'] == 'integration' else (into if into and into != main else None)
        rec = read_json(Path(path) / '.lane.json') if path else None
        base_sha = (rec or {}).get('base_sha')
        since = _count(root, '%s..refs/heads/%s' % (base_sha, branch)) if base_sha and branch else None
        ahead = _count(root, '%s..refs/heads/%s' % (main, branch)) if main and branch else None
        states = d.get('states') or []
        if 'closable' not in states:
            landed = 'no'
        elif d['kind'] == 'integration':
            landed = 'yes' if 'merged' in jr.values() else 'no'
        else:
            landed = 'unknown' if since is None else ('yes' if since > 0 else 'no')
        driver = _driver(ps, path) if d.get('exists') and path else 'unknown'
        trees = ([path] if d.get('exists') and path else []) + [str(root)]
        tickets = [str(t) for t in (d.get('tickets') or [])]
        states_t = [dict(zip(('stage', 'pct'), _ticket_state(trees, t, jr.get(t), driver, since)), ticket=t) for t in tickets]
        stages = []
        for s in states_t:
            if s['stage'] not in stages:
                stages.append(s['stage'])
        lanes.append({'lane': d.get('lane') or Path(path).name, 'branch': branch or 'unknown', 'kind': d['kind'], 'wave': wave,
                      'tickets': tickets, 'ticket_states': states_t, 'stage': ','.join(stages) if stages else d['kind'],
                      'driver': driver, 'ahead': ahead if ahead is not None else 'unknown', 'landed': landed,
                      'dir': path or 'unknown', 'lanes_dir': ldir})
    waves = []
    for key in sorted({l['wave'] for l in lanes if l['wave']}):
        members = [l for l in lanes if l['wave'] == key]
        jr = journals.get(next((l['lanes_dir'] for l in members if l['kind'] == 'integration'), members[0]['lanes_dir']), {})
        outs = [v[0] for v in jr.values()]
        tks, seen = [], set()
        for l in members:
            for s in l['ticket_states']:
                if s['ticket'] not in seen:
                    seen.add(s['ticket'])
                    tks.append(dict(s, lane=l['lane']))
        for tid, (outcome, jlane) in jr.items():
            if tid not in seen:
                seen.add(tid)
                st, pct = _ticket_state([str(root)], tid, outcome, 'no', None)
                tks.append({'ticket': tid, 'lane': jlane or 'unknown', 'stage': st, 'pct': pct})
        ahead = _count(root, '%s..refs/heads/%s' % (main, key)) if main else None
        if ahead is None:
            merged = 'unknown'
        else:
            merged = 'no' if ahead > 0 else ('yes' if 'merged' in outs else 'no')
        pcts = [t['pct'] for t in tks if t['pct'] is not None]
        waves.append({'wave': key, 'tickets': tks, 'ahead': ahead if ahead is not None else 'unknown', 'merged': merged,
                      'percent': sum(pcts) // len(pcts) if pcts else None})
    return {'lanes': lanes, 'waves': waves, 'unknown': []}


# ---------------------------------------------------------------- render

def entry_line(e, evidence):
    parts = [e['text'], e.get('outcome') or '-', short_time(e.get('time')) if e.get('time') else '-']
    if evidence:
        parts.append(e.get('evidence') or '-')
    return ' | '.join(parts)


def with_ev(text, pointer, evidence):
    return '%s | %s' % (text, pointer or '-') if evidence else text


def unknown_has(rec, path):
    return path in rec['unknown']


def view_summary(rec, o):
    ev = o['evidence']
    st, h = rec['state'], rec['health']
    out = []
    since = ' since %s' % short_time(st['since']) if st.get('since') else ''
    out.append(('state', with_ev('state: %s%s' % (st['state'], since), st.get('evidence'), ev)))
    needs = rec['needs']
    if needs:
        more = ' (+%d more)' % (len(needs) - 1) if len(needs) > 1 else ''
        out.append(('needs', with_ev('needs: %s: %s%s' % (needs[0]['kind'], needs[0]['text'], more), needs[0]['source'], ev)))
    else:
        out.append(('needs', 'needs: none'))
    tl = rec['timeline']
    out.append(('timeline', 'now: ' + (entry_line(tl['now'][0], ev) if tl['now'] else ('unknown' if unknown_has(rec, 'timeline.now') else 'nothing running'))))
    out.append(('timeline', 'next: ' + (entry_line(tl['next'][0], ev) if tl['next'] else 'nothing planned')))
    if tl['recent']:
        more = ' (+%d more)' % (len(tl['recent']) - 1) if len(tl['recent']) > 1 else ''
        out.append(('timeline', 'recent: ' + entry_line(tl['recent'][0], ev) + more))
    out.append(('health', 'grade: %s [U] | %s' % (h['grade'], h['grade_reason'])))
    if rec['unknown']:
        out.append(('unknown', 'unknown: %d fields (%s%s)' % (len(rec['unknown']), ', '.join(rec['unknown'][:3]), ', ...' if len(rec['unknown']) > 3 else '')))
    return out[:8]


def view_tasks(rec, o):
    ev, tl, w = o['evidence'], rec['timeline'], rec['work']
    out = []
    if w.get('ticket') or w.get('goal'):
        step = ' step %s of %s' % (w['step'], w['steps']) if w.get('step') else ''
        out.append(('work', with_ev('work: %s%s | %s' % (w.get('ticket') or w.get('task'), step, w.get('goal') or '-'), rec['evidence'].get('work'), ev)))
    for k in TENSES:
        if not tl[k]:
            out.append(('timeline', '%s: none' % k))
        for e in tl[k]:
            out.append(('timeline', '%s: %s' % (k, entry_line(e, ev))))
    return out


def view_signals(rec, o):
    ev, h = o['evidence'], rec['health']
    sev = o['severity']
    out = []
    for s in h['signals']:
        if not s['flagged'] or (sev != 'all' and s['severity'] != sev):
            continue
        out.append(('health', with_ev('%s %s: %s %s %s [U]' % (s['severity'], s['name'], fmt_value(s['value']), s['op'], fmt_value(s['threshold'])),
                                      s.get('evidence'), ev)))
    if not out:
        out.append(('health', 'no flags'))
    out.append(('health', 'grade: %s [U] | %s' % (h['grade'], h['grade_reason'])))
    return out


def view_context(rec, o):
    c = rec['health']['context']
    labels = (('peak_context_fill', 'peak context fill'), ('compactions', 'compactions'), ('re_reads', 're-reads'),
              ('read_to_use', 'read-to-use'), ('exploration', 'exploration'), ('workaround_chains', 'workaround chains'),
              ('noisy_output', 'noisy output'))
    out = []
    for k, label in labels:
        if k not in c:
            out.append(('health', '%s: unknown (no transcript)' % label))
        elif k == 'peak_context_fill':
            out.append(('health', '%s: %d%%' % (label, round(100 * c[k]))))
        elif k == 'noisy_output':
            out.append(('health', '%s: %s tokens in the largest tool result' % (label, c[k])))
        else:
            out.append(('health', '%s: %s' % (label, fmt_value(c[k]))))
    if o['evidence']:
        out.append(('health', 'evidence: %s' % (rec['health'].get('transcript') or 'no transcript')))
    return out


def view_cost(rec, o):
    c = rec['cost']
    out = []
    if c['dollars'] is None:
        d = 'unpriced' if c.get('unpriced_runs') else 'unknown'
    else:
        d = '$%.2f' % c['dollars']
    runs = '' if c.get('priced_runs') is None else ' (%d priced, %d unpriced)' % (c['priced_runs'], c['unpriced_runs'])
    out.append(('cost', with_ev('dollars: %s%s' % (d, runs), c.get('evidence'), o['evidence'])))
    out.append(('cost', 'tokens: %s' % (c['tokens'] if c['tokens'] is not None else 'unknown')))
    out.append(('cost', 'active minutes: %s' % (c['active_minutes'] if c['active_minutes'] is not None else 'unknown')))
    if c['budget'] == 'none':
        b = 'none set'
    elif c['budget'] is None:
        b = 'unknown'
    else:
        b = '$%.2f, %s%% used' % (c['budget'], c['budget_percent'] if c['budget_percent'] is not None else '?')
    out.append(('cost', 'budget: %s' % b))
    return out


def view_children(rec, o):
    kids = rec['work']['children']
    if not kids:
        return [('work', 'children: none' if rec['work'].get('task') else 'children: unknown (no task for this thread)')]
    return [('work', with_ev('%s %s%s | %s' % (k['status'], k['name'], ' ' + k['step'] if k['step'] else '', fmt_min(k['elapsed_minutes'])),
                             k['evidence'], o['evidence'])) for k in kids]


def view_identity(rec, o):
    out = [('identity', '%s: %s' % (k, v if v is not None else 'unknown')) for k, v in rec['identity'].items()]
    if o['evidence']:
        out.append(('identity', 'evidence: %s' % rec['evidence'].get('identity')))
    return out


def view_needs(rec, o):
    if not rec['needs']:
        return [('needs', 'none')]
    return [('needs', with_ev('%s: %s' % (n['kind'], n['text']), n['source'], o['evidence'])) for n in rec['needs']]


def view_evidence(rec, o):
    out = [('state', 'state: %s' % rec['state'].get('evidence')), ('work', 'work: %s' % rec['evidence'].get('work')),
           ('identity', 'identity: %s' % rec['evidence'].get('identity')), ('cost', 'cost: %s' % (rec['cost'].get('evidence') or 'no task'))]
    for k in TENSES:
        for e in rec['timeline'][k]:
            out.append(('timeline', '%s %s: %s' % (k, e['text'], e['evidence'] or '-')))
    for s in rec['health']['signals']:
        if s['flagged']:
            out.append(('health', 'signal %s: %s' % (s['name'], s['evidence'] or '-')))
    for n in rec['needs']:
        out.append(('needs', 'need %s: %s' % (n['text'][:60], n['source'])))
    if rec['unknown']:
        out.append(('unknown', 'unknown: %s' % ', '.join(rec['unknown'])))
    return out


def view_lanes(rec, o):
    if 'lanes' not in rec or rec.get('fleet_unknown'):
        return [('unknown', 'lanes: unknown (lanes.py list gave no rows)')]
    if not rec['lanes']:
        return [('work', 'lanes: none')]
    ev = o['evidence']
    out = [('work', 'lane | ticket | stage | driver alive | ahead of main | landed | dir')]
    for l in rec['lanes']:
        out.append(('work', with_ev(' | '.join([l['lane'], ','.join(l['tickets']) or '-', l['stage'], l['driver'], str(l['ahead']),
                                                l['landed'], l['dir']]), 'lanes.py list --all --json; git rev-list; ps', ev)))
    return out


def view_waves(rec, o):
    if 'waves' not in rec or rec.get('fleet_unknown'):
        return [('unknown', 'waves: unknown (lanes.py list gave no rows)')]
    if not rec['waves']:
        return [('work', 'waves: none')]
    ev = o['evidence']
    out = []
    for w in rec['waves']:
        pct = '%d%%' % w['percent'] if w['percent'] is not None else 'unknown'
        out.append(('work', with_ev('%s | %d tickets | %s | ahead of main %s | merged %s' % (w['wave'], len(w['tickets']), pct, w['ahead'], w['merged']),
                                    'git rev-list; logs/land.jsonl', ev)))
        for t in w['tickets']:
            tp = '%d%%' % t['pct'] if t['pct'] is not None else t['stage']
            out.append(('work', '  %s | lane %s | %s | %s' % (t['ticket'], t['lane'], t['stage'], tp)))
    return out


RENDERERS = {'summary': view_summary, 'tasks': view_tasks, 'signals': view_signals, 'needs': view_needs, 'context': view_context,
             'cost': view_cost, 'children': view_children, 'identity': view_identity, 'evidence': view_evidence,
             'lanes': view_lanes, 'waves': view_waves}


def compare(prev, cur, name):
    if prev is None:
        return ['no earlier snapshot']
    out = ['since snapshot %s' % name]
    a, b = prev.get('state', {}).get('state'), cur['state']['state']
    if a != b:
        out.append('state: %s -> %s' % (a, b))
    a, b = prev.get('health', {}).get('grade'), cur['health']['grade']
    if a != b:
        out.append('grade: %s -> %s' % (a, b))
    pf, cf = set(prev.get('health', {}).get('flags') or []), set(cur['health']['flags'])
    for f in sorted(cf - pf):
        out.append('+ flag %s' % f)
    for f in sorted(pf - cf):
        out.append('- flag %s' % f)
    seen = {e.get('text') for e in (prev.get('timeline', {}).get('recent') or [])}
    for e in cur['timeline']['recent']:
        if e['text'] not in seen:
            out.append('+ recent %s' % e['text'])
    pn, cn = {n.get('text') for n in prev.get('needs') or []}, {n['text'] for n in cur['needs']}
    for n in sorted(cn - pn):
        out.append('+ need %s' % n)
    for n in sorted(pn - cn):
        out.append('- need %s' % n)
    if len(out) == 1:
        out.append('no change')
    return out


def usage_text():
    return ('views: %s\noptions: %s (--session is reserved and refused)\n'
            'usage: report.py render [view...] [--since T] [--last N] [--next N] [--only G,...] [--severity problem|likely|all] '
            '[--format text|md|json] [--evidence] [--compare last] [--explain] [--no-snapshot]' % (' '.join(VIEWS), ' '.join(OPTIONS)))


def parse_render_args(argv):
    o = {'views': [], 'since': None, 'last': 5, 'next': 3, 'only': None, 'severity': 'all', 'format': 'text',
         'evidence': False, 'compare': None, 'explain': False, 'snapshot': True}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            name, eq, val = a.partition('=')
            if name in RESERVED or name in VALUED:
                if not eq:
                    if i + 1 >= len(argv):
                        raise Refuse(2, 'report.py: %s needs a value' % name)
                    i += 1
                    val = argv[i]
                if name == '--session':
                    RULES['refuse_session'](val)
                elif name in ('--last', '--next'):
                    if not val.isdigit():
                        raise Refuse(2, 'report.py: %s needs a whole number, got %r' % (name, val))
                    o[name[2:]] = int(val)
                elif name == '--only':
                    gs = [g.strip() for g in val.split(',') if g.strip()]
                    bad = [g for g in gs if g not in GROUPS]
                    if bad or not gs:
                        raise Refuse(2, 'report.py: --only names unknown group(s) %s; groups: %s' % (', '.join(bad) or '(none)', ' '.join(GROUPS)))
                    o['only'] = gs
                elif name == '--severity':
                    if val not in ('problem', 'likely', 'all'):
                        raise Refuse(2, 'report.py: --severity is problem, likely or all, got %r' % val)
                    o['severity'] = val
                elif name == '--format':
                    if val not in ('text', 'md', 'json'):
                        raise Refuse(2, 'report.py: --format is text, md or json, got %r' % val)
                    o['format'] = val
                elif name == '--compare':
                    if val != 'last':
                        raise Refuse(2, 'report.py: --compare takes only last, got %r' % val)
                    o['compare'] = val
                elif name == '--since':
                    o['since'] = val
            elif name in ('--evidence', '--explain', '--no-snapshot') and not eq:
                if name == '--no-snapshot':
                    o['snapshot'] = False
                else:
                    o[name[2:]] = True
            else:
                raise Refuse(2, 'report.py: unknown option %r' % a)
        else:
            RULES['check_view'](a)
            if a not in o['views']:
                o['views'].append(a)
        i += 1
    return o


def render(rec, o, compare_lines=None, explain_lines=None):
    views = o['views'] or ['summary']
    ev = o['evidence']
    order = []
    for v in views:
        for w in (FULL_ORDER if v == 'full' else (v,)):
            if w in RENDERERS and w not in order:
                order.append(w)
        if v == 'full':
            ev = True
    oo = dict(o, evidence=ev)
    sections = []
    for v in order:
        lines = RENDERERS[v](rec, oo)
        if o['only']:
            lines = [l for l in lines if l[0] in o['only']]
        sections.append((v, [t for _, t in lines]))
    if explain_lines is not None:
        sections.append(('explain', explain_lines))
    if compare_lines is not None:
        sections.append(('compare', compare_lines))
    out = []
    head = len(sections) > 1
    for name, lines in sections:
        if o['format'] == 'md':
            if head:
                out.append('## %s' % name)
            out.extend('- ' + l for l in lines)
        else:
            if head:
                out.append('%s:' % name)
            out.extend(lines)
    return '\n'.join(out) + '\n'


def project_root(cwd=None):
    cwd = Path(cwd or os.getcwd())
    r = run(['git', 'rev-parse', '--show-toplevel'], cwd, 10)
    return Path(r[1].strip()) if r and r[0] == 0 and r[1].strip() else cwd


def cmd_render(argv, root, env, now, out):
    o = parse_render_args(argv)
    th = read_thresholds(root)
    snapdir = Path(root) / '.sdlc' / 'runtime' / 'report'
    prev, prev_name = None, None
    if o['compare']:
        p = RULES['newest_snapshot'](snapdir)
        if p is not None:
            prev = read_json(p)
            if prev is None:
                raise Refuse(2, 'report.py: cannot read snapshot %s' % p)
            prev_name = p.name
    rec = collect(root, env, now, th, o['since'], o['last'], o['next'])
    if o['snapshot'] and (Path(root) / '.sdlc').is_dir():
        RULES['write_snapshot'](root, rec, now or utcnow())
    if any(v in ('lanes', 'waves') for v in o['views']):
        fleet = RULES['collect_fleet'](root, env)
        rec = dict(rec, lanes=fleet['lanes'], waves=fleet['waves'], fleet_unknown=bool(fleet['unknown']))
    if o['format'] == 'json':
        d = rec
        if o['only']:
            d = {k: v for k, v in rec.items() if k not in GROUPS or k in o['only'] or k == 'unknown'}
        out.write(json.dumps(d, indent=1, sort_keys=True, default=str) + '\n')
        return 0
    cmp_lines = compare(prev, rec, prev_name) if o['compare'] else None
    exp_lines = RULES['explain'](rec['health']['signals']) if o['explain'] else None
    out.write(render(rec, o, cmp_lines, exp_lines))
    return 0


def main(argv=None, root=None, env=None, now=None, out=None, err=None):
    argv = sys.argv[1:] if argv is None else argv
    out, err = out or sys.stdout, err or sys.stderr
    env = os.environ if env is None else env
    try:
        if not argv or argv[0] not in ('collect', 'render', 'selftest'):
            raise Refuse(2, 'report.py: the subcommand is collect, render or selftest')
        if argv[0] == 'selftest':
            return selftest()
        root = Path(root) if root else project_root()
        if argv[0] == 'collect':
            if argv[1:]:
                raise Refuse(2, 'report.py: collect takes no arguments')
            out.write(json.dumps(collect(root, env, now), indent=1, sort_keys=True, default=str) + '\n')
            return 0
        return cmd_render(argv[1:], root, env, now, out)
    except Refuse as e:
        err.write(e.message + '\n' + usage_text() + '\n')
        return e.code
    except CollectorError as e:
        err.write('report.py: collector error: %s\n' % e)
        return 1


# ---------------------------------------------------------------- selftest

def _tl(ts, kind, content, **extra):
    d = {'type': kind, 'timestamp': iso(ts), 'message': {'role': 'assistant' if kind == 'assistant' else 'user', 'content': content}}
    d.update(extra)
    return json.dumps(d)


class _Tx(object):
    """Builds a fixture transcript: tool calls at given times, with ok or failing results."""

    def __init__(self, t0):
        self.t0, self.lines, self.n = t0, [], 0

    def prompt(self, m, text='go'):
        self.lines.append(_tl(self.t0 + dt.timedelta(minutes=m), 'user', text))

    def call(self, m, name, inp, fail=False, size=10, tokens=1000):
        self.n += 1
        t = self.t0 + dt.timedelta(minutes=m)
        tid = 'toolu_%d' % self.n
        a = json.loads(_tl(t, 'assistant', [{'type': 'tool_use', 'id': tid, 'name': name, 'input': inp}]))
        a['message'].update({'id': 'msg_%d' % self.n, 'model': 'claude-test', 'usage': {'input_tokens': tokens, 'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0}})
        self.lines.append(json.dumps(a))
        self.lines.append(_tl(t + dt.timedelta(seconds=20), 'user', [{'type': 'tool_result', 'tool_use_id': tid, 'is_error': fail, 'content': 'x' * size}]))

    def compact(self, m):
        self.lines.append(json.dumps({'type': 'system', 'subtype': 'compact_boundary', 'timestamp': iso(self.t0 + dt.timedelta(minutes=m))}))

    def write(self, path):
        Path(path).write_text('\n'.join(self.lines) + '\n', encoding='utf-8')
        return Path(path)


def _w(p, text):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return p


def _fixture(base, now, pid, runs_text=None, running=True, next_section=True):
    """A fixture repo: one open ticket with two steps, a dependent ticket, a closed ticket, results and runs.jsonl."""
    root = Path(base)
    root.mkdir(parents=True, exist_ok=True)
    gitc = ['git', '-C', str(root), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false']
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    _w(root / 'f.txt', 'x\n')
    subprocess.run(gitc + ['add', '-A'], check=True)
    subprocess.run(gitc + ['commit', '-q', '-m', 'init'], check=True)
    sdlc = root / '.sdlc'
    _w(sdlc / 'config', 'ticket_folders: numbered\n')
    nxt = '\n## Next\n- tidy the docs\n' if next_section else ''
    t = _w(sdlc / '0001-demo' / 'handoff.md', '---\nid: T-0001\ntitle: "demo"\ntype: feature\nstatus: claimed\nsize: L3\ndepends: []\n---\n\n'
           '## Goal\nShip the demo.\n\n## Intent\n- Done when: `true` exits 0.\n- decide: pick a name for the demo\n' + nxt).parent
    ago = lambda m: iso(now - dt.timedelta(minutes=m))
    s1, s2 = t / 'step-1', t / 'step-2'
    _w(s1 / 'handoff.md', '## Step 1: one\n### Acceptance criteria\n- (red) `python3 check.py one`\n')
    _w(s1 / 'builder-L2.md', '## Status\ndone\n\n## Changes\nNone\n')
    _w(s1 / 'builder-L2.attempt.json', json.dumps({'name': 'builder-L2', 'role': 'builder', 'level': 'L2', 'status': 'completed',
                                                   'started_at': ago(60), 'finished_at': ago(40), 'parent_pid': pid}))
    _w(s1 / 'verifier-L2.md', '## Verdict\npass\n')
    _w(s1 / 'verifier-L2.attempt.json', json.dumps({'name': 'verifier-L2', 'role': 'verifier', 'level': 'L2', 'status': 'completed',
                                                    'started_at': ago(40), 'finished_at': ago(30), 'parent_pid': pid}))
    _w(s2 / 'handoff.md', '## Step 2: two\n### Acceptance criteria\n- (red) `python3 check.py two`\n')
    _w(s2 / 'builder-L3.attempt.json', json.dumps({'name': 'builder-L3', 'role': 'builder', 'level': 'L3', 'status': 'running' if running else 'completed',
                                                   'started_at': ago(10), 'parent_pid': pid}))
    _w(t / 'runs.jsonl', runs_text if runs_text is not None else
       json.dumps({'ts': ago(40), 'role': 'builder', 'cost_usd': 1.5, 'usage': {'input_tokens': 10, 'output_tokens': 5}, 'duration_ms': 60000}) + '\n')
    _w(sdlc / '0002-after' / 'handoff.md', '---\nid: T-0002\ntitle: "after"\ntype: feature\nstatus: proposed\nsize: L2\ndepends: [T-0001]\n---\n\n## Goal\nLater.\n')
    old = _w(sdlc / '.0000-old' / 'handoff.md', '---\nid: T-0000\ntitle: "old"\ntype: chore\nstatus: done\nsize: L1\ndepends: []\n---\n\n## Goal\nOld.\n').parent
    _w(old / 'verifier-L1.attempt.json', json.dumps({'name': 'verifier-L1', 'role': 'verifier', 'status': 'completed', 'started_at': ago(70), 'finished_at': ago(65)}))
    return root


def _fleet_fixture(base):
    """A throwaway repo with two waves: fanout/wave01 running (lane a: no plan, lane b: two steps, one passed) and
    fanout/wave02 merged into main and closed (its lane is gone, its land journal says merged)."""
    root = Path(base)
    root.mkdir(parents=True, exist_ok=True)

    def gc(cwd, *a):
        r = subprocess.run(['git', '-C', str(cwd), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false'] + list(a),
                           check=True, capture_output=True, text=True)
        return r.stdout.strip()

    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    gc(root, 'symbolic-ref', 'HEAD', 'refs/heads/main')
    _w(root / '.sdlc' / 'config', 'ticket_folders: numbered\n')
    for folder, tid, status in (('0101-a', 'T-0101', 'claimed'), ('0102-b', 'T-0102', 'claimed'), ('.0201-c', 'T-0201', 'done')):
        _w(root / '.sdlc' / folder / 'handoff.md', '---\nid: %s\ntitle: "t"\ntype: chore\nstatus: %s\nsize: L2\ndepends: []\n---\n\n## Goal\nx\n' % (tid, status))
    _w(root / 'f.txt', 'x\n')
    gc(root, 'add', '-A')
    gc(root, 'commit', '-q', '-m', 'init')
    one, two = root / '.worktrees' / 'fanout01', root / '.worktrees' / 'fanout02'
    for d in (one, two):
        (d / 'logs').mkdir(parents=True)
        _w(d / 'merge.lock', '')
    gc(root, 'worktree', 'add', '-q', '-b', 'fanout/wave01', str(one / 'integration'), 'main')
    gc(one / 'integration', 'commit', '-q', '--allow-empty', '-m', 'wave01 work')
    for lane, tid in (('a', 'T-0101'), ('b', 'T-0102')):
        gc(root, 'worktree', 'add', '-q', '-b', 'fanout/wave01-' + lane, str(one / lane), 'fanout/wave01')
        _w(one / lane / '.lane.json', json.dumps({'lane': lane, 'kind': 'fanout', 'branch': 'fanout/wave01-' + lane, 'base': 'fanout/wave01',
                                                  'base_sha': gc(root, 'rev-parse', 'fanout/wave01'), 'into': 'fanout/wave01', 'tickets': [tid]}))
    _w(one / 'b' / 'b.txt', 'b\n')
    gc(one / 'b', 'add', 'b.txt')
    gc(one / 'b', 'commit', '-q', '-m', 'b work')
    b = one / 'b' / '.sdlc' / '0102-b'
    _w(b / 'step-1' / 'handoff.md', '## Step 1: one\nlevel: L2\n')
    _w(b / 'step-1' / 'builder-L2.md', '## Status\ndone\n')
    _w(b / 'step-1' / 'verifier-L2.md', '## Verdict\npass\n')
    _w(b / 'step-2' / 'handoff.md', '## Step 2: two\nlevel: L2\n')
    gc(root, 'worktree', 'add', '-q', '-b', 'fanout/wave02', str(two / 'integration'), 'main')
    gc(two / 'integration', 'commit', '-q', '--allow-empty', '-m', 'wave02 work')
    gc(root, 'merge', '-q', '--no-ff', '-m', 'merge wave02', 'fanout/wave02')
    _w(two / 'logs' / 'land.jsonl', json.dumps({'run_id': 'r', 'lane': 'c', 'branch': 'fanout/wave02-c', 'ticket': 'T-0201', 'outcome': 'merged',
                                                 'commit': 'abc1234', 'kind': 'solo', 'tier': 'L2', 'files': []}) + '\n')
    return root


def _fake_runner(cmd, cwd, timeout=15):
    if len(cmd) > 1 and cmd[1].endswith('gate_lock.py'):
        return 0, json.dumps({'queue': []}), ''
    if len(cmd) > 1 and cmd[1].endswith('budget.py'):
        return 2, '', 'no budget\n'
    if len(cmd) > 1 and cmd[1].endswith('steps.py'):
        return 0, 'build L2\nreason: fixture\n', ''
    return run(cmd, cwd, timeout)


def selftest():
    global RUNNER
    failures = []
    now = utcnow()
    saved_runner, RUNNER = RUNNER, _fake_runner
    tmp = tempfile.TemporaryDirectory()
    base = Path(tmp.name)
    th = dict(THRESHOLDS)
    live = os.getpid()
    counter = [0]

    def fresh(**kw):
        counter[0] += 1
        return _fixture(base / ('r%d' % counter[0]), now, live, **kw)

    def env_for(root, tx=None, pid=None):
        e = {'CLAUDE_PID': str(pid or live), 'CLAUDE_CODE_SESSION_ID': 'sess-1', 'SDLC_CLAUDE_PROJECTS': str(base / 'projects')}
        e['SDLC_REPORT_TRANSCRIPT'] = str(tx) if tx else str(base / 'absent.jsonl')
        return e

    def call(argv, root, env):
        o, e = io.StringIO(), io.StringIO()
        rc = main(argv, root=root, env=env, now=now, out=o, err=e)
        return rc, o.getvalue(), e.getvalue()

    def safe(fn):
        try:
            return bool(fn())
        except Exception:
            return False

    def control(name, rule, noop, case):
        saved = RULES[rule]
        RULES[rule] = noop
        try:
            red = not safe(case)
        finally:
            RULES[rule] = saved
        green = safe(case)
        if red and green:
            print('ok: control %s: red without the rule, green with it' % name)
        else:
            print('FAIL: control %s: %s without the rule, %s with it' % (name, 'red' if red else 'GREEN', 'green' if green else 'RED'))
            failures.append(name)

    def case(label, ok):
        print('%s: %s' % ('ok' if ok else 'FAIL', label))
        if not ok:
            failures.append(label)

    def tx_file(build):
        counter[0] += 1
        t = _Tx(now - dt.timedelta(minutes=40))
        build(t)
        return t.write(base / ('tx%d.jsonl' % counter[0]))

    def flagged(rec, name):
        return name in rec['health']['flags']

    try:
        root = fresh()

        # dead pid
        p = subprocess.Popen([sys.executable, '-c', 'pass'])
        p.wait()
        dead = p.pid
        control('dead pid', 'pid_alive', lambda pid: True,
                lambda: (lambda r: r['state']['state'] == 'dead' and flagged(r, 'dead') and r['health']['grade'] == 'D')(
                    collect(root, env_for(root, pid=dead), now, th)))

        # stalled: the last tool call 30 minutes ago, no running child, no open question
        r_idle = fresh(running=False)
        tx_old = tx_file(lambda t: (t.prompt(0), t.call(10, 'Read', {'file_path': '/a'})))
        old_m = now - dt.timedelta(minutes=29)
        for f in r_idle.rglob('*'):
            if f.is_file() and '.git' not in f.parts:
                os.utime(str(f), (old_m.timestamp(), old_m.timestamp()))
        control('stalled', 'stall', lambda f, t: None,
                lambda: (lambda r: r['state']['state'] == 'stalled' and flagged(r, 'stall'))(collect(r_idle, env_for(r_idle, tx_old), now, th)))

        # unknown cost: an unreadable runs.jsonl is unknown, never 0
        r_bad = fresh(runs_text='{not json\n')
        control('unknown cost', 'read_runs', lambda p: [],
                lambda: (lambda r: 'cost.dollars' in r['unknown'] and r['cost']['dollars'] is None)(collect(r_bad, env_for(r_bad), now, th)))
        r_unpriced = fresh(runs_text=json.dumps({'role': 'builder', 'cost_usd': None}) + '\n')
        rec = collect(r_unpriced, env_for(r_unpriced), now, th)
        case('an unpriced run reads unpriced, not $0', rec['cost']['dollars'] is None and rec['cost']['unpriced_runs'] == 1
             and 'dollars: unpriced' in call(['render', 'cost', '--no-snapshot'], r_unpriced, env_for(r_unpriced))[1])

        # unknown view
        def unknown_view():
            rc, _, e = call(['render', 'nosuchview', '--no-snapshot'], root, env_for(root))
            return rc == 2 and all(v in e for v in VIEWS) and all(o in e for o in OPTIONS)
        control('unknown view', 'check_view', lambda v: None, unknown_view)
        rc, _, e = call(['render', '--bogus', '--no-snapshot'], root, env_for(root))
        case('an unknown option exits 2 and lists every option', rc == 2 and all(o in e for o in OPTIONS))

        # verb outside list
        def verb_case():
            ok = entry('built', 'recent', 'step 1', 'T-0001')['text'] == 'built step 1 T-0001'
            ok = ok and entry('built', 'now', 'step 1')['text'].startswith('building')
            ok = ok and entry('verified', 'next', 'step 1', trigger='after the build')['text'] == 'will verify step 1 after the build'
            try:
                entry('fixed', 'recent', 'step 1')
            except CollectorError:
                return ok
            return False
        control('verb outside list', 'verb_check', lambda v: None, verb_case)

        # late failure: four turns ten minutes apart; the first failing check falls in the last turn
        def lf_build(t):
            for k in range(4):
                t.prompt(k * 10, 'turn %d' % (k + 1))
                t.call(k * 10 + 1, 'Bash', {'command': 'python3 check.py %d' % k}, fail=(k == 3))
            t.prompt(32, 'end')
        tx_lf = tx_file(lf_build)
        control('late failure', 'late failure', lambda f, t: None,
                lambda: (lambda r: flagged(r, 'late failure') and r['health']['grade'] == 'D')(collect(root, env_for(root, tx_lf), now, th)))

        # re-reads: one file read three times with no edit between
        tx_rr = tx_file(lambda t: [t.call(m, 'Read', {'file_path': '/repo/a.py'}) for m in (1, 2, 3)])
        tx_rr_ok = tx_file(lambda t: [t.call(1, 'Read', {'file_path': '/repo/a.py'}), t.call(2, 'Edit', {'file_path': '/repo/a.py'}),
                                      t.call(3, 'Read', {'file_path': '/repo/a.py'}), t.call(4, 'Read', {'file_path': '/repo/a.py'})])
        control('re-reads', 're-reads', lambda f, t: None,
                lambda: flagged(collect(root, env_for(root, tx_rr), now, th), 're-reads')
                and not flagged(collect(root, env_for(root, tx_rr_ok), now, th), 're-reads'))

        # snapshot
        r_snap = fresh()

        def snap_case():
            d = r_snap / '.sdlc' / 'runtime' / 'report'
            before = len(list(d.glob('*.json'))) if d.exists() else 0
            call(['render', '--no-snapshot'], r_snap, env_for(r_snap))
            mid = len(list(d.glob('*.json'))) if d.exists() else 0
            rc, _, _ = call(['render'], r_snap, env_for(r_snap))
            files = sorted(d.glob('*.json')) if d.exists() else []
            return (rc == 0 and mid == before and len(files) == before + 1
                    and read_json(files[-1]).get('schema') == SCHEMA and re.match(r'^\d{8}T\d{6}Z\.json$', files[-1].name))
        control('snapshot', 'write_snapshot', lambda root, rec, now: None, snap_case)

        # compare last: the newest snapshot by name, even when its mtime is older
        r_cmp = fresh()
        d = r_cmp / '.sdlc' / 'runtime' / 'report'
        a = _w(d / '20200101T000000Z.json', json.dumps({'schema': SCHEMA, 'state': {'state': 'old-by-name'}, 'health': {'grade': 'A', 'flags': []}}))
        b = _w(d / '20200102T000000Z.json', json.dumps({'schema': SCHEMA, 'state': {'state': 'dead'}, 'health': {'grade': 'Z', 'flags': ['x']},
                                                       'timeline': {'recent': []}, 'needs': []}))
        os.utime(str(b), (1000000, 1000000))
        os.utime(str(a), (2000000, 2000000))

        def cmp_case():
            rc, o, _ = call(['render', '--compare', 'last', '--no-snapshot'], r_cmp, env_for(r_cmp))
            return rc == 0 and 'compare:' in o.splitlines() and '20200102T000000Z.json' in o and 'grade: Z -> ' in o and '- flag x' in o
        control('compare last', 'newest_snapshot', lambda d: None, cmp_case)
        _w(d / '20990101T000000Z.json', '{broken')
        rc, _, e = call(['render', '--compare', 'last', '--no-snapshot'], r_cmp, env_for(r_cmp))
        case('an unreadable compare snapshot exits 2', rc == 2 and 'cannot read snapshot' in e)

        # explain
        def explain_case():
            rc, o, _ = call(['render', 'signals', '--explain', '--no-snapshot'], root, env_for(root, tx_rr))
            line = [l for l in o.splitlines() if l.startswith('re-reads: rule ')]
            return rc == 0 and 'explain:' in o.splitlines() and line and 'value 3' in line[0] and 'threshold >= 3' in line[0] and '[U]' in line[0]
        control('explain', 'explain', lambda s: [], explain_case)

        # session refused
        def session_case():
            rc, _, e = call(['render', '--session', 'other', '--no-snapshot'], root, env_for(root))
            return rc == 2 and '--session' in e and all(v in e for v in VIEWS)
        control('session refused', 'refuse_session', lambda v: None, session_case)

        # intended next: an item with no ticket and no step is intended; one with a ticket is planned
        def next_case():
            r = collect(root, env_for(root), now, th, nxt=5)
            marks = {e['text']: e['mark'] for e in r['timeline']['next']}
            return (any('tidy the docs' in k and v == 'intended' for k, v in marks.items())
                    and any('T-0002' in k and v == 'planned' for k, v in marks.items()))
        control('intended next', 'next_mark', lambda it: 'planned', next_case)

        # the other draft signals
        tx_trivial_root = fresh()
        s1 = tx_trivial_root / '.sdlc' / '0001-demo' / 'step-1'
        _w(s1 / 'verifier-L2.md', '## Verdict\nfail\n\n## Criteria\n- #1 `grep -q x f`: fail. Evidence: grep found nothing.\n')
        control('trivial last failure', 'trivial last failure', lambda f, t: None,
                lambda: flagged(collect(tx_trivial_root, env_for(tx_trivial_root), now, th), 'trivial last failure'))

        r_rw = fresh()
        _w(r_rw / '.sdlc' / '0001-demo' / 'step-1' / 'runs.jsonl',
           ''.join(json.dumps({'role': 'verifier', 'cost_usd': 0.1}) + '\n' for _ in range(2)))
        control('rework', 'rework', lambda f, t: None, lambda: flagged(collect(r_rw, env_for(r_rw), now, th), 'rework'))

        tx_cfl = tx_file(lambda t: (t.prompt(0), t.call(1, 'Read', {'file_path': '/a'}), t.call(39, 'Bash', {'command': 'python3 check.py two'})))
        control('check first run late', 'check first run late', lambda f, t: None,
                lambda: flagged(collect(root, env_for(root, tx_cfl), now, th), 'check first run late'))

        tx_pk = tx_file(lambda t: t.call(1, 'Read', {'file_path': '/a'}, tokens=180000))
        control('peak context fill', 'peak context fill', lambda f, t: None,
                lambda: (lambda r: flagged(r, 'peak context fill') and r['health']['context']['peak_context_fill'] == 0.9)(collect(root, env_for(root, tx_pk), now, th)))

        tx_cp = tx_file(lambda t: (t.call(1, 'Read', {'file_path': '/a'}), t.compact(5), t.compact(9)))
        control('compactions', 'compactions', lambda f, t: None, lambda: flagged(collect(root, env_for(root, tx_cp), now, th), 'compactions'))

        tx_ru = tx_file(lambda t: [t.call(1, 'Read', {'file_path': '/f%d' % k}) for k in range(16)])
        control('read-to-use', 'read-to-use', lambda f, t: None, lambda: flagged(collect(root, env_for(root, tx_ru), now, th), 'read-to-use'))

        tx_ex = tx_file(lambda t: [t.call(1, 'Grep', {'pattern': 'p%d' % k}) for k in range(26)] + [t.call(2, 'Edit', {'file_path': '/a'})])
        control('exploration', 'exploration', lambda f, t: None, lambda: flagged(collect(root, env_for(root, tx_ex), now, th), 'exploration'))

        tx_wa = tx_file(lambda t: (t.call(1, 'Bash', {'command': 'a'}, fail=True), t.call(2, 'Bash', {'command': 'b'}, fail=True),
                                   t.call(3, 'Bash', {'command': 'c'})))
        control('workaround chain', 'workaround chain', lambda f, t: None, lambda: flagged(collect(root, env_for(root, tx_wa), now, th), 'workaround chain'))

        tx_rt = tx_file(lambda t: [t.call(m, 'Bash', {'command': 'same'}, fail=True) for m in (1, 2, 3)])
        control('retries', 'retries', lambda f, t: None, lambda: flagged(collect(root, env_for(root, tx_rt), now, th), 'retries'))

        r_rev = fresh()
        subprocess.run(['git', '-C', str(r_rev), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false',
                        'commit', '-q', '--allow-empty', '-m', 'Revert "init"'], check=True)
        control('dead-end work', 'dead-end work', lambda f, t: None, lambda: flagged(collect(r_rev, env_for(r_rev), now, th), 'dead-end work'))

        tx_no = tx_file(lambda t: t.call(1, 'Bash', {'command': 'cat big'}, size=4 * 20001))
        control('noisy output', 'noisy output', lambda f, t: None, lambda: flagged(collect(root, env_for(root, tx_no), now, th), 'noisy output'))

        def gate_runner(cmd, cwd, timeout=15):
            if len(cmd) > 1 and cmd[1].endswith('gate_lock.py'):
                return 0, json.dumps({'queue': [{'position': 1, 'repo': str(root), 'waited_s': 600}]}), ''
            return _fake_runner(cmd, cwd, timeout)
        RUNNER = gate_runner
        try:
            control('gate wait', 'gate wait', lambda f, t: None, lambda: flagged(collect(root, env_for(root), now, th), 'gate wait'))
        finally:
            RUNNER = _fake_runner

        # output shape
        rc, o, _ = call(['render', '--no-snapshot'], root, env_for(root, tx_rr))
        case('summary prints 1 to 8 lines with no header', rc == 0 and 1 <= len(o.splitlines()) <= 8 and not any(l in VIEWS_HEAD for l in o.splitlines()))
        rc, o, _ = call(['render', 'full', '--no-snapshot'], root, env_for(root, tx_rr))
        heads = [l for l in o.splitlines() if l.endswith(':') and l[:-1] in VIEWS]
        case('full prints every section header in order', rc == 0 and heads == [v + ':' for v in FULL_ORDER])
        rc, o, _ = call(['render', '--format', 'json', '--no-snapshot'], root, env_for(root))
        d = json.loads(o)
        case('json has the schema, nine groups, and context paths under unknown with no transcript',
             d['schema'] == SCHEMA and all(k in d for k in GROUPS) and isinstance(d['health']['context'], dict)
             and all('health.context.' + k in d['unknown'] for k in CONTEXT_KEYS))
        rec = collect(root, env_for(root), now, th)
        case('the thread task, running child, needs and next come from records',
             rec['work']['ticket'] == 'T-0001' and rec['state']['state'] == 'waiting-on-role' and rec['work']['step'] == 2
             and any(n['text'] == 'pick a name for the demo' for n in rec['needs'])
             and rec['timeline']['now'] and rec['timeline']['now'][0]['text'].startswith('building step 2')
             and any(e['verb'] == 'verified' for e in rec['timeline']['recent'])
             and any(e['verb'] == 'closed' for e in rec['timeline']['recent']) and rec['cost']['dollars'] == 1.5)
        rc, o, e = call(['render', '--last', 'x', '--no-snapshot'], root, env_for(root))
        case('a bad option value exits 2', rc == 2)
        _w(root / '.sdlc' / 'config', 'report.stall_minutes: soon\n')
        rc, o, e = call(['render', '--no-snapshot'], root, env_for(root))
        case('an unreadable threshold in .sdlc/config exits 2', rc == 2 and 'report.stall_minutes' in e)
        # lanes and waves (T-0483): two waves, one running and one merged and closed
        fl = _fleet_fixture(base / 'fleet')
        a_path = str(fl / '.worktrees' / 'fanout01' / 'a')

        def fleet_runner(cmd, cwd, timeout=15):
            if cmd and cmd[0] == 'ps':
                return 0, '    1 /sbin/launchd\n 4242 claude -p --plugin-dir %s/plugins/x\n' % a_path, ''
            return _fake_runner(cmd, cwd, timeout)
        RUNNER = fleet_runner
        try:
            saved_views = globals()['VIEWS']
            globals()['VIEWS'] = tuple(v for v in saved_views if v not in ('lanes', 'waves'))
            try:
                rc_old, _, e_old = call(['render', 'lanes', 'waves', '--no-snapshot'], fl, env_for(fl))
            finally:
                globals()['VIEWS'] = saved_views
            case('before the views exist, lanes and waves are refused as unknown (observed red)', rc_old == 2 and "unknown view 'lanes'" in e_old)
            def lanes_ok():
                rc, o, _ = call(['render', 'lanes', '--no-snapshot'], fl, env_for(fl))
                ls = o.splitlines()
                rows = {l.split(' | ')[0]: l.split(' | ') for l in ls[1:]}
                return (rc == 0 and ls[0].startswith('lane | ticket | stage | driver alive')
                        and rows['a'][1:6] == ['T-0101', 'building', 'yes (pid 4242)', '1', 'no']
                        and rows['b'][1:6] == ['T-0102', 'queued', 'no', '2', 'no']
                        and rows['b'][6].endswith('/fanout01/b'))
            case('lanes: a live driver, a plan at 50 percent and the dir per lane', lanes_ok())
            control('lanes view', 'collect_fleet', lambda root, env=None: {'lanes': [], 'waves': [], 'unknown': []}, lanes_ok)

            def waves_ok():
                rc, o, _ = call(['render', 'waves', '--no-snapshot'], fl, env_for(fl))
                wl = o.splitlines()
                return (rc == 0 and wl[0] == 'fanout/wave01 | 2 tickets | 30% | ahead of main 1 | merged no'
                        and '  T-0101 | lane a | building | 10%' in wl and '  T-0102 | lane b | queued | 50%' in wl
                        and 'fanout/wave02 | 1 tickets | 100% | ahead of main 0 | merged yes' in wl and '  T-0201 | lane c | closed | 100%' in wl)
            case('waves: one running wave and one merged and closed wave with tickets and percent', waves_ok())
            control('waves view', 'collect_fleet', lambda root, env=None: {'lanes': [], 'waves': [], 'unknown': []}, waves_ok)
            rc, o_j, _ = call(['render', 'lanes', '--format', 'json', '--no-snapshot'], fl, env_for(fl))
            got = {l['branch'] for l in json.loads(o_j)['lanes']}
            listed = {b.strip().lstrip('*+ ') for b in subprocess.run(['git', '-C', str(fl), 'branch', '--list', 'fanout/*'], capture_output=True, text=True).stdout.splitlines()}
            case('the lanes agree with git branch --list fanout/*', rc == 0 and got == listed and len(listed) == 4)
            RUNNER = lambda cmd, cwd, timeout=15: None if cmd[1].endswith('lanes.py') else fleet_runner(cmd, cwd, timeout)
            rc, o_u, _ = call(['render', 'lanes', 'waves', '--no-snapshot'], fl, env_for(fl))
            case('an unreadable lanes.py marks both views unknown', rc == 0 and o_u.count('unknown (lanes.py list gave no rows)') == 2)
        finally:
            RUNNER = _fake_runner
    finally:
        RUNNER = saved_runner
        tmp.cleanup()
    if failures:
        print('report.py selftest: %d failed: %s' % (len(failures), ', '.join(failures)))
        return 1
    print('report.py selftest: all cases passed')
    return 0


VIEWS_HEAD = tuple(v + ':' for v in VIEWS)

if __name__ == '__main__':
    sys.exit(main())
