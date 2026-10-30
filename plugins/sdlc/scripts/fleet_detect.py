#!/usr/bin/env python3
"""Mechanical waste and stall rules over fleet_collect.py fingerprints. No model call; pure over JSON.

Usage: fleet_detect.py detect <fingerprint.json>...     (`-` or /dev/stdin reads one fingerprint from stdin)
       fleet_detect.py selftest

Prints one JSON object per finding on stdout, one line each, and `fleet_detect: N findings in M fingerprints`
on stderr:
  rule       the rule id (below)
  repo       the fingerprint's `repo`
  scope      "repo" or "machine" (machine state is the same in every repo's fingerprint of one collection run,
             so a report collapses these findings across repos)
  evidence   the fingerprint path that triggered it, e.g. runs.by_ticket["no-barrels"].planner; the stall
             rule names two paths joined with " + ". `evidence_value(fp, evidence)` resolves one.
  value      the measured value at that path
  threshold  the number it was compared with (the newest installed version for plugin_version_stale)
  source     the fingerprint file
  detail     optional: the context a reader needs (ticket, pid, workflow)
Exit codes: 0 ok (findings are not a failure), 2 usage or an unreadable fingerprint (the others still run).

Reads nothing but the fingerprints it is given: no repo, no `ps`, no `gh`, no filesystem scan. A key a rule
needs that is absent or of another type (`runs: "none"`, `ci: "skipped"`, a fingerprint from before the key
existed) makes that rule print nothing, never fail.

Rules (a rule fires when the value is OVER its threshold; thresholds live in THRESHOLDS below):
  planner_results_per_ticket  one finding per ticket folder with more planner runs than the threshold
                              (runs.by_ticket)
  plan_review_share           planner plus plan-reviewer cost over total cost (plan_review_share)
  size_m_criteria             one finding per size L2 handoff (or its 0.21.x alias M) with more acceptance criteria than the threshold
                              (tickets.items)
  hook_cpu                    one finding per hook process over hook_cpu_pct %CPU that has been alive longer than
                              hook_etime_s seconds (processes.hooks.items). One `ps` snapshot cannot show a
                              sustained burn, so this is the lifetime-average CPU of a process older than the
                              limit, which is over 50 percent only if it burned more than half its life.
  chromium_load               Chromium processes (processes.chromium.count), and Chromium resident memory
                              (processes.chromium.rss_mb), each its own finding
  stall_attempts              interrupted attempts plus `.limit` markers (runs.interrupted.count + runs.limit_markers.count),
                              and minutes lost to interrupted attempts (runs.interrupted.lost_min_total), each its own finding
  plugin_version_stale        the plugin version in use (env.plugin.version) is older than the newest installed
                              one (env.plugin.installed[].version); numeric dotted parts only
  ci_push_duplicates          one finding per CI workflow whose push runs in the last 7 days that duplicate a
                              pull_request run of the same head commit (ci.by_workflow[...].push_dup_7d) exceed
                              the threshold
"""
import collections, copy, json, math, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --- thresholds: the one table; each rule compares its measured value with `value > threshold` ----------------
THRESHOLDS = collections.OrderedDict([
    ('planner_results_per_ticket', 5),    # planner runs in one ticket folder (runs.by_ticket[t].planner)
    ('plan_review_share', 0.40),          # (planner + plan-reviewer) cost over total cost, a fraction
    ('size_m_criteria', 20),              # acceptance criteria in one size L2 (alias M) handoff
    ('hook_cpu_pct', 50),                 # one hook process's ps %CPU ...
    ('hook_etime_s', 20),                 # ... while it has been alive longer than this many seconds
    ('chromium_processes', 30),           # Chromium process count
    ('chromium_rss_mb', 6144),            # Chromium resident memory in MB (6 GB, counted as 6144 MB)
    ('stall_attempts', 3),                # interrupted attempts plus .limit markers
    ('stall_lost_min', 120),              # minutes lost to interrupted attempts (runs.interrupted.lost_min_total)
    ('ci_push_dup_runs_7d', 25),          # push runs in 7 days that duplicate a pull_request run of the same sha
])

USAGE = ('usage: fleet_detect.py detect <fingerprint.json>...\n'
         '       fleet_detect.py selftest')


# --- reading a fingerprint ---------------------------------------------------

def num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def dig(d, *keys):
    """d[k1][k2]... or None when any step is absent or not a dict."""
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def key_path(*parts):
    """A fingerprint path from dotted names and index/key parts: ('runs', ('key', 't'), 'planner')."""
    out = ''
    for p in parts:
        if isinstance(p, tuple):
            out += '[%s]' % (json.dumps(p[1]) if p[0] == 'key' else p[1])
        else:
            out += ('.' if out else '') + p
    return out


_TOKEN = re.compile(r'\.([A-Za-z_]\w*)|^([A-Za-z_]\w*)|\[(\d+)\]|\[("(?:[^"\\]|\\.)*")\]')


def _walk(fp, path):
    pos, cur = 0, fp
    while pos < len(path):
        m = _TOKEN.match(path, pos)
        if not m:
            return None
        name, first, idx, quoted = m.groups()
        try:
            if name or first:
                cur = cur[name or first]
            elif idx is not None:
                cur = cur[int(idx)]
            else:
                cur = cur[json.loads(quoted)]
        except (KeyError, IndexError, TypeError):
            return None
        pos = m.end()
    return cur


def evidence_value(fp, path):
    """The value a finding's `evidence` points at; a path joined with " + " is the sum of its parts."""
    parts = [p.strip() for p in path.split(' + ')]
    if len(parts) == 1:
        return _walk(fp, parts[0])
    vals = [num(_walk(fp, p)) for p in parts]
    return None if any(v is None for v in vals) else sum(vals)


def version_tuple(text):
    m = re.match(r'\s*v?(\d+(?:\.\d+)*)', text) if isinstance(text, str) else None
    return tuple(int(x) for x in m.group(1).split('.')) if m else None


def older(a, b):
    """True when version tuple a is older than b (the shorter one is padded with zeros)."""
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)) < b + (0,) * (n - len(b))


# --- rules: each yields (evidence, value, threshold, detail) -----------------

def rule_planner_results_per_ticket(fp):
    limit = THRESHOLDS['planner_results_per_ticket']
    by_ticket = dig(fp, 'runs', 'by_ticket')
    for ticket, roles in (by_ticket.items() if isinstance(by_ticket, dict) else ()):
        n = num(roles.get('planner')) if isinstance(roles, dict) else None
        if n is not None and n > limit:
            yield key_path('runs', 'by_ticket', ('key', ticket), 'planner'), int(n), limit, {'ticket': ticket}


def rule_plan_review_share(fp):
    limit = THRESHOLDS['plan_review_share']
    share = num(fp.get('plan_review_share'))
    if share is not None and share > limit:
        cost = lambda role: num(dig(fp, 'runs', 'by_role', role, 'cost_usd'))
        detail = {k: v for k, v in (('planner_usd', cost('planner')), ('plan_reviewer_usd', cost('plan-reviewer')),
                                    ('total_usd', num(dig(fp, 'runs', 'cost_usd')))) if v is not None}
        yield 'plan_review_share', share, limit, detail


def rule_size_m_criteria(fp):
    limit = THRESHOLDS['size_m_criteria']
    items = dig(fp, 'tickets', 'items')
    for i, it in enumerate(items if isinstance(items, list) else ()):
        n = num(it.get('criteria')) if isinstance(it, dict) else None
        if n is not None and n > limit and str(it.get('size')).upper() in ('L2', 'M'):  # M: the 0.21.x alias of L2
            yield (key_path('tickets', 'items', ('idx', i), 'criteria'), int(n), limit,
                   {'ticket': it.get('ticket'), 'id': it.get('id')})


def rule_hook_cpu(fp):
    cpu_limit, age_limit = THRESHOLDS['hook_cpu_pct'], THRESHOLDS['hook_etime_s']
    items = dig(fp, 'processes', 'hooks', 'items')
    for i, it in enumerate(items if isinstance(items, list) else ()):
        if not isinstance(it, dict):
            continue
        cpu, age = num(it.get('cpu_pct')), num(it.get('etime_s'))
        if cpu is not None and age is not None and cpu > cpu_limit and age > age_limit:
            yield (key_path('processes', 'hooks', 'items', ('idx', i)), cpu, cpu_limit,
                   {'pid': it.get('pid'), 'etime_s': age, 'etime_threshold_s': age_limit,
                    'command': it.get('command')})


def rule_chromium_load(fp):
    count, rss = num(dig(fp, 'processes', 'chromium', 'count')), num(dig(fp, 'processes', 'chromium', 'rss_mb'))
    if count is not None and count > THRESHOLDS['chromium_processes']:
        yield 'processes.chromium.count', int(count), THRESHOLDS['chromium_processes'], {}
    if rss is not None and rss > THRESHOLDS['chromium_rss_mb']:
        yield 'processes.chromium.rss_mb', rss, THRESHOLDS['chromium_rss_mb'], {}


def rule_stall_attempts(fp):
    limit = THRESHOLDS['stall_attempts']
    inter, marks = num(dig(fp, 'runs', 'interrupted', 'count')), num(dig(fp, 'runs', 'limit_markers', 'count'))
    total = (inter or 0) + (marks or 0)
    if (inter is not None or marks is not None) and total > limit:
        yield ('runs.interrupted.count + runs.limit_markers.count', int(total), limit,
               {'interrupted': int(inter or 0), 'limit_markers': int(marks or 0)})
    lost = num(dig(fp, 'runs', 'interrupted', 'lost_min_total'))   # T-0796: two long stalls are under the count line
    if lost is not None and lost > THRESHOLDS['stall_lost_min']:
        yield ('runs.interrupted.lost_min_total', lost, THRESHOLDS['stall_lost_min'], {'interrupted': int(inter or 0)})


def rule_plugin_version_stale(fp):
    plugin = dig(fp, 'env', 'plugin')
    if not isinstance(plugin, dict):
        return
    mine = version_tuple(plugin.get('version'))
    installed = [e for e in (plugin.get('installed') or []) if isinstance(e, dict)
                 and version_tuple(e.get('version')) is not None] if isinstance(plugin.get('installed'), list) else []
    if mine is None or not installed:
        return
    newest = max(installed, key=lambda e: version_tuple(e['version']) + (0,) * 8)
    if older(mine, version_tuple(newest['version'])):
        yield ('env.plugin.version', plugin.get('version'), newest['version'],
               {'path': plugin.get('path'), 'installed_path': newest.get('path')})


def rule_ci_push_duplicates(fp):
    limit = THRESHOLDS['ci_push_dup_runs_7d']
    by = dig(fp, 'ci', 'by_workflow')
    for name, w in (by.items() if isinstance(by, dict) else ()):
        n = num(w.get('push_dup_7d')) if isinstance(w, dict) else None
        if n is not None and n > limit:
            yield (key_path('ci', 'by_workflow', ('key', name), 'push_dup_7d'), int(n), limit,
                   {'workflow': name, 'push_runs_7d': w.get('push_runs_7d'),
                    'pull_request_runs_7d': w.get('pull_request_runs_7d'),
                    'window_days': dig(fp, 'ci', 'window_days')})


# (rule id, scope, function): the order findings print in
RULES = [
    ('planner_results_per_ticket', 'repo', rule_planner_results_per_ticket),
    ('plan_review_share', 'repo', rule_plan_review_share),
    ('size_m_criteria', 'repo', rule_size_m_criteria),
    ('hook_cpu', 'machine', rule_hook_cpu),
    ('chromium_load', 'machine', rule_chromium_load),
    ('stall_attempts', 'repo', rule_stall_attempts),
    ('plugin_version_stale', 'machine', rule_plugin_version_stale),
    ('ci_push_duplicates', 'repo', rule_ci_push_duplicates),
]


def detect(fp, source=None):
    """The findings (dicts) for one fingerprint, in RULES order."""
    if not isinstance(fp, dict):
        return []
    repo = fp.get('repo') if isinstance(fp.get('repo'), str) else (source or 'unknown')
    out = []
    for rule, scope, fn in RULES:
        for evidence, value, threshold, detail in fn(fp):
            f = collections.OrderedDict([('rule', rule), ('repo', repo), ('scope', scope), ('evidence', evidence),
                                         ('value', value), ('threshold', threshold)])
            if source:
                f['source'] = source
            if detail:
                f['detail'] = detail
            out.append(f)
    return out


# --- cli ---------------------------------------------------------------------

def load_fingerprint(path):
    try:
        if path in ('-', '/dev/stdin'):
            return json.load(sys.stdin)
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise ValueError('%s: %s' % (path, e))


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == 'selftest':
        return selftest()
    if argv[0] != 'detect' or len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    findings, read, bad = 0, 0, 0
    for path in argv[1:]:
        try:
            fp = load_fingerprint(path)
        except ValueError as e:
            print('fleet_detect: %s' % e, file=sys.stderr)
            bad += 1
            continue
        if not isinstance(fp, dict):
            print('fleet_detect: %s: not a fingerprint (a JSON object is expected)' % path, file=sys.stderr)
            bad += 1
            continue
        read += 1
        for f in detect(fp, path):
            sys.stdout.write(json.dumps(f) + '\n')
            findings += 1
    print('fleet_detect: %d findings in %d fingerprints' % (findings, read), file=sys.stderr)
    return 2 if bad else 0


# --- selftest ----------------------------------------------------------------

def healthy():
    """A fingerprint with every measure exactly AT its threshold (not over), plus the near misses each rule
    must not flag: a size L ticket with 134 criteria, a hook at 100 percent for exactly 20 seconds, a hook at
    exactly 50 percent for ten minutes."""
    return {
        'repo': '/r/healthy',
        'env': {'plugin': {'version': '0.21.0', 'path': '/p/0.21.0',
                           'installed': [{'key': 'sdlc@x', 'version': '0.21.0', 'path': '/p/0.21.0'},
                                         {'key': 'sdlc@y', 'version': '0.20.9', 'path': '/p/0.20.9'}]}},
        'runs': {'total': 12, 'cost_usd': 100.0,
                 'by_role': {'planner': {'count': 5, 'cost_usd': 25.0}, 'plan-reviewer': {'count': 2, 'cost_usd': 15.0},
                             'builder': {'count': 5, 'cost_usd': 60.0}},
                 'by_ticket': {'t1': {'planner': 5, 'builder': 5}, 't2': {'planner': 2}},
                 'interrupted': {'count': 2, 'attempts': [], 'lost_min_total': 120.0}, 'limit_markers': {'count': 1, 'files': []}},
        'plan_review_share': 0.4,
        'tickets': {'count': 3, 'items': [
            {'ticket': 't1', 'id': 'T-1', 'size': 'M', 'criteria': 20},
            {'ticket': 't2', 'id': 'T-2', 'size': 'M', 'criteria': 9},
            {'ticket': 't3', 'id': 'T-3', 'size': 'L', 'criteria': 134}]},
        'processes': {'chromium': {'count': 30, 'cpu_pct': 10.0, 'rss_mb': 6144.0},
                      'hooks': {'count': 2, 'cpu_pct': 150.0, 'rss_mb': 2.0, 'items': [
                          {'pid': 11, 'cpu_pct': 100.0, 'etime_s': 20, 'command': 'bash block-disk-scan.sh'},
                          {'pid': 12, 'cpu_pct': 50.0, 'etime_s': 600, 'command': 'bash block-stray-worktree.sh'}]},
                      'claude': {'count': 3, 'cpu_pct': 5.0, 'rss_mb': 900.0}},
        'ci': {'since': '2026-09-29', 'window_days': 7, 'runs': 70, 'by_workflow': {
            'CI': {'runs': 70, 'push_runs_7d': 40, 'pull_request_runs_7d': 30, 'push_dup_7d': 25}}},
    }


def selftest():
    misses = []

    def ok(name, cond):
        if cond:
            print('ok: ' + name)
        else:
            misses.append(name)
            print('FAIL: ' + name)

    def put(fp, path, value):
        cur = fp
        for step in path[:-1]:
            cur = cur[step]
        cur[path[-1]] = value
        return fp

    def with_(*edits):
        fp = healthy()
        for path, value in edits:
            put(fp, path, value)
        return fp

    def resolves(fp, f):
        val = evidence_value(fp, f['evidence'])
        return (val.get('cpu_pct') if isinstance(val, dict) else val) == f['value']

    base = healthy()
    ok('baseline: every measure at its threshold yields no finding', detect(base) == [])

    # (rule, threshold key, positive fingerprint, evidence, value, threshold). The negative of each is the
    # baseline itself: that measure sits exactly at the threshold, which is not over it.
    cases = [
        ('planner_results_per_ticket', 'planner_results_per_ticket',
         with_((('runs', 'by_ticket', 't1', 'planner'), 6)), 'runs.by_ticket["t1"].planner', 6, 5),
        ('plan_review_share', 'plan_review_share',
         with_((('plan_review_share',), 0.41)), 'plan_review_share', 0.41, 0.40),
        ('size_m_criteria', 'size_m_criteria',
         with_((('tickets', 'items', 0, 'criteria'), 21)), 'tickets.items[0].criteria', 21, 20),
        ('hook_cpu', 'hook_cpu_pct',
         with_((('processes', 'hooks', 'items', 1, 'cpu_pct'), 50.1)), 'processes.hooks.items[1]', 50.1, 50),
        ('hook_cpu', 'hook_etime_s',
         with_((('processes', 'hooks', 'items', 0, 'etime_s'), 21)), 'processes.hooks.items[0]', 100.0, 50),
        ('chromium_load', 'chromium_processes',
         with_((('processes', 'chromium', 'count'), 31)), 'processes.chromium.count', 31, 30),
        ('chromium_load', 'chromium_rss_mb',
         with_((('processes', 'chromium', 'rss_mb'), 6144.1)), 'processes.chromium.rss_mb', 6144.1, 6144),
        ('stall_attempts', 'stall_attempts',
         with_((('runs', 'interrupted', 'count'), 3)),
         'runs.interrupted.count + runs.limit_markers.count', 4, 3),
        ('stall_attempts', 'stall_lost_min',
         with_((('runs', 'interrupted', 'lost_min_total'), 1345.1)), 'runs.interrupted.lost_min_total', 1345.1, 120),
        ('plugin_version_stale', None,
         with_((('env', 'plugin', 'version'), '0.20.11')), 'env.plugin.version', '0.20.11', '0.21.0'),
        ('ci_push_duplicates', 'ci_push_dup_runs_7d',
         with_((('ci', 'by_workflow', 'CI', 'push_dup_7d'), 26)), 'ci.by_workflow["CI"].push_dup_7d', 26, 25),
    ]
    for rule, key, fp, evidence, value, threshold in cases:
        found = detect(fp)
        label = '%s (%s)' % (rule, evidence)
        ok('positive: %s fires once and nothing else does' % label, len(found) == 1 and found[0]['rule'] == rule)
        f = found[0] if found else {}
        ok('positive: %s names its evidence, value and threshold' % label,
           f.get('evidence') == evidence and f.get('value') == value and f.get('threshold') == threshold
           and f.get('repo') == '/r/healthy')
        ok('positive: %s evidence path resolves to the measured value in the fingerprint' % label,
           f != {} and resolves(fp, f))
        if key:        # negative control: the threshold table is the only source of the number
            saved = THRESHOLDS[key]
            THRESHOLDS[key] = saved * 1000
            ok('negative control: raising %s in the table silences %s' % (key, rule), detect(fp) == [])
            THRESHOLDS[key] = saved

    # negatives just under the threshold, one per rule, each on its own (baseline is the all-at-threshold case)
    just_under = [
        ('planner_results_per_ticket', with_((('runs', 'by_ticket', 't1', 'planner'), 5))),
        ('plan_review_share', with_((('plan_review_share',), 0.4))),
        ('size_m_criteria', with_((('tickets', 'items', 0, 'criteria'), 20))),
        ('size_m_criteria: only size M counts', with_((('tickets', 'items', 2, 'criteria'), 500))),
        ('hook_cpu: not over the CPU line', with_((('processes', 'hooks', 'items', 1, 'etime_s'), 5000))),
        ('hook_cpu: not older than the age line', with_((('processes', 'hooks', 'items', 0, 'cpu_pct'), 400.0))),
        ('chromium_load: 30 processes', with_((('processes', 'chromium', 'count'), 30))),
        ('chromium_load: 6144 MB', with_((('processes', 'chromium', 'rss_mb'), 6144.0))),
        ('stall_attempts: 3 in total', with_((('runs', 'interrupted', 'count'), 2), (('runs', 'limit_markers', 'count'), 1))),
        ('stall_attempts: 120 minutes lost', with_((('runs', 'interrupted', 'lost_min_total'), 120))),
        ('plugin_version_stale: in use is the newest', with_((('env', 'plugin', 'version'), '0.21.0'))),
        ('plugin_version_stale: 0.21 equals 0.21.0', with_((('env', 'plugin', 'version'), '0.21'))),
        ('plugin_version_stale: newer than installed', with_((('env', 'plugin', 'version'), '0.22.1'))),
        ('ci_push_duplicates: 25 duplicates', with_((('ci', 'by_workflow', 'CI', 'push_dup_7d'), 25))),
        ('ci_push_duplicates: many push runs, none duplicated',
         with_((('ci', 'by_workflow', 'CI', 'push_runs_7d'), 400), (('ci', 'by_workflow', 'CI', 'push_dup_7d'), 0))),
    ]
    for label, fp in just_under:
        ok('negative: %s yields no finding' % label, detect(fp) == [])
    ok('plugin_version_stale: 0.9.0 is older than 0.10.0 (numeric, not text, order)', [f['rule'] for f in detect(
        with_((('env', 'plugin', 'version'), '0.9.0'), (('env', 'plugin', 'installed'),
                                                         [{'version': '0.10.0', 'path': '/p'}])))] == ['plugin_version_stale'])
    ok('size_m_criteria: a lowercase size m counts', [f['rule'] for f in detect(
        with_((('tickets', 'items', 2, 'size'), 'm'), (('tickets', 'items', 2, 'criteria'), 21)))] == ['size_m_criteria'])
    ok('size_m_criteria: a size L2 counts like its alias M', [f['rule'] for f in detect(
        with_((('tickets', 'items', 2, 'size'), 'L2'), (('tickets', 'items', 2, 'criteria'), 21)))] == ['size_m_criteria'])
    ok('size_m_criteria: a size L3 does not count', detect(
        with_((('tickets', 'items', 2, 'size'), 'L3'), (('tickets', 'items', 2, 'criteria'), 500))) == [])

    # a ticket key with a slash (ticket_root: tickets) round-trips through the evidence path
    nested = with_((('runs', 'by_ticket', 'tickets/0001-a'), {'planner': 6}))
    got = detect(nested)
    ok('evidence: a ticket key with a slash is quoted and resolves', len(got) == 1
       and got[0]['evidence'] == 'runs.by_ticket["tickets/0001-a"].planner' and resolves(nested, got[0]))

    # a fingerprint that trips several rules prints each, in RULES order, with scope
    many = with_((('runs', 'by_ticket', 't1', 'planner'), 12), (('plan_review_share',), 0.55),
                 (('processes', 'chromium', 'count'), 53), (('processes', 'chromium', 'rss_mb'), 10240.0))
    got = [(f['rule'], f['scope']) for f in detect(many)]
    ok('several rules: every finding prints, in table order, with its scope', got == [
        ('planner_results_per_ticket', 'repo'), ('plan_review_share', 'repo'), ('chromium_load', 'machine'),
        ('chromium_load', 'machine')])

    # robustness: absent keys, other types, and an old-shape fingerprint never fail
    shapes = [
        {}, {'repo': '/r/a'}, {'repo': '/r/none', 'runs': 'none', 'plan_review_share': None, 'ci': 'skipped'},
        {'repo': '/r/old', 'runs': {'total': 3, 'cost_usd': 0.0, 'by_role': {}, 'interrupted': {'count': 0},
                                    'limit_markers': {'count': 0}}, 'processes': {'chromium': {'count': 2, 'cpu_pct': 1}},
         'ci': {'by_workflow': {'CI': {'runs': 5}}}},
        {'repo': 3, 'runs': [], 'tickets': 'x', 'processes': [], 'env': 5, 'ci': {'by_workflow': []}},
        {'repo': '/r/junk', 'runs': {'by_ticket': {'t': 'x', 'u': {'planner': 'many'}}, 'interrupted': 'no',
                                     'limit_markers': {'count': 'a'}},
         'tickets': {'items': [None, 5, {}, {'size': 'M', 'criteria': 'lots'}]},
         'processes': {'hooks': {'items': [None, {'cpu_pct': 99}, {'cpu_pct': 'x', 'etime_s': 99}]},
                       'chromium': {'count': True, 'rss_mb': float('nan')}},
         'env': {'plugin': {'version': 7, 'installed': 'x'}}, 'plan_review_share': 'high'},
        {'repo': '/r/v', 'env': {'plugin': {'version': 'dev', 'installed': [{'version': 'dev'}, None]}}},
        [], 'text', None,
    ]
    crashed = []
    for s in shapes:
        try:
            if detect(s) != []:
                crashed.append('findings on %r' % (s,))
        except Exception as e:
            crashed.append('%s on %r' % (type(e).__name__, s))
    ok('robustness: absent or mistyped keys give no finding and no traceback', not crashed)
    if crashed:
        print('  ' + '; '.join(crashed))

    # the known 2026-10-06 findings. The agent-ui and maison values are the measured numbers in their
    # root-cause reports (193 runs and $787, planner $250 and plan-reviewer $186, three hooks at about 100
    # percent CPU for 30+ s; 53 Chromium processes holding about 10 GB). Its "12 planner results for no-barrels"
    # is not reproduced: the folder holds 6 planner results and the collector counts 6, so the fixture says 6.
    # The gen-ui-kit report is not on this machine, so its fixture encodes only the finding the ticket names,
    # at the lowest count over the threshold. maison's size M ticket (T-0137, 9 criteria) is not over 20.
    agent_ui = {'repo': '/Users/kimgranlund/Projects/nonoun/agent-ui', 'runs': {
        'total': 193, 'cost_usd': 787.0,
        'by_role': {'planner': {'count': 37, 'cost_usd': 250.0}, 'plan-reviewer': {'count': 25, 'cost_usd': 186.0},
                    'builder': {'count': 53, 'cost_usd': 181.0}, 'architect': {'count': 9, 'cost_usd': 101.0},
                    'verifier': {'count': 47, 'cost_usd': 59.0}, 'filer': {'count': 16, 'cost_usd': 5.0},
                    'solo': {'count': 4, 'cost_usd': 4.4}},
        'by_ticket': {'no-barrels': {'planner': 6, 'plan-reviewer': 5}},
        'interrupted': {'count': 0}, 'limit_markers': {'count': 1}},
        'plan_review_share': round((250.0 + 186.0) / 787.0, 4),
        'processes': {'chromium': {'count': 4, 'cpu_pct': 2.0, 'rss_mb': 300.0},
                      'hooks': {'count': 3, 'cpu_pct': 300.0, 'rss_mb': 3.0, 'items': [
                          {'pid': 49913 + i, 'cpu_pct': 100.0, 'etime_s': 31 + i, 'command': 'bash block-%s.sh' % n}
                          for i, n in enumerate(('pattern-kill', 'stray-worktree', 'disk-scan'))]}}}
    maison = {'repo': '/Users/kimgranlund/Projects/maison/ui-kit-maison', 'runs': {
        'total': 40, 'cost_usd': 60.0, 'by_ticket': {'T-0137': {'solo': 1}}, 'interrupted': {'count': 0},
        'limit_markers': {'count': 0}},
        'tickets': {'count': 1, 'items': [{'ticket': '0137-chart', 'id': 'T-0137', 'size': 'M', 'criteria': 9}]},
        'processes': {'chromium': {'count': 53, 'cpu_pct': 180.0, 'rss_mb': 10240.0}}}
    gen_ui_kit = {'repo': '/Users/kimgranlund/Projects/nonoun/gen-ui-kit',
                  'processes': {'chromium': {'count': 31, 'cpu_pct': 150.0, 'rss_mb': 4096.0}}}
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, fp in (('agent-ui', agent_ui), ('maison', maison), ('gen-ui-kit', gen_ui_kit),
                         ('healthy', healthy())):
            p = os.path.join(tmp, name + '.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(fp, f)
            paths.append(p)
        me = os.path.abspath(__file__)

        def cli(*args, stdin=None):
            p = subprocess.run([sys.executable, me] + list(args), input=stdin, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
            return p.returncode, p.stdout, p.stderr

        rc, out, err = cli('detect', *paths)
        lines = [json.loads(l) for l in out.splitlines()]
        have = {(os.path.basename(f['repo']), f['rule'], f['evidence']) for f in lines}
        ok('cli: detect prints one JSON object per line and exits 0 with findings', rc == 0 and len(lines) == len(
            out.splitlines()) and err.startswith('fleet_detect: %d findings in 4 fingerprints' % len(lines)))
        ok('known finding: agent-ui plan-review share is over 40 percent',
           ('agent-ui', 'plan_review_share', 'plan_review_share') in have
           and [f['value'] for f in lines if f['rule'] == 'plan_review_share'] == [0.554])
        ok('known finding: agent-ui planner results over 5 on one ticket and three runaway hooks',
           ('agent-ui', 'planner_results_per_ticket', 'runs.by_ticket["no-barrels"].planner') in have
           and sum(1 for f in lines if f['rule'] == 'hook_cpu') == 3)
        ok('known finding: maison Chromium is over the process and the memory threshold',
           ('ui-kit-maison', 'chromium_load', 'processes.chromium.count') in have
           and ('ui-kit-maison', 'chromium_load', 'processes.chromium.rss_mb') in have)
        ok('known finding: gen-ui-kit Chromium is over the process threshold',
           ('gen-ui-kit', 'chromium_load', 'processes.chromium.count') in have)
        ok('known findings: nothing is reported for maison size M (9 criteria) or for the healthy fingerprint',
           not any(f['rule'] == 'size_m_criteria' for f in lines) and not any(
               os.path.basename(f['repo']) == 'healthy' for f in lines))
        ok('cli: every finding carries rule, repo, scope, evidence, value, threshold and source', all(
            all(k in f for k in ('rule', 'repo', 'scope', 'evidence', 'value', 'threshold', 'source')) for f in lines))
        rc, out, err = cli('detect', paths[3])
        ok('cli: no findings still exits 0 and says so', rc == 0 and out == '' and err.startswith('fleet_detect: 0 findings'))
        rc, out, err = cli('detect', '-', stdin=json.dumps(agent_ui))
        ok('cli: a fingerprint on stdin (-) is read', rc == 0 and 'plan_review_share' in out)
        bad = os.path.join(tmp, 'bad.json')
        with open(bad, 'w', encoding='utf-8') as f:
            f.write('{not json')
        rc, out, err = cli('detect', bad, paths[1])
        ok('cli: an unreadable fingerprint exits 2 and the others still run', rc == 2 and 'chromium_load' in out
           and 'bad.json' in err)
        rc, out, err = cli('detect', os.path.join(tmp, 'missing.json'))
        ok('cli: a missing file exits 2', rc == 2)
        arr = os.path.join(tmp, 'arr.json')
        with open(arr, 'w', encoding='utf-8') as f:
            f.write('[]')
        rc, out, err = cli('detect', arr)
        ok('cli: a JSON value that is not an object exits 2', rc == 2 and out == '')
        ok('cli: no arguments exit 2', cli()[0] == 2 and cli('detect')[0] == 2 and cli('nope')[0] == 2)
        before = sorted(os.listdir(tmp))
        cli('detect', *paths)
        ok('read-only: detect writes nothing', sorted(os.listdir(tmp)) == before)

    if misses:
        print('fleet_detect selftest: %d failed: %s' % (len(misses), '; '.join(misses)), file=sys.stderr)
        return 1
    print('fleet_detect selftest: ok')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
