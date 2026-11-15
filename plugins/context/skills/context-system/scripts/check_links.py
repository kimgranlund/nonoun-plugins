#!/usr/bin/env python3
"""Check that every link and every path a corpus names resolves, and that every shipped file is named somewhere.

Usage: check_links.py [--root DIR] [--skip DIR,DIR] [--orphans DIR,DIR] [--also DIR,DIR] [--strict]

Three rules over the text files under --root (default: the current directory):

  broken-link   A Markdown link outside a code fence whose relative target does not exist.
  stale-path    A path written in prose, a comment or a message that starts with one of the root's own top-level
                directories and names no file. This is what a moved reference leaves behind.
  example-link  (warning) A Markdown link inside a code fence that does not resolve: say it is an illustration,
                without a link, or point it at a real file.
  unreferenced  (warning) A file under --orphans (default: every top-level directory except tests, fixtures and
                evals) that no other file names, or a Markdown file at the root that no other file names. The
                files a host or a convention names are never reported (AGENTS.md, CLAUDE.md, CLAUDE.local.md,
                GEMINI.md, SKILL.md and any README, INDEX, LICENSE, CHANGELOG or CONTRIBUTING). Where the root has
                none of those, a root file that names another file may be the entry under a name of its own, so it
                is not reported either. With
                --orphans, the root is checked only when the list holds a dot (`--orphans .,docs`).

What it does not look at: only files under --root with a text suffix (.md, .py, .yaml, .yml, .json, .txt, .toml) are
read, so a shell script, a build file or anything outside the root that names a file is not seen. A file reported as
unreferenced may still have such a reader; `check_move.py --consumers DIR` searches a folder outside the root for one.

Files under tests, fixtures and evals hold deliberate bad cases: their text is not scanned and they are not checked as
orphans, but a file they name counts as named.

Links with a scheme (https:, mailto:) and bare #anchors are not checked. A path holding a placeholder (<, >, *, {)
is not checked. --skip names directories to leave out entirely (default: .git, __pycache__, node_modules).
--also names top-level directories that are not under the root but whose paths must still not be written, such as the
folders a package leaves out.

Each finding is one line: SEVERITY RULE FILE:LINE: problem. Fix: fix.
Exit 0 when there are no errors (warnings allowed unless --strict), 1 on errors, 2 when --root cannot be read.
Standard library only; runs on Python 3.9.
"""
import argparse
import re
import sys
from collections import namedtuple
from pathlib import Path

TEXT = {'.md', '.py', '.yaml', '.yml', '.json', '.txt', '.toml'}
SKIP = ('.git', '__pycache__', 'node_modules')
ENTRY_NAMES = {'agents.md', 'claude.md', 'claude.local.md', 'gemini.md', 'skill.md'}
ENTRY_STEMS = ('readme', 'index', 'license', 'changelog', 'contributing')  # a root file whose name starts with one of these
EXAMPLES = ('tests', 'fixtures', 'evals')  # hold deliberate bad cases: not scanned, not checked as orphans; they still count as referrers
LINK = re.compile(r'\[[^\]\n]*\]\(([^)\s]+)\)')
PLACEHOLDER = re.compile(r'[<>*{}]')


class Finding(namedtuple('Finding', 'severity rule where problem fix')):
    def line(self):
        return f'{self.severity} {self.rule} {self.where}: {self.problem} Fix: {self.fix}'


def files_under(root, skip):
    return sorted(p for p in root.rglob('*') if p.is_file() and not set(p.relative_to(root).parts[:-1]) & set(skip)
                  and p.name != '.DS_Store')


def check(root, skip=SKIP, orphans=None, also=()):
    files = files_under(root, skip)
    tops = sorted({p.relative_to(root).parts[0] for p in files if len(p.relative_to(root).parts) > 1} | set(also))
    path_token = re.compile(r'(?<![\w./-])((?:%s)/[\w./-]*\.\w+)' % '|'.join(map(re.escape, tops))) if tops else None
    findings, texts = [], {}
    for f in files:
        if f.suffix not in TEXT:
            continue
        try:
            texts[f] = f.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
    for f, text in texts.items():
        rel, fenced = f.relative_to(root), False
        if rel.parts[0] in EXAMPLES:
            continue
        for n, line in enumerate(text.split('\n'), 1):
            if f.suffix == '.md' and line.lstrip().startswith('```'):
                fenced = not fenced
                continue
            where = f'{rel}:{n}'
            if f.suffix == '.md':
                for m in LINK.finditer(line):
                    target = m.group(1).split('#')[0]
                    if not target or re.match(r'[a-z][a-z0-9+.-]*:', target, re.I) or PLACEHOLDER.search(target):
                        continue
                    if (f.parent / target).exists():
                        continue
                    if fenced:
                        findings.append(Finding('WARNING', 'example-link', where, f'link to {target} in an example does not resolve.',
                                                'name the path without a link and say it is an illustration, or link a real file.'))
                    else:
                        findings.append(Finding('ERROR', 'broken-link', where, f'link to {target} does not resolve.',
                                                'point it at the file\'s present path, or remove the link.'))
            if path_token is None or fenced:
                continue
            for m in path_token.finditer(line):
                token = m.group(1).rstrip('.')
                if PLACEHOLDER.search(token) or (root / token).exists() or (f.parent / token).exists():
                    continue
                findings.append(Finding('ERROR', 'stale-path', where, f'{token} names no file under the root.',
                                        'write the file\'s present path.'))
    scope = orphans if orphans is not None else [t for t in tops if t not in EXAMPLES]
    is_entry = lambda p: p.name.lower() in ENTRY_NAMES or p.name.lower().startswith(ENTRY_STEMS)  # noqa: E731
    has_entry = any(is_entry(p) for p in files if len(p.relative_to(root).parts) == 1)
    for f in files:
        rel = f.relative_to(root)
        if len(rel.parts) < 2:
            name = f.name.lower()
            if f.suffix != '.md' or name in ENTRY_NAMES or name.startswith(ENTRY_STEMS) or (orphans is not None and '.' not in orphans):
                continue
            if not has_entry and any(other.name in texts.get(f, '') for other in files if other != f):
                continue  # no recognised entry at the root, and it names another file: possibly the entry
        elif rel.parts[0] not in scope:
            continue
        if not any(f.name in text for other, text in texts.items() if other != f):
            findings.append(Finding('WARNING', 'unreferenced', str(rel), 'no other file names it.',
                                    'link it from the file that uses it, or remove it; a reader outside the corpus is not seen here '
                                    '(check_move.py --consumers DIR finds one).'))
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--root', default='.')
    ap.add_argument('--skip', default=','.join(SKIP))
    ap.add_argument('--orphans', default=None)
    ap.add_argument('--also', default='')
    ap.add_argument('--strict', action='store_true')
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f'ERROR read {root}: not a directory. Fix: pass the corpus root with --root.')
        return 2
    findings = check(root.resolve(), tuple(x for x in args.skip.split(',') if x),
                     None if args.orphans is None else [x for x in args.orphans.split(',') if x],
                     tuple(x for x in args.also.split(',') if x))
    for f in findings:
        print(f.line())
    errors = sum(f.severity == 'ERROR' for f in findings)
    warnings = len(findings) - errors
    print(f'check_links: {errors} error(s), {warnings} warning(s)')
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == '__main__':
    sys.exit(main())
