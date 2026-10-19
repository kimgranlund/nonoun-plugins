#!/usr/bin/env python3
"""Onboard a repository to SDLC Lite: entry files, docs layout, and check mode.

Usage: onboard.py setup [--dry-run] [--force] [--init]   refresh the managed blocks (--init: create them)
       onboard.py check                                  report the state of every managed file
       onboard.py selftest                               run the gates on temp fixtures

Design: docs/specs/repo-onboarding/design.md. Standard library only; runs on Python 3.9.
The .sdlc layout is read through a function-local import of the sibling tickets.py, and the root
block names the resolved roadmap, notes, and archive paths (.sdlc/roadmap.md, .sdlc/notes.md, .sdlc/archive/, or
.sdlc/tickets/roadmap.md, .sdlc/notes/notes.md, .sdlc/work/archive/ with `layout: topics`, or
docs/work/ROADMAP.md, docs/work/NOTES.md, docs/work/archive/ with `work_root: docs/work`), the ticket root, and
the lane root from the sibling wtroot.py (`<bare parent>/lanes/` in a bare clone).

setup refreshes the managed blocks a file already holds and changes nothing else; it lists on
stderr each file --init would create or append a block to. setup --init also creates missing
entry files and docs/layout.md and appends a block to an unmanaged entry file.
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
KINDS = '## Kinds'
DECIDE = '## Decide'
LEGACY = '## Legacy'
LEVELS = '## Levels'
GRANDFATHERED = '## Grandfathered'
CAPS = '## Caps'
OPTIONAL_SECTIONS = (KINDS, DECIDE, LEGACY, LEVELS, GRANDFATHERED, CAPS)
DOC_KINDS = ('work', 'specs', 'planning', 'decisions', 'goals', 'kpi', 'references', 'guides', 'reports', 'assets', 'archive', 'other')
KIND_COLUMNS = ('id', 'kind', 'holds', 'not', 'why', 'writer', 'form', 'life', 'entry', 'read', 'owner')
KIND_REQUIRED = ('id', 'kind', 'holds', 'not', 'why', 'form', 'read')

LIST_LINE = re.compile(r'^\s*[-*+]')
HEADING = re.compile(r'^\s{0,3}(#{1,6})(?:\s|$)')
TICKED = r'`([^`]+)`'
HOME_FORM = re.compile(r'^\s*[-*+]\s+`([^`]*/)`(?:\s+takes\s+(' + TICKED + r'(?:\s*,\s*' + TICKED + r')*))?\s*$')
FROZEN_FORM = re.compile(r'^\s*[-*+]\s+' + TICKED + r'\s*$')
DECIDE_FORM = re.compile(r'^\s*(\d+)\.\s+(.*\?)\s+yes\s*->\s*`([^`]+)`\s*$')
LEVEL_FORM = re.compile(r'^\s*[-*+]\s+`([A-Z]+-\d+[a-z]?)`\s+(error|warning)\s*$')
CAP_FORM = re.compile(r'^\s*[-*+]\s+`([A-Z]+-\d+[a-z]?)`\s+(\d+)\s*$')
OTHERWISE_FORM = re.compile(r'^\s*otherwise\s*->\s*`([^`]+)`\s*$')
TABLE_SPLIT = re.compile(r'(?<!\\)\|')
SEPARATOR_CELL = re.compile(r'^:?-{3,}:?$')
FENCE_OPEN = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')

Layout = collections.namedtuple('Layout', 'homes frozen kinds decide legacy levels grandfathered caps',
                                defaults=({}, (), [], {}, [], {}))
Layout.__doc__ = ('homes: dict of home path to a tuple of globs, in file order. frozen: list of patterns. '
                  'kinds: dict of row id to a dict of the eleven registry fields, in file order. '
                  'decide: tuple of (question, id) in order, ending with ("otherwise", id); empty without a '
                  '## Decide section. legacy: list of globs. levels: dict of rule id to the level its warnings '
                  'are raised to (## Levels). grandfathered: list of globs whose names keep their pre-numbering form '
                  '(## Grandfathered). caps: dict of rule id to the number it caps (## Caps, `D-14` 12).')


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


def _parse_layout(path, skip=frozenset(), docs=True):
    """The parser. `skip` names rules to leave out; only the selftest's defective variants pass it."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    return _parse_layout_text(text, path, skip, docs)


def _cells(line):
    inner = line.strip()
    if not (inner.startswith('|') and inner.endswith('|') and len(inner) > 1):
        return None
    return [c.strip().replace('\\|', '|') for c in TABLE_SPLIT.split(inner[1:-1])]


def _parse_layout_text(text, path, skip=frozenset(), docs=True):
    """docs=False reads a layout for another tree (.sdlc): kinds are free text and the required
    ## Homes and ## Frozen paths sections and the home cross-check do not apply."""
    homes, frozen, legacy, levels, grandfathered, caps = {}, [], [], {}, [], {}
    kinds, decide = {}, []
    otherwise = None
    state = {'header': False, 'sep': False}
    seen = {}
    section = None
    n = 0
    for n, (line, fenced) in enumerate(scan_lines(text), 1):
        if fenced:
            continue
        m = HEADING.match(line)
        if m:
            head = line.strip()
            if head in SECTIONS or head in OPTIONAL_SECTIONS:
                if head in seen and 'duplicate-heading' not in skip:
                    raise LayoutError(path, n, '%r appears twice (first at line %d)' % (head, seen[head]))
                seen.setdefault(head, n)
                section = head
            elif len(m.group(1)) <= 2:
                section = None
            continue
        if section == KINDS:
            if not line.strip():
                continue
            cells = _cells(line)
            if cells is None or len(cells) != len(KIND_COLUMNS):
                if 'kinds-form' in skip:
                    continue
                raise LayoutError(path, n, 'line under %r is not a table row of %d cells' % (KINDS, len(KIND_COLUMNS)))
            if not state['header']:
                if tuple(c.lower() for c in cells) != KIND_COLUMNS and 'kinds-form' not in skip:
                    raise LayoutError(path, n, 'header under %r must name %s' % (KINDS, ', '.join(KIND_COLUMNS)))
                state['header'] = True
                continue
            if not state['sep']:
                state['sep'] = True
                if all(SEPARATOR_CELL.match(c) for c in cells):
                    continue
                if 'kinds-form' not in skip:
                    raise LayoutError(path, n, 'the row after the header under %r must be a separator row' % KINDS)
            row = dict(zip(KIND_COLUMNS, cells))
            for col in KIND_REQUIRED:
                if row[col] in ('', '-') and 'kinds-form' not in skip:
                    raise LayoutError(path, n, 'row under %r has no value for required column %r' % (KINDS, col))
            rid = row['id'].strip('`')
            row['id'] = rid
            row['kind'] = row['kind'].strip('`')
            if rid in kinds and 'kinds-duplicate' not in skip:
                raise LayoutError(path, n, 'row id %r is listed twice under %r' % (rid, KINDS))
            if docs and row['kind'] not in DOC_KINDS and 'kind-unknown' not in skip:
                raise LayoutError(path, n, 'kind %r is not one of %s' % (row['kind'], ', '.join(DOC_KINDS)))
            kinds[rid] = row
            state.setdefault('lines', {})[rid] = n
            continue
        if section == DECIDE:
            if not line.strip():
                continue
            if otherwise is not None and 'decide-form' not in skip:
                raise LayoutError(path, n, 'line after the otherwise line under %r' % DECIDE)
            m = OTHERWISE_FORM.match(line)
            if m:
                otherwise = m.group(1)
                continue
            m = DECIDE_FORM.match(line)
            if not m:
                if 'decide-form' in skip:
                    continue
                raise LayoutError(path, n, 'line under %r is not `N. <question>? yes -> `id`` or `otherwise -> `id``' % DECIDE)
            if int(m.group(1)) != len(decide) + 1 and 'decide-form' not in skip:
                raise LayoutError(path, n, 'decide line is numbered %s, expected %d' % (m.group(1), len(decide) + 1))
            decide.append((m.group(2), m.group(3)))
            continue
        if section is None or not LIST_LINE.match(line):
            continue
        if section == LEVELS:
            m = LEVEL_FORM.match(line)
            if not m:
                if 'levels-form' in skip:
                    continue
                raise LayoutError(path, n, 'list line under %r is not `<rule>` error|warning' % LEVELS)
            levels[m.group(1)] = m.group(2)
            continue
        if section == CAPS:
            m = CAP_FORM.match(line)
            if not m:
                if 'caps-form' in skip:
                    continue
                raise LayoutError(path, n, 'list line under %r is not `<rule>` <number>' % CAPS)
            caps[m.group(1)] = int(m.group(2))
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
                if 'form' in skip and section == FROZEN:
                    continue
                if 'legacy-form' in skip and section in (LEGACY, GRANDFATHERED):
                    continue
                raise LayoutError(path, n, 'list line under %r is not one `<glob>`' % section)
            {FROZEN: frozen, LEGACY: legacy, GRANDFATHERED: grandfathered}[section].append(m.group(1))
    if docs:
        for head in SECTIONS:
            if head not in seen:
                raise LayoutError(path, max(n, 1), 'section heading %r is missing' % head)
        if 'kinds-home' not in skip:
            for rid, ln in state.get('lines', {}).items():
                if rid not in homes:
                    raise LayoutError(path, ln, 'row id %r under %r is not a home listed under %r' % (rid, KINDS, HOMES))
    if DECIDE in seen and otherwise is None and 'decide-form' not in skip:
        raise LayoutError(path, max(n, 1), '%r has no otherwise line' % DECIDE)
    return Layout(homes, frozen, kinds, tuple(decide) + ((('otherwise', otherwise),) if otherwise else ()), legacy,
                  levels, grandfathered, caps)


def parse_layout(path, docs=True):
    """Parse a layout file into Layout. Raises LayoutError with file and line.

    docs=True is docs/layout.md; docs=False is another tree's layout (.sdlc/layout.md)."""
    return _parse_layout(path, docs=docs)


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


LINK = re.compile(r'\[[^\]]*\]\(<?([^)\s>]+)>?(?:\s+"[^"]*")?\)')
IMPORT_LINE = re.compile(r'^@(\S+)\s*$')


def _entry_paths(root):
    r = subprocess.run(['git', '-C', root, 'ls-files', '-z'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    paths = [p.decode('utf-8', 'surrogateescape') for p in r.stdout.split(b'\0')]
    return sorted(p for p in paths if p.rsplit('/', 1)[-1] in ('AGENTS.md', 'CLAUDE.md')
                  and os.path.isfile(os.path.join(root, p)))


def _targets(text, links=True):
    for line, fenced in scan_lines(text):
        if fenced:
            continue
        m = IMPORT_LINE.match(line)
        if m:
            yield m.group(1)
        if links:
            for m in LINK.finditer(re.sub(r'`[^`]*`', '', line)):
                yield m.group(1)


def resolve_entries(root, check_import=True, check_links=True):
    """Problem lines for tracked entry files: an AGENTS.md without a CLAUDE.md importing it, and a link or
    @import that names no file. The keyword switches exist only for the selftest's defective variants."""
    problems = []
    tracked = _entry_paths(root)
    for path in tracked:
        folder = path.rsplit('/', 1)[0] if '/' in path else ''
        name = path.rsplit('/', 1)[-1]
        if name == 'AGENTS.md' and check_import:
            sibling = (folder + '/' if folder else '') + 'CLAUDE.md'
            full = os.path.join(root, *sibling.split('/'))
            if not os.path.isfile(full) or not has_import(_read(full)):
                problems.append('no-import %s' % sibling)
        if not check_links:
            continue
        for target in _targets(_read(os.path.join(root, *path.split('/')))):
            if re.match(r'^([a-zA-Z][a-zA-Z0-9+.-]*:|#|/|~)', target):
                continue
            rel = target.split('#', 1)[0].split('?', 1)[0]
            if rel and not os.path.exists(os.path.normpath(os.path.join(root, folder, rel))):
                problems.append('broken-link %s: %s' % (path, target))
    return problems


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

`.sdlc/` holds SDLC Lite tickets and plans; run records live in the git-ignored `.sdlc/runtime/tasks/<folder>/`, and a closed ticket keeps only its `handoff.md` with its `## Outcome`.

- Pick the lane first with `steps.py lane <task dir>` (in the plugin's `scripts/` folder): `solo` is the default for ticket levels L1 and L2, `/sdlc-lite:fix` runs only when asked or when the lane script prints `fix`, and the full chain (`/sdlc-lite:chain`) needs a stated reason (an L4 or L5 step, a merge step, or cross-cutting scope). Roles launch with `run.sh`. Do not spawn another plugin's builder, planner, or reviewer agent in their place.
- Worktrees: lanes live in `../<repo>.worktrees/` (`wtroot.py root`, in the plugin's `scripts/` folder). Lane open, the solo and verifier runs in a lane, land and close write `.git` or the lane tree outside the checkout, so under Codex run them with full access, not the `workspace-write` sandbox.
- Several hosts in one repo (Claude Code, Codex, Pi): one conductor writes main; a worker writes only its locked lane, commits nothing, and runs `lanes.py ready` when done (the Lanes section of the plugin's `AGENTS.md`).
- Handoff files follow the `sdlc-lite:handoff-format` skill.
- Tickets are created, closed, and archived through the `sdlc-lite:ticket` skill.
- `.sdlc/roadmap.md` is generated. Do not edit it by hand.
- `.sdlc/messages/` is a local mailbox. Never commit it; a `.gitignore` line for it is advised.
- Do not move or rewrite a finished run record. Write no loose file at the top of `.sdlc/` or the project root: notes go to `.sdlc/notes.md`, an answer to another agent goes by `messages.py send`. The `.sdlc/AGENTS.md` Folder layout lists what may sit at the top; `tickets.py check` warns on anything else and `tickets.py tidy` moves it into `.sdlc/archive/`.
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

Pick one home from the table, then read one file. Placement effect unproven; see the docs-schema design.

| Home | Holds | Never holds |
|---|---|---|
| `work/` | Ticket and task folders, the generated `ROADMAP.md` and `NOTES.md` | Designs and plans under review -> `planning/` |
| `specs/` | What the system is and must do; edited in place | Proposals, dated evidence, steps |
| `planning/` | Proposals, roadmaps, plans under review (`status:`) | What exists today |
| `decisions/` | One numbered decision per file, immutable once accepted | Narrative design |
| `goals/` | One intended outcome per file (`G-NNN`): owner, status, the KPIs that show it is met | Change plans, tickets, result values |
| `kpi/` | One measure per file (`K-NNN`): command, unit, target, the goals it serves | Values over time, thresholds nobody can run |
| `references/` | Lookup tables, listings, glossaries | Procedures, opinions |
| `guides/` | How-to and operating procedures | Lookup tables, design |
| `reports/` | Dated evidence: runs, reviews, audits, releases | Instructions, living specs |
| `assets/` | Non-Markdown files cited by a document | Markdown |
| `archive/` | Superseded or retired documents | Live documents |
| `other/` | Unsorted inbox with `owner:` and `review-by:` | Anything with a clear home |

## Which home

The first line that matches wins.

1. A ticket or task record, or the generated roadmap or notes file: `work/`.
2. Picture, diagram source or data file: `assets/`.
3. Evidence of something that happened on a date: `reports/`.
4. One choice with its reasons: `decisions/`.
5. A proposal, roadmap or plan under review: `planning/`.
6. An outcome to steer toward, with an owner and a status: `goals/`.
7. A measure with a command that runs it, a unit and a target: `kpi/`.
8. Steps a person follows: `guides/`.
9. A table, listing or glossary you look things up in: `references/`.
10. What the system is or must do: `specs/`.
11. Retired or superseded: `archive/`.
12. None of the above, or unsure: `other/`.

## Adding a document

1. Pick the home above; [the layout](layout.md) lists any extra homes.
2. Name it lowercase kebab-case; reports lead with `YYYY-MM-DD-`. A home whose `## Kinds` form in [the layout](layout.md) is numbered (such as `NNNN-slug.md`) takes the next number from `docs_check.py next docs/<home>`, or by hand: read the highest existing number and held ref, then run `git update-ref refs/sdlc/doc-ids/<home>/<NNNN> "$(printf 'docs/<home>/<NNNN>\\n' | git hash-object -w --stdin)" ""`, which is create-only.
3. Add a link to it in its folder's `AGENTS.md`, outside the generated managed block, since a hand edit inside the block fails its stamp. The onboard setup also lists it.
4. Put dated evidence in its own file under `reports/`. Do not add it to an entry file.
5. Find the document's type in `specs/doc-standards/README.md`, when this repository has it, and follow the card its row names.

## Contents

<a link to README.md when it exists>
<one link per topic: to its entry, or to its single document>
<one line per home that exists: a link to its README.md, or the folder name>
<one link per loose document>
<!-- sdlc-lite:managed:end -->
"""

LAYOUT_TEMPLATE = """\
# Layout

Any other folder directly under `docs/` is a topic. It holds the designs, specifications, and decisions for one concept.

## Homes

- `work/`
- `specs/`
- `planning/`
- `decisions/`
- `goals/`
- `kpi/`
- `references/`
- `guides/`
- `reports/`
- `assets/`
- `archive/`
- `other/`

## Kinds

| id | kind | holds | not | why | writer | form | life | entry | read | owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `work/` | work | ticket and task folders, the generated `ROADMAP.md` and `NOTES.md` | designs and plans under review -> `planning/` | work records next to the docs they change | `tickets.py` | `NNNN-slug/handoff.md`, `ROADMAP.md`, `NOTES.md` | close dot-renames in place | - | running or closing a ticket | `tickets.py` |
| `specs/` | specs | what the system is and must do | plans -> `planning/` | one place to trust | people | kebab-case | supersede to `archive/` | - | defining the system | `docs_check.py` |
| `planning/` | planning | proposals and plans under review | built facts -> `specs/` | decisions need a place | people | `status:` front matter | accept, then `archive/` | - | deciding or scheduling | `docs_check.py` |
| `decisions/` | decisions | one numbered decision per file | narrative -> `specs/` | reasons outlive people | people | `NNNN-slug.md`, `status:` | supersede | - | asking why | `docs_check.py` |
| `goals/` | goals | one intended outcome per file | change plans -> `planning/` | steering needs a record | people | `NNN-slug.md`, `status:` | achieve or drop, then `archive/` | - | steering the work | `docs_check.py` |
| `kpi/` | kpi | one measure per file | values over time -> `reports/` | a number needs a command | people | `NNN-slug.md`, `measure:` | edit in place | - | measuring an outcome | `docs_check.py` |
| `references/` | references | lookup tables and listings | steps -> `guides/` | fast lookup | people | kebab-case | edit in place | - | looking something up | `docs_check.py` |
| `guides/` | guides | procedures a person follows | tables -> `references/` | do, not explain | people | kebab-case | edit in place | - | doing a task | `docs_check.py` |
| `reports/` | reports | dated evidence | steps -> `guides/` | evidence stays fixed | people | `YYYY-MM-DD-slug.md` | immutable | - | checking what was verified | `docs_check.py` |
| `assets/` | assets | non-Markdown files cited by a document | Markdown -> its home | keep prose clean | people | kebab-case | with its citer | - | opening a cited file | `docs_check.py` |
| `archive/` | archive | superseded or retired documents | live documents -> their home | history without noise | people | `status:`, `superseded-by:` | keep | - | researching history | `docs_check.py` |
| `other/` | other | unsorted documents | anything with a home -> that home | a visible backlog | anyone | `owner:`, `review-by:` | review-by date | - | sorting the inbox | `docs_check.py` |

## Decide

1. Is it a ticket or task record, or the generated roadmap or notes file? yes -> `work/`
2. Is it a picture, diagram source or data file? yes -> `assets/`
3. Is it evidence of something that happened on a date? yes -> `reports/`
4. Is it one choice with its reasons and alternatives? yes -> `decisions/`
5. Is it a proposal, roadmap or plan under review? yes -> `planning/`
6. Is it an outcome to steer toward, with an owner and a status? yes -> `goals/`
7. Is it a measure with a command that runs it, a unit and a target? yes -> `kpi/`
8. Is it steps a person follows? yes -> `guides/`
9. Is it a table, listing or glossary you look things up in? yes -> `references/`
10. Does it describe what the system is or must do? yes -> `specs/`
11. Is it retired or superseded? yes -> `archive/`
otherwise -> `other/`

## Frozen paths

- `docs/reports/`

## Legacy
"""

TOPIC_AGENTS_TEMPLATE = """\
# <topic folder name>

Describe what this topic covers.

<!-- sdlc-lite:managed:start v<N> sha256:<H> -->
## Contents

<a link to README.md when it exists, then one link per document>
<!-- sdlc-lite:managed:end -->
"""

PH_README = '<a link to README.md when it exists>'
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

Model = collections.namedtuple('Model', 'name topics homes loose readme nested roadmap notes archive tickets lanes',
                               defaults=((), '.sdlc/roadmap.md', '.sdlc/notes.md', '.sdlc/archive/', '.sdlc/',
                                         '../<repo>.worktrees/'))
Model.__doc__ = ('name: repository folder name. topics: list of Topic with one or more documents. '
                 'homes: list of Home that exist. loose: documents directly in docs/. '
                 'readme: docs/README.md exists. nested: list of Topic for a home, or a topic folder '
                 'under a home, that holds two or more documents (name is the path under docs/). '
                 'roadmap, notes: the resolved roadmap and notes paths relative to the root, posix form. '
                 'archive: the resolved tidy archive folder, the same form with a trailing slash. '
                 'tickets: the ticket root, the same form, or None with no .sdlc/ folder (the block then '
                 'keeps no .sdlc/ line). lanes: the lane root as the block names it.')
NO_SDLC_LINE = 'SDLC Lite tickets are not set up here: the repository has no `.sdlc/` folder.'
Topic = collections.namedtuple('Topic', 'name docs readme')
Home = collections.namedtuple('Home', 'path readme entry', defaults=(False,))
NESTED_LINK_CAP = 20


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
                                t.block.replace('<N>', n).replace('.sdlc/roadmap.md', model.roadmap)
                                .replace('.sdlc/notes.md', model.notes).replace('.sdlc/archive/', model.archive)
                                .replace('`.sdlc/` holds', '`%s` holds' % (model.tickets or '.sdlc/'))
                                .replace('`../<repo>.worktrees/`', '`%s`' % model.lanes),
                                t.after)
    if model.tickets is None:
        out['AGENTS.md'] = out['AGENTS.md']._replace(block=''.join(
            NO_SDLC_LINE + '\n' if line.startswith('`') else line
            for line in _split_keep(out['AGENTS.md'].block) if line.startswith('`') or '.sdlc' not in line))
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
        elif home.entry:
            home_lines.append(_link(home.path, home.path + 'AGENTS.md'))
        else:
            home_lines.append('- `%s`' % home.path)
    for doc in model.loose:
        loose_lines.append(_link(doc, doc))
    t = _split_template(DOCS_AGENTS_TEMPLATE)
    out['docs/AGENTS.md'] = Template(t.before, _substitute(
        t.block, {PH_README: [_link('README.md', 'README.md')] if model.readme else [],
                  PH_TOPICS: topic_lines, PH_HOMES: home_lines, PH_LOOSE: loose_lines}), t.after)
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
    entries = {t.name for t in model.nested}
    for topic in model.nested:
        links = [_link('README.md', 'README.md')] if topic.readme else []
        direct = [d for d in topic.docs if '/' not in d]
        subs = sorted({d.split('/', 1)[0] for d in topic.docs if '/' in d})
        links.extend(_link(sub + '/', sub + '/AGENTS.md') for sub in subs if topic.name + '/' + sub in entries)
        loose_subs = [d for d in topic.docs if '/' in d and topic.name + '/' + d.split('/', 1)[0] not in entries]
        shown = (direct + loose_subs)[:NESTED_LINK_CAP]
        links.extend(_link(doc, doc) for doc in shown)
        more = len(direct) + len(loose_subs) - len(shown)
        if more > 0:
            links.append('- and %d more documents in this folder' % more)
        base = 'docs/%s/' % topic.name
        out[base + 'AGENTS.md'] = Template(t.before.replace('<topic folder name>', topic.name.rsplit('/', 1)[-1]),
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
    nested = _nested_topics(root, layout, documents)
    entries = {t.name + '/' for t in nested}
    home_list = [Home(h, os.path.isfile(os.path.join(root, 'docs', h, 'README.md')), h in entries)
                 for h in homes if os.path.isdir(os.path.join(root, 'docs', h))]
    name = os.path.basename(os.path.normpath(root))
    return Model(name, topic_list, home_list, sorted(loose),
                 os.path.isfile(os.path.join(root, 'docs', 'README.md')), nested, *_sdlc_paths(root),
                 _lane_root(root))


def _sdlc_paths(root):
    """(roadmap, notes, archive, tickets) from .sdlc/config, relative to root in posix form; archive is
    <work>/archive/, and archive and tickets end in a slash; tickets is None with no .sdlc/ folder. A bad config
    is a SetupError."""
    import pathlib
    import tickets  # function-local: tickets.py imports this module at its top level
    try:
        paths = tickets.layout_paths(pathlib.Path(root, '.sdlc'))
    except tickets.Fail as e:
        raise SetupError(str(e))
    rel = lambda p: pathlib.Path(os.path.relpath(str(p), root)).as_posix()
    tickets_root = rel(paths.tickets) + '/' if os.path.isdir(os.path.join(root, '.sdlc')) else None
    return rel(paths.roadmap), rel(paths.notes), rel(paths.work / 'archive') + '/', tickets_root


def _lane_root(root):
    """The lane root as the block names it, from wtroot.root(): `../<repo>.worktrees/` for the default sibling
    root, `<bare parent>/<path>/` in a bare clone, else the path relative to the main checkout."""
    import pathlib
    import wtroot
    rel = lambda p, base: pathlib.Path(os.path.relpath(str(p), base)).as_posix() + '/'
    lanes = wtroot.root(root)
    bare = wtroot.bare_parent(root)
    if bare:
        return '<bare parent>/' + rel(lanes, bare)
    top = wtroot.main_top(root)
    if lanes is None or top is None or lanes == wtroot.default_root(top):
        return '../<repo>.worktrees/'
    return rel(lanes, top)


def _nested_topics(root, layout, documents):
    """Homes, and topic folders directly under a home, that hold ENTRY_THRESHOLD or more documents.

    Subfolders get an entry only under a home whose kind allows topics (specs, planning, references,
    guides, decisions); a report's evidence folder never does. The work home gets none: tickets.py writes its entry."""
    topic_kinds = ('specs', 'planning', 'references', 'guides', 'decisions')
    found = collections.OrderedDict()
    for home in layout.homes:
        key = home.rstrip('/')
        kind = layout.kinds[home]['kind'] if home in layout.kinds else (key if key in DOC_KINDS else None)
        if kind == 'work':
            continue
        prefix = 'docs/' + home
        inside = [d[len(prefix):] for d in documents if d.startswith(prefix)]
        if len(inside) >= ENTRY_THRESHOLD:
            found[key] = list(inside)
        if kind in topic_kinds:
            subs = {}
            for rel in inside:
                if '/' in rel:
                    subs.setdefault(rel.split('/', 1)[0], []).append(rel.split('/', 1)[1])
            for sub, docs in subs.items():
                if len(docs) >= ENTRY_THRESHOLD:
                    found[key + '/' + sub] = docs
    return [Topic(name, sorted(docs), os.path.isfile(os.path.join(root, 'docs', name, 'README.md')))
            for name, docs in found.items()]


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


def is_refresh(c):
    """A change to a managed block the file already holds; setup without --init writes only these."""
    return c.old is not None and c.action == 'replace'


# The parts of the implementation that the selftest swaps for defective variants.
Impl = collections.namedtuple('Impl', 'render wrap rows find_block labels preflight refresh')
REAL = Impl(render_templates, wrap_block, ROWS, find_block, LABELS, True, is_refresh)

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
    target = ROOT_SIZE_TARGET if '/' not in path or path == 'docs/AGENTS.md' else NESTED_SIZE_TARGET
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


def run_setup(root, impl=None, dry_run=False, force=False, init=False, out=None, err=None):
    """setup: print the diff (dry run) or write it. Returns the exit status.

    Without init only existing managed blocks are refreshed; every file init would create or
    append to is listed on stderr as `--init would <create|append a block to> <path>`.
    """
    impl, out, err = impl or REAL, out or sys.stdout, err or sys.stderr
    changes = _plan_or_report(root, impl, force, err)
    if changes is None:
        return 1
    for c in changes:
        size = _size_note(c, c.new)
        for note in c.notes + ([size] if size else []):
            err.write(note + '\n')
    todo = [c for c in changes if _changed(c)]
    if not init:
        for c in todo:
            if not impl.refresh(c):
                err.write('--init would %s %s\n' % ('create' if c.old is None else 'append a block to', c.path))
        todo = [c for c in todo if impl.refresh(c)]
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


def run_check(root, impl=None, out=None, err=None, resolver=None):
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
    problems = (resolver or resolve_entries)(root)
    for p in problems:
        out.write(p + '\n')
    return 0 if all(c.label in ('current', 'present') for c in changes) and not problems else 1


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


KIND_HEADER = '| ' + ' | '.join(KIND_COLUMNS) + ' |\n| ' + ' | '.join(['---'] * len(KIND_COLUMNS)) + ' |\n'


def _kind_row(rid, kind='specs', **over):
    cells = {'id': '`%s`' % rid, 'kind': kind, 'holds': 'the system', 'not': 'plans -> `planning/`', 'why': 'one place',
             'writer': '-', 'form': 'kebab', 'life': '-', 'entry': '-', 'read': 'when using it', 'owner': '-'}
    cells.update(over)
    return '| ' + ' | '.join(cells[c] for c in KIND_COLUMNS) + ' |\n'


def gate_layout_sections(parse):
    base = '## Homes\n- `specs/`\n- `reports/`\n## Frozen paths\n'
    kinds = '## Kinds\n' + KIND_HEADER + _kind_row('specs/') + _kind_row('reports/', 'reports')
    decide = ('## Decide\n1. Is it evidence of something that happened? yes -> `reports/`\n'
              '2. Is it a description of the system? yes -> `specs/`\notherwise -> `specs/`\n')
    legacy = '## Legacy\n- `reports/old/**`\n- `imported/**`\n'
    levels = '## Levels\n- `D-12` error\n## Grandfathered\n- `specs/old.md`\n## Caps\n- `D-14` 20\n'
    old_style = '## Homes\n- `maintenance/`\n## Frozen paths\n- `x/`\n## Kinds is mentioned in prose only\n'
    cases = [
        ('unknown kind', base + '## Kinds\n' + KIND_HEADER + _kind_row('specs/', 'diary'), 8),
        ('row for a home that is not listed', base + '## Kinds\n' + KIND_HEADER + _kind_row('guides/', 'guides'), 8),
        ('prose line under Kinds', base + '## Kinds\nsome prose\n', 6),
        ('header missing a column', base + '## Kinds\n| id | kind |\n| --- | --- |\n', 6),
        ('duplicate row id', base + '## Kinds\n' + KIND_HEADER + _kind_row('specs/') + _kind_row('specs/'), 9),
        ('missing required value', base + '## Kinds\n' + KIND_HEADER + _kind_row('specs/', holds='-'), 8),
        ('Kinds heading twice', base + kinds + '## Kinds\n', 10),
        ('Decide line outside the form', base + '## Decide\n1. Is it a plan? maybe\n', 6),
        ('Decide numbering skips', base + '## Decide\n2. Is it a plan? yes -> `specs/`\n', 6),
        ('Decide with no otherwise', base + '## Decide\n1. Is it a plan? yes -> `specs/`\n', 6),
        ('Decide line after otherwise', base + '## Decide\notherwise -> `specs/`\n1. Is it a plan? yes -> `specs/`\n', 7),
        ('Legacy line without backticks', base + '## Legacy\n- reports/old/**\n', 6),
        ('Levels line with an unknown level', base + '## Levels\n- `D-12` fatal\n', 6),
        ('Grandfathered line without backticks', base + '## Grandfathered\n- specs/old.md\n', 6),
        ('Caps line without a number', base + '## Caps\n- `D-14` many\n', 6),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        def write(name, text):
            p = os.path.join(tmp, name)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(text)
            return p

        got = parse(write('ok.md', base + kinds + '\n' + decide + '\n' + legacy + levels))
        expect(list(got.kinds) == ['specs/', 'reports/'], 'kinds parsed as %r' % (list(got.kinds),))
        expect(got.kinds['reports/']['kind'] == 'reports' and got.kinds['specs/']['read'] == 'when using it',
               'kind row fields parsed wrong: %r' % (got.kinds,))
        expect(got.decide == (('Is it evidence of something that happened?', 'reports/'),
                              ('Is it a description of the system?', 'specs/'), ('otherwise', 'specs/')),
               'decide parsed as %r' % (got.decide,))
        expect(got.legacy == ['reports/old/**', 'imported/**'], 'legacy parsed as %r' % (got.legacy,))
        expect(got.levels == {'D-12': 'error'} and got.grandfathered == ['specs/old.md'],
               'levels or grandfathered parsed as %r' % (got,))
        expect(got.caps == {'D-14': 20}, 'caps parsed as %r' % (got,))
        expect(got.homes == {'specs/': (), 'reports/': ()} and got.frozen == [], 'homes or frozen changed: %r' % (got,))
        got = parse(write('old.md', old_style))
        expect(got.kinds == {} and got.decide == () and got.legacy == [] and got.frozen == ['x/'],
               'an older-style file parsed as %r' % (got,))
        for i, (label, text, line) in enumerate(cases):
            path = write('bad%d.md' % i, text)
            try:
                parse(path)
            except LayoutError as e:
                expect(e.line == line, '%s: error at line %s, expected %d' % (label, e.line, line))
                expect(e.path == path, '%s: error names %r, expected %r' % (label, e.path, path))
                continue
            raise GateFailure('%s: parsed without an error' % label)


def gate_layout_other_tree(parse):
    """A .sdlc layout: free-text kinds, no Homes or Frozen sections required."""
    text = '## Kinds\n' + KIND_HEADER + _kind_row('notes.md', 'notebook')
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'layout.md')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
        got = parse(p)
        expect(list(got.kinds) == ['notes.md'] and got.kinds['notes.md']['kind'] == 'notebook',
               'other-tree kinds parsed as %r' % (got.kinds,))
        with open(p, 'w', encoding='utf-8') as f:
            f.write('## Kinds\n| id | kind |\n')
        try:
            parse(p)
        except LayoutError:
            return
        raise GateFailure('other-tree layout with a short header parsed without an error')


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


def gate_digest(digest_of):
    # Expected values: printf 'line one\nline two\n' | shasum -a 256 (first 12 hex characters).
    lf = 'line one\nline two\n'
    crlf = 'line one\r\nline two\r\n'
    want = 'e9024f1a07d2'
    got = digest_of(lf)
    expect(got == want, 'LF text hashed to %r, expected %r' % (got, want))
    got = digest_of(crlf)
    expect(got == want, 'CRLF text hashed to %r, expected %r' % (got, want))


def _digest_raw(text):
    """Defect variant: hashes without normalizing line endings."""
    return hashlib.sha256(text.encode('utf-8', 'surrogateescape')).hexdigest()[:12]


def _digest_prefix(length):
    """Defect variant: returns a prefix of a different length."""
    return lambda text: hashlib.sha256(text.replace('\r\n', '\n').encode('utf-8')).hexdigest()[:length]


# Fixtures for the setup and check gates: throwaway Git work trees named `demo`.

ROOT_STARTER = '# demo\n\n## What this repository is\n\n## Shared rules\n\n## Checks\n\n'
ROLE_LINE = "Do not spawn another plugin's builder, planner, or reviewer agent in their place."
STUB = '@AGENTS.md\n'
BASE_FILES = ['AGENTS.md', 'CLAUDE.md', 'docs/AGENTS.md', 'docs/CLAUDE.md', 'docs/layout.md']
RICH_DOCS = {
    'docs/alpha/design.md': '# Design\n',
    'docs/alpha/notes/one.md': '# One\n',
    'docs/alpha/README.md': '# Alpha\n',
    'docs/README.md': '# Docs\n',
    'docs/beta/only.md': '# Only\n',
    'docs/loose.md': '# Loose\n',
    'docs/guides/README.md': '# Operating\n',
    'docs/reports/2026-09-29.md': '# Report\n',
}
RICH_CONTENTS = ('- [README.md](README.md)\n- [alpha/](alpha/AGENTS.md)\n- [beta/only.md](beta/only.md)\n'
                 '- [guides/](guides/README.md)\n- `reports/`\n- [loose.md](loose.md)\n')


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
        rc, out, err = _call(run_setup, root, impl, init=True)
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
        expect(block.text.startswith('# Documents\n\nPick one home from the table, then read one file.'),
               'docs/AGENTS.md: block starts %r' % block.text[:60])
        for home in ('work', 'specs', 'planning', 'decisions', 'goals', 'kpi', 'references', 'guides', 'reports', 'assets', 'archive', 'other'):
            expect('| `%s/` |' % home in block.text, 'docs/AGENTS.md: the table lacks the home %s/' % home)
        expect('| `work/` | Ticket and task folders, the generated `ROADMAP.md` and `NOTES.md` | '
               'Designs and plans under review -> `planning/` |' in block.text, 'docs/AGENTS.md: the work/ row is wrong')
        expect('otherwise' not in block.text and '12. None of the above, or unsure: `other/`.' in block.text,
               'docs/AGENTS.md: the decision list is missing or malformed')
        expect(re.search(r'^1\. .*: `work/`\.$', block.text, re.M), 'docs/AGENTS.md: work/ is not first in Which home')
        expect(block.text.endswith('## Contents\n\n'), 'docs/AGENTS.md: contents in an empty fixture: %r'
               % block.text[-80:])
        expect(_text(root, LAYOUT_PATH) == LAYOUT_TEMPLATE, 'docs/layout.md is not the default layout')
        layout = parse_layout(os.path.join(root, 'docs', 'layout.md'))
        expect(list(layout.homes) == [h + '/' for h in DOC_KINDS] and layout.frozen == ['docs/reports/'],
               'default layout parsed as %r' % (layout,))
        expect(list(layout.kinds) == [h + '/' for h in DOC_KINDS] and layout.decide[-1] == ('otherwise', 'other/'),
               'default layout kinds or decide parsed as %r' % (layout,))
        work = layout.kinds.get('work/', {})
        expect((work.get('kind'), work.get('form'), work.get('life'), work.get('owner'))
               == ('work', '`NNNN-slug/handoff.md`, `ROADMAP.md`, `NOTES.md`', 'close dot-renames in place', '`tickets.py`'),
               'default layout work/ Kinds row is %r' % (work,))
        expect(layout.decide[0][1] == 'work/', 'default layout Decide does not start with work/: %r' % (layout.decide,))
    untracked = dict(RICH_DOCS, **{'docs/alpha/draft.md': '# Not tracked\n'})
    with _fixture(untracked, track=sorted(RICH_DOCS)) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
        expect(rc == 0, 'topic fixture: setup exited %d: %s' % (rc, err.strip()))
        want = sorted(BASE_FILES + list(untracked) + ['docs/alpha/AGENTS.md', 'docs/alpha/CLAUDE.md'])
        expect(_files(root) == want, 'topic fixture: files are %r' % _files(root))
        expect('docs/reference/' not in _snapshot(root), 'topic fixture: created an empty folder docs/reference/')
        before, block, after = _parts(_text(root, 'docs/alpha/AGENTS.md'), 'docs/alpha/AGENTS.md')
        expect(before == '# alpha\n\nDescribe what this topic covers.\n\n', 'topic entry starter is %r' % before)
        expect(block.text == '## Contents\n\n- [README.md](README.md)\n- [design.md](design.md)\n'
               '- [notes/one.md](notes/one.md)\n', 'topic entry block is %r' % block.text)
        expect(_text(root, 'docs/alpha/CLAUDE.md') == _region(TEMPLATE_VERSION, STUB), 'topic stub is wrong')
        _, block, _ = _parts(_text(root, 'docs/AGENTS.md'), 'docs/AGENTS.md')
        expect(block.text.endswith('## Contents\n\n' + RICH_CONTENTS), 'docs/AGENTS.md contents: %r'
               % block.text[block.text.find('## Contents'):])
    with _fixture({'docs': 'a regular file named docs\n', 'README.md': '# demo\n'}) as root:
        snap = _snapshot(root)
        rc, out, err = _call(run_setup, root, impl, init=True)
        expect(rc != 0, 'docs is a regular file: setup exited 0')
        expect(_snapshot(root) == snap, 'docs is a regular file: the fixture changed')
        expect('docs' in err, 'docs is a regular file: stderr does not name docs: %r' % err)


NESTED_DOCS = {
    'docs/guides/release.md': '# Release\n',
    'docs/guides/setup/one.md': '# One\n',
    'docs/guides/setup/two.md': '# Two\n',
    'docs/specs/api.md': '# API\n',
    'docs/reports/2026-10-05-a.md': '# A\n',
    'docs/reports/2026-10-05-b.md': '# B\n',
}


def _render_without_nested(model):
    return render_templates(model._replace(nested=()))


def _render_nested_for_every_home(model):
    extra = [Topic(h.path.rstrip('/'), ['x.md'], False) for h in model.homes]
    return render_templates(model._replace(nested=list(model.nested) + extra))


def gate_nested_entries(impl):
    with _fixture(NESTED_DOCS, track=sorted(NESTED_DOCS)) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
        expect(rc == 0, 'nested fixture: setup exited %d: %s' % (rc, err.strip()))
        files = _files(root)
        for want in ('docs/guides/AGENTS.md', 'docs/guides/CLAUDE.md', 'docs/guides/setup/AGENTS.md',
                     'docs/guides/setup/CLAUDE.md'):
            expect(want in files, 'nested fixture: %s was not created' % want)
        for gone in ('docs/specs/AGENTS.md', 'docs/reports/AGENTS.md'):
            expect(gone not in files, 'nested fixture: %s was created (one document, or a frozen home)' % gone)
        _, block, _ = _parts(_text(root, 'docs/guides/AGENTS.md'), 'docs/guides/AGENTS.md')
        expect('- [setup/](setup/AGENTS.md)' in block.text and '- [release.md](release.md)' in block.text,
               'nested fixture: the home entry block is %r' % block.text)
        _, block, _ = _parts(_text(root, 'docs/AGENTS.md'), 'docs/AGENTS.md')
        expect('- [guides/](guides/AGENTS.md)' in block.text, 'nested fixture: docs/AGENTS.md does not link the home entry')
        rc, out, err = _call(run_check, root, impl)
        expect(rc == 0, 'nested fixture: check after setup exited %d: %s %s' % (rc, out.strip(), err.strip()))


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
        rc, out, err = _call(run_setup, root, impl, init=True)
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
            rc, out, err = _call(run_setup, root, impl, init=True)
            expect(rc == 0, '%s fixture: first setup exited %d: %s' % (label, rc, err.strip()))
            snap = _snapshot(root)
            rc, out, err = _call(run_setup, root, impl, dry_run=True, init=True)
            expect(rc == 0 and out == '', '%s fixture: second dry run printed a diff:\n%s' % (label, out))
            rc, out, err = _call(run_setup, root, impl, init=True)
            expect(rc == 0 and out == '', '%s fixture: second setup reported %r' % (label, out))
            expect(_snapshot(root) == snap, '%s fixture: second setup changed the tree' % label)
            rows = dict((c.path, c.row) for c in plan(root, impl) if c.row is not None)
            expect(all(r in (5, 7) for r in rows.values()), '%s fixture: second run rows %r' % (label, rows))


def _refresh_everything(c):
    """Defect variant: treats every change as a refresh, so setup writes without --init."""
    return True


def gate_refresh_only(impl):
    """setup without --init changes no file in an unmanaged repo and lists what --init adds;
    --init behaves as before; a repo already set up keeps refreshing without --init."""
    files = dict(RICH_DOCS, **{'AGENTS.md': '# Mine\n\nkeep me\n'})
    with _fixture(files, track=sorted(RICH_DOCS)) as root:
        snap = _snapshot(root)
        for dry in (True, False):
            rc, out, err = _call(run_setup, root, impl, dry_run=dry)
            expect(rc == 0, 'no --init (dry run %s): setup exited %d: %s' % (dry, rc, err.strip()))
            expect(out == '', 'no --init (dry run %s): setup printed %r' % (dry, out))
            expect(_snapshot(root) == snap, 'no --init (dry run %s): the fixture changed' % dry)
            for line in ('--init would append a block to AGENTS.md', '--init would create CLAUDE.md',
                         '--init would create docs/AGENTS.md', '--init would create docs/alpha/AGENTS.md',
                         '--init would create docs/layout.md'):
                expect(line in err.splitlines(), 'no --init (dry run %s): stderr lacks %r: %r' % (dry, line, err))
        rc, out, err = _call(run_setup, root, impl, init=True)
        expect(rc == 0, '--init: setup exited %d: %s' % (rc, err.strip()))
        want = sorted(BASE_FILES + list(RICH_DOCS) + ['docs/alpha/AGENTS.md', 'docs/alpha/CLAUDE.md'])
        expect(_files(root) == want, '--init: files are %r' % _files(root))
        before, _, _ = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(before == '# Mine\n\nkeep me\n', '--init: AGENTS.md bytes before the block are %r' % before)
        expect('--init would' not in err, '--init: stderr still lists --init changes: %r' % err)
        _put(root, 'CLAUDE.md', _region(TEMPLATE_VERSION, 'an older stub\n'))
        _put(root, 'docs/beta/one.md', '# One\n')
        _put(root, 'docs/beta/two.md', '# Two\n')
        _git(root, 'add', '--', 'docs/beta/one.md', 'docs/beta/two.md')
        rc, out, err = _call(run_setup, root, impl)
        expect(rc == 0, 'set-up repo: setup exited %d: %s' % (rc, err.strip()))
        expect(_text(root, 'CLAUDE.md') == _region(TEMPLATE_VERSION, STUB), 'set-up repo: stale CLAUDE.md not refreshed')
        expect('updated CLAUDE.md' in out.splitlines(), 'set-up repo: setup reported %r' % out)
        expect('docs/beta/AGENTS.md' not in _files(root), 'set-up repo: created docs/beta/AGENTS.md without --init')
        expect('--init would create docs/beta/AGENTS.md' in err.splitlines(),
               'set-up repo: stderr does not list docs/beta/AGENTS.md: %r' % err)


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
                _call(run_setup, root, impl, init=True)
            before = _snapshot(root)
            got = dict((c.path, c) for c in plan(root, impl))[path]
            expect((got.row, got.action) == (row, action), 'row %d fixture: decided row %s (%s)'
                   % (row, got.row, got.action))
            rc, out, err = _call(run_setup, root, impl, init=True)
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
                rc, out, err = _call(run_setup, root, impl, force=True, init=True)
                _, block, _ = _parts(_text(root, path), path)
                expect(rc == 0 and 'Managed by SDLC Lite onboard' in block.text, 'row 4: --force did not replace')


def gate_malformed_markers(impl):
    old = '# Mine\n\n' + _region(TEMPLATE_VERSION, 'an older block\n') + '\ntail\n'
    with _fixture({'AGENTS.md': old}) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
        before, block, after = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(rc == 0 and before == '# Mine\n\n' and after == '\ntail\n', 'well-formed block: outside bytes changed')
        expect(ROLE_LINE in block.text, 'well-formed block: not replaced with the current template')
        _expect_hash(block, 'AGENTS.md')
    fenced = '# Mine\n\n```markdown\n' + START_MARKER % (TEMPLATE_VERSION, digest('x\n')) + '\nx\n```\n'
    with _fixture({'AGENTS.md': fenced}) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
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
            rc, out, err = _call(run_setup, root, impl, init=True)
            expect(_text(root, 'AGENTS.md') == content, '%s: the file changed' % label)
            expect('malformed AGENTS.md' in err, '%s: not reported: %r' % (label, err))
            rc, out, err = _call(run_check, root, impl)
            expect(rc != 0 and 'malformed AGENTS.md\n' in out, '%s: check printed %r' % (label, out))


def gate_entry_resolver(resolve):
    good = {'AGENTS.md': '# A\n[sub](sub/AGENTS.md)\n[web](https://x.y/z) [anchor](#top)\n```\n[fenced](nope.md)\n```\n',
            'CLAUDE.md': '@AGENTS.md\n', 'sub/AGENTS.md': '# S\n[up](../AGENTS.md#a)\n', 'sub/CLAUDE.md': '@AGENTS.md\n'}
    tracked = tuple(good)
    with _fixture(good, tracked) as root:
        expect(resolve(root) == [], 'positive fixture reported %r' % resolve(root))
    bad = [('no CLAUDE.md', {'sub/CLAUDE.md': None}, 'no-import sub/CLAUDE.md'),
           ('CLAUDE.md without the import', {'sub/CLAUDE.md': '# mine\n'}, 'no-import sub/CLAUDE.md'),
           ('broken link', {'AGENTS.md': '[gone](missing.md)\n'}, 'broken-link AGENTS.md: missing.md'),
           ('broken import', {'CLAUDE.md': '@AGENTS.md\n@nope.md\n'}, 'broken-link CLAUDE.md: nope.md')]
    for label, change, want in bad:
        files = dict(good)
        for k, v in change.items():
            if v is None:
                del files[k]
            else:
                files[k] = v
        with _fixture(files, tuple(files)) as root:
            expect(want in resolve(root), '%s: expected %r, got %r' % (label, want, resolve(root)))


def gate_check_mode(impl):
    with _fixture() as root:
        _call(run_setup, root, impl, init=True)
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
        _put(root, 'AGENTS.md', text.replace('Handoff files follow', 'Handoff files always follow'))

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
            _call(run_setup, root, impl, init=True)
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


# The lane line of the root block (T-0228): a block with the old route text is stale by TEXT (row 6), so setup replaces
# it with no version bump (TEMPLATE_VERSION is shared with tickets.py's router blocks, so a bump would make every
# router block stale); a hand-edited block stays edited and is not overwritten without --force.
OLD_ROUTE = '`/sdlc-lite:chain`, `/sdlc-lite:fix`, or `/sdlc-lite:build`'
LANE_LINE = 'Pick the lane first with `steps.py lane <task dir>`'


def _render_old_route(model):
    out = render_templates(model)
    t = out['AGENTS.md']
    block = t.block.replace(LANE_LINE, 'Plan, build, and verify work runs through SDLC Lite: ' + OLD_ROUTE
                            + ' (' + LANE_LINE + ')')
    out['AGENTS.md'] = t._replace(block=block)
    return out


def gate_lane_text(impl):
    old_block = ('## Work records\n\n- Plan, build, and verify work runs through SDLC Lite: ' + OLD_ROUTE
                 + ', which launch roles with `run.sh`.\n')
    stale = '# Mine\n\n' + _region(TEMPLATE_VERSION, old_block) + '\ntail\n'
    with _fixture({'AGENTS.md': stale}) as root:
        rc, out, err = _call(run_check, root, impl)
        expect('stale AGENTS.md' in out + err, 'a block with the old route is not reported stale: %r' % (out + err))
        rc, out, err = _call(run_setup, root, impl, init=True)
        _, block, _ = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(rc == 0 and block.version == TEMPLATE_VERSION, 'the old block is not replaced by the current version')
        expect(LANE_LINE in block.text and OLD_ROUTE not in block.text, 'the replaced block does not route by the lane')
        expect('solo' in block.text and ROLE_LINE in block.text, 'the replaced block lost the solo default or the role line')
    edited = '# Mine\n\n' + _region(TEMPLATE_VERSION, 'edited by hand\n', old_block) + '\ntail\n'
    with _fixture({'AGENTS.md': edited}) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
        expect('edited AGENTS.md' in out + err, 'a hand-edited block is not reported edited: %r' % (out + err))
        expect('edited by hand' in _text(root, 'AGENTS.md'), 'a hand-edited block was overwritten without --force')


def _render_layout(model, roadmap, notes, archive):
    return render_templates(model._replace(roadmap=roadmap, notes=notes, archive=archive))


def _render_topics_always(model):
    return _render_layout(model, '.sdlc/tickets/roadmap.md', '.sdlc/notes/notes.md', '.sdlc/work/archive/')


def _render_flat_always(model):
    return _render_layout(model, '.sdlc/roadmap.md', '.sdlc/notes.md', '.sdlc/archive/')


def gate_layout_variant(impl):
    flat = _split_template(ROOT_AGENTS_TEMPLATE).block.replace('<N>', str(TEMPLATE_VERSION))
    with _fixture({'.sdlc/config': ''}) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
        _, block, _ = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(rc == 0 and block.text == flat, 'a flat repo does not get the unsubstituted root block')
        rc, out, err = _call(run_check, root, impl)
        expect('current AGENTS.md' in out.splitlines(), 'flat AGENTS.md is not current: %r' % (out + err))
    with _fixture({'.sdlc/config': 'ticket_root: tickets\nlayout: topics\n'}) as root:
        rc, out, err = _call(run_setup, root, impl, init=True)
        _, block, _ = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(rc == 0 and '.sdlc/tickets/roadmap.md' in block.text and '.sdlc/roadmap.md' not in block.text,
               'a topics repo block does not name .sdlc/tickets/roadmap.md only')
        expect('.sdlc/notes/notes.md' in block.text and '.sdlc/work/archive/' in block.text
               and '.sdlc/notes.md' not in block.text and '.sdlc/archive/' not in block.text,
               'a topics repo block does not name .sdlc/notes/notes.md and .sdlc/work/archive/ only')
        expect(block.version == TEMPLATE_VERSION, 'topics block is v%d' % block.version)
        rc, out, err = _call(run_check, root, impl)
        expect('current AGENTS.md' in out.splitlines(), 'topics AGENTS.md is not current: %r' % (out + err))
    with _fixture({'.sdlc/config': 'work_root: docs/work\n'}) as root:  # T-0625: the work root's paths
        rc, out, err = _call(run_setup, root, impl, init=True)
        _, block, _ = _parts(_text(root, 'AGENTS.md'), 'AGENTS.md')
        expect(rc == 0 and '`docs/work/ROADMAP.md` is generated' in block.text
               and 'notes go to `docs/work/NOTES.md`' in block.text and 'into `docs/work/archive/`' in block.text
               and '`docs/work/` holds SDLC Lite tickets' in block.text
               and '.sdlc/roadmap.md' not in block.text and '.sdlc/notes.md' not in block.text,
               'a work_root repo block does not name docs/work/ROADMAP.md, docs/work/NOTES.md and docs/work/archive/')
        rc, out, err = _call(run_check, root, impl)
        expect('current AGENTS.md' in out.splitlines(), 'work_root AGENTS.md is not current: %r' % (out + err))


# The lane-root and ticket-root lines of the root block (T-0607): rendered from wtroot.root() and
# tickets.layout_paths(), so a bare clone and a tickets/ ticket root get their real paths.
DEFAULT_LANES = Model._field_defaults['lanes']


def _render_default_paths(model):
    return render_templates(model._replace(lanes=DEFAULT_LANES, tickets='.sdlc/'))


def _render_sdlc_always(model):
    return render_templates(model._replace(tickets=model.tickets or '.sdlc/'))


def _root_block(root, impl):
    model = build_model(root, _parse_layout_text(LAYOUT_TEMPLATE, LAYOUT_PATH), list_documents(root))
    return impl.render(model)['AGENTS.md'].block


def gate_block_paths(impl):
    with _fixture({'.sdlc/config': ''}) as root:
        block = _root_block(root, impl)
        expect('`%s`' % DEFAULT_LANES in block and '`.sdlc/` holds SDLC Lite tickets' in block,
               'a default repo block does not name ../<repo>.worktrees/ and .sdlc/')
        # a bare clone with lanes beside it (gen-ui-kit: <dir>/.bare, <dir>/lanes/<lane>)
        _git(root, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'x')
        kit = os.path.join(os.path.dirname(root), 'kit')
        _git(root, 'clone', '-q', '--bare', root, os.path.join(kit, '.bare'))
        lane = os.path.join(kit, 'lanes', 'lane-a')
        _git(os.path.join(kit, '.bare'), 'worktree', 'add', '-q', '--detach', lane, 'HEAD')
        block = _root_block(lane, impl)
        expect('`<bare parent>/lanes/`' in block and DEFAULT_LANES not in block,
               'a bare-clone block does not name <bare parent>/lanes/ only: %r' % block)
    with _fixture({'.sdlc/config': 'ticket_root: tickets\n'}) as root:
        block = _root_block(root, impl)
        expect('`.sdlc/tickets/` holds SDLC Lite tickets' in block,
               'a ticket_root: tickets block does not name .sdlc/tickets/: %r' % block)
    with _fixture() as root:
        block = _root_block(root, impl)
        expect('.sdlc' not in block.replace(NO_SDLC_LINE, '') and NO_SDLC_LINE in block,
               'a repo with no .sdlc/ folder gets .sdlc/ lines: %r' % block)
        expect('`%s`' % _lane_root(root) in block, 'a repo with no .sdlc/ folder lost the wtroot.root() lane line')


GATES = [
    ('block-paths', gate_block_paths, REAL, [
        ('renders the default lane and ticket roots everywhere', REAL._replace(render=_render_default_paths)),
        ('renders the .sdlc/ lines with no .sdlc/ folder', REAL._replace(render=_render_sdlc_always)),
    ]),
    ('entry-resolver', gate_entry_resolver, resolve_entries, [
        ('skips the CLAUDE.md import rule', functools.partial(resolve_entries, check_import=False)),
        ('skips the link rule', functools.partial(resolve_entries, check_links=False)),
    ]),
    ('layout-parsing', gate_layout_parsing, parse_layout, [
        ('skips the list-line form rule', functools.partial(_parse_layout, skip=frozenset({'form'}))),
        ('skips the duplicate heading rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-heading'}))),
        ('skips the duplicate home rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-home'}))),
    ]),
    ('layout-sections', gate_layout_sections, parse_layout, [
        ('skips the unknown kind rule', functools.partial(_parse_layout, skip=frozenset({'kind-unknown'}))),
        ('skips the home cross-check', functools.partial(_parse_layout, skip=frozenset({'kinds-home'}))),
        ('skips the table form rules', functools.partial(_parse_layout, skip=frozenset({'kinds-form'}))),
        ('skips the duplicate row rule', functools.partial(_parse_layout, skip=frozenset({'kinds-duplicate'}))),
        ('skips the Decide form rules', functools.partial(_parse_layout, skip=frozenset({'decide-form'}))),
        ('skips the Legacy form rule', functools.partial(_parse_layout, skip=frozenset({'legacy-form'}))),
        ('skips the Levels form rule', functools.partial(_parse_layout, skip=frozenset({'levels-form'}))),
        ('skips the Caps form rule', functools.partial(_parse_layout, skip=frozenset({'caps-form'}))),
        ('skips the duplicate heading rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-heading'}))),
    ]),
    ('layout-other-tree', gate_layout_other_tree, functools.partial(_parse_layout, docs=False), [
        ('skips the table form rules', functools.partial(_parse_layout, skip=frozenset({'kinds-form'}), docs=False)),
    ]),
    ('import-detection', gate_import_detection, has_import, [
        ('skips the code fence rule', functools.partial(_has_import, fences=False)),
    ]),
    ('digest', gate_digest, digest, [
        ('hashes without normalizing line endings', _digest_raw),
        ('returns a 16-character prefix', _digest_prefix(16)),
    ]),
    ('create', gate_create, REAL, [
        ('writes before checking every path', REAL._replace(preflight=False)),
        ('creates files without starter text', REAL._replace(render=_render_without_starter)),
    ]),
    ('nested-entries', gate_nested_entries, REAL, [
        ('creates no entry for a home or a topic under a home', REAL._replace(render=_render_without_nested)),
        ('creates an entry for a home with one document', REAL._replace(render=_render_nested_for_every_home)),
    ]),
    ('preserve', gate_preserve, REAL, [
        ('template variant writes outside the markers', REAL._replace(wrap=_wrap_writing_outside)),
    ]),
    ('idempotence', gate_idempotence, REAL, [
        ('template variant embeds a run counter', REAL._replace(render=_render_with_run_counter())),
    ]),
    ('refresh-only', gate_refresh_only, REAL, [
        ('writes every change without --init', REAL._replace(refresh=_refresh_everything)),
    ]),
    ('row-order', gate_row_order, REAL, [
        ('rows 4 and 6 swapped', REAL._replace(rows=_swap_rows(ROWS, 4, 6))),
    ]),
    ('malformed-markers', gate_malformed_markers, REAL, [
        ('treats a start marker with no end as no block',
         REAL._replace(find_block=functools.partial(_find_block, unclosed=False))),
        ('skips the code fence rule', REAL._replace(find_block=functools.partial(_find_block, fences=False))),
    ]),
    ('lane-text', gate_lane_text, REAL, [
        ('template still routes to the chain', REAL._replace(render=_render_old_route)),
        ('treats a stale block as current', REAL._replace(labels=_relabel(6, 'current'))),
    ]),
    ('layout-variant', gate_layout_variant, REAL, [
        ('renders the topics text for a flat repo', REAL._replace(render=_render_topics_always)),
        ('renders the flat text for a topics repo', REAL._replace(render=_render_flat_always)),
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
    sp.add_argument('--init', action='store_true',
                    help='also create missing entry files and docs/layout.md and append a block to an unmanaged file '
                         '(without it, setup refreshes existing managed blocks only)')
    sp.add_argument('--yes', action='store_true', help='write without asking (an interactive run asks once after the diff)')
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
        if not args.dry_run and not args.yes and sys.stdin.isatty():
            rc = run_setup(root, dry_run=True, force=args.force, init=args.init)
            if rc:
                return rc
            if input('Write these changes? [y/N] ').strip().lower() not in ('y', 'yes'):
                print('nothing written')
                return 0
        return run_setup(root, dry_run=args.dry_run, force=args.force, init=args.init)
    return run_check(root)


if __name__ == '__main__':
    sys.exit(main())
