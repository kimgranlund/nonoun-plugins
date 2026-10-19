#!/usr/bin/env python3
"""Deterministic checks for the docs/ folder schema (docs/planning/docs-schema/design.md, Enforcement).

Usage:
  docs_check.py [--root DIR] [--only GROUP_OR_ID[,..]] [--today YYYY-MM-DD]
  docs_check.py next docs/<home>
  docs_check.py grandfather [--write]
  docs_check.py selftest

The check is read-only: it reads the target, writes nothing, calls no model. Prints one line per finding,
`<error|warning> <rule> <path>: <message>`, then a summary; exits 1 when any error was found.
`--only` takes rule ids (D-3) or the groups `docs` (D-*), `goals` (G-*), `boundary` (B-*) and
`standards` (S-*).

The document standards rules S-1 to S-7 have their home in docs/specs/doc-standards/README.md, the
registry. S-2, S-4, S-5 and S-6 apply only to a file that opts in with a `doc-type:` front matter key
(requirements, runbook, policy, report); S-1 is silent without docs/assets/schemas/kpi.json and S-7
is silent without the registry.

The layout comes from docs/layout.md (parsed by onboard.parse_layout). Without that file the
twelve default homes apply. A `## Legacy` glob exempts a path from D-1, D-2, D-3, D-4, D-9, D-10,
D-11, D-12 and B-3a; it never exempts D-5, D-6, B-1a or B-2a. B-1a skips a path inside a report's evidence folder. The registry drift checks R-1 and R-2
belong to onboard.py check, not to this script.

D-12 (T-0620): UPPERCASE names are allowed only for ECOSYSTEM_NAMES and for singletons a `## Kinds` row's form
cell declares (`ROADMAP.md`). A row whose form declares `NNN-slug.md` numbers new files in its home: a file there
without the number is a D-12 warning unless `## Grandfathered` lists it (decisions, goals and kpi keep their own
name rules). `next` prints the next number of such a home and reserves it with a create-only ref under
refs/sdlc/doc-ids/<home>/ (as tickets.py reserves refs/sdlc/ids/), so parallel lanes never share one; it writes that
ref only. `grandfather` is the migrate step: it lists the files the numbered form flags, and with --write appends them
to `## Grandfathered` in docs/layout.md; nothing is renamed. A `## Levels` line (- `D-12` error) raises a rule's
warnings to that level.

A home of kind `work` holds ticket and task records, not documents: D-7, D-9, D-12 and B-1a skip it, and the
record rule B-2a applies instead, as it does under .sdlc/ (ticket and task folders, the record folders, the
entry files and the ROADMAP.md and NOTES.md singletons named by roots.py).
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
import roots  # noqa: E402

DEFAULT_HOMES = ('work', 'specs', 'planning', 'decisions', 'goals', 'kpi', 'references', 'guides', 'reports', 'assets', 'archive', 'other')
ENTRY_FILES = ('AGENTS.md', 'CLAUDE.md', 'README.md')
TOP_FILES = ENTRY_FILES + ('layout.md',)
TOPIC_KINDS = ('specs', 'planning', 'references', 'guides', 'decisions')
PLANNING_STATUS = ('proposed', 'accepted', 'rejected', 'superseded')
DECISION_STATUS = ('proposed', 'accepted', 'superseded')
CLOSED_STATUS = ('accepted', 'rejected', 'superseded')
LEGACY_EXEMPT = ('D-1', 'D-2', 'D-3', 'D-4', 'D-9', 'D-10', 'D-11', 'D-12', 'B-3a')
DATE_IN_NAME = re.compile(r'\d{4}-\d{2}-\d{2}')
GOAL_STATUS = ('proposed', 'active', 'achieved', 'dropped')
KPI_STATUS = ('proposed', 'active', 'retired')
GOAL_REQUIRED = ('id', 'title', 'status', 'owner', 'created', 'kpis')
KPI_REQUIRED = ('id', 'title', 'status', 'owner', 'created', 'unit', 'direction', 'target', 'measure', 'goals')
CONCEPT_NAME = re.compile(r'^(\d{3})-[a-z0-9]+(-[a-z0-9]+)*\.md$')
CONCEPT_ID = {'goals': 'G', 'kpi': 'K'}
GOAL_CLOSED = ('dropped', 'achieved')
KPI_CLOSED = ('retired',)
CONCEPT_AGE_DAYS = 30
KEBAB = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
VERSION_SUFFIX = re.compile(r'-v\d+(\.\d+)*$')
DECISION_NAME = re.compile(r'^(\d{4})-[a-z0-9]+(-[a-z0-9]+)*\.md$')
REPORT_NAME = re.compile(r'^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$')
ECOSYSTEM_NAMES = ('README.md', 'AGENTS.md', 'CLAUDE.md', 'CHANGELOG.md', 'LICENSE', 'CONTRIBUTING.md')
UPPER_STEM = re.compile(r'^[A-Z][A-Z0-9_]*(-[A-Z0-9_]+)*$')
NUMBER_FORM = re.compile(r'`(N{3,})-slug\.md`')
SINGLETON_FORM = re.compile(r'`([A-Z][A-Z0-9_]*(?:-[A-Z0-9_]+)*(?:\.[a-z]+)?)`')
OWN_NAME_RULE = ('decisions', 'goals', 'kpi', 'work')  # kinds whose file names another rule already checks
NUMBER_WIDTH = {'decisions': 4, 'goals': 3, 'kpi': 3}
DOC_ID_REFS = 'refs/sdlc/doc-ids/'
LINK = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
GENERATED_NAME = re.compile(r'^(runs\.jsonl|skips\.md|budget-ack\.md|[a-z][a-z-]*-L\d(-\d+)?\.md|.*\.attempt\.json|.*\.request\.json|.*\.running|.*\.log)$')
RETRY_NAME = re.compile(r'^[a-z][a-z-]*-L\d-\d+\.md$')
SDLC_RECORD_DIRS = ('tickets', 'work', 'notes', 'messages', 'evals', 'proposals', 'supervisor', '_templates', 'decompose')
SDLC_LOOSE_MD = ('AGENTS.md', 'CLAUDE.md', 'notes.md', 'roadmap.md', 'board.md')
TICKET_DIR = re.compile(r'^\.?\d{4}-')
WORK_RECORD_DIRS = ('archive', 'evals', 'proposals')
WORK_LOOSE_MD = ENTRY_FILES + (roots.ROADMAP, roots.NOTES)
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


def grandfathered(layout, rel):
    return any(onboard.frozen_match(p, rel) or onboard.frozen_match(p, 'docs/' + rel) for p in layout.grandfathered)


def number_width(layout, name):
    """Digits a home's Kinds row form declares (`NNN-slug.md` -> 3), or None when it declares no numbered form."""
    m = NUMBER_FORM.search(layout.kinds.get(name + '/', {}).get('form', ''))
    return len(m.group(1)) if m else None


def singletons(layout):
    """Home name -> the UPPERCASE file names its Kinds row form cell declares (`ROADMAP.md`)."""
    return {rid.rstrip('/'): set(SINGLETON_FORM.findall(row.get('form', ''))) for rid, row in layout.kinds.items()}


def record_findings(paths, prefix, record_dirs, loose_md):
    """B-2a over one record home: paths are relative to it, prefix is the home as a finding path."""
    have = set(paths)
    flagged = set()
    out = []
    for rel in paths:
        if not rel.lower().endswith('.md'):
            continue
        if '/' not in rel:
            if rel not in loose_md:
                out.append(Finding('warning', 'B-2a', prefix + rel, 'loose Markdown file outside the record types'))
            continue
        top = rel.split('/', 1)[0]
        if top in record_dirs or TICKET_DIR.match(top) or top.startswith('verify-') or top in flagged:
            continue
        if top + '/handoff.md' in have or any(p.startswith(top + '/step-') for p in paths):
            continue
        flagged.add(top)
        out.append(Finding('warning', 'B-2a', prefix + top + '/',
                           'folder is not a ticket folder, a task folder (handoff.md or step-N/), or a known record folder'))
    return out


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
        return (rule in only or ('docs' in only and rule.startswith('D-')) or ('boundary' in only and rule.startswith('B-'))
                or ('goals' in only and rule.startswith('G-')) or ('standards' in only and rule.startswith('S-')))

    def add(level, rule, rel, message):
        if rule in LEGACY_EXEMPT and legacy_match(layout, rel):
            return
        if level == 'warning' and 'levels' not in disable:
            level = layout.levels.get(rule, level)
        out.append(Finding(level, rule, 'docs/' + rel, message))

    def kind_of(rel):
        return kinds.get(rel.split('/', 1)[0]) if '/' in rel else None

    records = 'work-records' not in disable
    work = lambda rel: records and kind_of(rel) == 'work'  # noqa: E731

    entry = lambda rel: rel.rsplit('/', 1)[-1] in ENTRY_FILES  # noqa: E731
    singles = singletons(layout)
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
                                   'not one of the twelve default homes or a listed home with a ## Kinds row'))
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
        if on('D-9') and top is not None and not base.startswith('.') and not in_ev and not work(rel):
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
        stem, dot, ext = base.rpartition('.')
        if not dot:
            stem, ext = base, ''
        upper = bool(UPPER_STEM.match(stem)) and 'D-12-upper' not in disable
        allowed = upper and (('ecosystem-names' not in disable and base in ECOSYSTEM_NAMES)
                             or ('singletons' not in disable and depth == 1 and base in singles.get(top, ())))
        if on('D-12') and not in_ev and base not in ENTRY_FILES and base not in TOP_FILES and not work(rel) and not allowed:
            problems = []
            if ' ' in base:
                problems.append('has a space')
            if ext != ext.lower():
                problems.append('has an upper-case extension')
            if upper:
                problems.append('is UPPERCASE; only ecosystem names and singletons a layout.md Kinds row declares may be')
            elif not KEBAB.match(stem):
                problems.append('is not lowercase kebab-case')
            if VERSION_SUFFIX.search(stem):
                problems.append('has a version suffix')
            if kind == 'reports' and md(rel) and DATE_IN_NAME.search(base) and not REPORT_NAME.match(base):
                problems.append('report date must lead the name as YYYY-MM-DD-slug.md')
            if kind == 'decisions' and md(rel) and not DECISION_NAME.match(base):
                problems.append('decision name must be NNNN-slug.md')
            for p in problems:
                add('error', 'D-12', rel, 'file name %s' % p)
            width = number_width(layout, top) if top else None
            if ('D-12-numbered' not in disable and width and depth == 1 and md(rel) and kind not in OWN_NAME_RULE
                    and not re.match(r'^\d{%d}-[a-z0-9]+(-[a-z0-9]+)*\.md$' % width, base)
                    and not ('grandfathered' not in disable and grandfathered(layout, rel))):
                add('warning', 'D-12', rel, 'file name must be %s-slug.md: %s/ numbers new files (docs_check.py next docs/%s)'
                    % ('N' * width, top, top))
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
            if len(parts) < 2 or parts[0] not in kinds or entry(rel) or not md(rel) or under(ev, rel) or work(rel):
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
            # a report's evidence folder keeps copies of run output on purpose (the zone D-9 also treats as evidence)
            if work(rel):
                continue
            if GENERATED_NAME.match(rel.rsplit('/', 1)[-1]) and not ('B-1a-evidence' not in disable and under(ev, rel)):
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
        out.extend(record_findings(sdlc, '.sdlc/', SDLC_RECORD_DIRS, SDLC_LOOSE_MD))
        for name in sorted({rel.split('/', 1)[0] for rel in files if work(rel)}):
            inside = [rel[len(name) + 1:] for rel in files if rel.startswith(name + '/')]
            out.extend(record_findings(inside, 'docs/' + name + '/', WORK_RECORD_DIRS, WORK_LOOSE_MD))
    concept_rules(repo, kinds, today, add, on, root)
    standards_rules(repo, kinds, add, on, root)
    out.sort(key=lambda f: (f.rule, f.path, f.message))
    return out


def _plain(fm, key):
    """A front matter value without a trailing `# comment`; '' when the key is absent."""
    return re.sub(r'\s+#.*$', '', fm.get(key, '')).strip()


def _ids(value, letter):
    return re.findall(r'\b%s-\d{3}\b' % letter, value)


def concept_rules(repo, kinds, today, add, on, root):
    """G-1 to G-5 over the goals and kpi homes (docs/specs/repo-onboarding/goals-and-kpi.md, Checks)."""
    homes = {'goals': [], 'kpi': []}
    for rel in repo.docs():
        parts = rel.split('/')
        kind = kinds.get(parts[0])
        if kind in homes and len(parts) >= 2 and rel.lower().endswith('.md') and parts[-1] not in ENTRY_FILES:
            homes[kind].append(rel)
    meta = {}
    for kind, rels in homes.items():
        letter = CONCEPT_ID[kind]
        required = GOAL_REQUIRED if kind == 'goals' else KPI_REQUIRED
        statuses = GOAL_STATUS if kind == 'goals' else KPI_STATUS
        closed = GOAL_CLOSED if kind == 'goals' else KPI_CLOSED
        seen = {}
        for rel in rels:
            fm = front_matter(repo.text('docs/' + rel))
            meta[rel] = fm
            base = rel.rsplit('/', 1)[-1]
            m = CONCEPT_NAME.match(base) if rel.count('/') == 1 else None
            if on('G-1'):
                if not m:
                    add('error', 'G-1', rel, 'name must be NNN-slug.md directly in the folder (three digits, lowercase kebab-case)')
                else:
                    want = '%s-%s' % (letter, m.group(1))
                    if _plain(fm, 'id') != want:
                        add('error', 'G-1', rel, 'id %r does not match the file number, expected %s' % (_plain(fm, 'id'), want))
                    if m.group(1) in seen:
                        add('error', 'G-1', rel, 'number %s is also used by %s' % (m.group(1), seen[m.group(1)]))
                    else:
                        seen[m.group(1)] = rel
            if on('G-2'):
                missing = [k for k in required if not _plain(fm, k)]
                if missing:
                    add('error', 'G-2', rel, 'front matter lacks %s' % ', '.join(missing))
            st = _plain(fm, 'status')
            if on('G-5') and st and st not in statuses:
                add('error', 'G-5', rel, 'status: must be one of %s (found %r)' % ('|'.join(statuses), st))
            if on('G-5') and st in closed:
                stamp = _dates(_plain(fm, 'date')) or _mtime(root, 'docs/' + rel)
                if stamp and (today - stamp).days > CONCEPT_AGE_DAYS:
                    add('warning', 'G-5', rel, 'status %s for more than %d days; move to archive/ and keep the number'
                        % (st, CONCEPT_AGE_DAYS))
            if kind == 'goals' and on('G-4') and st == 'active':
                value = _plain(fm, 'kpis')
                if not _ids(value, 'K') and not re.match(r'^none:\s*\S', value):
                    add('error', 'G-4', rel, 'active goal has no kpis: list and no `none: <reason>`')
    if not on('G-3'):
        return
    by_id = {'goals': {}, 'kpi': {}}
    for kind, rels in homes.items():
        for rel in rels:
            i = _plain(meta[rel], 'id')
            if i:
                by_id[kind].setdefault(i, rel)
    for rel in homes['goals']:
        gid = _plain(meta[rel], 'id')
        for k in _ids(_plain(meta[rel], 'kpis'), 'K'):
            other = by_id['kpi'].get(k)
            if not other:
                add('error', 'G-3', rel, 'kpis: %s has no file in kpi/' % k)
            elif gid and gid not in _ids(_plain(meta[other], 'goals'), 'G'):
                add('error', 'G-3', rel, 'kpis: %s does not list %s back in goals:' % (k, gid))
    for rel in homes['kpi']:
        for g in _ids(_plain(meta[rel], 'goals'), 'G'):
            if g not in by_id['goals']:
                add('error', 'G-3', rel, 'goals: %s has no file in goals/' % g)


STANDARDS_HOME = 'docs/specs/doc-standards'
REGISTRY = STANDARDS_HOME + '/README.md'
KPI_SCHEMA = 'docs/assets/schemas/kpi.json'
REGISTRY_HEADER = ('Type', 'Home', 'Standard', 'Card', 'Template or schema', 'Check', 'Enforcement')
REQ_ID = re.compile(r'^(?:- )?[A-Z][A-Z0-9]*-\d+:')
HEADING = re.compile(r'^#{1,6}(\s|$)')
SHALL = re.compile(r'\bshall\b', re.I)
MODAL = re.compile(r'\b(must|shall|should|may)\b', re.I)
CODE_SPAN = re.compile(r'(`+)(.+?)\1')
NUMBERED = re.compile(r'^\d+\. ')
PATH_SPAN = re.compile(r'^[^\s<*$:]*/[^\s<*$:]*\.[A-Za-z0-9]+$')


def _body(text):
    """(line number, line) for each line outside the front matter and outside fences."""
    rows = list(onboard.scan_lines(text))
    start = 0
    if rows and rows[0][0].strip() == '---':
        for i in range(1, len(rows)):
            if rows[i][0].strip() == '---':
                start = i + 1
                break
    return [(i + 1, line) for i, (line, fenced) in enumerate(rows) if i >= start and not fenced]


def _links(line):
    """Relative link paths in a line: no scheme, no anchor-only, no absolute path."""
    out = []
    for m in LINK.finditer(line):
        target = m.group(1)
        if re.match(r'^[A-Za-z][A-Za-z0-9+.\-]*:', target) or target.startswith('#') or target.startswith('/'):
            continue
        path = re.split(r'[#?]', target, 1)[0]
        if path:
            out.append((target, path))
    return out


def _resolve(folder, path):
    return os.path.normpath(os.path.join(folder, path)).replace(os.sep, '/')


def _cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def standards_rules(repo, kinds, add, on, root):
    """S-1 to S-7, the document standards checks (docs/specs/doc-standards/README.md)."""
    exists = lambda rel: os.path.exists(os.path.join(root, rel))  # noqa: E731
    schema_keys = None
    if on('S-1') and KPI_SCHEMA in repo.files:
        try:
            import json
            schema_keys = [str(k) for k in json.loads(repo.text(KPI_SCHEMA)).get('required', [])]
        except (ValueError, AttributeError):
            add('error', 'S-1', KPI_SCHEMA[len('docs/'):], 'schema is not a JSON object with a required list')
    for rel in repo.docs():
        if not rel.lower().endswith('.md') or '/' not in rel:
            continue
        base = rel.rsplit('/', 1)[-1]
        kind = kinds.get(rel.split('/', 1)[0])
        text = repo.text('docs/' + rel)
        fm = front_matter(text)
        dtype = _plain(fm, 'doc-type')
        if schema_keys and kind == 'kpi' and CONCEPT_NAME.match(base):
            missing = [k for k in schema_keys if k not in fm]
            if missing:
                add('error', 'S-1', rel, 'front matter lacks %s, required by %s' % (', '.join(missing), KPI_SCHEMA))
        if on('S-2') and dtype == 'requirements':
            body = _body(text)
            for i, (n, line) in enumerate(body):
                s = line.lstrip()
                if SHALL.search(line) and not REQ_ID.match(s):
                    add('error', 'S-2', rel, 'line %d has shall but does not start with a stable ID and a colon' % n)
                if not REQ_ID.match(s):
                    continue
                found = False
                for _, nxt in body[i + 1:]:
                    t = nxt.strip()
                    if REQ_ID.match(nxt.lstrip()) or HEADING.match(t):
                        break
                    if t.startswith('Acceptance:'):
                        found = True
                        break
                if not found:
                    add('error', 'S-2', rel, 'requirement on line %d has no Acceptance: line' % n)
        if on('S-3') and kind == 'decisions' and base not in ENTRY_FILES:
            count = sum(1 for _, line in _body(text) if line.rstrip() == '## Decision')
            if count > 1:
                add('error', 'S-3', rel, '%d lines equal to ## Decision; a decision record has one' % count)
        if on('S-4') and dtype == 'runbook':
            if not any(NUMBERED.match(line) for _, line in _body(text)):
                add('error', 'S-4', rel, 'runbook has no numbered step line')
        if on('S-5') and dtype == 'policy':
            for n, line in _body(text):
                words = [w for w in MODAL.findall(CODE_SPAN.sub('', line)) if w != w.upper()]
                if words:
                    add('error', 'S-5', rel, 'line %d uses %s; write normative words in upper case' % (n, ', '.join(words)))
        if on('S-6') and kind == 'reports' and dtype == 'report':
            folder = os.path.dirname('docs/' + rel)
            for n, line in _body(text):
                for target, path in _links(line):
                    if not exists(_resolve(folder, path)):
                        add('error', 'S-6', rel, 'line %d link does not resolve: %s' % (n, target))
                for m in CODE_SPAN.finditer(line):
                    span = m.group(2).strip()
                    if not PATH_SPAN.match(span) or span.startswith(('/', '~')):
                        continue
                    if not exists(_resolve('.', span)) and not exists(_resolve(folder, span)):
                        add('error', 'S-6', rel, 'line %d path does not resolve from the repository root or the report folder: %s'
                            % (n, span))
    if on('S-7') and REGISTRY in repo.files:
        _registry(repo, add, root)


def _registry(repo, add, root):
    """S-7: every card is linked from the registry, its card and assets links resolve, and its rows are well formed."""
    reg = REGISTRY[len('docs/'):]
    body = _body(repo.text(REGISTRY))
    targets = set()
    for n, line in body:
        for target, path in _links(line):
            res = _resolve(STANDARDS_HOME, path)
            targets.add(res)
            card = os.path.dirname(res) == STANDARDS_HOME and res.lower().endswith('.md')
            if (card or res.startswith('docs/assets/')) and not os.path.exists(os.path.join(root, res)):
                add('error', 'S-7', reg, 'line %d link does not resolve: %s' % (n, target))
    for p in repo.files:
        if os.path.dirname(p) == STANDARDS_HOME and p.lower().endswith('.md') and os.path.basename(p) not in ENTRY_FILES:
            if p not in targets:
                add('error', 'S-7', p[len('docs/'):], 'card is not linked from the registry %s' % REGISTRY)
    header = None
    for n, line in body:
        if not line.lstrip().startswith('|'):
            header = None
            continue
        cells = _cells(line)
        if header is None:
            header = cells
            if cells[0] == 'Type' and tuple(cells) != REGISTRY_HEADER:
                add('error', 'S-7', reg, 'line %d registry header must be | %s |' % (n, ' | '.join(REGISTRY_HEADER)))
            continue
        if header[0] != 'Type' or tuple(header) != REGISTRY_HEADER or all(set(c) <= set('-: ') for c in cells):
            continue
        cells = [c.strip('`') for c in cells] + [''] * len(REGISTRY_HEADER)
        check, enforcement = cells[5], cells[6]
        if enforcement not in ('enforced', 'advisory'):
            add('error', 'S-7', reg, 'line %d Enforcement must be enforced or advisory (found %r)' % (n, enforcement))
        elif check == '-' and enforcement != 'advisory':
            add('error', 'S-7', reg, 'line %d has Check - so its Enforcement must be advisory' % n)


def _mtime(root, rel):
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(os.path.join(root, rel)))
    except OSError:
        return None


def retry_counts(root):
    """Role-result retry files under .sdlc/ and docs work homes (records), and elsewhere under docs/ (flagged)."""
    repo = Repo(root)
    kinds, _ = home_kinds(load_layout(root))
    retry = [p for p in repo.files if RETRY_NAME.match(p.rsplit('/', 1)[-1])]
    record = lambda p: p.startswith('.sdlc/') or (p.startswith('docs/') and p.count('/') > 1 and kinds.get(p.split('/')[1]) == 'work')  # noqa: E731
    sdlc = sum(1 for p in retry if record(p))
    docs = sum(1 for p in retry if p.startswith('docs/') and not record(p))
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


# ---------------------------------------------------------------- numbering

class NextError(Exception):
    pass


def next_number(root, folder, reserve=True):
    """The next free number in a numbered home, reserved through a create-only git ref so two lanes never share it.

    folder is the home relative to root (docs/decisions). The candidate is one past the highest number in a file name
    or a held ref of that home; a ref another lane created in between moves it on. Outside git nothing is reserved."""
    name = folder.strip('/')
    if not name.startswith('docs/') or '/' in name[len('docs/'):]:
        raise NextError('%s is not a home directly under docs/' % folder)
    name = name[len('docs/'):]
    layout = load_layout(root)
    kinds, _ = home_kinds(layout)
    if kinds.get(name) == 'work':
        raise NextError('docs/%s/ is a work home: tickets.py new allocates its ids' % name)
    width = number_width(layout, name) or NUMBER_WIDTH.get(kinds.get(name))
    if not width:
        raise NextError('docs/%s/ has no Kinds row whose form declares a numbered name such as `NNN-slug.md`' % name)
    pat = re.compile(r'^(\d{%d})-' % width)
    nums = [int(m.group(1)) for m in (pat.match(p.rsplit('/', 1)[-1]) for p in Repo(root).files
                                      if p.startswith('docs/%s/' % name) and p.count('/') == 2) if m]
    import pathlib
    import tickets  # function-local: tickets.py imports onboard and is large
    git = tickets.ref_git(pathlib.Path(root))
    prefix = DOC_ID_REFS + name + '/'
    if git:
        held = git('for-each-ref', '--format=%(refname)', prefix).stdout.split()
        nums += [int(r[len(prefix):]) for r in held if r[len(prefix):].isdigit()]
    n = max(nums, default=0) + 1
    while reserve and git:
        try:
            if tickets.ref_write(git, prefix + '%0*d' % (width, n), 'docs/%s/%0*d' % (name, width, n)):
                break
        except tickets.Fail as e:
            raise NextError(str(e))
        n += 1
    return '%0*d' % (width, n)


def grandfather(root, write):
    """The migrate step: misnamed files in numbered homes, relative to docs/, that ## Grandfathered does not list yet.
    With write, appends them to docs/layout.md under ## Grandfathered (adding the section when missing)."""
    found = sorted({f.path[len('docs/'):] for f in run(root, only={'D-12'}, disable=('levels',))
                    if f.level == 'warning' and '-slug.md:' in f.message})
    if not found or not write:
        return found
    path = os.path.join(root, onboard.LAYOUT_PATH)
    with open(path, encoding='utf-8') as f:
        text = f.read()
    lines = ''.join('- `%s`\n' % rel for rel in found)
    m = re.search(r'^## Grandfathered[ \t]*\n(?:[ \t]*\n|[ \t]*[-*+].*\n)*', text, re.M)
    if m:
        body = text[m.start():m.end()].rstrip('\n') + '\n'
        text = text[:m.start()] + body + lines + '\n' + text[m.end():].lstrip('\n')
    else:
        text = text.rstrip('\n') + '\n\n## Grandfathered\n\n' + lines
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text.rstrip('\n') + '\n')
    return found


# ---------------------------------------------------------------- selftest

class GateFailure(AssertionError):
    pass


TODAY = datetime.date(2026, 10, 5)
FM_PLAN = '---\nstatus: proposed\n---\n# Plan\n'


def _goal(n, kpis='[K-001]', status='active', owner='kim', extra=''):
    own = 'owner: %s\n' % owner if owner else ''
    return ('---\nid: G-%03d\ntitle: A goal\nstatus: %s\n%screated: 2026-10-05\nkpis: %s\n%s---\n# G\n'
            % (n, status, own, kpis, extra))


def _kpi(n, goals='[G-001]', status='active', extra=''):
    return ('---\nid: K-%03d\ntitle: A measure\nstatus: %s\nowner: kim\ncreated: 2026-10-05\nunit: percent\n'
            'direction: down\ntarget: "<= 5"\nmeasure: python3 x.py\ngoals: %s\n%s---\n# K\n' % (n, status, goals, extra))


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
    _write(root, 'docs/goals/001-first-goal.md', _goal(1))
    _write(root, 'docs/kpi/001-first-kpi.md', _kpi(1))


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
        ('B-1a', w('docs/references/builder-L1-2.md', 'x\n'), 'docs/references/builder-L1-2.md'),
        ('B-1a', w('docs/references/runs.jsonl', 'x\n'), 'docs/references/runs.jsonl'),
        ('B-2a', w('.sdlc/design-notes/review.md', '# R\n'), '.sdlc/design-notes/'),
        ('B-2a', w('.sdlc/stray.md', '# S\n'), '.sdlc/stray.md'),
        ('B-3a', w('docs/specs/cites.md', '[t](../../.sdlc/0001-x/handoff.md)\n'), 'docs/specs/cites.md'),
        ('D-12', many(('docs/decisions/0001-zebra.md', '---\nstatus: accepted\n---\n')), 'docs/decisions/0001-zebra.md'),
        ('G-1', w('docs/goals/fleet.md', _goal(2)), 'docs/goals/fleet.md'),
        ('G-1', w('docs/kpi/002-two.md', _kpi(7)), 'docs/kpi/002-two.md'),
        ('G-1', w('docs/goals/001-other.md', _goal(1)), 'docs/goals/001-other.md'),
        ('G-2', w('docs/goals/002-no-owner.md', _goal(2, kpis='none: not measurable yet', status='proposed', owner='')),
         'docs/goals/002-no-owner.md'),
        ('G-2', w('docs/kpi/002-no-unit.md', _kpi(2, goals='[G-001]').replace('unit: percent\n', '')), 'docs/kpi/002-no-unit.md'),
        ('G-3', w('docs/goals/002-missing-kpi.md', _goal(2, kpis='[K-009]', status='proposed')), 'docs/goals/002-missing-kpi.md'),
        ('G-3', w('docs/kpi/002-missing-goal.md', _kpi(2, goals='[G-009]')), 'docs/kpi/002-missing-goal.md'),
        ('G-3', w('docs/goals/002-no-backlink.md', _goal(2, kpis='[K-001]', status='proposed')), 'docs/goals/002-no-backlink.md'),
        ('G-4', w('docs/goals/002-wish.md', _goal(2, kpis='[]')), 'docs/goals/002-wish.md'),
        ('G-5', w('docs/goals/002-odd.md', _goal(2, kpis='none: later', status='wishful')), 'docs/goals/002-odd.md'),
        ('G-5', w('docs/goals/002-old.md', _goal(2, kpis='none: later', status='dropped', extra='date: 2026-01-01\n')),
         'docs/goals/002-old.md'),
        ('S-1', w(KPI_SCHEMA, '{"required": ["id", "baseline"]}\n'), 'docs/kpi/001-first-kpi.md'),
        ('S-2', w('docs/specs/reqs.md', '---\ndoc-type: requirements\n---\n# R\n\nREQ-1: The tool shall log.\n'),
         'docs/specs/reqs.md'),
        ('S-2', w('docs/specs/reqs.md', '---\ndoc-type: requirements\n---\n# R\n\nThe tool shall log.\n'), 'docs/specs/reqs.md'),
        ('S-3', w('docs/decisions/0002-twice.md', '---\nstatus: accepted\n---\n# D\n\n## Decision\n\nA\n\n## Decision\n\nB\n'),
         'docs/decisions/0002-twice.md'),
        ('S-4', w('docs/guides/deploy.md', '---\ndoc-type: runbook\n---\n# Deploy\n\nRun it.\n'), 'docs/guides/deploy.md'),
        ('S-5', w('docs/guides/access.md', '---\ndoc-type: policy\n---\n# Access\n\nYou must log in.\n'), 'docs/guides/access.md'),
        ('S-6', w('docs/reports/2026-10-06-gone.md', '---\ndoc-type: report\n---\n# G\n\n[x](missing.md)\n'),
         'docs/reports/2026-10-06-gone.md'),
        ('S-6', w('docs/reports/2026-10-06-span.md', '---\ndoc-type: report\n---\n# G\n\nSee `scripts/missing.py`.\n'),
         'docs/reports/2026-10-06-span.md'),
        ('S-7', many((REGISTRY, '# Standards\n\n| Type | Home | Standard | Card | Template or schema | Check | Enforcement |\n'
                                '|---|---|---|---|---|---|---|\n| policy | guides/ | x | - | - | - | enforced |\n')),
         REGISTRY),
        ('S-7', many((REGISTRY, '# Standards\n'), (STANDARDS_HOME + '/policy.md', '# P\n')), STANDARDS_HOME + '/policy.md'),
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
        _write(tmp, '.sdlc/verify-x/verdict.md', '# V\n')  # verifier record folder
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
        _write(tmp, 'docs/reports/2026-10-05-run.md', '# R\n')
        _write(tmp, 'docs/reports/2026-10-05-run/runs.jsonl', 'x\n')
        _write(tmp, 'docs/reports/2026-10-05-run/builder-L1-2.md', '# B\n')
        _write(tmp, 'docs/specs/runs.jsonl', 'x\n')
        got = runner(tmp)
        if any(f.rule == 'B-1a' and f.path.startswith('docs/reports/2026-10-05-run/') for f in got):
            raise GateFailure('a generated name inside a report evidence folder was flagged')
        if not any(f.rule == 'B-1a' and f.path == 'docs/specs/runs.jsonl' for f in got):
            raise GateFailure('a generated name outside an evidence folder was not flagged')
        only = run(tmp, only={'boundary'}, today=TODAY)
        if any(f.rule.startswith('D-') for f in only) or not only:
            raise GateFailure('--only boundary did not select only B rules')


def gate_work_home(runner):
    """Ticket folders and the UPPERCASE singletons under docs/work/ raise nothing; a stray file there is flagged."""
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, 'docs/work/0001-a/handoff.md', '# H\n')
        _write(tmp, 'docs/work/.0002-b/builder-L1-2.md', '# B\n')
        _write(tmp, 'docs/work/ROADMAP.md', '# R\n')
        _write(tmp, 'docs/work/NOTES.md', '# N\n')
        bad = [f.line() for f in runner(tmp) if f.level != 'info']
        if bad:
            raise GateFailure('work records were flagged: %r' % bad)
        _write(tmp, 'docs/work/stray.md', '# S\n')
        if not any(f.path == 'docs/work/stray.md' for f in runner(tmp)):
            raise GateFailure('a stray file under docs/work/ was not flagged')


SPECS_ROW = '| `specs/` | specs | what the system is and must do | plans -> `planning/` | one place to trust | people | kebab-case |'


def _layout(specs_form, tail=''):
    """The default layout with the specs/ row's form cell replaced, plus extra sections."""
    text = onboard.LAYOUT_TEMPLATE
    if SPECS_ROW not in text:
        raise GateFailure('the default layout has no specs/ row to edit')
    return text.replace(SPECS_ROW, SPECS_ROW[:-len(' kebab-case |')] + ' %s |' % specs_form) + tail


def gate_numbered(runner):
    """A row's `NNN-slug.md` form numbers new files in its home; a Grandfathered path keeps its name; a Levels line
    raises the warning to an error."""
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, 'docs/layout.md', _layout('`NNN-slug.md`', '\n## Grandfathered\n\n- `specs/api.md`\n'))
        _write(tmp, 'docs/specs/002-numbered.md', '# N\n')
        _write(tmp, 'docs/specs/AGENTS.md', '# S\n')
        bad = [f.line() for f in runner(tmp) if f.level != 'info']
        if bad:
            raise GateFailure('numbered or grandfathered files were flagged: %r' % bad)
        _write(tmp, 'docs/specs/new-thing.md', '# N\n')
        got = [f for f in runner(tmp) if f.rule == 'D-12' and f.path == 'docs/specs/new-thing.md']
        if [f.level for f in got] != ['warning']:
            raise GateFailure('an unnumbered new file gave %r, expected one D-12 warning' % [f.line() for f in got])
        _write(tmp, 'docs/layout.md', _layout('`NNN-slug.md`', '\n## Grandfathered\n\n- `specs/api.md`\n'
                                                               '\n## Levels\n\n- `D-12` error\n'))
        got = [f for f in runner(tmp) if f.rule == 'D-12' and f.path == 'docs/specs/new-thing.md']
        if [f.level for f in got] != ['error']:
            raise GateFailure('a Levels line did not raise D-12: %r' % [f.line() for f in got])


def gate_uppercase(runner):
    """Ecosystem names and singletons a Kinds row declares may be UPPERCASE; any other UPPERCASE stem is D-12."""
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, 'docs/layout.md', _layout('kebab-case, `INDEX.md`'))
        _write(tmp, 'docs/guides/CHANGELOG.md', '# C\n')
        _write(tmp, 'docs/guides/CONTRIBUTING.md', '# C\n')
        _write(tmp, 'docs/guides/AGENTS.md', '# G\n')
        _write(tmp, 'docs/specs/INDEX.md', '# I\n')
        _write(tmp, 'docs/specs/AGENTS.md', '# S\n')
        bad = [f.line() for f in runner(tmp) if f.level != 'info']
        if bad:
            raise GateFailure('ecosystem names or declared singletons were flagged: %r' % bad)
        _write(tmp, 'docs/specs/SPEC.md', '# S\n')
        _write(tmp, 'docs/guides/INDEX.md', '# I\n')
        got = {f.path for f in runner(tmp) if f.rule == 'D-12'}
        for rel in ('docs/specs/SPEC.md', 'docs/guides/INDEX.md'):
            if rel not in got:
                raise GateFailure('an undeclared UPPERCASE name was not flagged: %s' % rel)


def _git_fixture(tmp):
    _clean(tmp)
    subprocess.run(['git', 'init', '-q', tmp], check=True)
    subprocess.run(['git', '-C', tmp, 'add', '-A'], check=True)


def gate_next(alloc):
    """`next` reserves through a create-only ref: two calls never share a number, a held ref is skipped, and a folder
    whose row declares no numbered form is refused."""
    with tempfile.TemporaryDirectory() as tmp:
        _git_fixture(tmp)
        a, b = alloc(tmp, 'docs/decisions'), alloc(tmp, 'docs/decisions')
        if (a, b) != ('0002', '0003'):
            raise GateFailure('two reservations gave %r, expected 0002 and 0003' % ((a, b),))
        blob = subprocess.run(['git', '-C', tmp, 'hash-object', '-w', '--stdin'], input=b'x\n',
                              stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        subprocess.run(['git', '-C', tmp, 'update-ref', DOC_ID_REFS + 'decisions/0004', blob], check=True)
        c = alloc(tmp, 'docs/decisions')
        if c != '0005':
            raise GateFailure('a held ref was not skipped: got %r, expected 0005' % c)
        if alloc(tmp, 'docs/goals') != '002':
            raise GateFailure('goals/ did not allocate a three-digit number after 001')
        try:
            alloc(tmp, 'docs/specs')
        except NextError:
            return
        raise GateFailure('a folder with no numbered form was given a number')


def gate_grandfather(migrate):
    """The migrate step lists every misnamed file in a numbered home under ## Grandfathered, once."""
    with tempfile.TemporaryDirectory() as tmp:
        _clean(tmp)
        _write(tmp, 'docs/layout.md', _layout('`NNN-slug.md`'))
        _write(tmp, 'docs/specs/AGENTS.md', '# S\n')
        _write(tmp, 'docs/specs/002-numbered.md', '# N\n')
        _write(tmp, 'docs/specs/old-name.md', '# O\n')
        if migrate(tmp, True) != ['specs/api.md', 'specs/old-name.md']:
            raise GateFailure('the migrate step did not list the two misnamed files')
        bad = [f.line() for f in run(tmp, today=TODAY) if f.level != 'info']
        if bad:
            raise GateFailure('grandfathered files were still flagged: %r' % bad)
        if migrate(tmp, True):
            raise GateFailure('a second migrate run listed files again')


def _real(root):
    return run(root, today=TODAY)


def _without(rule):
    return lambda root: run(root, today=TODAY, disable=(rule,))


def selftest():
    failed = 0
    gates = [('rules', gate_rules, _real, [('drops %s' % r, _without(r)) for r in sorted({c[0] for c in _cases()})]),
             ('legacy', gate_legacy, _real, [('drops D-3', _without('D-3')), ('drops D-5', _without('D-5'))]),
             ('boundary', gate_boundary, _real, [('drops B-1a', _without('B-1a')), ('drops B-3a', _without('B-3a')),
                                                 ('drops B-2a', _without('B-2a')),
                                                 ('flags an evidence folder', lambda root: run(root, today=TODAY, disable=('B-1a-evidence',)))]),
             ('work-home', gate_work_home, _real, [('drops B-2a', _without('B-2a')),
                                                   ('applies the docs rules to work/', _without('work-records'))]),
             ('numbered', gate_numbered, _real, [('drops the numbered form', _without('D-12-numbered')),
                                                 ('ignores Grandfathered', _without('grandfathered')),
                                                 ('ignores Levels', _without('levels'))]),
             ('uppercase', gate_uppercase, _real, [('treats UPPERCASE names as plain names', _without('D-12-upper')),
                                                   ('drops the ecosystem names', _without('ecosystem-names')),
                                                   ('drops declared singletons', _without('singletons'))]),
             ('grandfather', gate_grandfather, grandfather, [('writes nothing', lambda root, write: grandfather(root, False))]),
             ('next', gate_next, next_number, [('reserves no ref', lambda root, folder: next_number(root, folder, reserve=False))]),
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
    ap.add_argument('cmd', nargs='?', choices=['selftest', 'next', 'grandfather'])
    ap.add_argument('folder', nargs='?', help='next: the numbered home, e.g. docs/decisions')
    ap.add_argument('--write', action='store_true', help='grandfather: append the list to docs/layout.md')
    ap.add_argument('--root', default=None)
    ap.add_argument('--only', default=None, help='comma list of rule ids or the groups docs, goals, boundary and standards')
    ap.add_argument('--today', default=None)
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    root = args.root or onboard.repo_root() or os.getcwd()
    if not os.path.isdir(root):
        sys.stderr.write('docs_check.py: %s is not a directory\n' % root)
        return 2
    try:
        if args.cmd == 'next':
            if not args.folder:
                sys.stderr.write('docs_check.py: next needs a folder, e.g. docs/decisions\n')
                return 2
            print(next_number(root, args.folder))
            return 0
        if args.cmd == 'grandfather':
            for rel in grandfather(root, args.write):
                print('- `%s`' % rel)
            return 0
    except (NextError, onboard.LayoutError) as e:
        sys.stderr.write('docs_check.py: %s\n' % e)
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
        sys.stdout.write('info B-1a: %d role-result retry files under .sdlc/ or a docs work home (they belong there, not flagged), '
                         '%d elsewhere under docs/ (flagged above)\n' % (sd, dc))
    return report(findings, sys.stdout)


if __name__ == '__main__':
    sys.exit(main())
