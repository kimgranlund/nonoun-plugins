#!/usr/bin/env python3
"""Generate one Claude agent definition per level-table row (Python 3.9+).

  claude_roles.py [--plugin DIR] generate [--check]
  claude_roles.py [--plugin DIR] selftest

The Claude table home is adapters/claude/levels.json: {role: {level: [model, effort]}}, the twin of
adapters/codex/models.json. A Claude sub-agent takes its effort from its definition and its model from the
Agent call, so each row gets its own definition in agents/ (T-0276):

  <role>-L<n>.md   one per pipeline-role row (builder-L3, verifier-L3, plan-reviewer-L1, ...)
  solo-L1|L2|L3.md one per solo level

Each file is the role body of agents/<role>.md verbatim, under a generated frontmatter, except that a row whose level
has a `## L<n>` section in overlays/<role>.md gets that section as an `## At this level` block inserted immediately
before the body's `## Output` line (insert_overlay). The frontmatter: name, description (the
role's, without its run.sh launch sentence, plus the level, serialized once as one double-quoted YAML scalar), model, effort, disallowedTools (every role but
builder, solo, and ui-designer: Edit and NotebookEdit; Write stays open for the role's one result file, which a hook scopes),
and skills (the role's own list). The verifier and plan-reviewer family remap changes only the Agent `model`
argument, so it adds no definition.

generate writes the files and removes a generated file whose row is gone. generate --check writes nothing: it
exits 1 when a generated file differs from what the table and the role file give (a hand edit, a levels.json
change not regenerated, a missing or orphaned file) and 0 otherwise. Edit agents/<role>.md, levels.json, or
overlays/<role>.md, then generate; never edit a generated file. Exit 2 is a usage, table, or overlay error.

overlays/<role>.md has no frontmatter and only `## L<n>` sections, one per level that needs one. overlay() refuses
(TableError, exit 2): a file for a role with no levels.json row, a level with no row, text before the first
section, any other `## ` line, a heading named after one of the role's results.SCHEMA sections, a section over
20 lines, and the denylist words in OVERLAY_DENY as whole words.
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import results

PLUGIN = Path(__file__).resolve().parents[1]
EFFORTS = ('low', 'medium', 'high', 'xhigh', 'max')
SOLO = 'solo'
# Roles that edit the project. Every other role is read-only (run.sh disallows Edit, Write, and NotebookEdit).
WRITERS = ('builder', SOLO, 'ui-designer')
DISALLOWED = 'Edit, NotebookEdit'
LAUNCH_SENTENCE = ' Launched headless by scripts/run.sh.'
GENERATED_RE = re.compile(r'[a-z]+(?:-[a-z]+)*-(?:L\d|S|M|L)')  # S|M|L: the 0.21.x solo files, removed as orphans. ALIAS_OK
SOURCE_RE = re.compile(r'---\n(.*?)\n---\n(.*)', re.S)
OVERLAY_MAX_LINES = 20
OVERLAY_LINE = 'You run at level %s. Where this section seems to differ from the sections above, those win.'
# Whole words only; `-` and `_` count as word characters, so PR inside another word passes.
OVERLAY_DENY = (re.compile(r'(?<![\w-])(?:push|publish|pkill|killall|run_in_background)(?![\w-])', re.I),
                re.compile(r'(?<![\w-])PR(?![\w-])'), re.compile(r'(?<![\w-])/tmp(?![\w-])'))
HEADING_RE = re.compile(r'(#{1,6})\s+(.*?)\s*#*\s*')


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
    return scalar_text(desc.group(1).strip(), path).removesuffix(LAUNCH_SENTENCE.strip()).rstrip(), skills, body


def scalar_text(raw, path):
    """The text of a one-line YAML scalar: a double-quoted one is decoded (JSON escapes, a subset of YAML's), a plain one is taken as is."""
    if not raw.startswith('"'):
        return raw
    try:
        value = json.loads(raw)
    except ValueError as e:
        raise TableError('%s: the description is not a valid double-quoted scalar: %s' % (path, e))
    if not isinstance(value, str):
        raise TableError('%s: the description is not a string' % path)
    return value


def overlay(plugin, role):
    """{level: text} from overlays/<role>.md; {} when there is no file. Raises TableError on a refused overlay."""
    path = Path(plugin) / 'overlays' / (role + '.md')
    if not path.is_file():
        return {}
    levels = table(plugin)
    if role not in levels:
        raise TableError('%s: overlay for %s, which has no levels.json role' % (path, role))
    try:
        lines = path.read_text(encoding='utf-8').split('\n')
    except OSError as e:
        raise TableError('%s: cannot read: %s' % (path, e))
    schema = set(results.SCHEMA.get(role, {}).get('sections', ()))
    sections, level = {}, None
    for n, line in enumerate(lines, 1):
        where = '%s:%d' % (path, n)
        head = re.fullmatch(r'## (L\d)', line)
        if head:
            level = head.group(1)
            if level not in levels[role]:
                raise TableError('%s: section %s has no levels.json row for %s' % (where, line, role))
            if level in sections:
                raise TableError('%s: a second %s section' % (where, line))
            sections[level] = []
            continue
        if line.startswith('## '):
            raise TableError('%s: %r is an H2 line that is not ## L<n>; use H3 or lower inside a section' % (where, line))
        if level is None:
            if line.strip():
                raise TableError('%s: text before the first ## L<n> section' % where)
            continue
        h = HEADING_RE.fullmatch(line)
        if h and h.group(2) in schema:
            raise TableError('%s: heading %r names a %s result section' % (where, line, role))
        for rx in OVERLAY_DENY:
            word = rx.search(line)
            if word:
                raise TableError('%s: %r is a word the role body owns; an overlay may not use it' % (where, word.group(0)))
        sections[level].append(line)
    out = {}
    for level, body in sections.items():
        while body and not body[0].strip():
            body = body[1:]
        while body and not body[-1].strip():
            body = body[:-1]
        if len(body) > OVERLAY_MAX_LINES:
            raise TableError('%s: section %s has %d lines; at most %d' % (path, level, len(body), OVERLAY_MAX_LINES))
        out[level] = '\n'.join(body)
    return out


def insert_overlay(body, level, text):
    """The body with the `## At this level` block inserted immediately before its `## Output` line."""
    m = re.search(r'^## Output$', body, re.M)
    if not m:
        raise TableError('the role body has no "## Output" line to insert the %s overlay before' % level)
    block = '## At this level\n%s\n\n%s\n\n' % (OVERLAY_LINE % level, text)
    return body[:m.start()] + block + body[m.start():]


def definitions(plugin):
    """{file name: text} for every row of the table."""
    out = {}
    tbl = table(plugin)
    for p in sorted((Path(plugin) / 'overlays').glob('*.md')):
        if p.stem not in tbl:
            raise TableError('%s: overlay for %s, which has no levels.json role' % (p, p.stem))
    for role, levels in tbl.items():
        desc, skills, body = source(plugin, role)
        sections = overlay(plugin, role)
        for level, (model, effort) in levels.items():
            name = '%s-%s' % (role, level)
            lines = ['---', 'name: ' + name,
                     'description: ' + json.dumps('%s Level %s: %s %s.' % (desc, level, model, effort), ensure_ascii=False),
                     'model: ' + model, 'effort: ' + effort]
            if role not in WRITERS:
                lines.append('disallowedTools: ' + DISALLOWED)
            if skills:
                lines += ['skills:'] + ['  - ' + s for s in skills]
            text = insert_overlay(body, level, sections[level]) if level in sections else body
            out[name + '.md'] = '\n'.join(lines + ['---', '']) + text
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
        if (Path(plugin) / 'overlays').is_dir():
            shutil.copytree(str(Path(plugin) / 'overlays'), str(d / 'overlays'))

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

        for name in ('builder-L1', 'builder-L3', 'solo-L1', 'solo-L3', 'verifier-L3', 'plan-reviewer-L1', 'architect-L1'):
            text = (d / 'agents' / (name + '.md')).read_text(encoding='utf-8')
            role = name.rsplit('-', 1)[0]
            m = SOURCE_RE.fullmatch(text)
            head, body = m.groups()
            role_body = SOURCE_RE.fullmatch((d / 'agents' / (role + '.md')).read_text(encoding='utf-8')).group(2)
            sections = overlay(d, role)
            level = name.rsplit('-', 1)[1]
            want = insert_overlay(role_body, level, sections[level]) if level in sections else role_body
            case('%s keeps the role body verbatim, or with its overlay before ## Output' % name, body == want)
            case('%s frontmatter name' % name, ('name: ' + name + '\n') in head + '\n')
            case('%s frontmatter model and effort match the row' % name, all(
                ('%s: %s\n' % (k, v)) in head + '\n' for k, v in zip(('model', 'effort'), data[role][name.rsplit('-', 1)[1]])))
            case('%s disallowedTools only for a read-only role' % name,
                 ('disallowedTools: ' + DISALLOWED in head) == (role not in WRITERS))
        built = (d / 'agents' / 'builder-L2.md').read_text(encoding='utf-8')
        want_desc = source(d, 'builder')[0] + ' Level L2: %s %s.' % tuple(data['builder']['L2'])
        case('builder-L2 description is one quoted scalar holding the whole text, level included',
             SOURCE_RE.fullmatch(built).group(1).split('\n')[1] == 'description: ' + json.dumps(want_desc))
        case('a double-quoted source description is decoded once (no quote characters kept)', not source(d, 'builder')[0].startswith('"'))
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

        # Overlays (T-0441): a valid table again, regenerated, then each overlay case; a refusal restores the file.
        shutil.copyfile(str(Path(plugin) / 'adapters' / 'claude' / 'levels.json'), str(levels))
        run('generate')
        ov = d / 'overlays' / 'builder.md'
        ov_text = ov.read_text(encoding='utf-8') if ov.is_file() else ''
        role_body = SOURCE_RE.fullmatch((d / 'agents' / 'builder.md').read_text(encoding='utf-8')).group(2)

        def block_before_output(level):
            text = (d / 'agents' / ('builder-%s.md' % level)).read_text(encoding='utf-8')
            at = text.find('## At this level\n' + OVERLAY_LINE % level + '\n')
            out = text.find('\n## Output\n', at)
            return at >= 0 and out > at and '\n## ' not in text[at:out]

        case('overlay: builder-L1 carries the At this level block before ## Output', block_before_output('L1'))
        case('overlay: builder-L5 carries the At this level block before ## Output', block_before_output('L5'))
        case('overlay: builder-L3 has no section and stays verbatim',
             SOURCE_RE.fullmatch((d / 'agents' / 'builder-L3.md').read_text(encoding='utf-8')).group(2) == role_body)
        shutil.move(str(d / 'overlays'), str(Path(tmp) / 'overlays-aside'))
        plain = all(SOURCE_RE.fullmatch(text).group(2) == source(d, name.rsplit('-', 1)[0])[2] for name, text in
                    ((n[:-3], t) for n, t in definitions(d).items()))
        shutil.move(str(Path(tmp) / 'overlays-aside'), str(d / 'overlays'))
        case('overlay: with no overlays/ dir every definition equals its role body', plain)
        ov.write_text(ov_text.replace('## L1\n', '## L1\nAn edit not regenerated.\n', 1), encoding='utf-8')
        case('overlay: an overlay edited without generate fails check', run('generate', '--check') == 1)
        ov.write_text(ov_text, encoding='utf-8')
        case('overlay: check passes again once the overlay is restored', run('generate', '--check') == 0)
        ghost = d / 'overlays' / 'ghost.md'
        ghost.write_text('## L1\nA role with no levels.json row.\n', encoding='utf-8')
        case('overlay: overlays/ghost.md exits 2', run('generate', '--check') == 2)
        ghost.unlink()
        for label, bad in (('an ## L9 section', ov_text + '\n## L9\nNo such row.\n'),
                           ('a ## Status heading inside a builder section', ov_text + '\n## Status\ndone\n'),
                           ('a ### Status heading inside a builder section', ov_text.replace('## L1\n', '## L1\n### Status\n', 1)),
                           ('a 21-line section', ov_text + '\n## L2\n' + ''.join('line %d\n' % i for i in range(21))),
                           ('the word push', ov_text + '\n## L2\nNever push the branch.\n'),
                           ('text before the first section', 'Preamble.\n' + ov_text)):
            ov.write_text(bad, encoding='utf-8')
            case('overlay: %s exits 2' % label, run('generate', '--check') == 2)
            ov.write_text(ov_text, encoding='utf-8')
        ov.write_text(ov_text + '\n## L2\nPRINT the npush-count and the PR-1 label.\n', encoding='utf-8')
        try:
            case('overlay: PR, push inside another word pass the denylist', overlay(d, 'builder').get('L2', '').startswith('PRINT'))
        except TableError:
            case('overlay: PR, push inside another word pass the denylist', False)
        ov.write_text(ov_text, encoding='utf-8')
        src = d / 'agents' / 'builder.md'
        src_text = src.read_text(encoding='utf-8')
        src.write_text(src_text.replace('\n## Output\n', '\n## Outputs\n'), encoding='utf-8')
        case('overlay: a role body with no ## Output line exits 2', run('generate', '--check') == 2)
        src.write_text(src_text, encoding='utf-8')
        case('overlay: check passes with every overlay restored', run('generate', '--check') == 0)
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
