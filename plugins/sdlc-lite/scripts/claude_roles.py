#!/usr/bin/env python3
"""Generate one Claude agent definition per level-table row (Python 3.9+).

  claude_roles.py [--plugin DIR] generate [--check]
  claude_roles.py [--plugin DIR] selftest

The Claude table home is adapters/claude/levels.json: {role: {level: [model, effort]}}, the twin of
adapters/codex/models.json. A Claude sub-agent takes its effort from its definition and its model from the
Agent call, so each row gets its own definition in agents/ (T-0276):

  <role>-L<n>.md   one per pipeline-role row (builder-L3, verifier-L3, plan-reviewer-L1, ...)
  solo-L1|L2|L3.md one per solo level

Each file is the role body of agents/<role>.md verbatim, under a generated frontmatter: name, description (the
role's, without its run.sh launch sentence, plus the level), model, effort, disallowedTools (every role but
builder and solo: Edit and NotebookEdit; Write stays open for the role's one result file, which a hook scopes),
and skills (the role's own list). The verifier and plan-reviewer family remap changes only the Agent `model`
argument, so it adds no definition.

generate writes the files and removes a generated file whose row is gone. generate --check writes nothing: it
exits 1 when a generated file differs from what the table and the role file give (a hand edit, a levels.json
change not regenerated, a missing or orphaned file) and 0 otherwise. Edit agents/<role>.md or levels.json, then
generate; never edit a generated file. Exit 2 is a usage or table error.
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
SOLO = 'solo'
# Roles that edit the project. Every other role is read-only (run.sh disallows Edit, Write, and NotebookEdit).
WRITERS = ('builder', SOLO)
DISALLOWED = 'Edit, NotebookEdit'
LAUNCH_SENTENCE = ' Launched headless by scripts/run.sh.'
GENERATED_RE = re.compile(r'[a-z]+(?:-[a-z]+)*-(?:L\d|S|M|L)')  # S|M|L: the 0.21.x solo files, removed as orphans. ALIAS_OK
SOURCE_RE = re.compile(r'---\n(.*?)\n---\n(.*)', re.S)


class TableError(Exception):
    """The level table or a role file cannot produce definitions."""


def table(plugin):
    path = Path(plugin) / 'adapters' / 'claude' / 'levels.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        raise TableError('%s: cannot read: %s' % (path, e))
    if not isinstance(data, dict) or not data:
        raise TableError('%s: expected a non-empty object of roles' % path)
    for role, levels in data.items():
        if not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', role) or not isinstance(levels, dict) or not levels:
            raise TableError('%s: role %r needs an object of levels' % (path, role))
        for level, row in levels.items():
            ok_level = re.fullmatch(r'L[1-3]', level) if role == SOLO else re.fullmatch(r'L\d', level)
            if not ok_level:
                raise TableError('%s: %s level %r is not %s' % (path, role, level, 'L1, L2, or L3' if role == SOLO else 'L1 to L9'))
            if not (isinstance(row, list) and len(row) == 2 and all(isinstance(v, str) and v for v in row)):
                raise TableError('%s: %s:%s must be [model, effort]' % (path, role, level))
            if row[1] not in EFFORTS:
                raise TableError('%s: %s:%s effort %r is not one of %s' % (path, role, level, row[1], ', '.join(EFFORTS)))
            if re.search(r'\s', row[0]):
                raise TableError('%s: %s:%s model %r holds whitespace' % (path, role, level, row[0]))
    return data


def source(plugin, role):
    """(description, skills, body) of agents/<role>.md; the body is everything after the frontmatter, unchanged."""
    path = Path(plugin) / 'agents' / (role + '.md')
    try:
        text = path.read_text(encoding='utf-8')
    except OSError as e:
        raise TableError('%s: cannot read the role file for levels.json role %s: %s' % (path, role, e))
    m = SOURCE_RE.fullmatch(text)
    if not m:
        raise TableError('%s: no frontmatter' % path)
    head, body = m.groups()
    desc = re.search(r'^description: (.+)$', head, re.M)
    if not desc:
        raise TableError('%s: no one-line description' % path)
    skills = []
    if re.search(r'^skills:\s*$', head, re.M):
        skills = re.findall(r'^  - ([a-z][a-z0-9-]*)$', head.split('skills:', 1)[1], re.M)
    return desc.group(1).strip().removesuffix(LAUNCH_SENTENCE.strip()).rstrip(), skills, body


def definitions(plugin):
    """{file name: text} for every row of the table."""
    out = {}
    for role, levels in table(plugin).items():
        desc, skills, body = source(plugin, role)
        for level, (model, effort) in levels.items():
            name = '%s-%s' % (role, level)
            lines = ['---', 'name: ' + name,
                     'description: %s Level %s: %s %s.' % (desc, level, model, effort),
                     'model: ' + model, 'effort: ' + effort]
            if role not in WRITERS:
                lines.append('disallowedTools: ' + DISALLOWED)
            if skills:
                lines += ['skills:'] + ['  - ' + s for s in skills]
            out[name + '.md'] = '\n'.join(lines + ['---', '']) + body
    return out


def generated_files(plugin):
    """Names of the files in agents/ that look generated, expected or not."""
    return sorted(p.name for p in (Path(plugin) / 'agents').glob('*.md') if GENERATED_RE.fullmatch(p.stem))


def generated_stems(plugin):
    """The stems the table generates, for checks that list agents/*.md and must skip them."""
    return {name[:-3] for name in definitions(plugin)}


def problems(plugin):
    want = definitions(plugin)
    agents = Path(plugin) / 'agents'
    out = []
    for name, text in want.items():
        path = agents / name
        if not path.is_file():
            out.append('missing: agents/%s' % name)
        elif path.read_text(encoding='utf-8') != text:
            out.append('differs from the level table and role file: agents/%s' % name)
    out += ['orphan (no levels.json row): agents/%s' % n for n in generated_files(plugin) if n not in want]
    return out


def generate(plugin):
    want = definitions(plugin)
    agents = Path(plugin) / 'agents'
    written = removed = 0
    for name, text in want.items():
        path = agents / name
        if not path.is_file() or path.read_text(encoding='utf-8') != text:
            path.write_text(text, encoding='utf-8')
            written += 1
    for name in generated_files(plugin):
        if name not in want:
            (agents / name).unlink()
            removed += 1
    print('Claude agent definitions generated: %d files, %d written, %d removed' % (len(want), written, removed))


def selftest(plugin):
    failures = []

    def case(label, ok):
        print('%s: %s' % ('ok' if ok else 'FAIL', label))
        if not ok:
            failures.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / 'plugin'
        (d / 'agents').mkdir(parents=True)
        (d / 'adapters' / 'claude').mkdir(parents=True)
        for p in (Path(plugin) / 'agents').glob('*.md'):
            if not GENERATED_RE.fullmatch(p.stem):
                shutil.copyfile(str(p), str(d / 'agents' / p.name))
        levels = d / 'adapters' / 'claude' / 'levels.json'
        shutil.copyfile(str(Path(plugin) / 'adapters' / 'claude' / 'levels.json'), str(levels))

        def run(*args):
            import io
            import contextlib
            err, out = io.StringIO(), io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                code = main(['--plugin', str(d)] + list(args))
            return code

        data = json.loads(levels.read_text(encoding='utf-8'))
        rows = sum(len(v) for v in data.values())
        case('check fails before generate (files missing)', run('generate', '--check') == 1)
        case('generate exits 0', run('generate') == 0)
        names = generated_files(d)
        case('one file per table row (%d)' % rows, len(names) == rows)
        case('check passes after generate', run('generate', '--check') == 0)

        for name in ('builder-L3', 'solo-L1', 'solo-L3', 'verifier-L3', 'plan-reviewer-L1', 'architect-L1'):
            text = (d / 'agents' / (name + '.md')).read_text(encoding='utf-8')
            role = name.rsplit('-', 1)[0]
            m = SOURCE_RE.fullmatch(text)
            head, body = m.groups()
            case('%s keeps the role body verbatim' % name, body == SOURCE_RE.fullmatch((d / 'agents' / (role + '.md')).read_text(encoding='utf-8')).group(2))
            case('%s frontmatter name' % name, ('name: ' + name + '\n') in head + '\n')
            case('%s frontmatter model and effort match the row' % name, all(
                ('%s: %s\n' % (k, v)) in head + '\n' for k, v in zip(('model', 'effort'), data[role][name.rsplit('-', 1)[1]])))
            case('%s disallowedTools only for a read-only role' % name,
                 ('disallowedTools: ' + DISALLOWED in head) == (role not in WRITERS))
        skills = (d / 'agents' / 'verifier-L3.md').read_text(encoding='utf-8')
        case('verifier-L3 carries the role skills', 'skills:\n  - checks-that-bite\n  - checking-rules\n---\n' in skills)

        victim = d / 'agents' / 'builder-L1.md'
        original = victim.read_text(encoding='utf-8')
        victim.write_text(original + 'hand edit\n', encoding='utf-8')
        case('negative control: a hand-edited generated file fails check', run('generate', '--check') == 1)
        case('generate repairs the hand edit', run('generate') == 0 and victim.read_text(encoding='utf-8') == original)

        data['builder']['L1'][1] = 'high'
        levels.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        case('negative control: a levels.json effort changed without generate fails check', run('generate', '--check') == 1)
        case('generate carries the effort into the definition', run('generate') == 0 and 'effort: high\n' in victim.read_text(encoding='utf-8'))
        case('check passes again', run('generate', '--check') == 0)

        del data['scout']
        levels.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        case('negative control: a removed row leaves an orphan that fails check', run('generate', '--check') == 1)
        case('generate removes the orphan', run('generate') == 0 and not (d / 'agents' / 'scout-L1.md').exists())

        for label, mutate in (('an unknown effort', lambda t: t['planner']['L1'].__setitem__(1, 'ultra')),
                              ('a role with no role file', lambda t: t.__setitem__('ghost', {'L1': ['sonnet', 'low']})),
                              ('a solo level named S (the retired tier name)', lambda t: t['solo'].__setitem__('S', ['sonnet', 'low'])),  # ALIAS_OK
                              ('a solo level L4', lambda t: t['solo'].__setitem__('L4', ['opus', 'xhigh']))):
            bad = json.loads(json.dumps(data))
            mutate(bad)
            levels.write_text(json.dumps(bad) + '\n', encoding='utf-8')
            case('negative control: %s exits 2' % label, run('generate', '--check') == 2)
    print('claude_roles selftest: %s' % ('FAIL' if failures else 'PASS'))
    return 1 if failures else 0


def main(argv):
    ap = argparse.ArgumentParser(prog='claude_roles.py', description=__doc__.split('\n')[0])
    ap.add_argument('--plugin', default=str(PLUGIN), help='the plugin dir (default: this script\'s plugin)')
    sub = ap.add_subparsers(dest='cmd')
    sub.required = True
    gen = sub.add_parser('generate', help='write the definitions, or verify them with --check')
    gen.add_argument('--check', action='store_true', help='write nothing; exit 1 when a definition is stale')
    sub.add_parser('selftest', help='run the regression cases in a temp dir')
    args = ap.parse_args(argv)
    try:
        if args.cmd == 'selftest':
            return selftest(args.plugin)
        if args.check:
            found = problems(args.plugin)
            for line in found:
                print('claude_roles.py: ' + line, file=sys.stderr)
            if found:
                print('claude_roles.py: Claude agent definitions are stale; run: python3 plugins/sdlc-lite/scripts/claude_roles.py generate', file=sys.stderr)
                return 1
            print('Claude agent definitions verified (%d files)' % len(definitions(args.plugin)))
            return 0
        generate(args.plugin)
        return 0
    except TableError as e:
        print('claude_roles.py: ' + str(e), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
