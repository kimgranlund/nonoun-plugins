#!/usr/bin/env python3
"""evals.py: recorded model and effort experiments, and the lock that ties the model table to one.

Evals live in <root>/evals/ (root is the .sdlc folder). The repo dir is <root>/.. resolved; every
evidence path and every path in the lock is relative to it, in posix form.

Eval file
  Name: NNNN-<slug>.md directly in <root>/evals/ (regex \\d{4}-[a-z0-9][a-z0-9-]*\\.md). AGENTS.md,
  CLAUDE.md, and non-.md files there are not evals.
  Text: a --- line, one `key: value` line per field, a --- line, then the body. Values are bare: no
  quoting, no comments. Only evidence may hold a one-line [a, b, c] list.
  Fields, in this order (validation reports the first problem in this order):
    role       [a-z][a-z-]*  (syntactic, so a renamed role never invalidates an old record)
    level      L1 to L5, or all
    model      [A-Za-z0-9][A-Za-z0-9._-]*  (any model id, in the table or not; all matches)
    effort     [a-z]+  (no fixed list)
    host       claude, codex, or all
    task_set   any non-empty one-line text, never checked for existence
    pass_rate  <passed>/<total>, non-negative integers, passed <= total (0/0 is allowed)
    cost_usd   a non-negative number (\\d+(\\.\\d+)?) or unknown
    date       YYYY-MM-DD
    evidence   one item or a [a, b, ...] list; each item is an http(s) URL (form only, never
               fetched) or a relative path with no .. segment that exists under the repo dir
  `all` in role, level, model, effort, and host marks a record that covers the whole table.
  Body: a `## Method` line and a later `## Result` line, each followed by at least one non-blank
  line before the next `## ` line.

Model table hash
  Every pipeline-role row of <plugin>/adapters/claude/levels.json (a level named L1 to L9; the solo
  tiers S, M, and L are not rows of the lock), formatted as `<role>:<level> <model> <effort>`,
  sorted, one per line, then adapters/codex/models.json dumped with sorted keys and compact
  separators, then a newline. table_sha256 is the sha256 hex of that UTF-8 text, so whitespace
  edits leave it alone and any value change moves it. The text equals the one the run.sh case rows
  gave before levels.json became the table home, so the hash did not move. evals.py never writes
  levels.json, run.sh, or models.json.

Lock
  <root>/evals/table-lock.json holds exactly {eval, previous_eval, table_sha256}: the cited eval,
  the eval it replaced (or null), and the hash the cited eval covers. Only `lock` writes it.

CLI (global options come before the subcommand)
  evals.py [--root DIR] [--plugin DIR] <cmd>
    --root DIR     the .sdlc folder (default: .sdlc in the cwd)
    --plugin DIR   the dir holding adapters/claude/levels.json and adapters/codex/models.json
                   (default: the parent of this script's dir)
  add <slug> --role R --level L --model M --effort E --host H --task-set S --pass-rate P/T
      --cost-usd C --date D --evidence X [--evidence Y ...] --method TEXT --result TEXT
                 write the next NNNN-<slug>.md; refuses an invalid record and writes nothing
  list           one tab-separated line per eval: name, date, host, role, level, model, effort,
                 pass_rate, cost_usd (or `<name>\\tinvalid: <reason>`); always exits 0
  check          validate every eval and the lock against the current table hash
  lock --eval PATH
                 cite PATH (from the cwd) in the lock; a replacement must be dated later than the
                 eval it replaces
  hash           print the current table_sha256
  selftest       run the temp-dir regression cases, including the negative controls
Exit codes: 0 ok, 1 refusal or failed check, 2 usage error.

Python API: FIELDS, canonical_table(plugin), table_sha256(plugin), validate_text(text, repo),
validate_eval(path, repo) (each validator returns None or one reason string), and
check_problems(root, plugin) (the list of problem lines).
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FIELDS = ('role', 'level', 'model', 'effort', 'host', 'task_set', 'pass_rate', 'cost_usd', 'date', 'evidence')

EVAL_NAME_RE = re.compile(r'\d{4}-[a-z0-9][a-z0-9-]*\.md')
NUMBER_RE = re.compile(r'(\d{4})-')
SLUG_RE = re.compile(r'[a-z0-9][a-z0-9-]*')
LEVEL_RE = re.compile(r'L\d')
URL_RE = re.compile(r'https?://\S+')
NOT_EVALS = ('AGENTS.md', 'CLAUDE.md')
LOCK_NAME = 'table-lock.json'
LOCK_KEYS = ('eval', 'previous_eval', 'table_sha256')
NAME_HINT = 'not an eval file name (NNNN-<slug>.md)'
RELOCK_HINT = 'add an eval, then run evals.py lock --eval <file>'

SIMPLE = {
    'role': (r'[a-z][a-z-]*', '[a-z][a-z-]*'),
    'level': (r'L[1-5]|all', 'L1 to L5, or all'),
    'model': (r'[A-Za-z0-9][A-Za-z0-9._-]*', '[A-Za-z0-9][A-Za-z0-9._-]*'),
    'effort': (r'[a-z]+', '[a-z]+'),
    'host': (r'claude|codex|all', 'claude, codex, or all'),
    'cost_usd': (r'\d+(\.\d+)?|unknown', 'a non-negative number or unknown'),
}


class TableError(Exception):
    """The model table could not be read or parsed."""


# ---------------------------------------------------------------- table

def canonical_table(plugin):
    """The canonical model table text: sorted levels.json rows, then the compact models.json dump."""
    plugin = Path(plugin)
    levels = plugin / 'adapters' / 'claude' / 'levels.json'
    models = plugin / 'adapters' / 'codex' / 'models.json'
    try:
        table = json.loads(levels.read_text(encoding='utf-8'))
        rows = sorted('%s:%s %s %s' % (role, level, model, effort)
                      for role, by_level in table.items() for level, (model, effort) in by_level.items()
                      if LEVEL_RE.fullmatch(level))
    except (OSError, UnicodeDecodeError, ValueError, AttributeError) as e:
        raise TableError('%s: cannot read: %s' % (levels, e))
    if not rows:
        raise TableError('%s: no role:level model rows parsed' % levels)
    try:
        data = json.loads(models.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise TableError('%s: cannot read: %s' % (models, e))
    return ''.join(r + '\n' for r in rows) + json.dumps(data, sort_keys=True, separators=(',', ':')) + '\n'


def table_sha256(plugin):
    return hashlib.sha256(canonical_table(plugin).encode('utf-8')).hexdigest()


# ---------------------------------------------------------------- format

def parse(text):
    """Split an eval text into (fields, body lines, reason); reason is None when it parsed."""
    lines = text.split('\n')
    if lines[0].rstrip('\r') != '---':
        return None, None, 'no front matter'
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip('\r') == '---':
            end = i
            break
    if end is None:
        return None, None, 'no front matter'
    fields = {}
    for n in range(1, end):
        line = lines[n].rstrip('\r')
        if not line.strip():
            continue
        if ': ' not in line:
            return None, None, 'bad front matter line %d' % (n + 1)
        key, value = line.split(': ', 1)
        key = key.strip()
        if not key:
            return None, None, 'bad front matter line %d' % (n + 1)
        if key in fields:
            return None, None, 'duplicate field %s' % key
        fields[key] = value.strip()
    return fields, [l.rstrip('\r') for l in lines[end + 1:]], None


def evidence_items(value):
    """One bare item, or the items of a one-line [a, b] list; None for an empty list item."""
    if value.startswith('[') and value.endswith(']'):
        items = [i.strip() for i in value[1:-1].split(',')]
        return items if all(items) else None
    return [value]


def field_problem(name, value, repo):
    """The reason a present value is malformed, or None."""
    def bad(shown, want):
        return 'bad field %s: %s (want %s)' % (name, shown, want)
    if '\n' in value or '\r' in value:
        return bad(value.replace('\r', '\\r').replace('\n', '\\n'), 'one line')
    if name in SIMPLE:
        regex, want = SIMPLE[name]
        return None if re.fullmatch(regex, value) else bad(value, want)
    if name == 'task_set':
        if value.startswith('[') and value.endswith(']'):
            return bad(value, 'one line of text, not a list')
        return None
    if name == 'pass_rate':
        m = re.fullmatch(r'(\d+)/(\d+)', value)
        if not m or int(m.group(1)) > int(m.group(2)):
            return bad(value, '<passed>/<total> with passed <= total')
        return None
    if name == 'date':
        try:
            ok = bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value)) and bool(datetime.date.fromisoformat(value))
        except ValueError:
            ok = False
        return None if ok else bad(value, 'YYYY-MM-DD')
    if name == 'evidence':
        items = evidence_items(value)
        if not items:
            return bad(value, 'one item or a one-line [a, b] list of items')
        for item in items:
            if URL_RE.fullmatch(item):
                continue
            parts = re.split(r'[\\/]', item)
            if (item.startswith(('/', '\\')) or os.path.isabs(item) or '..' in parts
                    or not (Path(repo) / item).exists()):
                return bad(item, 'an http(s) URL or an existing repo-relative path without ..')
        return None
    return None


def body_problem(body):
    try:
        m = body.index('## Method')
    except ValueError:
        return 'missing ## Method'
    results = [i for i, l in enumerate(body) if l == '## Result']
    if not results:
        return 'missing ## Result'
    later = [i for i in results if i > m]
    if not later:
        return '## Result before ## Method'
    for label, start in (('Method', m), ('Result', later[0])):
        filled = False
        for line in body[start + 1:]:
            if line.startswith('## '):
                break
            if line.strip():
                filled = True
                break
        if not filled:
            return 'empty ## %s' % label
    return None


def validate_text(text, repo):
    """None when text is a valid eval, else the first reason string."""
    fields, body, reason = parse(text)
    if reason:
        return reason
    for key in fields:
        if key not in FIELDS:
            return 'unknown field %s' % key
    for name in FIELDS:
        value = fields.get(name, '')
        if not value:  # rule: required
            return 'missing field %s' % name
        if value:
            reason = field_problem(name, value, repo)
            if reason:
                return reason
    return body_problem([l.rstrip() for l in body])


def validate_eval(path, repo):
    """None when path is a valid eval file, else the first reason string."""
    path = Path(path)
    if not path.is_file():
        return 'no such file'
    if not EVAL_NAME_RE.fullmatch(path.name):
        return NAME_HINT
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        return 'cannot read: %s' % e
    return validate_text(text, repo)


def eval_date(path):
    fields, _, _ = parse(Path(path).read_text(encoding='utf-8'))
    return fields['date']


# ---------------------------------------------------------------- lock

def not_later(date, old_date):
    """True when date is not later than old_date (ISO dates compare as text)."""
    if date <= old_date:  # rule: date
        return True
    return False


def repo_of(root):
    return Path(root).resolve().parent


def rel(path, repo):
    p = Path(path).resolve()
    try:
        return p.relative_to(repo).as_posix()
    except ValueError:
        return p.as_posix()


def read_lock(path):
    """(lock dict, None) or (None, why it is malformed)."""
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return None, 'not JSON: %s' % e
    if not isinstance(data, dict):
        return None, 'not a JSON object'
    if set(data) != set(LOCK_KEYS):
        return None, 'keys are [%s], want exactly eval, previous_eval, table_sha256' % ', '.join(sorted(data))
    if not isinstance(data['eval'], str):
        return None, 'eval is not a string'
    if not (data['previous_eval'] is None or isinstance(data['previous_eval'], str)):
        return None, 'previous_eval is neither a string nor null'
    sha = data['table_sha256']
    if not (isinstance(sha, str) and re.fullmatch(r'[0-9a-fA-F]{64}', sha)):
        return None, 'table_sha256 is not 64 hex characters'
    return data, None


def target_problem(path, root, repo):
    """Why path cannot be cited: missing, not directly in <root>/evals/, or not a valid eval."""
    path = Path(path)
    if not path.is_file():
        return 'no such file'
    evals_dir = (Path(root) / 'evals').resolve()
    if path.resolve().parent != evals_dir:
        return 'not in %s' % rel(evals_dir, repo)
    return validate_eval(path, repo)


def check_problems(root, plugin):
    """The list of problem lines for <root>/evals and its lock; empty when all is well."""
    root = Path(root)
    repo = repo_of(root)
    evals_dir = root / 'evals'
    if not evals_dir.is_dir():
        return ['%s: missing' % rel(evals_dir, repo)]
    problems = []
    numbers = {}
    for f in sorted(evals_dir.iterdir()):
        if not f.is_file() or f.suffix != '.md' or f.name in NOT_EVALS:
            continue
        subject = rel(f, repo)
        if not EVAL_NAME_RE.fullmatch(f.name):
            problems.append('%s: %s' % (subject, NAME_HINT))
            continue
        reason = validate_eval(f, repo)
        if reason:
            problems.append('%s: %s' % (subject, reason))
        number = f.name[:4]
        if number in numbers:
            problems.append('%s: number %s is used twice' % (subject, number))
        numbers.setdefault(number, f.name)
    lock_path = evals_dir / LOCK_NAME
    subject = rel(lock_path, repo)
    if not lock_path.exists():
        problems.append('%s: missing; %s' % (subject, RELOCK_HINT))
        return problems
    lock, why = read_lock(lock_path)
    if why:
        problems.append('%s: malformed: %s' % (subject, why))
        return problems
    try:
        current = table_sha256(plugin)
    except TableError as e:
        problems.append(str(e))
        current = None
    locked = lock['table_sha256']
    if current is not None:
        if current != locked:  # rule: hash
            problems.append('%s: model table changed: sha256 %s is not the locked %s; %s'
                            % (subject, current, locked, RELOCK_HINT))
    reason = target_problem(repo / lock['eval'], root, repo)
    if reason:
        problems.append('%s: lock names no valid eval: %s: %s' % (subject, lock['eval'], reason))
    previous = lock['previous_eval']
    if previous is not None:
        prev_reason = target_problem(repo / previous, root, repo)
        if prev_reason:
            problems.append('%s: previous_eval %s: %s' % (subject, previous, prev_reason))
        if not reason and not prev_reason:
            d, d0 = eval_date(repo / lock['eval']), eval_date(repo / previous)
            if not_later(d, d0):
                problems.append('%s: eval %s date %s is not later than previous_eval %s date %s; '
                                'a changed table needs a new eval' % (subject, lock['eval'], d, previous, d0))
    return problems


# ---------------------------------------------------------------- commands

def refuse(reason):
    print('evals.py: %s' % reason, file=sys.stderr)
    return 1


def cmd_add(args, root, plugin):
    if not SLUG_RE.fullmatch(args.slug):
        return refuse('bad slug %s' % args.slug)
    given = {
        'role': args.role, 'level': args.level, 'model': args.model, 'effort': args.effort,
        'host': args.host, 'task_set': args.task_set, 'pass_rate': args.pass_rate,
        'cost_usd': args.cost_usd, 'date': args.date, 'evidence': args.evidence,
    }
    repo = repo_of(root)
    lines = ['---']
    for name in FIELDS:
        value = given[name]
        if value is None:
            continue
        for item in (value if name == 'evidence' else [value]):
            if '\n' in item or '\r' in item:
                return refuse(field_problem(name, item, repo))
        if name == 'evidence':
            value = value[0] if len(value) == 1 else '[%s]' % ', '.join(value)
        lines.append('%s: %s' % (name, value))
    lines.append('---')
    method = args.method if args.method is not None else ''
    result = args.result if args.result is not None else ''
    text = '\n'.join(lines) + '\n## Method\n\n' + method + '\n\n## Result\n\n' + result
    if not text.endswith('\n'):
        text += '\n'
    reason = validate_text(text, repo)
    if reason:
        return refuse(reason)
    evals_dir = Path(root) / 'evals'
    highest = -1
    if evals_dir.is_dir():
        for f in evals_dir.iterdir():
            m = NUMBER_RE.match(f.name)
            if m and f.suffix == '.md':
                highest = max(highest, int(m.group(1)))
    if highest >= 9999:
        return refuse('no eval number left in %s' % rel(evals_dir, repo))
    path = evals_dir / ('%04d-%s.md' % (highest + 1, args.slug))
    evals_dir.mkdir(parents=True, exist_ok=True)
    with open(str(path), 'x', encoding='utf-8') as fh:
        fh.write(text)
    print(rel(path, repo))
    return 0


def cmd_list(args, root, plugin):
    repo = repo_of(root)
    evals_dir = Path(root) / 'evals'
    if not evals_dir.is_dir():
        return 0
    for f in sorted(evals_dir.iterdir()):
        if not f.is_file() or not EVAL_NAME_RE.fullmatch(f.name):
            continue
        reason = validate_eval(f, repo)
        if reason:
            print('%s\tinvalid: %s' % (f.name, reason))
            continue
        fields, _, _ = parse(f.read_text(encoding='utf-8'))
        print('\t'.join([f.name] + [fields[k] for k in
                                    ('date', 'host', 'role', 'level', 'model', 'effort', 'pass_rate', 'cost_usd')]))
    return 0


def cmd_check(args, root, plugin):
    problems = check_problems(root, plugin)
    if problems:
        for p in problems:
            print(p)
        print('evals check: FAIL')
        return 1
    evals_dir = Path(root) / 'evals'
    n = sum(1 for f in evals_dir.iterdir() if f.is_file() and EVAL_NAME_RE.fullmatch(f.name))
    lock, _ = read_lock(evals_dir / LOCK_NAME)
    print('evals check: ok (%d evals, lock cites %s)' % (n, lock['eval']))
    return 0


def cmd_lock(args, root, plugin):
    repo = repo_of(root)
    path = Path(args.eval)
    if not path.is_file():
        return refuse('no such eval: %s' % args.eval)
    reason = target_problem(path, root, repo)
    if reason:
        return refuse('%s: %s' % (args.eval, reason))
    lock_path = Path(root) / 'evals' / LOCK_NAME
    subject = rel(lock_path, repo)
    previous = None
    if lock_path.exists():
        lock, why = read_lock(lock_path)
        if why:
            return refuse('%s: malformed: %s' % (subject, why))
        old = lock['eval']
        old_reason = target_problem(repo / old, root, repo)
        if old_reason:
            return refuse('%s: lock names no valid eval: %s: %s' % (subject, old, old_reason))
        d, d0 = eval_date(path), eval_date(repo / old)
        if not_later(d, d0):
            return refuse('eval %s date %s is not later than the cited eval %s date %s; '
                          'a changed table needs a new eval' % (args.eval, d, old, d0))
        previous = old
    try:
        sha = table_sha256(plugin)
    except TableError as e:
        return refuse(str(e))
    lock = {'eval': rel(path, repo), 'previous_eval': previous, 'table_sha256': sha}
    tmp = lock_path.with_name(LOCK_NAME + '.tmp')
    tmp.write_text(json.dumps(lock, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(str(tmp), str(lock_path))
    print('locked %s (table sha256 %s)' % (lock['eval'], sha))
    return 0


def cmd_hash(args, root, plugin):
    try:
        print(table_sha256(plugin))
    except TableError as e:
        return refuse(str(e))
    return 0


# ---------------------------------------------------------------- selftest

def selftest(plugin):
    me = Path(__file__).resolve()
    src_levels = Path(plugin) / 'adapters' / 'claude' / 'levels.json'
    src_models = Path(plugin) / 'adapters' / 'codex' / 'models.json'
    tracked = {}
    violations = []
    runs = [0]
    report = []

    def sha(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def track(p):
        tracked[p] = sha(p)

    track(src_levels)
    track(src_models)

    def project(d):
        d.mkdir(parents=True, exist_ok=True)
        (d / '.sdlc').mkdir()
        (d / 'docs').mkdir()
        (d / 'docs' / 'e.md').write_text('e\n', encoding='utf-8')
        (d / 'plugin' / 'adapters' / 'claude').mkdir(parents=True)
        (d / 'plugin' / 'adapters' / 'codex').mkdir(parents=True)
        shutil.copyfile(str(src_levels), str(d / 'plugin' / 'adapters' / 'claude' / 'levels.json'))
        shutil.copyfile(str(src_models), str(d / 'plugin' / 'adapters' / 'codex' / 'models.json'))
        track(d / 'plugin' / 'adapters' / 'claude' / 'levels.json')
        track(d / 'plugin' / 'adapters' / 'codex' / 'models.json')
        return d

    def ev(d, args, script=None):
        cmd = [sys.executable, str(script or me), '--root', str(d / '.sdlc'), '--plugin', str(d / 'plugin')] + args
        proc = subprocess.run(cmd, cwd=str(d), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True)
        runs[0] += 1
        for p, h in list(tracked.items()):
            now = sha(p)
            if now != h:
                violations.append('%s changed by %s' % (p, ' '.join(args)))
                tracked[p] = now
        return proc.returncode, proc.stdout, proc.stderr

    def change_model_row(d):
        p = d / 'plugin' / 'adapters' / 'claude' / 'levels.json'
        table = json.loads(p.read_text(encoding='utf-8'))
        n = 1 if table['builder']['L1'][0] != 'evals-probe' else 0
        table['builder']['L1'][0] = 'evals-probe'
        p.write_text(json.dumps(table, indent=2) + '\n', encoding='utf-8')
        track(p)
        return n

    defaults = [('role', 'builder'), ('level', 'L2'), ('model', 'opus'), ('effort', 'low'), ('host', 'claude'),
                ('task_set', 'bench'), ('pass_rate', '3/4'), ('cost_usd', '1.5'), ('date', '2026-10-02'),
                ('evidence', 'docs/e.md'), ('method', 'm line'), ('result', 'r line')]

    def add_args(slug, **over):
        out = ['add', slug]
        for k, v in defaults:
            v = over.get(k, v)
            if v is None:
                continue
            for item in (v if isinstance(v, list) else [v]):
                out += ['--' + k.replace('_', '-'), item]
        return out

    def read_json(p):
        return json.loads(p.read_text(encoding='utf-8'))

    def patched(t, key, marker):
        """A copy of this file with the marked rule's condition replaced by False, or (None, why)."""
        pattern = re.compile(r'^([ \t]*)if .+:([ \t]*' + re.escape(marker) + r'[ \t]*)$', re.M)
        text, n = pattern.subn(r'\1if False:\2', me.read_text(encoding='utf-8'))
        if n != 1:
            return None, 'marker %r matched %d lines, want exactly 1' % (marker, n)
        d = t / ('neg-' + key)
        d.mkdir()
        (d / 'evals.py').write_text(text, encoding='utf-8')
        return d / 'evals.py', None

    def case(name, fn):
        misses = []

        def need(cond, detail):
            if not cond:
                misses.append(detail)
        try:
            fn(need)
        except Exception as e:  # a crashed case is a failed case, not a crashed selftest
            misses.append('exception: %r' % (e,))
        report.append((name, misses))

    with tempfile.TemporaryDirectory() as td:
        t = Path(td).resolve()
        a = project(t)
        evals_a = a / '.sdlc' / 'evals'
        lock_a = evals_a / LOCK_NAME
        more = t / 'more'

        def c1(need):
            rc, out, err = ev(a, add_args('first'))
            need(rc == 0 and out.strip() == '.sdlc/evals/0000-first.md', 'add: rc=%d %r %r' % (rc, out, err))
            f = evals_a / '0000-first.md'
            need(f.is_file(), 'no file %s' % f)
            want = ['---', 'role: builder', 'level: L2', 'model: opus', 'effort: low', 'host: claude',
                    'task_set: bench', 'pass_rate: 3/4', 'cost_usd: 1.5', 'date: 2026-10-02',
                    'evidence: docs/e.md', '---', '## Method', '', 'm line', '', '## Result', '', 'r line']
            got = f.read_text(encoding='utf-8').split('\n') if f.is_file() else []
            for i, line in enumerate(want):
                need(i < len(got) and got[i] == line, 'line %d: want %r, got %r' % (i + 1, line, got[i] if i < len(got) else None))
            rc, out, err = ev(a, ['list'])
            need(rc == 0 and out == '0000-first.md\t2026-10-02\tclaude\tbuilder\tL2\topus\tlow\t3/4\t1.5\n',
                 'list: rc=%d %r' % (rc, out))
            rc, out, err = ev(a, ['lock', '--eval', str(f)])
            need(rc == 0, 'lock: rc=%d %r %r' % (rc, out, err))
            lock = read_json(lock_a) if lock_a.exists() else {}
            need(sorted(lock) == sorted(LOCK_KEYS), 'lock keys %r' % sorted(lock))
            need(lock.get('eval') == '.sdlc/evals/0000-first.md' and lock.get('previous_eval', 'x') is None,
                 'lock %r' % lock)
            rc, out, err = ev(a, ['check'])
            need(rc == 0 and out == 'evals check: ok (1 evals, lock cites .sdlc/evals/0000-first.md)\n',
                 'check: rc=%d %r' % (rc, out))
        case('add then list then check pass on a temp project', c1)

        b = project(more / 'b')

        def c2(need):
            for name in FIELDS:
                rc, out, err = ev(b, add_args('x', **{name: None}))
                need(rc == 1 and ('missing field %s' % name) in err, '%s: rc=%d %r' % (name, rc, err))
                need(not (b / '.sdlc' / 'evals').exists(), '%s: wrote .sdlc/evals' % name)
        case('add refuses each missing field by name', c2)

        def c3(need):
            bad = {'role': 'Builder', 'level': 'L6', 'model': '.opus', 'effort': 'High', 'host': 'gcp',
                   'task_set': 'two\nlines', 'pass_rate': '5/4', 'cost_usd': '-1', 'date': '2026-13-01',
                   'evidence': 'docs/nope.md'}
            need(sorted(bad) == sorted(FIELDS), 'bad values do not cover FIELDS')
            for name in FIELDS:
                rc, out, err = ev(b, add_args('x', **{name: bad[name]}))
                need(rc == 1 and ('bad field %s' % name) in err, '%s: rc=%d %r' % (name, rc, err))
                need(not (b / '.sdlc' / 'evals').exists(), '%s: wrote .sdlc/evals' % name)
        case('add refuses each malformed field by name', c3)

        def c4(need):
            rc, out, err = ev(a, add_args('second', date='2026-10-03', evidence=['docs/e.md', 'https://example.com/r']))
            need(rc == 0 and out.strip() == '.sdlc/evals/0001-second.md', 'add: rc=%d %r %r' % (rc, out, err))
            f = evals_a / '0001-second.md'
            text = f.read_text(encoding='utf-8') if f.is_file() else ''
            need('\nevidence: [docs/e.md, https://example.com/r]\n' in text, 'evidence list line missing: %r' % text)
        case('add writes the next number', c4)

        def c5(need):
            d = project(more / 'hand')
            (d / '.sdlc' / 'evals').mkdir()
            (d / '.sdlc' / 'evals' / '0000-hand.md').write_text(
                '---\nrole: builder\nlevel: L1\nmodel: sonnet\neffort: low\ntask_set: s\npass_rate: 1/1\n'
                'cost_usd: unknown\ndate: 2026-10-01\nevidence: docs/e.md\n---\n## Method\n\nm\n\n## Result\n\nr\n',
                encoding='utf-8')
            rc, out, err = ev(d, ['check'])
            need(rc == 1 and '.sdlc/evals/0000-hand.md: missing field host\n' in out
                 and out.endswith('evals check: FAIL\n'), 'check: rc=%d %r' % (rc, out))
        case('check refuses a hand-written eval with a missing field', c5)

        def c6(need):
            n = change_model_row(a)
            need(n == 1, 'changed %d levels.json rows, want 1' % n)
            rc, out, err = ev(a, ['check'])
            need(rc == 1 and 'model table changed' in out, 'check: rc=%d %r' % (rc, out))
        case('a stale lock makes check fail naming the model table', c6)

        def c7(need):
            before = lock_a.read_bytes()
            rc, out, err = ev(a, ['lock'])
            need(rc == 2, 'lock: rc=%d %r' % (rc, err))
            need(lock_a.read_bytes() == before, 'lock changed')
        case('lock without --eval is refused and leaves the lock unchanged', c7)

        def c8(need):
            before = lock_a.read_bytes()
            rc, out, err = ev(a, ['lock', '--eval', str(evals_a / '0000-first.md')])
            need(rc == 1 and 'is not later than' in err, 'lock: rc=%d %r' % (rc, err))
            need(lock_a.read_bytes() == before, 'lock changed')
        case('lock with the cited eval again is refused as not later', c8)

        def c9(need):
            before = lock_a.read_bytes()
            rc, out, err = ev(a, ['lock', '--eval', str(evals_a / '0009-none.md')])
            need(rc == 1 and 'no such eval' in err, 'lock: rc=%d %r' % (rc, err))
            need(lock_a.read_bytes() == before, 'lock changed')
        case('lock with an eval path that does not exist is refused', c9)

        def c10(need):
            rc, out, err = ev(a, ['lock', '--eval', str(evals_a / '0001-second.md')])
            need(rc == 0, 'lock: rc=%d %r' % (rc, err))
            lock = read_json(lock_a)
            need(lock.get('eval') == '.sdlc/evals/0001-second.md', 'eval %r' % lock.get('eval'))
            need(lock.get('previous_eval') == '.sdlc/evals/0000-first.md', 'previous_eval %r' % lock.get('previous_eval'))
            rc, out, err = ev(a, ['hash'])
            need(rc == 0 and lock.get('table_sha256') == out.strip(), 'sha %r vs hash %r' % (lock.get('table_sha256'), out))
            rc, out, err = ev(a, ['check'])
            need(rc == 0 and out == 'evals check: ok (2 evals, lock cites .sdlc/evals/0001-second.md)\n',
                 'check: rc=%d %r' % (rc, out))
        case('lock with a valid newer eval passes and stamps the lock', c10)

        reused = project(more / 'reused')

        def c11(need):
            rc, out, err = ev(reused, add_args('only'))
            need(rc == 0, 'add: rc=%d %r' % (rc, err))
            rc, h, err = ev(reused, ['hash'])
            lock = {'eval': '.sdlc/evals/0000-only.md', 'previous_eval': '.sdlc/evals/0000-only.md',
                    'table_sha256': h.strip()}
            (reused / '.sdlc' / 'evals' / LOCK_NAME).write_text(json.dumps(lock, indent=2, sort_keys=True) + '\n',
                                                                 encoding='utf-8')
            rc, out, err = ev(reused, ['check'])
            need(rc == 1 and 'is not later than previous_eval' in out, 'check: rc=%d %r' % (rc, out))
        case('check refuses a lock whose eval is not later than previous_eval', c11)

        def c12(need):
            d = project(more / 'gone')
            rc, out, err = ev(d, add_args('real'))
            rc, h, err = ev(d, ['hash'])
            lock = {'eval': '.sdlc/evals/0009-missing.md', 'previous_eval': None, 'table_sha256': h.strip()}
            (d / '.sdlc' / 'evals' / LOCK_NAME).write_text(json.dumps(lock) + '\n', encoding='utf-8')
            rc, out, err = ev(d, ['check'])
            need(rc == 1 and 'lock names no valid eval: .sdlc/evals/0009-missing.md: no such file' in out,
                 'check: rc=%d %r' % (rc, out))
        case('check refuses a lock that names a missing eval', c12)

        def c14(need):
            d = project(more / 'stale')
            rc, out, err = ev(d, add_args('base'))
            rc2, out2, err2 = ev(d, ['lock', '--eval', str(d / '.sdlc' / 'evals' / '0000-base.md')])
            need(rc == 0 and rc2 == 0, 'fixture: add rc=%d lock rc=%d %r' % (rc, rc2, err + err2))
            change_model_row(d)
            rc, out, err = ev(d, ['check'])
            need(rc == 1 and 'model table changed' in out, 'real check passed the stale lock: rc=%d %r' % (rc, out))
            copy, why = patched(t, 'hash', '# rule' + ': hash')
            need(copy is not None, str(why))
            if copy:
                rc, out, err = ev(d, ['check'], script=copy)
                need(rc == 0, 'patched check still refused: rc=%d %r' % (rc, out))

        def c15(need):
            copy, why = patched(t, 'date', '# rule' + ': date')
            need(copy is not None, str(why))
            if copy:
                rc, out, err = ev(reused, ['check'], script=copy)
                need(rc == 0, 'patched check still refused: rc=%d %r' % (rc, out))

        def c16(need):
            d = project(more / 'nodate')
            copy, why = patched(t, 'required', '# rule' + ': required')
            need(copy is not None, str(why))
            if copy:
                rc, out, err = ev(d, add_args('x', date=None), script=copy)
                need(rc == 0 and (d / '.sdlc' / 'evals' / '0000-x.md').is_file(),
                     'patched add still refused: rc=%d %r' % (rc, err))

        case('negative control: evals.py without the hash comparison passes a stale lock', c14)
        case('negative control: evals.py without the date rule passes a reused eval', c15)
        case('negative control: evals.py without the required-field check accepts a missing field', c16)

        def c13(need):
            need(runs[0] > 0, 'no command ran')
            for v in violations:
                need(False, v)
        case('evals.py never writes levels.json or models.json', c13)
        report.insert(12, report.pop())  # case 13 runs last so it sees every command, but reports in place

    failed = False
    for name, misses in report:
        if misses:
            failed = True
            for m in misses:
                print('FAIL: %s: %s' % (name, m))
        else:
            print('ok: %s' % name)
    print('evals selftest: %s' % ('FAIL' if failed else 'PASS'))
    return 1 if failed else 0


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser(prog='evals.py', description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.sdlc', help='the .sdlc folder (default: .sdlc in the cwd)')
    ap.add_argument('--plugin', default=str(Path(__file__).resolve().parent.parent),
                    help='dir holding adapters/claude/levels.json and adapters/codex/models.json')
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    p = sub.add_parser('add', help='write the next NNNN-<slug>.md eval')
    p.add_argument('slug')
    for name in FIELDS:
        opt = '--' + name.replace('_', '-')
        if name == 'evidence':
            p.add_argument(opt, action='append', help='a URL or repo-relative path; repeatable')
        else:
            p.add_argument(opt)
    p.add_argument('--method')
    p.add_argument('--result')
    sub.add_parser('list', help='one line per eval')
    sub.add_parser('check', help='validate the evals and the table lock')
    p = sub.add_parser('lock', help='cite an eval for the current model table')
    p.add_argument('--eval', required=True)
    sub.add_parser('hash', help='print the current table sha256')
    sub.add_parser('selftest', help='run the regression cases in temp dirs')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest(args.plugin)
    handler = {'add': cmd_add, 'list': cmd_list, 'check': cmd_check, 'lock': cmd_lock, 'hash': cmd_hash}[args.cmd]
    return handler(args, Path(args.root), Path(args.plugin))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
