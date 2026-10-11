#!/usr/bin/env python3
"""Parse a plan doc (docs/specs/sdlc-lite/plan-doc-executor.md section 3) into front matter, H2 sections, step blocks and tables.

  plan_doc.py selftest

The one parser shared by plan_check.py (the `plan` kind) and plan_done.py, so the two cannot disagree on what a step is. A step
block is exactly what steps.py reads: it starts at a `## Step <n>: <title>` line (steps.STEP_RE) and runs to the next `## ` line, its
level line must match steps.LEVEL_RE, and its criteria are steps.criteria_lines. Deterministic: no model call, no network, no write.

    doc = parse(text)
    doc.front        front matter {key: value}, trailing ` # comment` removed; doc.front_ok False when missing or unclosed
    doc.sections     ordered [(title, body)] of the H2 sections that are not steps
    doc.section(t)   the body of the section titled t (case-insensitive), else None
    doc.steps        {n: Step}; Step has n, title, text, keys, level, criteria, spans
    table(body)      (header cells, [row cells]); cells split outside backtick spans, so a `|` inside a command stays whole
"""
import pathlib, re, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import steps  # noqa: E402  (the step grammar lives there; this module reuses it, never copies it)

KEY_RE = re.compile(r'^([a-z][a-z ]*?):\s*(.*)$')
ITEM_RE = re.compile(r'^\s*(?:[-*]|\d+[.)])\s+(\S.*)$')
LIST_RE = re.compile(r'^\[(.*)\]$')


class Step:
    def __init__(self, n, title, lines):
        self.n, self.title = n, title
        self.text = '\n'.join(lines)
        self.keys = {}
        for line in lines[1:]:
            if line.startswith('#'):
                break
            m = KEY_RE.match(line)
            if m and m.group(1) not in self.keys:
                self.keys[m.group(1)] = strip_comment(m.group(2))
        self.level_lines = [ln for ln in lines if ln.startswith('level:')]
        self.level = None
        for ln in lines:
            if steps.LEVEL_RE.match(ln):
                self.level = ln.split(':', 1)[1].strip()
                break
        self.criteria = [m.group(1).strip() for m in (ITEM_RE.match(x) for x in steps.criteria_lines(self.text)) if m]
        self.spans = [[m.group(2) for m in steps.SPAN_RE.finditer(c)] for c in self.criteria]

    def depends(self):
        """The depends list as ints, or None when the value is absent or not a list of integers."""
        return int_list(self.keys.get('depends'))

    def upserts(self):
        v = str_list(self.keys.get('upserts'))
        return v if v is not None else []

    def cap(self):
        m = re.fullmatch(r'\$\s?(\d+(?:\.\d+)?)', self.keys.get('cap', ''))
        return float(m.group(1)) if m else None


class Doc:
    def __init__(self):
        self.front, self.front_ok, self.sections, self.steps = {}, False, [], {}

    def section(self, title):
        for t, body in self.sections:
            if t.lower() == title.lower():
                return body
        return None


def strip_comment(value):
    return re.sub(r'\s+#.*$', '', value).strip()


def str_list(value):
    """`[a, b]` as ['a', 'b']; None when value is not a bracketed list. An empty list is []."""
    m = LIST_RE.match((value or '').strip())
    if not m:
        return None
    return [x.strip() for x in m.group(1).split(',') if x.strip()]


def int_list(value):
    items = str_list(value)
    if items is None or not all(re.fullmatch(r'\d+', x) for x in items):
        return None
    return [int(x) for x in items]


def parse(text):
    doc = Doc()
    lines = text.splitlines()
    body_from = 0
    if lines and lines[0].strip() == '---':
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
        if end is not None:
            doc.front_ok = True
            body_from = end + 1
            for ln in lines[1:end]:
                m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', ln)
                if m and m.group(1) not in doc.front:
                    doc.front[m.group(1)] = strip_comment(m.group(2))
    cur_title, cur, step_n = None, None, None
    blocks = []  # (kind, title or n, lines)
    for line in lines[body_from:]:
        if line.startswith('## '):
            m = steps.STEP_RE.match(line)
            if m:
                cur = [line]
                blocks.append(('step', (int(m.group(1)), m.group(2)), cur))
            else:
                cur = []
                blocks.append(('section', line[3:].strip(), cur))
            continue
        if cur is not None:
            cur.append(line)
    for kind, key, block in blocks:
        while block and not block[-1].strip():
            block.pop()
        if kind == 'step':
            n, title = key
            if n not in doc.steps:
                doc.steps[n] = Step(n, title, block)
        else:
            doc.sections.append((key, '\n'.join(block).strip('\n')))
    return doc


def split_row(line):
    """Cells of one table row, split on `|` outside backtick spans, stripped."""
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    cells, cur, code = [], '', False
    for ch in s:
        if ch == '`':
            code = not code
        if ch == '|' and not code:
            cells.append(cur.strip())
            cur = ''
        else:
            cur += ch
    cells.append(cur.strip())
    return cells


def table(body):
    """(header cells lowercased, [row cells]) of the first pipe table in body; ([], []) when there is none."""
    rows = [split_row(ln) for ln in (body or '').splitlines() if ln.strip().startswith('|')]
    rows = [r for r in rows if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
    if not rows:
        return [], []
    return [c.lower() for c in rows[0]], rows[1:]


def rows_as_dicts(body):
    head, rows = table(body)
    return head, [dict(zip(head, r + [''] * (len(head) - len(r)))) for r in rows]


def goal_line(done_body):
    """(goal line text or None, the Done when text with the Goal line and its fence left out)."""
    lines = (done_body or '').splitlines()
    for i, ln in enumerate(lines):
        m = re.match(r'^\s*Goal line\s*:\s*(.*)$', ln)
        if not m:
            continue
        text, end = m.group(1).strip().strip('`').strip(), i
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].lstrip().startswith('```'):
            k = next((x for x in range(j + 1, len(lines)) if lines[x].lstrip().startswith('```')), len(lines))
            text = (text + ' ' + ' '.join(x.strip() for x in lines[j + 1:k])).strip()
            end = min(k, len(lines) - 1)
        return text, '\n'.join(lines[:i] + lines[end + 1:])
    return None, '\n'.join(lines)


def selftest():
    bad, n = [], [0]

    def expect(label, cond):
        n[0] += 1
        print(('ok: ' if cond else 'FAIL: ') + label)
        if not cond:
            bad.append(label)
    import plan_check  # lazy: plan_check imports this module at its top
    doc = parse(plan_check.GOOD_PLAN)
    expect('plan_doc: front matter parses with its comments removed', doc.front_ok and doc.front.get('driver') == 'sonnet-high'
           and doc.front.get('goal') == 'G-002' and doc.front.get('approved_on') == '2026-10-09')
    expect('plan_doc: the H2 sections are read in order and steps are not among them',
           [t for t, _ in doc.sections] == ['Goal', 'Outcome', 'Measures', 'Authorization', 'Budget and stop rules', 'Upserts',
                                            'Later measures', 'Done when'])
    expect('plan_doc: step keys, the level line, the cap and the depends list parse',
           sorted(doc.steps) == [1, 2, 3, 4] and doc.steps[2].level == 'L2' and doc.steps[3].cap() == 20.0
           and doc.steps[4].depends() == [2, 3] and doc.steps[1].depends() == [] and doc.steps[3].upserts() == ['docs/references/sdlc-internals.md']
           and doc.steps[2].keys['executor'] == 'solo-L2')
    expect('plan_doc: criteria are the list items under ### Acceptance criteria, with their backtick spans',
           len(doc.steps[3].criteria) == 3 and doc.steps[3].criteria[0].startswith('(red)') and all(doc.steps[3].spans))
    head, rows = rows_as_dicts(doc.section('Measures'))
    expect('plan_doc: a Measures row keeps a command whole and reads the other cells', head[:2] == ['id', 'command'] and len(rows) == 2
           and rows[0]['id'] == 'K-002' and rows[0]['command'].startswith('`python3') and rows[0]['target'] == '<= 15')
    expect('plan_doc: a pipe inside a backtick span does not split the cell',
           split_row('| K-9 | `a | b` | x |') == ['K-9', '`a | b`', 'x'])
    text, rest = goal_line(doc.section('Done when'))
    expect('plan_doc: the Goal line is the fenced /goal text and is left out of the rest of Done when',
           text.startswith('/goal complete build and verify') and 'Goal line' not in rest and '/goal' not in rest and 'plan_done.py' in rest)
    expect('plan_doc: front matter missing or unclosed reads as not ok', not parse('## Goal\nx\n').front_ok and not parse('---\nid: x\n').front_ok)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / 'plan-doc.md'
        p.write_text(plan_check.GOOD_PLAN, encoding='utf-8')
        theirs = steps.parse_steps(p)
        expect('plan_doc: the steps match steps.parse_steps block for block',
               sorted(theirs) == sorted(doc.steps) and all(theirs[k] == doc.steps[k].text for k in theirs))
        r = subprocess.run([sys.executable, str(HERE / 'steps.py'), 'lint', str(p)], capture_output=True, text=True)
        expect('plan_doc: steps.py lint accepts the plan doc', r.returncode == 0 and 'steps lint: ok' in r.stdout)
        twice = plan_check.GOOD_PLAN.replace('## Step 2:', '## Step 1:')
        p.write_text(twice, encoding='utf-8')
        expect('plan_doc: steps.py rejects the same step number twice, as the parser keeps the first',
               subprocess.run([sys.executable, str(HERE / 'steps.py'), 'lint', str(p)], capture_output=True, text=True).returncode != 0
               and parse(twice).steps[1].title == doc.steps[1].title)
    print(f'plan_doc selftest: {"FAIL" if bad else "PASS"} ({n[0]} checks)')
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    print(__doc__.split('\n')[0], file=sys.stderr)
    print('usage: plan_doc.py selftest', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
