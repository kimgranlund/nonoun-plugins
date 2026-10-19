#!/usr/bin/env python3
"""Decide whether a ticket's diff needs no independent verifier: docs, records or reports only (T-0429), or the
tests-gate class of the pilot (T-0496).

Usage:
  verify_scope.py <base> [--root DIR] [--handoff FILE] [--report FILE]
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

tests-gate (T-0496, a pilot): evaluated only when the diff holds a path that is not docs-only, --handoff is given, and
<root>/.sdlc/config has the line `tests_gate: pilot`; in every other case the output is the one above. With every
condition met it prints `tests-gate` and exits 0. Otherwise it prints `tests-gate: <label>: <detail>` for the first
unmet condition and exits 1. The conditions, in the order checked:
  level           the handoff front matter `size:` is L2 (legacy M counts)
  lane            the last `- lane:` line of <task folder of the handoff dir>/skips.md is solo
  criteria        the criteria set (the bullets under `## Acceptance criteria` plus the `- Done when:` lines, outside
                  fences) is not empty and every bullet holds a command span (steps.line_spans)
  red-control     the handoff has a (red) criterion, and for each (red) span the newest `type: control` entry of
                  <records dir>/red-checkpoint.jsonl with its criterion_sha256 has phase pre-edit and result red
                  (redck.py record writes them; the attempt id is not checked)
  protected-path  no changed path outside .sdlc/ has a component agents, hooks or adapters, a basename levels.json,
                  models.json, run.sh, dispatch.py, results.py or gate_lock.py, or a component holding security,
                  secret, auth, credential or permission in any case
  size            the changed paths outside .sdlc/ are at most 8 files and 300 changed lines (added plus deleted,
                  plus every line of an untracked file; a binary file is over)
  shared-name     no name the diff removes has a dependent outside it: a quoted literal of 4 or more characters, a
                  name defined on the line (def, class, function, a line-start `X =`, a JSON "key":, a --flag) or
                  the basename of a deleted file, taken from the `-` lines outside .sdlc/ and found on no `+` line,
                  that `git grep -F -l` finds in a tracked file that is not a changed path and not under .sdlc/ or
                  docs/reports/. An added name has no dependents and is not searched
  report          only with --report: the report file is readable and, for every criterion span
                  (results.criterion_spans), holds a line with the span in backticks and `exit 0`
In protected-path, size and shared-name, `.sdlc/` also means the `work_root:` directory of <root>/.sdlc/config, when set.
The `verifier requested by <handoff>` line above is the ninth condition. Solo calls the CLI without --report, because
its report file is written after it ends; `tickets.py close` is the authority and always requires the report.
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
PILOT_RE = re.compile(r'\s*tests_gate\s*:\s*pilot\s*(?:#.*)?')
PROTECTED_DIRS = ('agents', 'hooks', 'adapters')
PROTECTED_NAMES = ('levels.json', 'models.json', 'run.sh', 'dispatch.py', 'results.py', 'gate_lock.py')
SENSITIVE = ('security', 'secret', 'auth', 'credential', 'permission')
MAX_FILES, MAX_LINES = 8, 300
QUOTED_RES = (re.compile(r"'([^'\n]{4,})'"), re.compile(r'"([^"\n]{4,})"'), re.compile(r'`([^`\n]{4,})`'))
NAME_RES = (re.compile(r'\b(?:def|class|function)\s+([A-Za-z_]\w*)'), re.compile(r'^\s*([A-Za-z_]\w*)\s*=(?!=)'),
            re.compile(r'"([^"\n]+)"\s*:'), re.compile(r'(?<![\w-])(--[A-Za-z][\w-]*)'))


def record_prefixes(root):
    """The repo-relative prefixes of the tracked work records: .sdlc/ plus the work_root of <root>/.sdlc/config, if any."""
    import roots
    try:
        return roots.record_prefixes(root)
    except (roots.Fail, OSError, ValueError):
        return ('.sdlc/',)


def outside_records(root):
    """The git pathspec of everything outside the work records."""
    return ('--', '.') + tuple(f':(exclude){p.rstrip("/")}' for p in record_prefixes(root))


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


def pilot_on(root):
    """True when <root>/.sdlc/config has a `tests_gate: pilot` line."""
    try:
        with open(os.path.join(root, '.sdlc', 'config'), encoding='utf-8') as fh:
            return any(PILOT_RE.fullmatch(ln) for ln in fh.read().splitlines())
    except OSError:
        return False


def criteria_bullets(text):
    """The criteria set of a ticket handoff: the bullets under `## Acceptance criteria` plus the `Done when:` lines,
    outside ``` fences (the lines results.criterion_spans reads its spans from)."""
    out, inside, fenced = [], False, False
    for line in text.splitlines():
        if line.startswith('## '):
            inside, fenced = line.rstrip() == '## Acceptance criteria', False
        elif line.lstrip().startswith('```'):
            fenced = not fenced
        elif not fenced and ((inside and re.match(r'\s*[-*] ', line)) or re.match(r'\s*[-*] Done when:', line)):
            out.append(line)
    return out


def protected_path(path):
    """True when one repo-relative path is one the tests-gate class never covers."""
    parts = path.split('/')
    return (any(p in PROTECTED_DIRS for p in parts) or parts[-1] in PROTECTED_NAMES
            or any(w in p.lower() for p in parts for w in SENSITIVE))


def size_problem(root, base, untracked):
    """None, or why the changed paths outside .sdlc/ are over MAX_FILES files or MAX_LINES changed lines."""
    stat = git(root, 'diff', '--numstat', '--no-renames', '-z', base, *outside_records(root))
    if stat.returncode != 0:
        raise ValueError(stat.stderr.strip() or f'git diff failed against {base}')
    files, lines = set(), 0
    for row in stat.stdout.split('\0'):
        cols = row.split('\t', 2)
        if len(cols) != 3:
            continue
        if not (cols[0].isdigit() and cols[1].isdigit()):
            return f'binary file {cols[2]}'
        files.add(cols[2])
        lines += int(cols[0]) + int(cols[1])
    for p in untracked:
        try:
            with open(os.path.join(root, p), 'rb') as fh:
                data = fh.read()
        except OSError:
            return f'unreadable file {p}'
        if b'\0' in data:
            return f'binary file {p}'
        files.add(p)
        lines += data.count(b'\n') + (1 if data and not data.endswith(b'\n') else 0)
    if len(files) > MAX_FILES:
        return f'{len(files)} files, over {MAX_FILES}'
    return f'{lines} changed lines, over {MAX_LINES}' if lines > MAX_LINES else None


def removed_names(root, base):
    """The shared-name tokens the diff against base removes outside .sdlc/, in order, a repeat once: quoted literals of
    4 or more characters, names defined on a `-` line and the basenames of deleted files, each found on no `+` line."""
    diff = git(root, 'diff', '-U0', '--no-renames', '--no-color', '--no-ext-diff', base, *outside_records(root))
    gone = git(root, 'diff', '--name-only', '--no-renames', '--diff-filter=D', '-z', base, *outside_records(root))
    if diff.returncode != 0 or gone.returncode != 0:
        raise ValueError((diff.stderr or gone.stderr).strip() or f'git diff failed against {base}')
    minus, plus, hunk = [], [], False
    for ln in diff.stdout.splitlines():
        if ln.startswith('diff --git '):
            hunk = False
        elif ln.startswith('@@'):
            hunk = True
        elif hunk and ln[:1] in '-+' and ln:
            (minus if ln[0] == '-' else plus).append(ln[1:])
    tokens = [m.group(1) for ln in minus for rx in QUOTED_RES + NAME_RES for m in rx.finditer(ln)]
    tokens += [p.split('/')[-1] for p in gone.stdout.split('\0') if p]
    added = '\n'.join(plus)
    out = []
    for t in tokens:
        if t not in out and not re.search(r'(?<![\w-])' + re.escape(t) + r'(?![\w-])', added):
            out.append(t)
    return out


def shared_name(root, base, changed):
    """None, or `<token> in <path>` for the first removed name a tracked file outside the diff still holds."""
    for t in removed_names(root, base):
        hits = git(root, 'grep', '-F', '-l', '-z', '-e', t, '--', '.',
                   *(f':(exclude){p.rstrip("/")}' for p in record_prefixes(root)), ':(exclude)docs/reports')
        for p in hits.stdout.split('\0'):
            if p and p not in changed:
                return f'{t} in {p}'
    return None


def clip(s, n=80):
    s = ' '.join(s.split())
    return s if len(s) <= n else s[:n - 3] + '...'


def tests_gate(root, base, handoff, paths, report=None, need_report=False):
    """None when the diff qualifies for the tests-gate class (T-0496), else `<label>: <detail>` for the first unmet
    condition, in the order of the module docstring."""
    import order    # local: only a pilot diff needs them, and redck imports steps
    import redck
    import results
    import steps
    try:
        with open(handoff, encoding='utf-8') as fh:
            text = fh.read()
    except OSError:
        return f'level: cannot read {handoff}'
    d = os.path.dirname(os.path.abspath(handoff))
    fm = re.match(r'---\r?\n.*?^---[ \t]*\r?$', text, re.S | re.M)
    size = re.search(r'^[ \t]*size[ \t]*:[ \t]*([^\s#]+)', fm.group(0), re.M) if fm else None
    if not size or size.group(1) not in ('L2', 'M'):
        return 'level: ' + (f'size is {size.group(1)}, not L2' if size else 'no size: line in the front matter')
    try:
        with open(os.path.join(order.task_dir(d) or d, 'skips.md'), encoding='utf-8') as fh:
            lanes = re.findall(r'(?m)^- lane:[ \t]*([^;\n]*)', fh.read())
    except OSError:
        lanes = []
    if not lanes or lanes[-1].strip() != 'solo':
        return 'lane: ' + (f'lane is {lanes[-1].strip()}, not solo' if lanes else 'no - lane: line in skips.md')
    bullets = criteria_bullets(text)
    if not bullets:
        return 'criteria: no acceptance criterion'
    for b in bullets:
        if not steps.line_spans(b):
            return f'criteria: no command span in {clip(b)}'
    reds = redck.red_items(handoff)
    if not reds:
        return 'red-control: no (red) criterion'
    controls = [e for e in redck.entries(order.records_dir(d)) if e.get('type') == 'control']
    for line, span in reds:
        key = redck.criterion_hash(line, span)
        last = next((e for e in reversed(controls) if e.get('criterion_sha256') == key), None)
        if last is None:
            return f'red-control: no control for {clip(span)}'
        if last.get('phase') != 'pre-edit':
            return f'red-control: {last.get("phase")} control for {clip(span)}'
        if last.get('result') != 'red':
            return f'red-control: control was {last.get("result")} for {clip(span)}'
    prefixes = record_prefixes(root)
    outside = [p for p in paths if not p.startswith(prefixes)]
    bad = next((p for p in outside if protected_path(p)), None)
    if bad is not None:
        return f'protected-path: {bad}'
    new = git(root, 'ls-files', '--others', '--exclude-standard', '-z').stdout.split('\0')
    why = size_problem(root, base, [p for p in new if p and not p.startswith(prefixes)])
    if why:
        return f'size: {why}'
    why = shared_name(root, base, set(outside))
    if why:
        return f'shared-name: {why}'
    if need_report:
        try:
            with open(report, encoding='utf-8') as fh:
                lines = fh.read().splitlines()
        except (OSError, TypeError, ValueError):
            return 'report: no readable solo report'
        for span in results.criterion_spans(text):
            if not any(f'`{span}`' in ln and re.search(r'\bexit 0\b', ln) for ln in lines):
                return f'report: no exit 0 line for {clip(span)}'
    return None


def scope(root, base, handoff=None, report=None, need_report=False):
    """(True, 'docs-only') when the diff against base is docs-only and its checks are green, (True, 'tests-gate') when
    the pilot is on and the diff meets every tests-gate condition, else (False, the first reason)."""
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
        if not handoff or not pilot_on(root):
            return False, bad
        why = tests_gate(root, base, handoff, paths, report, need_report)
        return (False, f'tests-gate: {why}') if why else (True, 'tests-gate')
    return (False, why) if (why := docs_problem(root) or link_problem(root)) else (True, 'docs-only')


def toplevel(cwd):
    p = git(cwd, 'rev-parse', '--show-toplevel')
    return p.stdout.strip() if p.returncode == 0 and p.stdout.strip() else None


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ['selftest']:
        return selftest()
    opt = {'--root': None, '--handoff': None, '--report': None}
    rest = []
    it = iter(argv)
    for a in it:
        if a in opt:
            v = next(it, None)
            if v is None:
                break
            opt[a] = v
        else:
            rest.append(a)
    root, handoff, report = opt['--root'], opt['--handoff'], opt['--report']
    if len(rest) != 1 or rest[0].startswith('-') or (argv and argv[-1] in opt):
        sys.stderr.write('usage: verify_scope.py <base> [--root DIR] [--handoff FILE] [--report FILE] | selftest\n')
        return 2
    top = toplevel(root or os.getcwd())
    if not top:
        sys.stderr.write('verify_scope.py: not inside a git repository\n')
        return 2
    if git(top, 'rev-parse', '--verify', '-q', rest[0] + '^{commit}').returncode != 0:
        sys.stderr.write(f'verify_scope.py: {rest[0]} is not a commit\n')
        return 2
    try:
        ok, detail = scope(top, rest[0], handoff, report, report is not None)
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

    # ---- tests-gate (T-0496): one qualifying L2 solo fixture, then one flipped property per negative control ----
    import hashlib
    import json
    RED = '- (red) `grep -q 2 tool.py`'
    SPAN = 'grep -q 2 tool.py'
    TOOL = 'x = 1\n\n\ndef helper():\n    return 1\n'

    def gate(tmp, name, size='L2', lane='solo', crit=RED, extra_crit='', tail='', phase='pre-edit', pilot=True,
             tool=TOOL.replace('x = 1', 'x = 2'), more=(), report=f'- `{SPAN}` exit 0\n', work_root=None):
        """(root, base, handoff, report) of the positive fixture with the named properties flipped."""
        r = os.path.join(tmp, name)
        os.makedirs(r)
        sh(r, 'init', '-q')
        sh(r, 'config', 'user.email', 't@t')
        sh(r, 'config', 'user.name', 't')
        put(r, 'tool.py', TOOL)
        put(r, 'other.py', 'from tool import helper\n')
        sh(r, 'add', '-A')
        sh(r, 'commit', '-qm', 'base')
        b = subprocess.run(['git', '-C', r, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        cfg = ('tests_gate: pilot\n' if pilot else '') + (f'work_root: {work_root}\n' if work_root else '')
        if cfg:
            put(r, '.sdlc/config', cfg)
        put(r, '.sdlc/t/handoff.md', f'---\nid: T-1\nsize: {size}   # level\n---\n\n## Goal\ng\n\n'
                                     f'## Acceptance criteria\n{crit}\n{extra_crit}{tail}')
        put(r, '.sdlc/t/skips.md', f'# Skips\n\n## Lane\n- lane: lean; point: p; reasons: r\n- lane: {lane}; point: p; reasons: r\n')
        key = hashlib.sha256(f'{RED}\n{SPAN}'.encode('utf-8')).hexdigest()
        put(r, '.sdlc/t/red-checkpoint.jsonl', ''.join(json.dumps(
            {'type': 'control', 'criterion_sha256': key, 'phase': ph, 'result': 'red'}) + '\n' for ph in ('pre-edit', phase)))
        put(r, '.sdlc/t/solo-L2-a.md', report)
        put(r, 'tool.py', tool)
        for rel, text in more:
            put(r, rel, text)
        return r, b, os.path.join(r, '.sdlc', 't', 'handoff.md'), os.path.join(r, '.sdlc', 't', 'solo-L2-a.md')

    def why(tmp, name, **flip):
        r, b, h, rep = gate(tmp, name, **flip)
        return scope(r, b, h, report=rep, need_report=True)[1]

    with tempfile.TemporaryDirectory() as tmp:
        r, b, h, rep = gate(tmp, 'ok')
        got = scope(r, b, h, report=rep, need_report=True)
        expect(f'tests-gate ok: a qualifying L2 solo diff with its report: {got}', got == (True, 'tests-gate'))
        expect('tests-gate ok: solo call without a report', scope(r, b, h) == (True, 'tests-gate'))
        p = subprocess.run(exe + [b, '--root', r, '--handoff', h, '--report', rep], capture_output=True, text=True)
        expect(f'tests-gate ok: cli with --report prints tests-gate and exits 0: {p.returncode} {p.stdout!r}',
               (p.returncode, p.stdout.strip()) == (0, 'tests-gate'))
        expect('tests-gate ok: legacy size M counts as L2', why(tmp, 'm', size='M') == 'tests-gate')
        got = why(tmp, 'level', size='L3')
        expect(f'tests-gate red: level: {got}', got.startswith('tests-gate: level'))
        got = why(tmp, 'lane', lane='full')
        expect(f'tests-gate red: lane: {got}', got.startswith('tests-gate: lane'))
        got = why(tmp, 'criteria', extra_crit='- the output reads well\n')
        expect(f'tests-gate red: criteria: {got}', got.startswith('tests-gate: criteria'))
        got = why(tmp, 'retro', phase='retrospective')
        expect(f'tests-gate red: red-control, a retrospective entry: {got}', got.startswith('tests-gate: red-control'))
        got = why(tmp, 'nored', crit=f'- `{SPAN}`')
        expect(f'tests-gate red: red-control, no (red) criterion: {got}', got.startswith('tests-gate: red-control'))
        got = why(tmp, 'protected', more=[('pkg/hooks/h.py', 'y = 1\n')])
        expect(f'tests-gate red: protected-path: {got}', got.startswith('tests-gate: protected-path'))
        got = why(tmp, 'size', more=[('big.py', 'y = 1\n' * 301)])
        expect(f'tests-gate red: size: {got}', got.startswith('tests-gate: size'))
        nine = [(f'docs/work/n{i}.md', 'x\n') for i in range(9)]
        got = why(tmp, 'work-default', more=nine)
        expect(f'tests-gate red: size, nine docs/work files without work_root: {got}', got.startswith('tests-gate: size'))
        got = why(tmp, 'work-size', more=nine, work_root='docs/work')
        expect(f'tests-gate ok: nine docs/work files under work_root do not count toward the file cap: {got}',
               got == 'tests-gate')
        got = why(tmp, 'work-prot-default', more=[('docs/work/auth.md', 'x\n')])
        expect(f'tests-gate red: protected-path, docs/work/auth.md without work_root: {got}',
               got.startswith('tests-gate: protected-path'))
        got = why(tmp, 'work-prot', more=[('docs/work/auth.md', 'x\n')], work_root='docs/work')
        expect(f'tests-gate ok: a sensitive name under work_root is a record, not protected: {got}', got == 'tests-gate')
        got = why(tmp, 'shared', tool=TOOL.replace('x = 1', 'x = 2').replace('helper', 'helper2'))
        expect(f'tests-gate red: shared-name: {got}', got == 'tests-gate: shared-name: helper in other.py')
        got = why(tmp, 'report', report=f'- `{SPAN}` exit 1\n')
        expect(f'tests-gate red: report: {got}', got.startswith('tests-gate: report'))
        got = why(tmp, 'verifier', tail='\nverifier: L2\n')
        expect(f'tests-gate red: the verifier line: {got}', got.startswith('verifier requested by'))
        got = why(tmp, 'off', pilot=False)
        expect(f'tests-gate red: pilot off keeps the first non-docs path: {got}', got == 'tool.py')
        r, b, h, rep = gate(tmp, 'cli-red', size='L3')
        p = subprocess.run(exe + [b, '--root', r, '--handoff', h, '--report', rep], capture_output=True, text=True)
        expect(f'cli tests-gate reason exits 1: {p.returncode} {p.stdout!r}',
               p.returncode == 1 and p.stdout.startswith('tests-gate: level'))
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
