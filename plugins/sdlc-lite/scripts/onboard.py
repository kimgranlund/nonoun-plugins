#!/usr/bin/env python3
"""Onboard a repository to SDLC Lite: entry files, docs layout, and check mode.

Usage: onboard.py setup [--dry-run] [--force]   create or update the managed files (Step 2)
       onboard.py check                         report whether every managed file is current (Step 2)
       onboard.py selftest                      run the gates on temp fixtures

Design: docs/repo-onboarding/design.md. Standard library only; runs on Python 3.9.

Importable from the same scripts/ dir: LayoutError, Layout, parse_layout, frozen_match,
scan_lines, has_import.
"""
import argparse
import collections
import functools
import os
import re
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


GATES = [
    ('layout-parsing', gate_layout_parsing, parse_layout, [
        ('skips the list-line form rule', functools.partial(_parse_layout, skip=frozenset({'form'}))),
        ('skips the duplicate heading rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-heading'}))),
        ('skips the duplicate home rule', functools.partial(_parse_layout, skip=frozenset({'duplicate-home'}))),
    ]),
    ('import-detection', gate_import_detection, has_import, [
        ('skips the code fence rule', functools.partial(_has_import, fences=False)),
    ]),
]


def selftest():
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
    sp.add_argument('--dry-run', action='store_true', help='report the actions without writing')
    sp.add_argument('--force', action='store_true', help='replace an edited managed block')
    sub.add_parser('check', help='report whether every managed file is current')
    sub.add_parser('selftest', help='run the gates on temp fixtures')
    args = ap.parse_args(argv)
    if args.cmd == 'selftest':
        return selftest()
    print('onboard.py %s: not implemented' % args.cmd, file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
