#!/usr/bin/env python3
"""Deterministic checks for the docs/ folder schema (docs/docs-schema/design.md, Enforcement).

Usage:
  docs_check.py [--root DIR] [--only GROUP_OR_ID[,..]] [--today YYYY-MM-DD]
  docs_check.py selftest

Read-only: reads the target, writes nothing, calls no model. Prints one line per finding,
`<error|warning> <rule> <path>: <message>`, then a summary; exits 1 when any error was found.
`--only` takes rule ids (D-3) or the groups `docs` (D-*) and `boundary` (B-*).

The layout comes from docs/layout.md (parsed by onboard.parse_layout). Without that file the
nine default homes apply. A `## Legacy` glob exempts a path from D-1, D-2, D-3, D-4, D-9, D-10,
D-11, D-12 and B-3a; it never exempts D-5, D-6, B-1a or B-2a. The registry drift checks R-1 and R-2
belong to onboard.py check, not to this script.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import onboard  # noqa: E402

DEFAULT_HOMES = ('specs', 'planning', 'decisions', 'references', 'guides', 'reports', 'assets', 'archive', 'other')
ENTRY_FILES = ('AGENTS.md', 'CLAUDE.md', 'README.md')
TOP_FILES = ENTRY_FILES + ('layout.md',)
TOPIC_KINDS = ('specs', 'planning', 'references', 'guides', 'decisions')
PLANNING_STATUS = ('proposed', 'accepted', 'rejected', 'superseded')
DECISION_STATUS = ('proposed', 'accepted', 'superseded')
CLOSED_STATUS = ('accepted', 'rejected', 'superseded')
LEGACY_EXEMPT = ('D-1', 'D-2', 'D-3', 'D-4', 'D-9', 'D-10', 'D-11', 'D-12', 'B-3a')
DATE_IN_NAME = re.compile(r'\d{4}-\d{2}-\d{2}')
KEBAB = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
VERSION_SUFFIX = re.compile(r'-v\d+(\.\d+)*$')
DECISION_NAME = re.compile(r'^(\d{4})-[a-z0-9]+(-[a-z0-9]+)*\.md$')
REPORT_NAME = re.compile(r'^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$')
LINK = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
GENERATED_NAME = re.compile(r'^(runs\.jsonl|skips\.md|budget-ack\.md|[a-z][a-z-]*-L\d(-\d+)?\.md|.*\.attempt\.json|.*\.request\.json|.*\.running|.*\.log)$')
RETRY_NAME = re.compile(r'^[a-z][a-z-]*-L\d-\d+\.md$')
SDLC_RECORD_DIRS = ('tickets', 'work', 'notes', 'messages', 'evals', 'proposals', 'supervisor', '_templates', 'decompose')
SDLC_LOOSE_MD = ('AGENTS.md', 'CLAUDE.md', 'notes.md', 'roadmap.md', 'board.md')
TICKET_DIR = re.compile(r'^\.?\d{4}-')
PLANNING_AGE_DAYS = 30
OTHER_MAX_AHEAD_DAYS = 90
ENTRY_TARGET_DOCS = 60
ENTRY_TARGET_NESTED = 30
DOC_LINE_LIMIT = 400


class Finding(object):
    def __init__(self, level, rule, path, message):
        self.level, self.rule, self.path, self.message = level, rule, path, message

    def line(self):
        return '%s %s %s: %s' % (self.level, self.rule, self.path, self.message)


def _dates(s):
    try:
        return datetime.date.fromisoformat(s)
    except (TypeError, ValueError):
        return None


def front_matter(text):
    """Flat key: value pairs of a leading --- block; {} when there is none."""
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return {}
    out = {}
    for ln in lines[1:]:
        if ln.strip() == '---':
            return out
        m = re.match(r'^([A-Za-z][\w-]*):\s*(.*?)\s*$', ln)
        if m:
            out[m.group(1)] = m.group(2).strip('"\'')
    return {}


class Repo(object):
    """The files under docs/ (and, for the boundary rules, .sdlc/) of one repository root."""

    def __init__(self, root):
        self.root = root
        self.files = self._list()
        self._text = {}

    def _list(self):
        paths = []
        if os.path.isdir(os.path.join(self.root, '.git')) or os.path.isfile(os.path.join(self.root, '.git')):
            try:
                r = subprocess.run(['git', '-C', self.root, 'ls-files', '-z', '-c', '-o', '--exclude-standard'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if r.returncode == 0:
                    paths = [p.decode('utf-8', 'surrogateescape') for p in r.stdout.split(b'\0') if p]
                    return sorted(p for p in set(paths) if os.path.isfile(os.path.join(self.root, p)))
            except OSError:
                pass
        for base, dirs, names in os.walk(self.root):
            dirs[:] = [d for d in dirs if d != '.git']
            for n in names:
                paths.append(os.path.relpath(os.path.join(base, n), self.root).replace(os.sep, '/'))
        return sorted(paths)

    def text(self, rel):
        if rel not in self._text:
            try:
                with open(os.path.join(self.root, rel), encoding='utf-8') as f:
                    self._text[rel] = f.read()
            except (OSError, UnicodeDecodeError):
                self._text[rel] = ''
        return self._text[rel]

    def docs(self):
        return [p[len('docs/'):] for p in self.files if p.startswith('docs/')]


def load_layout(root):
    path = os.path.join(root, onboard.LAYOUT_PATH)
    if not os.path.isfile(path):
        return onboard.Layout({h + '/': () for h in DEFAULT_HOMES}, [], {}, (), [])
    return onboard.parse_layout(path)


def home_kinds(layout):
    """Top-level folder name -> kind, for the default homes and every listed home with a Kinds row."""
    kinds = {h: h for h in DEFAULT_HOMES}
    custom = []
    for rid, row in layout.kinds.items():
        name = rid.rstrip('/')
        kinds[name] = row['kind']
        if name not in DEFAULT_HOMES:
            custom.append((name, row['kind']))
    return kinds, custom


def legacy_match(layout, rel):
    """rel is relative to docs/. A Legacy glob may be written relative to docs/ or to the repository."""
    for pat in layout.legacy:
        if onboard.frozen_match(pat, rel) or onboard.frozen_match(pat, 'docs/' + rel):
            return True
    return False


def evidence_dirs(files, kinds):
    """Folders named like a sibling report: docs/<reports-home>/.../<stem>/ next to <stem>.md."""
    have = set(files)
    out = set()
    for rel in files:
        parts = rel.split('/')
        if len(parts) < 3 or kinds.get(parts[0]) != 'reports':
            continue
        for i in range(1, len(parts) - 1):
            d = '/'.join(parts[:i + 1])
            if '/'.join(parts[:i] + [parts[i] + '.md']) in have:
                out.add(d)
    return out


def under(dirs, rel):
    return any(rel.startswith(d + '/') for d in dirs)


def _entry_target(rel):
    return ENTRY_TARGET_DOCS if rel == 'AGENTS.md' else ENTRY_TARGET_NESTED


def run(root, only=None, today=None, disable=()):
    """All findings for the repository at root. `disable` is for the selftest's defective variants."""
    repo = Repo(root)
    layout = load_layout(root)
    kinds, custom = home_kinds(layout)
    files = repo.docs()
    ev = evidence_dirs(files, kinds)
    today = today or datetime.date.today()
    out = []

    def on(rule):
        if rule in disable:
            return False
        if only is None:
            return True
        return rule in only or ('docs' in only and rule.startswith('D-')) or ('boundary' in only and rule.startswith('B-'))

    def add(level, rule, rel, message):
        if rule in LEGACY_EXEMPT and legacy_match(layout, rel):
            return
        out.append(Finding(level, rule, 'docs/' + rel, message))

    def kind_of(rel):
        return kinds.get(rel.split('/', 1)[0]) if '/' in rel else None

    entry = lambda rel: rel.rsplit('/', 1)[-1] in ENTRY_FILES  # noqa: E731
    md = lambda rel: rel.lower().endswith('.md')  # noqa: E731

    if on('D-1'):
        seen = set()
        for rel in files:
            if '/' not in rel:
                continue
            top = rel.split('/', 1)[0]
            if top in kinds or top in seen:
                continue
            seen.add(top)
            if any(not legacy_match(layout, r) for r in files if r.startswith(top + '/')):
                out.append(Finding('error', 'D-1', 'docs/' + top + '/',
                                   'not one of the nine default homes or a listed home with a ## Kinds row'))
        for name, kind in custom:
            out.append(Finding('info', 'D-1', 'docs/' + name + '/', 'custom home bound to kind %s' % kind))
    for rel in files:
        top = rel.split('/', 1)[0] if '/' in rel else None
        kind = kind_of(rel)
        base = rel.rsplit('/', 1)[-1]
        depth = rel.count('/')
        text = repo.text('docs/' + rel) if md(rel) else ''
        fm = front_matter(text) if md(rel) else {}
        in_ev = under(ev, rel)
        if on('D-2') and top is None and base not in TOP_FILES:
            add('error', 'D-2', rel, 'file directly in docs/; entry files, README.md and layout.md are the only ones allowed')
        if md(rel) and not entry(rel) and top is not None:
            if on('D-3') and kind == 'reports' and not in_ev:
                if not DATE_IN_NAME.search(base) and not _dates(fm.get('date')):
                    add('error', 'D-3', rel, 'report with no date in the file name and no date: front matter')
            if on('D-4') and kind in ('planning', 'decisions'):
                allowed = PLANNING_STATUS if kind == 'planning' else DECISION_STATUS
                if fm.get('status') not in allowed:
                    add('error', 'D-4', rel, 'status: must be one of %s (found %r)' % ('|'.join(allowed), fm.get('status')))
            if kind == 'other':
                rb = _dates(fm.get('review-by'))
                if on('D-5'):
                    if not fm.get('owner') or not rb:
                        add('error', 'D-5', rel, 'other/ file needs owner: and review-by: YYYY-MM-DD')
                    elif (rb - today).days > OTHER_MAX_AHEAD_DAYS:
                        add('error', 'D-5', rel, 'review-by is more than %d days ahead' % OTHER_MAX_AHEAD_DAYS)
                if on('D-6') and rb and rb < today:
                    add('error', 'D-6', rel, 'past its review-by date %s' % rb.isoformat())
            if on('D-8') and kind == 'planning' and fm.get('status') in CLOSED_STATUS:
                stamp = _dates(fm.get('date')) or _mtime(root, 'docs/' + rel)
                if stamp and (today - stamp).days > PLANNING_AGE_DAYS:
                    add('warning', 'D-8', rel, 'status %s for more than %d days; move to archive/ after its content is promoted'
                        % (fm.get('status'), PLANNING_AGE_DAYS))
        if on('D-9') and top is not None and not base.startswith('.') and not in_ev:
            sm = re.match(r'^(.*)\.(sha256|json)$', base)
            sidecar = bool(sm) and ('docs/' + rel.rsplit('/', 1)[0] + '/' + sm.group(1) + '.md') in repo.files
            if kind == 'assets' and md(rel) and not entry(rel):
                add('error', 'D-9', rel, 'Markdown file in assets/')
            elif kind != 'assets' and not md(rel) and not sidecar:
                add('error', 'D-9', rel, 'non-Markdown file outside assets/ and outside a report evidence folder')
        if on('D-10') and md(rel):
            folder = os.path.dirname(rel)
            for line, fenced in onboard.scan_lines(text):
                if fenced:
                    continue
                for m in LINK.finditer(line):
                    target = m.group(1)
                    if re.match(r'^[A-Za-z][A-Za-z0-9+.\-]*:', target) or target.startswith('#') or target.startswith('/'):
                        continue
                    path = re.split(r'[#?]', target, 1)[0]
                    if not path:
                        continue
                    res = os.path.normpath(os.path.join('docs', folder, path)).replace(os.sep, '/')
                    if res not in repo.files and not os.path.isdir(os.path.join(root, res)):
                        add('warning', 'D-10', rel, 'link does not resolve: %s' % target)
        if on('D-11') and md(rel):
            n = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
            if base == 'AGENTS.md':
                if n > _entry_target(rel):
                    add('warning', 'D-11', rel, 'entry file has %d lines, over its %d-line target' % (n, _entry_target(rel)))
            elif n > DOC_LINE_LIMIT:
                add('warning', 'D-11', rel, 'document has %d lines, over the %d-line soft limit' % (n, DOC_LINE_LIMIT))
        if on('D-12') and not in_ev and base not in ENTRY_FILES and base not in TOP_FILES:
            problems = []
            stem, dot, ext = base.rpartition('.')
            if not dot:
                stem, ext = base, ''
            if ' ' in base:
                problems.append('has a space')
            if ext != ext.lower():
                problems.append('has an upper-case extension')
            if not KEBAB.match(stem):
                problems.append('is not lowercase kebab-case')
            if VERSION_SUFFIX.search(stem):
                problems.append('has a version suffix')
            if kind == 'reports' and md(rel) and DATE_IN_NAME.search(base) and not REPORT_NAME.match(base):
                problems.append('report date must lead the name as YYYY-MM-DD-slug.md')
            if kind == 'decisions' and md(rel) and not DECISION_NAME.match(base):
                problems.append('decision name must be NNNN-slug.md')
            for p in problems:
                add('error', 'D-12', rel, 'file name %s' % p)
            for seg in rel.split('/')[:-1]:
                if not in_ev and not KEBAB.match(seg):
                    add('error', 'D-12', rel, 'folder name %r is not lowercase kebab-case' % seg)
                    break
    if on('D-12'):
        nums = {}
        for rel in files:
            if kinds.get(rel.split('/', 1)[0]) == 'decisions':
                m = DECISION_NAME.match(rel.rsplit('/', 1)[-1])
                if m:
                    nums.setdefault(m.group(1), []).append(rel)
        for n, paths in sorted(nums.items()):
            if len(paths) > 1:
                for rel in paths[1:]:
                    add('error', 'D-12', rel, 'decision number %s is also used by %s' % (n, paths[0]))
    if on('D-7'):
        homes_topics = {}
        for rel in files:
            parts = rel.split('/')
            if len(parts) < 2 or parts[0] not in kinds or entry(rel) or not md(rel) or under(ev, rel):
                continue
            homes_topics.setdefault(parts[0], 0)
            homes_topics[parts[0]] += 1
            if len(parts) >= 3 and kinds[parts[0]] in TOPIC_KINDS:
                key = parts[0] + '/' + parts[1]
                homes_topics[key] = homes_topics.get(key, 0) + 1
        have = set(files)
        for folder, count in sorted(homes_topics.items()):
            if count < onboard.ENTRY_THRESHOLD or onboard._frozen(layout.frozen, 'docs/' + folder):
                continue
            if folder + '/AGENTS.md' not in have and folder + '/CLAUDE.md' not in have:
                out.append(Finding('error', 'D-7', 'docs/' + folder + '/',
                                   '%d documents and no AGENTS.md or CLAUDE.md' % count))
    if on('B-1a'):
        for rel in files:
            if GENERATED_NAME.match(rel.rsplit('/', 1)[-1]):
                add('error', 'B-1a', rel, 'generated-file name under docs/; run output belongs in .sdlc/')
    if on('B-3a'):
        for rel in files:
            if not md(rel):
                continue
            folder = os.path.dirname(rel)
            for line, fenced in onboard.scan_lines(repo.text('docs/' + rel)):
                if fenced:
                    continue
                for m in LINK.finditer(line):
                    target = m.group(1)
                    if re.match(r'^[A-Za-z][A-Za-z0-9+.\-]*:', target) or target.startswith('#'):
                        continue
                    path = re.split(r'[#?]', target, 1)[0]
                    res = os.path.normpath(os.path.join('docs', folder, path.lstrip('/') if path.startswith('/') else path))
                    if res.replace(os.sep, '/').startswith('.sdlc/') or res.replace(os.sep, '/') == '.sdlc':
                        add('warning', 'B-3a', rel, 'docs file links to a path under .sdlc/: %s' % target)
    if on('B-2a'):
        sdlc = [p[len('.sdlc/'):] for p in repo.files if p.startswith('.sdlc/')]
        have = set(sdlc)
        flagged = set()
        for rel in sdlc:
            if not md(rel):
                continue
            if '/' not in rel:
                if rel not in SDLC_LOOSE_MD:
                    out.append(Finding('warning', 'B-2a', '.sdlc/' + rel, 'loose Markdown file outside the record types'))
                continue
            top = rel.split('/', 1)[0]
            if top in SDLC_RECORD_DIRS or TICKET_DIR.match(top) or top in flagged:
                continue
            if top + '/handoff.md' in have or any(p.startswith(top + '/step-') for p in sdlc):
                continue
            flagged.add(top)
            out.append(Finding('warning', 'B-2a', '.sdlc/' + top + '/',
                               'folder is not a ticket folder, a task folder (handoff.md or step-N/), or a known record folder'))
    out.sort(key=lambda f: (f.rule, f.path, f.message))
    return out


def _mtime(root, rel):
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(os.path.join(root, rel)))
    except OSError:
        return None


def retry_counts(root):
    repo = Repo(root)
    sdlc = sum(1 for p in repo.files if p.startswith('.sdlc/') and RETRY_NAME.match(p.rsplit('/', 1)[-1]))
    docs = sum(1 for p in repo.files if p.startswith('docs/') and RETRY_NAME.match(p.rsplit('/', 1)[-1]))
    return sdlc, docs


def report(findings, out):
    errors = [f for f in findings if f.level == 'error']
    warnings = [f for f in findings if f.level == 'warning']
    for f in findings:
        out.write(f.line() + '\n')
    counts = {}
    for f in findings:
        if f.level != 'info':
            counts[f.rule] = counts.get(f.rule, 0) + 1
    out.write('docs_check: %d errors, %d warnings%s\n' % (
        len(errors), len(warnings), (' (' + ', '.join('%s %d' % kv for kv in sorted(counts.items())) + ')') if counts else ''))
    return 1 if errors else 0


# ---------------------------------------------------------------- selftest

class GateFailure(AssertionError):
    pass


TODAY = datetime.date(2026, 10, 5)
FM_PLAN = '---\nstatus: proposed\n---\n# Plan\n'


def _write(root, rel, text=''):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)


def _clean(root):
    _write(root, 'docs/AGENTS.md', '# Docs\n')
    _write(root, 'docs/CLAUDE.md', '@AGENTS.md\n')
    _write(root, 'docs/README.md', '# Docs\n- [spec](specs/api.md)\n')
    _write(root, 'docs/specs/api.md', '# API\n')
    _write(root, 'docs/planning/new-idea.md', FM_PLAN)
    _write(root, 'docs/decisions/0001-use-python.md', '---\nstatus: accepted\n---\n# D\n')
    _write(root, 'docs/references/glossary.md', '# G\n')
    _write(root, 'docs/guides/release.md', '# R\n')
    _write(root, 'docs/reports/2026-10-05-run.md', '# Run\n')
    _write(root, 'docs/reports/2026-10-05-run/log.txt', 'x\n')
    _write(root, 'docs/reports/2026-10-05-run.sha256', 'x\n')
    _write(root, 'docs/assets/pic.png', 'x\n')
    _write(root, 'docs/archive/old.md', '---\nstatus: superseded\n---\n# O\n')
    _write(root, 'docs/other/inbox.md', '---\nowner: kim\nreview-by: 2026-11-01\n---\n# I\n')


def _cases():
    """(rule, setup, expected path) tuples; each setup mutates a clean fixture to break exactly one rule."""
    def w(rel, text=''):
        return lambda root: _write(root, rel, text)

    def many(*pairs):
        def f(root):
            for rel, text in pairs:
                _write(root, rel, text)
        return f

    return [
        ('D-1', w('docs/notes/a.md', '# A\n'), 'docs/notes/'),
        ('D-2', w('docs/loose.md', '# L\n'), 'docs/loose.md'),
        ('D-3', w('docs/reports/summary.md', '# S\n'), 'docs/reports/summary.md'),
        ('D-3', w('docs/reports/nested/summary.md', '# S\n'), 'docs/reports/nested/summary.md'),
        ('D-4', w('docs/planning/no-status.md', '# P\n'), 'docs/planning/no-status.md'),
        ('D-5', w('docs/other/orphan.md', '# O\n'), 'docs/other/orphan.md'),
        ('D-6', w('docs/other/late.md', '---\nowner: kim\nreview-by: 2026-09-01\n---\n'), 'docs/other/late.md'),
        ('D-7', many(('docs/guides/a.md', '# A\n'), ('docs/guides/b.md', '# B\n')), 'docs/guides/'),
        ('D-8', w('docs/planning/done-idea.md', '---\nstatus: accepted\ndate: 2026-01-01\n---\n'), 'docs/planning/done-idea.md'),
        ('D-9', w('docs/specs/diagram.png', 'x\n'), 'docs/specs/diagram.png'),
        ('D-10', w('docs/specs/links.md', '[x](missing.md)\n'), 'docs/specs/links.md'),
        ('D-11', w('docs/specs/long.md', 'x\n' * 401), 'docs/specs/long.md'),
        ('D-12', w('docs/specs/Bad Name.md', '# B\n'), 'docs/specs/Bad Name.md'),
        ('B-1a', w('docs/reports/2026-10-05-run/builder-L1-2.md', 'x\n'), 'docs/reports/2026-10-05-run/builder-L1-2.md'),
        ('B-1a', w('docs/reports/2026-10-05-run/runs.jsonl', 'x\n'), 'docs/reports/2026-10-05-run/runs.jsonl'),
        ('B-2a', w('.sdlc/design-notes/review.md', '# R\n'), '.sdlc/design-notes/'),
        ('B-2a', w('.sdlc/stray.md', '# S\n'), '.sdlc/stray.md'),
        ('B-3a', w('docs/specs/cites.md', '[t](../../.sdlc/0001-x/handoff.md)\n'), 'docs/specs/cites.md'),
        ('D-12', many(('docs/decisions/0001-zebra.md', '---\nstatus: accepted\n---\n')), 'docs/decisions/0001-zebra.md'),
    ]


def gate_rules(runner):
    """Each rule has a positive case; the clean fixture reports nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        got = runner(tmp)
        expect_none = [f.line() for f in got if f.level != 'info']
        if expect_none:
            raise GateFailure('clean fixture reported %r' % expect_none)
    for rule, setup, path in _cases():
        with tempfile.TemporaryDirectory() as tmp:
            _clean(tmp)
            setup(tmp)
            got = [f for f in runner(tmp) if f.rule == rule and f.path == path]
            if not got:
                raise GateFailure('%s: no finding for %s' % (rule, path))


def gate_legacy(runner):
    """A Legacy glob exempts D-3 but never D-5."""
    layout = ('## Homes\n\n- `reports/`\n- `other/`\n\n## Frozen paths\n\n## Legacy\n\n- `reports/old/**`\n- `other/**`\n')
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, 'docs/layout.md', layout)
        _write(tmp, 'docs/reports/old/summary.md', '# S\n')
        _write(tmp, 'docs/other/orphan.md', '# O\n')
        _write(tmp, 'docs/other/late.md', '---\nowner: kim\nreview-by: 2026-09-01\n---\n')
        got = runner(tmp)
        if not any(f.rule == 'D-6' and f.path == 'docs/other/late.md' for f in got):
            raise GateFailure('a Legacy path was exempted from D-6')
        if any(f.path == 'docs/reports/old/summary.md' for f in got):
            raise GateFailure('a Legacy path was not exempted from D-3')
        if not any(f.rule == 'D-5' and f.path == 'docs/other/orphan.md' for f in got):
            raise GateFailure('a Legacy path was exempted from D-5')
        _write(tmp, 'docs/reports/new-summary.md', '# S\n')
        if not any(f.rule == 'D-3' and f.path == 'docs/reports/new-summary.md' for f in runner(tmp)):
            raise GateFailure('a path outside Legacy was exempted from D-3')


def gate_read_only(runner):
    """The run writes nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, 'docs/loose.md', '# L\n')

        def snap():
            return sorted((os.path.relpath(os.path.join(b, n), tmp), os.path.getmtime(os.path.join(b, n)))
                          for b, _, ns in os.walk(tmp) for n in ns)
        before = snap()
        runner(tmp)
        if snap() != before:
            raise GateFailure('the run changed files')


def gate_boundary(runner):
    """Record types in .sdlc/ are clean; Legacy exempts B-3a and never B-1a; retry files under .sdlc/ are not B-1a."""
    layout = '## Homes\n\n- `specs/`\n- `reports/`\n\n## Frozen paths\n\n## Legacy\n\n- `specs/old.md`\n- `reports/old/**`\n'
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, '.sdlc/0001-x/handoff.md', '# H\n')
        _write(tmp, '.sdlc/.0002-y/builder-L1-2.md', '# B\n')
        _write(tmp, '.sdlc/wave-a/step-1/handoff.md', '# H\n')
        _write(tmp, '.sdlc/wave-b/handoff.md', '# H\n')
        _write(tmp, '.sdlc/messages/inbox/m.md', '# M\n')
        _write(tmp, '.sdlc/AGENTS.md', '# A\n')
        _write(tmp, '.sdlc/roadmap.md', '# R\n')
        # layout: topics record folders: ticket-less tasks in work/, the notes file in notes/, each with an entry file
        _write(tmp, '.sdlc/tickets/roadmap.md', '# R\n')
        _write(tmp, '.sdlc/work/AGENTS.md', '# W\n')
        _write(tmp, '.sdlc/work/w1/handoff.md', '# H\n')
        _write(tmp, '.sdlc/notes/AGENTS.md', '# N\n')
        _write(tmp, '.sdlc/notes/notes.md', '# N\n')
        bad = [f.line() for f in runner(tmp) if f.rule.startswith('B-')]
        if bad:
            raise GateFailure('record types were flagged: %r' % bad)
        _write(tmp, 'docs/layout.md', layout)
        _write(tmp, 'docs/specs/old.md', '[t](../../.sdlc/0001-x/handoff.md)\n')
        _write(tmp, 'docs/reports/old/builder-L1.md', '# B\n')
        _write(tmp, 'docs/specs/new.md', '[t](../../.sdlc/0001-x/handoff.md)\n')
        _write(tmp, '.sdlc/loose-folder/a.md', '# A\n')
        got = runner(tmp)
        if not any(f.rule == 'B-3a' and f.path == 'docs/specs/new.md' for f in got):
            raise GateFailure('a docs link into .sdlc/ was not flagged')
        if not any(f.rule == 'B-2a' and f.path == '.sdlc/loose-folder/' for f in got):
            raise GateFailure('a folder outside the record types was not flagged')
        if any(f.rule == 'B-3a' and f.path == 'docs/specs/old.md' for f in got):
            raise GateFailure('a Legacy path was not exempted from B-3a')
        if not any(f.rule == 'B-1a' and f.path == 'docs/reports/old/builder-L1.md' for f in got):
            raise GateFailure('a Legacy path was exempted from B-1a')
        only = run(tmp, only={'boundary'}, today=TODAY)
        if any(f.rule.startswith('D-') for f in only) or not only:
            raise GateFailure('--only boundary did not select only B rules')


def _real(root):
    return run(root, today=TODAY)


def _without(rule):
    return lambda root: run(root, today=TODAY, disable=(rule,))


def selftest():
    failed = 0
    gates = [('rules', gate_rules, _real, [('drops %s' % r, _without(r)) for r in sorted({c[0] for c in _cases()})]),
             ('legacy', gate_legacy, _real, [('drops D-3', _without('D-3')), ('drops D-5', _without('D-5'))]),
             ('boundary', gate_boundary, _real, [('drops B-1a', _without('B-1a')), ('drops B-3a', _without('B-3a')),
                                                 ('drops B-2a', _without('B-2a'))]),
             ('read-only', gate_read_only, _real, [])]
    for name, gate, real, defects in gates:
        problems = []
        try:
            gate(real)
        except GateFailure as e:
            problems.append('positive failed: %s' % e)
        except Exception as e:  # noqa: BLE001
            problems.append('positive crashed: %s: %s' % (type(e).__name__, e))
        for label, variant in defects:
            try:
                gate(variant)
            except GateFailure:
                continue
            except Exception as e:  # noqa: BLE001
                problems.append('negative (%s) crashed: %s: %s' % (label, type(e).__name__, e))
                continue
            problems.append('negative (%s) was not rejected' % label)
        if problems:
            failed += 1
            print('gate %s: FAIL %s' % (name, '; '.join(problems)))
        else:
            print('gate %s: positive ok, negative ok' % name)
    print('docs_check selftest: %s' % ('FAIL' if failed else 'PASS'))
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog='docs_check.py', description=__doc__.split('\n', 1)[0])
    ap.add_argument('cmd', nargs='?', choices=['selftest'])
    ap.add_argument('--root', default=None)
    ap.add_argument('--only', default=None, help='comma list of rule ids or the groups docs and boundary')
    ap.add_argument('--today', default=None)
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    root = args.root or onboard.repo_root() or os.getcwd()
    if not os.path.isdir(root):
        sys.stderr.write('docs_check.py: %s is not a directory\n' % root)
        return 2
    only = set(args.only.split(',')) if args.only else None
    today = _dates(args.today) if args.today else None
    try:
        findings = run(root, only=only, today=today)
    except onboard.LayoutError as e:
        sys.stderr.write('docs_check.py: %s\n' % e)
        return 2
    if only is None or 'boundary' in only or 'B-1a' in only:
        sd, dc = retry_counts(root)
        sys.stdout.write('info B-1a: %d role-result retry files under .sdlc/ (they belong there, not flagged), %d under docs/ (flagged above)\n' % (sd, dc))
    return report(findings, sys.stdout)


if __name__ == '__main__':
    sys.exit(main())
