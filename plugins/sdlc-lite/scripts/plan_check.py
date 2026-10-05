#!/usr/bin/env python3
"""Lint a planned /goal, /loop, or fanout block before it is handed to the user.

  plan_check.py goal|loop|fanout [--text T | --file F] [--root .sdlc]
  plan_check.py selftest

Reads the block from --text, --file, or stdin; a fenced block is unwrapped. Prints one `FAIL <rule>: <why>` line per
finding (exit 1), `warn <rule>: <why>` lines that never change the exit code, and `ok: <kind> plan passes` otherwise.
Deterministic: no model call, no network. Fanout flags are read from fanout.py's own parser text, so a flag fanout.py
does not have is a finding. /goal and /loop cannot run headlessly: their rules come from the skills'
references (the stop hook checks the goal each turn; /loop parses a leading interval token or a trailing `every N unit`).
"""
import argparse, glob, os, pathlib, re, shlex, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
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
    for key, pat in LABELS:
        m = re.search(rf'(?im)^\s*({pat})\b[^\n]*', text)
        if m:
            marks.append((m.start(), key))
    marks.sort()
    out = {}
    for i, (pos, key) in enumerate(marks):
        out[key] = text[pos:(marks[i + 1][0] if i + 1 < len(marks) else len(text))]
    return out


def check_goal(text):
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
        if '.sdlc/notes.md' not in s:
            fails.append(('stop-state', 'stop rules need where state is written (.sdlc/notes.md)'))
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
    if len(text) > 5000:
        fails.append(('too-long', f'{len(text)} characters; keep it under 5000 so it can be read overnight'))
    return fails, warns


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


# ---- driver --------------------------------------------------------------------------------------------------
def run_check(kind, text, root='.sdlc'):
    return {'goal': check_goal, 'loop': check_loop, 'fanout': lambda t: check_fanout(t, root)}[kind](text)


def report(kind, fails, warns, out=print):
    for r, w in fails:
        out(f'FAIL {r}: {w}')
    for r, w in warns:
        out(f'warn {r}: {w}')
    if not fails:
        out(f'ok: {kind} plan passes')
    return 1 if fails else 0


GOOD_GOAL = """```
/goal Overnight: ship the three listed tickets, then stop.

Scope (verify with tickets.py check first):
1. T-0001 first thing
2. T-0002 second thing

How to work: lane first with steps.py lane; solo for S and M; replan cap one, then record a limit; every claim from a command.
A verifier fail means fix and re-verify; never merge on a fail.

Budget and stop rules: stop and write state to .sdlc/notes.md at $60 total, $15 per ticket, a rate or weekly limit, or three 529s in a row.

Authorization: publish, push and tag are not implied. Authorized: a fast-forward push of the release commit only if the fact-check passes.

Done when: tickets.py check exits 0 and T-0001 and T-0002 are closed on main, or the goal stopped on a limit with state written to .sdlc/notes.md.
```"""
GOOD_LOOP = "/loop 20m a status update with progress since the last run; stop when .sdlc/notes.md says done"


def selftest():
    bad, n = [], [0]

    def expect(label, cond):
        n[0] += 1
        if not cond:
            bad.append(label)
    f, _ = check_goal(GOOD_GOAL)
    expect('goal: the good block passes', not f)
    muts = {
        'starts-with-goal': GOOD_GOAL.replace('/goal Overnight', 'Overnight'),
        'section-scope': GOOD_GOAL.replace('Scope (', 'Items ('),
        'scope-list': GOOD_GOAL.replace('1. T-0001', 'T-0001').replace('2. T-0002', 'T-0002'),
        'how-to-work': GOOD_GOAL.replace('steps.py lane', 'a lane'),
        'stop-money': GOOD_GOAL.replace('$60 total, $15 per ticket, ', ''),
        'stop-529': GOOD_GOAL.replace('three 529s in a row', 'errors'),
        'stop-state': GOOD_GOAL.replace('write state to .sdlc/notes.md', 'write state'),
        'verifier-fail': GOOD_GOAL.replace('A verifier fail means fix and re-verify; never merge on a fail.', ''),
        'authorization': GOOD_GOAL.replace('publish, push and tag are not implied. Authorized: a fast-forward push of the release commit only if the fact-check passes.', ''),
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
    ap.add_argument('kind', choices=('goal', 'loop', 'fanout'))
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--text')
    g.add_argument('--file')
    ap.add_argument('--root', default='.sdlc')
    a = ap.parse_args(argv)
    text = a.text if a.text is not None else (pathlib.Path(a.file).read_text(encoding='utf-8') if a.file else sys.stdin.read())
    return report(a.kind, *run_check(a.kind, text, a.root))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
