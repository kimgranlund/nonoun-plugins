#!/usr/bin/env python3
"""Decide whether a ticket's diff is docs, records or reports only, so no independent verifier is needed (T-0429).

Usage:
  verify_scope.py <base> [--root DIR] [--handoff FILE]
  verify_scope.py selftest

Reads `git diff --name-only <base>` (the working tree against the base) plus the untracked files, then:
  exit 0, prints `docs-only`: every changed path is docs-only (see docs_only), docs_check.py is green when the
    repository has a docs/ folder, and the broken relative Markdown links equal the docs/reports/broken-links-allowlist.md rows
    (the check.py item 32 rule); no `verifier: L1`..`L3` line in --handoff asks for one.
  exit 1, prints one line: the first path that is not docs-only, `no changes against <base>`, `docs_check: <first finding>`,
    `broken link: <file> -> <target>`, or `verifier requested by <handoff>`. The verifier is still needed.
  exit 2: usage error, or <base> is not a commit.

A path is docs-only when it is under docs/; or under .sdlc/ and a record file (.md, .json, .jsonl, .txt, or the
extensionless names config and base-sha), never a script; or a *.md file with no agents, skills, commands or hooks folder in its
path (a plugin's role, skill and hook text carries behavior). Reads and writes nothing in the repository.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

RECORD_EXT = ('.md', '.json', '.jsonl', '.txt')
RECORD_NAMES = ('config', 'base-sha')
BEHAVIOR_DIRS = ('agents', 'skills', 'commands', 'hooks')
VERIFIER_LINE = re.compile(r'^verifier:[ \t]*L[123][ \t]*$', re.M)
ALLOWLIST = 'docs/reports/broken-links-allowlist.md'


def docs_path(path):
    """True when one repo-relative path is docs, a record or a report."""
    parts = path.split('/')
    name = parts[-1]
    if parts[0] == 'docs':
        return True
    if parts[0] == '.sdlc':
        return name.endswith(RECORD_EXT) or name in RECORD_NAMES
    return name.endswith('.md') and not any(p in BEHAVIOR_DIRS for p in parts[:-1])


def first_non_docs(paths):
    """The first path that is not docs-only, or None."""
    return next((p for p in paths if not docs_path(p)), None)


def docs_only(paths):
    """True when paths is non-empty and every one is docs-only. An empty change set is not docs-only."""
    paths = list(paths)
    return bool(paths) and first_non_docs(paths) is None


def git(root, *args):
    return subprocess.run(['git', '-C', root, *args], capture_output=True, text=True)


def changed_paths(root, base):
    """Sorted repo-relative paths: tracked changes against base (working tree included, no rename pairing) and untracked files."""
    tracked = git(root, 'diff', '--name-only', '--no-renames', '-z', base)
    if tracked.returncode != 0:
        raise ValueError(tracked.stderr.strip() or f'git diff failed against {base}')
    new = git(root, 'ls-files', '--others', '--exclude-standard', '-z')
    return sorted({p for out in (tracked.stdout, new.stdout) for p in out.split('\0') if p})


def link_problem(root):
    """The first broken relative Markdown link not in the allowlist, or a stale allowlist row, as a line; None when they agree."""
    import rename_refs
    ls = git(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').stdout
    real = rename_refs.tracked
    rename_refs.tracked = lambda r: [p for p in ls.split('\0') if p]  # a link to a new, uncommitted doc resolves
    try:
        broken = {tuple(b) for b in rename_refs.link_report(root)[1]}
    finally:
        rename_refs.tracked = real
    allowed = set()
    try:
        with open(os.path.join(root, ALLOWLIST), encoding='utf-8') as fh:
            allowed = {tuple(c.strip('` ') for c in ln.split('|')[1:3]) for ln in fh.read().splitlines() if ln.startswith('| `')}
    except OSError:
        pass
    for f, t in sorted(broken - allowed):
        return f'broken link: {f} -> {t}'
    return None


def docs_problem(root):
    """The first docs_check finding as a line, or None when it is green or the repository has no docs/ folder."""
    if not os.path.isdir(os.path.join(root, 'docs')):
        return None
    p = subprocess.run([sys.executable, os.path.join(HERE, 'docs_check.py'), '--root', root], capture_output=True, text=True)
    if p.returncode == 0:
        return None
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith('error ')]
    return 'docs_check: ' + (lines[0] if lines else (p.stderr.strip() or p.stdout.strip() or f'rc={p.returncode}').splitlines()[0])


def scope(root, base, handoff=None):
    """(True, 'docs-only') when the diff against base is docs-only and its checks are green, else (False, the first reason)."""
    if handoff:
        try:
            with open(handoff, encoding='utf-8') as fh:
                if VERIFIER_LINE.search(fh.read()):
                    return False, f'verifier requested by {handoff}'
        except OSError:
            pass
    paths = changed_paths(root, base)
    if not paths:
        return False, f'no changes against {base}'
    bad = first_non_docs(paths)
    if bad is not None:
        return False, bad
    return (False, why) if (why := docs_problem(root) or link_problem(root)) else (True, 'docs-only')


def toplevel(cwd):
    p = git(cwd, 'rev-parse', '--show-toplevel')
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ['selftest']:
        return selftest()
    root = handoff = None
    rest = []
    it = iter(argv)
    for a in it:
        if a in ('--root', '--handoff'):
            v = next(it, None)
            if v is None:
                break
            root, handoff = (v, handoff) if a == '--root' else (root, v)
        else:
            rest.append(a)
    if len(rest) != 1 or rest[0].startswith('-') or (argv and argv[-1] in ('--root', '--handoff')):
        sys.stderr.write('usage: verify_scope.py <base> [--root DIR] [--handoff FILE] | selftest\n')
        return 2
    top = toplevel(root or os.getcwd())
    if not top:
        sys.stderr.write('verify_scope.py: not inside a git repository\n')
        return 2
    if git(top, 'rev-parse', '--verify', '-q', rest[0] + '^{commit}').returncode != 0:
        sys.stderr.write(f'verify_scope.py: {rest[0]} is not a commit\n')
        return 2
    try:
        ok, detail = scope(top, rest[0], handoff)
    except ValueError as e:
        sys.stderr.write(f'verify_scope.py: {e}\n')
        return 2
    print(detail)
    return 0 if ok else 1


def selftest():
    import tempfile
    failed = []

    def expect(name, cond):
        if not cond:
            failed.append(name)
            sys.stderr.write(f'FAIL {name}\n')

    for p in ('docs/specs/a.md', 'docs/x.json', '.sdlc/0001-a/handoff.md', '.sdlc/0001-a/runs.jsonl', '.sdlc/config',
              '.sdlc/0001-a/step-1/base-sha', 'README.md', 'plugins/p/AGENTS.md', 'plugins/p/adapters/codex/instructions.md'):
        expect(f'docs path {p}', docs_path(p))
    for p in ('plugins/p/scripts/a.py', 'plugins/p/agents/solo.md', 'plugins/p/skills/s/SKILL.md', 'plugins/p/hooks/x.md',
              'skills/s/SKILL.md', '.claude/agents/a.md', '.claude/commands/c.md', '.sdlc/0001-a/run.sh', '.sdlc/tools/x.py',
              'plugins/p/hooks/hooks.json', 'src/a.ts', 'scripts/check.py', 'plugins/p/agents/solo-L2.toml'):
        expect(f'non-docs path {p}', not docs_path(p))
    expect('docs_only of docs', docs_only(['docs/specs/a.md', '.sdlc/t/handoff.md']))
    expect('docs_only of docs plus one script', not docs_only(['docs/specs/a.md', 'scripts/a.py']))
    expect('docs_only of nothing', not docs_only([]))
    expect('first_non_docs names the first', first_non_docs(['docs/specs/a.md', 'b.py', 'c.py']) == 'b.py')

    def sh(cwd, *a):
        subprocess.run(['git', '-C', cwd, *a], check=True, capture_output=True)

    def repo(tmp, name, red=False):
        r = os.path.join(tmp, name)
        os.makedirs(os.path.join(r, 'docs'))
        os.makedirs(os.path.join(r, '.sdlc', 't'))
        sh(r, 'init', '-q')
        sh(r, 'config', 'user.email', 't@t')
        sh(r, 'config', 'user.name', 't')
        put(r, 'docs/specs/a.md', '# a\n')
        put(r, 'docs/specs/AGENTS.md', '# Specs\n')
        put(r, 'docs/specs/CLAUDE.md', '@AGENTS.md\n')
        put(r, 'tool.py', 'x = 1\n')
        if red:
            put(r, 'docs/loose.md', '# loose\n')  # D-2: a file directly in docs/
        sh(r, 'add', '-A')
        sh(r, 'commit', '-qm', 'base')
        return r, subprocess.run(['git', '-C', r, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()

    def put(r, rel, text):
        os.makedirs(os.path.dirname(os.path.join(r, rel)), exist_ok=True)
        with open(os.path.join(r, rel), 'w', encoding='utf-8') as fh:
            fh.write(text)

    with tempfile.TemporaryDirectory() as tmp:
        r, b = repo(tmp, 'plain')
        expect('no change is not docs-only', scope(r, b) == (False, f'no changes against {b}'))
        put(r, 'docs/specs/a.md', '# a\nmore\n')
        put(r, '.sdlc/t/note.md', 'x\n')
        expect('tracked edit plus untracked record is docs-only', scope(r, b) == (True, 'docs-only'))
        h = os.path.join(r, '.sdlc', 't', 'handoff.md')
        put(r, '.sdlc/t/handoff.md', '---\nid: T-1\n---\nverifier: L2\n')
        expect('a verifier: L2 line overrides', scope(r, b, h) == (False, f'verifier requested by {h}'))
        put(r, '.sdlc/t/handoff.md', '---\nid: T-1\n---\nsee verifier: L2 in prose\n')
        expect('a verifier mention in prose does not', scope(r, b, h) == (True, 'docs-only'))
        put(r, 'tool.py', 'x = 2\n')
        expect('one script path refuses and names it', scope(r, b) == (False, 'tool.py'))
        put(r, 'tool.py', 'x = 1\n')
        put(r, 'docs/specs/a.md', '# a\n[gone](missing.md)\n')
        ok, why = scope(r, b)
        expect('a new broken link refuses', not ok and why == 'broken link: docs/specs/a.md -> missing.md')
        put(r, 'docs/specs/a.md', '# a\n[new](n.md)\n')
        put(r, 'docs/specs/n.md', '# n\n')
        expect(f'a link to an untracked new doc resolves: {scope(r, b)}', scope(r, b) == (True, 'docs-only'))
        sh(r, 'rm', '-q', '--cached', 'tool.py')
        os.remove(os.path.join(r, 'tool.py'))
        expect('a deleted script refuses', scope(r, b) == (False, 'tool.py'))
        sh(r, 'checkout', '-q', 'HEAD', '--', 'tool.py')

        r2, b2 = repo(tmp, 'schema')
        put(r2, '.sdlc/t/handoff.md', '---\nid: T-1\n---\n')
        put(r2, 'docs/specs/b.md', '# b\n[a](a.md)\n')
        expect('a clean record and doc pass docs_check', scope(r2, b2) == (True, 'docs-only'))
        r3, b3 = repo(tmp, 'red', red=True)
        put(r3, '.sdlc/t/handoff.md', '---\nid: T-1\n---\n')
        ok3, why3 = scope(r3, b3)
        expect(f'a record-only diff in a repo failing docs_check refuses: {ok3} {why3}',
               not ok3 and why3.startswith('docs_check: error D-2 docs/loose.md'))
        expect('a bad base raises', _raises(lambda: scope(r2, 'nope')))

    exe = [sys.executable, os.path.abspath(__file__)]
    with tempfile.TemporaryDirectory() as tmp:
        r, b = repo(tmp, 'cli')
        put(r, 'docs/specs/a.md', '# a\nmore\n')
        p = subprocess.run(exe + [b, '--root', r], capture_output=True, text=True)
        expect('cli docs-only exits 0', (p.returncode, p.stdout.strip()) == (0, 'docs-only'))
        put(r, 'tool.py', 'x = 2\n')
        p = subprocess.run(exe + [b, '--root', r], capture_output=True, text=True)
        expect('cli script path exits 1', (p.returncode, p.stdout.strip()) == (1, 'tool.py'))
        expect('cli bad base exits 2', subprocess.run(exe + ['nope', '--root', r], capture_output=True, text=True).returncode == 2)
        expect('cli no args exits 2', subprocess.run(exe, capture_output=True, text=True).returncode == 2)
    if failed:
        print(f'verify_scope.py selftest: {len(failed)} failed')
        return 1
    print('verify_scope.py selftest: ok')
    return 0


def _raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


if __name__ == '__main__':
    sys.exit(main())
