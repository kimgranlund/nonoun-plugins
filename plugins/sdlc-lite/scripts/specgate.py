#!/usr/bin/env python3
"""Spec gate: refuse a plan before plan review when a cheap static check already finds a defect.

Usage: specgate.py {check <planner.md | task dir> | red <task dir | handoff.md> [--step N] [--timeout S] | selftest}
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
  red       red-first control for a (red) criterion: a span that checks the change must exit nonzero
            BEFORE the change and zero after it, so a criterion that is already green cannot detect
            anything. A (red) line is a list item (- or *) whose leading tags, after its marker, hold
            (red); lines in ``` fences are left out, and so is a span that references HEAD^1 or holds
            a <placeholder>. Without --step the target is a ticket handoff (a dir's handoff.md, or the
            file itself, a solo ticket): every (red) line of it, under Done when or ## Acceptance
            criteria or anywhere else, a repeated span once. With --step N the target is a plan (a
            planner-*.md file, or a task dir's newest by recorded run order, the way check picks it) and
            the spans are those of step N's ### Acceptance criteria; steps.py split --only runs the same
            rule beside its guards, so a chain gets it at split time. Each span runs once in the CURRENT
            tree (a builder never commits, so a base checkout would lack earlier steps) under bash -c
            from the git toplevel of the target (else its dir), under --timeout S (default 300), with
            SDLC_BASE_SHA from <step dir>/base-sha or <task dir>/base-sha when it names a commit, else
            HEAD. Refused, one stderr line each "specgate: red-first: [step <n>: ]`<span>` is green now;
            it cannot detect the change", "... timed out after <s>s; a (red) span must exit
            nonzero quickly", or "specgate: red-first: (red) spans changed the work tree: <paths>
            (restored)": in a git work tree the tree is snapshotted (status plus the content of every
            dirty file) before the first span and what a span changed is put back, so a refusal leaves
            the tree as it found it ("not restored: <paths>" names a path that could not be put back).
            Last line "specgate: red-first: <k> refusal(s); fix the criterion before the build", exit 1.
            All red: "specgate: red-first: ok: <k> (red) span(s) red now in <source>" on stdout, exit 0.
            No (red) criterion: "specgate: red-first: no (red) criteria in <source>", exit 0 (the tag is
            opt-in). A missing target, handoff, plan, or step exits 1. The spans run synchronously, so
            the caller must own the tree while they do. The execution lives in steps.red_first.
            A solo ticket runs it before the first edit; after the build it runs each (red) span itself
            and expects exit 0 (agents/solo.md).
  selftest  prove each finding, each exemption, the skip, the red-first control, and two replays of real plans.
"""
import argparse, contextlib, io, os, pathlib, re, subprocess, sys, tempfile, time

import steps

CHECK_SH_RE = re.compile(r'(?:^|[;&|(!]|\$\(|\b(?:then|do|else)\s)\s*(?:\w+=\S*\s+)*'
                         r'(?:(?:timeout\s+\S+|bash|sh|env)\s+)*["\']?\S*check\.sh["\']?(?=\s|$|[;&|)])')
GUARD_HINT = 'add "guard timeout: <seconds>" to ## Goal or to the step block'


def runs_check_sh(span):
    """True when a command word of the span ends in check.sh (it runs the script, not names it)."""
    return CHECK_SH_RE.search(span) is not None


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
            tags = steps.leading_tags(line)
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


def handoff_red_spans(handoff):
    """The command-like spans of a ticket handoff's (red) list items, outside ``` fences, a repeat once."""
    out, fenced = [], False
    for line in pathlib.Path(handoff).read_text(encoding='utf-8').splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
        elif not fenced and steps.list_item(line) and steps.is_red_line(line):
            out += [t for t in steps.line_spans(line) if t not in out]
    return out


def red_target(target, step):
    """(source path, step number or None, dir holding base-sha or None, runnable (red) spans). Raises
    steps.Fail when the handoff, plan, or step does not exist."""
    t = pathlib.Path(target)
    if step is None:
        handoff = t / 'handoff.md' if t.is_dir() else t
        if not handoff.is_file():
            raise steps.Fail(f'specgate: no ticket handoff at {handoff}')
        return handoff, None, handoff.parent, handoff_red_spans(handoff)
    plan, task_dir = steps.find_plan(t)
    blocks = steps.parse_steps(plan)
    if step not in blocks:
        raise steps.Fail(f'specgate: step {step} is not in {plan} (steps: {", ".join(map(str, blocks))})')
    d = task_dir / f'step-{step}'
    return plan, step, d if d.is_dir() else task_dir, steps.red_spans(blocks[step])


def cmd_red(target, step=None, timeout=steps.DEFAULT_GUARD_TIMEOUT):
    try:
        source, n, bdir, spans = red_target(target, step)
    except steps.Fail as e:
        print(e, file=sys.stderr)
        return 1
    spans = [t for t in spans if not steps.guard_skipped(t)]
    if not spans:
        print(f'specgate: red-first: no (red) criteria in {source}')
        return 0
    top = steps.git_toplevel(bdir)
    found = steps.red_first([(n, t, timeout) for t in spans], top, top or str(bdir), steps.base_sha(top, bdir))
    if found:
        for m in found:
            print(f'specgate: red-first: {m}', file=sys.stderr)
        print(f'specgate: red-first: {len(found)} refusal(s); fix the criterion before the build', file=sys.stderr)
        return 1
    print(f'specgate: red-first: ok: {len(spans)} (red) span(s) red now in {source}')
    return 0


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
    '- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/planning/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/supervisor.py)"`',
]
T0183_STEP3 = [
    '- `out=$(python3 plugins/sdlc-lite/scripts/supervisor.py selftest) && test "$(printf \'%s\\n\' "$out" | tail -n 1)" = "supervisor selftest: PASS" && for l in "cooldown: a second wake waits, status cooling" "control: a copy without the cooldown wakes twice" "cap: the hourly cap holds" "cap: the daily cap holds" "cap: limits set to 0 refuse every wake" "control: a copy without the caps wakes past them" "depth: a reply chain of three records needs a human" "depth: a chain of two still wakes" "depth: a wake-sent chain without re counts" "control: a copy without the depth rule wakes" "active: a running recorded wake skips the wake" "active: a recent transcript skips the wake" "active: a stale pid record is dropped" "control: a copy that ignores the active signal wakes" "failure: backoff, then failed after three" "failure: exit 0 without progress counts" "failure: a timed-out wake is killed and counts" "failure: a stranded read message is retried" "control: a copy that trusts the exit code fails" "control: a copy without the failure stop keeps waking" "reset: clears failed" "restart: counters survive a restart"; do printf \'%s\\n\' "$out" | grep -qxF "ok: $l" || exit 1; done`',
    '- `python3 plugins/sdlc-lite/scripts/supervisor.py reset --help | grep -qF -- "--receiver"`',
    '- `f=plugins/sdlc-lite/scripts/supervisor.py; test -f "$f" && ! grep -qE "shell=True|os\\.system\\(|os\\.popen\\(" "$f" && ! grep -qF "$(printf \'\\342\\200\\224\')" "$f"`',
    '- `p="$(dirname "$(cd "$(git rev-parse --git-common-dir)" && pwd)")/.sdlc/supervisor"; b=$(ls -A "$p" 2>/dev/null); python3 plugins/sdlc-lite/scripts/supervisor.py selftest >/dev/null && test "$(ls -A "$p" 2>/dev/null)" = "$b" && test ! -e .sdlc/supervisor`',
    '- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e docs/planning/ticket-stages/watcher-design.md -e docs/reports/idle-host-watcher-design-review.md -e plugins/sdlc-lite/scripts/check.sh)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/supervisor.py)"`',
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

        # red-first: a (red) criterion must fail before the change and pass after it; each case builds its own repo
        def make_repo(name, files):
            r = tmp / name
            r.mkdir()
            subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
            for rel, text in files.items():
                f = r / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(text, encoding='utf-8')
            subprocess.run(['git', '-C', str(r), 'add', '-A'], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false',
                            'commit', '-qm', 'i'], check=True, capture_output=True)
            return r

        def bash(r, span):
            return subprocess.run(['bash', '-c', span], cwd=str(r), capture_output=True).returncode

        def ticket(*lines):
            return '## Goal\ng\n\n## Intent\n- Done when:\n' + ''.join(f'  {x}\n' for x in lines)

        def porcelain(r):
            return subprocess.run(['git', '-C', str(r), 'status', '--porcelain', '--untracked-files=all'],
                                  capture_output=True, text=True).stdout

        def red_refusal(rc, out, err, k=1):
            lines = err.strip().splitlines()
            return (rc == 1 and out == '' and lines[-1] == f'specgate: red-first: {k} refusal(s); fix the criterion before the build'
                    and len(lines) == k + 1 and all(x.startswith('specgate: red-first: ') for x in lines))

        span = 'test -f out.txt'
        ac = f'## Acceptance criteria\n- (red) `{span}`\n- (guard) `test -d .sdlc`\n'
        r = make_repo('red-solo', {'.sdlc/t1/handoff.md': ticket(f'- (red) `{span}`', '- `test -d .sdlc`') + ac})
        h = r / '.sdlc' / 't1'
        before_rc = bash(r, span)
        rc, out, err = run_main(['red', str(h)])
        rc_b, out_b, err_b = run_main(['red', str(h / 'handoff.md')])
        (r / 'out.txt').write_text('built\n', encoding='utf-8')
        after_rc = bash(r, span)
        rc2, out2, err2 = run_main(['red', str(h)])
        check('red: a solo ticket fixture is red before the build and green after (observed)',
              before_rc != 0 and after_rc == 0
              and rc == 0 and out == f'specgate: red-first: ok: 1 (red) span(s) red now in {h / "handoff.md"}\n' and err == ''
              and rc_b == 0 and out_b == out and err_b == ''
              and red_refusal(rc2, out2, err2)
              and f'specgate: red-first: `{span}` is green now; it cannot detect the change' in err2)

        r = make_repo('red-green-base', {'out.txt': 'x\n', '.sdlc/t1/handoff.md': ticket(f'- (red) `{span}`')})
        rc, out, err = run_main(['red', str(r / '.sdlc' / 't1')])
        check('red: a (red) criterion green at base is refused with its name; a red one passes (the fixture above)',
              red_refusal(rc, out, err) and f'`{span}` is green now; it cannot detect the change' in err)

        r = make_repo('red-untagged', {'.sdlc/t1/handoff.md': ticket('- `touch ran-one`', '- (guard) `touch ran-two`',
                                                                      '- x (red) `touch ran-three`', '- (red) `touch <ran-four>`')
                                       + '```\n- (red) `touch ran-five`\n```\n'})
        rc, out, err = run_main(['red', str(r / '.sdlc' / 't1')])
        check('red: untagged, (guard), mid-line (red), placeholder, and fenced spans are never run',
              rc == 0 and out.startswith('specgate: red-first: no (red) criteria in ') and err == ''
              and not any((r / f).exists() for f in ('ran-one', 'ran-two', 'ran-three', 'ran-five'))
              and porcelain(r) == '')

        r = make_repo('red-tree', {'tracked.txt': 'a\n', '.sdlc/t1/handoff.md': ticket('- (red) `touch made; false`')})
        rc, out, err = run_main(['red', str(r / '.sdlc' / 't1')])
        check('red: a span that changes the tree is refused and the snapshot restores it',
              red_refusal(rc, out, err) and 'changed the work tree: made (restored)' in err
              and not (r / 'made').exists() and porcelain(r) == '')
        kept = steps.red_restore
        steps.red_restore = lambda *a: []
        try:
            rc, out, err = run_main(['red', str(r / '.sdlc' / 't1')])
        finally:
            steps.red_restore = kept
        check('red: control: with the restore disabled the changed file stays behind (the restore check bites)',
              rc == 1 and (r / 'made').exists())
        (r / 'made').unlink()

        r = make_repo('red-dirty', {'tracked.txt': 'a\n', '.sdlc/t1/handoff.md': ticket(
            '- (red) `echo more >> tracked.txt; echo mine > builder.txt; touch fresh; git add fresh; false`')})
        (r / 'builder.txt').write_text('builder work\n', encoding='utf-8')
        (r / 'tracked.txt').write_text('a\nedited by the builder\n', encoding='utf-8')
        pre = porcelain(r)
        rc, out, err = run_main(['red', str(r / '.sdlc' / 't1')])
        check('red: a tracked edit, an already-dirty file, and a staged new file all come back as they were',
              red_refusal(rc, out, err) and '(restored)' in err
              and (r / 'tracked.txt').read_text(encoding='utf-8') == 'a\nedited by the builder\n'
              and (r / 'builder.txt').read_text(encoding='utf-8') == 'builder work\n'
              and not (r / 'fresh').exists() and porcelain(r) == pre)

        r = make_repo('red-slow', {'.sdlc/t1/handoff.md': ticket('- (red) `sleep 30`')})
        t0 = time.monotonic()
        rc, out, err = run_main(['red', str(r / '.sdlc' / 't1'), '--timeout', '1'])
        check('red: a timeout is refused and does not wait out the span',
              red_refusal(rc, out, err) and 'timed out after 1s' in err and time.monotonic() - t0 < 15)

        r = make_repo('red-chain', {'.sdlc/c1/handoff.md': '## Goal\ng\n'})
        c = r / '.sdlc' / 'c1'
        (c / 'planner-L2.md').write_text(plan_text([], ('A', [], [f'- (red) `{span}`', '- (guard) `test -d .sdlc`']),
                                                   ('B', [], ['- `test -d .sdlc`'])), encoding='utf-8')
        rc, out, err = run_main(['red', str(c), '--step', '1'])
        rc_n, out_n, err_n = run_main(['red', str(c / 'planner-L2.md'), '--step', '2'])
        (r / 'out.txt').write_text('built\n', encoding='utf-8')
        rc2, out2, err2 = run_main(['red', str(c), '--step', '1'])
        rc9, out9, err9 = run_main(['red', str(c), '--step', '9'])
        check('red: --step reads a plan step: red passes, green is refused naming the step, no (red) is no-op',
              rc == 0 and 'ok: 1 (red) span(s) red now' in out and err == ''
              and rc_n == 0 and out_n.startswith('specgate: red-first: no (red) criteria in ') and err_n == ''
              and red_refusal(rc2, out2, err2) and f'step 1: `{span}` is green now' in err2
              and rc9 == 1 and out9 == '' and 'step 9 is not in' in err9)

        plain = tmp / 'red-plain'
        (plain / 't1').mkdir(parents=True)
        (plain / 't1' / 'handoff.md').write_text(ticket('- (red) `test -f out.txt`'), encoding='utf-8')
        rc, out, err = run_main(['red', str(plain / 't1')])
        (plain / 't1' / 'out.txt').write_text('x\n', encoding='utf-8')
        rc2, out2, err2 = run_main(['red', str(plain / 't1')])
        rc3, out3, err3 = run_main(['red', str(tmp / 'no-such-ticket')])
        rc4, out4, err4 = run_main(['red', str(empty)])
        check('red: outside git it runs in the target dir; a missing handoff or dir exits 1 with a message',
              rc == 0 and 'ok: 1 (red) span(s) red now' in out and red_refusal(rc2, out2, err2)
              and rc3 == 1 and out3 == '' and 'no ticket handoff' in err3
              and rc4 == 1 and out4 == '' and 'no ticket handoff' in err4)

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
    p = sub.add_parser('red', help='refuse a (red) criterion that is already green: it cannot detect the change')
    p.add_argument('target', help='a ticket handoff.md or its dir, or with --step a planner-*.md or its task dir')
    p.add_argument('--step', type=int, help='read step N of the plan instead of a ticket handoff')
    p.add_argument('--timeout', type=float, default=steps.DEFAULT_GUARD_TIMEOUT, help='seconds per span (default 300)')
    sub.add_parser('selftest', help='prove every finding, exemption, skip, and the red-first control')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'red':
        return cmd_red(a.target, a.step, a.timeout)
    return cmd_check(a.target)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
