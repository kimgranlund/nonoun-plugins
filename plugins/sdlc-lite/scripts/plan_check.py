#!/usr/bin/env python3
"""Lint a planned /goal, /loop, fanout, campaign, plan-doc, clarify, or compaction block before it is handed to the user.

  plan_check.py goal|loop|fanout|campaign [--text T | --file F] [--root .sdlc]
  plan_check.py plan [--text T | --file F] [--root .sdlc] [--run]
  plan_check.py clarify [--text T | --file F]
  plan_check.py <kind> ... --summary
  plan_check.py compaction [--text T | --file F] [--reply]
  plan_check.py selftest

Reads the block from --text, --file, or stdin; a fenced block is unwrapped. Prints one `FAIL <rule>: <why>` line per
finding (exit 1), `warn <rule>: <why>` lines that never change the exit code, and `ok: <kind> plan passes` otherwise.
A goal also carries the plan-verification outcome block (Outcome, Measured by, Rubric, Negative control): `outcome-block` and
`done-measured` are shape checks only, since the script cannot know a `before` value is true. Deterministic: no model call, no network. Fanout flags are read from fanout.py's own parser text, so a flag fanout.py
does not have is a finding. /goal and /loop cannot run headlessly: their rules come from the skills'
references (the stop hook checks the goal each turn; /loop parses a leading interval token or a trailing `every N unit`).
A plan doc (kind `plan`, docs/specs/sdlc-lite/plan-doc-executor.md section 3) is read through plan_doc.py, the parser plan_done.py shares, and
checked by 19 rules (plan-front, no-approval, outcome-block, done-measured, measure-row, measure-safe, later-named, step-shape, depends-order,
cap-sum, executor-unknown, verifier-seat, review-missing, upsert-shape, upsert-sweep, authorization, stop-rules, goal-line, done-plan-done) and
three warnings (l1-unverified, kpi-drift, kpi-unresolved). `--run` adds no-approval, the check that applies only before execution starts. The
text is never unwrapped, since a plan doc holds a fenced Goal line. The selftest prints one `ok: plan: <rule> ...` line per case.
A clarify block (kind `clarify`, the output of the clarify skill) is a task handoff with `## Goal` and `## Intent`; it is never unwrapped,
since it holds backticks. One non-empty line starting `already scoped: `, `follow-up: ` or `stopped: ` is a pass-through and passes. Eleven
rules: clarify-goal, clarify-non-goals (inline text or `- ` lines), clarify-level (`Level: L1` to `L4`), clarify-done (every `Done when:`
item holds a backticked command, an EARS line `When <trigger>, the <system> MUST <response>`, or `unverifiable: <why>`), clarify-done-defect
(an item reads its own verifier result, names a fixed sha, or needs a live run), clarify-pass-through (a pass-through line followed by more
text), clarify-hedge (a CLARIFY_HEDGE word in the Goal or a Do step), clarify-delta (a `Deltas:` item is not one of the three forms
`-> defaulted:`, `-> answered:`, `-> gap (gap: ...; default: ...)` with a CLARIFY_TYPES type), clarify-do-verb (no numbered Do step, or one
whose first word is not in CLARIFY_VERBS), clarify-rfc2119 (an upper-case RFC 2119 keyword in Goal or Intent outside `Literal ask:` and EARS
items, or a lower-case must, shall or should in `## Constraints`), and clarify-default-source (a defaulted delta without `[U]` and
`(source: ...)`). Two warnings: clarify-goal-length (over 2 sentences or 50 words) and clarify-glossary (an unapproved alias from
docs/references/glossary.md in the Goal or a Do step; skipped when the file is absent). An item starting `[owner: maintainer]` is exempt
from the two Done when rules. The selftest prints one `ok: clarify: <rule> ...` line per case.
Controlled language (T-0469): the goal, campaign and plan kinds add three warnings that reuse the clarify lists: `hedge` (a CLARIFY_HEDGE word in
the /goal line, a Goal or an Outcome line), `verb` (a How to work or step Do statement that does not start with a CLARIFY_VERBS verb) and
`rfc2119` (an Authorization with no upper-case MUST, or a lower-case must, shall or should in it). `--summary` on any kind prints one more line
after the lint lines, `cost: $<sum> of $<cap> (<n> tickets: T-0001 L2 $30, ...)`: the tickets the block names, each at its size level's row in
budget.py TIERS, against its `$<n> total` figure. A ticket with no size or tier makes the sum `unknown`, never 0; a sum above the cap ends `over`.
A compaction block (kind `compaction`, the `/compact` prompt of the plan skill's compaction kind) is unwrapped, then read as one identity
line, the seven headers GOAL, RULES, DECISIONS, STATE, OPEN, NEXT, DROP, and a last line `NEXT <one action>`. `lines: <N> of 60` and
`pin: <M> of 40` print first. Nine rules: compaction-words (a line over 20 words; a lone pipe is no word), compaction-verb (a DROP section
line that starts with neither DROP nor NEXT, or a first token of 3 or more upper-case letters outside KEEP, POINT, DROP, NEXT),
compaction-order (a header missing, repeated or out of order, not exactly one line before GOAL, or a last line that does not start `NEXT `),
compaction-lines (over 60 lines), compaction-pin (over 40 PIN lines: lines under GOAL to NEXT that are no header, not `none`, and start with
neither POINT nor DROP), compaction-em-dash, compaction-entry-copy (a line of 4 or more words that, less its leading verb, equals a line of
`CLAUDE.md` or `AGENTS.md` in the working directory with its list marker removed; a missing file is skipped), compaction-decision (a
DECISIONS line that is not `<user|agent> <YYYY-MM-DD> <decision> | <reason of 1 to 5 words> | <pointer>`), and compaction-approval (an
approval word with neither a double-quoted span nor `[U]`). One warning: compaction-glossary (an unapproved alias from
docs/references/glossary.md outside code spans; skipped when the file is absent). The selftest prints one `ok: compaction: <rule> ...` line
per case.
`compaction --reply` reads the whole reply instead of the block and checks the return shape of references/compaction.md section 6 (rule
compaction-return): at most one `stale: ` line, the fenced block, then exactly `lines: N of 60`, `pin: M of 40` (both equal to the block's own counts)
and `Run: /compact <paste>`, with no other line before the fence or after `Run:`.
"""
import argparse, glob, json, os, pathlib, re, shlex, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import plan_doc  # noqa: E402  (the shared plan-doc parser)
HOT = {'check.py', 'check.sh', 'AGENTS.md', 'README.md'}  # shared files that conflict at merge: warn, not fail
VAGUE = re.compile(r"(?i)looks? good|feels?|seems?|good enough|as needed|when (it's|it is) done|everything works|all done")
CHECKABLE = re.compile(r"(?i)exit(s)? 0|rc=0|rc 0|\btag\b|origin/main|published|pushed|merged|closed|status: done|\.md\b|"
                       r"tickets\.py check|\bpasses\b|\breturns\b|\bexists\b|\bequals\b")


def unwrap(text):
    m = re.search(r'```[a-zA-Z]*\n(.*?)```', text, re.S)
    return (m.group(1) if m else text).strip()


# ---- goal ----------------------------------------------------------------------------------------------------
LABELS = (('scope', r'Scope'), ('how', r'How to work'), ('stop', r'(Budget|Stop rules?)'),
          ('auth', r'Authori[sz](ation|ed)'), ('done', r'Done when'))


def sections(text):
    marks = []
    for key, pat in LABELS + (('_outcome', r'Outcome'),):  # the outcome block ends the Scope section
        m = re.search(rf'(?im)^\s*({pat})\b[^\n]*', text)
        if m:
            marks.append((m.start(), key))
    marks.sort()
    out = {}
    for i, (pos, key) in enumerate(marks):
        out[key] = text[pos:(marks[i + 1][0] if i + 1 < len(marks) else len(text))]
    return out


def check_goal(text, root='.sdlc'):
    text = unwrap(text)
    fails, warns = [], []
    if not re.match(r'/goal\s+\S', text):
        fails.append(('starts-with-goal', 'the block must start with `/goal <text>`'))
    sec = sections(text)
    for key, pat in LABELS:
        if key not in sec:
            fails.append((f'section-{key}', f'missing the `{pat.split("(")[0].strip()}` section'))
    if 'scope' in sec and not re.search(r'(?m)^\s*\d+\.\s+\S', sec['scope']):
        fails.append(('scope-list', 'Scope must be a numbered list of tickets or deliverables'))
    if 'how' in sec and not (re.search(r'steps\.py lane', sec['how']) and re.search(r'(?i)replan', sec['how'])):
        fails.append(('how-to-work', 'How to work must name `steps.py lane` and a replan cap'))
    if 'stop' in sec:
        s = sec['stop']
        if not re.search(r'\$\s?\d+', s):
            fails.append(('stop-money', 'stop rules need a dollar cap (a number)'))
        if '529' not in s:
            fails.append(('stop-529', 'stop rules need the three-529s rule'))
        if not re.search(r'(?i)rate|weekly|limit', s):
            fails.append(('stop-limit', 'stop rules need the rate or weekly limit rule'))
        if not re.search(r'\.sdlc/notes(/notes)?\.md', s):
            fails.append(('stop-state', 'stop rules need where state is written (.sdlc/notes.md, or .sdlc/notes/notes.md with layout: topics)'))
    if not re.search(r'(?is)verifier.{0,80}fail|fail.{0,80}verifier', text):
        fails.append(('verifier-fail', 'say that a verifier fail means fix and re-verify, never merge on a fail'))
    if 'auth' in sec:
        a = sec['auth']
        body = re.sub(r'(?im)^\s*Authori[sz](ation|ed)[^:\n]*:?', '', a, count=1).strip()
        if not body or not re.search(r'(?i)\b(none|not implied|never implied|only|authori[sz]ed)\b', a) \
                or not re.search(r'(?i)publish|push|tag|release|external|write', a):
            fails.append(('authorization', 'state exactly what is authorized (publish, push, tag, external writes) or `None`'))
    if 'done' in sec:
        d = sec['done']
        if VAGUE.search(d):
            fails.append(('done-vague', f'Done when must be checkable, not "{VAGUE.search(d).group(0)}"'))
        if not CHECKABLE.search(d):
            fails.append(('done-uncheckable', 'Done when needs a command exit code, a file, a tag, or a merged ticket'))
        if not re.search(r'(?i)stopped|limit|notes\.md', d):
            fails.append(('done-limit', 'Done when must also cover stopping on a budget or limit with state written'))
    f2, w2, measure = check_outcome(text)
    fails.extend(f2)
    warns.extend(w2)
    if measure and 'done' in sec:
        ids, cmds, target = measure
        d = re.sub(r'\s+', ' ', sec['done'])
        if not (any(i in d for i in ids) or any(c in d for c in cmds) or (target and target in d)):
            fails.append(('done-measured', 'Done when must name the Measured by id or command, or its target, so closing tickets alone cannot end the goal'))
    warns.extend(kpi_unresolved(text, root))
    warns.extend(language_goal(text))
    if len(text) > 5000:
        fails.append(('too-long', f'{len(text)} characters; keep it under 5000 so it can be read overnight'))
    return fails, warns


def check_outcome(text):
    """The plan-verification outcome block: (fails, warns, measure) with measure = (K ids, commands, target) or None."""
    fails, warns, measure = [], [], None

    def bad(why):
        fails.append(('outcome-block', why))
    m = re.search(r'(?im)^\s*Outcome\s*:[^\n]*\S[^\n]*', text)
    if not m:
        bad('missing the `Outcome:` line (the state of the world that means the work succeeded)')
    elif not re.search(r'Why:\s*\S', m.group(0)):
        bad('the Outcome line needs `Why:` and one sentence on what it protects or buys')
    m = re.search(r'(?im)^\s*Measured by\s*:([^\n]*)', text)
    if not m:
        bad('missing the `Measured by:` line (a KPI id or a backticked command, `before:` and `target:`)')
    elif re.match(r'\s*none\s*:\s*\S', m.group(1), re.I):
        warns.append(('no-measure', 'Measured by is `none`: the goal cannot show the outcome moved'))
    else:
        body = m.group(1)
        ids, cmds = re.findall(r'\b[A-Z]-\d+\b', body), [re.sub(r'\s+', ' ', c) for c in re.findall(r'`([^`]+)`', body)]
        before, target = re.search(r'before\s*:\s*(\S[^,]*)', body), re.search(r'target\s*:\s*(\S[^\n]*?)\s*\.?\s*$', body)
        if not (ids or cmds):
            bad('Measured by must name a measure id (K-001, M-001) or a backticked command')
        if not before:
            bad('Measured by needs `before: <value>` read by running the measure now')
        elif re.match(r'unmeasured\b', before.group(1), re.I):
            warns.append(('before-unmeasured', 'the before value is unmeasured: the goal starts without a reproducible baseline'))
        if not target:
            bad('Measured by needs `target: <bound>`')
        if (ids or cmds) and before and target:
            measure = (ids, cmds, re.sub(r'\s+', ' ', target.group(1)))
    m = re.search(r'(?im)^\s*Rubric\s*:[^\n]*\n', text)
    if not m:
        bad('missing the `Rubric:` list (3 to 5 numbered criteria)')
    else:
        items = []
        for ln in text[m.end():].splitlines():
            if re.match(r'\s*\d+\.\s+\S', ln):
                items.append(ln)
            else:
                break
        if not 3 <= len(items) <= 5:
            bad(f'Rubric needs 3 to 5 numbered criteria, found {len(items)}')
        if any('pass:' not in i for i in items):
            bad('every Rubric criterion needs `pass: <threshold>`')
    if not re.search(r'(?im)^\s*Negative control\s*:\s*\S', text):
        bad('missing the `Negative control:` line (a state in which the measure reads red)')
    return fails, warns, measure


def kpi_unresolved(text, root):
    """Advice only: a cited K-NNN with no docs/kpi/NNN-*.md, when the repository (the parent of --root) keeps a docs/kpi folder."""
    kpi = pathlib.Path(root).resolve().parent / 'docs' / 'kpi'
    if not kpi.is_dir():
        return []
    return [('kpi-unresolved', f'K-{n} has no file docs/kpi/{n}-*.md')
            for n in dict.fromkeys(re.findall(r'\bK-(\d+)\b', text)) if not list(kpi.glob(f'{n}-*.md'))]


# ---- loop ----------------------------------------------------------------------------------------------------
UNIT = {'s': 1, 'sec': 1, 'secs': 1, 'second': 1, 'seconds': 1, 'm': 60, 'min': 60, 'mins': 60, 'minute': 60,
        'minutes': 60, 'h': 3600, 'hr': 3600, 'hrs': 3600, 'hour': 3600, 'hours': 3600, 'd': 86400, 'day': 86400,
        'days': 86400}


def parse_loop(text):
    """(interval_seconds or None, prompt, attempt) where attempt is an interval-looking token that did not parse."""
    body = re.sub(r'^/loop\s*', '', text.strip())
    first = body.split(None, 1)[0] if body.split() else ''
    m = re.fullmatch(r'(\d+)([smhd])', first)
    if m:
        return int(m.group(1)) * UNIT[m.group(2)], body[len(first):].strip(), None
    t = re.search(r'(?i)\bevery\s+(\d+)\s*([a-z]+)\s*$', body)
    if t and t.group(2).lower() in UNIT:
        return int(t.group(1)) * UNIT[t.group(2).lower()], body[:t.start()].strip(), None
    attempt = first if re.fullmatch(r'(?i)\d+\s*[a-z]+:?', first) or re.fullmatch(r'(?i)\d+', first) else None
    return None, body, attempt


def check_loop(text):
    text = unwrap(text)
    fails, warns = [], []
    if not re.match(r'/loop\b', text):
        fails.append(('starts-with-loop', 'the block must start with `/loop`'))
    secs, prompt, attempt = parse_loop(text)
    if attempt:
        fails.append(('interval-token', f'`{attempt}` is not a valid interval token and /loop would fall into dynamic '
                      'mode: use a leading token like 20m, 1h, 30s, 2d, or a trailing `every 20m`'))
    if not prompt.strip():
        fails.append(('prompt-empty', 'the loop prompt is empty'))
    if secs is not None:
        if not re.search(r'(?i)\b(stop|no-op|ends? the loop|until|cancel)\b', prompt):
            fails.append(('stop-condition', 'a recurring loop prompt needs a stop or no-op condition'))
        if secs < 60:
            warns.append(('seconds', 'cron has one-minute granularity: seconds round up to 1m'))
        elif secs < 3600 and secs % 60 == 0 and 60 % (secs // 60) != 0:
            warns.append(('uneven', f'{secs // 60}m does not divide an hour: it rounds to a clean interval and gaps are uneven'))
        elif secs >= 3600 and secs < 86400 and (secs % 3600 or 24 % (secs // 3600)):
            warns.append(('uneven', 'an hours interval should divide 24: it rounds to a clean one'))
        elif secs >= 86400 * 7:
            warns.append(('expiry', 'recurring tasks auto-expire after 7 days'))
        if not re.search(r'(?i)since the last|since last|changed since', prompt):
            warns.append(('progress', 'say "since the last run" so each fire reports progress, not a restatement'))
    if re.search(r'(?<!\d)\d{1,2}:(00|30)\b', prompt) and secs is None:
        warns.append(('minute-mark', 'avoid exactly :00 and :30 when the time is approximate'))
    return fails, warns


# ---- fanout --------------------------------------------------------------------------------------------------
def fanout_parser():
    src = (HERE / 'fanout.py').read_text(encoding='utf-8')
    start = src.index("ap.add_argument('lanes'")
    end = src.index("ap.add_argument('--dry-run'")
    block = src[start:end] + src[end:end + 200].split('\n')[0]
    m = re.search(r'MAX_LANES_DEFAULT, MAX_LANES_HARD, STAGGER_DEFAULT = (\d+), (\d+), (\d+)', src)
    dflt, hard, stag = (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (4, 16, 20)

    class P(argparse.ArgumentParser):
        def error(self, message):
            raise ValueError(message)
    p = P(prog='fanout.py run', add_help=False)
    p.add_argument('lanes', nargs='+')
    for call in block.split('ap.add_argument(')[2:]:
        m = re.match(r"\s*'(--[a-z-]+)'", call)
        if not m:
            continue
        flag = m.group(1)
        if 'action=\'store_true\'' in call or 'action="store_true"' in call:
            p.add_argument(flag, action='store_true')
        elif "action='append'" in call:
            p.add_argument(flag, action='append')
        else:
            p.add_argument(flag, type=(float if flag == '--stagger' else int if flag == '--max-lanes' else str),
                           default=(stag if flag == '--stagger' else dflt if flag == '--max-lanes' else None))
    p.hard_cap = hard
    return p


def commands(text):
    """The commands in a block, with trailing-backslash continuations joined; env prefixes kept as env."""
    lines, cur = [], ''
    for raw in text.splitlines():
        s = raw.rstrip()
        if not s.strip() or s.lstrip().startswith('#'):
            continue
        if s.endswith('\\'):
            cur += s[:-1] + ' '
            continue
        lines.append(cur + s)
        cur = ''
    out = []
    for ln in lines:
        try:
            toks = shlex.split(ln)
        except ValueError as e:
            out.append((None, None, f'unparseable command: {e}'))
            continue
        env = {}
        while toks and re.fullmatch(r'[A-Z_][A-Z0-9_]*=.*', toks[0]):
            k, v = toks.pop(0).split('=', 1)
            env[k] = v
        idx = next((i for i, t in enumerate(toks) if t.endswith('fanout.py')), None)
        if idx is None or toks[idx + 1:idx + 2] != ['run']:
            out.append((env, None, f'not a `fanout.py run` command: {ln[:60]}'))
            continue
        out.append((env, toks[idx + 2:], None))
    return out


def load_tickets(root):
    found = {}
    for p in glob.glob(os.path.join(root, '**', 'handoff.md'), recursive=True):
        parts = pathlib.Path(p).relative_to(root).parts
        if any(x.startswith('step-') or x.startswith('verify') for x in parts):
            continue
        t = pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
        fm = t.split('---')[1] if t.startswith('---') and t.count('---') >= 2 else ''
        i = re.search(r'(?m)^id:\s*(T-\d+)', fm)
        if i:
            found[i.group(1)] = {'status': (re.search(r'(?m)^status:\s*(\w+)', fm) or [0, ''])[1],
                                 'text': t, 'budget': bool(re.search(r'(?m)^budget_usd:', fm))}
    return found


def est_scope(text):
    out = set()
    for m in re.finditer(r'(?<![\w/.-])((?:plugins|docs|scripts|skills|agents|src|tests)/[\w./-]*\w\.[A-Za-z0-9]+)', text):
        out.add(m.group(1))
    for m in re.finditer(r'(?<![\w/.-])([\w-]+\.(?:py|sh|md|json|toml))\b', text):
        if m.group(1) in HOT:
            out.add(m.group(1))
    return out


def check_fanout(text, root='.sdlc'):
    text = unwrap(text)
    fails, warns = [], []
    cmds = commands(text)
    if not cmds:
        return [('no-command', 'no `fanout.py run` command found')], warns
    try:
        parser = fanout_parser()
    except Exception as e:  # pragma: no cover
        return [('parser', f'could not read fanout.py flags: {e}')], warns
    tickets = load_tickets(root)
    parsed = []
    for env, args, err in cmds:
        if err:
            fails.append(('command', err))
            continue
        try:
            ns = parser.parse_intermixed_args(args)
        except ValueError as e:
            fails.append(('flag', f'fanout.py would reject this: {e}'))
            continue
        if env.get('SDLC_BACKEND', 'claude') not in ('claude', 'codex'):
            fails.append(('backend', 'SDLC_BACKEND must be claude or codex'))
        parsed.append((env, ns, args))
    if not parsed:
        return fails, warns
    seen, lanes = {}, {}
    for _, ns, _ in parsed[:1]:
        for spec in ns.lanes:
            m = re.fullmatch(r'([A-Za-z0-9._-]+)(?:@[^=\s]+)?=(T-\d+(?:,T-\d+)*)', spec)
            if not m:
                fails.append(('lane-spec', f'`{spec}` is not <lane>=<id>[,<id>...] with ids like T-0123'))
                continue
            for tid in m.group(2).split(','):
                if tid in seen:
                    fails.append(('duplicate-ticket', f'{tid} is in lanes {seen[tid]} and {m.group(1)}'))
                seen[tid] = m.group(1)
                lanes.setdefault(m.group(1), []).append(tid)
                tk = tickets.get(tid)
                if tk is None:
                    fails.append(('unknown-ticket', f'{tid} is not a ticket under {root}'))
                elif tk['status'] in ('done', 'dropped'):
                    fails.append(('closed-ticket', f'{tid} is {tk["status"]}; fanout refuses it'))
                elif not tk['budget']:
                    warns.append(('no-budget', f'{tid} has no budget_usd; set one with budget.py set'))
        ns0 = ns
        cap = ns0.max_lanes
        if cap > parser.hard_cap and not ns0.yes_many:
            fails.append(('yes-many', f'--max-lanes {cap} is above {parser.hard_cap}: add --yes-many'))
        if len(lanes) > cap:
            fails.append(('lane-cap', f'{len(lanes)} lanes against --max-lanes {cap}'))
        if ns0.stagger < 0:
            fails.append(('stagger', '--stagger must be 0 or more'))
        if not ns0.allow_overlap:
            names = list(lanes)
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    for ta in lanes[a]:
                        for tb in lanes[b]:
                            if ta in tickets and tb in tickets:
                                shared = est_scope(tickets[ta]['text']) & est_scope(tickets[tb]['text'])
                                hard = sorted(s for s in shared if os.path.basename(s) not in HOT)
                                hot = sorted(s for s in shared if os.path.basename(s) in HOT)
                                if hard:
                                    fails.append(('overlap', f'{ta} ({a}) and {tb} ({b}) both cite {", ".join(hard)}: '
                                                  'put them in one lane or pass --allow-overlap'))
                                elif hot:
                                    warns.append(('hot-spot', f'{ta} and {tb} both touch {", ".join(hot)}: expect a merge conflict'))
    dry = [i for i, (_, ns, _) in enumerate(parsed) if ns.dry_run]
    real = [i for i, (_, ns, _) in enumerate(parsed) if not ns.dry_run]
    if not dry or (real and dry[0] > real[0]):
        fails.append(('dry-run-first', 'the block must show a --dry-run command before the real one'))
    elif real:
        a, b = [x for x in parsed[dry[0]][2] if x != '--dry-run'], parsed[real[0]][2]
        if a != b:
            fails.append(('dry-run-same', 'the real command must equal the dry run without --dry-run'))
    return fails, warns


# ---- campaign ------------------------------------------------------------------------------------------------
def goal_block(text):
    """(plan text before the /goal block, the /goal block or None). A fenced block wins; else the first `/goal` line to the end."""
    m = re.search(r'(?ms)^```[a-zA-Z]*\n(/goal\s.*?)^```', text) or re.search(r'(?ms)^(/goal\s.*)\Z', text)
    return (text[:m.start()], m.group(1)) if m else (text, None)


def wave_text(plan, n):
    m = re.search(rf'(?ims)^\s*Wave {n}\b.*?(?=^\s*Wave {n + 1}\b|^\s*(?:Stop rules?|Budget|Done when|Reference PR)\b|\Z)', plan)
    return m.group(0) if m else ''


def partition_rows(plan):
    rows = []
    for ln in plan.splitlines():
        cells = [c.strip().strip('`') for c in ln.strip().strip('|').split('|')] if ln.strip().startswith('|') else []
        if len(cells) >= 2 and cells[0] and not set(cells[0]) <= set('-: ') and cells[0].lower() != 'lane':
            rows.append((cells[0], cells[1].rstrip('/')))
    return rows


def machine_load():
    try:
        return os.getloadavg()[0], os.cpu_count() or 1
    except (OSError, AttributeError):  # pragma: no cover
        return 0.0, 1


def check_campaign(text, root='.sdlc', load=None):
    fails, warns = [], []
    plan, goal = goal_block(text)
    if not re.search(r'(?im)^\s*Census\b[^\n]*`[^`]+`[^\n]*', plan):
        fails.append(('no-census', 'name a `Census:` command in backticks that counts the units still to migrate (exit 0, prints a number)'))
    w0 = wave_text(plan, 0)
    if not w0 or not re.search(r'(?i)\bgate\b', w0):
        fails.append(('no-wave0-gate', 'Wave 0 must exist and land a shared tool and a blocking gate'))
    elif not re.search(r'(?i)allowlist', w0):
        warns.append(('no-allowlist', 'Wave 0 names no day-one allowlist, so the gate cannot start green'))
    done = ' '.join(re.findall(r'(?im)^\s*Done when\b[^\n]*', plan))
    if not re.search(r'(?i)`[^`]+`\s+exits?\s+0\b[^\n]*\bmain\b|\bmain\b[^\n]*`[^`]+`\s+exits?\s+0\b', done):
        fails.append(('done-not-command', 'Done when must be a backticked command that exits 0 on main'))
    rows = partition_rows(plan)
    for i, (la, da) in enumerate(rows):
        for lb, db in rows[i + 1:]:
            if da == db or db.startswith(da + '/') or da.startswith(db + '/'):
                fails.append(('overlap', f'lanes {la} ({da}) and {lb} ({db}) share files: the partition must be file-disjoint, one writer per file'))
    cap = re.search(r'(?im)^\s*Lane cap\b\D{0,12}(\d+)', plan)
    reason = re.search(r'(?im)^\s*Cap reason\b[:\s]*\S+', plan)
    if not rows:
        fails.append(('no-partition', 'Wave 1 needs a partition table: | lane | directory | units |'))
    elif not cap:
        fails.append(('no-lane-cap', 'state `Lane cap: N`'))
    elif len(rows) > int(cap.group(1)) and not reason:
        fails.append(('lane-cap', f'{len(rows)} lanes against a cap of {cap.group(1)} with no `Cap reason:` line'))
    stop = ' '.join(re.findall(r'(?im)^\s*(?:Budget and )?stop rules?\b[^\n]*', plan))
    if not re.search(r'\$\s?\d+', stop):
        fails.append(('no-dollar-stop', 'a `Stop rules:` line needs a dollar number'))
    w3 = wave_text(plan, 3)
    if not re.search(r'(?i)\b\d+(\s*(to|-)\s*\d+)?\s+(bulk\s+)?PRs?\b|\bPRs?\b\W{0,3}(target|count|:)\W{0,3}\d+', w3):
        fails.append(('pr-unbounded', 'Wave 3 needs a target PR count (a number or a range like 8 to 10)'))
    if not re.search(r'(?im)^\s*Dependency order\b[^\n]*Wave 0[^\n]*\bbefore\b[^\n]*Wave 1', plan):
        fails.append(('no-order', 'state `Dependency order:` with Wave 0 landing on main before any Wave 1 lane starts'))
    if goal is None:
        fails.append(('no-goal-block', 'return one fenced /goal block that passes `plan_check.py goal`'))
    else:
        fails.extend((f'goal-{r}', w) for r, w in check_goal(goal)[0])
        warns.extend(language_goal(goal))
    warns.extend(lang_warn([('the Campaign line', m.group(0)) for m in re.finditer(r'(?m)^[ \t]*Campaign:[^\n]*', plan)], [], None))
    if not re.search(r'(?im)^\s*Reference PR\b[^\n]*\S', plan):
        warns.append(('no-reference-pr', 'name one reference PR as the pattern every lane copies'))
    l1, cpus = load or machine_load()
    if cap and l1 > cpus / 2 and int(cap.group(1)) > max(1, cpus - l1):
        warns.append(('machine-load', f'lane cap {cap.group(1)} against load {l1:.1f} on {cpus} CPUs (above half): fewer lanes will run than planned'))
    if os.path.basename(os.path.normpath(root)) != '.sdlc' and not load_tickets(root):
        warns.append(('ticket-root', f'{root} holds 0 tickets; `tickets.py --root .sdlc check` may be reading the wrong root'))
    return fails, warns


# ---- plan doc ------------------------------------------------------------------------------------------------
# docs/specs/sdlc-lite/plan-doc-executor.md section 3.3. plan_doc.py is the one parser (plan_done.py reads it too).
PLAN_STATUS = ('draft', 'approved', 'running', 'done', 'stopped')
PLAN_FRONT = ('id', 'title', 'status', 'goal', 'driver')
UNSAFE_NOW = re.compile(r'\brm\b|git push|\bgh |npm publish|curl -X')
AUTH_WORDS = (('git push', r'push'), ('git tag', r'\btag'), ('gh pr', r'gh pr|pull request|\bPRs?\b'),
              ('npm publish', r'publish'), ('onboard.py setup', r'onboard'))
DRIVER_VERIFIES = re.compile(r'(?i)\bdriver\b[^.\n]{0,40}\bverif(?:y|ies|ier)\b|\bverif\w*\s+(?:is\s+)?(?:done\s+)?by\s+(?:the\s+)?driver\b')
UPSERT_HOMES = ('docs/', 'plugins/', 'scripts/')
UPSERT_ROOT_FILES = ('AGENTS.md', 'CLAUDE.md', 'README.md')
TICKET_RE = re.compile(r'T-\d+|new (?:feature|bug|chore|spike|idea) [\w-]+')
MEASURE_COLS = ('id', 'command', 'read', 'target', 'direction')


def writes_file(cmd):
    """True when a command redirects into a file; `2>&1` and `>/dev/null` are not writes."""
    for m in re.finditer(r'(?<![=-])>>?(?![=>])\s*(\S*)', cmd):
        if not (m.group(1).startswith('&') or m.group(1) == '/dev/null'):
            return True
    return False


def same_path(a, b):
    a, b = os.path.normpath(a), os.path.normpath(b)
    return a == b or a.endswith(os.sep + b) or b.endswith(os.sep + a)


def level_rows():
    try:
        data = json.loads((HERE.parent / 'adapters' / 'claude' / 'levels.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return {f'{role}-{lvl}' for role in ('solo', 'builder') for lvl in data.get(role, {})}


def goal_kpis(goal, root):
    """The kpis: ids of the goal file docs/goals/NNN-*.md named by a front matter goal id (G-002), else []."""
    m = re.fullmatch(r'G-(\d+)', goal or '')
    d = pathlib.Path(root).resolve().parent / 'docs' / 'goals'
    if not m or not d.is_dir():
        return []
    for f in sorted(d.glob(f'{m.group(1)}-*.md')):
        k = re.search(r'(?m)^kpis:\s*\[([^\]]*)\]', f.read_text(encoding='utf-8', errors='replace'))
        if k:
            return re.findall(r'K-\d+', k.group(1))
    return []


def kpi_drift(rows, root):
    """Advice only: a Measures row whose command script or target differs from its docs/kpi/NNN-*.md file."""
    kpi = pathlib.Path(root).resolve().parent / 'docs' / 'kpi'
    out = []
    for r in rows:
        m = re.fullmatch(r'K-(\d+)', r.get('id', ''))
        files = sorted(kpi.glob(f'{m.group(1)}-*.md')) if m and kpi.is_dir() else []
        if not files:
            continue
        t = files[0].read_text(encoding='utf-8', errors='replace')
        meas, tgt = re.search(r'(?m)^measure:\s*(.+)$', t), re.search(r'(?m)^target:\s*"?([^"\n]+?)"?\s*$', t)
        cmd = r.get('command', '').strip('`').split()[:3]
        if meas and cmd and meas.group(1).split()[:3] != cmd:
            out.append(('kpi-drift', f'{r["id"]}: the Measures command starts `{" ".join(cmd)}`, the KPI file says `{" ".join(meas.group(1).split()[:3])}`'))
        elif tgt and r.get('target') and tgt.group(1).strip() != r['target'].strip():
            out.append(('kpi-drift', f'{r["id"]}: the Measures target is {r["target"]}, the KPI file says {tgt.group(1).strip()}'))
    return out


def check_plan(text, root='.sdlc', run=False, path=None):
    """(fails, warns) for a plan doc. run adds the checks that apply only before execution starts; path is the file's own path."""
    fails, warns = [], []

    def bad(rule, why):
        fails.append((rule, why))
    doc = plan_doc.parse(text)
    sec = doc.section
    # plan-front
    if not doc.front_ok:
        bad('plan-front', 'the file must open with a `---` front matter block that is closed')
    for k in PLAN_FRONT:
        if doc.front_ok and not doc.front.get(k):
            bad('plan-front', f'front matter lacks `{k}:`')
    status = doc.front.get('status', '')
    if status and status not in PLAN_STATUS:
        bad('plan-front', f'status `{status}` is not one of {", ".join(PLAN_STATUS)}')
    if sec('Goal') is None:
        bad('plan-front', 'missing the `## Goal` section (steps.py reads it)')
    # no-approval
    if run:
        if status not in ('approved', 'running'):
            bad('no-approval', f'--run needs status approved or running, found `{status or "none"}`')
        for k in ('approved_by', 'approved_on'):
            if not doc.front.get(k):
                bad('no-approval', f'--run needs `{k}:` in the front matter')
    # outcome-block, done-measured
    outcome = sec('Outcome')
    measure = None
    if outcome is None:
        bad('outcome-block', 'missing the `## Outcome` section (Outcome, Measured by, Rubric, Negative control)')
    else:
        f2, w2, measure = check_outcome(outcome)
        fails.extend(f2)
        warns.extend(w2)
    done = sec('Done when')
    goal_text, done_rest = plan_doc.goal_line(done)
    if measure and done is not None:
        ids, cmds, target = measure
        d = re.sub(r'\s+', ' ', done_rest)
        if not (any(i in d for i in ids) or any(c in d for c in cmds) or (target and target in d)):
            bad('done-measured', 'Done when must name the Measured by id or command, or its target, so closing tickets alone cannot end the plan')
    # measure-row, measure-safe
    mrows = []
    if sec('Measures') is None:
        bad('measure-row', 'missing the `## Measures` section: one row per KPI the plan reads')
    else:
        mhead, mrows = plan_doc.rows_as_dicts(sec('Measures'))
        miss = [c for c in MEASURE_COLS if c not in mhead]
        if miss:
            bad('measure-row', f'the Measures table lacks the column(s) {", ".join(miss)}')
        elif not mrows:
            bad('measure-row', 'the Measures table has no rows')
        for r in [] if miss else mrows:
            who = r.get('id') or '?'
            for c in MEASURE_COLS:
                if not r.get(c):
                    bad('measure-row', f'Measures row {who} has an empty `{c}` cell')
            if r.get('command') and not re.fullmatch(r'`[^`]+`', r['command']):
                bad('measure-row', f'Measures row {who}: the command must be one backticked span')
            if r.get('direction') and r['direction'] not in ('up', 'down', 'hold'):
                bad('measure-row', f'Measures row {who}: direction must be up, down or hold')
            if not r.get('when') or r['when'] == 'now':
                cmd = r.get('command', '').strip('`')
                hit = UNSAFE_NOW.search(cmd)
                if hit or writes_file(cmd):
                    why = f'contains `{hit.group(0).strip()}`' if hit else 'writes with >'
                    bad('measure-safe', f'Measures row {who} runs now but its command {why}; a measure only reads')
    # later-named
    later = sec('Later measures') or ''
    named = {r.get('id') for r in mrows} | set(re.findall(r'\bK-\d+\b', later))
    cited = list(dict.fromkeys(re.findall(r'\bK-\d+\b', outcome or '') + goal_kpis(doc.front.get('goal'), root)))
    for k in cited:
        if k not in named:
            bad('later-named', f'{k} is cited by the Outcome or the goal but is in neither Measures nor Later measures')
    # steps
    levels = level_rows()
    total = None
    budget = sec('Budget and stop rules')
    if budget is not None:
        m = re.search(r'\$\s?(\d+(?:\.\d+)?)\s*(?:total|overall)\b|\b(?:total|overall)\b[^$\n]{0,30}\$\s?(\d+(?:\.\d+)?)', budget)
        if m:
            total = float(m.group(1) or m.group(2))
    if not doc.steps:
        bad('step-shape', 'no `## Step <n>: <title>` blocks')
    caps, owners = 0.0, {}
    for n, st in sorted(doc.steps.items()):
        k, tag = st.keys, f'step {n}'
        if st.level is None:
            if st.level_lines:
                bad('step-shape', f'{tag}: the level line must read exactly `level: L1` to `level: L5` with nothing after it (steps.py reads it)')
            else:
                bad('step-shape', f'{tag}: lacks `level: L1` to `level: L5`')
        for key in ('ticket', 'depends', 'cap'):
            if not k.get(key):
                bad('step-shape', f'{tag}: lacks `{key}:`')
        if k.get('ticket') and not TICKET_RE.fullmatch(k['ticket']):
            bad('step-shape', f'{tag}: ticket must be an id like T-0413 or `new feature <slug>`')
        if k.get('depends') and st.depends() is None:
            bad('step-shape', f'{tag}: depends must be a list of step numbers like [1, 2]')
        if k.get('cap'):
            if st.cap() is None:
                bad('step-shape', f'{tag}: cap must be a dollar amount like $12')
            else:
                caps += st.cap()
        if not st.criteria:
            bad('step-shape', f'{tag}: needs a numbered or bulleted list under `### Acceptance criteria`')
        for crit, spans in zip(st.criteria, st.spans):
            if VAGUE.search(crit):
                bad('step-shape', f'{tag}: criterion is vague ("{VAGUE.search(crit).group(0)}"): {crit[:60]}')
            elif not spans and not re.search(r'(?i)^see ticket\b|[\w-]+\.(?:py|sh|md|json|toml|js)\b', crit):
                bad('step-shape', f'{tag}: criterion names no backticked command or file: {crit[:60]}')
        for d in st.depends() or []:
            if d == n:
                bad('depends-order', f'{tag}: depends on itself')
            elif d > n:
                bad('depends-order', f'{tag}: depends on step {d}, which comes later')
            elif d not in doc.steps:
                bad('depends-order', f'{tag}: depends on step {d}, which does not exist')
        ex = k.get('executor', 'auto')
        if ex != 'auto' and (levels is None or ex not in levels):
            bad('executor-unknown', f'{tag}: executor `{ex}` is neither auto nor a solo or builder row of adapters/claude/levels.json')
        if k.get('verify', 'auto') not in ('auto', 'required'):
            bad('verifier-seat', f'{tag}: verify must be auto or required, found `{k["verify"]}`')
        if DRIVER_VERIFIES.search(st.text):
            bad('verifier-seat', f'{tag}: the text assigns verification to the driver; the verifier is a separate sub-agent')
        if st.level == 'L1' and k.get('verify', 'auto') == 'auto':
            warns.append(('l1-unverified', f'{tag} is L1 with verify: auto, so no independent verifier will run'))
        if st.upserts() and not any(re.search(r'git grep|docs_check\.py', c) for c in st.criteria):
            bad('upsert-sweep', f'{tag}: lists upserts but no criterion runs `git grep` or `docs_check.py`')
        for p in st.upserts():
            owners.setdefault(p, set()).add(n)
    if total is None:
        bad('cap-sum', 'Budget and stop rules needs a total dollar cap like `$60 total`')
    elif caps > total + 1e-9:
        bad('cap-sum', f'the step caps sum to ${caps:g}, above the total cap of ${total:g}')
    big = [n for n, st in sorted(doc.steps.items()) if st.level in ('L4', 'L5')]
    if big and not doc.front.get('reviewed'):
        bad('review-missing', f'step {big[0]} is {doc.steps[big[0]].level} and the front matter has no `reviewed:` plan-reviewer result')
    # upsert-shape
    up = sec('Upserts')
    if up:
        _, urows = plan_doc.rows_as_dicts(up)
        for r in urows:
            p, mode, stp = r.get('path', '').strip('`'), r.get('mode', ''), r.get('step', '')
            if mode not in ('create', 'edit', 'retire'):
                bad('upsert-shape', f'Upserts row {p or "?"}: mode `{mode}` is not create, edit or retire')
            if not p or p.startswith('/') or '..' in pathlib.PurePosixPath(p).parts or not (
                    p.startswith(UPSERT_HOMES) or p in UPSERT_ROOT_FILES):
                bad('upsert-shape', f'Upserts row {p or "?"}: the path must sit in docs/, plugins/, scripts/ or be a root entry file, inside the repository')
            if not re.fullmatch(r'\d+', stp) or int(stp) not in doc.steps:
                bad('upsert-shape', f'Upserts row {p or "?"}: step `{stp}` is not a step of this plan')
            elif p:
                owners.setdefault(p, set()).add(int(stp))
    for p, who in sorted(owners.items()):
        if len(who) > 1:
            bad('upsert-shape', f'{p} is owned by steps {", ".join(map(str, sorted(who)))}: one writer per file')
    # authorization
    auth = sec('Authorization')
    if auth is None or not auth.strip():
        bad('authorization', 'state exactly what is authorized (publish, push, tag, onboard.py setup, external writes) or `None`')
        auth = ''
    elif not re.match(r'(?i)\s*none\b', auth) and not (
            re.search(r'(?i)\b(none|not implied|never implied|only|authori[sz]ed)\b', auth)
            and re.search(r'(?i)publish|push|tag|release|external|write', auth)):
        bad('authorization', 'state exactly what is authorized (publish, push, tag, onboard.py setup, external writes) or `None`')
    given = '\n'.join(s for s in re.split(r'(?<=[.;])\s+|\n', '' if re.match(r'(?i)\s*none\b', auth) else auth)
                      if not re.search(r'(?i)\bnot\b|\bnever\b|\bnone\b|\bno\b', s))
    for cmd, name in AUTH_WORDS:
        where = [n for n, st in sorted(doc.steps.items()) if cmd in st.text]
        if where and not re.search(name, given, re.I):
            bad('authorization', f'step {where[0]} runs `{cmd}` but Authorization does not name it')
    # stop-rules
    if budget is None:
        bad('stop-rules', 'missing the `## Budget and stop rules` section')
    else:
        for why, ok in (('a dollar cap (a number)', re.search(r'\$\s?\d+', budget)), ('the three-529s rule', '529' in budget),
                        ('the rate or weekly limit rule', re.search(r'(?i)rate|weekly|limit', budget)),
                        ('where state is written (.sdlc/notes.md, or .sdlc/notes/notes.md)', re.search(r'\.sdlc/notes(/notes)?\.md', budget)),
                        ('`replan cap: 1`', re.search(r'(?i)replan cap\W{0,3}1\b', budget))):
            if not ok:
                bad('stop-rules', f'Budget and stop rules needs {why}')
    # goal-line, done-plan-done
    if done is None:
        bad('goal-line', 'missing the `## Done when` section holding `Goal line:`')
        bad('done-plan-done', 'missing the `## Done when` section')
    else:
        if not goal_text:
            bad('goal-line', 'Done when needs `Goal line:` with the fenced one-line /goal text')
        else:
            mp = re.search(r'plan_done\.py\s+([^\s`]+\.md)\b', goal_text)
            if not goal_text.startswith('/goal'):
                bad('goal-line', 'the Goal line must start with `/goal`')
            elif not mp:
                bad('goal-line', 'the Goal line must run `plan_done.py <this plan doc>`')
            elif path and not same_path(mp.group(1), path):
                bad('goal-line', f'the Goal line runs plan_done.py on {mp.group(1)}, not this file ({path})')
            elif not (re.search(r'exits?\s+0', goal_text) and re.search(r'exits?\s+4', goal_text) and 'plan done' in goal_text):
                bad('goal-line', 'the Goal line needs the stop clause: exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop`')
        if not (re.search(r'plan_done\.py', done_rest) and re.search(r'exits?\s+0', done_rest) and re.search(r'exits?\s+4', done_rest)):
            bad('done-plan-done', 'Done when must require `plan_done.py` to exit 0, or exit 4 (stopped with state written)')
    warns.extend(kpi_drift(mrows, root))
    warns.extend(kpi_unresolved(text, root))
    warns.extend(language_plan(doc))
    return fails, warns


GOOD_PLAN = r"""---
id: PD-reliability
title: Restart and blocked run reliability
status: approved
goal: G-002
driver: sonnet-high            # the session that runs run-plan
approved_by: maintainer
approved_on: 2026-10-09
---
## Goal
Build the restart and blocked run tickets in order, one step per ticket, so G-002 has its measures and its fixes.

## Outcome
Outcome: a host restart or a blocked run costs minutes, not hours. Why: lost work per interrupted run is the largest cost of unattended runs.
Measured by: K-002 (`python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d`), before: 34.3, target: <= 15.
Rubric:
1. Lost minutes | pass: K-002 reads 15 or below.
2. No regression | pass: check.sh exits 0 on main.
3. Time measures listed | pass: K-004 sits under Later measures with an owner and a date.
Negative control: K-002 reads 34.3 now, above the target of 15, so it is red before any step lands.

## Measures
| id | command | read | target | direction | before | when |
|---|---|---|---|---|---|---|
| K-002 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` | runs.interrupted.lost_min_median | <= 15 | down | 34.3 | now |
| K-003 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` | results.builder.blocked | <= 1 | down | 4 | now |

## Authorization
The run MUST NOT publish, push, tag or write externally. Authorized: `onboard.py setup` in step 4 only, after `onboard.py check` exits 0.

## Budget and stop rules
Stop and write state to .sdlc/notes.md at $60 total, $20 per step, a rate or weekly limit, or three 529s in a row. replan cap: 1, then stop.

## Step 1: Collector fields for K-002 and K-003
level: L2
ticket: new feature collector-fields
depends: []
executor: auto
verify: auto
cap: $12
### Do
Add the new keys to `fleet_collect.py` and the matching selftest cases.
### Acceptance criteria
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: results: a builder result whose Status is blocked is counted'`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest`

## Step 2: Resume partial work
level: L2
ticket: T-0413
depends: [1]
executor: solo-L2
verify: auto
cap: $12
### Do
Change the dispatch record to name the lane worktree.
### Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`
2. (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`

## Step 3: Restart sweep and the internals reference
level: L3
ticket: T-0414
depends: [1, 2]
executor: builder-L3
verify: required
cap: $20
upserts: [docs/references/sdlc-internals.md]
### Do
Add the sweep and describe it in the internals reference.
### Acceptance criteria
- (red) `grep -qF 'recover --root' plugins/sdlc-lite/scripts/dispatch.py`
- `git grep -qF 'recover --root' -- docs/references/sdlc-internals.md`
- (guard) `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`

## Step 4: Close-out
level: L1
ticket: new chore close-out
depends: [2, 3]
executor: auto
verify: required
cap: $10
### Do
Update the entry file blocks with `python3 plugins/sdlc-lite/scripts/onboard.py setup`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/onboard.py check`

## Upserts
| path | mode | step |
|---|---|---|
| docs/references/sdlc-internals.md | edit | 3 |

## Later measures
| id | read | owner | date |
|---|---|---|---|
| K-004 | per-retro median | maintainer | 2026-11-09 |

## Done when
Measure: K-002 reads <= 15 by the Measured by command.
Plan: `python3 plugins/sdlc-lite/scripts/plan_done.py .sdlc/demo/plan-doc.md` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote state to .sdlc/notes.md.
Goal line:
```
/goal complete build and verify .sdlc/demo/plan-doc.md by the run-plan skill: done when `python3 plugins/sdlc-lite/scripts/plan_done.py .sdlc/demo/plan-doc.md` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote the state. Do not end the turn while it exits 1 and an item is open that you can work on.
```
"""
GOOD_PLAN_PATH = '.sdlc/demo/plan-doc.md'

# ---- clarify -------------------------------------------------------------------------------------------------
CLARIFY_PASS = ('already scoped: ', 'follow-up: ', 'stopped: ')
CLARIFY_OWNER = '[owner: maintainer]'
CLARIFY_VERIFIER = re.compile(r'verifier-L[0-9]|verifier-\*|(?i:verifier result)')
CLARIFY_SHA = re.compile(r'(?<![\w$])[0-9a-f]{7,40}(?!\w)')
CLARIFY_LIVE = re.compile(r'(?i)live run|rehearsal|throwaway project')
# The controlled vocabularies of a clarify handoff. The clarify skill copies both lists on its `Do verbs:` and `Hedge words:`
# lines, and the selftest compares them, so this file stays the one authority.
CLARIFY_VERBS = ('add', 'amend', 'build', 'change', 'close', 'create', 'define', 'delete', 'document', 'extend', 'fix', 'generate',
                 'keep', 'lint', 'link', 'mark', 'merge', 'move', 'record', 'remove', 'rename', 'replace', 'replay', 'report', 'run',
                 'set', 'split', 'test', 'update', 'write')
CLARIFY_HEDGE = ('maybe', 'perhaps', 'possibly', 'probably', 'likely', 'might', 'could', 'ideally', 'hopefully', 'try to',
                 'attempt to', 'somewhat', 'fairly', 'quite', 'rather', 'arguably', 'as needed', 'as appropriate', 'if possible',
                 'where possible', 'if needed', 'etc.')
CLARIFY_HEDGE_RE = re.compile(r'(?i)(?<!\w)(?:' + '|'.join(re.escape(w.rstrip('.')) for w in CLARIFY_HEDGE) + r')(?!\w)')
CLARIFY_TYPES = ('category-mismatch', 'ambiguity', 'conflict', 'assumption', 'missing-acceptance', 'hidden-scope')
_CT = '|'.join(CLARIFY_TYPES)
CLARIFY_DELTA = (re.compile(rf'^- (?:{_CT}): \S.*? -> defaulted: \S.*$'),
                 re.compile(rf'^- (?:{_CT}): \S.*? -> answered: \S.*$'),
                 re.compile(rf'^- (?:{_CT}): \S.*? -> gap \(gap: [^;)]*\S[^;)]*; default: [^)]*\S[^)]*\)$'))
CLARIFY_SOURCE = re.compile(r'\(source: [^)]*\S[^)]*\)')
CLARIFY_EARS = re.compile(r'^When\b[^,]*\S,\s+the\s+\S.*?\sMUST\s+\S')
CLARIFY_RFC_UPPER = re.compile(r'\b(?:MUST|SHALL|SHOULD|MAY|REQUIRED|RECOMMENDED|OPTIONAL)\b')
CLARIFY_RFC_LOWER = re.compile(r'\b(?:must|shall|should)\b')
CLARIFY_GLOSSARY = 'docs/references/glossary.md'


def clarify_section(text, name):
    """The body of `## <name>` up to the next level-1 or level-2 heading, or None when the heading is missing."""
    m = re.search(rf'(?m)^##[ \t]+{re.escape(name)}[ \t]*$', text)
    if not m:
        return None
    end = re.search(r'(?m)^#{1,2}[ \t]', text[m.end():])
    return text[m.end():m.end() + end.start()] if end else text[m.end():]


def clarify_done_items(intent):
    """The Done when items of an Intent body: inline text is one item, then the `- ` list lines that follow. None when absent."""
    lines = intent.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'^([ \t]*)(?:-[ \t]+)?Done when:[ \t]*(.*)$', line)
        if not m:
            continue
        bulleted = line.lstrip().startswith('-')
        items = [m.group(2).strip()] if m.group(2).strip() else []
        for nxt in lines[i + 1:]:
            li = re.match(r'^([ \t]*)-[ \t]+(.*)$', nxt)
            if not li or (bulleted and len(li.group(1)) <= len(m.group(1))):
                break
            items.append(li.group(2).strip())
        return items
    return None


def clarify_block(intent, label, item):
    """(inline text, following item lines) for the first `<label>:` line of an Intent body, or None when the line is missing."""
    lines = intent.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf'^[ \t]*(?:-[ \t]+)?{label}:[ \t]*(.*)$', line)
        if not m:
            continue
        items = []
        for nxt in lines[i + 1:]:
            if not re.match(item, nxt):
                break
            items.append(nxt.strip())
        return m.group(1).strip(), items
    return None


def clarify_glossary_aliases(glossary):
    """The unapproved aliases in the last column of a glossary table. None reads docs/references/glossary.md from the working
    directory and yields none when it is absent (a consumer install has no such file)."""
    if glossary is None:
        p = pathlib.Path(CLARIFY_GLOSSARY)
        glossary = p.read_text(encoding='utf-8') if p.is_file() else ''
    aliases = []
    for line in glossary.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.lstrip().startswith('|') else []
        if len(cells) < 2 or cells[0] == 'Term' or set(cells[0]) <= set('-: '):
            continue
        aliases += [a.strip() for a in cells[-1].split(',') if a.strip()]
    return aliases


def clarify_foreign(token):
    """True when the token is an absolute path outside the git toplevel of the working directory: another repository's
    file (T-0613; the steps.py reads_own_verifier exemption). A relative or in-repo path, or no git, is not foreign."""
    path = token.split('=', 1)[-1]
    if not path.startswith('/'):
        return False
    try:
        r = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False
    top = r.stdout.strip()
    if r.returncode != 0 or not top:
        return False
    a, root = pathlib.Path(path).resolve(), pathlib.Path(top).resolve()
    return not (a == root or root in a.parents)


def clarify_defect(item):
    own = ' '.join(t for t in re.split(r'[\s`\'"]+', item) if not (CLARIFY_VERIFIER.search(t) and clarify_foreign(t)))
    if CLARIFY_VERIFIER.search(own):
        return 'reads its own step\'s verifier result'
    for tok in CLARIFY_SHA.findall(item):
        if re.search(r'[0-9]', tok) and re.search(r'[a-f]', tok):
            return f'names a fixed sha ({tok})'
    if CLARIFY_LIVE.search(item):
        return 'needs a live run a verifier cannot do; move it to [owner: maintainer]'
    return None


def no_code(s):
    return re.sub(r'`[^`\n]*`', '', s)


def check_clarify(text, glossary=None):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines and lines[0].startswith(CLARIFY_PASS):
        if len(lines) == 1:
            return [], []
        return [('clarify-pass-through', 'a pass-through (`already scoped: `, `follow-up: ` or `stopped: `) must be the only line')], []
    fails, warns = [], []
    goal = clarify_section(text, 'Goal')
    if goal is None or not goal.strip():
        fails.append(('clarify-goal', '`## Goal` is missing or empty'))
    goal = (goal or '').strip()
    intent = clarify_section(text, 'Intent') or ''
    nong = clarify_block(intent, 'Non-goals', r'^[ \t]*-[ \t]+\S')
    if not nong or not (nong[0] or nong[1]):
        fails.append(('clarify-non-goals', '`## Intent` has no `Non-goals:` line with text or `- ` lines under it'))
    if not re.search(r'(?m)^[ \t]*(?:-[ \t]+)?Level:[ \t]*L[1-4]\b', intent):
        fails.append(('clarify-level', '`## Intent` has no `Level: L1` to `L4` line'))
    items = clarify_done_items(intent)
    if not items:
        fails.append(('clarify-done', '`## Intent` has no `Done when:` line with an item'))
    ears = set()
    for it in items or []:
        if it.startswith(CLARIFY_OWNER):
            continue
        if CLARIFY_EARS.match(it):
            ears.add(it)
        elif not (re.search(r'`[^`\n]+`', it) or re.search(r'unverifiable: \S', it)):
            fails.append(('clarify-done', 'Done when item is no backticked command, no `When <trigger>, the <system> MUST <response>` '
                                          f'line and no `unverifiable: <why>`: {it[:80]}'))
        why = clarify_defect(it)
        if why:
            fails.append(('clarify-done-defect', f'Done when item {why}: {it[:80]}'))
    deltas = clarify_block(intent, 'Deltas', r'^[ \t]*-[ \t]')
    if deltas:
        if deltas[0] and deltas[0].lower() != 'none':
            fails.append(('clarify-delta', f'`Deltas:` takes `- ` lines, not inline text: {deltas[0][:80]}'))
        for d in deltas[1]:
            if not any(p.match(d) for p in CLARIFY_DELTA):
                fails.append(('clarify-delta', 'a delta is not `- <type>: <statement> -> defaulted: | answered: | gap (gap: ...; '
                                               f'default: ...)` with a type from {", ".join(CLARIFY_TYPES)}: {d[:80]}'))
            elif ' -> defaulted: ' in d and not ('[U]' in d and CLARIFY_SOURCE.search(d)):
                fails.append(('clarify-default-source', f'a defaulted delta needs `[U]` and `(source: <text>)`, else use the gap form: {d[:80]}'))
    do = clarify_block(intent, 'Do', r'^[ \t]*\d+\.[ \t]+\S')
    steps = [re.sub(r'^\d+\.[ \t]+', '', s) for s in do[1]] if do else []
    if not do or do[0] or not steps:
        fails.append(('clarify-do-verb', '`Do:` needs no inline text and numbered `1. <Verb> ...` lines under it'))
    for s in steps:
        first = re.sub(r'[^a-z]', '', s.split()[0].lower()) if s.split() else ''
        if first not in CLARIFY_VERBS:
            fails.append(('clarify-do-verb', f'Do step does not start with a verb from CLARIFY_VERBS: {s[:80]}'))
    for where, s in [('Goal', goal)] + [('Do step', s) for s in steps]:
        hit = CLARIFY_HEDGE_RE.search(no_code(s))
        if hit:
            fails.append(('clarify-hedge', f'{where} holds the hedge word "{hit.group(0)}": {s[:80]}'))
    rfc = [('Goal', ln) for ln in goal.splitlines()]
    for ln in intent.splitlines():
        body = re.sub(r'^[ \t]*-[ \t]+', '', ln).strip()
        if not re.match(r'(?:-[ \t]+)?Literal ask:', ln.strip()) and body not in ears:
            rfc.append(('Intent', ln))
    for where, ln in rfc:
        hit = CLARIFY_RFC_UPPER.search(no_code(ln))
        if hit:
            fails.append(('clarify-rfc2119', f'{where} holds the RFC 2119 keyword {hit.group(0)} outside Literal ask and EARS: {ln.strip()[:80]}'))
    for ln in (clarify_section(text, 'Constraints') or '').splitlines():
        hit = CLARIFY_RFC_LOWER.search(no_code(ln))
        if hit:
            fails.append(('clarify-rfc2119', f'a Constraints line writes "{hit.group(0)}" in lower case; write MUST or MUST NOT: {ln.strip()[:80]}'))
    prose = no_code(goal)
    n_sent = len([s for s in re.split(r'[.!?](?:\s+|$)', prose) if s.strip()])
    if n_sent > 2 or len(prose.split()) > 50:
        warns.append(('clarify-goal-length', f'the Goal has {n_sent} sentences and {len(prose.split())} words; keep it to 2 and 50'))
    for a in clarify_glossary_aliases(glossary):
        pat = re.compile(rf'(?i)(?<!\w){re.escape(a)}(?!\w)')
        for where, s in [('Goal', goal)] + [('Do step', s) for s in steps]:
            if pat.search(no_code(s)):
                warns.append(('clarify-glossary', f'{where} uses the unapproved alias "{a}" (docs/references/glossary.md)'))
    return fails, warns


# ---- controlled language of plan artifacts (T-0469) ---------------------------------------------------------
# The rules of T-0461 applied to goal, campaign and plan-doc text, reusing the clarify lists and patterns above. Three warnings, not
# FAILs, until the five-ask replay shows how often they misfire: hedge (a CLARIFY_HEDGE word in the /goal line, a Goal or an Outcome
# line), verb (a How to work or step Do statement whose first word is not in CLARIFY_VERBS) and rfc2119 (an Authorization with no
# upper-case MUST, or a lower-case must, shall or should in it).
LANG_OUTCOME = re.compile(r'(?m)^[ \t]*Outcome:[^\n]*')


def lang_leads(body, every=False):
    """The statements of a body that open with a verb: list items and the line after a blank (every non-blank line when every is
    set), with the list marker removed and fenced lines skipped."""
    out, blank, fence = [], True, False
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith('```'):
            fence = not fence
            continue
        if fence:
            continue
        if not s:
            blank = True
            continue
        item = re.match(r'(?:[-*]|\d+\.)[ \t]+(.*)', s)
        if every or blank or item:
            out.append(item.group(1) if item else s)
        blank = False
    return out


def lang_warn(hedged, led, auth):
    """warns for (where, text) pairs to scan for hedge words, pairs whose first word must be a verb, and an Authorization body or None."""
    warns = []
    for where, s in hedged:
        hit = CLARIFY_HEDGE_RE.search(no_code(s))
        if hit:
            warns.append(('hedge', f'{where} holds the hedge word "{hit.group(0)}": {s.strip()[:80]}'))
    for where, s in led:
        first = re.sub(r'[^a-z]', '', s.split()[0].lower()) if s.split() else ''
        if first not in CLARIFY_VERBS:
            warns.append(('verb', f'{where} does not start with a verb from CLARIFY_VERBS: {s[:80]}'))
    if auth is not None:
        if not re.search(r'\bMUST\b', no_code(auth)):
            warns.append(('rfc2119', 'Authorization has no `MUST` or `MUST NOT` line; write what the run MUST NOT do'))
        for ln in auth.splitlines():
            hit = CLARIFY_RFC_LOWER.search(no_code(ln))
            if hit:
                warns.append(('rfc2119', f'Authorization writes "{hit.group(0)}" in lower case; write MUST or MUST NOT: {ln.strip()[:80]}'))
    return warns


def language_goal(text):
    """The controlled-language warnings of a /goal block."""
    text = unwrap(text)
    sec = sections(text)
    hedged = [('the /goal line', text.splitlines()[0] if text else '')] + [('the Outcome line', m.group(0)) for m in LANG_OUTCOME.finditer(text)]
    led = [('How to work', s) for s in lang_leads(re.sub(r'(?i)^\s*How to work[^:\n]*:?', '', sec.get('how', ''), count=1), every=True)]
    auth = re.sub(r'(?i)^\s*Authori[sz](?:ation|ed)[^:\n]*:?', '', sec['auth'], count=1) if 'auth' in sec else None
    return lang_warn(hedged, led, auth)


def language_plan(doc):
    """The controlled-language warnings of a parsed plan doc: the Goal and Outcome lines, each step's Do, and Authorization."""
    hedged = [('the Goal', ln) for ln in (doc.section('Goal') or '').splitlines() if ln.strip()]
    hedged += [('the Outcome line', m.group(0)) for m in LANG_OUTCOME.finditer(doc.section('Outcome') or '')]
    led = []
    for n, st in sorted(doc.steps.items()):
        m = re.search(r'(?ims)^###[ \t]+Do\b[^\n]*\n(.*?)(?=^###[ \t]|\Z)', st.text)
        led += [(f'step {n} Do', s) for s in lang_leads(m.group(1))] if m else []
    return lang_warn(hedged, led, doc.section('Authorization'))


# ---- cost line (--summary) -----------------------------------------------------------------------------------
def cost_line(text, root='.sdlc'):
    """`cost: $<sum of caps> of $<cap> (<n> tickets: T-0001 L2 $30, ...)` for the tickets a block names. The cap of a ticket is its
    size level's row in budget.py TIERS. A ticket with no size, no row in TIERS or no folder under root makes the sum `unknown`, never 0;
    a block that names no ticket sums to `unknown`; no `$<n> total` figure in the block makes the cap `unknown`; a sum above the
    cap ends with `over`. A ceiling, not a forecast of spend."""
    import budget  # lazy: budget imports tickets, which no other lint here needs
    found = load_tickets(root)
    rows, total = [], 0
    for tid in dict.fromkeys(re.findall(r'\bT-\d+\b', text)):
        size = re.search(r'(?m)^size:[ \t]*(\S+)', found[tid]['text'].split('---')[1]) if tid in found else None
        level = budget.tickets.size_level(size.group(1)) if size else None
        usd = budget.tier_usd(level) if level else None
        if usd is None:
            total = None
        elif total is not None:
            total += usd
        rows.append(f'{tid} {level} ${usd:g}' if usd is not None else f'{tid} unknown')
    cap = re.search(r'\$\s?(\d+(?:\.\d+)?)\s+total\b|total cap[ :]+\$\s?(\d+(?:\.\d+)?)', text)
    cap = float(cap.group(1) or cap.group(2)) if cap else None
    shown = f'${total:g}' if rows and total is not None else 'unknown'
    over = ' over' if total is not None and cap is not None and total > cap else ''
    return f'cost: {shown} of {f"${cap:g}" if cap is not None else "unknown"} ({len(rows)} ticket{"" if len(rows) == 1 else "s"}' \
           f'{": " + ", ".join(rows) if rows else ""}){over}'

# ---- compaction ----------------------------------------------------------------------------------------------
COMPACTION_HEADERS = ('GOAL', 'RULES', 'DECISIONS', 'STATE', 'OPEN', 'NEXT', 'DROP')
COMPACTION_VERBS = ('KEEP', 'POINT', 'DROP', 'NEXT')
COMPACTION_ENTRY = ('CLAUDE.md', 'AGENTS.md')
COMPACTION_MAX_LINES, COMPACTION_MAX_PIN, COMPACTION_MAX_WORDS = 60, 40, 20
COMPACTION_EM_DASH = chr(0x2014)  # U+2014, built from its code point: the repository bans the literal character
COMPACTION_APPROVAL = re.compile(r'(?i)(?<!\w)(?:approv(?:e|ed|al)|authori[sz](?:e|ed|ation)|consent|agreed|signed off)(?!\w)')
COMPACTION_WHO = re.compile(r'^(?:user|agent) \d{4}-\d{2}-\d{2} \S')


def compaction_rows(text):
    """(section, line) for each non-blank line of an unwrapped block. A header row holds its own name and the line None; a line
    before the first header holds the section None."""
    rows, sec = [], None
    for ln in text.splitlines():
        s = ln.strip()
        if s in COMPACTION_HEADERS:
            sec = s
            rows.append((s, None))
        elif s:
            rows.append((sec, s))
    return rows


def compaction_pins(rows):
    return [s for sec, s in rows if s is not None and sec in COMPACTION_HEADERS[:6] and s != 'none' and s.split()[0] not in ('POINT', 'DROP')]


def compaction_counts(text):
    """(lines, PIN lines) of a block, counted on the unwrapped text."""
    text = unwrap(text)
    return len(text.splitlines()), len(compaction_pins(compaction_rows(text)))


def check_compaction(text, entry=None, glossary=None):
    """`entry` is a list of entry-file texts; None reads CLAUDE.md and AGENTS.md from the working directory and skips a missing file."""
    text = unwrap(text)
    fails, warns = [], []
    rows = compaction_rows(text)
    body = [(sec, s) for sec, s in rows if s is not None]
    heads = [sec for sec, s in rows if s is None]
    if heads != list(COMPACTION_HEADERS):
        fails.append(('compaction-order', f'the headers read "{" ".join(heads)}"; write {", ".join(COMPACTION_HEADERS)} once each, in that order'))
    before = next((i for i, (_, s) in enumerate(rows) if s is None), len(rows))
    if before != 1:
        fails.append(('compaction-order', f'{before} lines stand before the first header; write one identity line before GOAL'))
    if not body or rows[-1][1] is None or not rows[-1][1].startswith('NEXT '):
        fails.append(('compaction-order', 'the last line does not start with `NEXT `'))
    n_lines, pins = len(text.splitlines()), compaction_pins(rows)
    if n_lines > COMPACTION_MAX_LINES:
        fails.append(('compaction-lines', f'the block has {n_lines} lines; the cap is {COMPACTION_MAX_LINES}'))
    if len(pins) > COMPACTION_MAX_PIN:
        fails.append(('compaction-pin', f'the block has {len(pins)} PIN lines; the cap is {COMPACTION_MAX_PIN}: demote some to POINT lines'))
    if COMPACTION_EM_DASH in text:
        fails.append(('compaction-em-dash', 'the block holds an em dash (U+2014)'))
    if entry is None:
        entry = [p.read_text(encoding='utf-8') for p in map(pathlib.Path, COMPACTION_ENTRY) if p.is_file()]
    known = {' '.join(re.sub(r'^(?:[-*+]|\d+[.)])\s+', '', ln.strip()).split()) for t in entry for ln in t.splitlines()}
    for sec, s in body:
        toks = s.split()
        n = len([t for t in toks if t != '|'])
        if n > COMPACTION_MAX_WORDS:
            fails.append(('compaction-words', f'a line holds {n} words; the cap is {COMPACTION_MAX_WORDS}: {s[:80]}'))
        if sec == 'DROP' and toks[0] not in ('DROP', 'NEXT'):
            fails.append(('compaction-verb', f'a DROP section line starts with neither DROP nor NEXT: {s[:80]}'))
        elif re.fullmatch(r'[A-Z]{3,}', toks[0]) and toks[0] not in COMPACTION_VERBS:
            fails.append(('compaction-verb', f'"{toks[0]}" is not one of {", ".join(COMPACTION_VERBS)}: {s[:80]}'))
        if len(toks) >= 4 and ' '.join(toks[1:] if toks[0] in COMPACTION_VERBS else toks) in known:
            fails.append(('compaction-entry-copy', f'a line copies an entry file ({" or ".join(COMPACTION_ENTRY)}); drop it or POINT to the file: {s[:80]}'))
        if sec == 'DECISIONS' and s != 'none' and toks[0] != 'POINT':
            cells = [c.strip() for c in s.split('|')]
            if not (len(cells) == 3 and COMPACTION_WHO.match(cells[0]) and 1 <= len(cells[1].split()) <= 5 and cells[2]):
                fails.append(('compaction-decision', 'a DECISIONS line is not `<user|agent> <YYYY-MM-DD> <decision> | <reason of 1 to 5 words> | '
                                                     f'<pointer>`: {s[:80]}'))
        hit = COMPACTION_APPROVAL.search(s)
        if hit and not (re.search(r'"[^"\n]+"', s) or '[U]' in s):
            fails.append(('compaction-approval', f'"{hit.group(0)}" stands with neither the user\'s quoted words nor `[U]`: {s[:80]}'))
    for a in clarify_glossary_aliases(glossary):
        pat = re.compile(rf'(?i)(?<!\w){re.escape(a)}(?!\w)')
        for _, s in body:
            if pat.search(no_code(s)):
                warns.append(('compaction-glossary', f'a line uses the unapproved alias "{a}" (docs/references/glossary.md): {s[:80]}'))
    return fails, warns


COMPACTION_RETURN_LAST = 'Run: /compact <paste>'


def check_compaction_return(reply):
    """The return shape of references/compaction.md section 6, read on the whole reply: one finding per departure."""
    rows = reply.strip('\n').splitlines()
    if rows and rows[0].startswith('stale: '):
        rows = rows[1:]
    if not rows or rows[0].strip() != '```':
        return [('compaction-return', 'the reply does not open with the fence (only one `stale: ` line may come first)')]
    ends = [i for i, ln in enumerate(rows) if i and ln.strip() == '```']
    if not ends:
        return [('compaction-return', 'the fenced block is never closed')]
    block, tail = '\n'.join(rows[1:ends[0]]), [ln.strip() for ln in rows[ends[0] + 1:]]
    n_lines, n_pin = compaction_counts(block)
    want = [f'lines: {n_lines} of {COMPACTION_MAX_LINES}', f'pin: {n_pin} of {COMPACTION_MAX_PIN}', COMPACTION_RETURN_LAST]
    if tail != want:
        return [('compaction-return', 'after the fence the reply must be exactly the lines ' + ' / '.join(want) + f'; it holds {len(tail)} line(s): {" / ".join(tail)[:120]}')]
    return []


# ---- driver --------------------------------------------------------------------------------------------------
def run_check(kind, text, root='.sdlc', run=False, path=None):
    return {'goal': lambda t: check_goal(t, root), 'loop': check_loop, 'fanout': lambda t: check_fanout(t, root),
            'campaign': lambda t: check_campaign(t, root), 'plan': lambda t: check_plan(t, root, run, path),
            'clarify': check_clarify, 'compaction': check_compaction}[kind](text)


def report(kind, fails, warns, out=print):
    for r, w in fails:
        out(f'FAIL {r}: {w}')
    for r, w in warns:
        out(f'warn {r}: {w}')
    if not fails:
        out('ok: plan doc passes' if kind == 'plan' else f'ok: {kind} plan passes')
    return 1 if fails else 0


GOOD_GOAL = """```
/goal Overnight: ship the three listed tickets, then stop.

Scope (verify with tickets.py check first):
1. T-0001 first thing
2. T-0002 second thing

Outcome: every run leaves a cost row. Why: spend and load cannot be sized from unmetered runs.
Measured by: K-001 (`python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d`), before: 8.3, target: <= 5.
Rubric:
1. Unmetered share | pass: the measure reads 5 or below.
2. No regression | pass: check.sh exits 0 on main.
3. Scope held | pass: only T-0001 and T-0002 are closed by this goal.
Negative control: the measure reads 8.3 now, above the target of 5, so it is red before any ticket lands.

How to work: run steps.py lane first, then solo for S and M; keep the replan cap at one, then record a limit; report every claim from a command.
Fix every verifier fail and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $60 total, $15 per ticket, a rate or weekly limit, or three 529s in a row.

Authorization: The run MUST NOT publish, push or tag. Authorized: a fast-forward push of the release commit only if the fact-check passes.

Done when: K-001 reads <= 5 (the Measured by command), tickets.py check exits 0 and T-0001 and T-0002 are closed on main, or the goal stopped on a limit with state written to .sdlc/notes.md.
```"""
GOOD_CAMPAIGN = """Campaign: granular dependency loading is the standard for every page

Census: `python3 scripts/census-page-css.py` exits 0 and prints the pages still linking a bundle (158 at planning time: 136 on components.css, 22 on themes.css)
Dependency order: Wave 0 lands on main before any Wave 1 lane starts; Wave 2 starts when every Wave 1 lane is merged; Wave 3 starts when Wave 2 passes.
Lane cap: 16
Cap reason: 50 file-disjoint directories and the owner authorized --yes-many; uptime checked first.

Wave 0 (one lane, lands first): a derivation tool and a blocking gate `python3 scripts/check-page-css.py`, wired into the existing gate chain with no new CI job. The gate starts green through a day-one allowlist of current violators, each with a justification string; a stale entry fails the gate.
Wave 1 (50 lanes, file-disjoint, one writer per file): each lane migrates its pages and deletes its own allowlist entries.
Reference PR: #412 (the pattern every lane copies)

__ROWS__

Wave 2 (bulk review): one verifier per bundle of 5 to 10 lanes on a different model family than the builders, plus a probe sweep with before and after request counts per page (say dev server or dist).
Wave 3 (bulk PRs): one integration branch per area, 8 to 10 PRs, one plain push each.

Stop rules: stop and write state to .sdlc/notes.md at $900 total (a backstop: level L2 $30 times 30 lanes), $30 per lane, a rate or weekly limit, or three 529s in a row.
Done when: `python3 scripts/check-page-css.py` exits 0 on main with an empty allowlist

```
/goal Migrate every page to granular dependency loading, then stop.

Scope (verify with tickets.py check first):
1. Wave 0: the derivation tool and the blocking gate with a day-one allowlist
2. Wave 1: 50 file-disjoint page lanes
3. Wave 2: bulk verifier review and probe sweep
4. Wave 3: 8 to 10 bulk PRs

Outcome: every page loads only the dependencies it uses. Why: the shared bundles cost every page load.
Measured by: `python3 scripts/census-page-css.py`, before: 158, target: 0.
Rubric:
1. Pages still on a bundle | pass: the census prints 0.
2. Gate holds | pass: `python3 scripts/check-page-css.py` exits 0 on main with an empty allowlist.
3. Scope held | pass: only the four waves land.
Negative control: the census prints 158 now, above the target of 0, so it is red before Wave 0 lands.

How to work: run steps.py lane first; keep one writer per file; land Wave 0 before any lane starts; keep the replan cap at one, then record a limit.
Fix every verifier fail and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $900 total, $30 per lane, a rate or weekly limit, or three 529s in a row. No retry loops.

Authorization: The run MUST NOT publish, tag or deploy. Authorized: one plain push per integration branch.

Done when: `python3 scripts/census-page-css.py` prints 0 and `python3 scripts/check-page-css.py` exits 0 on main with an empty allowlist, or the goal stopped on a limit with state written to .sdlc/notes.md.
```
"""
GOOD_ROWS = '| lane | directory | units |\n|---|---|---|\n' + '\n'.join(f'| p{i:02d} | site/pages/a{i:02d} | 3 |' for i in range(50))
GOOD_CAMPAIGN = GOOD_CAMPAIGN.replace('__ROWS__', GOOD_ROWS)
GOOD_LOOP = "/loop 20m a status update with progress since the last run; stop when .sdlc/notes.md says done"


def plan_selftest(expect):
    """One observed-failing mutant per rule of section 3.3, each of which must be flagged as exactly its rule."""
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, '.sdlc')
        os.makedirs(root)
        P = GOOD_PLAN

        def rules(text, run=False, root=root, path=GOOD_PLAN_PATH):
            return sorted({r for r, _ in check_plan(text, root=root, run=run, path=path)[0]})

        def mutant(rule, why, text, run=False, **kw):
            got = rules(text, run=run, **kw)
            expect(f'plan: {rule} mutant "{why}" is flagged as exactly {rule}', got == [rule])
            if got != [rule]:
                print('  got', got, [w for r, w in check_plan(text, root=root, run=run, path=GOOD_PLAN_PATH)[0]][:3])

        def swap(old, new, count=1):
            assert old in P, old
            return P.replace(old, new, count)
        f, w = check_plan(P, root=root, path=GOOD_PLAN_PATH)
        expect('plan: GOOD_PLAN passes with no FAIL and no warning', not f and not w)
        f, w = check_plan(P, root=root, run=True, path=GOOD_PLAN_PATH)
        expect('plan: GOOD_PLAN passes with --run', not f)
        expect('plan: GOOD_PLAN passes without a known path', not check_plan(P, root=root)[0])
        expect('plan: a plan that reports ok exits 0 through report()', report('plan', *check_plan(P, root=root), out=lambda s: None) == 0)
        expect('plan: a failing plan exits 1 through report()', report('plan', *check_plan('x', root=root), out=lambda s: None) == 1)
        # plan-front
        mutant('plan-front', 'driver line deleted', swap('driver: sonnet-high            # the session that runs run-plan\n', ''))
        mutant('plan-front', 'status: busy', swap('status: approved', 'status: busy'))
        mutant('plan-front', 'front matter deleted', P[P.index('## Goal'):])
        mutant('plan-front', 'Goal section deleted', re.sub(r'(?ms)^## Goal\n.*?(?=^## Outcome)', '', P))
        # no-approval (with --run)
        mutant('no-approval', 'status: draft with --run', swap('status: approved', 'status: draft'), run=True)
        mutant('no-approval', 'approved_on deleted with --run', swap('approved_on: 2026-10-09\n', ''), run=True)
        mutant('no-approval', 'approved_by deleted with --run', swap('approved_by: maintainer\n', ''), run=True)
        expect('plan: no-approval is silent without --run: a draft plan passes', not check_plan(swap('status: approved', 'status: draft'), root=root)[0])
        expect('plan: no-approval accepts status running with --run', not check_plan(swap('status: approved', 'status: running'), root=root, run=True)[0])
        # outcome-block, done-measured (the goal check's own mutants, applied to the plan text)
        mutant('outcome-block', 'Outcome line deleted', re.sub(r'(?m)^Outcome:.*\n', '', P))
        mutant('outcome-block', 'Why deleted', swap(' Why: lost work per interrupted run is the largest cost of unattended runs.', ''))
        mutant('outcome-block', 'before deleted', swap(' before: 34.3,', ''))
        mutant('outcome-block', 'target deleted', swap(', target: <= 15', ''))
        mutant('outcome-block', 'Rubric cut to 2', swap('3. Time measures listed | pass: K-004 sits under Later measures with an owner and a date.\n', ''))
        mutant('outcome-block', 'one pass deleted', swap(' | pass: check.sh exits 0 on main.', ''))
        mutant('outcome-block', 'Negative control deleted', re.sub(r'(?m)^Negative control:.*\n', '', P))
        mutant('outcome-block', 'Outcome section deleted', re.sub(r'(?ms)^## Outcome\n.*?(?=^## Measures)', '', P))
        mutant('done-measured', 'Done when only closes tickets', swap('Measure: K-002 reads <= 15 by the Measured by command.', 'All step tickets are closed.'))
        mutant('done-measured', 'Done when names a different K id', swap('Measure: K-002 reads <= 15 by the Measured by command.', 'Measure: K-003 reads below its limit.'))
        expect('plan: done-measured accepts the Measured by command in Done when',
               not check_plan(swap('Measure: K-002 reads <= 15 by the Measured by command.',
                                   'Measure: `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` reads 15 or below.'), root=root)[0])
        # T-0438: a measure id of any letter is the id Done when must name (an M- id used to pass only when the target text was named too)
        pm = P.replace('K-002', 'M-002').replace('Measure: M-002 reads <= 15 by the Measured by command.', 'Measure: M-002 reads below its limit.')
        expect('plan: done-measured accepts an M- measure id named in Done when', not check_plan(pm, root=root)[0])
        expect('plan: done-measured control: the M- plan with Done when naming no id still fails',
               any(r == 'done-measured' for r, _ in check_plan(pm.replace('Measure: M-002 reads below its limit.', 'All step tickets are closed.'), root=root)[0]))
        # measure-row, measure-safe
        mutant('measure-row', 'target cell emptied', swap('| runs.interrupted.lost_min_median | <= 15 |', '| runs.interrupted.lost_min_median |  |'))
        mutant('measure-row', 'command unquoted', swap('| K-002 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` |', '| K-002 | python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d |'))
        mutant('measure-row', 'direction sideways', swap('| <= 15 | down |', '| <= 15 | sideways |'))
        expect('plan: measure-row flags a plan with no Measures section',
               'measure-row' in rules(re.sub(r'(?ms)^## Measures\n.*?(?=^## Authorization)', '', P)))
        mutant('measure-row', 'direction column deleted', swap('| id | command | read | target | direction | before | when |', '| id | command | read | target | before | when |'))
        mutant('measure-safe', 'now command contains git push', swap('| K-003 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` |', '| K-003 | `git push origin main` |'))
        mutant('measure-safe', 'now command writes with >', swap('| K-003 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` |', '| K-003 | `python3 x.py > out.txt` |'))
        mutant('measure-safe', 'now command contains rm', swap('| K-003 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` |', '| K-003 | `rm -rf out` |'))
        expect('plan: measure-safe lets a redirect to /dev/null and 2>&1 through',
               not check_plan(swap('| K-003 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` |', '| K-003 | `python3 x.py 2>&1 >/dev/null` |'), root=root)[0])
        expect('plan: measure-safe ignores a later measure', not check_plan(swap('| results.builder.blocked | <= 1 | down | 4 | now |', '| results.builder.blocked | <= 1 | down | 4 | later: owner, 2026-11-09 |').replace(
            '| K-003 | `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` |', '| K-003 | `git push origin main` |'), root=root)[0])
        # later-named
        mutant('later-named', 'Later measures row for K-004 deleted', swap('| K-004 | per-retro median | maintainer | 2026-11-09 |\n', ''))
        docs = os.path.join(d, 'docs')
        os.makedirs(os.path.join(docs, 'goals'))
        goal = pathlib.Path(docs, 'goals', '002-x.md')
        goal.write_text('---\nid: G-002\nkpis: [K-002, K-004, K-005]\n---\n')
        mutant('later-named', 'the goal file lists K-005 that the plan never names', P)
        goal.write_text('---\nid: G-002\nkpis: [K-002, K-003, K-004]\n---\n')
        expect('plan: later-named is satisfied when Measures and Later measures name every goal KPI', not check_plan(P, root=root, path=GOOD_PLAN_PATH)[0])
        # kpi warnings never fail
        os.makedirs(os.path.join(docs, 'kpi'))
        pathlib.Path(docs, 'kpi', '002-x.md').write_text('---\nid: K-002\ntarget: "<= 20"\nmeasure: python3 plugins/sdlc-lite/scripts/fleet_collect.py collect <repo> --since <date>\n---\n')
        f, w = check_plan(P, root=root, path=GOOD_PLAN_PATH)
        expect('plan: a Measures target that differs from docs/kpi warns kpi-drift and does not fail', not f and any(r == 'kpi-drift' for r, _ in w))
        expect('plan: a K id with no docs/kpi file warns kpi-unresolved and does not fail', not f and any(r == 'kpi-unresolved' for r, _ in w))
        pathlib.Path(docs, 'kpi', '002-x.md').write_text('---\nid: K-002\ntarget: "<= 15"\nmeasure: python3 x/other.py collect\n---\n')
        f, w = check_plan(P, root=root, path=GOOD_PLAN_PATH)
        expect('plan: a Measures command that differs from docs/kpi warns kpi-drift and does not fail', not f and any(r == 'kpi-drift' for r, _ in w))
        # step-shape
        mutant('step-shape', 'cap deleted from step 2', swap('executor: solo-L2\nverify: auto\ncap: $12\n', 'executor: solo-L2\nverify: auto\n'))
        mutant('step-shape', 'a criterion reading "looks good"', swap('1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`', '1. the record looks good'))
        mutant('step-shape', 'a criterion with no command or file', swap('1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`', '1. the dispatch record is correct'))
        mutant('step-shape', 'ticket deleted from step 1', swap('ticket: new feature collector-fields\n', ''))
        mutant('step-shape', 'depends deleted from step 2', swap('depends: [1]\nexecutor: solo-L2', 'executor: solo-L2'))
        mutant('step-shape', 'level line with a trailing note', swap('level: L2\nticket: T-0413', 'level: L2  # note\nticket: T-0413'))
        mutant('step-shape', 'level line deleted', swap('level: L2\nticket: T-0413\n', 'ticket: T-0413\n'))
        mutant('step-shape', 'criteria list deleted from step 4', swap('- `python3 plugins/sdlc-lite/scripts/onboard.py check`\n', ''))
        mutant('step-shape', 'ticket that is not an id', swap('ticket: T-0413', 'ticket: soon'))
        mutant('step-shape', 'cap that is not a dollar amount', swap('cap: $10', 'cap: ten'))
        expect('plan: step-shape accepts a `see ticket` criterion', not check_plan(swap('1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest`', '1. see ticket'), root=root)[0])
        # depends-order
        mutant('depends-order', 'step 2 depends on step 3', swap('depends: [1]\nexecutor: solo-L2', 'depends: [3]\nexecutor: solo-L2'))
        mutant('depends-order', 'step 2 depends on itself', swap('depends: [1]\nexecutor: solo-L2', 'depends: [2]\nexecutor: solo-L2'))
        mutant('depends-order', 'step 2 depends on an absent step 9', swap('depends: [1]\nexecutor: solo-L2', 'depends: [1, 9]\nexecutor: solo-L2'))
        # cap-sum
        mutant('cap-sum', 'a step cap raised so the sum passes the total by $1', swap('cap: $12', 'cap: $19'))
        mutant('cap-sum', 'total cap missing', swap('at $60 total, $20 per step,', 'at $20 per step,'))
        expect('plan: cap-sum accepts caps that equal the total', not check_plan(swap('cap: $12', 'cap: $18'), root=root)[0])
        # executor-unknown
        mutant('executor-unknown', 'executor: haiku-5.5-high on a step', swap('executor: solo-L2', 'executor: haiku-5.5-high'))
        mutant('executor-unknown', 'a planner row is not a worker row', swap('executor: solo-L2', 'executor: planner-L2'))
        mutant('executor-unknown', 'a solo level that does not exist', swap('executor: solo-L2', 'executor: solo-L5'))
        # verifier-seat
        mutant('verifier-seat', 'verify: none on an L2 step', swap('verify: auto\ncap: $12\n### Do\nChange', 'verify: none\ncap: $12\n### Do\nChange'))
        mutant('verifier-seat', 'step text assigns verification to the driver', swap('Change the dispatch record to name the lane worktree.', 'Change the dispatch record to name the lane worktree. The driver verifies this step.'))
        mutant('verifier-seat', 'verified by the driver', swap('Change the dispatch record to name the lane worktree.', 'Change the dispatch record to name the lane worktree; verification is done by the driver.'))
        f, w = check_plan(swap('verify: required\ncap: $10', 'verify: auto\ncap: $10'), root=root)
        expect('plan: an L1 step with verify: auto warns l1-unverified and does not fail', not f and any(r == 'l1-unverified' for r, _ in w))
        # review-missing
        mutant('review-missing', 'a step raised to L4 with no reviewed:', swap('level: L2\nticket: new feature collector-fields', 'level: L4\nticket: new feature collector-fields'))
        expect('plan: review-missing is satisfied by a reviewed: line', not check_plan(swap('level: L2\nticket: new feature collector-fields', 'level: L5\nticket: new feature collector-fields').replace(
            'approved_on: 2026-10-09\n', 'approved_on: 2026-10-09\nreviewed: .sdlc/demo/plan-reviewer-L1.md\n'), root=root)[0])
        # upsert-shape
        mutant('upsert-shape', 'the same path listed for steps 3 and 4', swap('| docs/references/sdlc-internals.md | edit | 3 |', '| docs/references/sdlc-internals.md | edit | 3 |\n| docs/references/sdlc-internals.md | edit | 4 |'))
        mutant('upsert-shape', 'a mode outside the three', swap('| edit | 3 |', '| delete | 3 |'))
        mutant('upsert-shape', 'a path outside the repository', swap('| docs/references/sdlc-internals.md | edit | 3 |', '| ../outside.md | edit | 3 |'))
        mutant('upsert-shape', 'a path outside the allowed homes', swap('| docs/references/sdlc-internals.md | edit | 3 |', '| src/app.py | edit | 3 |'))
        mutant('upsert-shape', 'a step that does not exist', swap('| edit | 3 |', '| edit | 9 |'))
        expect('plan: upsert-shape accepts a root entry file and a retire row', not check_plan(swap('| docs/references/sdlc-internals.md | edit | 3 |', '| docs/references/sdlc-internals.md | edit | 3 |\n| AGENTS.md | retire | 4 |'), root=root)[0])
        # upsert-sweep
        mutant('upsert-sweep', 'the sweep criterion of step 3 deleted', swap("- `git grep -qF 'recover --root' -- docs/references/sdlc-internals.md`\n", ''))
        # authorization
        mutant('authorization', 'Authorization reduced to None while step 4 runs onboard.py setup',
               swap('The run MUST NOT publish, push, tag or write externally. Authorized: `onboard.py setup` in step 4 only, after `onboard.py check` exits 0.', 'None.'))
        mutant('authorization', 'a step runs git push that Authorization never names',
               swap('Add the sweep and describe it in the internals reference.', 'Add the sweep and describe it in the internals reference, then run git push origin main.'))
        mutant('authorization', 'Authorization section deleted', re.sub(r'(?ms)^## Authorization\n.*?(?=^## Budget)', '', P))
        mutant('authorization', 'a criterion runs gh pr create', swap("- `python3 plugins/sdlc-lite/scripts/onboard.py check`", "- `gh pr create --fill`"))
        mutant('authorization', 'Authorization says only that it is vague', swap('The run MUST NOT publish, push, tag or write externally. Authorized: `onboard.py setup` in step 4 only, after `onboard.py check` exits 0.', 'See the maintainer.'))
        expect('plan: authorization accepts a push that Authorization names with its condition',
               not check_plan(swap('Add the sweep and describe it in the internals reference.', 'Add the sweep, then run git push origin lane.').replace(
                   '`onboard.py setup` in step 4 only,', 'A plain push of the lane branch in step 3 only; `onboard.py setup` in step 4 only,'), root=root)[0])
        # stop-rules
        mutant('stop-rules', 'the replan cap clause deleted', swap(' replan cap: 1, then stop.', ''))
        mutant('stop-rules', 'the three-529s rule deleted', swap(', or three 529s in a row', ''))
        mutant('stop-rules', 'the state path deleted', swap('write state to .sdlc/notes.md at', 'write state at'))
        mutant('stop-rules', 'the rate or weekly limit deleted', swap(', a rate or weekly limit', ''))
        mutant('stop-rules', 'a replan cap of 2', swap('replan cap: 1,', 'replan cap: 2,'))
        # goal-line
        mutant('goal-line', 'Goal line pointing at another file', swap(
            '/goal complete build and verify .sdlc/demo/plan-doc.md by the run-plan skill: done when `python3 plugins/sdlc-lite/scripts/plan_done.py .sdlc/demo/plan-doc.md`',
            '/goal complete build and verify .sdlc/other/plan-doc.md by the run-plan skill: done when `python3 plugins/sdlc-lite/scripts/plan_done.py .sdlc/other/plan-doc.md`'))
        mutant('goal-line', 'Goal line deleted', re.sub(r'(?ms)^Goal line:\n```.*?```\n', '', P))
        mutant('goal-line', 'Goal line without the stop clause', swap(', or exits 4 after `plan_done.py stop` wrote the state. Do not end', '. Do not end'))
        mutant('goal-line', 'Goal line that does not start with /goal', swap('\n/goal complete build', '\ncomplete build'))
        expect('plan: goal-line accepts the same file named by a different relative form', not check_plan(P, root=root, path='/work/repo/.sdlc/demo/plan-doc.md')[0])
        # done-plan-done
        mutant('done-plan-done', 'Done when reduced to "all tickets closed"', swap(
            'Plan: `python3 plugins/sdlc-lite/scripts/plan_done.py .sdlc/demo/plan-doc.md` exits 0 and prints `plan done`, or exits 4 after `plan_done.py stop` wrote state to .sdlc/notes.md.',
            'Plan: all step tickets are closed.'))
        mutant('done-plan-done', 'Done when without the exit 4 clause', swap(', or exits 4 after `plan_done.py stop` wrote state to .sdlc/notes.md.', '.'))
        # the step blocks the parser extracts are accepted by steps.py lint
        p = pathlib.Path(d) / 'plan-doc.md'
        p.write_text(P, encoding='utf-8')
        r = subprocess.run([sys.executable, str(HERE / 'steps.py'), 'lint', str(p)], capture_output=True, text=True)
        expect('plan: steps.py lint accepts the step blocks of GOOD_PLAN', r.returncode == 0 and 'steps lint: ok' in r.stdout)
        if r.returncode:
            print(r.stdout, r.stderr)
        r = subprocess.run([sys.executable, str(HERE / 'plan_check.py'), 'plan', '--file', str(p), '--root', root], capture_output=True, text=True)
        expect('plan: the plan kind on a file other than its Goal line names exits 1 with goal-line', r.returncode == 1 and 'FAIL goal-line' in r.stdout)
        p2 = pathlib.Path(d) / 'sub' / 'plan-doc.md'
        p2.parent.mkdir()
        p2.write_text(P.replace('.sdlc/demo/plan-doc.md', 'sub/plan-doc.md'), encoding='utf-8')
        r = subprocess.run([sys.executable, str(HERE / 'plan_check.py'), 'plan', '--file', str(p2), '--root', root, '--run'], capture_output=True, text=True, cwd=d)
        expect('plan: plan --file --run on a good plan exits 0 and prints ok', False if r.returncode else 'ok: plan doc passes' in r.stdout)
        r = subprocess.run([sys.executable, str(HERE / 'plan_check.py'), 'plan', '--text', 'x'], capture_output=True, text=True)
        expect('plan: plan --text x exits 1 with FAIL lines', r.returncode == 1 and 'FAIL plan-front' in r.stdout)


GOOD_CLARIFY = """## Goal
A ticket whose diff touches only docs or records closes on its own checks, with no verifier run.

## Intent
Literal ask: skip the verifier when a ticket only changes docs, maybe records too; it MUST stay safe.
Level: L2 (lane: solo; cost: low, one script and one close rule; reversible: yes)
Deltas:
- missing-acceptance: the ask names no done-condition -> defaulted: a selftest case per path class, observed failing first [U] (source: root AGENTS.md)
- ambiguity: which paths count as docs -> gap (gap: whether `.sdlc/` records count as docs; default: they count)
- conflict: the repo runs one independent verifier per ticket -> answered: a narrow exception that a script decides
Do:
1. Add `scripts/verify_scope.py <base>` that prints `docs-only` for a docs-only diff.
2. Change `tickets.py close` to accept a docs-only diff with no verifier run.
Non-goals:
- skipping the verifier for any code, skill, agent or hook change
- model or effort changes
Done when:
- `python3 plugins/sdlc-lite/scripts/verify_scope.py selftest` exits 0
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 against `$SDLC_BASE_SHA`
- When a diff holds only docs paths, the close rule MUST accept the ticket with no verifier run
- unverifiable: the close message reads well to a maintainer

## Constraints
A code, skill, agent or hook change MUST NOT skip the verifier.
"""
CLARIFY_FIXTURE_GLOSSARY = """| Term | Part of speech | Definition | Unapproved aliases |
|---|---|---|---|
| lane | noun | The route a ticket runs through. | track, mode |
| step | noun | One ordered unit of a plan. | phase |
"""


def clarify_selftest(expect):
    """One observed-failing mutant per clarify rule, each flagged as exactly its rule; no rule flags GOOD_CLARIFY."""
    C = GOOD_CLARIFY
    RULES = ('clarify-goal', 'clarify-non-goals', 'clarify-level', 'clarify-done', 'clarify-done-defect', 'clarify-pass-through',
             'clarify-hedge', 'clarify-delta', 'clarify-do-verb', 'clarify-rfc2119', 'clarify-default-source')

    def rules(text):
        return sorted({r for r, _ in check_clarify(text, CLARIFY_FIXTURE_GLOSSARY)[0]})

    def warned(text):
        return sorted({r for r, _ in check_clarify(text, CLARIFY_FIXTURE_GLOSSARY)[1]})

    def swap(old, new):
        assert old in C, old
        return C.replace(old, new, 1)

    def mutant(rule, why, text):
        got = rules(text)
        expect(f'clarify: {rule} mutant "{why}" is flagged as exactly {rule}', got == [rule])
        if got != [rule]:
            print('  got', got)

    def warn_mutant(rule, why, text):
        got, bad = warned(text), rules(text)
        expect(f'clarify: {rule} mutant "{why}" warns exactly {rule} and fails nothing', got == [rule] and bad == [])
        if got != [rule] or bad:
            print('  got', got, bad)
    good = rules(C)
    for rule in RULES:
        expect(f'clarify: {rule} does not flag GOOD_CLARIFY', rule not in good)
    expect('clarify: clarify-goal-length GOOD_CLARIFY yields no warning', warned(C) == [])
    expect('clarify: clarify-pass-through a one-line already scoped: passes', rules('already scoped: add one link, done = `docs_check.py` exits 0\n') == [])
    expect('clarify: clarify-pass-through a one-line follow-up: passes', rules('\nfollow-up: "any updates" points at session state\n\n') == [])
    expect('clarify: clarify-pass-through a one-line stopped: passes', rules('stopped: merging a lane to main needs a ticket, and none exists\n') == [])
    mutant('clarify-pass-through', 'a stopped: line followed by a handoff', 'stopped: no ticket\n' + C)
    mutant('clarify-goal', 'Goal body emptied', re.sub(r'(?s)(## Goal\n).*?(\n## Intent)', r'\1\2', C))
    mutant('clarify-goal', 'Goal heading deleted', swap('## Goal\n', ''))
    mutant('clarify-non-goals', 'Non-goals line deleted', re.sub(r'(?m)^Non-goals:.*\n(?:- .*\n)*', '', C))
    mutant('clarify-non-goals', 'Non-goals emptied', re.sub(r'(?m)^Non-goals:.*\n(?:- .*\n)*', 'Non-goals:\n', C))
    expect('clarify: clarify-non-goals inline Non-goals text passes',
           rules(re.sub(r'(?m)^Non-goals:.*\n(?:- .*\n)*', 'Non-goals: model or effort changes.\n', C)) == [])
    mutant('clarify-level', 'Level line deleted', re.sub(r'(?m)^Level:.*\n', '', C))
    mutant('clarify-level', 'Level L5', swap('Level: L2', 'Level: L5'))
    mutant('clarify-done', 'Done when deleted', re.sub(r'(?ms)^Done when:.*', '', C))
    mutant('clarify-done', 'an item with no command', swap('- unverifiable: the close message reads well to a maintainer', '- the close message reads well'))
    mutant('clarify-done', 'an EARS item with a lower-case must', swap('the close rule MUST accept', 'the close rule must accept'))
    mutant('clarify-done-defect', 'an item reads its own verifier result',
           swap('- unverifiable:', '- `cat .sdlc/x/step-1/verifier-L2.md` says pass\n- unverifiable:'))
    expect('clarify: clarify-done-defect T-0613 an item citing a verifier result outside the repository is exempt',
           rules(swap('- unverifiable:', '- `test -s /nonexistent-other-repo/.sdlc/x/verifier-L1.md`\n- unverifiable:')) == [])
    mutant('clarify-done-defect', 'an item names a fixed sha', swap('against `$SDLC_BASE_SHA`', 'against `a9d42334`'))
    mutant('clarify-done-defect', 'an item needs a live rehearsal',
           swap('- unverifiable:', '- one more rehearsal plan runs to `plan done` with no hand step\n- unverifiable:'))
    mutant('clarify-pass-through', 'a pass-through line followed by a handoff', 'already scoped: x\n' + C)
    expect('clarify: clarify-done-defect an [owner: maintainer] live rehearsal item is exempt',
           rules(swap('- unverifiable:', '- [owner: maintainer] one more rehearsal plan runs to plan done with no hand step\n- unverifiable:')) == [])
    expect('clarify: clarify-done-defect the same rehearsal item without [owner: maintainer] is flagged',
           rules(swap('- unverifiable:', '- one more rehearsal plan runs to `plan done` with no hand step\n- unverifiable:')) == ['clarify-done-defect'])
    expect('clarify: clarify-done inline Done when text counts as one item',
           rules(re.sub(r'(?ms)^Done when:.*', 'Done when: `python3 x.py selftest` exits 0\n', C)) == [])
    expect('clarify: clarify-done a bulleted Done when with indented items passes',
           rules(re.sub(r'(?ms)^Done when:.*', '- Done when:\n  - `python3 x.py selftest` exits 0\n', C)) == [])
    expect('clarify: clarify-done-defect ordinary words and $SDLC_BASE_SHA are not a sha',
           rules(swap('- unverifiable:', '- `git diff --name-only $SDLC_BASE_SHA` lists a decade of facade changes\n- unverifiable:')) == [])
    mutant('clarify-hedge', 'a hedge word in the Goal', swap('closes on its own checks', 'probably closes on its own checks'))
    mutant('clarify-hedge', 'a hedge phrase in a Do step', swap('1. Add `scripts/verify_scope.py', '1. Add, if possible, `scripts/verify_scope.py'))
    expect('clarify: clarify-hedge a hedge word in Literal ask or a code span is not flagged',
           rules(swap('prints `docs-only`', 'prints `maybe-docs`')) == [] and 'maybe' in C.split('Literal ask:')[1].split('\n')[0])
    mutant('clarify-delta', 'a delta type outside the list', swap('- ambiguity: which paths', '- vagueness: which paths'))
    mutant('clarify-delta', 'a delta with no resolution', swap(' -> answered: a narrow exception that a script decides', ''))
    mutant('clarify-delta', 'the old free-form delta',
           swap('- conflict: the repo runs one independent verifier per ticket -> answered: a narrow exception that a script decides',
                '- conflict with a repo rule: defaulted: a narrow exception'))
    mutant('clarify-delta', 'a gap with no default', swap('; default: they count)', ')'))
    mutant('clarify-do-verb', 'a Do step whose first word is no listed verb', swap('2. Change `tickets.py close`', '2. Ensure `tickets.py close`'))
    mutant('clarify-do-verb', 'an inline Do with no numbered step',
           re.sub(r'(?m)^Do:\n(?:\d+\. .*\n)*', 'Do: add `scripts/verify_scope.py` and change the close rule.\n', C))
    mutant('clarify-do-verb', 'the Do line deleted', re.sub(r'(?m)^Do:\n(?:\d+\. .*\n)*', '', C))
    mutant('clarify-rfc2119', 'an upper-case MUST in the Goal', swap('closes on its own checks', 'MUST close on its own checks'))
    mutant('clarify-rfc2119', 'an upper-case SHOULD in a delta', swap('-> answered: a narrow exception', '-> answered: a narrow exception that SHOULD be'))
    mutant('clarify-rfc2119', 'a lower-case must not in Constraints', swap('change MUST NOT skip', 'change must not skip'))
    mutant('clarify-default-source', 'a defaulted delta without [U]', swap(' [U] (source:', ' (source:'))
    mutant('clarify-default-source', 'a defaulted delta without a source', swap(' (source: root AGENTS.md)', ''))
    warn_mutant('clarify-goal-length', 'a three-sentence Goal', swap('with no verifier run.', 'with no verifier run. It is fast. It is cheap.'))
    warn_mutant('clarify-goal-length', 'a Goal over 50 words', swap('with no verifier run.', 'with no verifier run' + ', and one more clause' * 10 + '.'))
    warn_mutant('clarify-glossary', 'an unapproved alias in the Goal', swap('closes on its own checks', 'closes on its own track'))
    warn_mutant('clarify-glossary', 'an unapproved alias in a Do step', swap('for a docs-only diff.', 'for a docs-only diff in any mode.'))
    expect('clarify: clarify-glossary an empty glossary yields no alias', clarify_glossary_aliases('') == [])
    expect('clarify: clarify-goal a passing block exits 0 through report()', report('clarify', *check_clarify(C, ''), out=lambda s: None) == 0)
    r = subprocess.run([sys.executable, str(HERE / 'plan_check.py'), 'clarify', '--text', 'x'], capture_output=True, text=True)
    expect('clarify: clarify-goal clarify --text x exits 1 with FAIL clarify-goal', r.returncode == 1 and 'FAIL clarify-goal' in r.stdout)
    skill = (HERE.parent / 'skills/clarify/SKILL.md').read_text(encoding='utf-8')
    for label, const, name in (('Do verbs', CLARIFY_VERBS, 'CLARIFY_VERBS'), ('Hedge words', CLARIFY_HEDGE, 'CLARIFY_HEDGE')):
        m = re.search(rf'(?m)^{label}: (.+)$', skill)
        got = {w.strip() for w in m.group(1).split(',')} if m else set()
        expect(f'clarify: skill {label} match {name}', got == set(const))
        if got != set(const):
            print('  diff', sorted(got ^ set(const)))
    evals = sorted((HERE.parent / 'skills/clarify/evals').glob('*.expected.md'))
    expect('clarify: eval the glob finds at least one expected file', len(evals) > 0)
    for f in evals:
        got = sorted({r for r, _ in check_clarify(f.read_text(encoding='utf-8'), '')[0]})
        expect(f'clarify: eval {f.name} passes', got == [])
        if got:
            print('  got', got)


GOOD_COMPACTION = """Continue T-0465; keep the sections below.
GOAL
Build the compaction kind of the plan skill | turn 2
RULES
No write to the entry files | "never touch the entry files" turn 4
DECISIONS
user 2026-10-12 invocation is a kind of the plan skill | maintainer fixed placement | turn 6
agent 2026-10-12 handoff write stays off by default | reload unverified | [U]
STATE
Branch `fanout/wave54-f`, 0 dirty files
POINT `.sdlc/.0465-compaction-prompt/handoff.md` -> goal, constraints, done-when
OPEN
Live check of the `CLAUDE.local.md` reload not run
NEXT
planned: verify step 1
DROP
DROP tool output, retry history, superseded plans, resolved errors
NEXT run /sdlc-lite:verify on step 1
"""
COMPACTION_FIXTURE_ENTRY = ['# Rules\n\n- Stop only processes owned by the task.\n1. Run commands from the repository root.\n']
COMPACTION_RULES = ('compaction-words', 'compaction-verb', 'compaction-order', 'compaction-lines', 'compaction-pin', 'compaction-em-dash',
                    'compaction-entry-copy', 'compaction-decision', 'compaction-approval')


def compaction_selftest(expect):
    """One observed-failing mutant per compaction rule, each flagged as exactly its rule; no rule flags GOOD_COMPACTION."""
    C = GOOD_COMPACTION

    def rules(text, entry=COMPACTION_FIXTURE_ENTRY):
        return sorted({r for r, _ in check_compaction(text, entry, CLARIFY_FIXTURE_GLOSSARY)[0]})

    def warned(text):
        return sorted({r for r, _ in check_compaction(text, COMPACTION_FIXTURE_ENTRY, CLARIFY_FIXTURE_GLOSSARY)[1]})

    def swap(old, new):
        assert old in C, old
        return C.replace(old, new, 1)

    def mutant(rule, what, text):
        got = rules(text)
        expect(f'compaction: {rule} flags {what}', got == [rule])
        if got != [rule]:
            print('  got', got)
    good = rules(C)
    expect('compaction: the good block passes', good == [] and warned(C) == [] and compaction_counts(C) == (18, 7))
    for rule in COMPACTION_RULES:
        expect(f'compaction: {rule} does not flag GOOD_COMPACTION', rule not in good)
    state, drop = 'Branch `fanout/wave54-f`, 0 dirty files', 'DROP tool output'
    mutant('compaction-words', 'a fact line of 24 words', swap(state, state + ' and' + ' one more word' * 6))
    expect('compaction: compaction-words does not count a pipe as a word',
           rules(swap('invocation is a kind of the plan skill', ' '.join(['w'] * 13))) == [])
    mutant('compaction-verb', 'a DROP section line with no leading verb', swap(drop, 'tool output'))
    mutant('compaction-verb', 'an upper-case first token outside the closed list', swap('Live check of', 'TODO run the check of'))
    expect('compaction: compaction-verb passes the two-letter fact PR 833 merged', rules(swap(state, state + '\nPR 833 merged')) == [])
    mutant('compaction-order', 'a missing header', swap('OPEN\n', ''))
    mutant('compaction-order', 'a repeated header', swap('STATE\n', 'STATE\nSTATE\n'))
    mutant('compaction-order', 'headers out of order', C.replace('GOAL\n', 'X\n', 1).replace('RULES\n', 'GOAL\n', 1).replace('X\n', 'RULES\n', 1))
    mutant('compaction-order', 'two lines before GOAL', swap('GOAL\n', 'One more line.\nGOAL\n'))
    mutant('compaction-order', 'no identity line before GOAL', C.split('\n', 1)[1])
    mutant('compaction-order', 'a last line that is not NEXT', swap('NEXT run /sdlc-lite:verify on step 1\n', ''))
    mutant('compaction-lines', 'a block of 63 lines', swap(drop, 'DROP x\n' * 45 + drop))
    expect('compaction: compaction-lines passes a block of 60 lines', rules(swap(drop, 'DROP x\n' * 42 + drop)) == [])
    lanes = [f'Lane `l{i:02d}` is open\n' for i in range(34)]
    mutant('compaction-pin', '41 PIN lines in a block of 52 lines', swap(state, ''.join(lanes) + state))
    expect('compaction: compaction-pin passes 40 PIN lines', rules(swap(state, ''.join(lanes[:33]) + state)) == [])
    expect('compaction: compaction-pin does not count POINT, DROP, none or header lines',
           compaction_counts(swap(state, state + '\nPOINT `a.md` -> the plan\nDROP the old plan\nnone')) == (21, 7))
    mutant('compaction-em-dash', 'the character U+2014', swap(', 0 dirty files', ' ' + COMPACTION_EM_DASH + ' 0 dirty files'))
    mutant('compaction-entry-copy', 'a KEEP line copied from an entry file', swap('DECISIONS\n', 'KEEP Stop only processes owned by the task.\nDECISIONS\n'))
    copied = swap('DECISIONS\n', 'Run commands from the repository root.\nDECISIONS\n')
    mutant('compaction-entry-copy', 'a fact line copied from a numbered entry line', copied)
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        try:
            os.chdir(d)
            none = sorted({r for r, _ in check_compaction(copied, None, '')[0]})
            pathlib.Path('AGENTS.md').write_text(COMPACTION_FIXTURE_ENTRY[0], encoding='utf-8')
            one = sorted({r for r, _ in check_compaction(copied, None, '')[0]})
        finally:
            os.chdir(cwd)
    expect('compaction: compaction-entry-copy skips a missing entry file and reads the one present',
           none == [] and one == ['compaction-entry-copy'])
    mutant('compaction-decision', 'a decision with no who', swap('user 2026-10-12', 'maintainer 2026-10-12'))
    mutant('compaction-decision', 'a decision with no date', swap('agent 2026-10-12 ', 'agent '))
    mutant('compaction-decision', 'a reason of 6 words', swap('reload unverified', 'the reload is not verified yet'))
    mutant('compaction-decision', 'a decision with an empty pointer', swap(' | [U]', ' |'))
    mutant('compaction-decision', 'a decision of two fields', swap(' | maintainer fixed placement', ''))
    opened = 'Live check of the `CLAUDE.local.md` reload not run'
    mutant('compaction-approval', 'an approval with no quote and no [U]', swap(opened, 'The user approved the merge'))
    expect('compaction: compaction-approval passes a quoted approval and one marked [U]',
           rules(swap(opened, 'Merge of the lane | "approved" turn 9\nPush is authorised [U]')) == [])
    got, bad = warned(swap('0 dirty files', '0 dirty files on this track')), rules(swap('0 dirty files', '0 dirty files on this track'))
    expect('compaction: compaction-glossary warns on an unapproved alias and fails nothing', got == ['compaction-glossary'] and bad == [])
    expect('compaction: compaction-glossary skips an alias inside a code span', warned(swap('0 dirty files', '0 dirty files in `track`')) == [])
    r = subprocess.run([sys.executable, str(HERE / 'plan_check.py'), 'compaction', '--text', 'DROP x'], capture_output=True, text=True)
    expect('compaction: compaction-order compaction --text "DROP x" exits 1 after the lines and pin counts',
           r.returncode == 1 and r.stdout.startswith('lines: 1 of 60\npin: 0 of 40\nFAIL compaction-order: '))
    reply = '```\n' + C + '```\nlines: 18 of 60\npin: 7 of 40\nRun: /compact <paste>\n'

    def returned(text):
        return sorted({r for r, _ in check_compaction_return(text)})
    expect('compaction: compaction-return passes the fenced block, lines, pin and Run lines', returned(reply) == [])
    expect('compaction: compaction-return passes one stale line before the fence', returned('stale: written 2026-10-01\n' + reply) == [])
    for what, text in (('a sentence before the fence', 'Here is the prompt.\n' + reply), ('a next-action line after Run', reply + 'Next, paste it.\n'),
                       ('the lines and pin lines merged', reply.replace('lines: 18 of 60\npin: 7 of 40', 'lines: 18 of 60, pin: 7 of 40')),
                       ('a lines count that differs from the block', reply.replace('lines: 18', 'lines: 17')),
                       ('a missing Run line', reply.replace('Run: /compact <paste>\n', '')), ('an unclosed fence', reply.replace('```\nlines', 'lines'))):
        expect(f'compaction: compaction-return flags {what}', returned(text) == ['compaction-return'])
    r = subprocess.run([sys.executable, str(HERE / 'plan_check.py'), 'compaction', '--reply', '--text', 'Sure.\n' + reply], capture_output=True, text=True)
    expect('compaction: compaction-return --reply exits 1 on a sentence before the fence', r.returncode == 1 and r.stdout.startswith('FAIL compaction-return: '))
    ref_txt = (HERE.parent / 'skills/plan/references/compaction.md').read_text(encoding='utf-8') if (HERE.parent / 'skills/plan/references/compaction.md').is_file() else ''
    ex = re.search(r'## Example block[^\n]*\n\n(```\n.*?\n```)', ref_txt, re.S)
    expect('compaction: the example of references/compaction.md returns in the shape of section 6',
           bool(ex) and returned(ex.group(1) + '\nlines: %d of 60\npin: %d of 40\nRun: /compact <paste>\n' % compaction_counts(ex.group(1))) == [])
    ref = HERE.parent / 'skills/plan/references/compaction.md'
    f, _ = check_compaction(ref.read_text(encoding='utf-8'), [], '') if ref.is_file() else ([('missing', '')], [])
    expect('compaction: the example block of references/compaction.md passes', f == [] and ref.is_file()
           and compaction_counts(ref.read_text(encoding='utf-8'))[0] > 10)
    if f:
        print('  got', f)


def selftest():
    bad, n = [], [0]

    def expect(label, cond):
        n[0] += 1
        if label.startswith(('plan: ', 'clarify: ', 'compaction: ')):
            print(('ok: ' if cond else 'FAIL: ') + label)
        if not cond:
            bad.append(label)
    f, _ = check_goal(GOOD_GOAL)
    expect('goal: the good block passes', not f)
    f, _ = check_goal(GOOD_GOAL.replace('.sdlc/notes.md', '.sdlc/notes/notes.md'))
    expect('goal: the topics-layout notes path passes', not f)
    f, _ = check_goal(GOOD_GOAL.replace('write state to .sdlc/notes.md', 'write state to .sdlc/notes/other.md'))
    expect('goal: a notes folder file that is not notes.md is flagged as stop-state', any(r == 'stop-state' for r, _ in f))
    muts_ob = {
        'a Outcome line deleted': re.sub(r'(?m)^Outcome:.*\n', '', GOOD_GOAL),
        'b Why deleted': GOOD_GOAL.replace(' Why: spend and load cannot be sized from unmetered runs.', ''),
        'c measure replaced by "it works"': GOOD_GOAL.replace('K-001 (`python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d`)', 'it works'),
        'd before deleted': GOOD_GOAL.replace(' before: 8.3,', ''),
        'e Rubric cut to 2': GOOD_GOAL.replace('3. Scope held | pass: only T-0001 and T-0002 are closed by this goal.\n', ''),
        'f one pass deleted': GOOD_GOAL.replace(' | pass: check.sh exits 0 on main.', ''),
        'g Negative control deleted': re.sub(r'(?m)^Negative control:.*\n', '', GOOD_GOAL),
        'h target deleted': GOOD_GOAL.replace(', target: <= 5', ''),
        'i Rubric cut to 6': GOOD_GOAL.replace('3. Scope held', '3. Scope held | pass: x.\n4. a | pass: x.\n5. b | pass: x.\n6. c | pass: x.\n7. Scope held', 1),
        'j whole block deleted': re.sub(r'(?ms)^Outcome:.*?^Negative control:[^\n]*\n\n', '', GOOD_GOAL),
    }
    for why, text in muts_ob.items():
        f, _ = check_goal(text)
        expect(f'goal: mutant "{why}" is flagged as outcome-block', any(r == 'outcome-block' for r, _ in f))
    expect('goal: the Outcome, Measured by, Rubric and Negative control block deleted names outcome-block', any(r == 'outcome-block' for r, _ in check_goal(muts_ob['j whole block deleted'])[0]))
    tickets_only = re.sub(r'(?m)^Done when:.*$', 'Done when: T-0001 and T-0002 are closed on main, or the goal stopped on a limit with state written to .sdlc/notes.md', GOOD_GOAL)
    f, _ = check_goal(tickets_only)
    expect('goal: a Done when that only closes tickets is flagged as done-measured', [r for r, _ in f] == ['done-measured'])
    f, _ = check_goal(GOOD_GOAL.replace('Done when: K-001 reads <= 5 (the Measured by command)', 'Done when: K-002 reads below its limit'))
    expect('goal: a Done when naming a different K id is flagged as done-measured', [r for r, _ in f] == ['done-measured'])
    f, _ = check_goal(GOOD_GOAL.replace('Done when: K-001 reads <= 5 (the Measured by command)', 'Done when: `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 7d` reads 5 or below'))
    expect('goal: a Done when naming the Measured by command passes', not f)
    f, w = check_goal(GOOD_GOAL.replace('before: 8.3', 'before: unmeasured: the collector has not run here'))
    expect('goal: an unmeasured before value passes with a before-unmeasured warning', not f and [r for r, _ in w] == ['before-unmeasured'])
    nm = re.sub(r'(?m)^Measured by:.*$', 'Measured by: none: no metric exists yet', GOOD_GOAL)
    f, w = check_goal(nm)
    expect('goal: Measured by none passes with a no-measure warning', not f and [r for r, _ in w] == ['no-measure'])
    f, w = check_goal(GOOD_GOAL)
    expect('goal: the good block has no warnings', not w)
    with tempfile.TemporaryDirectory() as d:
        (pathlib.Path(d) / 'docs' / 'kpi').mkdir(parents=True)
        (pathlib.Path(d) / '.sdlc').mkdir()
        f, w = check_goal(GOOD_GOAL, root=os.path.join(d, '.sdlc'))
        expect('goal: a K id with no docs/kpi file warns kpi-unresolved and does not fail', not f and [r for r, _ in w] == ['kpi-unresolved'])
        (pathlib.Path(d) / 'docs' / 'kpi' / '001-x.md').write_text('---\nid: K-001\n---\n')
        f, w = check_goal(GOOD_GOAL, root=os.path.join(d, '.sdlc'))
        expect('goal: a K id with its docs/kpi file does not warn', not f and not w)
    muts = {
        'starts-with-goal': GOOD_GOAL.replace('/goal Overnight', 'Overnight'),
        'section-scope': GOOD_GOAL.replace('Scope (', 'Items ('),
        'scope-list': GOOD_GOAL.replace('1. T-0001', 'T-0001').replace('2. T-0002', 'T-0002'),
        'how-to-work': GOOD_GOAL.replace('steps.py lane', 'a lane'),
        'stop-money': GOOD_GOAL.replace('$60 total, $15 per ticket, ', ''),
        'stop-529': GOOD_GOAL.replace('three 529s in a row', 'errors'),
        'stop-state': GOOD_GOAL.replace('write state to .sdlc/notes.md', 'write state'),
        'verifier-fail': GOOD_GOAL.replace('Fix every verifier fail and re-verify; never merge on a fail.', ''),
        'authorization': GOOD_GOAL.replace('The run MUST NOT publish, push or tag. Authorized: a fast-forward push of the release commit only if the fact-check passes.', ''),
        'done-vague': GOOD_GOAL.replace('tickets.py check exits 0', 'it looks good'),
        'done-limit': GOOD_GOAL.replace(', or the goal stopped on a limit with state written to .sdlc/notes.md', ''),
        'too-long': GOOD_GOAL.replace('Scope', 'x' * 5200 + '\nScope', 1),
    }
    for rule, text in muts.items():
        f, _ = check_goal(text)
        expect(f'goal: mutant for {rule} is flagged as {rule}', any(r == rule for r, _ in f))
    expect('goal: a vague done-when names done-vague', any(r == 'done-vague' for r, _ in check_goal(muts['done-vague'])[0]))
    expect('goal: a missing /goal names starts-with-goal', any(r == 'starts-with-goal' for r, _ in check_goal(muts['starts-with-goal'])[0]))
    f, w = check_loop(GOOD_LOOP)
    expect('loop: the good line passes', not f and not w)
    expect('loop: trailing `every 20m` parses', parse_loop('/loop check the deploy every 20m')[0] == 1200)
    expect('loop: leading 1h parses', parse_loop('/loop 1h x')[0] == 3600)
    for bad_tok in ('20mins:', '20 minutes:', '20min'):
        f, _ = check_loop(f'/loop {bad_tok} a status update; stop when done')
        expect(f'loop: "{bad_tok}" is flagged as interval-token', any(r == 'interval-token' for r, _ in f))
    expect('loop: an empty prompt is flagged', any(r == 'prompt-empty' for r, _ in check_loop('/loop 5m')[0]))
    expect('loop: no stop condition is flagged', any(r == 'stop-condition' for r, _ in check_loop('/loop 20m do the thing')[0]))
    expect('loop: dynamic mode needs no interval', not check_loop('/loop check the deploy and report')[0])
    expect('loop: 7m warns uneven', any(r == 'uneven' for r, _ in check_loop('/loop 7m x; stop when done; since the last run')[1]))
    expect('loop: 30s warns seconds', any(r == 'seconds' for r, _ in check_loop('/loop 30s x; stop when done')[1]))
    expect('loop: a block without /loop is flagged', any(r == 'starts-with-loop' for r, _ in check_loop('20m x')[0]))
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, '.sdlc')
        for tid, status, body in (('T-0001', 'ready', 'edits plugins/sdlc-lite/scripts/a.py'),
                                  ('T-0002', 'ready', 'edits plugins/sdlc-lite/scripts/b.py and check.py'),
                                  ('T-0003', 'ready', 'edits plugins/sdlc-lite/scripts/a.py and check.py'),
                                  ('T-0004', 'done', 'old'),
                                  ('T-0005', 'ready', 'edits plugins/sdlc-lite/scripts/c.py'),
                                  ('T-0006', 'ready', 'edits plugins/sdlc-lite/scripts/d.py'),
                                  ('T-0007', 'ready', 'edits plugins/sdlc-lite/scripts/e.py')):
            os.makedirs(os.path.join(root, tid.lower()))
            pathlib.Path(root, tid.lower(), 'handoff.md').write_text(
                f'---\nid: {tid}\nstatus: {status}\nsize: S\nbudget_usd: 5\n---\n\n## Goal\n{body}\n')
        base = 'python3 plugins/sdlc-lite/scripts/fanout.py run'
        good = f'{base} --dry-run a=T-0001 b=T-0002\n{base} a=T-0001 b=T-0002'
        f, w = check_fanout(good, root)
        expect('fanout: the good block passes', not f)
        cases = {
            'unknown flag': (good.replace('a=T-0001 b=T-0002', 'a=T-0001 b=T-0002 --nope'), 'flag'),
            'unknown ticket': (good.replace('T-0002', 'T-0999'), 'unknown-ticket'),
            'closed ticket': (good.replace('T-0002', 'T-0004'), 'closed-ticket'),
            'duplicate ticket': (good.replace('b=T-0002', 'b=T-0001'), 'duplicate-ticket'),
            'overlap across lanes': (good.replace('b=T-0002', 'b=T-0003'), 'overlap'),
            'lane cap': (good.replace('a=T-0001 b=T-0002', 'a=T-0001 b=T-0002 c=T-0005 d=T-0006 e=T-0007'), 'lane-cap'),
            'no dry run': (f'{base} a=T-0001 b=T-0002', 'dry-run-first'),
            'real before dry': (f'{base} a=T-0001 b=T-0002\n{base} --dry-run a=T-0001 b=T-0002', 'dry-run-first'),
            'real differs': (f'{base} --dry-run a=T-0001 b=T-0002\n{base} a=T-0001', 'dry-run-same'),
            'bad lane spec': (good.replace('a=T-0001', 'a=foo'), 'lane-spec'),
            'many lanes': (good.replace('--dry-run', '--dry-run --max-lanes 17', 1), 'yes-many'),
            'bad backend': (good.replace('python3', 'SDLC_BACKEND=gemini python3', 1), 'backend'),
        }
        for label, (text, rule) in cases.items():
            f, _ = check_fanout(text, root)
            expect(f'fanout: mutant "{label}" is flagged as {rule}', any(r == rule for r, _ in f))
        f, _ = check_fanout(good.replace('b=T-0002', 'a=T-0001,T-0003').replace('a=T-0001 ', ''), root)
        expect('fanout: overlapping tickets in ONE lane pass', not any(r == 'overlap' for r, _ in f))
        f, _ = check_fanout(good.replace('b=T-0002', 'b=T-0003').replace('--dry-run', '--dry-run --allow-overlap', 1)
                            .replace('\n' + base + ' a=', '\n' + base + ' --allow-overlap a='), root)
        expect('fanout: --allow-overlap lifts the overlap finding', not any(r == 'overlap' for r, _ in f))
        hot = good.replace('a=T-0001', 'a=T-0002').replace('b=T-0002', 'b=T-0003')
        f, w = check_fanout(hot, root)
        expect('fanout: two tickets sharing only check.py warn as hot-spot, not fail', not any(r == 'overlap' for r, _ in f) and any(r == 'hot-spot' for r, _ in w))
        f, _ = check_fanout(good.replace('a=T-0001', 'a=T-0001,T-0005 c=T-0006'), root)
        expect('fanout: three lanes within the cap pass', not f)
    f, w = check_campaign(GOOD_CAMPAIGN, load=(0.5, 8))
    expect('campaign: the gen-ui-kit page-CSS plan passes with no warning', not f and not w)
    expect('campaign: its /goal block passes plan_check goal', not check_goal(goal_block(GOOD_CAMPAIGN)[1])[0])
    cmuts = {
        'no-wave0-gate': (re.sub(r'(?m)^Wave 0 .*\n', 'Wave 0 (one lane): a derivation tool.\n', GOOD_CAMPAIGN), 'no-wave0-gate'),
        'done-not-command': (GOOD_CAMPAIGN.replace('Done when: `python3 scripts/check-page-css.py` exits 0 on main with an empty allowlist', 'Done when: every page is migrated'), 'done-not-command'),
        'overlap': (GOOD_CAMPAIGN.replace('site/pages/a01 ', 'site/pages/a00/inner '), 'overlap'),
        'lane-cap': (GOOD_CAMPAIGN.replace('Cap reason: 50 file-disjoint directories and the owner authorized --yes-many; uptime checked first.\n', ''), 'lane-cap'),
        'no-dollar-stop': (GOOD_CAMPAIGN.replace('at $900 total (a backstop: level L2 $30 times 30 lanes), $30 per lane, ', 'at ', 1), 'no-dollar-stop'),
        'pr-unbounded': (GOOD_CAMPAIGN.replace('8 to 10 PRs', 'as many PRs as needed'), 'pr-unbounded'),
        'no-order': (GOOD_CAMPAIGN.replace('Dependency order: Wave 0 lands on main before any Wave 1 lane starts; ', 'Dependency order: '), 'no-order'),
        'no-census': (GOOD_CAMPAIGN.replace('Census: `python3 scripts/census-page-css.py` exits 0', 'Census: a count of pages'), 'no-census'),
        'goal-block-fails-goal': (GOOD_CAMPAIGN.replace('three 529s in a row. No retry', 'errors. No retry'), 'goal-stop-529'),
        'no-goal-block': (GOOD_CAMPAIGN.split('```')[0], 'no-goal-block'),
    }
    for label, (text, rule) in cmuts.items():
        f, _ = check_campaign(text, load=(0.5, 8))
        expect(f'campaign: mutant "{label}" is flagged as {rule}', any(r == rule for r, _ in f))
    f, _ = check_campaign(GOOD_CAMPAIGN.replace('Lane cap: 16', 'Lane cap: 50').replace('Cap reason: 50 file-disjoint directories and the owner authorized --yes-many; uptime checked first.\n', ''), load=(0.5, 8))
    expect('campaign: lanes equal to the cap need no reason', not f)
    f, w = check_campaign(GOOD_CAMPAIGN.replace('Reference PR: #412 (the pattern every lane copies)\n', ''), load=(0.5, 8))
    expect('campaign: a missing reference PR warns and does not fail', not f and any(r == 'no-reference-pr' for r, _ in w))
    f, w = check_campaign(GOOD_CAMPAIGN, load=(7.0, 8))
    expect('campaign: a loaded machine warns and does not fail', not f and any(r == 'machine-load' for r, _ in w))
    with tempfile.TemporaryDirectory() as d:
        f, w = check_campaign(GOOD_CAMPAIGN, root=os.path.join(d, 'tickets'), load=(0.5, 8))
        expect('campaign: a ticket root with 0 tickets warns and does not fail', not f and any(r == 'ticket-root' for r, _ in w))
    f, w = check_campaign(GOOD_CAMPAIGN, root='x/.sdlc', load=(0.5, 8))
    expect('campaign: a root named .sdlc never warns about the ticket root', not any(r == 'ticket-root' for r, _ in w))
    # controlled language (T-0469): each rule has a mutant that must warn as exactly that rule, and the good blocks must not
    def lang(rule, label, w):
        expect(f'language: {label} warns {rule}', rule in [r for r, _ in w])
    lang('hedge', 'goal: a hedged /goal line', check_goal(GOOD_GOAL.replace('/goal Overnight: ship', '/goal Overnight: probably ship'))[1])
    lang('hedge', 'goal: a hedged Outcome line', check_goal(GOOD_GOAL.replace('Outcome: every run leaves', 'Outcome: ideally every run leaves'))[1])
    lang('verb', 'goal: a How to work line that opens with a noun', check_goal(GOOD_GOAL.replace('How to work: run steps.py lane', 'How to work: lane first with steps.py lane'))[1])
    lang('verb', 'goal: a second How to work line that opens with a noun', check_goal(GOOD_GOAL.replace('Fix every verifier fail', 'A verifier fail means: fix every one'))[1])
    lang('rfc2119', 'goal: an Authorization with no MUST', check_goal(GOOD_GOAL.replace('The run MUST NOT publish, push or tag.', 'Publish, push and tag are not implied.'))[1])
    lang('rfc2119', 'goal: a lower-case must in Authorization', check_goal(GOOD_GOAL.replace('The run MUST NOT publish', 'The run MUST NOT publish and must not tag; MUST NOT publish'))[1])
    lang('hedge', 'campaign: a hedged Campaign line', check_campaign(GOOD_CAMPAIGN.replace('Campaign: granular', 'Campaign: ideally granular'), load=(0.5, 8))[1])
    lang('verb', 'campaign: a goal block How to work that opens with a noun', check_campaign(GOOD_CAMPAIGN.replace('How to work: run steps.py lane first', 'How to work: lane first'), load=(0.5, 8))[1])
    lang('rfc2119', 'campaign: a goal block Authorization with no MUST', check_campaign(GOOD_CAMPAIGN.replace('The run MUST NOT publish, tag or deploy.', 'Publish, tag and deploy are not implied.'), load=(0.5, 8))[1])
    lang('hedge', 'plan: a hedged Goal', check_plan(GOOD_PLAN.replace('Build the restart', 'Probably build the restart'))[1])
    lang('hedge', 'plan: a hedged Outcome line', check_plan(GOOD_PLAN.replace('Outcome: a host restart', 'Outcome: arguably a host restart'))[1])
    lang('verb', 'plan: a step Do that opens with a noun', check_plan(GOOD_PLAN.replace('### Do\nChange the dispatch', '### Do\nThe dispatch'))[1])
    lang('verb', 'plan: a bulleted step Do item that opens with a noun', check_plan(GOOD_PLAN.replace('### Do\nChange the dispatch', '### Do\n- Add a test\n- Dispatch record names the lane worktree'))[1])
    lang('rfc2119', 'plan: an Authorization with no MUST', check_plan(GOOD_PLAN.replace('The run MUST NOT publish, push, tag or write externally. ', 'Publish, push, tag and external writes are not implied. '))[1])
    lang('rfc2119', 'plan: a lower-case should in Authorization', check_plan(GOOD_PLAN.replace('Authorized: `onboard', 'The run should stop. Authorized: `onboard'))[1])
    expect('language: the Do verb rule ignores fenced lines', not [r for r, _ in check_plan(GOOD_PLAN.replace('### Do\nChange the dispatch record to name the lane worktree.', '### Do\nChange the dispatch record to name the lane worktree.\n```\nthe dispatch\n```'))[1] if r == 'verb'])
    expect('language: a hedge word in a code span is not flagged', not [r for r, _ in check_goal(GOOD_GOAL.replace('Outcome: every run', 'Outcome: `maybe` every run'))[1] if r == 'hedge'])
    expect('language: the good goal, campaign and plan carry no language warning',
           not [r for r, _ in check_goal(GOOD_GOAL)[1] + check_campaign(GOOD_CAMPAIGN, load=(0.5, 8))[1] + check_plan(GOOD_PLAN)[1] if r in ('hedge', 'verb', 'rfc2119')])
    f, w = check_goal(GOOD_GOAL.replace('Fix every verifier fail', 'A verifier fail means: fix every one'))
    expect('language: a language finding warns and does not fail', not f and any(r == 'verb' for r, _ in w))
    # the cost line (T-0469): a sized ticket, an unsized one, a ticket over the cap, a missing cap, and a block with no ticket
    with tempfile.TemporaryDirectory() as d:
        for tid, size in (('T-0001', 'L2'), ('T-0002', 'L3'), ('T-0003', 'L4'), ('T-0004', None)):
            os.makedirs(os.path.join(d, f'{tid[2:]}-x'))
            front = f'id: {tid}\nstatus: ready\n' + (f'size: {size}\n' if size else '')
            pathlib.Path(d, f'{tid[2:]}-x', 'handoff.md').write_text(f'---\n{front}---\n## Goal\nx\n')
        cap = 'stop at $100 total'
        expect('cost: two sized tickets sum their caps', cost_line(f'T-0001 T-0002 {cap}', d) == 'cost: $90 of $100 (2 tickets: T-0001 L2 $30, T-0002 L3 $60)')
        expect('cost: a sum above the cap ends over', cost_line('T-0001 T-0002 stop at $60 total', d) == 'cost: $90 of $60 (2 tickets: T-0001 L2 $30, T-0002 L3 $60) over')
        expect('cost: a level with no TIERS row sums unknown, never 0', cost_line(f'T-0001 T-0003 {cap}', d) == 'cost: unknown of $100 (2 tickets: T-0001 L2 $30, T-0003 unknown)')
        expect('cost: a ticket with no size sums unknown, never 0', cost_line(f'T-0004 {cap}', d) == 'cost: unknown of $100 (1 ticket: T-0004 unknown)')
        expect('cost: a ticket with no folder sums unknown', cost_line(f'T-0099 {cap}', d) == 'cost: unknown of $100 (1 ticket: T-0099 unknown)')
        expect('cost: no total cap in the block reads unknown', cost_line('T-0001', d) == 'cost: $30 of unknown (1 ticket: T-0001 L2 $30)')
        expect('cost: a block with no ticket sums unknown, never 0', cost_line(f'no ids {cap}', d) == 'cost: unknown of $100 (0 tickets)')
        expect('cost: a repeated ticket id counts once', cost_line(f'T-0001 T-0001 {cap}', d).startswith('cost: $30 of $100 (1 ticket'))
        import io, contextlib
        for kind, block in (('goal', GOOD_GOAL.replace('T-0001', 'T-0001').replace('T-0002', 'T-0002')), ('plan', GOOD_PLAN)):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = main([kind, '--text', block, '--root', d, '--summary'])
            lines = buf.getvalue().splitlines()
            expect(f'cost: --summary on {kind} prints the lint lines then one cost line, exit {rc}', rc == 0 and lines[-1].startswith('cost: ') and lines[-2].startswith('ok: '))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(['goal', '--text', GOOD_GOAL, '--root', d])
        expect('cost: without --summary no cost line prints', 'cost:' not in buf.getvalue())
    plan_selftest(expect)
    clarify_selftest(expect)
    compaction_selftest(expect)
    rc = report('goal', *check_goal(GOOD_GOAL), out=lambda s: None)
    expect('report: a passing block exits 0', rc == 0)
    rc = report('goal', *check_goal('nope'), out=lambda s: None)
    expect('report: a failing block exits 1', rc == 1)
    for b in bad:
        print('FAIL', b)
    print(f'plan_check selftest: {"FAIL" if bad else "PASS"} ({n[0]} checks)')
    return 1 if bad else 0


def main(argv):
    if argv[:1] == ['selftest']:
        return selftest()
    ap = argparse.ArgumentParser(prog='plan_check.py', description=__doc__.split('\n')[0])
    ap.add_argument('kind', choices=('goal', 'loop', 'fanout', 'campaign', 'plan', 'clarify', 'compaction'))
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--text')
    g.add_argument('--file')
    ap.add_argument('--root', default='.sdlc')
    ap.add_argument('--run', action='store_true', help='plan only: add the checks that apply before execution starts')
    ap.add_argument('--reply', action='store_true', help='compaction only: check the return shape of the whole reply, not the block')
    ap.add_argument('--summary', action='store_true', help='after the lint lines, print the cost line: the caps of the tickets the block names against its total cap')
    a = ap.parse_args(argv)
    if a.run and a.kind != 'plan':
        ap.error('--run applies to the plan kind only')
    if a.reply and a.kind != 'compaction':
        ap.error('--reply applies to the compaction kind only')
    text = a.text if a.text is not None else (pathlib.Path(a.file).read_text(encoding='utf-8') if a.file else sys.stdin.read())
    if a.reply:
        return report('compaction return', check_compaction_return(text), [])
    if a.kind == 'compaction':
        n_lines, n_pin = compaction_counts(text)
        print(f'lines: {n_lines} of {COMPACTION_MAX_LINES}')
        print(f'pin: {n_pin} of {COMPACTION_MAX_PIN}')
    rc = report(a.kind, *run_check(a.kind, text, a.root, a.run, a.file))
    if a.summary:
        print(cost_line(text, a.root))
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
