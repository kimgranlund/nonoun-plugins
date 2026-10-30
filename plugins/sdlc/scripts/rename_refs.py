#!/usr/bin/env python3
"""Rename a tracked folder's references safely: scan, apply, check, and link-count.

Usage (run from the repository root; reads only git-tracked files):
  rename_refs.py links                       count broken relative Markdown links (tracked .md files; links in code fences or inline code are examples and not counted)
  rename_refs.py plan  OLD NEW [--map O=N] [--only GLOB]... [--skip GLOB]...   list files and occurrences a rewrite would change
  rename_refs.py apply OLD NEW [--map O=N] [--only GLOB]... [--skip GLOB]...   rewrite them in place (no git commands; run it BEFORE the move, so a moved file's own links resolve from its old folder; --skip leaves a file untouched)
  rename_refs.py check OLD [--allow GLOB]... exit 1 when a path token OLD remains outside the allowlist
  rename_refs.py selftest

OLD and NEW are repository-relative folder or file paths such as docs/validation and docs/reports. A map is tried
in order, so list a file's own map before its folder's. When the moved file is a Markdown file, its links to files
that stay are recomputed too (a depth change breaks them otherwise).
A path token is OLD at the start of text, or after whitespace, a quote, a backtick, a paren,
a bracket, '=', '|', '!', '*', or '/', and followed by '/', whitespace, a quote, a backtick, a
paren, '|', or punctuation. It is never rewritten inside a URL (a token containing '://'),
after ':' (text bound to a tag such as v0.20.7:docs/validation/x.md), or when OLD is a prefix of a
longer name (docs/validation-notes). Markdown link targets are resolved against the file's own
folder, so a relative link such as ../validation/x.md becomes ../reports/x.md. Only path text
changes; anchors survive. Dated record text is otherwise untouched.
"""
import fnmatch
import os
import re
import subprocess
import sys

TEXT_SUFFIXES = ('.md', '.py', '.sh', '.json', '.toml', '.txt', '.yml', '.yaml', '.mjs', '.js', '.ts')
LINK = re.compile(r'(\]\()([^)\s]+)(\s*(?:"[^"]*")?\))|(^\s*\[[^\]]+\]:\s*)(\S+)', re.M)
PRE_OK = r'(?<![A-Za-z0-9_.:\-])'


def tracked(root):
    out = subprocess.run(['git', '-C', root, 'ls-files', '-z'], capture_output=True, text=True, check=True).stdout
    return [p for p in out.split('\0') if p]


def read(root, rel):
    try:
        with open(os.path.join(root, rel), encoding='utf-8') as fh:
            return fh.read()
    except (UnicodeDecodeError, OSError, IsADirectoryError):
        return None


def token_regex(old):
    return re.compile(PRE_OK + re.escape(old) + r'(?=/|$|[\s`\'")\]|,.;!?*])', re.M)


def in_url(text, start):
    s = start
    while s > 0 and not text[s - 1].isspace() and text[s - 1] not in '`\'"()[]<>':
        s -= 1
    return '://' in text[s:start]


def rewrite_tokens(text, maps):
    n = 0
    for old, new in maps:
        rx = token_regex(old)
        out, last = [], 0
        for m in rx.finditer(text):
            if in_url(text, m.start()):
                continue
            out.append(text[last:m.start()])
            out.append(new)
            last = m.end()
            n += 1
        out.append(text[last:])
        text = ''.join(out)
    return text, n


def split_target(t):
    for i, ch in enumerate(t):
        if ch in '#?':
            return t[:i], t[i:]
    return t, ''


def rewrite_links(text, rel, maps, files):
    """Rewrite relative Markdown link targets whose resolved path moves."""
    folder = os.path.dirname(rel)
    n = 0

    def move(resolved):
        for old, new in maps:
            if resolved == old or resolved.startswith(old + '/'):
                return new + resolved[len(old):]
        return None

    def fix(target):
        nonlocal n
        if re.match(r'^[A-Za-z][A-Za-z0-9+.\-]*:', target) or target.startswith('#') or target.startswith('/'):
            return target
        path, tail = split_target(target)
        if not path:
            return target
        resolved = os.path.normpath(os.path.join(folder, path)).replace(os.sep, '/')
        moved = move(resolved)
        # The source file may itself have moved; compute the link from the file's NEW folder.
        new_folder = folder
        for old, new in maps:
            if rel == old or rel.startswith(old + '/'):
                new_folder = os.path.dirname(new + rel[len(old):])
                break
        if moved is None:
            if new_folder == folder:
                return target
            moved = resolved  # a link from a moved file to a file that stays: recompute it from the new folder
        newrel = os.path.relpath(moved, new_folder or '.').replace(os.sep, '/')
        if path.endswith('/') and not newrel.endswith('/'):
            newrel += '/'
        if path.startswith('./') and not newrel.startswith('.'):
            newrel = './' + newrel
        if newrel != path:
            n += 1
        return newrel + tail

    def sub(m):
        if m.group(1):
            return m.group(1) + fix(m.group(2)) + m.group(3)
        return m.group(4) + fix(m.group(5))

    return LINK.sub(sub, text), n


def plan_or_apply(root, maps, only, apply, skip=()):
    files = tracked(root)
    changed, total = [], 0
    for rel in files:
        if not rel.endswith(TEXT_SUFFIXES):
            continue
        if only and not any(fnmatch.fnmatch(rel, g) for g in only):
            continue
        if any(fnmatch.fnmatch(rel, g) for g in skip):
            continue
        text = read(root, rel)
        if text is None:
            continue
        new, n1 = rewrite_tokens(text, maps)
        n2 = 0
        if rel.endswith('.md'):
            new, n2 = rewrite_links(new, rel, maps, None)
        if new != text:
            changed.append((rel, n1 + n2))
            total += n1 + n2
            if apply:
                with open(os.path.join(root, rel), 'w', encoding='utf-8') as fh:
                    fh.write(new)
    return changed, total


FENCE = re.compile(r'^ {0,3}(```|~~~).*?^ {0,3}\1[^\n]*$', re.M | re.S)
INLINE = re.compile(r'(?<!`)(`+)(?!`)[^\n]*?(?<!`)\1(?!`)')


def strip_code(text):
    """Blank fenced blocks and inline code spans: a link-shaped string in code is an example, not a link."""
    text = FENCE.sub(lambda m: '\n' * m.group(0).count('\n'), text)
    return INLINE.sub('', text)


def link_report(root):
    files = tracked(root)
    have = set(files)
    dirs = set()
    for f in files:
        d = os.path.dirname(f)
        while d:
            dirs.add(d)
            d = os.path.dirname(d)
    broken, total = [], 0
    for rel in files:
        if not rel.endswith('.md'):
            continue
        text = read(root, rel)
        if text is None:
            continue
        for m in LINK.finditer(strip_code(text)):
            target = m.group(2) or m.group(5)
            if re.match(r'^[A-Za-z][A-Za-z0-9+.\-]*:', target) or target.startswith('#'):
                continue
            path, _ = split_target(target)
            if not path:
                continue
            total += 1
            base = '' if path.startswith('/') else os.path.dirname(rel)
            res = os.path.normpath(os.path.join(base, path.lstrip('/'))).replace(os.sep, '/')
            if res not in have and res.rstrip('/') not in dirs:
                broken.append((rel, target))
    return total, broken


def stale(root, old, allow):
    rx = token_regex(old)
    hits = []
    for rel in tracked(root):
        if any(fnmatch.fnmatch(rel, g) for g in allow):
            continue
        text = read(root, rel)
        if text is None:
            continue
        for m in rx.finditer(text):
            if in_url(text, m.start()):
                continue
            line = text.count('\n', 0, m.start()) + 1
            hits.append((rel, line))
    return hits


def parse_maps(args):
    maps, rest, i = [], [], 0
    while i < len(args):
        if args[i] == '--map' and i + 1 < len(args):
            o, _, n = args[i + 1].partition('=')
            maps.append((o.rstrip('/'), n.rstrip('/')))
            i += 2
        else:
            rest.append(args[i])
            i += 1
    return maps, rest


def collect(args, flag):
    vals, rest, i = [], [], 0
    while i < len(args):
        if args[i] == flag and i + 1 < len(args):
            vals.append(args[i + 1])
            i += 2
        else:
            rest.append(args[i])
            i += 1
    return vals, rest


def selftest():
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp()
    bad = []

    def expect(label, cond):
        if not cond:
            bad.append(label)

    try:
        def run(*a):
            return subprocess.run(['git', '-C', tmp] + list(a), capture_output=True, text=True)
        run('init', '-q')
        run('config', 'user.email', 'a@b.c')
        run('config', 'user.name', 'x')
        files = {
            'docs/validation/a.md': '# A\nsee [b](b.md) and [up](../README.md)\n',
            'docs/validation/b.md': 'text docs/validation/a.md and v0.1.0:docs/validation/a.md\n',
            'docs/README.md': '- [a](validation/a.md#top)\n- `docs/validation/b.md`\n- https://x.test/docs/validation/a.md\n- docs/validation-notes/x\n',
            'docs/topic/t.md': '[a](../validation/a.md) and (docs/validation/a.md) and "docs/validation/b.md"\n',
            'AGENTS.md': 'f=docs/validation/a.md; <repo>/docs/validation/\n',
            'docs/other.md': 'plain\n',
        }
        for rel, body in files.items():
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)) or tmp, exist_ok=True)
            with open(os.path.join(tmp, rel), 'w') as fh:
                fh.write(body)
        run('add', '-A')
        run('commit', '-qm', 'x')
        total0, broken0 = link_report(tmp)
        expect('baseline links resolve', not broken0)
        expect('stale before apply is found', len(stale(tmp, 'docs/validation', [])) >= 6)
        run('mv', 'docs/validation', 'docs/reports')
        _, broken_moved = link_report(tmp)
        expect('moving without rewriting breaks links', len(broken_moved) >= 2)
        changed, n = plan_or_apply(tmp, [('docs/validation', 'docs/reports')], [], True)
        expect('apply changed files', n >= 8 and len(changed) >= 4)
        _, broken1 = link_report(tmp)
        expect('after apply no broken links', not broken1)
        r = open(os.path.join(tmp, 'docs/README.md')).read()
        expect('relative link rewritten with anchor', '(reports/a.md#top)' in r)
        expect('url untouched', 'https://x.test/docs/validation/a.md' in r)
        expect('longer name untouched', 'docs/validation-notes/x' in r)
        t = open(os.path.join(tmp, 'docs/topic/t.md')).read()
        expect('up-link rewritten', '(../reports/a.md)' in t and '(docs/reports/a.md)' in t and '"docs/reports/b.md"' in t)
        b = open(os.path.join(tmp, 'docs/reports/b.md')).read()
        expect('tag-bound text untouched, plain rewritten', 'v0.1.0:docs/validation/a.md' in b and ' docs/reports/a.md' in b)
        ag = open(os.path.join(tmp, 'AGENTS.md')).read()
        expect('shell var and repo-qualified rewritten', 'f=docs/reports/a.md' in ag and '<repo>/docs/reports/' in ag)
        left = stale(tmp, 'docs/validation', [])
        files_left = {h[0] for h in left}
        expect('only url-free, tag-free refs removed', files_left == {'docs/reports/b.md'} or files_left == set() or files_left <= {'docs/reports/b.md', 'docs/README.md'})
        with open(os.path.join(tmp, 'docs/other.md'), 'a') as fh:
            fh.write('use docs/validation/new.md here\n')
        run('add', '-A')
        hits = stale(tmp, 'docs/validation', [])
        expect('negative control: reintroduced stale reference found', any(h[0] == 'docs/other.md' for h in hits))
        expect('allowlist suppresses it', not any(h[0] == 'docs/other.md' for h in stale(tmp, 'docs/validation', ['docs/other.md'])))
        # depth change: a moved file's link to a file that stays, and --skip, with a negative control
        for rel, body in {
            'docs/old/x.md': '[up](../README.md) [sib](y.md) [out](../../AGENTS.md)\n',
            'docs/old/y.md': '[x](x.md)\n',
            'docs/keep.md': '[x](old/x.md) docs/old/x.md\n',
            'docs/skipme.md': 'docs/old/x.md\n',
        }.items():
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            with open(os.path.join(tmp, rel), 'w') as fh:
                fh.write(body)
        run('add', '-A')
        _, b_before = link_report(tmp)
        os.makedirs(os.path.join(tmp, 'docs/specs'), exist_ok=True)
        run('mv', 'docs/old', 'docs/specs/old')
        _, b_negative = link_report(tmp)
        expect('negative control: a depth-changing move without the rewrite breaks links', len(b_negative) > len(b_before))
        run('mv', 'docs/specs/old', 'docs/old')
        ch, _n = plan_or_apply(tmp, [('docs/old', 'docs/specs/old')], [], True, ['docs/skipme.md'])
        run('mv', 'docs/old', 'docs/specs/old')
        _, b_after = link_report(tmp)
        expect('moved file links to stayers and siblings resolve after the rewrite', len(b_after) <= len(b_before))
        expect('skip leaves the file untouched', open(os.path.join(tmp, 'docs/skipme.md')).read() == 'docs/old/x.md\n' and all(c[0] != 'docs/skipme.md' for c in ch))
        expect('citing token rewritten', 'docs/specs/old/x.md' in open(os.path.join(tmp, 'docs/keep.md')).read())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for b in bad:
        print('FAIL: ' + b)
    print('rename_refs selftest: ' + ('FAIL' if bad else 'PASS'))
    return 1 if bad else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    root = os.getcwd()
    if cmd == 'selftest':
        return selftest()
    if cmd == 'links':
        total, broken = link_report(root)
        print('links: %d checked, %d broken' % (total, len(broken)))
        for rel, t in broken:
            print('  broken: %s -> %s' % (rel, t))
        return 0
    if cmd in ('plan', 'apply'):
        maps, rest = parse_maps(rest)
        only, rest = collect(rest, '--only')
        skip, rest = collect(rest, '--skip')
        if len(rest) != 2:
            print('usage: %s OLD NEW [--map O=N] [--only GLOB] [--skip GLOB]' % cmd)
            return 2
        maps = [(rest[0].rstrip('/'), rest[1].rstrip('/'))] + maps
        changed, total = plan_or_apply(root, maps, only, cmd == 'apply', skip)
        for rel, n in changed:
            print('%s %s (%d)' % ('rewrote' if cmd == 'apply' else 'would rewrite', rel, n))
        print('%s: %d files, %d references' % (cmd, len(changed), total))
        return 0
    if cmd == 'check':
        allow, rest = collect(rest, '--allow')
        if len(rest) != 1:
            print('usage: check OLD [--allow GLOB]...')
            return 2
        hits = stale(root, rest[0].rstrip('/'), allow)
        for rel, line in hits[:200]:
            print('stale: %s:%d' % (rel, line))
        print('check: %d stale references' % len(hits))
        return 1 if hits else 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
