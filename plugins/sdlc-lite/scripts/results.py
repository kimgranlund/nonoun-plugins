#!/usr/bin/env python3
"""One declared result schema per role, and the validator every role result passes before the pipeline reads it.

Usage: results.py validate <result.md> [--role R]   exit 0, or print one "results.py: <file>: <reason>" line and exit 1
       results.py schema [--role R]                 print <role> TAB <key> TAB <allowed|-> TAB <sections>, one line per role
       results.py key <role>                        print the key section name of the role
       results.py solo-report <report.md> --handoff <handoff.md>
                                                    exit 0, or print the spans a `verify: needed` solo report left without an exit-code line and exit 1
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

A Codex report keeps its host envelope (T-0506): run.sh stores the report as received under that header, so a
stored Codex result may carry one `profile: <fingerprint>` line directly after the header (blank lines allowed).
It is not a section and is skipped; any other first line that starts `profile:` is a malformed envelope. The role
body that follows is validated by the same rules, so a valid envelope never excuses a missing or misordered section.

A verifier criterion has four states (T-0408, docs/specs/sdlc-lite/verifier-held-criteria.md): pass, fail,
`unmet-dependency <subject>` and `deferred <owner>`. The Verdict keeps its three values; validate (not
structure_error) refuses Verdict pass beside any criterion line that is not pass, and a held line with no #ref
or no Evidence text. criteria_states and settled_refs read those lines for steps.py.

The ui-designer key section `Mode` names the mode the run took (T-0520): plan, review, or generate, or
`blocked: <question>` when the handoff's `mode:` line is missing or unknown (the same shape as `inherited red: <tests>`).

Importable from the same scripts/ dir: SCHEMA, ROLES, validate, structure_error, key_value, attempt_reported,
criteria_states, settled_refs.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

_INHERITED = ('inherited', r'inherited red: .+', 'inherited red: <tests>')
_BLOCKED_Q = ('blocked', r'blocked: .+', 'blocked: <question>')

SCHEMA = {
    'builder': {
        'key': 'Status',
        'allowed': (('done', r'done', 'done'), ('blocked', r'blocked', 'blocked'), _INHERITED),
        'sections': ('Status', 'Changes', 'Checks', 'Notes'),
    },
    'verifier': {
        'key': 'Verdict',
        'allowed': (('pass', r'pass', 'pass'), ('fail', r'fail', 'fail'), _INHERITED),
        'sections': ('Verdict', 'Criteria', 'Out of scope changes', 'For the next attempt', 'Notes'),
    },
    'plan-reviewer': {
        'key': 'Verdict',
        'allowed': (('pass', r'pass', 'pass'), ('replan', r'replan', 'replan'), ('blocked', r'blocked', 'blocked')),
        'sections': ('Verdict', 'Findings', 'Missing decisions'),
    },
    'planner': {'key': 'Goal', 'allowed': (), 'sections': ('Goal', 'Assumptions', 'Risks')},
    'researcher': {'key': 'Answer', 'allowed': (), 'sections': ('Answer', 'Findings', 'Conflicts and gaps', 'Carry forward')},
    'scout': {'key': 'Map', 'allowed': (), 'sections': ('Map', 'Entry points', 'Not found', 'Carry forward')},
    'archaeologist': {
        'key': 'Summary', 'allowed': (),
        'sections': ('Summary', 'Decisions', 'Landmines', 'Inferred', 'Carry forward'),
    },
    'architect': {
        'key': 'Approach', 'allowed': (),
        'sections': (
            'Approach', 'Interfaces', 'Constraints and assumptions', 'Rejected alternatives', 'Risks', 'Carry forward',
        ),
    },
    'filer': {
        'key': 'Warnings', 'allowed': (),
        'sections': ('Warnings', 'PR title', 'PR body', 'Changelog entry', 'Follow-ups'),
    },
    'solo': {'key': 'Output', 'allowed': (), 'sections': ('Output',)},
    'ui-designer': {
        'key': 'Mode',
        'allowed': (('plan', r'plan', 'plan'), ('review', r'review', 'review'), ('generate', r'generate', 'generate'), _BLOCKED_Q),
        'sections': ('Mode', 'Decisions', 'Findings', 'Changes', 'Context used', 'Carry forward'),
    },
}
ROLES = tuple(SCHEMA)

HEADER = re.compile(r'^<!-- role=([a-z-]+) level=(L[1-5]) model=(\S+) effort=(\S+)((?: [a-z_]+=\S+)*) -->$')
ENVELOPE = re.compile(r'profile:\s*\S+')
ENVELOPE_REASON = 'malformed profile envelope (want one `profile: <fingerprint>` line directly after the header)'
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
    first = next((line.strip() for line in lines[1:] if line.strip()), '')
    if first.startswith('profile:') and not ENVELOPE.fullmatch(first):
        return ENVELOPE_REASON
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
    if value_checks and role == 'verifier':
        return _criteria_error(lines)
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


def attempt_reported(attempt_path, role):
    """True when the result file beside an attempt record (<stem>.md for <stem>.attempt.json) holds a key-section
    value from SCHEMA (a verdict): the role finished and reported, whatever the record's status says (T-0445)."""
    name = os.path.basename(attempt_path)
    if not name.endswith('.attempt.json'):
        return False
    return key_value(os.path.join(os.path.dirname(attempt_path), name[:-len('.attempt.json')] + '.md'), role) is not None


CRITERION_RE = re.compile(
    r'^\s*(?:[-*]\s*)?(?:\d+\.\s*)?(?:#(?:(step-\d+|ticket)#)?(\d+)\s+)?(.+?):\s+'
    r'(pass|fail|unmet-dependency\s+\S+|deferred\s+\S+)\.\s*Evidence:(.*)$', re.I)
SETTLE_RE = re.compile(r'^\s*[-*]\s*`?#?(step-\d+|ticket)#(\d+)`?\s*$')


def notes_lines(path):
    """The non-blank lines of a verifier result's ## Notes section (nits no criterion names), else []."""
    try:
        lines = open(path).read().splitlines()
    except OSError:
        return []
    return [l.strip() for l in _section_lines(lines, 'Notes') if l.strip() and l.strip().lower() != 'none']


def _section_lines(lines, name):
    i = _first_heading(lines, name)
    if i is None:
        return []
    out = []
    for rest in lines[i + 1:]:
        if rest.startswith('## '):
            break
        out.append(rest)
    return out


def criteria_states(path):
    """[{scope, k, state, who, evidence}] for each line under ## Criteria that ends `: <state>. Evidence: ...`;
    state is pass, fail, unmet-dependency or deferred, who the subject or owner token ('' for pass and fail),
    scope the `step-<n>` or `ticket` of a qualified `#step-1#4` ref (None when the line has `#<k>` or no ref),
    k its ordinal (None when the line has no ref). A line that does not match is ignored. Never raises."""
    try:
        lines = _lines(path)
    except OSError:
        return []
    out = []
    for line in _section_lines(lines, 'Criteria'):
        m = CRITERION_RE.match(line)
        if not m:
            continue
        word = m.group(4).split()
        out.append({'scope': m.group(1), 'k': int(m.group(2)) if m.group(2) else None, 'state': word[0].lower(),
                    'who': word[1] if len(word) > 1 else '', 'evidence': m.group(5).strip()})
    return out


def settled_refs(path):
    """[(scope, k)] for each `- step-<n>#<k>` or `- ticket#<k>` item under ## Settles. Never raises."""
    try:
        lines = _lines(path)
    except OSError:
        return []
    return [(m.group(1), int(m.group(2))) for m in map(SETTLE_RE.match, _section_lines(lines, 'Settles')) if m]


def _ref_text(c):
    if c['k'] is None:
        return '#<ref>'
    return '#' + (f"{c['scope']}#" if c['scope'] else '') + str(c['k'])


def _criteria_error(lines):
    """The reason a verifier result breaks the held-criteria rules, else None: a held line needs its #<ref> and
    Evidence text, and Verdict pass cannot sit beside a criterion line that is not pass."""
    states = []
    for line in _section_lines(lines, 'Criteria'):
        m = CRITERION_RE.match(line)
        if m:
            word = m.group(4).split()
            states.append({'scope': m.group(1), 'k': int(m.group(2)) if m.group(2) else None,
                           'state': word[0].lower(), 'who': word[1] if len(word) > 1 else '',
                           'evidence': m.group(5).strip()})
    for c in states:
        if c['state'] in ('unmet-dependency', 'deferred'):
            if c['k'] is None:
                return 'held criterion needs its #<ref>'
            if not c['evidence']:
                return f'held criterion {_ref_text(c)} needs Evidence text'
    present, value = _key_body_value(lines, SCHEMA['verifier']['key'])
    if present and value.lower() == 'pass':
        for c in states:
            if c['state'] != 'pass':
                return f"## Verdict pass but {_ref_text(c)} is {c['state']}" + (f" {c['who']}" if c['who'] else '')
    return None


def criterion_spans(handoff_text):
    """The command-like code spans of a ticket handoff's acceptance criteria: the bullets under `## Acceptance
    criteria` and the `Done when:` lines, outside ``` fences, a repeat once (steps.line_spans picks the spans)."""
    import steps
    out, inside, fenced = [], False, False
    for line in handoff_text.splitlines():
        if line.startswith('## '):
            inside, fenced = line.rstrip() == '## Acceptance criteria', False
        elif line.lstrip().startswith('```'):
            fenced = not fenced
        elif not fenced and ((inside and re.match(r'\s*[-*] ', line)) or re.match(r'\s*[-*] Done when:', line)):
            out += [t for t in steps.line_spans(line) if t not in out]
    return out


def solo_report_error(report_text, spans):
    """None, or the spans a solo report that says `verify: needed` lists without an exit-code line (T-0471, the
    Run-verbatim rule in agents/solo.md): a report line holds the span exactly as written in backticks and `exit <n>`."""
    if not re.search(r'(?m)^\s*(?:[-*] )?verify: needed\b', report_text):
        return None
    lines = report_text.splitlines()
    missing = [s for s in spans if not any(f'`{s}`' in ln and re.search(r'\bexit \d+\b', ln) for ln in lines)]
    if not missing:
        return None
    return 'verify: needed without an exit-code line for: ' + '; '.join(f'`{s}`' for s in missing)


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
        'researcher': '## Answer\na\n\n## Findings\nf\n\n## Conflicts and gaps\nNone\n\n## Carry forward\n- x\n',
        'scout': '## Map\nm\n\n## Entry points\ne\n\n## Not found\nNone\n\n## Carry forward\n- x\n',
        'archaeologist': '## Summary\ns\n\n## Decisions\nd\n\n## Landmines\nl\n\n## Inferred\ni\n\n## Carry forward\n- x\n',
        'architect': '## Approach\na\n\n## Interfaces\ni\n\n## Constraints and assumptions\nc\n\n'
                     '## Rejected alternatives\nr\n\n## Risks\nr\n\n## Carry forward\n- x\n',
        'solo': '## Output\nfiles: x\nverify: skipped\n',
        'ui-designer': '## Mode\nplan\n\n## Decisions\nd\n\n## Findings\nNone\n\n## Changes\nNone\n\n'
                       '## Context used\n- tokens.css\n\n## Carry forward\n- x\n',
        'filer': '## Warnings\nNone\n\n## PR title\nt\n\n## PR body\nb\n\n## Changelog entry\nc\n\n## Follow-ups\nNone\n',
    }
    case('the schema covers the eleven roles', set(bodies), set(ROLES))
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
    env = 'profile: 0.25.0+abcdef012345\n'
    case('a valid profile envelope before a valid scout body passes', validate(write('env-ok.md', head('scout') + env + '\n## Map\n- a:1: x\n')), None)
    case('a valid envelope does not excuse a missing key section',
         validate(write('env-nokey.md', head('scout') + env + '## Entry points\nx\n')), 'lacks ## Map')
    case('a valid envelope does not excuse a misordered body',
         validate(write('env-order.md', head('scout') + env + '## Not found\nNone\n## Map\n- a:1: x\n')), '## Not found comes before ## Map')
    case('a malformed envelope is rejected', validate(write('env-bad.md', head('scout') + 'profile:\n## Map\n- a:1: x\n')), ENVELOPE_REASON)
    case('a value is read case-insensitively', validate(write('upper.md', head('builder') + '## Status\nDone\n')), None)
    case('a missing builder Status fails',
         validate(write('nostatus.md', head('builder') + '## Changes\na\n')),
         'lacks ## Status (done|blocked|inherited red: <tests>)')
    case('a missing ui-designer Mode fails',
         validate(write('nomode.md', head('ui-designer') + '## Decisions\nd\n')),
         'lacks ## Mode (plan|review|generate|blocked: <question>)')
    case('ui-designer accepts blocked: <question>',
         validate(write('ui-blocked.md', head('ui-designer') + '## Mode\nblocked: which surface is this for?\n')), None)
    case('a missing scout Map fails', validate(write('nomap.md', head('scout') + '## Entry points\ne\n')), 'lacks ## Map')
    case('an empty planner Goal body passes', validate(write('emptygoal.md', head('planner') + '## Goal\n\n## Risks\nr\n')), None)
    for role in ('builder', 'verifier', 'plan-reviewer', 'ui-designer'):
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
    case('schema prints - for a role with no allowed set', schema_lines('scout'),
         ['scout\tMap\t-\tMap|Entry points|Not found|Carry forward'])
    case('a scout result without ## Carry forward passes',
         validate(write('cf-none.md', head('scout') + '## Map\nm\n\n## Entry points\ne\n\n## Not found\nNone\n')), None)
    case('a scout result with ## Carry forward before ## Map fails',
         validate(write('cf-order.md', head('scout') + '## Carry forward\n- x\n\n## Map\nm\n')),
         '## Carry forward comes before ## Map')

    # T-0408: a verifier may hold a declared criterion (unmet-dependency or deferred); the Verdict stays fail
    vhead = head('verifier')
    held = '## Criteria\n- #4 `test -s out`: deferred integration. Evidence: out/ is absent\n\n'
    case('a verifier result with a ## Notes section validates',
         validate(write('notes-ok.md', vhead + '## Verdict\npass\n\n## Criteria\n- #1 `t`: pass. Evidence: e\n\n## For the next attempt\nNone\n\n## Notes\n- a.py:3 em dash in a comment\n')), None)
    case('Notes before For the next attempt fails',
         validate(write('notes-order.md', vhead + '## Verdict\npass\n\n## Notes\n- x\n\n## For the next attempt\nNone\n')),
         '## Notes comes before ## For the next attempt')
    case('a verdict pass with notes is still refused',
         validate(write('pass-notes.md', vhead + '## Verdict\npass with notes\n\n## Notes\n- x\n')) is not None, True)
    case('a held criterion under Verdict fail validates',
         validate(write('held-ok.md', vhead + '## Verdict\nfail\n\n' + held + '## For the next attempt\ndeferred: integration\n')), None)
    case('an unmet-dependency criterion under Verdict fail validates',
         validate(write('unmet-ok.md', vhead + '## Verdict\nfail\n\n## Criteria\n- #1 `t`: unmet-dependency T-0307. '
                        'Evidence: T-0307 is ready\n')), None)
    case('Verdict pass with a deferred criterion is refused',
         validate(write('held-pass.md', vhead + '## Verdict\npass\n\n' + held)),
         '## Verdict pass but #4 is deferred integration')
    case('Verdict pass with an unmet-dependency criterion is refused',
         validate(write('unmet-pass.md', vhead + '## Verdict\npass\n\n## Criteria\n- #1 `t`: unmet-dependency T-0307. '
                        'Evidence: e\n')), '## Verdict pass but #1 is unmet-dependency T-0307')
    case('Verdict pass with a fail criterion line is refused',
         validate(write('fail-pass.md', vhead + '## Verdict\npass\n\n## Criteria\n- #2 `t`: fail. Evidence: e\n')),
         '## Verdict pass but #2 is fail')
    case('a held criterion with no #ref is refused',
         validate(write('held-noref.md', vhead + '## Verdict\nfail\n\n## Criteria\n- `t`: deferred integration. '
                        'Evidence: e\n')), 'held criterion needs its #<ref>')
    case('a held criterion with no evidence text is refused',
         validate(write('held-noev.md', vhead + '## Verdict\nfail\n\n## Criteria\n- #3 `t`: deferred integration. '
                        'Evidence:\n')), 'held criterion #3 needs Evidence text')
    case('deferred with no owner token is an ordinary line, not held',
         validate(write('def-noowner.md', vhead + '## Verdict\nfail\n\n## Criteria\n- #3 `t`: deferred. Evidence: e\n')), None)
    case('an old result with only pass lines validates',
         validate(write('old-pass.md', vhead + '## Verdict\npass\n\n## Criteria\n- `a`: pass. Evidence: e\n- `b`: pass. '
                        'Evidence: e\n\n## Out of scope changes\nNone\n')), None)
    case('an old result with a fail line under Verdict fail validates',
         validate(write('old-fail.md', vhead + '## Verdict\nfail\n\n## Criteria\n- `a`: pass. Evidence: e\n- `b`: fail. '
                        'Evidence: e\n')), None)
    case('criteria_states reads a qualified ref and a held state',
         [(c['scope'], c['k'], c['state'], c['who']) for c in criteria_states(write(
             'cs.md', vhead + '## Verdict\nfail\n\n## Criteria\n- #step-1#4 `t`: deferred integration. Evidence: e\n'
                      '- #2 `u`: pass. Evidence: e\n'))],
         [('step-1', 4, 'deferred', 'integration'), (None, 2, 'pass', '')])
    case('settled_refs reads the ## Settles list',
         settled_refs(write('st.md', vhead + '## Verdict\npass\n\n## Settles\n- step-1#4\n- ticket#2\n- not a ref\n')),
         [('step-1', 4), ('ticket', 2)])
    case('structure_error ignores the criteria rule',
         structure_error(write('se-held.md', vhead + '## Verdict\npass\n\n' + held)), None)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'results.py'), encoding='utf-8') as f:
        src = f.read()
    stub = os.path.join(tmp, 'nocrit.py')
    with open(stub, 'w', encoding='utf-8') as f:
        cut = src.rindex('\nif __name__')
        f.write(src[:cut] + '\n_criteria_error = lambda lines: None\n' + src[cut:])
    p = subprocess.run([sys.executable, stub, 'validate', os.path.join(tmp, 'held-pass.md')], capture_output=True, text=True)
    case('negative control: a results.py with the criteria rule removed validates Verdict pass with a deferred line',
         p.returncode, 0)

    # solo report detect rule (T-0471): verify: needed needs one exit-code line per criterion span.
    ho = ('## Acceptance criteria\n- [ ] `python3 a.py check` exits 0\n- [ ] `python3 b.py selftest` exits 0\n'
          '\n## Notes\n- `python3 c.py not-a-criterion` is prose\n```\n- [ ] `python3 fenced.py x`\n```\n')
    sp = criterion_spans(ho)
    case('criterion_spans reads the criteria bullets and skips prose and fences',
         sp, ['python3 a.py check', 'python3 b.py selftest'])
    full = 'files: x\n- `python3 a.py check` exit 0\n- `python3 b.py selftest` exit 0\nverify: needed\n'
    case('a verify: needed report with an exit-code line per span passes', solo_report_error(full, sp), None)
    case('a report with no verify: needed line passes without exit-code lines',
         solo_report_error('files: x\nverify: skipped (docs/records only; docs_check green)\n', sp), None)
    short = 'files: x\n- `python3 a.py check` exit 0\nverify: needed\n'
    case('observed red: a verify: needed report missing one span line is flagged',
         solo_report_error(short, sp) is not None and 'b.py selftest' in solo_report_error(short, sp), True)
    para = 'files: x\n- `python3 a.py check` exit 0\n- `python3 b.py` exit 0\nverify: needed\n'
    case('observed red: a paraphrased span (not verbatim) is flagged', solo_report_error(para, sp) is not None, True)
    noexit = 'files: x\n- `python3 a.py check` ok\n- `python3 b.py selftest` ok\nverify: needed\n'
    case('observed red: span lines with no exit code are flagged', solo_report_error(noexit, sp) is not None, True)
    rp, hp = write('solo-report.md', short), write('solo-handoff.md', ho)
    p = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.py'),
                        'solo-report', rp, '--handoff', hp], capture_output=True, text=True)
    case('solo-report exits 1 on the short report and names the span', (p.returncode, 'b.py selftest' in p.stderr), (1, True))
    rp = write('solo-report-ok.md', full)
    p = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.py'),
                        'solo-report', rp, '--handoff', hp], capture_output=True, text=True)
    case('solo-report exits 0 on the full report', p.returncode, 0)

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
    r = sub.add_parser('solo-report', help='check a solo report that says verify: needed against its handoff')
    r.add_argument('report')
    r.add_argument('--handoff', required=True)
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
    if a.cmd == 'solo-report':
        with open(a.report, encoding='utf-8') as f, open(a.handoff, encoding='utf-8') as h:
            reason = solo_report_error(f.read(), criterion_spans(h.read()))
        if reason is None:
            return 0
        print(f'results.py: {a.report}: {reason}', file=sys.stderr)
        return 1
    return selftest()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
