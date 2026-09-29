#!/usr/bin/env python3
"""Onboard a repository to SDLC Lite: entry files, docs layout, and check mode.

Usage: onboard.py setup [--dry-run] [--force]   create or update the managed files
       onboard.py check                         report the state of every managed file
       onboard.py selftest                      run the gates on temp fixtures

Design: docs/repo-onboarding/design.md. Standard library only; runs on Python 3.9.

setup --dry-run prints a unified diff of every change on stdout and nothing else, and writes
nothing. setup writes the same changes; --force also replaces a managed block edited by hand.
check writes nothing, prints `<label> <path>` per file, and exits 1 unless every entry file is
current and docs/layout.md is present. Reports (malformed, newer, edited, skipped symbolic
links, size targets) go to stderr. Outside a Git work tree, or on a docs/layout.md parse error,
both commands print the reason to stderr, exit 1, and write nothing.

Importable from the same scripts/ dir: LayoutError, Layout, parse_layout, frozen_match,
scan_lines, has_import, find_block, digest, decide, ROWS, plan, run_setup, run_check.
"""
import argparse
import collections
import contextlib
import difflib
import functools
import hashlib
import io
import itertools
import os
import re
import shutil
import subprocess
import sys
import tempfile

HOMES = '## Homes'
FROZEN = '## Frozen paths'
SECTIONS = (HOMES, FROZEN)

LIST_LINE = re.compile(r'^\s*[-*+]')
HEADING = re.compile(r'^\s{0,3}(#{1,6})(?:\s|$)')
TICKED = r'`([^`]+)`'
HOME_FORM = re.compile(r'^\s*[-*+]\s+`([^`]*/)`(?:\s+takes\s+(' + TICKED + r'(?:\s*,\s*' + TICKED + r')*))?\s*$')
FROZEN_FORM = re.compile(r'^\s*[-*+]\s+' + TICKED + r'\s*$')
FENCE_OPEN = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')

Layout = collections.namedtuple('Layout', 'homes frozen')
Layout.__doc__ = 'homes: dict of home path to a tuple of globs, in file order. frozen: list of patterns.'


class LayoutError(Exception):
    """A layout file that the script must stop on. Carries the file path and a 1-based line."""

    def __init__(self, path, line, reason):
        self.path, self.line, self.reason = str(path), line, reason
        super().__init__('%s:%d: %s' % (self.path, line, reason))


class SetupError(Exception):
    """A repository state that setup and check stop on before writing anything."""


# ---------------------------------------------------------------- layout file

def _split_lines(text):
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return [ln[:-1] if ln.endswith('\r') else ln for ln in lines]


def _parse_layout(path, skip=frozenset()):
    """The parser. `skip` names rules to leave out; only the selftest's defective variants pass it."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    return _parse_layout_text(text, path, skip)


def _parse_layout_text(text, path, skip=frozenset()):
    homes, frozen = {}, []
    seen = {}
    section = None
    n = 0
    for n, (line, fenced) in enumerate(scan_lines(text), 1):
        if fenced:
            continue
        m = HEADING.match(line)
        if m:
            head = line.strip()
            if head in SECTIONS:
                if head in seen and 'duplicate-heading' not in skip:
                    raise LayoutError(path, n, '%r appears twice (first at line %d)' % (head, seen[head]))
                seen.setdefault(head, n)
                section = head
            elif len(m.group(1)) <= 2:
                section = None
            continue
        if section is None or not LIST_LINE.match(line):
            continue
        if section == HOMES:
            m = HOME_FORM.match(line)
            if not m:
                if 'form' in skip:
                    continue
                raise LayoutError(path, n, 'list line under %r is not `<home>/` [takes `<glob>`, ...]' % HOMES)
            home = m.group(1)
            globs = tuple(re.findall(TICKED, m.group(2))) if m.group(2) else ()
            if home in homes and 'duplicate-home' not in skip:
                raise LayoutError(path, n, 'home %r is listed twice' % home)
            homes[home] = globs
        else:
            m = FROZEN_FORM.match(line)
            if not m:
                if 'form' in skip:
                    continue
                raise LayoutError(path, n, 'list line under %r is not one `<glob>`' % FROZEN)
            frozen.append(m.group(1))
    for head in SECTIONS:
        if head not in seen:
            raise LayoutError(path, max(n, 1), 'section heading %r is missing' % head)
    return Layout(homes, frozen)


def parse_layout(path):
    """Parse docs/layout.md into Layout(homes, frozen). Raises LayoutError with file and line."""
    return _parse_layout(path)


def _glob_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out.append('(?:.*/)?')
            i += 3
        elif pattern.startswith('**', i):
            out.append('.*')
            i += 2
        elif pattern[i] == '*':
            out.append('[^/]*')
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return ''.join(out)


def _norm(relpath):
    p = str(relpath).replace(os.sep, '/')
    while p.startswith('./'):
        p = p[2:]
    return p


def frozen_match(pattern, relpath):
    """True when relpath (relative to the repository root) is under the frozen pattern.

    A pattern ending in '/' matches everything under that folder. '*' matches within one path
    segment and '**' matches across segments.
    """
    pattern, relpath = _norm(pattern), _norm(relpath)
    if pattern.endswith('/'):
        rx = '^' + _glob_regex(pattern.rstrip('/')) + '(?:/.*)?$'
    else:
        rx = '^' + _glob_regex(pattern) + '$'
    return re.match(rx, relpath) is not None


def _frozen(patterns, relpath):
    """True when a frozen pattern matches relpath or a folder that holds it."""
    parts = _norm(relpath).split('/')
    paths = ['/'.join(parts[:i]) for i in range(1, len(parts) + 1)]
    return any(frozen_match(p, q) for p in patterns for q in paths)


# ---------------------------------------------------------------- entry files

def scan_lines(text):
    """Yield (line, in_fence) for each line. Fence lines themselves count as inside the fence.

    A fence opens with three or more backticks or tildes after at most three spaces, and closes
    with the same character repeated at least as often and nothing else on the line. An unclosed
    fence runs to the end of the text.
    """
    fence = None
    for line in _split_lines(text):
        if fence is None:
            m = FENCE_OPEN.match(line)
            if m and not (m.group(1)[0] == '`' and '`' in m.group(2)):
                fence = m.group(1)
                yield line, True
                continue
            yield line, False
        else:
            s = line.strip()
            indent = len(line) - len(line.lstrip(' '))
            if indent <= 3 and s and set(s) == {fence[0]} and len(s) >= len(fence):
                fence = None
            yield line, True


IMPORTS = ('@AGENTS.md', '@./AGENTS.md')


def _has_import(text, fences=True):
    for line, fenced in scan_lines(text):
        if fenced and fences:
            continue
        if line.rstrip() in IMPORTS:
            return True
    return False


def has_import(text):
    """True when a line outside any code fence, trailing whitespace removed, imports AGENTS.md."""
    return _has_import(text)


# ---------------------------------------------------------------- templates

TEMPLATE_VERSION = 1

TEMPLATE_START = '<!-- sdlc-lite:managed:start v<N> sha256:<H> -->'
START_MARKER = '<!-- sdlc-lite:managed:start v%d sha256:%s -->'
END_MARKER = '<!-- sdlc-lite:managed:end -->'
START_PREFIX = '<!-- sdlc-lite:managed:start'
END_PREFIX = '<!-- sdlc-lite:managed:end'
START_RE = re.compile(r'<!-- sdlc-lite:managed:start v([0-9]+) sha256:([0-9a-f]{12}) -->\Z')

# The template texts are copied byte for byte from the design's Templates section.
ROOT_AGENTS_TEMPLATE = """\
# <repository folder name>

## What this repository is

## Shared rules

## Checks

<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
## Documents

Read [the docs entry](docs/AGENTS.md) before adding or moving a document.

Managed by SDLC Lite onboard, template <N>.

## Work records

`.sdlc/` holds SDLC Lite tickets, plans, and run records.

- Plan, build, and verify work runs through SDLC Lite: `/sdlc-lite:chain`, `/sdlc-lite:fix`, or `/sdlc-lite:build`, which launch roles with `run.sh`. Do not spawn another plugin's builder, planner, or reviewer agent in their place.
- Handoff files follow the `sdlc-lite:handoff-format` skill.
- Tickets are created, closed, and archived through the `sdlc-lite:ticket` skill.
- `.sdlc/roadmap.md` is generated. Do not edit it by hand.
- Do not move or rewrite a finished run record.
<!-- sdlc-lite:managed:end -->
"""

CLAUDE_TEMPLATE = """\
<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
@AGENTS.md
<!-- sdlc-lite:managed:end -->
"""

DOCS_AGENTS_TEMPLATE = """\
<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
# Documents

## Adding a document

1. Pick the home from [the layout](layout.md).
2. Run the onboard setup again to refresh the links below.
3. Put dated evidence in its own file. Do not add it to an entry file.

## Contents

<one link per topic: to its entry, or to its single document>
<one line per home that exists: a link to its README.md, or the folder name>
<one link per loose document>
<!-- sdlc-lite:managed:end -->
"""

LAYOUT_TEMPLATE = """\
# Layout

Any other folder directly under `docs/` is a topic. It holds the designs, specifications, and decisions for one concept.

## Homes

- `maintenance/`
- `reference/`
- `reports/`

## Frozen paths

- `docs/reports/`
"""

TOPIC_AGENTS_TEMPLATE = """\
# <topic folder name>

Describe what this topic covers.

<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
## Documents

<a link to README.md when it exists, then one link per document>
<!-- sdlc-lite:managed:end -->
"""

PH_TOPICS = '<one link per topic: to its entry, or to its single document>'
PH_HOMES = '<one line per home that exists: a link to its README.md, or the folder name>'
PH_LOOSE = '<one link per loose document>'
PH_TOPIC_DOCS = '<a link to README.md when it exists, then one link per document>'

LAYOUT_PATH = 'docs/layout.md'
NOT_DOCUMENTS = ('AGENTS.md', 'CLAUDE.md', 'README.md')
MARKDOWN = ('.md', '.markdown')
ENTRY_THRESHOLD = 2
ROOT_SIZE_TARGET = 60
NESTED_SIZE_TARGET = 30

Template = collections.namedtuple('Template', 'before block after')
Template.__doc__ = 'One entry file: starter text before the block, the block text, starter text after it.'

Model = collections.namedtuple('Model', 'name topics homes loose')
Model.__doc__ = ('name: repository folder name. topics: list of Topic with one or more documents. '
                 'homes: list of Home that exist. loose: documents directly in docs/.')
Topic = collections.namedtuple('Topic', 'name docs readme')
Home = collections.namedtuple('Home', 'path readme')


def _split_keep(text):
    """Split on LF only, keeping each line's ending. Aligned line for line with scan_lines."""
    return re.findall(r'[^\n]*\n|[^\n]+\Z', text)


def _split_template(text):
    lines = _split_keep(text)
    i = lines.index(TEMPLATE_START + '\n')
    j = lines.index(END_MARKER + '\n')
    return Template(''.join(lines[:i]), ''.join(lines[i + 1:j]), ''.join(lines[j + 1:]))


def _substitute(text, table):
    """Replace each whole placeholder line named in table with zero or more lines."""
    out = []
    for line in _split_keep(text):
        key = line[:-1] if line.endswith('\n') else line
        if key in table:
            out.extend(item + '\n' for item in table[key])
        else:
            out.append(line)
    return ''.join(out)


def _link(text, target):
    text = text.replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')
    if any(c in target for c in ' ()<>'):
        target = '<%s>' % target.replace('<', '%3C').replace('>', '%3E')
    return '- [%s](%s)' % (text, target)


def digest(text):
    """First 12 hex characters of the SHA-256 of text, line endings normalized to LF."""
    data = text.replace('\r\n', '\n').encode('utf-8', 'surrogateescape')
    return hashlib.sha256(data).hexdigest()[:12]


def wrap_block(block):
    """The managed region: start marker (version and hash of block), block, end marker."""
    return START_MARKER % (TEMPLATE_VERSION, digest(block)) + '\n' + block + END_MARKER + '\n'


def render_templates(model):
    """Every entry file for the model, in write order: relpath -> Template."""
    n = str(TEMPLATE_VERSION)
    out = collections.OrderedDict()
    t = _split_template(ROOT_AGENTS_TEMPLATE)
    out['AGENTS.md'] = Template(t.before.replace('<repository folder name>', model.name),
                                t.block.replace('<N>', n), t.after)
    stub = _split_template(CLAUDE_TEMPLATE)
    out['CLAUDE.md'] = stub
    topic_lines, home_lines, loose_lines = [], [], []
    for topic in model.topics:
        if len(topic.docs) >= ENTRY_THRESHOLD:
            topic_lines.append(_link(topic.name + '/', topic.name + '/AGENTS.md'))
        else:
            topic_lines.append(_link(topic.name + '/' + topic.docs[0], topic.name + '/' + topic.docs[0]))
    for home in model.homes:
        if home.readme:
            home_lines.append(_link(home.path, home.path + 'README.md'))
        else:
            home_lines.append('- `%s`' % home.path)
    for doc in model.loose:
        loose_lines.append(_link(doc, doc))
    t = _split_template(DOCS_AGENTS_TEMPLATE)
    out['docs/AGENTS.md'] = Template(t.before, _substitute(
        t.block, {PH_TOPICS: topic_lines, PH_HOMES: home_lines, PH_LOOSE: loose_lines}), t.after)
    out['docs/CLAUDE.md'] = stub
    t = _split_template(TOPIC_AGENTS_TEMPLATE)
    for topic in model.topics:
        if len(topic.docs) < ENTRY_THRESHOLD:
            continue
        links = [_link('README.md', 'README.md')] if topic.readme else []
        links.extend(_link(doc, doc) for doc in topic.docs)
        base = 'docs/%s/' % topic.name
        out[base + 'AGENTS.md'] = Template(t.before.replace('<topic folder name>', topic.name),
                                           _substitute(t.block, {PH_TOPIC_DOCS: links}), t.after)
        out[base + 'CLAUDE.md'] = stub
    return out


# ---------------------------------------------------------------- repository model

def repo_root(cwd=None):
    """`git rev-parse --show-toplevel` from cwd, or None outside a Git work tree."""
    try:
        r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=cwd,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None
    top = r.stdout.decode('utf-8', 'surrogateescape').rstrip('\n')
    return top if r.returncode == 0 and top else None


def list_documents(root):
    """Tracked Markdown files that exist, other than entry files, README.md, and docs/layout.md."""
    try:
        r = subprocess.run(['git', '-C', root, 'ls-files', '-z'],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        raise SetupError('git ls-files failed: %s' % e)
    if r.returncode:
        raise SetupError('git ls-files failed: %s' % r.stderr.decode('utf-8', 'replace').strip())
    docs = []
    for raw in r.stdout.split(b'\0'):
        path = raw.decode('utf-8', 'surrogateescape')
        if not path or not path.lower().endswith(MARKDOWN):
            continue
        if path.rsplit('/', 1)[-1] in NOT_DOCUMENTS or path == LAYOUT_PATH:
            continue
        if os.path.isfile(os.path.join(root, path)):
            docs.append(path)
    return sorted(docs)


def build_model(root, layout, documents):
    """Topics, existing homes, and loose documents, per the design's Definitions."""
    homes = list(layout.homes)
    loose, topics = [], collections.OrderedDict()
    for path in documents:
        if not path.startswith('docs/'):
            continue
        rel = path[len('docs/'):]
        if '/' not in rel:
            loose.append(rel)
            continue
        name = rel.split('/', 1)[0]
        if name + '/' in layout.homes or any(rel.startswith(h) for h in homes):
            continue
        if _frozen(layout.frozen, 'docs/' + name):
            continue
        topics.setdefault(name, []).append(rel[len(name) + 1:])
    topic_list = [Topic(name, sorted(topics[name]),
                        os.path.isfile(os.path.join(root, 'docs', name, 'README.md')))
                  for name in sorted(topics)]
    home_list = [Home(h, os.path.isfile(os.path.join(root, 'docs', h, 'README.md')))
                 for h in homes if os.path.isdir(os.path.join(root, 'docs', h))]
    name = os.path.basename(os.path.normpath(root))
    return Model(name, topic_list, home_list, sorted(loose))


# ---------------------------------------------------------------- managed blocks

Block = collections.namedtuple('Block', 'start end version digest text')
Block.__doc__ = 'start, end: 0-based marker line indexes. text: the bytes between them, LF-normalized.'
Found = collections.namedtuple('Found', 'status block reason')
Found.__doc__ = "status: 'none', 'malformed' (reason set), or 'block' (block set)."


def _find_block(text, fences=True, unclosed=True):
    """The parser. The keyword switches exist only for the selftest's defective variants."""
    marks = []
    for i, (raw, (_, fenced)) in enumerate(zip(_split_keep(text), scan_lines(text))):
        if fenced and fences:
            continue
        line = raw.rstrip()
        if line.startswith(START_PREFIX):
            marks.append(('start', i, line))
        elif line.startswith(END_PREFIX):
            marks.append(('end', i, line))
    if not marks:
        return Found('none', None, None)
    open_at, pairs = None, []
    for kind, i, line in marks:
        if kind == 'start':
            if open_at is not None:
                return Found('malformed', None, 'start marker at line %d has no end marker after it'
                             % (open_at[0] + 1))
            open_at = (i, line)
        else:
            if open_at is None:
                return Found('malformed', None, 'end marker at line %d has no start marker before it' % (i + 1))
            pairs.append((open_at, (i, line)))
            open_at = None
    if open_at is not None:
        if not unclosed and not pairs:
            return Found('none', None, None)
        return Found('malformed', None, 'start marker at line %d has no end marker after it' % (open_at[0] + 1))
    if len(pairs) > 1:
        return Found('malformed', None, 'the file has %d managed blocks' % len(pairs))
    (i, start), (j, end) = pairs[0]
    m = START_RE.match(start)
    if not m:
        return Found('malformed', None, 'start marker at line %d has no version and hash' % (i + 1))
    if end != END_MARKER:
        return Found('malformed', None, 'end marker at line %d is not exactly %s' % (j + 1, END_MARKER))
    body = ''.join(_split_keep(text)[i + 1:j]).replace('\r\n', '\n')
    return Found('block', Block(i, j, int(m.group(1)), m.group(2), body), None)


def find_block(text):
    """The file's managed block. Markers count only as whole lines outside any code fence."""
    return _find_block(text)


# ---------------------------------------------------------------- upsert table

State = collections.namedtuple('State', 'exists found import_only has_import template_block')


def _row_missing(s):
    return not s.exists


def _row_malformed(s):
    return s.found.status == 'malformed'


def _row_newer(s):
    return s.found.status == 'block' and s.found.block.version > TEMPLATE_VERSION


def _row_edited(s):
    return s.found.status == 'block' and digest(s.found.block.text) != s.found.block.digest


def _row_current(s):
    return s.found.status == 'block' and s.found.block.text == s.template_block


def _row_other_block(s):
    return s.found.status == 'block'


def _row_import_only(s):
    return s.found.status == 'none' and s.import_only and s.has_import


def _row_no_block(s):
    return True


# The upsert table, rows 1 to 8, in order. decide() takes the first row that matches.
ROWS = (
    (1, _row_missing),
    (2, _row_malformed),
    (3, _row_newer),
    (4, _row_edited),
    (5, _row_current),
    (6, _row_other_block),
    (7, _row_import_only),
    (8, _row_no_block),
)
ACTIONS = {1: 'create', 2: 'report', 3: 'report', 4: 'report', 5: 'none', 6: 'replace', 7: 'none', 8: 'append'}
LABELS = {1: 'missing', 2: 'malformed', 3: 'newer', 4: 'edited', 5: 'current', 6: 'stale', 7: 'current',
          8: 'unmanaged'}


def decide(state, rows=ROWS):
    """The upsert decision: the number of the first row whose state matches."""
    for row, matches in rows:
        if matches(state):
            return row
    raise AssertionError('no upsert row matched')


# The parts of the implementation that the selftest swaps for defective variants.
Impl = collections.namedtuple('Impl', 'render wrap rows find_block labels preflight')
REAL = Impl(render_templates, wrap_block, ROWS, find_block, LABELS, True)

Change = collections.namedtuple('Change', 'path row action label old new notes')
Change.__doc__ = 'One file. row is None outside the upsert table. old/new are None when not read or not written.'


def _read(full):
    with open(full, 'rb') as f:
        return f.read().decode('utf-8', 'surrogateescape')


def _write(root, path, text):
    full = os.path.join(root, *path.split('/'))
    folder = os.path.dirname(full)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(full, 'wb') as f:
        f.write(text.encode('utf-8', 'surrogateescape'))


def _newline(text):
    m = re.search(r'\r?\n', text)
    return m.group(0) if m else '\n'


def _replace_region(text, block, region):
    """Swap the marker lines and everything between them; bytes outside stay identical."""
    lines = _split_keep(text)
    nl = _newline(text)
    region = region.replace('\n', nl)
    if not lines[block.end].endswith('\n'):
        region = region[:-len(nl)]
    return ''.join(lines[:block.start]) + region + ''.join(lines[block.end + 1:])


def _append_region(text, region):
    """Row 8: existing bytes untouched; a newline ends an unterminated last line first."""
    nl = _newline(text)
    sep = nl if text and not text.endswith('\n') else ''
    return text + sep + region.replace('\n', nl)


def _preflight(root, relpath):
    parts = relpath.split('/')
    for i in range(1, len(parts)):
        folder = os.path.join(root, *parts[:i])
        if os.path.lexists(folder) and not os.path.isdir(folder):
            raise SetupError('%s exists and is not a folder, so %s cannot be written'
                             % ('/'.join(parts[:i]), relpath))
    full = os.path.join(root, *parts)
    if os.path.lexists(full) and not os.path.islink(full) and not os.path.isfile(full):
        raise SetupError('%s exists and is not a regular file' % relpath)


def _size_note(c, text):
    """Size target report for an entry file, or None. Only entry files have a row."""
    if c.row is None or text is None:
        return None
    path = c.path
    lines = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
    target = ROOT_SIZE_TARGET if '/' not in path else NESTED_SIZE_TARGET
    if lines > target:
        return 'size %s: %d lines, over the %d-line target; not trimmed' % (path, lines, target)
    return None


def _entry_change(root, path, tmpl, impl, force):
    full = os.path.join(root, *path.split('/'))
    if os.path.islink(full):
        return Change(path, None, 'skip', 'unmanaged', None, None,
                      ['skipped %s: symbolic link; left unchanged' % path])
    text = _read(full) if os.path.lexists(full) else None
    found = impl.find_block(text) if text is not None else Found('none', None, None)
    whole = tmpl.before + tmpl.block + tmpl.after
    state = State(text is not None, found, whole.strip() in IMPORTS,
                  text is not None and has_import(text), tmpl.block)
    row = decide(state, impl.rows)
    action, notes, new = ACTIONS[row], [], text
    if row == 1:
        new = tmpl.before + impl.wrap(tmpl.block) + tmpl.after
    elif row == 2:
        notes.append('malformed %s: %s; left unchanged' % (path, found.reason))
    elif row == 3:
        notes.append('newer %s: block is template v%d, this plugin writes v%d; left unchanged'
                     % (path, found.block.version, TEMPLATE_VERSION))
    elif row == 4 and force:
        action, new = 'replace', _replace_region(text, found.block, impl.wrap(tmpl.block))
        notes.append('edited %s: replaced a block edited by hand (--force)' % path)
    elif row == 4:
        notes.append('edited %s: the managed block was edited by hand; left unchanged '
                     '(--force replaces it)' % path)
    elif row == 6:
        new = _replace_region(text, found.block, impl.wrap(tmpl.block))
    elif row == 8:
        new = _append_region(text, impl.wrap(tmpl.block))
    return Change(path, row, action, impl.labels[row], text, new, notes)


def plan(root, impl=None, force=False):
    """Every managed file's Change, computed before anything is written.

    Raises LayoutError on a bad docs/layout.md and SetupError on a path that cannot be written.
    """
    impl = impl or REAL
    layout_full = os.path.join(root, 'docs', 'layout.md')
    if os.path.isfile(layout_full):
        try:
            layout = parse_layout(layout_full)
        except UnicodeDecodeError as e:
            raise LayoutError(layout_full, e.object[:e.start].count(b'\n') + 1, 'not valid UTF-8')
    else:
        layout = _parse_layout_text(LAYOUT_TEMPLATE, LAYOUT_PATH)
    model = build_model(root, layout, list_documents(root))
    targets = [(p, t) for p, t in impl.render(model).items() if not _frozen(layout.frozen, p)]
    with_layout = not _frozen(layout.frozen, LAYOUT_PATH)
    if impl.preflight:
        for path in [p for p, _ in targets] + ([LAYOUT_PATH] if with_layout else []):
            _preflight(root, path)
    changes = [_entry_change(root, p, t, impl, force) for p, t in targets]
    if with_layout:
        if os.path.lexists(layout_full):
            changes.append(Change(LAYOUT_PATH, None, 'none', 'present', None, None, []))
        else:
            changes.append(Change(LAYOUT_PATH, None, 'create', 'missing', None, LAYOUT_TEMPLATE, []))
    return changes


def _changed(c):
    return c.new is not None and c.new != c.old


def _diff(path, old, new):
    a = _split_keep(old) if old is not None else []
    lines = difflib.unified_diff(a, _split_keep(new), '/dev/null' if old is None else 'a/' + path, 'b/' + path)
    return ''.join(ln if ln.endswith('\n') else ln + '\n\\ No newline at end of file\n' for ln in lines)


def _plan_or_report(root, impl, force, err):
    try:
        return plan(root, impl, force)
    except LayoutError as e:
        err.write('%s:%d: %s\n' % (LAYOUT_PATH, e.line, e.reason))
    except (SetupError, OSError) as e:
        err.write('onboard.py: %s\n' % e)
    return None


def run_setup(root, impl=None, dry_run=False, force=False, out=None, err=None):
    """setup: print the diff (dry run) or write it. Returns the exit status."""
    impl, out, err = impl or REAL, out or sys.stdout, err or sys.stderr
    changes = _plan_or_report(root, impl, force, err)
    if changes is None:
        return 1
    for c in changes:
        size = _size_note(c, c.new)
        for note in c.notes + ([size] if size else []):
            err.write(note + '\n')
    todo = [c for c in changes if _changed(c)]
    if dry_run:
        for c in todo:
            out.write(_diff(c.path, c.old, c.new))
        return 0
    try:
        for c in todo:
            _write(root, c.path, c.new)
            out.write('%s %s\n' % ('created' if c.old is None else 'updated', c.path))
    except OSError as e:
        err.write('onboard.py: %s\n' % e)
        return 1
    return 0


def run_check(root, impl=None, out=None, err=None):
    """check: one `<label> <path>` line per file; 1 unless all are current or present."""
    impl, out, err = impl or REAL, out or sys.stdout, err or sys.stderr
    changes = _plan_or_report(root, impl, False, err)
    if changes is None:
        return 1
    for c in changes:
        size = _size_note(c, c.old)
        for note in c.notes + ([size] if size else []):
            err.write(note + '\n')
        out.write('%s %s\n' % (c.label, c.path))
    return 0 if all(c.label in ('current', 'present') for c in changes) else 1


# ---------------------------------------------------------------- selftest

class GateFailure(AssertionError):
    pass


def expect(cond, msg):
    if not cond:
        raise GateFailure(msg)


def gate_layout_parsing(parse):
    valid = (
        '# Layout\n\nExplanatory text is ignored.\n\n'
        '## Homes\n\n- `maintenance/`\n* `reference/` takes `*.ref.md`, `api/**`\n  + `reports/`\n\n'
        '## Frozen paths\n\n- `docs/reports/`\n'
        '## Notes\n\n- a list line outside both sections is ignored\n'
    )
    empty = '## Homes\n\n## Frozen paths\n'
    cases = [
        ('no backticks', '## Homes\n- `maintenance/`\n- reference/\n## Frozen paths\n', 3),
        ('duplicate heading', '## Homes\n- `a/`\n## Frozen paths\n## Homes\n', 4),
        ('home twice', '## Homes\n- `a/`\n- `b/`\n- `a/` takes `*.md`\n## Frozen paths\n', 4),
        ('frozen without backticks', '## Homes\n## Frozen paths\n- docs/reports/\n', 3),
        ('missing heading', '## Homes\n- `a/`\n', 2),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        def write(name, text):
            p = os.path.join(tmp, name)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(text)
            return p

        got = parse(write('valid.md', valid))
        expect(got.homes == {'maintenance/': (), 'reference/': ('*.ref.md', 'api/**'), 'reports/': ()},
               'valid homes parsed as %r' % (got.homes,))
        expect(list(got.homes) == ['maintenance/', 'reference/', 'reports/'], 'homes out of file order')
        expect(got.frozen == ['docs/reports/'], 'valid frozen parsed as %r' % (got.frozen,))
        got = parse(write('empty.md', empty))
        expect(got.homes == {} and got.frozen == [], 'empty sections parsed as %r' % (got,))
        for i, (label, text, line) in enumerate(cases):
            path = write('bad%d.md' % i, text)
            try:
                parse(path)
            except LayoutError as e:
                expect(e.line == line, '%s: error at line %s, expected %d' % (label, e.line, line))
                expect(e.path == path, '%s: error names %r, expected %r' % (label, e.path, path))
                continue
            raise GateFailure('%s: parsed without an error' % label)


def gate_import_detection(detect):
    yes = [
        '@AGENTS.md\n',
        '# Title\n\n@./AGENTS.md   \n',
        '```\n@AGENTS.md\n```\n@AGENTS.md\n',
        '~~~~\n```\n~~~~\n@./AGENTS.md\r\n',
    ]
    no = [
        '',
        '```\n@AGENTS.md\n```\n',
        '~~~ md\n@./AGENTS.md\n~~~\n',
        '````\n```\n@AGENTS.md\n````\n',
        '```\n@AGENTS.md\n',
        '  @AGENTS.md\n',
        '@AGENTS.md.bak\n',
        'See @AGENTS.md\n',
    ]
    for text in yes:
        expect(detect(text) is True, 'missed the import in %r' % text)
    for text in no:
        expect(detect(text) is False, 'counted an import in %r' % text)


# Fixtures for the setup and check gates: throwaway Git work trees named `demo`.

ROOT_STARTER = '# demo\n\n## What this repository is\n\n## Shared rules\n\n## Checks\n\n'
ROLE_LINE = "Do not spawn another plugin's builder, planner, or reviewer agent in their place."
STUB = '@AGENTS.md\n'
BASE_FILES = ['AGENTS.md', 'CLAUDE.md', 'docs/AGENTS.md', 'docs/CLAUDE.md', 'docs/layout.md']
RICH_DOCS = {
    'docs/alpha/design.md': '# Design\n',
    'docs/alpha/notes/one.md': '# One\n',
    'docs/alpha/README.md': '# Alpha\n',
    'docs/beta/only.md': '# Only\n',
    'docs/loose.md': '# Loose\n',
    'docs/maintenance/README.md': '# Operating\n',
    'docs/reports/2026-09-29.md': '# Report\n',
}
RICH_CONTENTS = ('- [alpha/](alpha/AGENTS.md)\n- [beta/only.md](beta/only.md)\n'
                 '- [maintenance/](maintenance/README.md)\n- `reports/`\n- [loose.md](loose.md)\n')


def _git(root, *args):
    subprocess.run(('git', '-C', root) + args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _put(root, path, content):
    full = os.path.join(root, *path.split('/'))
    if not os.path.isdir(os.path.dirname(full)):
        os.makedirs(os.path.dirname(full))
    with open(full, 'wb') as f:
        f.write(content if isinstance(content, bytes) else content.encode('utf-8'))


@contextlib.contextmanager
def _fixture(files=None, track=()):
    """A fresh `git init` work tree holding files; paths in track are added to the index."""
    tmp = tempfile.mkdtemp(prefix='onboard-selftest-')
    root = os.path.join(tmp, 'demo')
    try:
        os.mkdir(root)
        _git(root, 'init', '-q')
        for path, content in (files or {}).items():
            _put(root, path, content)
        if track:
            _git(root, 'add', '-f', '--', *track)
        yield root
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _snapshot(root):
    snap = {}
    for folder, dirs, names in os.walk(root):
        rel = os.path.relpath(folder, root).replace(os.sep, '/')
        if rel == '.':
            dirs[:] = [d for d in dirs if d != '.git']
        snap[rel + '/'] = None
        for name in names:
            with open(os.path.join(folder, name), 'rb') as f:
                snap[(name if rel == '.' else rel + '/' + name)] = f.read()
    return snap


def _files(root):
    return sorted(k for k, v in _snapshot(root).items() if v is not None)


def _text(root, path):
    return _read(os.path.join(root, *path.split('/')))


def _call(fn, root, impl, **kw):
    out, err = io.StringIO(), io.StringIO()
    rc = fn(root, impl, out=out, err=err, **kw)
    return rc, out.getvalue(), err.getvalue()


def _region(version, text, digest_of=None):
    """A managed region written by hand: markers around text, hashed from digest_of (default text)."""
    return START_MARKER % (version, digest(text if digest_of is None else digest_of)) + '\n' + text + END_MARKER + '\n'


def _parts(text, what):
    """(bytes before the start marker line, Block, bytes after the end marker line), by the real parser."""
    found = _find_block(text)
    expect(found.status == 'block', '%s: expected one well-formed block, found %s %s'
           % (what, found.status, found.reason or ''))
    lines = _split_keep(text)
    return ''.join(lines[:found.block.start]), found.block, ''.join(lines[found.block.end + 1:])


def _expect_hash(block, what):
    expect(block.version == TEMPLATE_VERSION, '%s: block is v%d, expected v%d' % (what, block.version, TEMPLATE_VERSION))
    expect(block.digest == digest(block.text), '%s: marker hash %s does not match the block text' % (what, block.digest))


def gate_create(impl):
    with _fixture() as root:
        rc, out, err = _call(run_setup, root, impl)
        expect(rc == 0, 'empty fixture: setup exited %d: %s' % (rc, err.strip()))
        expect(_files(root) == sorted(BASE_FILES), 'empty fixture: files are %r' % _files(root))
        before, block, after = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(before == ROOT_STARTER, 'AGENTS.md: starter text is %r' % before)
        expect(after == '', 'AGENTS.md: text after the block: %r' % after)
        _expect_hash(block, 'AGENTS.md')
        for line in ('Read [the docs entry](docs/AGENTS.md) before adding or moving a document.',
                     'Managed by SDLC Lite onboard, template %d.' % TEMPLATE_VERSION, ROLE_LINE):
            expect(line in block.text, 'AGENTS.md: block lacks %r' % line)
        for stub in ('CLAUDE.md', 'docs/CLAUDE.md'):
            expect(_text(root, stub) == _region(TEMPLATE_VERSION, STUB), '%s is %r' % (stub, _text(root, stub)))
        before, block, after = _parts(_text(root, 'docs/AGENTS.md'), 'docs/AGENTS.md')
        expect(before == '' and after == '', 'docs/AGENTS.md: starter text %r %r' % (before, after))
        _expect_hash(block, 'docs/AGENTS.md')
        expect(block.text.startswith('# Documents\n\n## Adding a document\n\n1. Pick the home from [the layout]'
                                     '(layout.md).\n'), 'docs/AGENTS.md: block starts %r' % block.text[:60])
        expect(block.text.endswith('## Contents\n\n'), 'docs/AGENTS.md: contents in an empty fixture: %r'
               % block.text[-80:])
        expect(_text(root, LAYOUT_PATH) == LAYOUT_TEMPLATE, 'docs/layout.md is not the default layout')
        layout = parse_layout(os.path.join(root, 'docs', 'layout.md'))
        expect(list(layout.homes) == ['maintenance/', 'reference/', 'reports/'] and layout.frozen == ['docs/reports/'],
               'default layout parsed as %r' % (layout,))
    untracked = dict(RICH_DOCS, **{'docs/alpha/draft.md': '# Not tracked\n'})
    with _fixture(untracked, track=sorted(RICH_DOCS)) as root:
        rc, out, err = _call(run_setup, root, impl)
        expect(rc == 0, 'topic fixture: setup exited %d: %s' % (rc, err.strip()))
        want = sorted(BASE_FILES + list(untracked) + ['docs/alpha/AGENTS.md', 'docs/alpha/CLAUDE.md'])
        expect(_files(root) == want, 'topic fixture: files are %r' % _files(root))
        expect('docs/reference/' not in _snapshot(root), 'topic fixture: created an empty folder docs/reference/')
        before, block, after = _parts(_text(root, 'docs/alpha/AGENTS.md'), 'docs/alpha/AGENTS.md')
        expect(before == '# alpha\n\nDescribe what this topic covers.\n\n', 'topic entry starter is %r' % before)
        expect(block.text == '## Documents\n\n- [README.md](README.md)\n- [design.md](design.md)\n'
               '- [notes/one.md](notes/one.md)\n', 'topic entry block is %r' % block.text)
        expect(_text(root, 'docs/alpha/CLAUDE.md') == _region(TEMPLATE_VERSION, STUB), 'topic stub is wrong')
        _, block, _ = _parts(_text(root, 'docs/AGENTS.md'), 'docs/AGENTS.md')
        expect(block.text.endswith('## Contents\n\n' + RICH_CONTENTS), 'docs/AGENTS.md contents: %r'
               % block.text[block.text.find('## Contents'):])
    with _fixture({'docs': 'a regular file named docs\n', 'README.md': '# demo\n'}) as root:
        snap = _snapshot(root)
        rc, out, err = _call(run_setup, root, impl)
        expect(rc != 0, 'docs is a regular file: setup exited 0')
        expect(_snapshot(root) == snap, 'docs is a regular file: the fixture changed')
        expect('docs' in err, 'docs is a regular file: stderr does not name docs: %r' % err)


def gate_preserve(impl):
    older = _region(TEMPLATE_VERSION, 'an older stub\n')
    user = {
        'AGENTS.md': ('# Mine\n\nkeep me\n', '# Mine\n\nkeep me\n', ''),
        'CLAUDE.md': ('# mine, no final newline', '# mine, no final newline\n', ''),
        'docs/AGENTS.md': ('# Docs\r\n\r\nWindows line endings\r\n', '# Docs\r\n\r\nWindows line endings\r\n', ''),
        'docs/CLAUDE.md': ('above\n\n' + older + '\nbelow\n', 'above\n\n', '\nbelow\n'),
        'docs/alpha/AGENTS.md': ('# Alpha by hand\n\n```\n<!-- sdlc-lite:managed:end -->\n```\n',
                                 '# Alpha by hand\n\n```\n<!-- sdlc-lite:managed:end -->\n```\n', ''),
    }
    files = dict((p, v[0]) for p, v in user.items())
    files.update({'docs/alpha/a.md': '# A\n', 'docs/alpha/b.md': '# B\n'})
    with _fixture(files, track=['docs/alpha/a.md', 'docs/alpha/b.md']) as root:
        rc, out, err = _call(run_setup, root, impl)
        expect(rc == 0, 'setup exited %d: %s' % (rc, err.strip()))
        for path, (orig, want_before, want_after) in user.items():
            text = _text(root, path)
            expect(text != orig, '%s: did not gain a block' % path)
            before, block, after = _parts(text, path)
            expect(before == want_before, '%s: bytes before the block are %r, expected %r' % (path, before, want_before))
            expect(after == want_after, '%s: bytes after the block are %r, expected %r' % (path, after, want_after))
        region = _text(root, 'docs/AGENTS.md')[len(user['docs/AGENTS.md'][1]):]
        expect('\n' not in region.replace('\r\n', ''), 'docs/AGENTS.md: block added with LF in a CRLF file')


def gate_idempotence(impl):
    rich = dict(RICH_DOCS)
    rich.update({'AGENTS.md': '# Mine\n\nkeep me\n', 'docs/AGENTS.md': '# Docs\r\n\r\nmine\r\n',
                 'docs/beta/CLAUDE.md': 'not managed, and beta has no entry\n'})
    for label, files, track in (('empty', {}, ()), ('rich', rich, sorted(RICH_DOCS))):
        with _fixture(files, track=track) as root:
            rc, out, err = _call(run_setup, root, impl)
            expect(rc == 0, '%s fixture: first setup exited %d: %s' % (label, rc, err.strip()))
            snap = _snapshot(root)
            rc, out, err = _call(run_setup, root, impl, dry_run=True)
            expect(rc == 0 and out == '', '%s fixture: second dry run printed a diff:\n%s' % (label, out))
            rc, out, err = _call(run_setup, root, impl)
            expect(rc == 0 and out == '', '%s fixture: second setup reported %r' % (label, out))
            expect(_snapshot(root) == snap, '%s fixture: second setup changed the tree' % label)
            rows = dict((c.path, c.row) for c in plan(root, impl) if c.row is not None)
            expect(all(r in (5, 7) for r in rows.values()), '%s fixture: second run rows %r' % (label, rows))


def gate_row_order(impl):
    cases = [
        (1, 'AGENTS.md', None, 'create'),
        (2, 'AGENTS.md', '# x\n' + START_MARKER % (TEMPLATE_VERSION, digest('a\n')) + '\na\n', 'report'),
        (3, 'AGENTS.md', _region(TEMPLATE_VERSION + 1, 'future, and edited\n', 'future\n'), 'report'),
        (4, 'AGENTS.md', _region(TEMPLATE_VERSION, 'edited by hand\n', 'as written\n'), 'report'),
        (5, 'AGENTS.md', 'current', 'none'),
        (6, 'AGENTS.md', 'top\n' + _region(TEMPLATE_VERSION, 'older text\n') + 'bottom\n', 'replace'),
        (7, 'CLAUDE.md', '# mine\n\n@AGENTS.md\n', 'none'),
        (8, 'AGENTS.md', '# mine\n', 'append'),
    ]
    reported = {2: 'malformed', 3: 'newer', 4: 'edited'}
    for row, path, content, action in cases:
        files = {} if content in (None, 'current') else {path: content}
        with _fixture(files) as root:
            if content == 'current':
                _call(run_setup, root, impl)
            before = _snapshot(root)
            got = dict((c.path, c) for c in plan(root, impl))[path]
            expect((got.row, got.action) == (row, action), 'row %d fixture: decided row %s (%s)'
                   % (row, got.row, got.action))
            rc, out, err = _call(run_setup, root, impl)
            expect(rc == 0, 'row %d fixture: setup exited %d: %s' % (row, rc, err.strip()))
            old, new = before.get(path), _snapshot(root).get(path)
            if action in ('report', 'none'):
                expect(new == old, 'row %d fixture: %s changed' % (row, path))
            else:
                expect(new != old, 'row %d fixture: %s did not change' % (row, path))
                _, block, _ = _parts(_text(root, path), path)
                expect('Managed by SDLC Lite onboard' in block.text, 'row %d fixture: block is not current' % row)
            if row in reported:
                expect('%s %s' % (reported[row], path) in err, 'row %d fixture: not reported: %r' % (row, err))
            if row == 4:
                rc, out, err = _call(run_setup, root, impl, force=True)
                _, block, _ = _parts(_text(root, path), path)
                expect(rc == 0 and 'Managed by SDLC Lite onboard' in block.text, 'row 4: --force did not replace')


def gate_malformed_markers(impl):
    old = '# Mine\n\n' + _region(TEMPLATE_VERSION, 'an older block\n') + '\ntail\n'
    with _fixture({'AGENTS.md': old}) as root:
        rc, out, err = _call(run_setup, root, impl)
        before, block, after = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(rc == 0 and before == '# Mine\n\n' and after == '\ntail\n', 'well-formed block: outside bytes changed')
        expect(ROLE_LINE in block.text, 'well-formed block: not replaced with the current template')
        _expect_hash(block, 'AGENTS.md')
    fenced = '# Mine\n\n```markdown\n' + START_MARKER % (TEMPLATE_VERSION, digest('x\n')) + '\nx\n```\n'
    with _fixture({'AGENTS.md': fenced}) as root:
        rc, out, err = _call(run_setup, root, impl)
        text = _text(root, 'AGENTS.md')
        expect(rc == 0 and text.startswith(fenced) and text != fenced,
               'a start marker inside a code fence was not ordinary text: %r' % err)
    start = START_MARKER % (TEMPLATE_VERSION, digest('a\n')) + '\n'
    bad = [
        ('start marker with no end marker', '# Mine\n\n' + start + 'a\n'),
        ('end marker with no start marker', '# Mine\n\na\n' + END_MARKER + '\n'),
        ('two blocks', _region(TEMPLATE_VERSION, 'a\n') + _region(TEMPLATE_VERSION, 'b\n')),
        ('start marker with no hash', '<!-- sdlc-lite:managed:start v1 -->\na\n' + END_MARKER + '\n'),
    ]
    for label, content in bad:
        with _fixture({'AGENTS.md': content}) as root:
            rc, out, err = _call(run_setup, root, impl)
            expect(_text(root, 'AGENTS.md') == content, '%s: the file changed' % label)
            expect('malformed AGENTS.md' in err, '%s: not reported: %r' % (label, err))
            rc, out, err = _call(run_check, root, impl)
            expect(rc != 0 and 'malformed AGENTS.md\n' in out, '%s: check printed %r' % (label, out))


def gate_check_mode(impl):
    with _fixture() as root:
        _call(run_setup, root, impl)
        snap = _snapshot(root)
        rc, out, err = _call(run_check, root, impl)
        want = ['current %s' % p for p in BASE_FILES if p != LAYOUT_PATH] + ['present ' + LAYOUT_PATH]
        expect(rc == 0, 'current fixture: check exited %d:\n%s%s' % (rc, out, err))
        expect(sorted(out.splitlines()) == sorted(want), 'current fixture: check printed %r' % out)
        expect(_snapshot(root) == snap, 'current fixture: check wrote to the tree')

    def stale(root):
        _put(root, 'docs/guide.md', '# Guide\n')
        _git(root, 'add', '-f', '--', 'docs/guide.md')

    def edited(root):
        text = _text(root, 'AGENTS.md')
        _put(root, 'AGENTS.md', text.replace('Do not move or rewrite', 'Please do not move or rewrite'))

    def newer(root):
        _put(root, 'AGENTS.md', _region(TEMPLATE_VERSION + 1, 'from a later plugin\n'))

    cases = [
        ('stale', 'docs/AGENTS.md', stale),
        ('edited', 'AGENTS.md', edited),
        ('missing', 'docs/CLAUDE.md', lambda root: os.remove(os.path.join(root, 'docs', 'CLAUDE.md'))),
        ('missing', LAYOUT_PATH, lambda root: os.remove(os.path.join(root, 'docs', 'layout.md'))),
        ('unmanaged', 'CLAUDE.md', lambda root: _put(root, 'CLAUDE.md', '# mine\n')),
        ('newer', 'AGENTS.md', newer),
        ('malformed', 'AGENTS.md', lambda root: _put(root, 'AGENTS.md', END_MARKER + '\n')),
    ]
    for label, path, mutate in cases:
        with _fixture() as root:
            _call(run_setup, root, impl)
            mutate(root)
            snap = _snapshot(root)
            rc, out, err = _call(run_check, root, impl)
            expect(rc != 0, '%s fixture: check exited 0:\n%s' % (label, out))
            expect('%s %s' % (label, path) in out.splitlines(), '%s fixture: check printed %r' % (label, out))
            expect(_snapshot(root) == snap, '%s fixture: check wrote to the tree' % label)


def _render_without_starter(model):
    return collections.OrderedDict((p, t._replace(before='', after='')) for p, t in render_templates(model).items())


def _render_with_run_counter():
    counter = itertools.count(1)

    def render(model):
        out = render_templates(model)
        t = out['AGENTS.md']
        out['AGENTS.md'] = t._replace(block=t.block + 'Run %d.\n' % next(counter))
        return out
    return render


def _wrap_writing_outside(block):
    return '<!-- written by onboard -->\n' + wrap_block(block)


def _relabel(row, label):
    labels = dict(LABELS)
    labels[row] = label
    return labels


def _swap_rows(rows, a, b):
    rows = list(rows)
    ia = [r for r, _ in rows].index(a)
    ib = [r for r, _ in rows].index(b)
    rows[ia], rows[ib] = rows[ib], rows[ia]
    return tuple(rows)


GATES = [
    ('layout-parsing', gate_layout_parsing, parse_layout, [
        ('skips the list-line form rule', functools.partial(_parse_layout, skip=frozenset({'form'}))),
        ('skips the duplicate heading rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-heading'}))),
        ('skips the duplicate home rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-home'}))),
    ]),
    ('import-detection', gate_import_detection, has_import, [
        ('skips the code fence rule', functools.partial(_has_import, fences=False)),
    ]),
    ('create', gate_create, REAL, [
        ('writes before checking every path', REAL._replace(preflight=False)),
        ('creates files without starter text', REAL._replace(render=_render_without_starter)),
    ]),
    ('preserve', gate_preserve, REAL, [
        ('template variant writes outside the markers', REAL._replace(wrap=_wrap_writing_outside)),
    ]),
    ('idempotence', gate_idempotence, REAL, [
        ('template variant embeds a run counter', REAL._replace(render=_render_with_run_counter())),
    ]),
    ('row-order', gate_row_order, REAL, [
        ('rows 4 and 6 swapped', REAL._replace(rows=_swap_rows(ROWS, 4, 6))),
    ]),
    ('malformed-markers', gate_malformed_markers, REAL, [
        ('treats a start marker with no end as no block',
         REAL._replace(find_block=functools.partial(_find_block, unclosed=False))),
        ('skips the code fence rule', REAL._replace(find_block=functools.partial(_find_block, fences=False))),
    ]),
    ('check-mode', gate_check_mode, REAL, [
        ('labels an edited block current', REAL._replace(labels=_relabel(4, 'current'))),
        ('labels a stale block current', REAL._replace(labels=_relabel(6, 'current'))),
    ]),
]

# Variables that would point the fixtures' git commands at another repository.
GIT_LOCATION_ENV = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY',
                    'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_PREFIX')


def selftest():
    saved = dict((k, os.environ.pop(k)) for k in GIT_LOCATION_ENV if k in os.environ)
    try:
        return _selftest()
    finally:
        os.environ.update(saved)


def _selftest():
    failed = 0
    for name, gate, real, defects in GATES:
        problems = []
        try:
            gate(real)
        except GateFailure as e:
            problems.append('positive failed: %s' % e)
        except Exception as e:  # noqa: BLE001 - a crash is a failure, reported by type
            problems.append('positive crashed: %s: %s' % (type(e).__name__, e))
        for label, variant in defects:
            try:
                gate(variant)
            except GateFailure:
                continue
            except Exception as e:  # noqa: BLE001 - a crash is not a rejection
                problems.append('negative (%s) crashed: %s: %s' % (label, type(e).__name__, e))
                continue
            problems.append('negative (%s) was not rejected' % label)
        if problems:
            failed += 1
            print('gate %s: FAIL %s' % (name, '; '.join(problems)))
        else:
            print('gate %s: positive ok, negative ok' % name)
    return 1 if failed else 0


# ---------------------------------------------------------------- command line

def main(argv=None):
    ap = argparse.ArgumentParser(prog='onboard.py', description=__doc__.split('\n', 1)[0])
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    sp = sub.add_parser('setup', help='create or update the managed files')
    sp.add_argument('--dry-run', action='store_true', help='print the diff of every change and write nothing')
    sp.add_argument('--force', action='store_true', help='replace a managed block edited by hand')
    sub.add_parser('check', help='report the state of every managed file and write nothing')
    sub.add_parser('selftest', help='run the gates on temp fixtures')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError):
            stream.reconfigure(encoding='utf-8', errors='surrogateescape')
    root = repo_root()
    if root is None:
        print('onboard.py %s: not a Git work tree; run it inside the repository' % args.cmd, file=sys.stderr)
        return 1
    if args.cmd == 'setup':
        return run_setup(root, dry_run=args.dry_run, force=args.force)
    return run_check(root)


if __name__ == '__main__':
    sys.exit(main())
