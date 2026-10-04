#!/usr/bin/env python3
"""One declared result schema per role, and the validator every role result passes before the pipeline reads it.

Usage: results.py validate <result.md> [--role R]   exit 0, or print one "results.py: <file>: <reason>" line and exit 1
       results.py schema [--role R]                 print <role> TAB <key> TAB <allowed|-> TAB <sections>, one line per role
       results.py key <role>                        print the key section name of the role
       results.py selftest                          prove the rules on temp fixtures

SCHEMA below is the only copy of the table. Each role has a key section (required), an allowed set for the
key section's first non-blank line (empty when the role has none), and the declared section order taken from
the "## " lines of the output template in agents/<role>.md. Only the key section is required; any other
declared section is optional, but the declared sections that are present must appear in the declared order
(first occurrences). Undeclared "## " headings (a planner's "## Step <n>: ...") are ignored.

Parsing matches run.sh and steps.section(): a heading matches when line.rstrip() == "## <Name>"; a section's
body runs to the next line starting with "## "; the key value is the first non-blank body line, stripped and
lowercased, and must re.fullmatch one allowed regex. The first line must be the header run.sh writes:
<!-- role=<r> level=<L> model=<m> effort=<e>[ key=value ...] -->.

Importable from the same scripts/ dir: SCHEMA, ROLES, validate, structure_error, key_value.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

_INHERITED = ('inherited', r'inherited red: .+', 'inherited red: <tests>')

SCHEMA = {
    'builder': {
        'key': 'Status',
        'allowed': (('done', r'done', 'done'), ('blocked', r'blocked', 'blocked'), _INHERITED),
        'sections': ('Status', 'Changes', 'Checks', 'Notes'),
    },
    'verifier': {
        'key': 'Verdict',
        'allowed': (('pass', r'pass', 'pass'), ('fail', r'fail', 'fail'), _INHERITED),
        'sections': ('Verdict', 'Criteria', 'Out of scope changes', 'For the next attempt'),
    },
    'plan-reviewer': {
        'key': 'Verdict',
        'allowed': (('pass', r'pass', 'pass'), ('replan', r'replan', 'replan'), ('blocked', r'blocked', 'blocked')),
        'sections': ('Verdict', 'Findings', 'Missing decisions'),
    },
    'planner': {'key': 'Goal', 'allowed': (), 'sections': ('Goal', 'Assumptions', 'Risks')},
    'researcher': {'key': 'Answer', 'allowed': (), 'sections': ('Answer', 'Findings', 'Conflicts and gaps')},
    'scout': {'key': 'Map', 'allowed': (), 'sections': ('Map', 'Entry points', 'Not found')},
    'archaeologist': {'key': 'Summary', 'allowed': (), 'sections': ('Summary', 'Decisions', 'Landmines', 'Inferred')},
    'architect': {
        'key': 'Approach', 'allowed': (),
        'sections': ('Approach', 'Interfaces', 'Constraints and assumptions', 'Rejected alternatives', 'Risks'),
    },
    'filer': {
        'key': 'Warnings', 'allowed': (),
        'sections': ('Warnings', 'PR title', 'PR body', 'Changelog entry', 'Follow-ups'),
    },
}
ROLES = tuple(SCHEMA)

HEADER = re.compile(r'^<!-- role=([a-z-]+) level=(L[1-5]) model=(\S+) effort=(\S+)((?: [a-z_]+=\S+)*) -->$')
HEADER_REASON = 'first line is not a <!-- role=<r> level=<L> model=<m> effort=<e> --> header'


def displays(role):
    return '|'.join(a[2] for a in SCHEMA[role]['allowed'])


def _lines(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read().splitlines()


def _first_heading(lines, name):
    """Index of the first line that is the heading '## <name>', or None."""
    want = f'## {name}'
    return next((i for i, line in enumerate(lines) if line.rstrip() == want), None)


def _key_body_value(lines, name):
    """(present, value): value is the first non-blank line under the heading, stripped ('' when none)."""
    i = _first_heading(lines, name)
    if i is None:
        return False, ''
    for rest in lines[i + 1:]:
        if rest.startswith('## '):
            break
        if rest.strip():
            return True, rest.strip()
    return True, ''


def _token(role, value):
    """The allowed token the value matches (case-insensitive), or None."""
    low = value.lower()
    return next((tok for tok, rx, _ in SCHEMA[role]['allowed'] if re.fullmatch(rx, low)), None)


def _check(path, role, value_checks):
    if role is not None and role not in SCHEMA:
        raise ValueError(f'unknown role {role}')
    if not os.path.isfile(path):
        return 'no such file'
    try:
        lines = _lines(path)
    except OSError as e:
        return f'cannot read: {e.strerror}'
    if not any(line.strip() for line in lines):
        return 'empty result'
    m = HEADER.match(lines[0].rstrip())
    if not m:
        return HEADER_REASON
    head_role = m.group(1)
    if head_role not in SCHEMA:
        return f'unknown role {head_role} in header'
    if role is not None and head_role != role:
        return f'header role={head_role} does not match --role {role}'
    role = head_role
    spec = SCHEMA[role]
    key = spec['key']
    if value_checks or not spec['allowed']:
        present, value = _key_body_value(lines, key)
        if not present:
            return f'lacks ## {key}' + (f' ({displays(role)})' if spec['allowed'] else '')
        if spec['allowed'] and _token(role, value) is None:
            return f'## {key} first line "{value}" is not one of {displays(role)}'
    # Declared sections present, in file order of their first occurrence.
    found = []
    for name in spec['sections']:
        i = _first_heading(lines, name)
        if i is not None:
            found.append((i, name))
    found.sort()
    pos = {name: n for n, name in enumerate(spec['sections'])}
    for (_, above), (_, cur) in zip(found, found[1:]):
        if pos[cur] < pos[above]:
            return f'## {above} comes before ## {cur}'
    return None


def validate(path, role=None):
    """None when the result at path is valid, else one reason string."""
    return _check(path, role, True)


def structure_error(path, role=None):
    """validate() without the key presence and value checks for roles with an allowed set."""
    return _check(path, role, False)


def key_value(path, role):
    """The allowed token for the key section's value, or None. Ignores the header; never raises."""
    try:
        spec = SCHEMA.get(role)
        if not spec or not spec['allowed']:
            return None
        present, value = _key_body_value(_lines(path), spec['key'])
        return _token(role, value) if present else None
    except Exception:
        return None


def schema_lines(role=None):
    out = []
    for r in ROLES:
        if role is None or r == role:
            s = SCHEMA[r]
            out.append('\t'.join((r, s['key'], displays(r) or '-', '|'.join(s['sections']))))
    return out


def _steps_cases(case):
    """steps.py next, run as a subprocess from this scripts/ dir, refuses a headerless builder result;
    a copy beside an accept-all results.py does not (the negative control)."""
    here = os.path.dirname(os.path.abspath(__file__))
    with tempfile.TemporaryDirectory(prefix='results-steps-') as tmp:
        d = os.path.join(tmp, 'step-1')
        os.mkdir(d)
        with open(os.path.join(d, 'handoff.md'), 'w', encoding='utf-8') as f:
            f.write('## Task goal\ng\n\n## Step 1: x\nlevel: L2\n')
        with open(os.path.join(d, 'runs.jsonl'), 'w', encoding='utf-8') as f:
            f.write('{"file": "builder-L2.md"}\n')
        builder = os.path.join(d, 'builder-L2.md')

        def first_line(steps_py):
            p = subprocess.run([sys.executable, steps_py, 'next', d], capture_output=True, text=True)
            return (p.stdout.splitlines() or [f'(rc={p.returncode}, no stdout: {p.stderr.strip()})'])[0]

        with open(builder, 'w', encoding='utf-8') as f:
            f.write('## Status\ndone\n')
        got = first_line(os.path.join(here, 'steps.py'))
        ok = got.startswith('invalid result:') and 'builder-L2.md: ' in got
        case('steps.py next on a headerless builder result prints invalid result, not verify',
             True if ok else got, True)
        accept = os.path.join(tmp, 'accept-all')
        os.mkdir(accept)
        for name in ('steps.py', 'order.py', 'results.py'):
            shutil.copy(os.path.join(here, name), os.path.join(accept, name))
        with open(os.path.join(accept, 'results.py'), 'a', encoding='utf-8') as f:
            f.write('\nvalidate = lambda path, role=None: None\nstructure_error = lambda path, role=None: None\n')
        case('negative control: an accept-all results.py lets steps.py next print verify',
             first_line(os.path.join(accept, 'steps.py')), 'verify L1')
        with open(builder, 'w', encoding='utf-8') as f:
            f.write('<!-- role=builder level=L2 model=opus effort=low -->\n## Status\ndone\n')
        case('steps.py next on a valid builder result prints verify L1',
             first_line(os.path.join(here, 'steps.py')), 'verify L1')


def selftest():
    misses = []
    tmp = tempfile.mkdtemp(prefix='results-selftest-')

    def write(name, text):
        p = os.path.join(tmp, name)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
        return p

    def head(role, extra=''):
        return f'<!-- role={role} level=L2 model=sonnet effort=medium{extra} -->\n'

    def case(name, got, want):
        if got == want:
            print(f'ok: {name}')
        else:
            misses.append(name)
            print(f'MISS: {name}: got {got!r}, want {want!r}', file=sys.stderr)

    bodies = {
        'builder': '## Status\ndone\n\n## Changes\na.py\n\n## Checks\nx: ok\n\n## Notes\nNone\n',
        'verifier': '## Verdict\npass\n\n## Criteria\n1. ok\n\n## Out of scope changes\nNone\n\n## For the next attempt\nNone\n',
        'plan-reviewer': '## Verdict\nreplan\n\n## Findings\n- x\n\n## Missing decisions\nNone\n',
        'planner': '## Goal\ng\n\n## Step 1: a\ndo\n\n## Step 2: b\ndo\n\n## Assumptions\n- a\n\n## Risks\n- r\n',
        'researcher': '## Answer\na\n\n## Findings\nf\n\n## Conflicts and gaps\nNone\n',
        'scout': '## Map\nm\n\n## Entry points\ne\n\n## Not found\nNone\n',
        'archaeologist': '## Summary\ns\n\n## Decisions\nd\n\n## Landmines\nl\n\n## Inferred\ni\n',
        'architect': '## Approach\na\n\n## Interfaces\ni\n\n## Constraints and assumptions\nc\n\n'
                     '## Rejected alternatives\nr\n\n## Risks\nr\n',
        'filer': '## Warnings\nNone\n\n## PR title\nt\n\n## PR body\nb\n\n## Changelog entry\nc\n\n## Follow-ups\nNone\n',
    }
    case('the schema covers the nine roles', set(bodies), set(ROLES))
    for role, body in bodies.items():
        case(f'a valid {role} result passes', validate(write(f'{role}-ok.md', head(role) + body)), None)
        case(f'a valid {role} result passes with --role', validate(write(f'{role}-ok2.md', head(role) + body), role), None)
    case('a header with shared_with_builder=yes passes',
         validate(write('shared.md', head('verifier', ' shared_with_builder=yes') + '## Verdict\nfail\n')), None)
    case('only the key section is required (verifier)', validate(write('only-v.md', head('verifier') + '## Verdict\npass\n')), None)
    for role in ('builder', 'verifier'):
        key = SCHEMA[role]['key']
        case(f'{role} accepts inherited red: test_a',
             validate(write(f'{role}-inh.md', head(role) + f'## {key}\ninherited red: test_a\n')), None)
        case(f'{role} rejects bare inherited red',
             validate(write(f'{role}-bare.md', head(role) + f'## {key}\ninherited red\n')),
             f'## {key} first line "inherited red" is not one of {displays(role)}')
    case('a value is read case-insensitively', validate(write('upper.md', head('builder') + '## Status\nDone\n')), None)
    case('a missing builder Status fails',
         validate(write('nostatus.md', head('builder') + '## Changes\na\n')),
         'lacks ## Status (done|blocked|inherited red: <tests>)')
    case('a missing scout Map fails', validate(write('nomap.md', head('scout') + '## Entry points\ne\n')), 'lacks ## Map')
    case('an empty planner Goal body passes', validate(write('emptygoal.md', head('planner') + '## Goal\n\n## Risks\nr\n')), None)
    for role in ('builder', 'verifier', 'plan-reviewer'):
        key = SCHEMA[role]['key']
        case(f'{role} rejects maybe',
             validate(write(f'{role}-maybe.md', head(role) + f'## {key}\nmaybe\n')),
             f'## {key} first line "maybe" is not one of {displays(role)}')
    case('a result with no header fails', validate(write('nohead.md', '## Status\ndone\n'), 'builder'), HEADER_REASON)
    case('a header without level= fails',
         validate(write('nolevel.md', '<!-- role=builder model=sonnet effort=low -->\n## Status\ndone\n')), HEADER_REASON)
    case('an empty file fails', validate(write('empty.md', ''), 'scout'), 'empty result')
    case('a whitespace-only file fails', validate(write('blank.md', '\n  \n'), 'scout'), 'empty result')
    case('a missing file fails', validate(os.path.join(tmp, 'absent.md')), 'no such file')
    case('an unknown header role fails',
         validate(write('unk.md', head('poet') + '## Status\ndone\n')), 'unknown role poet in header')
    case('a role mismatch fails',
         validate(write('mismatch.md', head('builder') + '## Status\ndone\n'), 'verifier'),
         'header role=builder does not match --role verifier')
    case('a verifier with Criteria before Verdict fails',
         validate(write('order-v.md', head('verifier') + '## Criteria\nx\n\n## Verdict\npass\n')),
         '## Criteria comes before ## Verdict')
    case('a builder with Checks before Changes fails',
         validate(write('order-b.md', head('builder') + '## Status\ndone\n\n## Checks\nx\n\n## Changes\ny\n')),
         '## Checks comes before ## Changes')
    case('structure_error ignores a missing builder Status',
         structure_error(write('se-b.md', head('builder') + '## Changes\na\n\n## Notes\nn\n')), None)
    case('structure_error ignores a disallowed builder Status',
         structure_error(write('se-b2.md', head('builder') + '## Status\nmaybe\n')), None)
    case('structure_error still reports a planner missing Goal',
         structure_error(write('se-p.md', head('planner') + '## Assumptions\na\n')), 'lacks ## Goal')
    case('structure_error still enforces order',
         structure_error(write('se-o.md', head('builder') + '## Notes\nn\n\n## Changes\nc\n')), '## Notes comes before ## Changes')
    kv_v = key_value(write('kv-v.md', '## Verdict\npass\n'), 'verifier')
    kv_b = key_value(write('kv-b.md', '## Status\ninherited red: t\n'), 'builder')
    case('key_value reads the key value of a headerless result', (kv_v, kv_b), ('pass', 'inherited'))
    case('key_value returns None for a missing file', key_value(os.path.join(tmp, 'absent.md'), 'builder'), None)
    case('key_value returns None for a disallowed value', key_value(write('kv-x.md', '## Status\nmaybe\n'), 'builder'), None)
    case('key_value returns None for an unknown role', key_value(write('kv-u.md', '## Status\ndone\n'), 'poet'), None)
    case('schema prints the plan-reviewer line',
         schema_lines('plan-reviewer'), ['plan-reviewer\tVerdict\tpass|replan|blocked\tVerdict|Findings|Missing decisions'])
    case('schema prints - for a role with no allowed set', schema_lines('scout'), ['scout\tMap\t-\tMap|Entry points|Not found'])

    for name in os.listdir(tmp):
        os.remove(os.path.join(tmp, name))
    os.rmdir(tmp)
    _steps_cases(case)
    if misses:
        print(f'results selftest: FAIL ({len(misses)} missed: {", ".join(misses)})', file=sys.stderr)
        return 1
    print('results selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='results.py', description='Role result schema and validator.')
    sub = ap.add_subparsers(dest='cmd', required=True)
    v = sub.add_parser('validate', help='validate one result file')
    v.add_argument('file')
    v.add_argument('--role', choices=ROLES)
    s = sub.add_parser('schema', help='print the schema table')
    s.add_argument('--role', choices=ROLES)
    k = sub.add_parser('key', help='print the key section of a role')
    k.add_argument('role', choices=ROLES)
    sub.add_parser('selftest', help='run the selftest')
    a = ap.parse_args(argv)
    if a.cmd == 'validate':
        reason = validate(a.file, a.role)
        if reason is None:
            return 0
        print(f'results.py: {a.file}: {reason}', file=sys.stderr)
        return 1
    if a.cmd == 'schema':
        print('\n'.join(schema_lines(a.role)))
        return 0
    if a.cmd == 'key':
        print(SCHEMA[a.role]['key'])
        return 0
    return selftest()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
