#!/usr/bin/env python3
"""Split a planner result into one step handoff per step, so /chain never parses a plan by hand.

Usage: steps.py {split <planner.md | task dir> [--only N ...] [--guard-timeout SECONDS] |
                 lint <planner.md | task dir> | next <step dir> | selftest}
  split     read the plan (a planner-*.md file, or the newest planner-*.md in a task dir,
            by recorded run order in its runs.jsonl, see order.py)
            and the task goal (the ## Goal section of <task dir>/handoff.md, front matter skipped),
            then write <task dir>/step-<n>/handoff.md as "## Task goal", the goal, a blank line,
            and the step block verbatim (## Step <n>: ... up to the next ## heading, trailing
            blank lines trimmed). Prints one line per file written.
            --only N (repeatable) writes only those steps; an N not in the plan is an error.
            Refuses a step whose step-<n>/ already holds builder-*.md or verifier-*.md: rename it
            to step-<n>.superseded-<k>/ first (/chain 4.2). This script never renames anything.
            Refuses a plan whose acceptance criterion commands do not parse (see lint): the
            refusal names each span and ends with "plan defect: replan this step (/chain 3)".
            It also refuses a criterion span that joins two checks with an unquoted || (see lint).
            With --only N, split then runs that step's (guard) criteria against the current tree:
            each command-like code span on a criterion line that starts with "(guard)" runs under
            bash -c, from the git toplevel of the task dir (else the task dir), under
            --guard-timeout SECONDS (default 300). A span that references HEAD^1 or holds a
            <placeholder> is skipped, never run. A red guard (nonzero exit) or a timeout refuses:
            one line per red guard with its exit code or timeout and its output tail, then a last
            line "plan defect: step <n> red guard: <span>; replan this step (/chain 3)".
            In a git work tree it also snapshots `git status --porcelain --untracked-files=all`
            (plus each listed path's size and mtime) before the first runnable guard and after
            the last; a path that is new or different afterwards means the guards changed the
            work tree, and split refuses: one line per such path, then one last line
            "plan defect: ... (guard) criteria changed the work tree: <paths>; replan this step
            (/chain 3)" (a red guard, if any, is named on the same line). A tree dirty before
            the guards passes when they leave it as it was. Nothing is undone.
            A full split (no --only) and lint never execute a span.
            Every check runs before any write: a failure prints on stderr, exits 1, writes nothing.
  lint      pick the plan the same way split does, then check that every command-like code span
            under a step's ### Acceptance criteria (outside ``` fences) parses under bash -n, with
            each <placeholder> replaced first, and that none holds an unquoted || operator (a
            fallback passes on either side, so the criterion cannot fail); a || inside quotes, or
            one whose left operand is exactly `test $# -eq 0`, is allowed. Never executes a span, writes nothing, and needs no
            handoff.md. Prints "steps lint: ok", or the split refusal on stderr and exits 1.
  next      print the next escalation action for a step dir (/chain step 4), from its newest
            builder-*.md and verifier-*.md by order.py (ordered, newest, counts_after; never file
            times). Writes nothing. Stdout: "<action>" or "<action> L<n>", then "reason: <text>",
            then one "read: <path>" per result file consulted; exit 0. Rules, in order:
              build level = level of the newest builder result, else the handoff's level: line;
              verifier level: build L1/L2 -> L1, L3 -> L2, L4/L5 -> L3.
              no builder result                          -> build L<handoff level>
              newest builder Status blocked              -> replan (whatever its Notes say)
              no verifier result counts after the build  -> verify L<verifier level>
              newest verifier has no pass/fail Verdict   -> reverify L<level of that verifier>,
                but 2+ consecutive no-verdict verifiers after the build -> stop
              newest verifier Verdict pass               -> done
              fail whose ## For the next attempt starts "plan defect:" -> replan
              else count non-plan-defect fails whose paired builder (newest before each
              verifier) is at the current build level: 1 -> rebuild L<n>,
              2+ at L1..L4 -> bump L<n+1>, 2+ at L5 -> stop.
              A verifier with no verdict is never counted as a fail.
            Errors (missing dir, no handoff level with no builder result, a builder with no
            done/blocked Status) print one "steps next: "
            line on stderr, nothing on stdout, and exit 1.
  selftest  build fixtures in a temp dir and prove every case and every failure fires
"""
import argparse
import contextlib
import io
import os
import pathlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

import order

STEP_RE = re.compile(r'^## Step (\d+): (.+)$')
LEVEL_RE = re.compile(r'^level: L[1-5]\s*$')
SPAN_RE = re.compile(r'(`+)(.+?)\1')
ASSIGN_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*=')
PLACEHOLDER_RE = re.compile(r'<[^<>\s][^<>]*>')
BUILTINS = {'cd', 'test', '[', 'echo', 'printf', 'export', 'set', 'true', 'false', 'time', 'type',
            'command', 'eval', 'exec', 'source', '.'}
PLAN_DEFECT = 'plan defect: replan this step (/chain 3)'


class Fail(Exception):
    """A refusal: the message goes to stderr and the command exits 1. Never a traceback."""


def find_plan(target):
    """Return (planner file, task dir) for a planner file or a task dir."""
    target = pathlib.Path(target)
    if target.is_dir():
        plan = order.newest(target, 'planner')
        if not plan:
            raise Fail(f'steps: no planner-*.md in {target}')
        return pathlib.Path(plan), target
    if target.is_file():
        return target, target.parent
    raise Fail(f'steps: no such file or directory: {target}')


def read_goal(task_dir):
    handoff = task_dir / 'handoff.md'
    if not handoff.is_file():
        raise Fail(f'steps: no task handoff at {handoff}; the goal comes from its ## Goal section')
    lines = handoff.read_text(encoding='utf-8').splitlines()
    i = 0
    if lines and lines[0].strip() == '---':
        end = next((j for j in range(1, len(lines)) if lines[j].strip() == '---'), None)
        if end is None:
            raise Fail(f'steps: {handoff} opens front matter with --- but never closes it')
        i = end + 1
    start = next((j for j in range(i, len(lines)) if lines[j].rstrip() == '## Goal'), None)
    if start is None:
        raise Fail(f'steps: {handoff} has no ## Goal section')
    body = []
    for line in lines[start + 1:]:
        if line.startswith('## '):
            break
        body.append(line)
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if not body:
        raise Fail(f'steps: the ## Goal section of {handoff} is empty')
    return '\n'.join(body)


def parse_steps(plan):
    """Return {n: block text} in plan order. A block runs from its ## Step line to the next ## line."""
    steps = {}
    cur = None
    for line in plan.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            cur = None
            m = STEP_RE.match(line)
            if m:
                n = int(m.group(1))
                if n in steps:
                    raise Fail(f'steps: {plan} has step {n} twice')
                steps[n] = cur = [line]
            continue
        if cur is not None:
            cur.append(line)
    if not steps:
        raise Fail(f'steps: {plan} has no "## Step <n>: <title>" blocks')
    out = {}
    for n, block in steps.items():
        while block and not block[-1].strip():
            block.pop()
        if not any(LEVEL_RE.match(line) for line in block):
            raise Fail(f'steps: step {n} in {plan} has no "level: L1".."level: L5" line')
        out[n] = '\n'.join(block)
    return out


def criteria_lines(block):
    """Lines under each ### Acceptance criteria of a step block, up to the next ## or ### line,
    with ``` fenced lines left out."""
    out = []
    inside = fenced = False
    for line in block.splitlines():
        if line.startswith('## ') or line.startswith('### '):
            inside = line.strip() == '### Acceptance criteria'
            fenced = False
            continue
        if not inside:
            continue
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


def is_command(text):
    """True when a code span reads as a shell command, judged by its head token."""
    tokens = text.split()
    assigns = []
    i = 0
    while i < len(tokens) and (ASSIGN_RE.match(tokens[i]) or tokens[i] == '!'):
        if tokens[i] != '!':
            assigns.append(tokens[i])
        i += 1
    if any('$(' in a for a in assigns):
        return True
    if i == len(tokens):
        return False
    head = tokens[i]
    return (head in BUILTINS or '/' in head or head.endswith('.py') or head.endswith('.sh')
            or shutil.which(head) is not None)


def line_spans(line):
    """The command-like code spans on one line, in order."""
    spans = []
    for m in SPAN_RE.finditer(line):
        text = m.group(2)
        if text.startswith(' '):
            text = text[1:]
        if text.endswith(' '):
            text = text[:-1]
        if re.search(r'\s', text) and is_command(text):
            spans.append(text)
    return spans


def command_spans(block):
    """The command-like code spans under a step block's acceptance criteria, in order."""
    return [text for line in criteria_lines(block) for text in line_spans(line)]


def is_guard_line(line):
    """True when a criterion line, after its list marker (- or *), starts with (guard)."""
    text = line.lstrip()
    if text.startswith('- ') or text.startswith('* '):
        text = text[2:].lstrip()
    return text.startswith('(guard)')


def guard_spans(block):
    """The command-like code spans on a step block's (guard) criterion lines, in order.
    Same lines (criteria_lines) and same span test (line_spans) as command_spans."""
    return [text for line in criteria_lines(block) if is_guard_line(line) for text in line_spans(line)]


def guard_skipped(text):
    """A guard span that cannot run against the current tree: it references HEAD^1 (a merge
    commit not made yet) or holds a <placeholder>."""
    return 'HEAD^1' in text or PLACEHOLDER_RE.search(text) is not None


def git_toplevel(task_dir):
    """The git toplevel of the task dir, or None outside a git work tree."""
    try:
        r = subprocess.run(['git', '-C', str(task_dir), 'rev-parse', '--show-toplevel'],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    top = r.stdout.strip()
    return top if r.returncode == 0 and top else None


def guard_cwd(task_dir):
    """The git toplevel of the task dir, else the task dir itself."""
    return git_toplevel(task_dir) or str(task_dir)


def tree_state(top):
    """The work tree's status for side-effect detection: path -> (porcelain XY, size, mtime_ns),
    tracked and untracked (ignored files excluded), or None when git status fails. Read-only:
    --no-optional-locks keeps git from refreshing the index."""
    try:
        r = subprocess.run(['git', '--no-optional-locks', '-C', top, 'status', '--porcelain',
                            '--untracked-files=all', '-z'],
                           capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0:
        return None
    state = {}
    fields = r.stdout.decode('utf-8', errors='surrogateescape').split('\0')
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        xy, path = entry[:2], entry[3:]
        if 'R' in xy or 'C' in xy:
            i += 1  # a rename or copy is followed by its source path
        try:
            st = os.lstat(os.path.join(top, path))
            stat = (st.st_size, st.st_mtime_ns)
        except OSError:
            stat = None
        state[path] = (xy, stat)
    return state


def tree_changes(before, after):
    """Paths new in after, gone from after, or different between the two states, sorted."""
    return sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))


def run_guard(text, cwd, timeout):
    """Run one guard span. Returns (rc or None on timeout, combined output tail lines).
    It runs in its own session so a timeout kills the whole process group, grandchildren too."""
    proc = subprocess.Popen(['bash', '-c', '--', text], cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        rc = None
    tail = [line for line in (err + out).decode('utf-8', errors='replace').splitlines() if line.strip()]
    return rc, tail[-5:]


def run_guards(plan, steps, chosen, task_dir, timeout):
    """Run the runnable (guard) spans of each chosen step; raise Fail naming every red one.
    Called only by split --only; a full split and lint never execute a span."""
    top = git_toplevel(task_dir)
    cwd = top or str(task_dir)
    lines, red, before, ran = [], [], None, False
    for n in chosen:
        for text in guard_spans(steps[n]):
            if guard_skipped(text):
                continue
            if top and not ran:
                before = tree_state(top)
            ran = True
            rc, tail = run_guard(text, cwd, timeout)
            if rc == 0:
                continue
            why = f'timed out after {timeout:g}s' if rc is None else f'exit {rc}'
            lines.append(f'steps: {plan} step {n}: (guard) criterion is red now ({why}): {text}')
            lines += [f'  {t}' for t in tail]
            red.append(f'step {n} red guard: {text}')
    after = tree_state(top) if before is not None else None
    changed = tree_changes(before, after) if after is not None else []
    if changed:
        which = f'step {chosen[0]}' if len(chosen) == 1 else f'steps {", ".join(map(str, chosen))}'
        lines += [f'steps: {plan} {which}: (guard) criteria changed the work tree: {p}' for p in changed]
        red.append(f'{which} (guard) criteria changed the work tree: {", ".join(changed)}')
    if red:
        raise Fail('\n'.join(lines + [f'plan defect: {"; ".join(red)}; replan this step (/chain 3)']))


OR_ALLOWED_LEFT = ['test', '$#', '-eq', '0']


def or_fallback(text):
    """True when a span holds an unquoted || whose left operand is not exactly `test $# -eq 0`.
    Raises ValueError on text shlex cannot tokenize (an unparsable span, already reported)."""
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
    lex.commenters = ''
    lex.whitespace_split = True
    left = []
    for tok in lex:
        if tok and all(c in lex.punctuation_chars for c in tok):
            if tok == '||' and left != OR_ALLOWED_LEFT:
                return True
            if ';' in tok or '|' in tok or '&&' in tok:
                left = []
                continue
        left.append(tok)
    return False


def lint_steps(plan, steps):
    """Return one finding per command-like criterion span that bash -n cannot parse, and one per
    span that joins two checks with an unquoted ||; [] when clean. bash -n parses and never executes."""
    findings = []
    for n, block in steps.items():
        for text in command_spans(block):
            probe = PLACEHOLDER_RE.sub('PLACEHOLDER', text)
            try:
                r = subprocess.run(['bash', '-n', '-c', '--', probe], capture_output=True, text=True, timeout=5)
                rc, err = r.returncode, r.stderr
            except subprocess.TimeoutExpired:
                rc, err = 1, 'bash -n did not finish within 5 seconds'
            if rc != 0:
                lines = [f'steps: {plan} step {n}: acceptance criterion command does not parse: {text}']
                lines += [f'  {e}' for e in err.splitlines() if e.strip()]
                findings.append('\n'.join(lines))
                continue
            try:
                joined = or_fallback(text)
            except ValueError:
                continue
            if joined:
                findings.append(f'steps: {plan} step {n}: acceptance criterion joins two checks with ||: {text}\n'
                                '  the fallback can pass on either side, so the criterion cannot fail: '
                                'split it into separate criteria')
    return findings


def lint_or_fail(plan, steps):
    findings = lint_steps(plan, steps)
    if findings:
        raise Fail('\n'.join(findings + [PLAN_DEFECT]))


def split(target, only=None, guard_timeout=300):
    """Check everything, then write. Returns the paths written. With only, the chosen steps'
    runnable (guard) spans run before any write."""
    plan, task_dir = find_plan(target)
    goal = read_goal(task_dir)
    steps = parse_steps(plan)
    lint_or_fail(plan, steps)
    if only:
        missing = sorted(set(n for n in only if n not in steps))
        if missing:
            raise Fail(f'steps: --only {", ".join(map(str, missing))} not in {plan} '
                       f'(steps: {", ".join(map(str, steps))})')
        chosen = [n for n in steps if n in set(only)]
    else:
        chosen = list(steps)
    for n in chosen:
        d = task_dir / f'step-{n}'
        done = sorted(p.name for pat in ('builder-*.md', 'verifier-*.md') for p in d.glob(pat)) if d.is_dir() else []
        if done:
            raise Fail(f'steps: {d} already holds role output ({", ".join(done)}). Per /chain 4.2, rename it '
                       f'to step-{n}.superseded-<k>/ (next free k) first, then split again. Nothing was written.')
    if only:
        run_guards(plan, steps, chosen, task_dir, guard_timeout)
    written = []
    for n in chosen:
        d = task_dir / f'step-{n}'
        d.mkdir(parents=True, exist_ok=True)
        path = d / 'handoff.md'
        path.write_text(f'## Task goal\n{goal}\n\n{steps[n]}\n', encoding='utf-8')
        written.append(path)
    return written


def cmd_split(target, only, guard_timeout=300):
    try:
        written = split(target, only, guard_timeout)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    for p in written:
        print(p)
    return 0


def cmd_lint(target):
    try:
        plan, _ = find_plan(target)
        lint_or_fail(plan, parse_steps(plan))
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print('steps lint: ok')
    return 0


# --- next -------------------------------------------------------------------

HANDOFF_LEVEL_RE = re.compile(r'^level: L([1-5])\s*$')
RESULT_LEVEL_RE = re.compile(r'^[a-z]+-L(\d+)')


def verifier_level(build_level):
    """Verifier level from build level: L1 or L2 -> L1, L3 -> L2, L4 or L5 -> L3."""
    return 1 if build_level <= 2 else 2 if build_level == 3 else 3


def result_level(path):
    m = RESULT_LEVEL_RE.match(os.path.basename(path))
    if not m:
        raise Fail(f'steps next: cannot read a level from the name {path}')
    return int(m.group(1))


def section(path, heading):
    """Lines under '## <heading>' up to the next ## line, or None when the heading is absent."""
    lines = pathlib.Path(path).read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines):
        if line.rstrip() == f'## {heading}':
            body = []
            for rest in lines[i + 1:]:
                if rest.startswith('## '):
                    break
                body.append(rest)
            return body
    return None


def first_word(path, heading, allowed, kind):
    """The first non-blank line under ## <heading>, which must be one of allowed."""
    body = section(path, heading)
    first = next((line.strip() for line in body if line.strip()), '') if body is not None else ''
    if first.lower() not in allowed:
        raise Fail(f'steps next: {path} has no {kind} ({"/".join(allowed)}) under ## {heading}')
    return first.lower()


def build_status(path):
    return first_word(path, 'Status', ('done', 'blocked'), 'builder status')


def verdict(path):
    return first_word(path, 'Verdict', ('pass', 'fail'), 'verifier verdict')


def verdict_or_none(path):
    """'pass' or 'fail' from the first non-blank line under ## Verdict, else None. Never raises."""
    try:
        return verdict(path)
    except Exception:
        return None


def is_plan_defect(path):
    body = section(path, 'For the next attempt') or []
    first = next((line.strip() for line in body if line.strip()), '')
    return first.startswith('plan defect:')


def handoff_level(d):
    h = d / 'handoff.md'
    if not h.is_file():
        raise Fail(f'steps next: no builder result and no {h} to read a level from')
    for line in h.read_text(encoding='utf-8').splitlines():
        m = HANDOFF_LEVEL_RE.match(line)
        if m:
            return int(m.group(1))
    raise Fail(f'steps next: no builder result and {h} has no "level: L1".."level: L5" line')


def next_action(step_dir):
    """Return (action, level or None, reason, [result paths read]). Reads only; never file times.
    Ordering comes from order.py alone (ordered, newest, counts_after)."""
    d = pathlib.Path(step_dir)
    if not d.is_dir():
        raise Fail(f'steps next: no such directory: {d}')
    builders = order.ordered(d, 'builder')
    b = order.newest(d, 'builder')
    if b is None:
        n = handoff_level(d)
        return 'build', n, f'no builder result; handoff level L{n}', []
    level = result_level(b)
    read = [b]
    if build_status(b) == 'blocked':
        return 'replan', None, f'newest builder {os.path.basename(b)} is blocked (a blocked build replans)', read
    v = order.newest(d, 'verifier')
    if v is None or not order.counts_after(v, b):
        why = 'no verifier result' if v is None else f'verifier {os.path.basename(v)} is older than the build'
        return ('verify', verifier_level(level),
                f'{why}; build L{level} -> verifier L{verifier_level(level)}', read)
    read.append(v)
    if verdict_or_none(v) is None:
        runs = 0
        for w in reversed(order.ordered(d, 'verifier')):
            if not order.counts_after(w, b):
                continue
            if verdict_or_none(w) is not None:
                break
            runs += 1
        name = os.path.basename(v)
        if runs <= 1:
            return ('reverify', result_level(v),
                    f'{name} has no verdict (pass/fail) under ## Verdict; rerun the verifier at the same level',
                    read)
        return ('stop', None,
                f'{runs} consecutive verifier results with no verdict at build L{level} (newest {name}); ask the user',
                read)
    if verdict(v) == 'pass':
        return 'done', None, f'newest verifier {os.path.basename(v)} passed', read
    if is_plan_defect(v):
        return 'replan', None, f'newest verifier {os.path.basename(v)} failed with a plan defect', read
    count = 0
    for w in order.ordered(d, 'verifier'):
        paired = [x for x in builders if order.counts_after(w, x)]
        if not paired or result_level(paired[-1]) != level:
            continue
        if w not in read:
            read.append(w)
        if verdict_or_none(w) == 'fail' and not is_plan_defect(w):
            count += 1
    if count <= 1:
        return 'rebuild', level, f'first counted fail at build L{level}', read
    if level < 5:
        return 'bump', level + 1, f'{count} counted fails at build L{level}', read
    return 'stop', None, f'{count} counted fails at build L5; there is no L6, ask the user', read


def cmd_next(step_dir):
    try:
        action, level, reason, read = next_action(step_dir)
    except Fail as e:
        print(e, file=sys.stderr)
        return 1
    print(action if level is None else f'{action} L{level}')
    print(f'reason: {reason}')
    for p in read:
        print(f'read: {p}')
    return 0


# --- selftest ---------------------------------------------------------------

HANDOFF = """---
id: T-0001
title: "x"
---

## Goal

Ship the widget.
Second goal line.

## Intent
- not part of the goal
"""

GOAL = 'Ship the widget.\nSecond goal line.'

STEP1 = """## Step 1: First thing
level: L2
### Do
Do one.

### Acceptance criteria
- one works"""

STEP2 = """## Step 2: Second thing
level: L1
### Do
Do two.
### Acceptance criteria
- two works"""

PLAN = f"""# Plan
## Goal
plan goal, not the task goal

{STEP1}


{STEP2}

## Risks
- RISKTEXT must not leak
"""

BROKEN_CRITERION = "- `grep -c 'foo' bar'`"

BROKEN_PLAN = PLAN.replace('- one works', BROKEN_CRITERION)


def snapshot(root):
    """Every file under root: relative path -> (mtime_ns, bytes)."""
    snap = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = pathlib.Path(dirpath) / f
            snap[str(p.relative_to(root))] = (p.stat().st_mtime_ns, p.read_bytes())
    return snap


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


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

        def task(plan=PLAN, handoff=HANDOFF, plan_name='planner-L2.md'):
            count[0] += 1
            d = tmp / f'task{count[0]}'
            d.mkdir()
            if handoff is not None:
                (d / 'handoff.md').write_text(handoff, encoding='utf-8')
            if plan is not None:
                (d / plan_name).write_text(plan, encoding='utf-8')
            return d

        def refused(name, argv, root, needle=None, needles=()):
            before = snapshot(root)
            rc, out, err = run_main(argv)
            check(name, rc != 0 and err.strip() != '' and out == '' and snapshot(root) == before
                  and (needle is None or needle in err) and all(x in err for x in needles))

        want1 = f'## Task goal\n{GOAL}\n\n{STEP1}\n'
        want2 = f'## Task goal\n{GOAL}\n\n{STEP2}\n'

        # (a) normal plan followed by ## Risks
        d = task()
        rc, out, _ = run_main(['split', str(d / 'planner-L2.md')])
        h1, h2 = d / 'step-1' / 'handoff.md', d / 'step-2' / 'handoff.md'
        got1 = h1.read_text(encoding='utf-8') if h1.is_file() else None
        got2 = h2.read_text(encoding='utf-8') if h2.is_file() else None
        check('(a) 2-step plan writes both handoffs exactly, Risks stays out',
              rc == 0 and got1 == want1 and got2 == want2 and got2 is not None and 'RISKTEXT' not in got2
              and out.split() == [str(h1), str(h2)])

        # (b) --only 2 writes only step-2; --only 9 fails and writes nothing
        d = task()
        rc, out, _ = run_main(['split', str(d), '--only', '2'])
        h2 = d / 'step-2' / 'handoff.md'
        check('(b) --only 2 writes only step-2',
              rc == 0 and not (d / 'step-1').exists() and h2.is_file()
              and h2.read_text(encoding='utf-8') == want2)
        d = task()
        refused('(b) --only 9 fails and writes nothing', ['split', str(d), '--only', '9'], d)

        # (c) task dir input picks the newest planner-*.md by recorded run order, never by file time
        def c_case(times, runs):
            d = task(plan=PLAN.replace('Do one.', 'L3 PLAN'), plan_name='planner-L3.md')
            (d / 'planner-L2.md').write_text(PLAN.replace('Do one.', 'L2 PLAN'), encoding='utf-8')
            for name, t in times.items():
                os.utime(d / name, (t, t))
            if runs is not None:
                (d / 'runs.jsonl').write_text(''.join(
                    f'{{"role": "planner", "level": "{n[8:10]}", "file": "{n}"}}\n' for n in runs), encoding='utf-8')
            rc, _, _ = run_main(['split', str(d)])
            h1 = d / 'step-1' / 'handoff.md'
            return rc, h1.read_text(encoding='utf-8') if h1.is_file() else ''

        def uses(res, want, other):
            rc, got = res
            return rc == 0 and f'{want} PLAN' in got and f'{other} PLAN' not in got

        recorded = ['planner-L3.md', 'planner-L2.md']
        check('(c) equal mtimes: runs.jsonl decides, the lower-named file recorded last is used',
              uses(c_case({'planner-L2.md': 1_000_000, 'planner-L3.md': 1_000_000}, recorded), 'L2', 'L3'))
        check('(c) inverse mtimes: runs.jsonl still decides, same result',
              uses(c_case({'planner-L2.md': 1_000_000, 'planner-L3.md': 2_000_000}, recorded), 'L2', 'L3'))
        check('(c) no runs.jsonl: level then k order, planner-L3.md beats a newer planner-L2.md',
              uses(c_case({'planner-L3.md': 1_000_000, 'planner-L2.md': 2_000_000}, None), 'L3', 'L2'))

        # (d) a step with no level line
        d = task(plan=PLAN.replace('level: L1\n', 'Level is L1\n'))
        refused('(d) missing level: fails and writes nothing', ['split', str(d)], d)

        # (e) duplicate step number
        d = task(plan=PLAN.replace('## Step 2:', '## Step 1:'))
        refused('(e) duplicate step number fails and writes nothing', ['split', str(d)], d)

        # (f) no steps
        d = task(plan='# Plan\n## Goal\nnothing\n## Risks\n- none\n')
        refused('(f) no steps fails and writes nothing', ['split', str(d)], d)

        # (g) step-1 holds builder output: refuse, step-1 and step-2 untouched
        d = task()
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text('old step 1\n', encoding='utf-8')
        (d / 'step-1' / 'builder-L2.md').write_text('## Status\ndone\n', encoding='utf-8')
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'handoff.md').write_text('old step 2\n', encoding='utf-8')
        refused('(g) step-1 with builder-L2.md refuses, names superseded, changes nothing',
                ['split', str(d)], d, needle='superseded')
        d = task()
        (d / 'step-2').mkdir()
        (d / 'step-2' / 'verifier-L1.md').write_text('pass\n', encoding='utf-8')
        refused('(g) verifier-*.md output also refuses', ['split', str(d)], d, needle='superseded')

        # (h) handoff with no Goal section, and no handoff at all
        d = task(handoff='---\nid: T-0001\n---\n\n## Intent\n- x\n')
        refused('(h) handoff with no ## Goal fails and writes nothing', ['split', str(d)], d)
        d2 = task(handoff=None)
        refused('(h) missing handoff.md fails and writes nothing', ['split', str(d2)], d2)

        # re-split over a plain handoff.md with no role output overwrites it
        d = task()
        (d / 'step-1').mkdir()
        (d / 'step-1' / 'handoff.md').write_text('stale\n', encoding='utf-8')
        rc, _, _ = run_main(['split', str(d)])
        check('re-split overwrites a plain step-1/handoff.md with no role output',
              rc == 0 and (d / 'step-1' / 'handoff.md').read_text(encoding='utf-8') == want1)

        # (i) a dot-prefixed closed ticket folder (.NNNN-slug) splits like any task dir
        d = tmp / '.0003-x'
        d.mkdir()
        (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
        (d / 'planner-L2.md').write_text(PLAN, encoding='utf-8')
        rc, _, _ = run_main(['split', str(d)])
        h1 = d / 'step-1' / 'handoff.md'
        check('(i) split on .0003-x writes .0003-x/step-1/handoff.md',
              rc == 0 and h1.is_file() and h1.read_text(encoding='utf-8') == want1)

        # (j) a criterion command that does not parse: split and lint refuse as a plan defect
        d = task(plan=BROKEN_PLAN)
        refused('(j) split refuses a broken criterion command as a plan defect, writes nothing',
                ['split', str(d)], d, needles=('plan defect', 'step 1', 'does not parse'))
        refused('(j) lint on the plan file exits 1 with plan defect, writes nothing',
                ['lint', str(d / 'planner-L2.md')], d, needle='plan defect')

        def j_dir(broken_name, clean_name):
            d = task(plan=None)
            (d / broken_name).write_text(BROKEN_PLAN, encoding='utf-8')
            (d / clean_name).write_text(PLAN, encoding='utf-8')
            (d / 'runs.jsonl').write_text(''.join(
                f'{{"role": "planner", "level": "{n[8:10]}", "file": "{n}"}}\n'
                for n in ('planner-L3.md', 'planner-L2.md')), encoding='utf-8')
            return d

        d = j_dir('planner-L2.md', 'planner-L3.md')
        refused('(j) lint on a task dir lints the plan runs.jsonl names newest (broken planner-L2.md)',
                ['lint', str(d)], d, needle='plan defect')
        d = j_dir('planner-L3.md', 'planner-L2.md')
        rc, out, err = run_main(['lint', str(d)])
        rc2, _, _ = run_main(['split', str(d)])
        check('(j) lint on a task dir skips an older broken planner-L3.md, like split',
              rc == 0 and out.strip() == 'steps lint: ok' and err == '' and rc2 == 0)

        # (k) command spans that parse, and non-command spans, pass
        k_spans = ['grep -c "x" scripts/steps.py', 'scripts/steps.py',
                   'python3 scripts/board.py --root <tmp>', 'SDLC_DRY_RUN=1 scripts/run.sh builder L3 x.md',
                   'd=$(mktemp -d) && ls "$d"', '--sort recent', 'duplicate of T-0002 (beta)']
        k_plan = PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in k_spans))
        d = task(plan=k_plan)
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        kept = command_spans(parse_steps(d / 'planner-L2.md')[1])
        check('(k) parsing command spans, a path, a flag, and prose pass: split writes both, lint ok',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file()
              and rc2 == 0 and out2.strip() == 'steps lint: ok'
              and kept == [k_spans[0], k_spans[2], k_spans[3], k_spans[4]])

        # (k2) a || fallback between checks: lint and split refuse; quoted ||, the
        # `test $# -eq 0 ||` short circuit, and && pass
        d = task(plan=PLAN.replace('- one works', '- `grep -q a x || grep -q b x`'))
        refused('(k2) split refuses a || fallback criterion as a plan defect, writes nothing',
                ['split', str(d)], d, needles=('plan defect', 'step 1', 'joins two checks with ||'))
        refused('(k2) lint refuses a || fallback criterion with plan defect',
                ['lint', str(d / 'planner-L2.md')], d, needle='plan defect')
        ok_spans = ['grep -qE "a||b" x', "grep -q 'a||b' x",
                    'set -- $(ls); test $# -eq 0 || grep -q x "$@"', 'grep -q a x && grep -q b x']
        d = task(plan=PLAN.replace('- one works', '\n'.join(f'- `{s}`' for s in ok_spans)))
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d / 'planner-L2.md')])
        check('(k2) quoted ||, the test $# -eq 0 || short circuit, and && pass: split and lint ok',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and rc2 == 0
              and out2.strip() == 'steps lint: ok')

        # (l) a broken command under ### Do is not a criterion
        d = task(plan=PLAN.replace('Do one.', BROKEN_CRITERION))
        rc, _, _ = run_main(['split', str(d)])
        check('(l) a broken command under ### Do is ignored: split writes normally',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file())

        # (m) a broken command inside a ``` fence under the criteria is skipped
        d = task(plan=PLAN.replace('- one works', f'- one works\n```\n{BROKEN_CRITERION}\n```'))
        rc, _, _ = run_main(['split', str(d)])
        check('(m) a broken command inside a ``` fence is skipped: split writes normally',
              rc == 0 and (d / 'step-1' / 'handoff.md').is_file() and (d / 'step-2' / 'handoff.md').is_file())

        # (n) split --only runs the step's (guard) criteria; full split and lint never do.
        # Every guard uses absolute tmp paths, so none touches the repo.
        def guard_plan(*criteria):
            return ('## Step 1: x\nlevel: L1\n### Do\nd\n### Acceptance criteria\n'
                    + ''.join(f'- {c}\n' for c in criteria))

        red_span = f'test -e {tmp}/nonexistent-sdlc-guard'
        d = task(plan=guard_plan('not a guard', f'(guard) `{red_span}`'))
        before = snapshot(d)
        rc, out, err = run_main(['split', str(d), '--only', '1'])
        last = err.strip().splitlines()[-1] if err.strip() else ''
        check('(n) --only with a red guard refuses, writes nothing, last line is plan defect with the span',
              rc == 1 and out == '' and snapshot(d) == before and not (d / 'step-1').exists()
              and last.startswith('plan defect:') and red_span in last and '(exit 1)' in err)

        green = tmp / 'n-green-ran'
        d = task(plan=guard_plan(f'(guard) `touch {green} && test -f handoff.md`'))
        rc, out, err = run_main(['split', str(d), '--only', '1'])
        check('(n) --only with a green guard runs it (from the task dir outside git) and writes the handoff',
              rc == 0 and err == '' and green.exists() and (d / 'step-1' / 'handoff.md').is_file())

        d = task(plan=guard_plan(f'(guard) `git diff --quiet HEAD^1 HEAD && test -e {tmp}/nope`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) a HEAD^1 guard is skipped (it would be red if run)',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

        d = task(plan=guard_plan('(guard) `test -e <tmp>/nope`'))
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(n) a <placeholder> guard is skipped (it would be red if run)',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())

        d = task(plan=guard_plan('(guard) `sleep 30`'))
        before = snapshot(d)
        t0 = time.monotonic()
        rc, out, err = run_main(['split', str(d), '--only', '1', '--guard-timeout', '1'])
        took = time.monotonic() - t0
        last = err.strip().splitlines()[-1] if err.strip() else ''
        check('(n) a guard past --guard-timeout refuses fast, writes nothing, plan defect last line',
              rc == 1 and out == '' and snapshot(d) == before and took < 15
              and 'timed out after 1s' in err and last.startswith('plan defect:') and 'sleep 30' in last)

        marker = tmp / 'n-full-ran'
        d = task(plan=guard_plan(f'(guard) `touch {marker}`', f'(guard) `{red_span}`'))
        rc, _, _ = run_main(['split', str(d)])
        rc2, out2, _ = run_main(['lint', str(d)])
        check('(n) full split and lint execute no guard: marker absent, a red guard does not refuse',
              rc == 0 and rc2 == 0 and out2.strip() == 'steps lint: ok'
              and (d / 'step-1' / 'handoff.md').is_file() and not marker.exists())

        check('(n) guard_spans keeps only (guard) lines and the same spans command_spans sees',
              guard_spans('## Step 1: x\nlevel: L1\n### Do\n- (guard) `ls -e /`\n### Acceptance criteria\n'
                          '- `ls -a /`\n* (guard) `ls -b /` and `ls -c /`\n  - (guard) `ls -f /`\n'
                          '- (guard) prose\n- x (guard) `ls -d /`\n```\n- (guard) `ls -g /`\n```\n')
              == ['ls -b /', 'ls -c /', 'ls -f /'])

        # (o) split --only in a git work tree refuses when the guards changed the tree
        # (tracked or untracked); a tree already dirty before passes when the guards leave it as is.
        # Each case builds its own throwaway repo under tmp; guards run from its toplevel.
        def o_repo(*criteria, commit=None, dirty=None):
            count[0] += 1
            r = tmp / f'o-repo{count[0]}'
            r.mkdir()
            subprocess.run(['git', 'init', '-q', str(r)], check=True, capture_output=True)
            if commit:
                (r / commit).write_text('a\n', encoding='utf-8')
                subprocess.run(['git', '-C', str(r), 'add', commit], check=True, capture_output=True)
                subprocess.run(['git', '-C', str(r), '-c', 'user.name=t', '-c', 'user.email=t@t',
                                'commit', '-qm', 'i'], check=True, capture_output=True)
            if dirty:
                (r / dirty).write_text('pre\n', encoding='utf-8')
            d = r / '.sdlc' / 'x'
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(HANDOFF, encoding='utf-8')
            (d / 'planner-L2.md').write_text(guard_plan(*criteria), encoding='utf-8')
            return d

        def o_refused(name, d, path):
            rc, out, err = run_main(['split', str(d), '--only', '1'])
            last = err.strip().splitlines()[-1] if err.strip() else ''
            check(name, rc == 1 and out == '' and not (d / 'step-1').exists()
                  and last.startswith('plan defect:') and 'changed the work tree' in last
                  and path in last and last.endswith('; replan this step (/chain 3)')
                  and f'(guard) criteria changed the work tree: {path}' in err)

        o_refused('(o) a guard that creates an untracked file refuses, writes nothing, plan defect names the path',
                  o_repo('(guard) `touch o-made && test -f o-made`'), 'o-made')
        o_refused('(o) a guard that modifies a committed tracked file refuses, writes nothing, names the path',
                  o_repo('(guard) `echo b >> tracked.txt`', commit='tracked.txt'), 'tracked.txt')
        d = o_repo('(guard) `test -d .sdlc`', commit='tracked.txt')
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(o) a guard that changes nothing passes and writes the handoff',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())
        d = o_repo('(guard) `test -f already-dirty && grep -q a tracked.txt`', commit='tracked.txt',
                   dirty='already-dirty')
        (d.parents[1] / 'tracked.txt').write_text('a\nedited before\n', encoding='utf-8')
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        check('(o) a tree dirty before (untracked and modified), guards changing nothing, passes',
              rc == 0 and err == '' and (d / 'step-1' / 'handoff.md').is_file())
        d = o_repo('(guard) `echo more >> already-dirty`', dirty='already-dirty')
        o_refused('(o) a guard that changes an already-dirty file refuses', d, 'already-dirty')
        d = o_repo('(guard) `touch o-both`', f'(guard) `{red_span}`')
        rc, _, err = run_main(['split', str(d), '--only', '1'])
        lines = err.strip().splitlines()
        check('(o) a red guard and a changed tree are both reported, one plan defect last line',
              rc == 1 and not (d / 'step-1').exists() and red_span in lines[-1] and 'o-both' in lines[-1]
              and sum(x.startswith('plan defect:') for x in lines) == 1)
        d = o_repo('(guard) `touch o-full`')
        rc, _, _ = run_main(['split', str(d)])
        check('(o) full split in a git repo runs no guard and does not refuse',
              rc == 0 and not (d.parents[1] / 'o-full').exists() and (d / 'step-1' / 'handoff.md').is_file())

        # next: the /chain step 4 action from the newest results, by recorded run order
        DONE, BLOCKED = '## Status\ndone\n', '## Status\nblocked\n\n## Notes\nplan defect: c1 bad\n'
        PASS = '## Verdict\npass\n\n## For the next attempt\nNone\n'
        FAIL = '## Verdict\nfail\n\n## For the next attempt\nfix x\n'
        DEFECT = '## Verdict\nfail\n\n## For the next attempt\n\nplan defect: c2 contradicts c1\n'

        def step(level, files=(), handoff=True):
            """files: (name, text) in run order; each is recorded in runs.jsonl with a file field."""
            count[0] += 1
            d = tmp / f'step{count[0]}'
            d.mkdir()
            if handoff:
                (d / 'handoff.md').write_text(f'## Task goal\ng\n\n## Step 1: x\nlevel: L{level}\n',
                                              encoding='utf-8')
            for name, text in files:
                (d / name).write_text(text, encoding='utf-8')
            if files:
                (d / 'runs.jsonl').write_text(''.join(f'{{"file": "{n}"}}\n' for n, _ in files),
                                              encoding='utf-8')
            return d

        def nxt(d, want):
            rc, out, err = run_main(['next', str(d)])
            lines = out.splitlines()
            return (rc == 0 and err == '' and lines[:1] == [want] and len(lines) >= 2
                    and lines[1].startswith('reason: ') and all(x.startswith('read: ') for x in lines[2:]))

        check('next build: no results -> build at the handoff level',
              nxt(step(2), 'build L2'))
        check('next verify: build L2 done, no verifier -> verify L1',
              nxt(step(2, [('builder-L2.md', DONE)]), 'verify L1'))
        check('next verify: build L4 done, no verifier -> verify L3',
              nxt(step(4, [('builder-L4.md', DONE)]), 'verify L3'))
        check('next verify: build L3 done, no verifier -> verify L2',
              nxt(step(3, [('builder-L3.md', DONE)]), 'verify L2'))
        check('next replan: a blocked builder replans, whatever its Notes say',
              nxt(step(2, [('builder-L2.md', BLOCKED)]), 'replan'))
        check('next replan: a fail whose next-attempt note starts "plan defect:" replans',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', DEFECT)]), 'replan'))
        check('next done: the newest verifier passed',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', PASS)]), 'done'))
        check('next rebuild: one counted fail -> rebuild at the same level',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL)]), 'rebuild L2'))
        check('next bump: two counted fails at L2 -> bump L3',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL)]), 'bump L3'))
        check('next rebuild after a bump: fails at L2 do not count at L3 -> rebuild L3',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL),
                           ('builder-L3.md', DONE), ('verifier-L2.md', FAIL)]), 'rebuild L3'))
        check('next plan-defect fails are not counted: defect then fail at L2 -> rebuild L2',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', DEFECT),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL)]), 'rebuild L2'))
        check('next stop: two counted fails at L5 -> stop',
              nxt(step(5, [('builder-L5.md', DONE), ('verifier-L3.md', FAIL),
                           ('builder-L5-2.md', DONE), ('verifier-L3-2.md', FAIL)]), 'stop'))
        check('next verify: a stale verifier older than the rebuild -> verify L1',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE)]), 'verify L1'))
        NOVERDICT = 'Nothing to do until the test gate reports.\n'
        check('next reverify: a verifier with no verdict -> reverify at its level',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT)]), 'reverify L1'))
        check('next stop: two consecutive no-verdict verifiers after the build -> stop',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT),
                           ('verifier-L1-2.md', '## Notes\nhm\n')]), 'stop'))
        check('next rebuild: no verdict then a real fail at L2 -> rebuild L2 (no-verdict not counted)',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT),
                           ('verifier-L1-2.md', FAIL)]), 'rebuild L2'))
        check('next done: no verdict then a pass -> done',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', NOVERDICT),
                           ('verifier-L1-2.md', PASS)]), 'done'))
        check('next reverify: fail, rebuild, fail, then no verdict at L2 -> reverify L1, not bump',
              nxt(step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL),
                           ('builder-L2-2.md', DONE), ('verifier-L1-2.md', FAIL),
                           ('verifier-L1-3.md', NOVERDICT)]), 'reverify L1'))
        # order comes from runs.jsonl, never from file times: times set inverse to the run order
        d = step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL), ('builder-L2-2.md', DONE)])
        for i, name in enumerate(('builder-L2-2.md', 'verifier-L1.md', 'builder-L2.md')):
            t = 1_700_000_000 + i * 100
            os.utime(d / name, (t, t))
        check('next verify: file times are ignored, runs.jsonl decides', nxt(d, 'verify L1'))

        def next_refused(name, d):
            root = d if d.is_dir() else tmp
            before = snapshot(root)
            rc, out, err = run_main(['next', str(d)])
            check(name, rc == 1 and out == '' and err.startswith('steps next: ')
                  and len(err.strip().splitlines()) == 1 and snapshot(root) == before)

        next_refused('next error: a dir that does not exist', tmp / 'no-such-step')
        next_refused('next error: no handoff.md and no builder result', step(2, handoff=False))
        d = step(2)
        (d / 'handoff.md').write_text('## Task goal\ng\n\n## Step 1: x\n', encoding='utf-8')
        next_refused('next error: a handoff with no level line and no builder result', d)
        next_refused('next error: a builder with no done/blocked Status',
                     step(2, [('builder-L2.md', '## Status\nmaybe\n')]))

        d = step(2, [('builder-L2.md', DONE), ('verifier-L1.md', FAIL)])
        before = snapshot(d)
        rc, _, _ = run_main(['next', str(d)])
        check('next writes nothing: the step dir snapshot is equal before and after',
              rc == 0 and snapshot(d) == before)

    if misses:
        print('steps selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('steps selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='steps.py', description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('split', help='write step-<n>/handoff.md for each step of a plan')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    p.add_argument('--only', type=int, action='append', metavar='N',
                   help='write only step N (repeatable); runs its (guard) criteria first')
    p.add_argument('--guard-timeout', type=float, default=300, metavar='SECONDS',
                   help='per-guard timeout for --only (default 300); a timeout is a red guard')
    p = sub.add_parser('lint', help='check that criterion commands parse under bash -n; writes nothing')
    p.add_argument('target', help='a planner-*.md file, or a task dir (its newest planner-*.md by recorded run order)')
    p = sub.add_parser('next', help='print the next escalation action for a step dir; writes nothing')
    p.add_argument('step_dir', help='a step dir (step-<n>/) holding handoff.md and builder/verifier results')
    sub.add_parser('selftest', help='prove every case and every refusal fires')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'next':
        return cmd_next(a.step_dir)
    if a.cmd == 'lint':
        return cmd_lint(a.target)
    if not 0 < a.guard_timeout < float('inf'):
        print('steps: --guard-timeout must be a finite number of seconds greater than 0', file=sys.stderr)
        return 1
    return cmd_split(a.target, a.only, a.guard_timeout)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
