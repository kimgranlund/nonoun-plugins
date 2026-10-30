#!/usr/bin/env python3
"""Score assistant replies against the author output rules (T-0466).

Usage:
  reply_lint.py score <transcript.jsonl> [--last N=20] [--before ISO-TIMESTAMP]
  reply_lint.py selftest

`score` reads a Claude Code session transcript (JSONL), keeps the assistant text of the main chain
(sidechain, tool calls, tool results and thinking are skipped), and groups it into replies: one reply
is all assistant text between two real user messages. It scores the last N replies (those stamped before
--before, when given) and prints one line per reply, the per-rule totals, and the per-anchor use counts.
Read-only, no model call, mechanical checks only: it counts, it never judges quality. Exit 0 on a
scored run, 2 on a usage error or an unreadable transcript. `selftest` runs a fixture per rule: the bad
fixture must be flagged (observed red) and its fix must not be (green); exit 0 or 1.

The rule text lives in docs/specs/doc-standards/core.md and docs/planning/author-output-block-draft.md
(section 1 for the text, section 3 for the scoring list); the 20 anchors are docs/references/visual-anchors.md.

Rules (a reply is flagged when its count is above 0):
  R-1  first line starts with a forbidden opener (Let me, I'll, Sure, Great question)
  R-2  work remains and the last line is not `Next:` or `👉` followed by Run, Open, Edit, Paste, Wait or Decide
  R-3  sentences over 20 words (code blocks and table rows skipped, a code span counts as one word)
  R-4  last line holds a forbidden closer (Hope this helps, Let me know)
  R-5  em dashes and en dashes
  R-6  an anchored line without an item and a reason (under 4 words after the glyph; 👉 needs 2)
  R-7  an emoji outside the closed set of 20 anchors
  R-8  more than 8 anchored lines
  R-9  an emoji not at the start of its line
  R-10 two or more emojis on one line
  R-11 an emoji with no text after it
  R-12 an emoji inside a code block or code span
  R-13 work remains and the last line does not start with 👉
  R-14 informational only, never a flag: bare numbers (no unit, id or source) and hedged claims with no [U]

"Work remains" is a proxy: a state or guard anchor (🟡 🔴 ⏳ 🔁 ❓ ⚠️ 🐛 🛑 🔑 👉) opens a line, or the text
holds a phrase such as remain, remaining, not yet, pending, blocked, waiting, next step or todo.

Importable: parse_replies, score_reply, score_file, selftest.
"""
import contextlib
import io
import json
import re
import sys
import tempfile
from pathlib import Path

ANCHORS = ('🟢 🟡 🔴 ⏳ 👉 ❓ 🔁 🏆 🚀 🔀 🎫 🧹 ⚠️ 🛑 🐛 🔑 📊 💰 ⏱️ 🧪').split()
VS = '️'


def norm(s):
    return s.replace(VS, '')


ANCHOR_SET = tuple(norm(a) for a in ANCHORS)
WORK_ANCHORS = tuple(norm(a) for a in '🟡 🔴 ⏳ 🔁 ❓ ⚠️ 🐛 🛑 🔑 👉'.split())
EMOJI = re.compile(
    '[\U0001F000-\U0001FAFF☀-⛿✅✨❌❎❓-❕❗➕-➗➰'
    '➿⬛⬜⭐⭕⌚⌛⏏⏩-⏳⏸-⏺]')
OPENERS = ('Let me', "I'll", 'Sure', 'Great question')
CLOSERS = ('Hope this helps', 'Let me know')
NEXT_VERBS = ('Run', 'Open', 'Edit', 'Paste', 'Wait', 'Decide')
NEXT_LINE = re.compile(r'^(?:' + norm('👉') + r'\s*|Next:?\s*)(?:' + '|'.join(NEXT_VERBS) + r')\b')
WORK_WORDS = re.compile(r'(?i)\b(remain(?:s|ing)?|not yet|pending|blocked|waiting|next step|todo|to do|still (?:runs?|running|open|needs?))\b')
FENCE = re.compile(r'^\s*(```|~~~)')
CODE_SPAN = re.compile(r'(`+)(.+?)\1')
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9`"(\[])')
BARE_NUM = re.compile(r'(?<![\w`$.#/-])(\d+(?:\.\d+)?)(?![\w.]*\d)(?!\.\d)\b(?!\s*(?:%|[a-zA-Z]))')
HEDGE = re.compile(r'(?i)\b(probably|presumably|likely|seems?|appears?|I think|I guess|should be)\b')
RULES = tuple('R-%d' % i for i in range(1, 15))


def parse_replies(path, before=None):
    """Return [(timestamp, text)]: assistant text of the main chain, grouped per turn."""
    replies, cur, ts = [], [], None
    for line in Path(path).read_text(errors='replace').splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get('isSidechain') or d.get('type') not in ('user', 'assistant'):
            continue
        content = (d.get('message') or {}).get('content')
        if d['type'] == 'user':
            real = isinstance(content, str) or (
                isinstance(content, list) and any(b.get('type') == 'text' for b in content if isinstance(b, dict)))
            if real and not d.get('isMeta'):
                if cur:
                    replies.append((ts, '\n\n'.join(cur)))
                cur, ts = [], None
            continue
        if not isinstance(content, list):
            continue
        for b in content:
            if isinstance(b, dict) and b.get('type') == 'text' and b.get('text', '').strip():
                if ts is None:
                    ts = d.get('timestamp')
                cur.append(b['text'].strip())
    if cur:
        replies.append((ts, '\n\n'.join(cur)))
    if before:
        replies = [r for r in replies if r[0] and r[0] < before]
    return replies


def split_code(text):
    """Return (prose_lines, code_lines): fenced block lines are code; inline spans stay in prose lines."""
    prose, code, fenced = [], [], False
    for ln in text.splitlines():
        if FENCE.match(ln):
            fenced = not fenced
            continue
        (code if fenced else prose).append(ln)
    return prose, code


def lead_anchor(line):
    for a in ANCHOR_SET:
        if line.startswith(a):
            return a
    return None


def strip_md(ln):
    ln = re.sub(r'^\s*(?:[-*+]\s+|\d+[.)]\s+|#+\s+|>\s+)', '', ln)
    return ln.replace('**', '').replace('__', '')


def long_sentences(prose):
    n = 0
    for ln in prose:
        if ln.lstrip().startswith('|') or not ln.strip():
            continue
        t = CODE_SPAN.sub('X', strip_md(ln))
        t = EMOJI.sub('', t)
        for s in SENT_SPLIT.split(t.strip()):
            if len(s.split()) > 20:
                n += 1
    return n


def score_reply(text):
    """Return {rule: count} for one reply."""
    text = norm(text)
    prose, code = split_code(text)
    lines = [ln for ln in prose if ln.strip()]
    first = lines[0].strip() if lines else ''
    all_lines = [ln for ln in text.splitlines() if ln.strip()]
    last = all_lines[-1].strip() if all_lines else ''
    first_bare = first.lstrip(''.join(ANCHOR_SET)).strip() if lead_anchor(first) else first
    c = dict.fromkeys(RULES, 0)
    anchored = [ln.strip() for ln in lines if lead_anchor(ln.strip())]
    work = bool(WORK_WORDS.search(text)) or any(a.startswith(WORK_ANCHORS) for a in anchored)
    c['R-1'] = int(first_bare.startswith(OPENERS))
    c['R-2'] = int(work and not NEXT_LINE.match(last))
    c['R-3'] = long_sentences(prose)
    c['R-4'] = int(any(p in last for p in CLOSERS))
    c['R-5'] = text.count('—') + text.count('–')
    for ln in anchored:
        a = lead_anchor(ln)
        words = len(CODE_SPAN.sub('X', ln[len(a):]).split())
        if words < (2 if a == norm('👉') else 4):
            c['R-6'] += 1
    c['R-8'] = int(len(anchored) > 8)
    for ln in prose:
        c['R-12'] += sum(len(EMOJI.findall(x[1])) for x in CODE_SPAN.findall(ln))
        s = CODE_SPAN.sub('', ln)
        marks = list(EMOJI.finditer(s))
        c['R-7'] += sum(1 for m in marks if m.group() not in ANCHOR_SET)
        body = s.strip()
        if not marks:
            continue
        c['R-9'] += sum(1 for m in marks if s[:m.start()].strip())
        c['R-10'] += int(len(marks) > 1)
        if not EMOJI.sub('', body).strip():
            c['R-11'] += 1
    c['R-12'] += sum(len(EMOJI.findall(ln)) for ln in code)
    c['R-13'] = int(work and not last.startswith(norm('👉')))
    plain = CODE_SPAN.sub('', '\n'.join(prose))
    plain = re.sub(r'\b[A-Za-z]+-\d+\b|\bv?\d+\.\d+\.\d+\b|\b\d{4}-\d\d-\d\d\b|^\s*\d+[.)]\s', '', plain, flags=re.M)
    c['R-14'] = len(BARE_NUM.findall(plain)) + sum(
        1 for ln in prose if HEDGE.search(ln) and '[U]' not in ln)
    anchor_use = {a: sum(1 for ln in anchored if lead_anchor(ln) == a) for a in ANCHOR_SET}
    return c, anchor_use, work


def score_file(path, last=20, before=None):
    replies = parse_replies(path, before)[-last:]
    rows, tot, flagged = [], dict.fromkeys(RULES, 0), dict.fromkeys(RULES, 0)
    use = dict.fromkeys(ANCHOR_SET, 0)
    nwork = 0
    for ts, text in replies:
        c, au, work = score_reply(text)
        rows.append((ts, c, work))
        nwork += work
        for r in RULES:
            tot[r] += c[r]
            flagged[r] += int(c[r] > 0)
        for a in ANCHOR_SET:
            use[a] += au[a]
    return rows, tot, flagged, use, nwork


def cmd_score(args):
    last, before, path = 20, None, None
    it = iter(args)
    for a in it:
        if a == '--last':
            last = int(next(it, 'x'))
        elif a == '--before':
            before = next(it, None)
        elif a.startswith('-') or path:
            print('usage: reply_lint.py score <transcript.jsonl> [--last N=20] [--before ISO]', file=sys.stderr)
            return 2
        else:
            path = a
    if not path or not Path(path).is_file():
        print('reply_lint.py: transcript not found: %s' % path, file=sys.stderr)
        return 2
    rows, tot, flagged, use, nwork = score_file(path, last, before)
    n = len(rows)
    print('replies scored: %d (last %d%s)' % (n, last, ', before %s' % before if before else ''))
    for i, (ts, c, work) in enumerate(rows, 1):
        hit = ' '.join('%s=%d' % (r, c[r]) for r in RULES if c[r])
        print('%2d %s work=%s %s' % (i, (ts or '-')[:19], 'y' if work else 'n', hit or 'clean'))
    print('totals (flagged replies / occurrences):')
    for r in RULES:
        print('  %s %d/%d  %d' % (r, flagged[r], n, tot[r]))
    print('work remains in %d of %d replies' % (nwork, n))
    if nwork:
        print('next line ok when work remains: %d of %d' % (nwork - flagged['R-2'], nwork))
    print('first line not a forbidden opener: %d of %d' % (n - flagged['R-1'], n))
    print('anchor use: ' + ' '.join('%s=%d' % (a, use[norm(a)]) for a in ANCHORS))
    unused = [a for a in ANCHORS if not use[norm(a)]]
    print('unused in sample (prune candidates): ' + (' '.join(unused) if unused else 'none'))
    return 0


# ---- selftest ----

CLEAN = '🟢 `T-0466` merged, checks passed.\n\n👉 Run `check.sh`'
# rule: (bad fixture, fixed fixture)
CASES = {
    'R-1': ("Let me check that.\nThe file holds 3 lines.", 'The file holds 3 lines.'),
    'R-2': ('Two checks remain.\nRun them later.', 'Two checks remain.\nNext: Run `check.sh`'),
    'R-3': ('This sentence has far more words than the twenty that the output rule allows for a single fact, so it is flagged.',
            'This sentence is short. It states one fact.'),
    'R-4': ('The file is fixed.\nLet me know if you want more.', 'The file is fixed.'),
    'R-5': ('The file — fixed.', 'The file is fixed.'),
    'R-6': ('🟢 done', '🟢 `T-0466` done, checks pass.'),
    'R-7': ('✅ `T-0466` done, checks pass.', '🟢 `T-0466` done, checks pass.'),
    'R-8': ('\n'.join('🟢 `T-%04d` done, checks pass.' % i for i in range(9)),
            '\n'.join('🟢 `T-%04d` done, checks pass.' % i for i in range(8))),
    'R-9': ('`T-0466` done 🟢 and checks pass.', '🟢 `T-0466` done, checks pass.'),
    'R-10': ('🟢 `T-0466` done 🟢 checks pass.', '🟢 `T-0466` done, checks pass.'),
    'R-11': ('Done.\n🟢', 'Done.\n🟢 `T-0466` done, checks pass.'),
    'R-12': ('Done.\n```\n🟢 in a block\n```', 'Done.\n```\nin a block\n```'),
    'R-13': ('Two checks remain.\nNext: Run `check.sh`', 'Two checks remain.\n👉 Run `check.sh`'),
    'R-14': ('The suite took 12 to finish and probably passes.', 'The suite took 12 seconds [U] and passes.'),
}


def selftest():
    fails = []

    def check(ok, what):
        if not ok:
            fails.append(what)

    c, _, _ = score_reply(CLEAN)
    check(not any(c.values()), 'clean fixture flagged: %s' % {r: v for r, v in c.items() if v})
    for rule, (bad, good) in CASES.items():
        cb, _, _ = score_reply(bad)
        cg, _, _ = score_reply(good)
        check(cb[rule] > 0, '%s: bad fixture not flagged (not red)' % rule)
        check(cg[rule] == 0, '%s: fixed fixture still flagged' % rule)
        print('%s red=%d green=%d' % (rule, cb[rule], cg[rule]))
    # anchor counting and prune list
    _, au, _ = score_reply('🟢 `T-0466` done, checks pass.\n🟢 `T-0467` done, checks pass.')
    check(au[norm('🟢')] == 2 and au[norm('🧪')] == 0, 'anchor counts')
    # transcript parsing: sidechain, tool calls, tool results, thinking and meta are skipped; turns group text
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 't.jsonl'
        msgs = [
            {'type': 'user', 'message': {'content': 'hi'}, 'timestamp': '2026-10-12T00:00:01Z'},
            {'type': 'assistant', 'message': {'content': [{'type': 'thinking', 'thinking': 'x'}, {'type': 'text', 'text': 'Part one.'},
                                                          {'type': 'tool_use', 'name': 'Bash'}]}, 'timestamp': '2026-10-12T00:00:02Z'},
            {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'content': 'out'}]}},
            {'type': 'assistant', 'isSidechain': True, 'message': {'content': [{'type': 'text', 'text': 'Sub text.'}]}},
            {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Part two.'}]}, 'timestamp': '2026-10-12T00:00:03Z'},
            {'type': 'user', 'message': {'content': [{'type': 'text', 'text': 'next'}]}, 'timestamp': '2026-10-12T00:01:00Z'},
            {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Second.'}]}, 'timestamp': '2026-10-12T00:01:01Z'},
        ]
        p.write_text('\n'.join(json.dumps(m) for m in msgs) + '\nnot json\n')
        got = parse_replies(p)
        check([t for _, t in got] == ['Part one.\n\nPart two.', 'Second.'], 'parse_replies grouping: %r' % got)
        check(len(parse_replies(p, before='2026-10-12T00:00:30Z')) == 1, 'parse_replies --before')
        with contextlib.redirect_stdout(io.StringIO()):
            check(cmd_score([str(p), '--last', '1']) == 0, 'score exit code')
    with contextlib.redirect_stderr(io.StringIO()):
        check(cmd_score(['/nonexistent/x.jsonl']) == 2, 'missing transcript exit code')
    if fails:
        for f in fails:
            print('FAIL: ' + f)
        return 1
    print('reply_lint selftest ok')
    return 0


def main(argv):
    if argv[:1] == ['selftest'] and len(argv) == 1:
        return selftest()
    if argv[:1] == ['score']:
        return cmd_score(argv[1:])
    print(__doc__.split('\n\n')[0] + '\nusage: reply_lint.py score <transcript.jsonl> [--last N] [--before ISO] | selftest',
          file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
