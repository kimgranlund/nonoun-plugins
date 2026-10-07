#!/usr/bin/env python3
"""Citation resolver: open every backticked path:line in a document and check that it holds.

Usage:
  cite_check.py DOC [--root DIR] [--alias NAME=PREFIX]... [--strict]
  cite_check.py selftest

Read-only: reads DOC and the cited files, writes nothing, calls no model. A citation is a whole
backticked span of the form `path:N`, `path:N-M` or `path:N,M-K` (the path holds a letter and a `.`
or `/`, so `19:08:15` and `ID: <ns>/<name>` are not citations). Per citation it checks that the path
is a file tracked in git (evidence an untracked or git-ignored file cannot back), and that every
cited line is in the file (1 to its line count, ranges forward). Prints one line per problem,
`warning <doc>:<line>: <cite>: <problem>`, then a summary, `ok: N citations resolved in <doc>` or
`<P> of <N> citations have problems`. Exits 0 either way, so a lint starts as a warning; --strict
exits 1 on any problem. Exits 2 when DOC is missing or the root is not a git work tree.

Shorthand the resolver accepts:
  alias    `PC/x.md:3` with `PC` defined in the document as "`PC` means `plugins/pc`" (the first such
           sentence per name), or by --alias PC=plugins/pc; the alias is a leading path segment.
  bare     `x.md:3` (no slash) names the last tracked file seen earlier in the document (a backticked
           path, with or without :line) that ends in it, even when a root file has that name; else
           the root file; else the one tracked file that ends in it; else it is ambiguous or not found.
           A partial path (`a/x.md:3`) tries the root path first, then the same two fallbacks.
Skipped as not of this repository: a citation inside an `[O word ...]` group, where a word sits
between the label and the first backtick (`[O maison `a.md:2`]` names another repository). Lines
inside fenced code blocks are not read.

Limit: it proves a cited file is tracked and the line exists, not that the line says what the claim
says. A line number that drifted after an edit to the cited file still passes.
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile

CITE_RE = re.compile(r'^([^\s:<>`]+):(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)$')
SPAN_RE = re.compile(r'(?<!`)`([^`\n]+)`(?!`)')
GROUP_RE = re.compile(r'\[(O)[ \t]+([^\]\n]*)\]')
ALIAS_RE = re.compile(r'`([A-Za-z][A-Za-z0-9_]*)` means `([^`\s]+)`')


def git(root, *args):
    return subprocess.run(['git', '-C', root] + list(args), capture_output=True, text=True)


def tracked_files(root):
    r = git(root, 'ls-files', '-z')
    if r.returncode != 0:
        return None
    return sorted(x for x in r.stdout.split('\0') if x)


def is_citation(span):
    m = CITE_RE.match(span)
    if not m or not re.search(r'[A-Za-z]', m.group(1)) or not re.search(r'[./]', m.group(1)):
        return None
    return m.group(1), m.group(2)


def foreign(line, start):
    """True when the span at column start sits in an [O word ...] group: a word before the first backtick
    names another repository."""
    for g in GROUP_RE.finditer(line):
        if g.group(1) == 'O' and g.start() <= start < g.end():
            return bool(g.group(2).split('`')[0].strip())
    return False


def line_ranges(spec):
    """[(first, last)] from '3', '2-10', '1,10,4-6'."""
    out = []
    for part in spec.split(','):
        a, _, b = part.partition('-')
        out.append((int(a), int(b) if b else int(a)))
    return out


def line_count(path):
    with open(path, 'rb') as f:
        return len(f.read().decode('utf-8', 'replace').splitlines())


def resolve(path, aliases, files, seen):
    """(tracked path or None, problem or None). seen is the tracked paths cited earlier, oldest first."""
    head, _, rest = path.partition('/')
    if rest and head in aliases:
        path = aliases[head].rstrip('/') + '/' + rest
    path = path[2:] if path.startswith('./') else path
    ends = [f for f in files if f == path or f.endswith('/' + path)]
    earlier = [f for f in reversed(seen) if f in ends]
    if '/' not in path and earlier:
        return earlier[0], None
    if path in files:
        return path, None
    if earlier:
        return earlier[0], None
    if len(ends) == 1:
        return ends[0], None
    if len(ends) > 1:
        return None, 'ambiguous, matches %s; cite the full path once earlier in the document' % ', '.join(ends[:3])
    return None, None


def check(doc, root, aliases):
    """(citations checked, [(line number, cite, problem)])."""
    files = tracked_files(root)
    fileset = set(files)
    with open(doc, encoding='utf-8', errors='replace') as f:
        lines = f.read().splitlines()
    aliases = dict(aliases)
    for text in lines:
        for m in ALIAS_RE.finditer(text):
            aliases.setdefault(m.group(1), m.group(2))
    seen, found, n, fenced = [], [], 0, False
    for ln, text in enumerate(lines, 1):
        if text.lstrip().startswith('```'):
            fenced = not fenced
            continue
        if fenced:
            continue
        for sm in SPAN_RE.finditer(text):
            span = sm.group(1)
            cite = is_citation(span)
            if cite is None:
                p = span.strip()
                head, _, rest = p.partition('/')
                p = aliases[head].rstrip('/') + '/' + rest if rest and head in aliases else p
                if p in fileset:
                    seen.append(p)
                continue
            if foreign(text, sm.start()):
                continue
            n += 1
            path, spec = cite
            hit, problem = resolve(path, aliases, files, seen)
            if hit:
                seen.append(hit)
                if not os.path.isfile(os.path.join(root, hit)):
                    problem = '%s is tracked but missing from the work tree' % hit
                else:
                    total = line_count(os.path.join(root, hit))
                    for a, b in line_ranges(spec):
                        if a < 1:
                            problem = 'line %d is not a line (lines start at 1)' % a
                        elif b < a:
                            problem = 'range %d-%d runs backwards' % (a, b)
                        elif b > total:
                            problem = 'line %d is past the end (%s has %d lines)' % (b, hit, total)
                        if problem:
                            break
            elif problem is None:
                full = os.path.join(root, path)
                if os.path.isfile(full):
                    ignored = git(root, 'check-ignore', '-q', '--', path).returncode == 0
                    problem = 'exists but is %s, so no commit backs it' % ('git-ignored' if ignored else 'untracked')
                else:
                    problem = 'no tracked file matches'
            if problem:
                found.append((ln, span, problem))
    return n, found


def main(argv):
    ap = argparse.ArgumentParser(prog='cite_check.py', description=__doc__.split('\n')[0])
    ap.add_argument('doc', help='the document to check, or `selftest`')
    ap.add_argument('--root', default=None, help='the git work tree the paths resolve in (default: the one holding DOC)')
    ap.add_argument('--alias', action='append', default=[], metavar='NAME=PREFIX',
                    help='a leading path segment NAME stands for PREFIX; repeatable')
    ap.add_argument('--strict', action='store_true', help='exit 1 when any citation has a problem')
    a = ap.parse_args(argv)
    if a.doc == 'selftest':
        return selftest()
    if not os.path.isfile(a.doc):
        print('cite_check.py: %s is not a file' % a.doc, file=sys.stderr)
        return 2
    root = a.root
    if root is None:
        top = git(os.path.dirname(os.path.abspath(a.doc)), 'rev-parse', '--show-toplevel')
        root = top.stdout.strip() if top.returncode == 0 else ''
    if not root or tracked_files(root) is None:
        print('cite_check.py: %s is not a git work tree' % (root or os.path.dirname(os.path.abspath(a.doc))),
              file=sys.stderr)
        return 2
    aliases = {}
    for item in a.alias:
        name, eq, prefix = item.partition('=')
        if not eq or not name or not prefix:
            print('cite_check.py: --alias wants NAME=PREFIX, got %r' % item, file=sys.stderr)
            return 2
        aliases[name] = prefix
    n, found = check(a.doc, root, aliases)
    for ln, cite, problem in found:
        print('warning %s:%d: `%s`: %s' % (a.doc, ln, cite, problem))
    print('ok: %d citations resolved in %s' % (n, a.doc) if not found
          else '%d of %d citations have problems in %s' % (len(found), n, a.doc))
    return 1 if found and a.strict else 0


def selftest():
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    def wr(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, 'repo')
        os.makedirs(root)
        git(root, 'init', '-q')
        wr(os.path.join(root, 'src', 'a.py'), ''.join('line %d\n' % i for i in range(1, 11)))
        wr(os.path.join(root, 'pc', 'ref.md'), ''.join('r%d\n' % i for i in range(1, 6)))
        wr(os.path.join(root, 'docs', 'x', 'design.md'), 'x1\nx2\nx3\n')
        wr(os.path.join(root, 'docs', 'y', 'design.md'), ''.join('y%d\n' % i for i in range(1, 9)))
        wr(os.path.join(root, 'notes.md'), 'n1\nn2\n')
        wr(os.path.join(root, 'docs', 'x', 'notes.md'), ''.join('m%d\n' % i for i in range(1, 7)))
        wr(os.path.join(root, '.gitignore'), 'ignored.txt\n')
        wr(os.path.join(root, 'ignored.txt'), 'i\n')
        wr(os.path.join(root, 'untracked.txt'), 'u\n')
        git(root, 'add', 'src', 'pc', 'docs', 'notes.md', '.gitignore')

        good = os.path.join(root, 'good.md')
        wr(good, '\n'.join([
            '# Good',
            '`PC` means `pc`. Paths are relative to the repository root.',
            'Direct [O `src/a.py:3`], a range [O `src/a.py:2-10`], a list [O `src/a.py:1,10`].',
            'Alias [O `PC/ref.md:5`], bare unique [O `a.py:4`], partial [O `x/design.md:2`].',
            'Full `docs/x/design.md:3` then `docs/y/design.md:8`, then bare [O `design.md:6`].',
            'Bare root file [O `notes.md:2`], full `docs/x/notes.md:1`, then bare [O `notes.md:6`] means the full one.',
            'Other repository [O other `nowhere.py:9`], an [E W3C PROV, named at `src/a.py:2`] group is read.',
            'Not citations: `19:08:15`, `ID: <ns>/<name>`, `status:`, `127.0.0.1:8080`, `T-0254`.',
            '```',
            '`src/missing.py:1` sits in a fenced block and is not read',
            '```',
            '']))
        rc, out, err = run_cli(good, '--strict')
        expect('good doc: no warning, exit 0 under --strict: rc=%d %r %r' % (rc, out, err),
               rc == 0 and out.strip() == 'ok: 13 citations resolved in %s' % good)

        bad = os.path.join(root, 'bad.md')
        wr(bad, '\n'.join([
            '# Bad',
            'Past the end `src/a.py:11`.',
            'Missing `src/missing.py:1`.',
            'Untracked `untracked.txt:1`.',
            'Ignored `ignored.txt:1`.',
            'Ambiguous `design.md:1` before any full path.',
            'Backwards `src/a.py:5-2`, zero `src/a.py:0`.',
            'Second range past the end `src/a.py:1,12`.',
            'Earlier path does not cover it: `docs/x/design.md:1` then `docs/y/design.md:1` then `design.md:9`.',
            '']))
        rc, out, err = run_cli(bad)
        got = out.splitlines()
        want = [(2, 'is past the end'), (3, 'no tracked file matches'), (4, 'untracked'), (5, 'git-ignored'),
                (6, 'ambiguous'), (7, 'runs backwards'), (7, 'not a line'), (8, 'is past the end'),
                (9, 'is past the end')]
        expect('bad doc: one warning per defect, in order: rc=%d %r' % (rc, got),
               rc == 0 and len(got) == len(want) + 1
               and all(g.startswith('warning %s:%d:' % (bad, n)) and frag in g for g, (n, frag) in zip(got, want))
               and got[-1] == '9 of 11 citations have problems in %s' % bad)
        rc, out, err = run_cli(bad, '--strict')
        expect('bad doc under --strict exits 1: rc=%d' % rc, rc == 1)
        rc, out, err = run_cli(good, '--alias', 'PC=pc', '--root', root)
        expect('--alias and --root accepted: rc=%d %r' % (rc, out), rc == 0 and out.strip().startswith('ok: 13'))
        rc, out, err = run_cli(os.path.join(tmp, 'nope.md'))
        expect('missing doc exits 2: rc=%d' % rc, rc == 2)
        outside = os.path.join(tmp, 'plain')
        wr(os.path.join(outside, 'd.md'), '`a.py:1`\n')
        rc, out, err = run_cli(os.path.join(outside, 'd.md'))
        expect('a doc outside a git work tree exits 2: rc=%d %r' % (rc, err), rc == 2 and 'not a git work tree' in err)

    if misses:
        print('cite_check selftest: FAIL, these did not bite:', file=sys.stderr)
        for m in misses:
            print('  - %s' % m, file=sys.stderr)
        return 1
    print('cite_check selftest: PASS')
    return 0


def run_cli(*args):
    r = subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
