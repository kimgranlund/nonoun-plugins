#!/usr/bin/env python3
"""Reference checks for the plugin's prompt files: agents, skills, and level overlays (T-0447).

Usage:
  prompt_lint.py [FILE ...]
  prompt_lint.py selftest

With no FILE, lint the plugin's agents/*.md, skills/*/SKILL.md, and overlays/*.md; the plugin root is
the parent of this script's folder. Read-only: reads files, writes nothing, calls no model. Prints one
line per finding, `<error|warning|info> <rule> <path>: <message>`, with the path as given (defaults
relative to the current directory), then one summary line. Exit 1 on any error, 0 otherwise, 2 on a
usage error.

Rules:
  P-1 error    agents and overlays: a `rule N` cite names a top-level numbered line (`N. `) of the role
               body. The role body of overlays/<role>.md and of agents/<role>-L<n>.md is agents/<role>.md.
  P-2 error    in code spans and fenced lines, a plugin script's subcommand and each `--flag` after it
               appear in the script's module docstring or as a quoted string literal in its source. On a
               fenced line the script counts only in command position (a folder tree's notes are prose).
  P-3 error    each ${CLAUDE_PLUGIN_ROOT}/<path> exists; a bare scripts/<name>.py, scripts/<name>.sh, or
               skills/<skill>/scripts/<name> path resolves against the skill folder (skill files) or the
               plugin root, or its basename exists nowhere in the plugin (a quoted example).
  P-4 warning  overlays/<role>.md: the smallest-level section holds `### Gap defaults`; the largest-level
               section holds `### Goal`, `### KPI`, and `### Budget` (levels from adapters/claude/levels.json).
  P-5 warning  role bodies agents/<role>.md: a `closed step` or `closed ticket` line, and the first line under
               the key section holds only allowed display strings. Statuses come from results.py.
  P-6 info     counts of prohibitions, upper-case NEVER, and vague words. Never changes the exit code.

Prior art: the prompt-wording-rules skill of github.com/kimgranlund/claude-plugins (harness/skills/
prompt-wording-rules, commit 5f9819b86b4dc77934fd36226025cec2e2a88d81) and its potency_lint.py. Nothing
is vendored from it; these rules check this plugin's own references.

Importable: Ctx, lint_text, lint_files, default_files, report, run_cli, selftest.
"""
import ast
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import results  # noqa: E402

PLUGIN_ROOT = HERE.parent
RULES = ('P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'P-6')
CITE = re.compile(r'\brules? (\d+)((?:, \d+)*(?:,? (?:and|or|to) \d+)?)')
NUMBERED = re.compile(r'^(\d+)\. ')
FENCE = re.compile(r'^\s*(```|~~~)')
INLINE = re.compile(r'(`+)(.+?)\1')
PLACEHOLDER = re.compile(r'<[^<>]*>')
CMD_SEP = re.compile(r'\|\||&&|[|;>]')
SUBCOMMAND = re.compile(r'[a-z][a-z0-9-]*')
FLAG = re.compile(r'--[A-Za-z][\w-]*')
ROOT_PATH = re.compile(r'\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`"\'()\[\]]+)')
BARE_PATH = re.compile(r'(?<![\w./${}-])((?:skills/[\w-]+/)?scripts/[\w.-]+)')
GENERATED = re.compile(r'^(?P<role>.+)-L\d+$')
CLOSED = re.compile(r'(?i)\bclosed (step|ticket)\b')
PROHIBITION = re.compile(r"(?i)\b(never|do not|don't|must not|cannot)\b")
UPPER_NEVER = re.compile(r'\bNEVER\b')
VAGUE = re.compile(r'(?i)\b(a\s+few|several|some|many|various|appropriate|appropriately|reasonable|reasonably'
                   r'|as\s+needed|if\s+needed|etc)\b')
P5_EXTRA = ('solo', 'conductor')
INTERPRETERS = ('bash', 'sh', 'exec', 'uv', 'run', 'env', 'time')
P5_SKIP = ('messenger',)


class Finding:
    def __init__(self, level, rule, path, message):
        self.level, self.rule, self.path, self.message = level, rule, path, message

    def line(self):
        return '%s %s %s: %s' % (self.level, self.rule, self.path, self.message)


class Ctx:
    """What the rules read from one plugin root: its scripts, its file names, its level table."""

    def __init__(self, root):
        self.root = Path(root)
        self.scripts = {}
        for p in sorted(self.root.glob('scripts/*.py')) + sorted(self.root.glob('skills/*/scripts/*.py')):
            self.scripts.setdefault(p.name, []).append(p)
        self.names = {p.name for p in self.root.rglob('*')
                      if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}
        lv = self.root / 'adapters' / 'claude' / 'levels.json'
        self.levels = json.loads(lv.read_text(encoding='utf-8')) if lv.is_file() else {}
        self._vocab = {}
        self._numbers = {}

    def vocab(self, base):
        """(docstring, string literals) of every plugin script with this basename."""
        if base not in self._vocab:
            doc, lits = [], set()
            for p in self.scripts.get(base, ()):
                src = p.read_text(encoding='utf-8', errors='replace')
                try:
                    tree = ast.parse(src)
                    doc.append(ast.get_docstring(tree) or '')
                    lits |= {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
                except SyntaxError:
                    lits |= set(re.findall(r'[\'"]([^\'"\n]+)[\'"]', src))
            self._vocab[base] = ('\n'.join(doc), lits)
        return self._vocab[base]

    def knows(self, base, word):
        doc, lits = self.vocab(base)
        return word in lits or re.search(r'(?<![\w-])%s(?![\w-])' % re.escape(word), doc) is not None

    def numbers(self, rel, text=None):
        """Top-level numbered line numbers of a role body (text given, or read from rel)."""
        if text is None:
            if rel not in self._numbers:
                p = self.root / rel
                self._numbers[rel] = _numbers(p.read_text(encoding='utf-8', errors='replace')) if p.is_file() else None
            return self._numbers[rel]
        return _numbers(text)


def _unfenced(text):
    """Yield (lineno, line, fenced) for each line."""
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
            yield n, line, True
            continue
        yield n, line, fenced


def _numbers(text):
    return {int(m.group(1)) for _, line, f in _unfenced(text) if not f for m in [NUMBERED.match(line)] if m}


def _code(text):
    """Yield (lineno, code, fenced) for each inline code span and each fenced line."""
    for n, line, fenced in _unfenced(text):
        if fenced:
            if not FENCE.match(line):
                yield n, line, True
            continue
        for m in INLINE.finditer(line):
            yield n, m.group(2), False


def _invoked(toks, i, first):
    """A fenced line can be prose (a folder tree with notes): there a script counts only in command position."""
    prev = toks[i - 1].rsplit('/', 1)[-1] if i else ''
    return '/' in toks[i] or (i == 0 and first) or prev.startswith('python') or prev in INTERPRETERS


def kind_of(rel):
    parts = Path(rel).parts
    if len(parts) == 2 and parts[0] == 'agents' and parts[1].endswith('.md'):
        return 'agent'
    if len(parts) == 2 and parts[0] == 'overlays' and parts[1].endswith('.md'):
        return 'overlay'
    if len(parts) == 3 and parts[0] == 'skills' and parts[2] == 'SKILL.md':
        return 'skill'
    return 'other'


def role_body(rel):
    """The plugin-relative role body that a cite in rel resolves against."""
    stem = Path(rel).stem
    if kind_of(rel) == 'overlay':
        return 'agents/%s.md' % stem
    m = GENERATED.match(stem)
    return 'agents/%s.md' % m.group('role') if m else rel


def p1(ctx, rel, text, path):
    if kind_of(rel) not in ('agent', 'overlay'):
        return []
    body = role_body(rel)
    nums = ctx.numbers(body, text if body == rel else None)
    out = []
    for n, line, _ in _unfenced(text):
        for m in CITE.finditer(line):
            missing = [x for x in re.findall(r'\d+', m.group(0)) if nums is None or int(x) not in nums]
            if missing:
                where = 'no role body %s' % body if nums is None else 'no top-level line %s in %s' % (', '.join(missing), body)
                out.append(Finding('error', 'P-1', path, 'line %d: "%s" cites %s' % (n, m.group(0), where)))
    return out


def p2(ctx, rel, text, path):
    out = []
    for n, code, fenced in _code(text):
        for k, cmd in enumerate(CMD_SEP.split(PLACEHOLDER.sub('ARG', code))):
            toks = [t.strip('\'"[](){}') for t in cmd.split()]
            for i, tok in enumerate(toks):
                base = tok.rsplit('/', 1)[-1]
                if not base.endswith('.py') or base not in ctx.scripts:
                    continue
                if fenced and not _invoked(toks, i, k == 0):
                    continue
                rest = []
                for t in toks[i + 1:]:
                    if t.rsplit('/', 1)[-1] in ctx.scripts:
                        break
                    rest.append(t)
                if rest and SUBCOMMAND.fullmatch(rest[0]) and not ctx.knows(base, rest[0]):
                    out.append(Finding('error', 'P-2', path, 'line %d: %s has no subcommand "%s"' % (n, base, rest[0])))
                for t in rest:
                    m = FLAG.match(t)
                    if m and not ctx.knows(base, m.group(0)):
                        out.append(Finding('error', 'P-2', path, 'line %d: %s has no flag "%s"' % (n, base, m.group(0))))
    return out


def p3(ctx, rel, text, path):
    out = []
    skill_dir = ctx.root / Path(rel).parent if kind_of(rel) == 'skill' else None
    for n, line, _ in _unfenced(text):
        for m in ROOT_PATH.finditer(line):
            p = m.group(1).rstrip('.,;:')
            if any(c in p for c in '<>*$') or set(p.replace('/', '')) <= {'.'}:
                continue
            if not (ctx.root / p).exists():
                out.append(Finding('error', 'P-3', path, 'line %d: ${CLAUDE_PLUGIN_ROOT}/%s does not exist' % (n, p)))
        for m in BARE_PATH.finditer(line):
            p = m.group(1).rstrip('.,;:')
            if not p.startswith('skills/') and not p.endswith(('.py', '.sh')):
                continue
            if (skill_dir is not None and (skill_dir / p).exists()) or (ctx.root / p).exists():
                continue
            if p.rsplit('/', 1)[-1] in ctx.names:
                out.append(Finding('error', 'P-3', path, 'line %d: bare path %s does not resolve; the file lives elsewhere in the plugin' % (n, p)))
    return out


def _sections(text):
    """{level key: set of ### headings} for each ## L<n> section, outside fences."""
    out, cur = {}, None
    for _, line, fenced in _unfenced(text):
        if fenced:
            continue
        m = re.match(r'^## (L\d+)\s*$', line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, set())
        elif line.startswith('## '):
            cur = None
        elif cur and line.startswith('### '):
            out[cur].add(line[4:].strip())
    return out


def p4(ctx, rel, text, path):
    if kind_of(rel) != 'overlay':
        return []
    levels = ctx.levels.get(Path(rel).stem) or {}
    if len(levels) < 2:
        return []
    keys = sorted(levels, key=lambda k: int(k[1:]))
    secs = _sections(text)
    out = []
    for key, need in ((keys[0], ('Gap defaults',)), (keys[-1], ('Goal', 'KPI', 'Budget'))):
        if key not in secs:
            continue
        for h in need:
            if h not in secs[key]:
                out.append(Finding('warning', 'P-4', path, '## %s has no ### %s heading' % (key, h)))
    return out


def p5(ctx, rel, text, path):
    stem = Path(rel).stem
    if kind_of(rel) != 'agent' or GENERATED.match(stem) or stem in P5_SKIP:
        return []
    if stem not in results.SCHEMA and stem not in P5_EXTRA:
        return []
    out = []
    if not any(CLOSED.search(line) for line in text.splitlines()):
        out.append(Finding('warning', 'P-5', path, 'no "closed step" or "closed ticket" line'))
    spec = results.SCHEMA.get(stem)
    if spec and spec['allowed']:
        allowed = [a[2] for a in spec['allowed']]
        lines = text.splitlines()
        head = next((i for i, line in enumerate(lines) if line.rstrip() == '## %s' % spec['key']), None)
        first = None
        if head is not None:
            for line in lines[head + 1:]:
                if line.startswith('## '):
                    break
                if line.strip():
                    first = line.strip()
                    break
        if first is None:
            out.append(Finding('warning', 'P-5', path, 'no first line under ## %s' % spec['key']))
        else:
            bad = [v.strip() for v in first.split(' | ') if v.strip() not in allowed]
            if bad:
                out.append(Finding('warning', 'P-5', path, '## %s names %s, not one of %s' % (
                    spec['key'], ', '.join('"%s"' % b for b in bad), ' | '.join(allowed))))
    return out


def p6(ctx, rel, text, path):
    return [Finding('info', 'P-6', path, 'prohibitions %d, NEVER %d, vague %d' % (
        len(PROHIBITION.findall(text)), len(UPPER_NEVER.findall(text)), len(VAGUE.findall(text))))]


CHECKS = (('P-1', p1), ('P-2', p2), ('P-3', p3), ('P-4', p4), ('P-5', p5), ('P-6', p6))


def lint_text(ctx, rel, text, path=None, disable=()):
    """Findings for one file: rel is its plugin-relative path (it picks the rules), path is what to print."""
    path = path or rel
    out = []
    for rule, fn in CHECKS:
        if rule not in disable:
            out.extend(fn(ctx, rel, text, path))
    return out


def rel_of(ctx, p):
    """Plugin-relative path of p; a file outside the root is placed by its trailing folders."""
    a = Path(p).resolve()
    try:
        return a.relative_to(ctx.root.resolve()).as_posix()
    except ValueError:
        pass
    if a.parent.name in ('agents', 'overlays'):
        return '%s/%s' % (a.parent.name, a.name)
    if a.name == 'SKILL.md' and a.parent.parent.name == 'skills':
        return 'skills/%s/SKILL.md' % a.parent.name
    return a.name


def default_files(root):
    root = Path(root)
    return sorted(root.glob('agents/*.md')) + sorted(root.glob('skills/*/SKILL.md')) + sorted(root.glob('overlays/*.md'))


def lint_files(ctx, files, disable=()):
    """files: (path to read, path to print) pairs."""
    out = []
    for p, shown in files:
        out.extend(lint_text(ctx, rel_of(ctx, p), Path(p).read_text(encoding='utf-8', errors='replace'), shown, disable))
    return out


def report(findings, nfiles, stream, strict=False):
    for f in findings:
        stream.write(f.line() + '\n')
    errors = sum(1 for f in findings if f.level == 'error')
    warnings = sum(1 for f in findings if f.level == 'warning')
    stream.write('prompt_lint: %d files, %d errors, %d warnings\n' % (nfiles, errors, warnings))
    return 1 if errors or (strict and warnings) else 0


def run_cli(args, root, stream, strict=False):
    ctx = Ctx(root)
    if args:
        files = [(a, a) for a in args]
    else:
        files = [(str(p), os.path.relpath(str(p))) for p in default_files(root)]
    return report(lint_files(ctx, files), len(files), stream, strict)


# --- selftest -------------------------------------------------------------------------------------

class GateFailure(Exception):
    pass


FAKE_SCRIPT = '"""Fake tool.\n\nUsage: fake.py run [--fast]\n       fake.py selftest\n"""\nFLAGS = (\'--quiet\',)\n'
LOCAL_SCRIPT = '"""Local tool.\n\nUsage: local.py check\n"""\n'
BUILDER = ('# Builder\n\n## Rules\n1. Do the step.\n2. Run the checks.\n3. Stop when blocked.\n\n'
           'The goal is a closed step. See rule 2.\n\n## Status\ndone | blocked | inherited red: <tests>\n')
BUILDER_L1 = '# Builder L1\n\nFollow rules 1 and 3.\n'
OVERLAY = ('## L1\n### Procedure\n1. Follow rule 3.\n\n### Gap defaults\n- Create a missing file.\n\n'
           '## L5\n### Goal\nA closed step.\n\n### KPI\nFirst pass.\n\n### Budget\nSixty calls.\n')
SKILL = ('# X\n\nRun `fake.py run --fast` and `fake.py selftest`, or `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fake.py" run --quiet | tee x`.\n'
         'Its helper is `scripts/local.py`; a quoted example names `scripts/util.sh`.\n'
         '```\npython3 ${CLAUDE_PLUGIN_ROOT}/skills/x/scripts/local.py check\nnotes/    a folder tree line; fake.py keeps them\n```\n')
LEVELS = {'builder': {'L1': ['sonnet', 'low'], 'L5': ['fable', 'xhigh']}, 'scout': {'L1': ['haiku', 'low']}}


def _fixture(tmp, **over):
    files = {'scripts/fake.py': FAKE_SCRIPT, 'skills/x/scripts/local.py': LOCAL_SCRIPT, 'skills/x/SKILL.md': SKILL,
             'agents/builder.md': BUILDER, 'agents/builder-L1.md': BUILDER_L1, 'overlays/builder.md': OVERLAY,
             'adapters/claude/levels.json': json.dumps(LEVELS)}
    files.update(over)
    for rel, text in files.items():
        p = Path(tmp) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    return Ctx(tmp)


def _lint(ctx, disable):
    return lint_files(ctx, [(str(p), p.relative_to(ctx.root).as_posix()) for p in default_files(ctx.root)], disable)


def _planted(rule, over, expect):
    """Gate: the clean fixture is clean; the planted defect is reported under exactly this rule."""
    def gate(disable):
        with tempfile.TemporaryDirectory() as tmp:
            loud = [f.line() for f in _lint(_fixture(tmp), disable) if f.level != 'info']
            if loud:
                raise GateFailure('the clean fixture reported %r' % loud)
        with tempfile.TemporaryDirectory() as tmp:
            got = [f for f in _lint(_fixture(tmp, **over), disable) if f.level != 'info']
            hits = [f for f in got if f.rule == rule and f.path == expect[0] and expect[1] in f.message]
            if not hits:
                raise GateFailure('the planted %s defect was not reported' % rule)
            other = [f.line() for f in got if f.rule != rule]
            if other:
                raise GateFailure('the planted %s defect was reported under another rule: %r' % (rule, other))
    return gate


def _gate_p6(disable):
    with tempfile.TemporaryDirectory() as tmp:
        text = BUILDER + "\nNEVER guess. Do not widen, don't push, never skip; it cannot. Some, several, many, etc.\n"
        ctx = _fixture(tmp, **{'agents/builder.md': text})
        got = [f for f in _lint(ctx, disable) if f.rule == 'P-6' and f.path == 'agents/builder.md']
        want = 'prohibitions 5, NEVER 1, vague 4'
        if not got or got[0].level != 'info' or got[0].message != want:
            raise GateFailure('P-6 counts were %r, not %r' % ([f.line() for f in got], want))


def _gate_exit(strict):
    """A P-5 warning and P-6 counts leave the exit code at 0."""
    import io
    with tempfile.TemporaryDirectory() as tmp:
        _fixture(tmp, **{'agents/builder.md': BUILDER.replace('a closed step', 'a done step')})
        buf = io.StringIO()
        code = run_cli([str(Path(tmp) / 'agents' / 'builder.md')], tmp, buf, strict)
        out = buf.getvalue()
        if ' P-5 ' not in out or ' P-6 ' not in out:
            raise GateFailure('the case did not report a P-5 warning and P-6 counts: %r' % out)
        if code != 0:
            raise GateFailure('a P-5 warning or P-6 counts gave exit %d' % code)


GATES = (
    ('P-1', _planted('P-1', {'overlays/builder.md': OVERLAY + '\nSee rule 9.\n'}, ('overlays/builder.md', 'rule 9'))),
    ('P-2', _planted('P-2', {'skills/x/SKILL.md': SKILL + 'Then `fake.py run --nope`.\n'}, ('skills/x/SKILL.md', '--nope'))),
    ('P-3', _planted('P-3', {'agents/builder-L1.md': BUILDER_L1 + 'Run `scripts/local.py`.\n'}, ('agents/builder-L1.md', 'scripts/local.py'))),
    ('P-4', _planted('P-4', {'overlays/builder.md': OVERLAY.replace('### Gap defaults', '### Defaults')}, ('overlays/builder.md', 'Gap defaults'))),
    ('P-5', _planted('P-5', {'agents/builder.md': BUILDER.replace('blocked | inherited', 'maybe | inherited')}, ('agents/builder.md', 'maybe'))),
    ('P-6', _gate_p6),
)


def _run_gate(name, positive, negatives):
    problems = []
    try:
        positive()
    except GateFailure as e:
        problems.append('positive failed: %s' % e)
    except Exception as e:  # noqa: BLE001
        problems.append('positive crashed: %s: %s' % (type(e).__name__, e))
    for label, neg in negatives:
        try:
            neg()
        except GateFailure:
            continue
        except Exception as e:  # noqa: BLE001
            problems.append('negative (%s) crashed: %s: %s' % (label, type(e).__name__, e))
            continue
        problems.append('negative (%s) was not rejected' % label)
    if problems:
        print('gate %s: FAIL %s' % (name, '; '.join(problems)))
        return 1
    print('gate %s: positive ok, negative ok' % name)
    return 0


def selftest():
    failed = 0
    for rule, gate in GATES:
        failed += _run_gate(rule, lambda g=gate: g(()), [('drops %s' % rule, lambda g=gate, r=rule: g((r,)))])
    failed += _run_gate('exit', lambda: _gate_exit(False), [('warnings fail the exit', lambda: _gate_exit(True))])
    print('prompt_lint selftest: %s' % ('FAIL' if failed else 'PASS'))
    return 1 if failed else 0


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args[:1] in (['-h'], ['--help']):
        sys.stdout.write(__doc__)
        return 0
    if args[:1] == ['selftest']:
        if len(args) > 1:
            sys.stderr.write('prompt_lint.py: selftest takes no arguments\n')
            return 2
        return selftest()
    for a in args:
        if a.startswith('-'):
            sys.stderr.write('prompt_lint.py: unknown option %s\n' % a)
            return 2
        if not os.path.isfile(a):
            sys.stderr.write('prompt_lint.py: %s is not a file\n' % a)
            return 2
    return run_cli(args, PLUGIN_ROOT, sys.stdout)


if __name__ == '__main__':
    sys.exit(main())
