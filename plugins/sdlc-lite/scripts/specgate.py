#!/usr/bin/env python3
"""Spec gate: refuse a plan before plan review when a cheap static check already finds a defect.

Usage: specgate.py {check <planner.md | task dir> | selftest}
  check     pick the plan the way steps.py split does (a planner-*.md file, or the newest
            planner-*.md in a task dir by recorded run order) and read it with steps.py's own
            parser (find_plan, parse_steps, criteria_lines, line_spans, is_guard_line,
            plan_guard_timeout, step_guard_timeout). Read-only; never runs a span. Finding kinds:
              slow guard      a span on a (guard) criterion line runs check.sh (a command word
                              ending in check.sh, at the start of the span or after ; & | ( $( !
                              then do else, past VAR=x, bash, sh, env, or timeout N prefixes), and
                              neither that step block nor the plan outside every ## Step block holds
                              a "guard timeout: <seconds>" line (steps.py split --only reads it)
              duplicate span  a command span on a criterion line not tagged (guard) repeats verbatim
                              a criterion span of an earlier step; the detail names that step.
                              (guard) lines and steps titled "Merge ..." are exempt, and a repeat
                              inside one step is not flagged
              red and guard   a criterion line whose leading tag run, after "- " or "* ", holds both
                              (guard) and (red)
            Each finding prints on stderr as "specgate: <plan>: step <n>: <kind>: <detail>", then a
            last line "specgate: <k> finding(s); fix the plan before plan review", exit 1.
            A clean plan prints "specgate: ok: <plan>" on stdout, exit 0. A target that does not
            exist exits 1. A dir with no planner-*.md, or a plan steps.parse_steps refuses (no step
            blocks, a step with no level line), prints "specgate: skip: <reason>" on stderr, exit 0.
            run.sh runs check on the handoff dir before every plan-reviewer run (SDLC_SPECGATE=off
            skips it) and exits 2 when it refuses.
  selftest  prove each finding, each exemption, the skip, and two replays of real plans.
"""
import argparse, contextlib, io, pathlib, re, sys, tempfile

import steps

CHECK_SH_RE = re.compile(r'(?:^|[;&|(!]|\$\(|\b(?:then|do|else)\s)\s*(?:\w+=\S*\s+)*'
                         r'(?:(?:timeout\s+\S+|bash|sh|env)\s+)*["\']?\S*check\.sh["\']?(?=\s|$|[;&|)])')
TAG_RUN_RE = re.compile(r'^(?:\([\w-]+\)\s*)+')
GUARD_HINT = 'add "guard timeout: <seconds>" to ## Goal or to the step block'


def runs_check_sh(span):
    """True when a command word of the span ends in check.sh (it runs the script, not names it)."""
    return CHECK_SH_RE.search(span) is not None


def leading_tags(line):
    """The tags of a criterion line's leading tag run, after its list marker (- or *)."""
    text = line.lstrip()
    if text.startswith('- ') or text.startswith('* '):
        text = text[2:].lstrip()
    m = TAG_RUN_RE.match(text)
    return re.findall(r'\(([\w-]+)\)', m.group(0)) if m else []


class Skip(Exception):
    """No plan to check: the caller prints a skip line and exits 0."""


def findings(target):
    """(plan, [(n, kind, detail)]) for a planner file or task dir. Raises Skip when there is no
    plan to check, steps.Fail when the target does not exist."""
    if not pathlib.Path(target).exists():
        raise steps.Fail(f'specgate: no such file or directory: {target}')
    try:
        plan, _ = steps.find_plan(target)
        blocks = steps.parse_steps(plan)
    except steps.Fail as e:
        raise Skip(str(e)) from None
    plan_timeout = steps.plan_guard_timeout(plan)
    out, seen = [], {}
    for n, block in blocks.items():
        title = steps.STEP_RE.match(block.splitlines()[0]).group(2)
        merge = title.startswith('Merge ')
        timed = plan_timeout is not None or steps.step_guard_timeout(block) is not None
        mine = []
        for line in steps.criteria_lines(block):
            tags = leading_tags(line)
            if 'guard' in tags and 'red' in tags:
                out.append((n, 'red and guard', f'one criterion line is tagged both (guard) and (red): {line.strip()}'))
            guard = steps.is_guard_line(line)
            for span in steps.line_spans(line):
                mine.append(span)
                if guard:
                    if not timed and runs_check_sh(span):
                        out.append((n, 'slow guard', f'`{span}` runs check.sh with no guard timeout line; {GUARD_HINT}'))
                elif not merge and span in seen:
                    out.append((n, 'duplicate span', f'`{span}` repeats a criterion of step {seen[span]} verbatim'))
        for span in mine:
            seen.setdefault(span, n)
    return plan, out


def cmd_check(target):
    try:
        plan, found = findings(target)
    except Skip as e:
        print(f'specgate: skip: {e}', file=sys.stderr)
        return 0
    except steps.Fail as e:
        print(e, file=sys.stderr)
        return 1
    if not found:
        print(f'specgate: ok: {plan}')
        return 0
    for n, kind, detail in found:
        print(f'specgate: {plan}: step {n}: {kind}: {detail}', file=sys.stderr)
    print(f'specgate: {len(found)} finding(s); fix the plan before plan review', file=sys.stderr)
    return 1


# Replay fixtures: criterion lines copied verbatim from real plans that later needed a fix.
# T-0183 (.worktrees/t0183/.sdlc/0183-supervisor-script/planner-L3.md, untracked): step 3 repeats two
# step 2 criteria, and step 7 runs check.sh with no guard timeout line.
T0183_STEP2 = [
    '- `out=$(python3 plugins/sdlc-lite/scripts/supervisor.py selftest) && test "$(printf \'%s\\n\' "$out" | tail -n 1)" = "supervisor selftest: PASS"`',
    '- `out=$(python3 plugins/sdlc-lite/scripts/supervisor.py selftest) && for l in "init: entry files, limits, and git-ignore" "config: a bad limit or host entry is refused" "status: idle with no mail" "wake: one call on arrival, status waking" "dry-run: no call without --run" "debounce: a young message waits" "wake: the mailbox is byte-identical" "control: a claiming copy fails the byte-identity check" "prompt: no body and no topic" "control: a topic-leaking copy fails the prompt check" "argv: claude ephemeral and attached" "argv: codex ephemeral and attached" "env: scrubbed, SDLC_ROLE and SDLC_HEADLESS set" "notify: no call, one line" "lock: a second watcher exits 1, a restart succeeds" "lock: a linked worktree shares the lock" "control: a lockless copy lets two watchers run" "stop: STOP exits 0 with no call" "stop: removing STOP lets a wake happen" "control: a copy that ignores STOP wakes"; do printf \'%s\\n\' "$out" | grep -qxF "ok: $l" || exit 1; done`',
    '- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && grep -qxF "import messages" "$f" && grep -qF "messages.wait_ready(" "$f" && grep -qF "messages.mailbox(" "$f" && ! grep -qE "^def (parse|check|load|load_or_none|wait_ready|mailbox|message_ids)\\(" "$f"`',
    '- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && ! grep -qE "shell=True|os\\.system\\(|os\\.popen\\(" "$f" && ! grep -qF "$(printf \'\\342\\200\\224\')" "$f"`',
    '- `h=$(python3 plugins/sdlc-lite/scripts/supervisor.py --help) && printf \'%s\\n\' "$h" | grep -qF "{init,watch,status,reset,selftest}" && w=$(python3 plugins/sdlc-lite/scripts/supervisor.py watch --help) && for o in --run --once --now --driver; do printf \'%s\\n\' "$w" | grep -qF -- "$o" || exit 1; done`',
    '- `grep -qF \'python3 "$root/scripts/supervisor.py" selftest\' plugins/sdlc-lite/scripts/check.sh && grep -qF "messages.py, and supervisor.py selftests" plugins/sdlc-lite/scripts/check.sh`',
    '- `p="$(dirname "$(cd "$(git rev-parse --git-common-dir)" && pwd)")/.sdlc/supervisor"; b=$(ls -A "$p" 2>/dev/null); python3 plugins/sdlc-lite/scripts/supervisor.py selftest >/dev/null && test "$(ls -A "$p" 2>/dev/null)" = "$b" && test ! -e .sdlc/supervisor`',
    '- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/validation/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/supervisor.py)"`',
]
T0183_STEP3 = [
    '- `out=$(python3 plugins/sdlc-lite/scripts/supervisor.py selftest) && test "$(printf \'%s\\n\' "$out" | tail -n 1)" = "supervisor selftest: PASS" && for l in "cooldown: a second wake waits, status cooling" "control: a copy without the cooldown wakes twice" "cap: the hourly cap holds" "cap: the daily cap holds" "cap: limits set to 0 refuse every wake" "control: a copy without the caps wakes past them" "depth: a reply chain of three records needs a human" "depth: a chain of two still wakes" "depth: a wake-sent chain without re counts" "control: a copy without the depth rule wakes" "active: a running recorded wake skips the wake" "active: a recent transcript skips the wake" "active: a stale pid record is dropped" "control: a copy that ignores the active signal wakes" "failure: backoff, then failed after three" "failure: exit 0 without progress counts" "failure: a timed-out wake is killed and counts" "failure: a stranded read message is retried" "control: a copy that trusts the exit code fails" "control: a copy without the failure stop keeps waking" "reset: clears failed" "restart: counters survive a restart"; do printf \'%s\\n\' "$out" | grep -qxF "ok: $l" || exit 1; done`',
    '- `python3 plugins/sdlc-lite/scripts/supervisor.py reset --help | grep -qF -- "--receiver"`',
    '- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && ! grep -qE "shell=True|os\\.system\\(|os\\.popen\\(" "$f" && ! grep -qF "$(printf \'\\342\\200\\224\')" "$f"`',
    '- `p="$(dirname "$(cd "$(git rev-parse --git-common-dir)" && pwd)")/.sdlc/supervisor"; b=$(ls -A "$p" 2>/dev/null); python3 plugins/sdlc-lite/scripts/supervisor.py selftest >/dev/null && test "$(ls -A "$p" 2>/dev/null)" = "$b" && test ! -e .sdlc/supervisor`',
    '- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/ticket-stages/watcher-design.md -e docs/validation/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/supervisor.py)"`',
]
T0183_STEP7 = [
    '- (guard) `bash plugins/sdlc-lite/scripts/check.sh`',
]
# T-0195 (.sdlc/.0195-runner-family-task-dir/planner-L3-2.md): step 4 runs check.sh with no guard timeout line.
T0195_STEP4 = [
    '- (guard) `bash plugins/sdlc-lite/scripts/check.sh`',
]


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


HEADER = '<!-- role=planner level=L2 model=opus effort=medium -->\n'


def plan_text(goal_extra, *step_specs):
    """A planner result: ## Goal (plus goal_extra lines), then one step per (title, extra, criteria)."""
    parts = [HEADER, '## Goal\ng\n', *(f'{x}\n' for x in goal_extra), '\n']
    for i, (title, extra, criteria) in enumerate(step_specs, 1):
        parts.append(f'## Step {i}: {title}\nlevel: L1\n')
        parts += [f'{x}\n' for x in extra]
        parts.append('### Do\nd\n### Acceptance criteria\n')
        parts += [f'{c}\n' for c in criteria]
        parts.append('\n')
    parts.append('## Assumptions\nNone\n\n## Risks\nNone\n')
    return ''.join(parts)


def selftest():
    misses = []

    def check(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        count = [0]

        def write(text, name='planner-L2.md'):
            count[0] += 1
            d = tmp / f't{count[0]}'
            d.mkdir()
            (d / name).write_text(text, encoding='utf-8')
            return d / name

        def kinds(text):
            """(rc, stdout, stderr, [(step, kind)]) of check on a plan file."""
            p = write(text)
            rc, out, err = run_main(['check', str(p)])
            got = [(int(m.group(1)), m.group(2)) for m in
                   re.finditer(rf'^specgate: {re.escape(str(p))}: step (\d+): ([a-z ]+): ', err, re.M)]
            return rc, out, err, got, p

        def refused(rc, out, err, got):
            last = err.strip().splitlines()[-1] if err.strip() else ''
            return (rc == 1 and out == '' and last == f'specgate: {len(got)} finding(s); fix the plan before plan review'
                    and len(err.strip().splitlines()) == len(got) + 1)

        chk = '(guard) `bash plugins/sdlc-lite/scripts/check.sh`'
        rc, out, err, got, p = kinds(plan_text(['guard timeout: 900'], ('Gates', [], [chk])))
        rc2, out2, err2, got2, _ = kinds(plan_text([], ('A', [], ['- x']), ('Gates', [], ['- x'])))
        check('check: a plan with a guard timeout line passes',
              rc == 0 and out == f'specgate: ok: {p}\n' and err == '' and got == []
              and rc2 == 0 and err2 == '' and out2.startswith('specgate: ok: '))

        forms = ['bash plugins/sdlc-lite/scripts/check.sh', 'bash "$root/scripts/check.sh"',
                 'cd plugins/sdlc-lite && bash scripts/check.sh', 'cd . && timeout 900 bash scripts/check.sh',
                 'env bash scripts/check.sh',
                 'X=1 sh ./check.sh 2>&1 | tail -n 3', 'if true; then bash scripts/check.sh; fi',
                 'out=$(bash scripts/check.sh) && test -n "$out"', '! bash scripts/check.sh --no-such-flag']
        rc, out, err, got, _ = kinds(plan_text([], ('Gates', [], [f'- (guard) `{f}`' for f in forms])))
        rc2, out2, err2, got2, _ = kinds(plan_text(['guard timeout: 0'], ('Gates', [], [f'- {chk}'])))
        check('check: a check.sh guard with no guard timeout line is refused',
              refused(rc, out, err, got) and got == [(1, 'slow guard')] * len(forms)
              and 'step 1: slow guard: `bash plugins/sdlc-lite/scripts/check.sh` runs check.sh' in err
              and refused(rc2, out2, err2, got2) and got2 == [(1, 'slow guard')])

        rc, out, err, got, _ = kinds(plan_text([], ('A', ['guard timeout: 900'], [f'- {chk}']),
                                               ('B', [], [f'- {chk}'])))
        check('check: a step guard timeout line covers only its own step',
              refused(rc, out, err, got) and got == [(2, 'slow guard')])

        named = ['grep -qF x plugins/sdlc-lite/scripts/check.sh',
                 'test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | grep -vxF -e plugins/sdlc-lite/scripts/check.sh)"',
                 'shellcheck plugins/sdlc-lite/scripts/check.sh', 'python3 scripts/check-packaging.py',
                 'grep -c check.sh docs/x.md', 'bash scripts/check.sh.bak']
        rc, out, err, got, _ = kinds(plan_text([], ('Gates', [], [f'- (guard) `{s}`' for s in named]
                                                    + [f'- `bash plugins/sdlc-lite/scripts/check.sh`'])))
        check('check: a guard that only names check.sh is not flagged',
              rc == 0 and err == '' and got == [] and not any(runs_check_sh(s) for s in named))

        rep = '- `grep -qF needle plugins/x/y.md`'
        rc, out, err, got, _ = kinds(plan_text([], ('A', [], [rep, rep]), ('B', [], ['- `test -f a/b`']),
                                               ('C', [], ['- (red) `test -f c/d`', rep])))
        check('check: a criterion repeated across steps is refused',
              refused(rc, out, err, got) and got == [(3, 'duplicate span')]
              and 'step 3: duplicate span: `grep -qF needle plugins/x/y.md` repeats a criterion of step 1 verbatim' in err)

        scope = '- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . | grep -vxF -e a/b)"`'
        rc, out, err, got, _ = kinds(plan_text([], ('A', [], ['- `test -f a/b`', scope]),
                                               ('B', [], ['- `test -f a/c`', scope])))
        check('check: a guard repeated across steps is not flagged', rc == 0 and err == '' and got == [])

        tmpl = ['- `test "$(git rev-list --count HEAD^1..HEAD^2)" -ge 1`', '- `! git rev-parse -q --verify MERGE_HEAD`']
        rc, out, err, got, _ = kinds(plan_text([], ('A', [], ['- `test -f a/b`']), ('Merge lane-a', [], tmpl),
                                               ('Merge lane-b', [], tmpl)))
        check('check: a merge step template criterion is not flagged', rc == 0 and err == '' and got == [])

        rc, out, err, got, _ = kinds(plan_text([], ('A', [], ['- (red) (guard) `test -f a/b`', '* (guard)(red) `test -f a/c`',
                                                          '- (guard) (red-ish) `test -f a/d`',
                                                          '- (guard) `test -f a/e` is not (red)'])))
        check('check: (red) beside (guard) on one line is refused',
              refused(rc, out, err, got) and got == [(1, 'red and guard')] * 2)

        empty = tmp / 'empty'
        empty.mkdir()
        rc, out, err = run_main(['check', str(empty)])
        skips = [rc == 0 and out == '' and err.startswith('specgate: skip: ')]
        for text in (HEADER, '## Goal\nx\n', HEADER + '## Goal\nx\n\n## Step 1: A\n### Do\nx\n'):
            p = write(text, 'planner-L1.md')
            for t in (p, p.parent):
                rc, out, err = run_main(['check', str(t)])
                skips.append(rc == 0 and out == '' and err.startswith('specgate: skip: ')
                             and len(err.strip().splitlines()) == 1)
        rc, out, err = run_main(['check', str(tmp / 'missing')])
        check('check: no planner result or no step blocks skips with exit 0',
              all(skips) and len(skips) == 7 and rc == 1 and out == '' and 'skip' not in err)

        def lines_step(n, title, criteria):
            return [f'## Step {n}: {title}', 'level: L3', '### Do', 'x', '### Acceptance criteria', *criteria, '']

        t0183 = '\n'.join([HEADER.rstrip('\n'), '## Goal', 'g', '',
                           *lines_step(2, 'supervisor.py core', T0183_STEP2),
                           *lines_step(3, 'supervisor.py limits', T0183_STEP3),
                           *lines_step(7, 'Gates green', T0183_STEP7), '## Risks', 'None', ''])
        rc, out, err, got, _ = kinds(t0183)
        check('replay: T-0183 step 3 duplicate and step 7 timeout are flagged',
              refused(rc, out, err, got) and got == [(3, 'duplicate span'), (3, 'duplicate span'), (7, 'slow guard')]
              and err.count('repeats a criterion of step 2 verbatim') == 2)

        t0195 = '\n'.join([HEADER.rstrip('\n'), '## Goal', 'g', '', *lines_step(4, 'Gates green', T0195_STEP4),
                           '## Risks', 'None', ''])
        rc, out, err, got, _ = kinds(t0195)
        check('replay: T-0195 step 4 timeout is flagged', refused(rc, out, err, got) and got == [(4, 'slow guard')])

    if misses:
        print('specgate selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('specgate selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='specgate.py', description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('check', help='refuse a plan with a slow guard, a duplicate span, or (red) beside (guard)')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    sub.add_parser('selftest', help='prove every finding, exemption, and skip')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    return cmd_check(a.target)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
