#!/usr/bin/env python3
"""Turn one repo's run records and the machine state into one JSON fingerprint. No model call, read-only.

Usage: fleet_collect.py collect <repo> [--since DATE] [--until DATE] [--gh] [--days N] [--du-timeout SEC] > out.json
       fleet_collect.py selftest

Prints one JSON object on stdout and a `runs: ...` line on stderr. Keys:
  repo, summary, window {since, until}
  env             plugin {version, path, installed[]} (the plugin this script runs from, plus the sdlc-lite
                  entries of ~/.claude/plugins/installed_plugins.json), claude version, time (UTC),
                  uptime_load {uptime_s, load1, load5, load15, cpus}
  runs            the string "none" when no `.sdlc` exists under the repo or any of its worktrees; else
                  total, cost_usd, duration_s, unmetered (null cost_usd or unpriced true), by_role {role: count, cost_usd,
                  duration_s}, by_lane {solo, full}, by_ticket {ticket folder: {role: count}}, interrupted
                  {count, attempts[] {attempt_id, role, level, started_at, lost_min, path}, lost_min_median,
                  lost_min_total}, orphaned {count, attempts[] {attempt_id, role, level, started_at, path}},
                  limit_markers {count, files[]}, lane_overrides[], duplicates_dropped, sources
  results         {builder: {total, blocked}}: builder rows of runs.jsonl in the window (deduplicated as `runs` is);
                  blocked counts those whose result file (the row's `file`, beside its runs.jsonl) has a `## Status`
                  section whose first non-blank line starts with the word `blocked`
  plan_defects    {late, early}: late counts builder and verifier rows whose result file holds a line starting
                  `plan defect:` (after an optional list marker); early counts the lines of each scanned
                  `handoff.md` `## Plan review` section that match `- <YYYY-MM-DD> plan defect at split: ` with
                  that date (as <date>T00:00:00Z) in the window, deduplicated by (handoff path, line), plus the
                  lines of legacy `refusals.jsonl` files with a `ts` in the window, deduplicated by (plan, text)
  attempts        {by_role: {role: {count, median_min, max_min}}, over_budget: {count, attempts[] {attempt_id, role,
                  level, wall_min, budget_min, path}}}: completed `*.attempt.json` records in the window, minutes
                  from started_at to finished_at; over_budget lists those whose wall time reached their budget
                  (dispatch.over_budget: the record's time_budget_min, else the role's ROLE_MINUTES) (T-0811)
  plan_review_share   (plan-reviewer + planner cost_usd) / total cost_usd, null with no cost
  tickets         {count, items[]}: each `.sdlc/<folder>/handoff.md` (main checkout first, then worktrees; the first
                  copy of a folder wins) is counted. A ticket folder is keyed by its path under `.sdlc`: its name,
                  or `tickets/<name>` when any checkout's `.sdlc/config` sets `ticket_root: tickets` (the same key
                  as in `runs.by_ticket`). With a `work_root: <path>` line (roots.py) the folders under
                  `<checkout>/<path>` are read too, keyed by their path under it: the flat layout's key. items lists those with an `## Acceptance criteria` section as {ticket, id,
                  size, criteria} (criteria = top-level list lines in that section). Not windowed.
  processes       chromium, hooks, claude: {count, cpu_pct, rss_mb} from one `ps` snapshot; hooks also carries
                  items[] {pid, cpu_pct, etime_s, command} (capped, busiest first)
  worktrees       linked worktrees: count, size (a "<n> MB" string, or "unknown" when any `du` timed out),
                  size_kb_known, items[] {path, size}
  ci              "skipped" without --gh; with --gh runs, wall_minutes, failed, by_workflow from `gh api`
                  (run wall time is updated_at minus run_started_at), or {"error": ...}. Each workflow also
                  carries by_event {event: runs}, and over the last 7 days (`window_days` of the fetch, at most
                  7 are counted) push_runs_7d, pull_request_runs_7d, and push_dup_7d (push runs whose head_sha
                  also has a pull_request run of the same workflow).

Runs. Every `.sdlc/**/runs.jsonl` under the repo and each worktree (`git worktree list`, plus each folder
under the worktree root and the legacy roots, wtroot.py) is read and deduplicated by attempt_id (a row with none is deduplicated on its
whole line), the way budget.py dedupes. A worktree's `.sdlc` carries the ticket's runs, so the totals cover
the repo's whole history, not one checkout. A record under `.sdlc/runtime/tasks/<key>/` (the records dir,
order.py) belongs to its task folder (order.task_dir, else `<work_root>/<key>` or `<work_root>/.<key>`), keyed by
that folder's path under `.sdlc` (`.0001-a`, `tickets/0001-a`) or under the work root (`.0001-a`, the same key as
the flat layout), else by `<key>` when no task folder exists. The work root's runs, skips and handoffs are scanned
like `.sdlc`'s. The lane of a run is the effective lane of the
nearest ancestor `skips.md`, searched from the task folder for a records-dir record: the last `Lane: <lane> ...`
prose line (a conductor override) wins over the last `- lane: <lane>;` line under `## Lane` (the steps.py
record). With no skips.md the lane is read from the task folder handoff's `## Outcome` header (`lane: solo|full|fix`
on its first non-blank line). `lean` and `fix` count as `full`; role `solo` is always `solo`; with neither the
lane is `full` unless the role is solo. interrupted counts `*.attempt.json` files whose status is `interrupted`,
deduplicated by attempt_id; one whose result file (<stem>.md beside <stem>.attempt.json) already holds a verdict
is not counted (T-0445). lost_min of an interrupted attempt is the minutes from its started_at to the started_at
of the next attempt record of the same role in the same directory, else to its own finished_at (null with neither);
the median and total skip a null. orphaned counts attempt records still `running` that started in the window and that
dispatch.attempt_state_at calls orphaned now (the same call `dispatch.py status` makes: a claude-backend attempt
whose parent_pid, else owner_pid, is dead or reused, or any running attempt whose ticket is done or dropped, T-0809),
deduplicated by attempt_id. limit_markers counts `*.limit` files (run.sh's 429 resume markers).
--since keeps records at or after DATE; --until keeps records up to DATE (a bare YYYY-MM-DD includes that whole
day, a full ISO instant is an inclusive bound). A record with no readable timestamp is dropped when a bound is
given. DATE is YYYY-MM-DD or ISO 8601; no zone means UTC.

Read-only: nothing under the repo is written. Only `ps`, `du -sk`, `git worktree list`, `claude --version`, and
(with --gh) `gh api` GET calls run, each bounded by a timeout and killed with its process group on expiry.
Exit codes: 0 ok (a repo with no `.sdlc` included), 2 usage or a missing repo.
"""
import collections, datetime, json, math, os, re, shutil, signal, statistics, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dispatch  # noqa: E402
import order  # noqa: E402
import results  # noqa: E402
import roots as sdlc_roots  # noqa: E402  (`roots` names the checkout list below)
import wtroot  # noqa: E402
PLUGIN_ROOT = os.path.dirname(HERE)
UTC = datetime.timezone.utc

DU_CMD = 'du'
DU_TIMEOUT = 10.0        # seconds per worktree
DU_TOTAL = 30.0          # seconds across all worktrees; later ones are `unknown` without a du
PS_CMD = 'ps'
GH_CMD = 'gh'
GH_TIMEOUT = 120.0
CLAUDE_CMD = 'claude'
PROBE_TIMEOUT = 10.0
SKIP_DIRS = {'node_modules', '.git'}
LIST_CAP = 50

USAGE = ('usage: fleet_collect.py collect <repo> [--since DATE] [--until DATE] [--gh] [--days N] [--du-timeout SEC]\n'
         '       fleet_collect.py selftest')


# --- bounded subprocess ------------------------------------------------------

class Ran(object):
    """Outcome of run_bounded: rc is None when the command could not start or timed out."""
    def __init__(self, rc, out='', err='', timed_out=False):
        self.rc, self.out, self.err, self.timed_out = rc, out, err, timed_out

    @property
    def ok(self):
        return self.rc == 0


def run_bounded(cmd, timeout, cwd=None):
    """Run cmd with no stdin; on timeout kill its whole process group and return timed_out."""
    try:
        p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, universal_newlines=True, start_new_session=True)
    except OSError as e:
        return Ran(None, err=str(e))
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            p.kill()
        try:
            p.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        return Ran(None, timed_out=True)
    return Ran(p.returncode, out, err)


# --- time --------------------------------------------------------------------

def parse_ts(s):
    """An aware datetime from an ISO 8601 string (Z, offset, or bare date), else None."""
    if not isinstance(s, str) or not s.strip():
        return None
    t = s.strip()
    if t.endswith(('Z', 'z')):
        t = t[:-1] + '+00:00'
    t = re.sub(r'(\.\d{6})\d+', r'\1', t)
    try:
        dt = datetime.datetime.fromisoformat(t)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


class Window(object):
    """since <= ts, and ts <= until (an inclusive instant) or ts < until (a bare date's next midnight)."""
    def __init__(self, since=None, until=None):
        self.since_text, self.until_text = since, until
        self.since = parse_ts(since) if since else None
        self.until, self.until_excl = None, False
        if until:
            u = parse_ts(until)
            if u is not None and re.fullmatch(r'\s*\d{4}-\d{2}-\d{2}\s*', until):
                u, self.until_excl = u + datetime.timedelta(days=1), True
            self.until = u
        for text, val in ((since, self.since), (until, self.until)):
            if text and val is None:
                raise ValueError('not a date: %r (use YYYY-MM-DD or ISO 8601)' % text)

    @property
    def active(self):
        return self.since is not None or self.until is not None

    def has(self, ts):
        """True when ts (a string) is inside the window; with no bounds always True."""
        if not self.active:
            return True
        dt = parse_ts(ts)
        if dt is None:
            return False
        if self.since is not None and dt < self.since:
            return False
        if self.until is not None and (dt >= self.until if self.until_excl else dt > self.until):
            return False
        return True


# --- roots and scanning ------------------------------------------------------

def parse_worktree_porcelain(text):
    """Paths from `git worktree list --porcelain`, main worktree first."""
    return [line[len('worktree '):].strip() for line in text.splitlines() if line.startswith('worktree ')]


def lane_roots(repo):
    """The worktree root of repo, then its legacy roots (wtroot.py, T-0575); outside git, the same folders by
    wtroot's default rule for repo as the main checkout."""
    r = wtroot.root(repo)
    found = ([r] + wtroot.legacy_roots(repo)) if r else [
        wtroot.default_root(repo), os.path.join(repo, *wtroot.CLAUDE), os.path.join(repo, wtroot.LEGACY)]
    return [str(p) for p in found]


def worktree_roots(repo):
    """(main-first list of every checkout root, list of linked worktree roots), by realpath.

    Linked = registered with git (not the first entry) or a directory directly under a worktree root of the repo
    (wtroot.py root, then the legacy roots; outside git, the same folders by wtroot's default rule), which covers a
    non-git repo and fanout lane dirs git forgot."""
    repo = os.path.realpath(repo)
    listed = []
    r = run_bounded(['git', '-C', repo, 'worktree', 'list', '--porcelain'], PROBE_TIMEOUT)
    if r.ok:
        listed = [os.path.realpath(p) for p in parse_worktree_porcelain(r.out)]
    linked = [p for p in listed[1:] if p != repo]
    for base in lane_roots(repo):
        try:
            names = sorted(os.listdir(base))
        except OSError:
            continue
        for n in names:
            p = os.path.realpath(os.path.join(base, n))
            if os.path.isdir(p) and p != repo and p not in linked:
                linked.append(p)
    roots = [repo] + [p for p in linked if p != repo]
    return roots, linked


def scan_sdlc(roots, rel=None):
    """(runs files, attempt files, limit files, skips files, refusals files, handoff files) under each root's
    `.sdlc`, then its work root `<root>/<rel>` (rel: the repo's work_root value), in root order. Each file is
    paired with its checkout's `.sdlc`."""
    runs, attempts, limits, skips, refusals, handoffs = [], [], [], [], [], []
    seen_dirs = set()
    for root in roots:
        sd = os.path.join(root, '.sdlc')
        if not os.path.isdir(sd) or os.path.realpath(sd) in seen_dirs:
            continue
        seen_dirs.add(os.path.realpath(sd))
        tops = [t for t in (sd, work_dir(sd, rel)) if t and os.path.isdir(t)]
        for cur, dirs, files in (w for t in tops for w in os.walk(t)):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for n in sorted(files):
                p = os.path.join(cur, n)
                if n == 'runs.jsonl':
                    runs.append((sd, p))
                elif n.endswith('.attempt.json'):
                    attempts.append((sd, p))
                elif n.endswith('.limit'):
                    limits.append((sd, p))
                elif n == 'skips.md':
                    skips.append((sd, p))
                elif n == 'refusals.jsonl':
                    refusals.append((sd, p))
                elif n == 'handoff.md':
                    handoffs.append((sd, p))
    return runs, attempts, limits, skips, refusals, handoffs


def read_text(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def parse_skips(text):
    """(recorded lane or None, override lane or None, override note) from one skips.md."""
    recorded = override = None
    note = ''
    inside = False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.strip().lower() == '## lane'
            continue
        m = re.match(r'^- lane:\s*([A-Za-z]+)', line)
        if inside and m:
            recorded = m.group(1).lower()
            continue
        m = re.match(r'^Lane:\s*(solo|lean|full)\b(.*)$', line, re.I)
        if m:
            override, note = m.group(1).lower(), (m.group(1) + m.group(2)).strip()[:200]
    return recorded, override, note


OUTCOME_LANE_RE = re.compile(r'lane:\s*(solo|full|fix)\b')


def outcome_lane(text):
    """The lane on the first non-blank line after `## Outcome` in a handoff, else None."""
    inside = False
    for line in text.splitlines():
        if line.startswith('## '):
            if inside:
                return None
            inside = line.strip() == '## Outcome'
            continue
        if inside and line.strip():
            m = OUTCOME_LANE_RE.search(line)
            return m.group(1) if m else None
    return None


def runtime_task(sdlc, d, work=None):
    """(True, task folder or None) when d is under `<sdlc>/runtime/tasks/<key>`, else (False, None). The task
    folder is order.task_dir's, else `<work>/<key>` or `<work>/.<key>` holding a handoff.md (work: the work root)."""
    tasks = os.path.join(sdlc, 'runtime', 'tasks')
    if not d.startswith(tasks + os.sep):
        return False, None
    tf = order.task_dir(d)
    if tf is None and work:
        key = d[len(tasks) + 1:].split(os.sep, 1)[0]
        tf = next((c for c in (os.path.join(work, key), os.path.join(work, '.' + key))
                   if os.path.isfile(os.path.join(c, 'handoff.md'))), None)
    return True, (str(tf) if tf is not None else None)


def under(path, d):
    """True when path is d or below it."""
    return bool(d) and (path == d or path.startswith(d + os.sep))


class Lanes(object):
    """Effective lane per runs.jsonl dir: the nearest ancestor skips.md up to its `.sdlc` (from the task folder
    for a records dir under `runtime/tasks/`), else the task folder handoff's `## Outcome` lane. rel is the repo's
    work_root value: a folder under `<checkout>/<rel>` walks up to that work root and is named relative to it."""
    def __init__(self, rel=None):
        self.rel = rel
        self.cache = {}
        self.outcomes = {}
        self.overrides = {}

    def of_file(self, sdlc, path):
        d = os.path.dirname(path)
        runtime, tf = runtime_task(sdlc, d, work_dir(sdlc, self.rel))
        if runtime:
            if tf is None:
                return None
            d = tf
        lane = self._walk(sdlc, d)
        if lane is None:
            folder = order.task_dir(d)
            if folder is not None:
                folder = str(folder)
                if folder not in self.outcomes:
                    self.outcomes[folder] = outcome_lane(read_text(os.path.join(folder, 'handoff.md')))
                lane = self.outcomes[folder]
        return lane

    def _walk(self, sdlc, d):
        work = work_dir(sdlc, self.rel)
        top = work if under(d, work) else sdlc
        chain = []
        while True:
            if d in self.cache:
                lane = self.cache[d]
                break
            chain.append(d)
            skips = os.path.join(d, 'skips.md')
            if os.path.isfile(skips):
                lane = self._read(top, d, skips)
                break
            if d == top or os.path.dirname(d) == d:
                lane = None
                break
            d = os.path.dirname(d)
        for c in chain:
            self.cache[c] = lane
        return lane

    def _read(self, sdlc, d, skips):
        recorded, override, note = parse_skips(read_text(skips))
        effective = override or recorded
        if override and override != recorded:
            ticket = os.path.relpath(d, sdlc)
            self.overrides.setdefault((ticket, recorded, override, note), {
                'ticket': ticket, 'recorded': recorded, 'effective': override, 'note': note})
        return effective


def num(v):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def nested_tickets(sdlc):
    """True when `<sdlc>/config` has a `ticket_root: tickets` line (roots.parse): the ticket folders then live in
    `<sdlc>/tickets/`, and any other folder under `.sdlc` is a plain task."""
    return any(v == 'tickets' for v, _ in sdlc_roots.parse(read_text(os.path.join(sdlc, 'config'))).ticket_root)


def work_root(sdlc):
    """The work_root value `<sdlc>/config` sets (roots.py), as a path relative to the checkout, else None. A value
    roots.py refuses is None too: the collector never fails on config."""
    text = read_text(os.path.join(sdlc, 'config'))
    if not sdlc_roots.parse(text).work_root:
        return None
    try:
        return os.path.relpath(str(sdlc_roots.resolve(sdlc, text).work), os.path.dirname(sdlc))
    except sdlc_roots.Fail:
        return None


def repo_work(roots):
    """The first work_root value any checkout's `.sdlc/config` sets, else None (the layout is the repo's, as in
    repo_nested)."""
    return next((w for w in (work_root(os.path.join(r, '.sdlc')) for r in roots) if w), None)


def work_dir(sdlc, rel):
    """`<checkout>/<rel>`, the work root of the checkout whose `.sdlc` is sdlc, or None when rel is None."""
    return os.path.join(os.path.dirname(sdlc), rel) if rel else None


def repo_nested(roots):
    """True when any checkout's `.sdlc/config` sets `ticket_root: tickets`. The layout is the repo's, not one
    checkout's: `.sdlc/config` can be untracked, so a lane worktree holding `tickets/<folder>` has no config."""
    return any(nested_tickets(os.path.join(r, '.sdlc')) for r in roots)


def ticket_of(sdlc, path, nested=False, rel=None):
    """The ticket folder a runs.jsonl belongs to, as a path under `.sdlc`: its first component, or
    `tickets/<folder>` with `ticket_root: tickets`. A record under `runtime/tasks/<key>/` belongs to its task
    folder (order.task_dir: `.0001-a`, `tickets/0001-a`), else to `<key>` when no task folder exists. With a
    work_root value rel, a folder under `<checkout>/<rel>` is keyed by its path under that work root, the flat
    layout's key (`0001-a`, `.0001-a`)."""
    work = work_dir(sdlc, rel)
    runtime, tf = runtime_task(sdlc, os.path.dirname(path), work)
    if runtime:
        if tf is not None:
            return os.path.relpath(tf, work if under(tf, work) else sdlc).replace(os.sep, '/')
        tasks = os.path.join(sdlc, 'runtime', 'tasks')
        return os.path.relpath(os.path.dirname(path), tasks).split(os.sep)[0]
    if under(os.path.dirname(path), work):
        return os.path.relpath(os.path.dirname(path), work).split(os.sep)[0]
    rel = os.path.relpath(os.path.dirname(path), sdlc)
    if rel == '.':
        return '.sdlc'
    parts = rel.split(os.sep)
    return '/'.join(parts[:2]) if nested and parts[0] == 'tickets' else parts[0]


def new_bucket():
    return {'count': 0, 'cost_usd': 0.0, 'duration_s': 0.0}


def add_bucket(b, cost, dur):
    b['count'] += 1
    b['cost_usd'] += cost or 0.0
    b['duration_s'] += (dur or 0.0) / 1000.0


def round_bucket(b):
    return {'count': b['count'], 'cost_usd': round(b['cost_usd'], 4), 'duration_s': round(b['duration_s'], 1)}


def minutes_between(start, end):
    """Minutes from ISO string start to end, rounded to 0.1, or None when either is unreadable or end < start."""
    a, b = parse_ts(start), parse_ts(end)
    if a is None or b is None or b < a:
        return None
    return round((b - a).total_seconds() / 60.0, 1)


def median_or_none(vals):
    return round(statistics.median(vals), 1) if vals else None


def result_text(runs_path, rec):
    """The result file a runs.jsonl row names (`file`, beside the runs.jsonl), or ''."""
    name = rec.get('file')
    return read_text(os.path.join(os.path.dirname(runs_path), name)) if isinstance(name, str) and name else ''


STATUS_RE = re.compile(r'^##[ \t]+Status[ \t]*$', re.M)
PLAN_DEFECT_RE = re.compile(r'^[ \t]*(?:(?:[-*+]|\d+[.)])[ \t]+)?plan defect:', re.M)


SPLIT_DEFECT_RE = re.compile(r'^- (\d{4}-\d{2}-\d{2}) plan defect at split: ')


def plan_review_lines(text):
    """The lines of a handoff's `## Plan review` section."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.strip() == '## Plan review'
            continue
        if inside:
            out.append(line)
    return out


def result_blocked(text):
    """True when the line after `## Status` (the next non-blank one) starts with the word `blocked`."""
    m = STATUS_RE.search(text)
    if not m:
        return False
    for line in text[m.end():].splitlines():
        if line.strip():
            w = re.match(r'\W*([A-Za-z]+)', line)
            return bool(w) and w.group(1).lower() == 'blocked'
    return False


def collect_runs(repo, window, dedupe=True, extra=None):
    """The `runs` object (or the string "none") plus the lane overrides' source roots. dedupe=False is the
    negative control: every row counts, so duplicates change the totals. extra, when a dict, receives the keys
    `results`, `plan_defects` and `attempts` that `collect` adds beside `runs`."""
    roots, _linked = worktree_roots(repo)
    rel = repo_work(roots)
    runs_files, attempt_files, limit_files, skips_files, refusal_files, handoff_files = scan_sdlc(roots, rel)
    if not runs_files and not attempt_files and not limit_files and not skips_files:
        return 'none'
    result_rows = []                      # (role, runs.jsonl path, row) of builder and verifier rows in the window
    lanes = Lanes(rel)
    for sdlc, p in skips_files:           # read every skips.md so overrides in runless tickets show too
        lanes.of_file(sdlc, os.path.join(os.path.dirname(p), 'x'))
    seen = set()
    dup = undated = 0
    total = new_bucket()
    unmetered = 0
    by_role, by_lane = collections.OrderedDict(), {'solo': new_bucket(), 'full': new_bucket()}
    by_ticket, nested = {}, repo_nested(roots)
    for sdlc, p in runs_files:
        lane_of = lanes.of_file(sdlc, p)
        ticket = ticket_of(sdlc, p, nested, rel)
        for line in read_text(p).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict):
                continue
            if window.active and parse_ts(rec.get('ts')) is None:
                undated += 1
                continue
            if not window.has(rec.get('ts')):
                continue
            aid = rec.get('attempt_id')
            if dedupe:
                key = ('id', aid) if isinstance(aid, str) and aid else ('raw', line)
                if key in seen:
                    dup += 1
                    continue
                seen.add(key)
            role = rec.get('role') if isinstance(rec.get('role'), str) and rec.get('role') else 'unknown'
            cost, dur = num(rec.get('cost_usd')), num(rec.get('duration_ms'))
            if cost is None or rec.get('unpriced') is True:  # T-0402: the flag dispatch.py record writes counts too
                unmetered += 1
            if role in ('builder', 'verifier'):
                result_rows.append((role, p, rec))
            lane = 'solo' if role == 'solo' or lane_of == 'solo' else 'full'
            add_bucket(total, cost, dur)
            add_bucket(by_role.setdefault(role, new_bucket()), cost, dur)
            add_bucket(by_lane[lane], cost, dur)
            roles = by_ticket.setdefault(ticket, {})
            roles[role] = roles.get(role, 0) + 1
    attempt_recs = []                     # (path, record, dir under .sdlc) of every readable attempt file
    for sdlc, p in attempt_files:
        try:
            with open(p, encoding='utf-8') as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(rec, dict):
            attempt_recs.append((p, rec, os.path.relpath(os.path.dirname(p), sdlc)))
    starts = {}                           # (dir, role) -> sorted started_at instants of every attempt there
    for _p, rec, rel in attempt_recs:
        t = parse_ts(rec.get('started_at'))
        if t is not None:
            starts.setdefault((rel, rec.get('role')), []).append(t)
    for v in starts.values():
        v.sort()

    def lost_min(rec, rel):
        """Minutes from the attempt's start to the next attempt of the same role in the same dir, else to finished_at."""
        t = parse_ts(rec.get('started_at'))
        if t is None:
            return None
        later = [x for x in starts.get((rel, rec.get('role')), ()) if x > t]
        if later:
            return round((later[0] - t).total_seconds() / 60.0, 1)
        return minutes_between(rec.get('started_at'), rec.get('finished_at'))

    settled = {r.get('attempt_id') for _p, r, _rel in attempt_recs
               if r.get('status') != 'running' and isinstance(r.get('attempt_id'), str)}   # another copy moved on
    interrupted, attempts_seen, lost_all = [], set(), []
    orphaned, orphans_seen = [], set()
    done_min, done_seen = {}, set()
    overran = []                          # T-0811: completed attempts whose wall time passed their role's budget
    for p, rec, rel in attempt_recs:
        status = rec.get('status')
        aid = rec.get('attempt_id')
        key = aid if isinstance(aid, str) and aid else p
        if status == 'interrupted':
            if results.attempt_reported(p, rec.get('role')):
                continue                  # T-0445: its result file holds a verdict, so nothing was lost
            if not window.active or window.has(rec.get('started_at') or rec.get('finished_at')):
                if not (dedupe and key in attempts_seen):
                    attempts_seen.add(key)
                    lost = lost_min(rec, rel)
                    if lost is not None:
                        lost_all.append(lost)
                    interrupted.append({'attempt_id': aid if isinstance(aid, str) else None, 'role': rec.get('role'),
                                        'level': rec.get('level'), 'started_at': rec.get('started_at'),
                                        'lost_min': lost, 'path': p})
        elif status == 'running':
            if (window.has(rec.get('started_at')) and aid not in settled
                    and dispatch.attempt_state_at(p, rec) == 'orphaned' and not (dedupe and key in orphans_seen)):
                orphans_seen.add(key)
                orphaned.append({'attempt_id': aid if isinstance(aid, str) else None, 'role': rec.get('role'),
                                 'level': rec.get('level'), 'started_at': rec.get('started_at'), 'path': p})
        elif status == 'completed':
            mins = minutes_between(rec.get('started_at'), rec.get('finished_at'))
            if mins is not None and window.has(rec.get('started_at')) and not (dedupe and key in done_seen):
                done_seen.add(key)
                role = rec.get('role') if isinstance(rec.get('role'), str) and rec.get('role') else 'unknown'
                done_min.setdefault(role, []).append(mins)
                hit = dispatch.over_budget(rec)
                if hit:
                    overran.append({'attempt_id': aid if isinstance(aid, str) else None, 'role': role, 'level': rec.get('level'),
                                    'wall_min': round(mins, 1), 'budget_min': hit[1], 'path': p})
    limits, limits_seen = [], set()
    for sdlc, p in limit_files:
        raw = read_text(p).strip()
        try:
            rec = json.loads(raw.splitlines()[0]) if raw else {}
        except ValueError:
            rec = {}
        rec = rec if isinstance(rec, dict) else {}
        if window.active and not window.has(rec.get('ts')):
            continue
        key = (os.path.basename(p), raw)
        if dedupe:
            if key in limits_seen:
                continue
            limits_seen.add(key)
        limits.append({'file': p, 'role': rec.get('role'), 'level': rec.get('level'), 'ts': rec.get('ts'),
                       'reset': rec.get('reset')})
    if extra is not None:
        built, blocked, late = 0, 0, 0
        for role, rp, row in result_rows:
            text = result_text(rp, row)
            if role == 'builder':
                built += 1
                blocked += result_blocked(text)
            late += bool(PLAN_DEFECT_RE.search(text))
        early, early_seen = 0, set()
        for _sdlc, rp in refusal_files:
            for line in read_text(rp).splitlines():
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(r, dict) or not window.has(r.get('ts')):
                    continue
                key = (r.get('plan'), r.get('text'))
                if dedupe:
                    if key in early_seen:
                        continue
                    early_seen.add(key)
                early += 1
        for _sdlc, hp in handoff_files:
            for line in plan_review_lines(read_text(hp)):
                m = SPLIT_DEFECT_RE.match(line)
                if not m or not window.has(m.group(1) + 'T00:00:00Z'):
                    continue
                key = (hp, line)
                if dedupe:
                    if key in early_seen:
                        continue
                    early_seen.add(key)
                early += 1
        extra['results'] = {'builder': {'total': built, 'blocked': blocked}}
        extra['plan_defects'] = {'late': late, 'early': early}
        extra['attempts'] = {'by_role': {
            role: {'count': len(v), 'median_min': median_or_none(v), 'max_min': max(v)}
            for role, v in sorted(done_min.items())},
            'over_budget': {'count': len(overran), 'attempts': overran[:LIST_CAP]}}
    return {
        'total': total['count'], 'cost_usd': round(total['cost_usd'], 4),
        'duration_s': round(total['duration_s'], 1), 'unmetered': unmetered,
        'by_role': {k: round_bucket(v) for k, v in by_role.items()},
        'by_lane': {k: round_bucket(v) for k, v in by_lane.items()},
        'by_ticket': {t: dict(sorted(r.items())) for t, r in sorted(by_ticket.items())},
        'interrupted': {'count': len(interrupted), 'attempts': interrupted[:LIST_CAP],
                        'lost_min_median': median_or_none(lost_all), 'lost_min_total': round(sum(lost_all), 1)},
        'orphaned': {'count': len(orphaned), 'attempts': orphaned[:LIST_CAP]},
        'limit_markers': {'count': len(limits), 'files': limits[:LIST_CAP]},
        'lane_overrides': sorted(lanes.overrides.values(), key=lambda o: o['ticket']),
        'duplicates_dropped': dup, 'undated_dropped': undated,
        'sources': {'roots': len(roots), 'runs_files': len(runs_files)},
    }


def parse_handoff(text):
    """(id, size, criteria count or None) from one handoff.md. criteria counts the top-level list lines of the
    `## Acceptance criteria` section (fenced blocks skipped); None when the section is absent."""
    tid = size = None
    lines = text.splitlines()
    if lines and lines[0].strip() == '---':
        for line in lines[1:]:
            if line.strip() == '---':
                break
            m = re.match(r'^(id|size):\s*"?([^\s"#]+)', line)
            if m:
                if m.group(1) == 'id':
                    tid = m.group(2)
                else:
                    size = m.group(2).upper()
    criteria, inside, fenced = None, False, False
    for line in lines:
        if line.startswith('## '):
            inside = line.strip().lower() == '## acceptance criteria'
            fenced = False
            if inside:
                criteria = 0
            continue
        if not inside:
            continue
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        if not fenced and re.match(r'^(?:[-*+]|\d+[.)])\s+\S', line):
            criteria += 1
    return tid, size, criteria


def ticket_folders(sdlc, nested, rel=None):
    """(key, dir) for each ticket or task folder under a `.sdlc`: its direct children, and when `nested` the
    folders in `tickets/` keyed `tickets/<folder>`; with a work_root value rel, then the direct children of
    `<checkout>/<rel>` keyed by name."""
    work = work_dir(sdlc, rel)
    extra = [(m, os.path.join(work, m)) for m in sorted(os.listdir(work))] if work and os.path.isdir(work) else []
    try:
        names = sorted(os.listdir(sdlc))
    except OSError:
        return extra
    out = []
    for n in names:
        if n == 'tickets' and nested:
            try:
                inner = sorted(os.listdir(os.path.join(sdlc, n)))
            except OSError:
                inner = []
            out.extend(('tickets/' + m, os.path.join(sdlc, n, m)) for m in inner)
        else:
            out.append((n, os.path.join(sdlc, n)))
    return out + extra


def tickets_info(repo):
    """Every ticket folder that holds a handoff.md, main checkout first; the first copy of a folder wins."""
    roots, _linked = worktree_roots(repo)
    nested, rel = repo_nested(roots), repo_work(roots)
    seen, items = set(), []
    for root in roots:
        for key, d in ticket_folders(os.path.join(root, '.sdlc'), nested, rel):
            h = os.path.join(d, 'handoff.md')
            if key in seen or not os.path.isfile(h):
                continue
            seen.add(key)
            tid, size, criteria = parse_handoff(read_text(h))
            if criteria is not None:
                items.append({'ticket': key, 'id': tid, 'size': size, 'criteria': criteria})
    return {'count': len(seen), 'items': items}


def plan_review_share(runs):
    if not isinstance(runs, dict) or not runs['cost_usd']:
        return None
    plan = sum(runs['by_role'].get(r, {}).get('cost_usd', 0.0) for r in ('planner', 'plan-reviewer'))
    return round(plan / runs['cost_usd'], 4)


# --- machine state -----------------------------------------------------------

def read_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def uptime_seconds():
    try:
        with open('/proc/uptime', encoding='utf-8') as f:
            return int(float(f.read().split()[0]))
    except (OSError, ValueError, IndexError):
        pass
    r = run_bounded(['sysctl', '-n', 'kern.boottime'], PROBE_TIMEOUT)
    m = re.search(r'sec\s*=\s*(\d+)', r.out) if r.ok else None
    return int(time.time()) - int(m.group(1)) if m else None


def env_info():
    manifest = read_json(os.path.join(PLUGIN_ROOT, '.claude-plugin', 'plugin.json')) or {}
    installed = []
    reg = read_json(os.path.expanduser('~/.claude/plugins/installed_plugins.json')) or {}
    for key, entries in sorted((reg.get('plugins') or {}).items()):
        if key.startswith('sdlc-lite@') and isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict):
                    installed.append({'key': key, 'version': e.get('version'), 'path': e.get('installPath'),
                                      'scope': e.get('scope')})
    r = run_bounded([CLAUDE_CMD, '--version'], PROBE_TIMEOUT)
    version = r.out.strip().splitlines()[0] if r.ok and r.out.strip() else 'unknown'
    try:
        load = [round(x, 2) for x in os.getloadavg()]
    except (OSError, AttributeError):
        load = [None, None, None]
    return {
        'plugin': {'version': manifest.get('version', 'unknown'),
                   'path': os.path.realpath(os.environ.get('CLAUDE_PLUGIN_ROOT') or PLUGIN_ROOT),
                   'installed': installed},
        'claude_version': version,
        'time': datetime.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'uptime_load': {'uptime_s': uptime_seconds(), 'load1': load[0], 'load5': load[1], 'load15': load[2],
                        'cpus': os.cpu_count()},
    }


def classify_process(cmd):
    """'claude', 'hooks', 'chromium', or None for one `ps` command line."""
    toks = cmd.split()
    if not toks:
        return None
    first = os.path.basename(toks[0])
    if first in ('claude', 'claude-code') or (first in ('node', 'bun') and len(toks) > 1
                                              and 'claude-code' in toks[1]):
        return 'claude'
    if re.search(r'block-[\w-]+\.sh|/hooks/[\w.-]+\.(sh|py)', ' '.join(toks[:2])):
        return 'hooks'
    exe = cmd.split(' --')[0].rsplit('/', 1)[-1]   # the executable's own name; a path may hold spaces
    if re.match(r'(chrom(e|ium)|google chrome|headless_shell)', exe, re.I):
        return 'chromium'
    return None


def parse_etime(text):
    """Seconds from a ps etime field `[[dd-]hh:]mm:ss`, else None."""
    m = re.fullmatch(r'(?:(\d+)-)?(?:(\d+):)?(\d+):(\d+)', text.strip())
    if not m:
        return None
    d, h, mi, sec = (int(g) if g else 0 for g in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + sec


def parse_ps_line(line):
    """(pid, cpu_pct, etime_s, rss_kb, command) from one `ps -axo pid=,pcpu=,etime=,rss=,command=` line, else None."""
    m = re.match(r'^\s*(\d+)\s+([\d.]+)\s+(\S+)\s+(\d+)\s+(.*)$', line)
    if not m:
        return None
    return int(m.group(1)), float(m.group(2)), parse_etime(m.group(3)), int(m.group(4)), m.group(5)


def process_info():
    out = {k: {'count': 0, 'cpu_pct': 0.0, 'rss_kb': 0} for k in ('chromium', 'hooks', 'claude')}
    hooks = []
    r = run_bounded([PS_CMD, '-axo', 'pid=,pcpu=,etime=,rss=,command='], PROBE_TIMEOUT)
    if not r.ok:
        out['error'] = 'ps unavailable'
        for k in ('chromium', 'hooks', 'claude'):
            out[k]['rss_mb'] = 0.0
            del out[k]['rss_kb']
        out['hooks']['items'] = []
        return out
    me = os.getpid()
    for line in r.out.splitlines():
        parsed = parse_ps_line(line)
        if not parsed or parsed[0] == me:
            continue
        pid, cpu, etime, rss, cmd = parsed
        kind = classify_process(cmd)
        if kind:
            out[kind]['count'] += 1
            out[kind]['cpu_pct'] += cpu
            out[kind]['rss_kb'] += rss
            if kind == 'hooks':
                hooks.append({'pid': pid, 'cpu_pct': cpu, 'etime_s': etime, 'command': cmd[:200]})
    for k in ('chromium', 'hooks', 'claude'):
        out[k]['cpu_pct'] = round(out[k]['cpu_pct'], 1)
        out[k]['rss_mb'] = round(out[k].pop('rss_kb') / 1024.0, 1)
    out['hooks']['items'] = sorted(hooks, key=lambda h: -h['cpu_pct'])[:LIST_CAP]
    return out


def du_kb(path, timeout):
    """Size in KiB, or None when du timed out, failed, or printed nothing parseable."""
    r = run_bounded([DU_CMD, '-sk', path], timeout)
    m = re.match(r'\s*(\d+)', r.out) if r.rc is not None and r.out else None
    return int(m.group(1)) if m else None


def fmt_kb(kb):
    return 'unknown' if kb is None else '%.1f MB' % (kb / 1024.0)


def worktree_info(repo, du_timeout=None):
    du_timeout = DU_TIMEOUT if du_timeout is None else du_timeout
    _roots, linked = worktree_roots(repo)
    items, known, unknown = [], 0, 0
    deadline = time.monotonic() + DU_TOTAL
    for p in linked:
        left = deadline - time.monotonic()
        kb = du_kb(p, min(du_timeout, left)) if os.path.isdir(p) and left > 0 else None
        if kb is None:
            unknown += 1
        else:
            known += kb
        items.append({'path': p, 'size': 'missing' if not os.path.isdir(p) else fmt_kb(kb)})
    return {'count': len(linked), 'size': 'unknown' if unknown else fmt_kb(known), 'size_kb_known': known,
            'items': items[:LIST_CAP]}


CI_RECENT_DAYS = 7      # the push-run counts cover this many days back from `now`


def ci_info(repo, window, days, now=None):
    now = now or datetime.datetime.now(UTC)
    start = window.since or (now - datetime.timedelta(days=days))
    cmd = [GH_CMD, 'api', '-X', 'GET', 'repos/{owner}/{repo}/actions/runs', '-f', 'per_page=100',
           '-f', 'created=>=' + start.strftime('%Y-%m-%d'), '--paginate', '--jq',
           '.workflow_runs[] | {name, event, head_sha, conclusion, run_started_at, updated_at} | @json']
    r = run_bounded(cmd, GH_TIMEOUT, cwd=repo)
    if r.timed_out:
        return {'error': 'gh api timed out'}
    if not r.ok:
        return {'error': (r.err.strip().splitlines() or ['gh failed'])[0][:200]}
    by, total, failed, wall = {}, 0, 0, 0.0
    recent_from = now - datetime.timedelta(days=CI_RECENT_DAYS)
    pr_shas, pushes, pr_recent = {}, {}, {}
    for line in r.out.splitlines():
        try:
            run = json.loads(line)
        except ValueError:
            continue
        if not isinstance(run, dict):
            continue
        a, b = parse_ts(run.get('run_started_at')), parse_ts(run.get('updated_at'))
        mins = max((b - a).total_seconds() / 60.0, 0.0) if a and b else 0.0
        name = run.get('name') or 'unknown'
        w = by.setdefault(name, {'runs': 0, 'wall_minutes': 0.0, 'failed': 0, 'by_event': {}})
        w['runs'] += 1
        w['wall_minutes'] += mins
        event = run.get('event') if isinstance(run.get('event'), str) else 'unknown'
        w['by_event'][event] = w['by_event'].get(event, 0) + 1
        sha = run.get('head_sha') if isinstance(run.get('head_sha'), str) else None
        if event == 'pull_request' and sha:
            pr_shas.setdefault(name, set()).add(sha)
        if a and a >= recent_from:
            if event == 'push':
                pushes.setdefault(name, []).append(sha)
            elif event == 'pull_request':
                pr_recent[name] = pr_recent.get(name, 0) + 1
        if run.get('conclusion') == 'failure':
            w['failed'] += 1
            failed += 1
        total += 1
        wall += mins
    out = {}
    for k, v in sorted(by.items()):
        shas = pushes.get(k, [])
        out[k] = {'runs': v['runs'], 'wall_minutes': round(v['wall_minutes'], 1), 'failed': v['failed'],
                  'by_event': dict(sorted(v['by_event'].items())),
                  'push_runs_7d': len(shas), 'pull_request_runs_7d': pr_recent.get(k, 0),
                  'push_dup_7d': sum(1 for h in shas if h and h in pr_shas.get(k, ()))}
    return {'since': start.strftime('%Y-%m-%d'),
            'window_days': min(CI_RECENT_DAYS, max(0, int((now - start).total_seconds() // 86400))),
            'runs': total, 'wall_minutes': round(wall, 1), 'failed': failed, 'by_workflow': out}


def summary_line(runs):
    if runs == 'none':
        return 'runs: none'
    return 'runs: %d deduped, $%.2f, %d interrupted, %d limit markers' % (
        runs['total'], runs['cost_usd'], runs['interrupted']['count'], runs['limit_markers']['count'])


def collect(repo, since=None, until=None, gh=False, days=14, du_timeout=None, dedupe=True):
    window = Window(since, until)
    extra = {}
    runs = collect_runs(repo, window, dedupe=dedupe, extra=extra)
    return collections.OrderedDict([
        ('repo', os.path.realpath(repo)),
        ('summary', summary_line(runs)),
        ('window', {'since': since, 'until': until}),
        ('env', env_info()),
        ('runs', runs),
        ('plan_review_share', plan_review_share(runs)),
        ('results', extra.get('results', {'builder': {'total': 0, 'blocked': 0}})),
        ('plan_defects', extra.get('plan_defects', {'late': 0, 'early': 0})),
        ('attempts', extra.get('attempts', {'by_role': {}, 'over_budget': {'count': 0, 'attempts': []}})),
        ('tickets', tickets_info(repo)),
        ('processes', process_info()),
        ('worktrees', worktree_info(repo, du_timeout)),
        ('ci', ci_info(os.path.realpath(repo), window, days) if gh else 'skipped'),
    ])


# --- cli ---------------------------------------------------------------------

def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == 'selftest':
        return selftest()
    if argv[0] != 'collect' or len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    repo, since, until, gh, days, du_timeout = None, None, None, False, 14, None
    rest, i = argv[1:], 0
    try:
        while i < len(rest):
            a = rest[i]
            if a == '--gh':
                gh = True
            elif a in ('--since', '--until', '--days', '--du-timeout') and i + 1 < len(rest):
                i += 1
                if a == '--since':
                    since = rest[i]
                elif a == '--until':
                    until = rest[i]
                elif a == '--days':
                    days = int(rest[i])
                else:
                    du_timeout = float(rest[i])
            elif not a.startswith('--') and repo is None:
                repo = a
            else:
                print(USAGE, file=sys.stderr)
                return 2
            i += 1
        if repo is None or not os.path.isdir(repo):
            print('fleet_collect: no such repo directory: %s' % repo, file=sys.stderr)
            return 2
        out = collect(repo, since, until, gh, days, du_timeout)
    except ValueError as e:
        print('fleet_collect: %s' % e, file=sys.stderr)
        return 2
    print(out['summary'], file=sys.stderr)
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


# --- selftest ----------------------------------------------------------------

def selftest():
    misses = []

    def ok(name, cond):
        if cond:
            print('ok: ' + name)
        else:
            misses.append(name)
            print('FAIL: ' + name)

    def write(path, data, mode=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
        if mode:
            os.chmod(path, mode)

    def rows(*recs):
        return ''.join(json.dumps(r) + '\n' for r in recs)

    def rec(role, aid, cost, ms, ts):
        return {'ts': ts, 'role': role, 'level': 'L2', 'attempt_id': aid, 'cost_usd': cost, 'duration_ms': ms}

    def snap(d):
        out = []
        for cur, _ds, ns in os.walk(d):
            for n in ns:
                p = os.path.join(cur, n)
                st = os.stat(p)
                out.append((os.path.relpath(p, d), st.st_size, st.st_mtime_ns))
        return sorted(out)

    me = os.path.abspath(__file__)

    def cli(*args):
        p = subprocess.run([sys.executable, me] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True)
        return p.returncode, p.stdout, p.stderr

    saved = (DU_CMD, DU_TIMEOUT, DU_TOTAL, GH_CMD)
    with tempfile.TemporaryDirectory() as tmp:
        # --- fixture repo: duplicate attempt_ids, an interrupted attempt, a limit marker, lane overrides
        repo = os.path.join(tmp, 'repo')
        t1 = os.path.join(repo, '.sdlc', 't1')
        write(os.path.join(t1, 'runs.jsonl'), rows(
            rec('planner', 'A', 1.0, 60000, '2026-10-01T10:00:00Z'),
            rec('planner', 'A', 1.0, 60000, '2026-10-01T10:00:00Z'),          # duplicate attempt_id
            rec('plan-reviewer', 'B', 0.5, 30000, '2026-10-02T10:00:00Z'),
            rec('solo', 'C', 2.0, 120000, '2026-10-03T10:00:00Z'),
            {'ts': '2026-10-03T11:00:00Z', 'role': 'filer', 'cost_usd': None},  # no attempt_id, unmetered
            {'ts': '2026-10-03T11:00:00Z', 'role': 'filer', 'cost_usd': None},  # same line again
        ))
        write(os.path.join(t1, 'step-1', 'runs.jsonl'), rows(
            rec('plan-reviewer', 'B', 0.5, 30000, '2026-10-02T10:00:00Z'),      # duplicate across files
            rec('builder', 'D', 3.0, 90000, '2026-10-04T10:00:00Z')))
        write(os.path.join(t1, 'step-1', 'builder-L2.attempt.json'), json.dumps(
            {'attempt_id': 'X', 'role': 'builder', 'level': 'L2', 'status': 'interrupted',
             'started_at': '2026-10-04T09:00:00.123456+00:00'}))
        write(os.path.join(t1, 'step-1', 'builder-L2-2.attempt.json'), json.dumps(
            {'attempt_id': 'Y', 'role': 'builder', 'level': 'L2', 'status': 'completed',
             'started_at': '2026-10-04T09:30:00+00:00'}))
        write(os.path.join(t1, 'planner-L2.limit'), json.dumps(
            {'ts': '2026-10-01T09:00:00Z', 'role': 'planner', 'level': 'L2', 'reset': '1:40pm'}) + '\n')
        write(os.path.join(t1, 'skips.md'), '# Skips\n\n## Lane\n'
              '- lane: full; point: before planning; reasons: size L decides before planning\n\n'
              'Lane: solo (tier L) because the user asked for a solo builder; steps.py lane prints full\n')
        t2 = os.path.join(repo, '.sdlc', 't2')
        write(os.path.join(t2, 'runs.jsonl'), rows(rec('verifier', 'E', 0.25, 10000, '2026-10-05T10:00:00Z')))
        write(os.path.join(t2, 'skips.md'), '## Lane\n- lane: solo; point: before planning; reasons: size M\n\n'
              'Lane: solo because size M decides before planning (steps.py lane)\n')     # same lane: no override
        t3 = os.path.join(repo, '.sdlc', 't3')
        write(os.path.join(t3, 'runs.jsonl'), rows(rec('planner', 'F', 4.0, 5000, '2026-10-06T10:00:00Z')))
        write(os.path.join(repo, '.sdlc', 'AGENTS.md'), 'no runs here\n')
        # a lane worktree directory the repo does not register: its copy of t1 plus one new run
        lane = os.path.join(repo, '.worktrees', 'lane1')
        write(os.path.join(lane, '.sdlc', 't1', 'runs.jsonl'), rows(
            rec('planner', 'A', 1.0, 60000, '2026-10-01T10:00:00Z'),            # copy of A
            rec('builder', 'G', 1.0, 1000, '2026-10-06T12:00:00Z')))
        write(os.path.join(lane, '.sdlc', 't1', 'step-1', 'builder-L2.attempt.json'), json.dumps(
            {'attempt_id': 'X', 'role': 'builder', 'level': 'L2', 'status': 'interrupted',
             'started_at': '2026-10-04T09:00:00.123456+00:00'}))                # copy of the interrupted attempt
        write(os.path.join(t1, 'handoff.md'), '---\nid: T-0001\nsize: M      # S | M | L\n---\n\n## Goal\n- not a criterion\n\n'
              '## Acceptance criteria\n- one\n  - nested, not counted\n2. two\n```\n- fenced, not counted\n```\n'
              '* three\nprose line\n\n## Closed\n- after the section\n')
        write(os.path.join(t2, 'handoff.md'), '---\nid: "T-0002"\nsize: L\n---\n\n## Goal\nno criteria yet\n')
        write(os.path.join(lane, '.sdlc', 't1', 'handoff.md'), '---\nid: T-0001\nsize: S\n---\n## Acceptance criteria\n- x\n')

        def layout(root, base, config=None):
            """Two tickets of 3 planner rows each and a size M handoff with 25 criteria, under root/.sdlc/<base>."""
            if config is not None:
                write(os.path.join(root, '.sdlc', 'config'), config)
            for name, ids in (('0001-a', 'abc'), ('0002-b', 'def')):
                write(os.path.join(root, '.sdlc', base, name, 'runs.jsonl'), rows(*[
                    rec('planner', name + i, 1.0, 1000, '2026-10-05T10:00:00Z') for i in ids]))
            write(os.path.join(root, '.sdlc', base, '0001-a', 'handoff.md'), '---\nid: T-9\nsize: M\n---\n'
                  '## Acceptance criteria\n' + ''.join('- c%d\n' % i for i in range(25)))
            write(os.path.join(root, '.sdlc', 'plain', 'runs.jsonl'), rows(rec('planner', 'p', 1.0, 1000, '2026-10-05T10:00:00Z')))

        flat, nest, cmt = (os.path.join(tmp, n) for n in ('flat', 'nest', 'cmt'))
        layout(flat, '')
        layout(nest, 'tickets', 'ticket_folders: numbered\nticket_root: tickets  # the one supported value\n')
        layout(cmt, '', '# ticket_root: tickets\nticket_folders: numbered\n')
        # a lane worktree of the nested repo: its `.sdlc/config` is untracked, so the lane has none
        write(os.path.join(nest, '.worktrees', 'lane', '.sdlc', 'tickets', '0003-c', 'runs.jsonl'),
              rows(rec('planner', 'lane1', 1.0, 1000, '2026-10-05T10:00:00Z')))
        before = snap(tmp)
        fr, nr, cr = (collect_runs(d, Window())['by_ticket'] for d in (flat, nest, cmt))
        ok('ticket_root: tickets keys each ticket folder, not the tickets dir, in a config-less lane too', nr == {
            'plain': {'planner': 1}, 'tickets/0001-a': {'planner': 3}, 'tickets/0002-b': {'planner': 3},
            'tickets/0003-c': {'planner': 1}})
        ok('ticket_root control: the flat layout keys the same folders by name', fr == {
            'plain': {'planner': 1}, '0001-a': {'planner': 3}, '0002-b': {'planner': 3}})
        ok('ticket_root control: a commented ticket_root line does not switch layouts', cr == fr)
        ok('tickets: the nested layout is read too, and the flat one', tickets_info(nest)['items'] == [
            {'ticket': 'tickets/0001-a', 'id': 'T-9', 'size': 'M', 'criteria': 25}]
           and tickets_info(flat)['items'] == [{'ticket': '0001-a', 'id': 'T-9', 'size': 'M', 'criteria': 25}]
           and tickets_info(nest)['count'] == 1)

        tk = tickets_info(repo)
        ok('tickets: count, size, and the criteria of the first copy of each folder', tk['count'] == 2
           and tk['items'] == [{'ticket': 't1', 'id': 'T-0001', 'size': 'M', 'criteria': 3}])
        ok('tickets: a repo with no .sdlc has none', tickets_info(os.path.join(tmp, 'nowhere')) == {'count': 0, 'items': []})

        r = collect_runs(repo, Window())
        # unique: A, B, C, no-id filer (once), D, E, F, G = 8; cost 1+0.5+2+3+0.25+4+1 = 11.75
        ok('dedupe: each attempt counts once', r['total'] == 8)
        ok('dedupe: cost sums each attempt once', abs(r['cost_usd'] - 11.75) < 1e-9)
        ok('dedupe: dropped rows are counted', r['duplicates_dropped'] == 4)   # A, B, no-id line, A copy
        ok('unmetered: a null cost is reported', r['unmetered'] == 1)
        # T-0402: a row flagged unpriced counts as unmetered even with a cost; a null-cost row still does; a priced row does not.
        repo2_tmp = tempfile.mkdtemp(prefix='fleet-unpriced.')
        repo2 = os.path.join(repo2_tmp, 'repo2')
        write(os.path.join(repo2, '.sdlc', 't1', 'runs.jsonl'), rows(
            {'ts': '2026-10-03T12:00:00Z', 'role': 'builder', 'cost_usd': 0.1, 'unpriced': True, 'attempt_id': 'U1'},
            {'ts': '2026-10-03T12:00:00Z', 'role': 'builder', 'cost_usd': None, 'unpriced': True, 'attempt_id': 'U2'},
            {'ts': '2026-10-03T12:00:00Z', 'role': 'builder', 'cost_usd': 0.2, 'attempt_id': 'P1'}))
        ok('unmetered: an unpriced true row is counted once, a priced row is not', collect_runs(repo2, Window())['unmetered'] == 2)
        shutil.rmtree(repo2_tmp, ignore_errors=True)
        ok('by_role: planner has two attempts', r['by_role']['planner']['count'] == 2
           and abs(r['by_role']['planner']['cost_usd'] - 5.0) < 1e-9)
        ok('interrupted: reported once across a worktree copy', r['interrupted']['count'] == 1
           and r['interrupted']['attempts'][0]['attempt_id'] == 'X')
        ok('interrupted: lost_min runs to the next attempt start in the same dir and role',
           r['interrupted']['attempts'][0]['lost_min'] == 30.0 and r['interrupted']['lost_min_median'] == 30.0
           and r['interrupted']['lost_min_total'] == 30.0)
        ok('interrupted: no interrupted attempt gives a null median and a zero total',
           collect_runs(repo, Window(since='2026-10-05'))['interrupted']['lost_min_median'] is None
           and collect_runs(repo, Window(since='2026-10-05'))['interrupted']['lost_min_total'] == 0)
        ok('limit marker counted', r['limit_markers']['count'] == 1 and r['limit_markers']['files'][0]['reset'] == '1:40pm')
        ok('lane override: full recorded, solo effective', any(
            o['ticket'] == 't1' and o['recorded'] == 'full' and o['effective'] == 'solo' for o in r['lane_overrides']))
        ok('lane override: a same-lane prose line is not an override', all(o['ticket'] != 't2' for o in r['lane_overrides']))
        # solo lane: A,B,C,filer,D (t1 effective solo) + E (t2 solo) = 6 runs, cost 1+.5+2+3+.25 = 6.75
        ok('by_lane: override and role solo count as solo', r['by_lane']['solo']['count'] == 6
           and abs(r['by_lane']['solo']['cost_usd'] - 6.75) < 1e-9)
        ok('by_lane: no skips.md and a skipsless worktree copy are full', r['by_lane']['full']['count'] == 2
           and abs(r['by_lane']['full']['cost_usd'] - 5.0) < 1e-9)
        ok('by_ticket: runs per ticket folder and role, deduplicated, worktree copy included',
           r['by_ticket']['t1'] == {'builder': 2, 'filer': 1, 'plan-reviewer': 1, 'planner': 1, 'solo': 1}
           and r['by_ticket']['t3'] == {'planner': 1} and r['by_ticket']['t2'] == {'verifier': 1})
        ok('plan_review_share: (planner + plan-reviewer) / total', abs(plan_review_share(r) - 5.5 / 11.75) < 1e-3)
        ok('duration_s sums milliseconds', abs(r['duration_s'] - 316.0) < 1e-6)
        # negative control: with dedupe off, duplicates change the total
        n = collect_runs(repo, Window(), dedupe=False)
        ok('negative control: dedupe off changes the total', n['total'] > r['total'] and n['cost_usd'] > r['cost_usd'])
        ok('negative control: dedupe off double-counts the interrupted attempt', n['interrupted']['count'] == 2)

        w = collect_runs(repo, Window('2026-10-03', '2026-10-04'))
        ok('window: bare dates include the whole until day', w['total'] == 3)      # C, filer (once), D
        w = collect_runs(repo, Window(until='2026-10-02T10:00:00Z'))
        ok('window: an ISO until is inclusive', w['total'] == 2 and w['limit_markers']['count'] == 1)
        w = collect_runs(repo, Window(since='2026-10-05'))
        ok('window: since drops the interrupted attempt and the limit marker',
           w['total'] == 3 and w['interrupted']['count'] == 0 and w['limit_markers']['count'] == 0)
        try:
            Window('not-a-date')
            ok('window: a bad date is refused', False)
        except ValueError:
            ok('window: a bad date is refused', True)

        # KPI fields (T-0411): orphaned attempts, blocked builders, plan defects, attempt minutes. Own temp tree so the
        # read-only snapshot above stays whole.
        kpi_tmp = tempfile.mkdtemp(prefix='fleet-kpi.')
        kp = os.path.join(kpi_tmp, 'repo')
        dead = subprocess.Popen([sys.executable, '-c', 'pass'])
        dead.wait()                                  # a pid that has exited and been reaped: dead now
        live_start = datetime.datetime.now(UTC).isoformat()   # after this process began, so its pid is not "reused"
        def att(aid, role, status, started, **kw):
            return json.dumps(dict({'attempt_id': aid, 'role': role, 'level': 'L2', 'status': status,
                                    'started_at': started}, **kw))
        k1 = os.path.join(kp, '.sdlc', 'k1')
        write(os.path.join(k1, 'a-dead.attempt.json'), att('RD', 'builder', 'running', '2026-10-05T08:00:00+00:00',
                                                          parent_pid=dead.pid))
        write(os.path.join(k1, 'b-alive.attempt.json'), att('RA', 'builder', 'running', live_start,
                                                           parent_pid=os.getpid()))
        write(os.path.join(k1, 'c-codex.attempt.json'), att('RC', 'builder', 'running', '2026-10-05T08:00:00+00:00',
                                                           parent_pid=dead.pid, backend='codex'))
        write(os.path.join(k1, 'd-old.attempt.json'), att('RO', 'builder', 'running', '2026-09-01T08:00:00+00:00',
                                                         parent_pid=dead.pid))
        write(os.path.join(k1, 'e-owner.attempt.json'), att('RW', 'planner', 'running', '2026-10-05T08:00:00+00:00',
                                                           owner_pid=dead.pid))
        write(os.path.join(kp, '.worktrees', 'lane', '.sdlc', 'k1', 'a-dead.attempt.json'),
              att('RD', 'builder', 'running', '2026-10-05T08:00:00+00:00', parent_pid=dead.pid))   # worktree copy
        write(os.path.join(k1, 'f-moved.attempt.json'), att('RS', 'builder', 'running', '2026-10-05T08:00:00+00:00',
                                                           parent_pid=dead.pid))
        write(os.path.join(kp, '.worktrees', 'lane', '.sdlc', 'k1', 'f-moved.attempt.json'), att(
            'RS', 'builder', 'completed', '2026-10-05T08:00:00+00:00', finished_at='2026-10-05T08:05:00+00:00'))
        write(os.path.join(k1, 'step-1', 'verifier-L2.attempt.json'), att(
            'V1', 'verifier', 'completed', '2026-10-05T10:00:00+00:00', finished_at='2026-10-05T10:12:00+00:00'))
        write(os.path.join(k1, 'step-2', 'verifier-L2.attempt.json'), att(
            'V2', 'verifier', 'completed', '2026-10-06T10:00:00+00:00', finished_at='2026-10-06T10:30:00+00:00'))
        write(os.path.join(k1, 'step-2', 'builder-L2.attempt.json'), att(
            'I1', 'builder', 'interrupted', '2026-10-06T08:00:00+00:00', finished_at='2026-10-06T08:20:00+00:00'))
        write(os.path.join(k1, 'runs.jsonl'), rows(
            dict(rec('builder', 'B1', 1.0, 1000, '2026-10-05T12:00:00Z'), file='builder-L2-1.md'),
            dict(rec('builder', 'B1', 1.0, 1000, '2026-10-05T12:00:00Z'), file='builder-L2-1.md'),     # duplicate row
            dict(rec('builder', 'B2', 1.0, 1000, '2026-10-05T13:00:00Z'), file='builder-L2-2.md'),
            dict(rec('builder', 'B3', 1.0, 1000, '2026-09-01T13:00:00Z'), file='builder-L2-3.md'),      # outside window
            dict(rec('verifier', 'V1', 1.0, 1000, '2026-10-05T14:00:00Z'), file='verifier-L2-1.md')))
        write(os.path.join(k1, 'builder-L2-1.md'), '# Builder\n\n## Status\n\nblocked: no way to run the check\n')
        write(os.path.join(k1, 'builder-L2-2.md'), '# Builder\n\n## Status\ndone\n\n## Notes\nblocked by nothing\n')
        write(os.path.join(k1, 'builder-L2-3.md'), '## Status\nblocked\n')
        write(os.path.join(k1, 'verifier-L2-1.md'), '## Verdict\nfail\n\n- plan defect: the criterion cannot pass\n')
        write(os.path.join(k1, 'refusals.jsonl'),
              json.dumps({'ts': '2026-10-05T09:00:00Z', 'tool': 'steps.py lint', 'plan': 'p.md', 'step': 1, 'text': 'x'}) + '\n'
              + json.dumps({'ts': '2026-10-05T09:00:05Z', 'tool': 'steps.py lint', 'plan': 'p.md', 'step': 1, 'text': 'x'}) + '\n'
              + json.dumps({'ts': '2026-10-05T09:01:00Z', 'tool': 'steps.py split', 'plan': 'p.md', 'step': 2, 'text': 'y'}) + '\n'
              + json.dumps({'ts': '2026-09-01T09:00:00Z', 'tool': 'steps.py lint', 'plan': 'q.md', 'step': 1, 'text': 'z'}) + '\n'
              + 'not json\n')
        kx = {}
        kr = collect_runs(kp, Window(since='2026-10-01'), extra=kx)
        ok('orphaned: a running attempt whose parent pid is dead is counted',
           sorted(a['attempt_id'] for a in kr['orphaned']['attempts']) == ['RD', 'RW'] and kr['orphaned']['count'] == 2)
        ok('negative control: a running attempt whose parent pid is alive is not counted orphaned',
           all(a['attempt_id'] != 'RA' for a in kr['orphaned']['attempts']))
        ok('orphaned: an attempt another worktree copy shows finished is not counted',
           all(a['attempt_id'] != 'RS' for a in kr['orphaned']['attempts']))
        ok('orphaned: a codex attempt and one started before the window are not counted',
           all(a['attempt_id'] not in ('RC', 'RO') for a in kr['orphaned']['attempts']))
        # T-0809: a running attempt with a live parent pid on a done or dropped ticket is orphaned, as dispatch.py status says
        k2 = os.path.join(kp, '.sdlc', 'k2')
        write(os.path.join(k2, 'handoff.md'), '---\nid: T-0999\nstatus: done\n---\n## Goal\nx\n')
        write(os.path.join(k2, 'verifier-L2.attempt.json'), att('RT', 'verifier', 'running', live_start,
                                                               parent_pid=os.getpid()))
        k3 = os.path.join(kp, '.sdlc', 'k3')
        write(os.path.join(k3, 'handoff.md'), '---\nid: T-0998\nstatus: claimed\n---\n## Goal\nx\n')
        write(os.path.join(k3, 'verifier-L2.attempt.json'), att('RU', 'verifier', 'running', live_start,
                                                               parent_pid=os.getpid()))
        kc = collect_runs(kp, Window(since='2026-10-01'))
        ok('orphaned: a live-pid running attempt on a done ticket is counted, as dispatch.py status counts it',
           'RT' in [a['attempt_id'] for a in kc['orphaned']['attempts']])
        ok('negative control: a live-pid running attempt on an open ticket is not counted orphaned',
           'RU' not in [a['attempt_id'] for a in kc['orphaned']['attempts']])
        # T-0445: an interrupted record whose result file holds a verdict is not a lost run; one with no result still is
        write(os.path.join(k1, 'step-3', 'verifier-L2.attempt.json'), att(
            'IR', 'verifier', 'interrupted', '2026-10-06T09:00:00+00:00', finished_at='2026-10-06T09:40:00+00:00'))
        write(os.path.join(k1, 'step-3', 'verifier-L2.md'), '<!-- role=verifier level=L2 model=sonnet effort=high -->\n## Verdict\npass\n')
        write(os.path.join(k1, 'step-4', 'verifier-L2.attempt.json'), att(
            'IN', 'verifier', 'interrupted', '2026-10-06T09:00:00+00:00', finished_at='2026-10-06T09:40:00+00:00'))
        write(os.path.join(k1, 'step-4', 'verifier-L2.md'), '<!-- role=verifier level=L2 model=sonnet effort=high -->\n## Findings\nno verdict\n')
        kr2 = collect_runs(kp, Window(since='2026-10-01'))
        ok('interrupted: an attempt whose result file holds a verdict is not counted',
           all(a['attempt_id'] != 'IR' for a in kr2['interrupted']['attempts']))
        ok('negative control: an interrupted attempt whose result holds no verdict is still counted',
           sorted(a['attempt_id'] for a in kr2['interrupted']['attempts']) == ['I1', 'IN']
           and kr2['interrupted']['lost_min_total'] == 60.0)
        os.remove(os.path.join(k1, 'step-3', 'verifier-L2.md'))
        os.remove(os.path.join(k1, 'step-3', 'verifier-L2.attempt.json'))
        os.remove(os.path.join(k1, 'step-4', 'verifier-L2.md'))
        os.remove(os.path.join(k1, 'step-4', 'verifier-L2.attempt.json'))
        ok('interrupted: lost_min falls back to finished_at with no later attempt',
           kr['interrupted']['attempts'][0]['lost_min'] == 20.0)
        ok('results: a builder result whose Status is blocked is counted',
           kx['results']['builder'] == {'total': 2, 'blocked': 1})
        ok('plan_defects: a plan defect line in a builder or verifier result is counted late',
           kx['plan_defects']['late'] == 1)
        ok('plan_defects: a refusals.jsonl line in the window is counted early',
           kx['plan_defects']['early'] == 2)
        ok('attempts: completed verifier minutes run from started_at to finished_at',
           kx['attempts']['by_role'] == {'builder': {'count': 1, 'median_min': 5.0, 'max_min': 5.0},
                                         'verifier': {'count': 2, 'median_min': 21.0, 'max_min': 30.0}})
        ob = kx['attempts']['over_budget']
        ok('attempts: a completed verifier that ran 30m against 25m is named once with role, wall and budget (T-0811)',
           ob['count'] == 1 and [(a['role'], a['wall_min'], a['budget_min']) for a in ob['attempts']] == [('verifier', 30.0, 25)])
        ok('negative control: a completed builder inside its budget is not named', all(a['role'] != 'builder' for a in ob['attempts']))
        kd = {}
        collect_runs(kp, Window(since='2026-10-01'), dedupe=False, extra=kd)
        ok('negative control: dedupe off double-counts the builder row and the repeated refusal',
           kd['results']['builder']['total'] == 3 and kd['plan_defects']['early'] == 3)
        kc = collect(kp, since='2026-10-01', du_timeout=1)
        ok('collect: results, plan_defects and attempts sit beside runs', kc['results']['builder']['blocked'] == 1
           and kc['plan_defects']['late'] == 1 and 'verifier' in kc['attempts']['by_role'])
        ke = collect(os.path.join(kpi_tmp, 'nowhere'), du_timeout=1)
        ok('collect: a repo with no .sdlc reads zero results, defects and attempts', ke['runs'] == 'none'
           and ke['results'] == {'builder': {'total': 0, 'blocked': 0}} and ke['attempts'] == {'by_role': {}, 'over_budget': {'count': 0, 'attempts': []}}
           and ke['plan_defects'] == {'late': 0, 'early': 0})
        shutil.rmtree(kpi_tmp, ignore_errors=True)

        # --- records dir (order.py): runtime/tasks/<key> rows belong to the task folder; legacy reads in place
        fm = '---\nid: T-0001\ntitle: "a"\nstatus: done\n---\n\n## Goal\na\n'
        outcome = '\n## Outcome\n\n2026-10-13 \u00b7 lane: solo L2\n- Changed: see commits\n'
        review = ('\n## Plan review\n\n- 2026-10-05 plan defect at split: step 2: no criterion\n'
                  '- 2026-10-05 plan defect at split: step 2: no criterion\n'
                  '- 2026-09-01 plan defect at split: step 1: before the window\n'
                  '- plan defect at split: no date\n')
        rt = tempfile.mkdtemp()             # outside tmp: the read-only snapshot of tmp is taken earlier
        rs = os.path.join(rt, '.sdlc')
        write(os.path.join(rs, '.0001-a', 'handoff.md'), fm + outcome + review)
        write(os.path.join(rs, 'runtime', 'tasks', '0001-a', 'runs.jsonl'),
              rows(rec('builder', 'RB', 1.5, 1000, '2026-10-05T12:00:00Z')))
        write(os.path.join(rs, 'runtime', 'tasks', '0001-a', 'step-1', 'runs.jsonl'),
              rows(rec('verifier', 'RV', 0.5, 1000, '2026-10-05T13:00:00Z')))
        write(os.path.join(rs, 'runtime', 'tasks', '0009-z', 'runs.jsonl'),
              rows(rec('solo', 'RZ', 2.0, 1000, '2026-10-05T14:00:00Z')))
        rx = {}
        rr = collect_runs(rt, Window(since='2026-10-01'), extra=rx)
        ok('records dir: runtime-only fixture keys rows by the task folder, else by the bare key',
           rr['by_ticket'] == {'.0001-a': {'builder': 1, 'verifier': 1}, '0009-z': {'solo': 1}}
           and rr['cost_usd'] == 4.0)
        ok('records dir: runtime-only fixture reads the lane from the Outcome header with no skips.md',
           rr['by_lane']['solo']['count'] == 3 and rr['by_lane']['full']['count'] == 0)
        ok('plan_defects: a dated plan defect at split line in a handoff Plan review is counted early once',
           rx['plan_defects']['early'] == 1)
        rd = {}
        collect_runs(rt, Window(since='2026-10-01'), dedupe=False, extra=rd)
        ok('negative control: dedupe off counts the repeated plan defect at split line twice',
           rd['plan_defects']['early'] == 2)
        write(os.path.join(rs, '.0001-a', 'handoff.md'), fm + review)
        rn = collect_runs(rt, Window(since='2026-10-01'))
        ok('negative control: records dir: runtime-only fixture with no Outcome and no skips.md reads full',
           rn['by_lane']['solo']['count'] == 1 and rn['by_lane']['full']['count'] == 2)
        write(os.path.join(rs, '.0001-a', 'handoff.md'), fm + outcome)
        write(os.path.join(rs, '.0001-a', 'skips.md'), '# Skips\n\n## Lane\n- lane: full; point: before planning\n')
        rk = collect_runs(rt, Window(since='2026-10-01'))
        ok('records dir: runtime-only fixture: the task folder skips.md wins over the Outcome lane',
           rk['by_lane']['solo']['count'] == 1 and rk['by_lane']['full']['count'] == 2)
        shutil.rmtree(os.path.join(rs, 'runtime'))
        os.remove(os.path.join(rs, '.0001-a', 'skips.md'))
        write(os.path.join(rs, '.0001-a', 'runs.jsonl'), rows(rec('builder', 'RB', 1.5, 1000, '2026-10-05T12:00:00Z')))
        write(os.path.join(rs, '.0001-a', 'step-1', 'runs.jsonl'),
              rows(rec('verifier', 'RV', 0.5, 1000, '2026-10-05T13:00:00Z')))
        rl = collect_runs(rt, Window(since='2026-10-01'))
        ok('records dir: legacy fixture reads in-folder records under the same key and Outcome lane',
           rl['by_ticket'] == {'.0001-a': {'builder': 1, 'verifier': 1}} and rl['cost_usd'] == 2.0
           and rl['by_lane']['solo']['count'] == 2)
        shutil.rmtree(rt, ignore_errors=True)

        # --- work_root (roots.py): ticket folders under <top>/<work_root> keep the flat layout's keys
        crit = '\n## Acceptance criteria\n- one\n- two\n'
        wt_tmp = tempfile.mkdtemp()
        wflat, wroot, wcmt = (os.path.join(wt_tmp, n) for n in ('flat', 'work', 'cmt'))
        for top, base, config in ((wflat, '.sdlc', None), (wroot, os.path.join('docs', 'work'), 'work_root: docs/work\n'),
                                  (wcmt, os.path.join('docs', 'work'), '# work_root: docs/work\n')):
            if config is not None:
                write(os.path.join(top, '.sdlc', 'config'), config)
            write(os.path.join(top, base, '0001-a', 'handoff.md'), fm.replace('done', 'claimed') + outcome + crit)
            write(os.path.join(top, base, '.0002-b', 'handoff.md'), fm.replace('T-0001', 'T-0002') + crit)
            write(os.path.join(top, '.sdlc', 'runtime', 'tasks', '0001-a', 'runs.jsonl'),
                  rows(rec('builder', 'W1', 1.0, 1000, '2026-10-05T12:00:00Z')))
            write(os.path.join(top, '.sdlc', 'runtime', 'tasks', '0002-b', 'runs.jsonl'),
                  rows(rec('verifier', 'W2', 1.0, 1000, '2026-10-05T12:00:00Z')))
        wf, ww, wc = (collect_runs(d, Window()) for d in (wflat, wroot, wcmt))
        ok('work_root: runtime/tasks/0001-a keys to ticket 0001-a read from docs/work, as the flat layout keys it',
           ww['by_ticket'] == wf['by_ticket'] == {'0001-a': {'builder': 1}, '.0002-b': {'verifier': 1}})
        ok('work_root: the lane is read from the docs/work handoff Outcome, as in the flat layout',
           ww['by_lane']['solo']['count'] == wf['by_lane']['solo']['count'] == 1)
        ok('work_root: tickets lists the docs/work folders under the flat keys', tickets_info(wroot) == tickets_info(wflat)
           == {'count': 2, 'items': [{'ticket': '.0002-b', 'id': 'T-0002', 'size': None, 'criteria': 2},
                                     {'ticket': '0001-a', 'id': 'T-0001', 'size': None, 'criteria': 2}]})
        ok('work_root control: a commented work_root line does not read docs/work',
           wc['by_ticket'] == {'0001-a': {'builder': 1}, '0002-b': {'verifier': 1}}
           and tickets_info(wcmt)['count'] == 0)
        shutil.rmtree(wt_tmp, ignore_errors=True)

        # cli: json out, summary on stderr, repo untouched
        rc, out, err = cli('collect', repo, '--until', '2026-10-06T12:00:00Z', '--du-timeout', '5')
        data = json.loads(out) if rc == 0 else {}
        ok('cli: collect exits 0 with JSON', rc == 0 and data.get('runs', {}).get('total') == 8)
        ok('cli: stderr carries the runs line', err.startswith('runs: 8 deduped'))
        ok('cli: every documented key is present', all(k in data for k in (
            'env', 'runs', 'plan_review_share', 'tickets', 'processes', 'worktrees', 'ci', 'summary')))
        ok('cli: env names the plugin version and the time', data['env']['plugin']['version'] != ''
           and data['env']['time'].endswith('Z') and 'load1' in data['env']['uptime_load'])
        ok('cli: ci is skipped without --gh', data.get('ci') == 'skipped')
        ok('cli: lane worktree dir is counted as a worktree', data['worktrees']['count'] == 1)
        ok('read-only: the collected repo is byte for byte unchanged', snap(tmp) == before)

        # no .sdlc
        bare = os.path.join(tmp, 'bare')
        os.makedirs(bare)
        rc, out, err = cli('collect', bare)
        data = json.loads(out) if rc == 0 else {}
        ok('no .sdlc: exits 0 with runs: none', rc == 0 and data.get('runs') == 'none'
           and data.get('summary') == 'runs: none' and err.startswith('runs: none'))
        ok('no .sdlc: plan_review_share is null', data.get('plan_review_share') is None)
        rc, _o, _e = cli('collect', os.path.join(tmp, 'missing'))
        ok('missing repo: exit 2', rc == 2)
        rc, _o, _e = cli('collect', bare, '--since', 'nope')
        ok('bad --since: exit 2', rc == 2)

        # T-0575: lane dirs under the sibling root (wtroot.py root, <parent>/<repo>.worktrees) git does not register
        sib = os.path.realpath(os.path.join(tmp, 'sibrepo'))
        os.makedirs(sib)
        subprocess.run(['git', '-C', sib, 'init', '-q'], check=True, capture_output=True)
        write(os.path.join(sib + '.worktrees', 'fanout-a', '.sdlc', 't9', 'runs.jsonl'),
              rows(rec('planner', 'S1', 1.0, 1000, '2026-10-05T10:00:00Z')))
        _r, linked = worktree_roots(sib)
        ok('sibling root: an unregistered lane dir under <repo>.worktrees is a linked root',
           os.path.join(sib + '.worktrees', 'fanout-a') in linked)
        sr = collect_runs(sib, Window())
        ok('sibling root: its runs are read', isinstance(sr, dict) and sr['by_ticket'] == {'t9': {'planner': 1}})
        plain = os.path.realpath(os.path.join(tmp, 'plainrepo'))
        write(os.path.join(plain + '.worktrees', 'l', 'x.txt'), 'x\n')
        ok('sibling root: a repo outside git reads <repo>.worktrees too',
           worktree_roots(plain)[1] == [os.path.join(plain + '.worktrees', 'l')])

        # du timeout: a fake du that sleeps, killed cleanly
        fake = os.path.join(tmp, 'bin', 'slow-du')
        write(fake, '#!/bin/sh\nexec sleep 30\n', 0o755)
        globals()['DU_CMD'], globals()['DU_TIMEOUT'], globals()['DU_TOTAL'] = fake, 0.3, 30.0
        t0 = time.monotonic()
        wt = worktree_info(repo)
        took = time.monotonic() - t0
        ok('du timeout: size is unknown, not a hang', wt['size'] == 'unknown' and took < 5
           and wt['items'][0]['size'] == 'unknown')
        globals()['DU_TOTAL'] = 0.0
        ok('du total budget spent: later worktrees are unknown without a du', worktree_info(repo)['size'] == 'unknown')
        globals()['DU_CMD'], globals()['DU_TIMEOUT'], globals()['DU_TOTAL'] = saved[0], saved[1], saved[2]
        wt = worktree_info(repo)
        ok('du: a real du gives a size', wt['size'] != 'unknown' and wt['size_kb_known'] >= 0)

        # git worktree discovery through a real repository
        if run_bounded(['git', '--version'], 5).ok:
            g = os.path.join(tmp, 'g')
            os.makedirs(g)
            gitc = ['git', '-C', g, '-c', 'user.name=t', '-c', 'user.email=t@t']
            subprocess.run(gitc + ['init', '-q'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            write(os.path.join(g, 'f.txt'), 'x\n')
            subprocess.run(gitc + ['add', 'f.txt'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(gitc + ['commit', '-q', '-m', 'x'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            gw = os.path.join(tmp, 'g-wt')
            subprocess.run(gitc + ['worktree', 'add', '-q', gw, '-b', 'lane'], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            write(os.path.join(gw, '.sdlc', 't', 'runs.jsonl'), rows(rec('builder', 'Z', 1.5, 1000, '2026-10-06T00:00:00Z')))
            gr = collect_runs(g, Window())
            ok('git worktree list: a registered worktree outside the repo is scanned',
               isinstance(gr, dict) and gr['total'] == 1 and worktree_info(g)['count'] == 1)
        else:
            print('skip: git not found; worktree discovery not exercised')

        # process classification
        samples = [
            ('/Users/x/.local/bin/claude -p --plugin-dir /p', 'claude'),
            ('node /usr/lib/node_modules/@anthropic-ai/claude-code/cli.js -p', 'claude'),
            ('bash /p/plugins/sdlc-lite/hooks/block-pattern-kill.sh', 'hooks'),
            ('/bin/bash /x/block-disk-scan.sh', 'hooks'),
            ('/Users/x/Library/Caches/ms-playwright/chromium-1100/chrome-mac/Chromium.app/Contents/MacOS/Chromium --headless', 'chromium'),
            ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --type=renderer', 'chromium'),
            ('vim notes-about-chromium.md', None),
            ('python3 /x/fleet_collect.py collect /r', None),
        ]
        ok('processes: classification of known command lines', all(classify_process(c) == k for c, k in samples))
        ps = process_info()
        ok('processes: a live ps snapshot has the three groups', all(k in ps for k in ('chromium', 'hooks', 'claude')))
        ok('processes: every group carries cpu, rss and the hooks carry items', all(
            'cpu_pct' in ps[k] and 'rss_mb' in ps[k] for k in ('chromium', 'hooks', 'claude'))
           and isinstance(ps['hooks']['items'], list))
        ok('processes: etime forms', [parse_etime(t) for t in ('00:07', '1:02:03', '2-01:00:00', 'x')]
           == [7, 3723, 176400, None])
        ok('processes: a ps line gives pid, cpu, etime, rss and the command', parse_ps_line(
            '  4321  99.5   00:31 20480 /bin/bash /p/hooks/block-disk-scan.sh')
           == (4321, 99.5, 31, 20480, '/bin/bash /p/hooks/block-disk-scan.sh') and parse_ps_line('garbage') is None)

        # gh: a stub gh feeds the aggregation; a missing gh is an error object, not a crash
        stub = os.path.join(tmp, 'bin', 'gh')
        write(stub, '#!/bin/sh\ncat <<EOF\n'
              '{"name":"CI","event":"pull_request","head_sha":"aaa","conclusion":"success","run_started_at":"2026-10-05T10:00:00Z","updated_at":"2026-10-05T10:10:00Z"}\n'
              '{"name":"CI","event":"push","head_sha":"aaa","conclusion":"failure","run_started_at":"2026-10-05T11:00:00Z","updated_at":"2026-10-05T11:05:30Z"}\n'
              '{"name":"CI","event":"push","head_sha":"bbb","conclusion":"success","run_started_at":"2026-10-05T12:00:00Z","updated_at":"2026-10-05T12:01:00Z"}\n'
              '{"name":"CI","event":"push","head_sha":"aaa","conclusion":"success","run_started_at":"2026-09-01T12:00:00Z","updated_at":"2026-09-01T12:01:00Z"}\n'
              '{"name":"Deploy","conclusion":"success","run_started_at":"2026-10-05T12:00:00Z","updated_at":"2026-10-05T12:02:00Z"}\n'
              'EOF\n', 0o755)
        globals()['GH_CMD'] = stub
        ci = ci_info(repo, Window(), 7, now=datetime.datetime(2026, 10, 6, tzinfo=UTC))
        ok('ci: runs and wall minutes by workflow', ci.get('runs') == 5 and ci['failed'] == 1
           and ci['by_workflow']['CI']['runs'] == 4 and ci['by_workflow']['CI']['failed'] == 1
           and ci['by_workflow']['CI']['wall_minutes'] == 17.5
           and ci['by_workflow']['Deploy']['wall_minutes'] == 2.0)
        ok('ci: runs by event, and a missing event is unknown', ci['by_workflow']['CI']['by_event']
           == {'pull_request': 1, 'push': 3} and ci['by_workflow']['Deploy']['by_event'] == {'unknown': 1}
           and ci['window_days'] == 7)
        ok('ci: push runs over the last 7 days, and the ones duplicating a pull_request run',
           ci['by_workflow']['CI']['push_runs_7d'] == 2 and ci['by_workflow']['CI']['pull_request_runs_7d'] == 1
           and ci['by_workflow']['CI']['push_dup_7d'] == 1 and ci['by_workflow']['Deploy']['push_dup_7d'] == 0)
        globals()['GH_CMD'] = os.path.join(tmp, 'bin', 'no-such-gh')
        ok('ci: a missing gh is an error object', 'error' in ci_info(repo, Window(), 7))
        globals()['GH_CMD'] = saved[3]
    globals()['DU_CMD'], globals()['DU_TIMEOUT'], globals()['DU_TOTAL'], globals()['GH_CMD'] = saved
    if misses:
        print('fleet_collect selftest: %d failed: %s' % (len(misses), '; '.join(misses)), file=sys.stderr)
        return 1
    print('fleet_collect selftest: ok')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
