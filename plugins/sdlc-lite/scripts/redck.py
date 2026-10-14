#!/usr/bin/env python3
"""Red checkpoint: a builder records its (red) criteria failing before it edits, and a completed build without that record leaves a process deviation.

Usage: redck.py {record <handoff.md | dir> [--attempt-id ID] [--timeout S] | audit <handoff.md | dir> [--attempt-id ID] | deviations <dir> | selftest}
  record    run before the first edit of a build. Every (red) criterion of the handoff (a list item whose
            leading tags hold (red), outside ``` fences, the spans specgate.py red would run) runs once in the
            current tree (steps.red_first: the tree is snapshotted and restored, a timeout is a refusal) and one
            JSON line per span is appended to <records dir>/red-checkpoint.jsonl: type control, ts, attempt_id,
            handoff_sha256 (provenance), criterion_sha256 (sha256 of the criterion line, a newline, and the span: the
            key an audit matches on, T-0425), base_sha (the dir's base-sha, else HEAD), criterion (the exact line), span, exit,
            result (red, green, or timeout), phase, dirty, at_sha (HEAD at record time, None outside git). phase is
            read against the working tree at HEAD, not base_sha (T-0473): pre-edit only when no source path differs
            from HEAD (git diff against HEAD plus untracked files, paths under .sdlc/ and the handoff dir left out),
            so a resumed builder on a branch that already holds earlier commits records pre-edit; otherwise
            retrospective, with the changed paths in dirty. The phase is derived from the tree, never claimed by
            the caller. Test prelude (T-0395): a dirty path that the
            handoff names on a `tests:` line (comma-separated exact repo-relative files, steps.declared_tests)
            and that exists is the regression fixture written before the implementation: it does not make the
            phase retrospective, and the control stores {path: sha256} in prelude; any other dirty path,
            declared tests included only when named, still does. The attempt id is --attempt-id, else
            SDLC_ATTEMPT_ID (a run.sh role has it), else the newest running builder *.attempt.json of the dir
            (a Claude sub-agent), else empty, which no audit accepts. A span that is green now or times out is
            surfaced on stderr and the exit is 1: a criterion already green cannot detect the change, so it is
            never a successful red control (fix the criterion or report `plan defect:`). A retrospective
            record exits 0 and says so: on a resumed build it is a base control, not the original checkpoint.
  audit     run by dispatch.py record and run.sh when a builder completes (also by hand). It reads only
            red-checkpoint.jsonl, never the builder's report and never a later baseline run, so the order is
            not inferred. For each (red) span of the handoff the entries must carry the handoff's current
            criterion_sha256 (an old-format entry without one: the handoff's current sha256) and a base_sha that is
            the dir's current base sha or an ancestor of HEAD (T-0473: the same lineage; outside git, equality
            only). A control from a different lineage stays unbound. A handoff edit that leaves a criterion line
            and its span intact, such as steps.py widen, keeps its control valid; an edited criterion or span
            unbinds only that control:
              ok                this attempt has a pre-edit control and its latest one was red
              preserved         this attempt has no pre-edit red control (none, or its latest was green or timed
                                out), but an earlier attempt has a bound pre-edit red one: a resumed build keeps
                                the original
              green-baseline    this attempt's pre-edit control was green or timed out and no earlier attempt
                                has a bound pre-edit red one (not a red control)
              retrospective     only post-edit controls (phase retrospective)
              prelude-changed   the pre-edit control is red but a declared test no longer matches the sha256 it stored
              missing           no control bound to this attempt (or the attempt id is empty)
            The run status is the worst span (missing, prelude-changed, retrospective, green-baseline, preserved, ok); none
            when the handoff has no (red) criterion. Every audit appends an audit line to red-checkpoint.jsonl; for
            missing, prelude-changed, retrospective, and green-baseline that line also stores, under the key
            deviation, the line "process deviation: red-checkpoint: <status>: ..." it prints on stderr (T-0543: no
            process-deviations.md is written). Exit 0 always: a deviation is recorded, it does not fail the run.
  deviations  <dir>, a task, records or step dir. Print the process deviations recorded there, the lines the
            verifier, filer and builder read: `redck.py deviations <dir>` reads red-checkpoint.jsonl in
            order.records_dir(<dir>) and in each live step-<n>/ under it, in step order (step-<n>.superseded-<k>/
            dirs are left out), and prints the deviation line of each audit row whose status is deviating, prefixed
            "step-<n>: " for the rows of a step dir under it; an older audit row without the key prints "process deviation:
            red-checkpoint: <status>: attempt <id or unbound>". The process deviation: lines of a legacy
            process-deviations.md in the same dirs print too. An identical line prints once. Writes nothing; a
            missing dir prints nothing; exit 0 always. deviation_lines(dir) returns the same lines.
Three records stay apart: runner acceptance (results.py validate and the runs.jsonl completed status say the
report has the right shape), the builder's own check results (its report, unverified), and independent
verification (the verifier verdict). This file speaks only to the order of the (red) controls. A pre-edit
record shows the span failed before this attempt's source changes; it does not show the later green.
Enforcement per host: procedural on both. The builder contract (agents/builder.md) tells the builder to run
record before it edits; nothing stops an edit before it. The audit at completion is mechanical on both hosts
(dispatch.py record on Claude, run.sh on Codex and legacy exec, which also covers the Codex native exchange), so
a missing checkpoint is always recorded. A Claude PreToolUse hook could deny the first source edit until a
control exists; no such hook is registered, and Codex has no hook to register. Live Codex behavior is unverified.
"""
import argparse, contextlib, hashlib, io, json, os, pathlib, re, subprocess, sys, tempfile, time

import order  # same scripts/ dir: the records dir rule (records_dir)
import steps

CHECKPOINT = 'red-checkpoint.jsonl'
LEGACY_DEVIATIONS = 'process-deviations.md'  # read only: written by an audit before T-0543
RANK = {'ok': 0, 'preserved': 1, 'green-baseline': 2, 'retrospective': 3, 'prelude-changed': 4, 'missing': 5}
DEVIATING = ('missing', 'retrospective', 'green-baseline', 'prelude-changed')


def resolve(target, create=False):
    """(handoff, records dir): the dir argument goes through order.records_dir, which holds red-checkpoint.jsonl
    and the *.attempt.json files; a task-side step dir reads its records-side handoff.
    create makes a runtime records dir (a writer: record, audit)."""
    t = pathlib.Path(target)
    if t.is_dir() or (not t.exists() and t.name != 'handoff.md'):
        handoff = t / 'handoff.md'
        if not handoff.is_file():
            handoff = order.records_dir(t) / 'handoff.md'
    else:
        handoff = t if t.exists() else order.records_dir(t.parent) / 'handoff.md'
    if not handoff.is_file():
        raise steps.Fail(f'redck: no handoff at {handoff}')
    return handoff, order.records_dir(handoff.parent, create)


def red_items(handoff):
    """(criterion line, span) for each runnable span of the handoff's (red) list items, outside ``` fences, a repeat once."""
    out, seen, fenced = [], set(), False
    for line in pathlib.Path(handoff).read_text(encoding='utf-8').splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
        elif not fenced and steps.list_item(line) and steps.is_red_line(line):
            for span in steps.line_spans(line):
                if span not in seen and not steps.guard_skipped(span):
                    seen.add(span)
                    out.append((line.strip(), span))
    return out


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def criterion_hash(criterion, span):
    """T-0425: the key of one control, sha256 of its criterion line and span, so an edit elsewhere in the handoff (a
    steps.py widen) does not unbind it."""
    return hashlib.sha256(f'{criterion}\n{span}'.encode('utf-8')).hexdigest()


def git_lines(top, *args):
    r = subprocess.run(['git', '-C', top, *args], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    return r.stdout.splitlines() if r.returncode == 0 else None


def dirty_paths(top, d):
    """Paths that differ from HEAD (tracked diff plus untracked, T-0473: the working tree, not the base, so a
    resumed builder on a branch holding earlier commits sees a clean tree), .sdlc/ and the handoff dir left out;
    None when git cannot say. Splitting off the declared test prelude is split_prelude's job."""
    if not top:
        return None
    tracked = git_lines(top, 'diff', '--name-only', 'HEAD', '--')
    untracked = git_lines(top, 'ls-files', '--others', '--exclude-standard')
    if tracked is None or untracked is None:
        return None
    here = os.path.relpath(os.path.realpath(d), os.path.realpath(top)).replace(os.sep, '/') + '/'
    # T-0486: a root-level `<role>.out` or `<role>.err` is a launcher's stdout/stderr capture, not an edit
    untracked = [p for p in untracked if not (p.count('/') == 0 and p.endswith(('.out', '.err')))]
    return sorted(p for p in set(tracked + untracked) if not p.startswith('.sdlc/') and not p.startswith(here))


def split_prelude(top, handoff, dirty):
    """(implementation paths, prelude) for the dirty paths (T-0395): a dirty path that is a test the handoff declares
    (a `tests:` line, steps.declared_tests) and exists as a file is the regression-fixture prelude, {path: sha256 of
    its content}; every other dirty path is an implementation edit. None dirty stays None. An unsafe `tests:` entry
    declares nothing and is surfaced on stderr."""
    if dirty is None:
        return None, {}
    paths, problems = steps.declared_tests(pathlib.Path(handoff).read_text(encoding='utf-8'))
    for t in problems:
        print(f'redck: tests: entry {t} is not an exact repo-relative file path and declares nothing', file=sys.stderr)
    prelude = {p: sha256(pathlib.Path(top) / p) for p in dirty if p in paths and (pathlib.Path(top) / p).is_file()}
    return [p for p in dirty if p not in prelude], prelude


def entries(d):
    f = pathlib.Path(d) / CHECKPOINT
    out = []
    if f.is_file():
        for line in f.read_text(encoding='utf-8').splitlines():
            with contextlib.suppress(ValueError):
                e = json.loads(line)
                if isinstance(e, dict):
                    out.append(e)
    return out


def append(d, entry):
    with (pathlib.Path(d) / CHECKPOINT).open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, separators=(',', ':')) + '\n')


def attempt_of(d, given):
    """--attempt-id, else SDLC_ATTEMPT_ID, else the newest running builder attempt record of the dir, else ''."""
    if given:
        return given
    if os.environ.get('SDLC_ATTEMPT_ID'):
        return os.environ['SDLC_ATTEMPT_ID']
    best = ('', '')
    for f in pathlib.Path(d).glob('*.attempt.json'):
        with contextlib.suppress(OSError, ValueError):
            a = json.loads(f.read_text(encoding='utf-8'))
            if a.get('role') == 'builder' and a.get('status') == 'running' and a.get('attempt_id'):
                best = max(best, (str(a.get('started_at', '')), a['attempt_id']))
    return best[1]


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def cmd_record(target, attempt_id='', timeout=steps.DEFAULT_GUARD_TIMEOUT):
    try:
        handoff, d = resolve(target, create=True)
    except steps.Fail as e:
        print(e, file=sys.stderr)
        return 1
    items = red_items(handoff)
    if not items:
        print(f'redck: no (red) criteria in {handoff}')
        return 0
    top = steps.exec_toplevel(d)
    base = steps.base_sha(top, handoff.parent)
    dirty, prelude = split_prelude(top, handoff, dirty_paths(top, handoff.parent))
    phase = 'pre-edit' if dirty == [] else 'retrospective'
    at = (git_lines(top, 'rev-parse', 'HEAD') or [None])[0] if top else None
    aid, sha = attempt_of(d, attempt_id), sha256(handoff)
    got = []
    refusals = steps.red_first([(None, span, timeout) for _, span in items], top, top or str(d), base, got)
    for (crit, span), (_, _, rc) in zip(items, got):
        result = 'timeout' if rc is None else 'green' if rc == 0 else 'red'
        append(d, dict(type='control', ts=now(), attempt_id=aid, handoff_sha256=sha, criterion_sha256=criterion_hash(crit, span), base_sha=base, at_sha=at, tree=top, criterion=crit, span=span,
                       exit=rc, result=result, phase=phase, dirty=dirty or [], prelude=prelude))
    if not aid:
        print('redck: no attempt id found; this control binds to no attempt and an audit will not accept it', file=sys.stderr)
    if phase == 'retrospective':
        why = 'git cannot say' if dirty is None else f'{len(dirty)} source path(s) already differ from HEAD'
        print(f'redck: retrospective: {why}; this is a base control, not a red-before-edit checkpoint', file=sys.stderr)
    for m in refusals:
        print(f'redck: {m}', file=sys.stderr)
    if refusals:
        print(f'redck: {len(refusals)} refusal(s); a green or timed-out span is not a red control (fix the criterion or report plan defect)', file=sys.stderr)
        return 1
    print(f'redck: recorded {len(items)} {phase} control(s) red in {d / CHECKPOINT}')
    return 0


def prelude_changed(top, e):
    """The declared test paths of a control whose content no longer matches the sha256 the control stored."""
    pre = e.get('prelude') or {}
    out = []
    for p, h in pre.items():
        f = pathlib.Path(top or '.') / p
        if not f.is_file() or sha256(f) != h:
            out.append(p)
    return out


def same_lineage(top, b, base, cache):
    """T-0473: a control's base binds when it is the current base or, inside git, an ancestor of HEAD; the ancestor
    answer is cached per sha for one audit."""
    if b == base:
        return True
    if not top or not b:
        return False
    if b not in cache:
        try:
            r = subprocess.run(['git', '-C', top, 'merge-base', '--is-ancestor', b, 'HEAD'], capture_output=True,
                               stdin=subprocess.DEVNULL, timeout=30)
            cache[b] = r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            cache[b] = False
    return cache[b]


def span_status(es, crit, span, aid, sha, base, top=None, cache=None):
    key = criterion_hash(crit, span)
    cache = {} if cache is None else cache
    # T-0425: a control binds to its own criterion and span; an old-format entry (no criterion_sha256) still binds
    # to the whole handoff hash as before
    mine = [e for e in es if e.get('type') == 'control' and e.get('span') == span
            and (e['criterion_sha256'] == key if e.get('criterion_sha256') else e.get('handoff_sha256') == sha)
            and same_lineage(top, e.get('base_sha'), base, cache)]
    own = [e for e in mine if aid and e.get('attempt_id') == aid]
    pre = [e for e in own if e.get('phase') == 'pre-edit']
    if pre and pre[-1].get('result') == 'red':
        bad = prelude_changed(top, pre[-1])
        return ('prelude-changed', ', '.join(bad)) if bad else ('ok', '')
    # T-0473: an own pre-edit control that is not red defers to an earlier attempt's pre-edit red original
    earlier = [e for e in mine if e.get('attempt_id') != aid and e.get('phase') == 'pre-edit' and e.get('result') == 'red']
    if earlier:
        bad = prelude_changed(top, earlier[-1])
        return ('prelude-changed', ', '.join(bad)) if bad else ('preserved', earlier[-1].get('attempt_id') or '')
    if pre:
        return 'green-baseline', ''
    return ('retrospective' if own else 'missing'), ''


def clip(s, n=70):
    return s if len(s) <= n else s[:n - 3] + '...'


def cmd_audit(target, attempt_id=''):
    try:
        handoff, d = resolve(target, create=True)
    except steps.Fail as e:
        print(e, file=sys.stderr)
        return 1
    items = red_items(handoff)
    if not items:
        print(f'redck: audit: none: no (red) criteria in {handoff}')
        return 0
    top = steps.exec_toplevel(d)
    base, sha = steps.base_sha(top, handoff.parent), sha256(handoff)
    aid = attempt_of(d, attempt_id)
    es = entries(d)
    cache = {}
    per = [(span,) + span_status(es, crit, span, aid, sha, base, top, cache) for crit, span in items]
    status = max((s for _, s, _ in per), key=RANK.get)
    for span, s, src in per:
        note = f' (original from attempt {src})' if src and s == 'preserved' else f' (declared test changed: {src})' if src else ''
        print(f'redck: audit: {s}{note}: {clip(span)}')
    print(f'redck: audit: {status}')
    row = dict(type='audit', ts=now(), attempt_id=aid, handoff_sha256=sha, base_sha=base, status=status,
               spans=[dict(span=sp, status=s) for sp, s, _ in per])
    line = None
    if status in DEVIATING:
        bad = [clip(sp) for sp, s, _ in per if s in DEVIATING]
        changed = '; '.join(src for _, s, src in per if s == 'prelude-changed' and src)
        what = (f'(red) criteria whose declared test ({changed}) changed after the pre-edit control' if status == 'prelude-changed'
                else '(red) criteria without a pre-edit red control')
        line = (f'process deviation: red-checkpoint: {status}: attempt {aid or "unbound"}, handoff sha256 {sha[:12]}, '
                f'{len(bad)} of {len(per)} {what}: ' + '; '.join(f'`{b}`' for b in bad))
        row['deviation'] = line
    append(d, row)
    if line:
        print(f'redck: {line}', file=sys.stderr)
    return 0


def deviation_lines(target):
    """The process deviation lines recorded for a task, records or step dir (see deviations in the docstring):
    audit rows of red-checkpoint.jsonl, then a legacy process-deviations.md, per dir, the records dir first and then
    each live step-<n>/ under it in step order, whose lines carry "step-<n>: ". Reads only; a missing dir gives []."""
    d = order.records_dir(target)
    dirs = [d]
    with contextlib.suppress(OSError):
        steps_ = [c for c in d.iterdir() if c.is_dir() and re.fullmatch(r'step-\d+', c.name)]
        dirs += sorted(steps_, key=lambda c: int(c.name.split('-')[1]))
    out, seen = [], set()
    for x in dirs:
        prefix = '' if x == d else f'{x.name}: '
        found = []
        with contextlib.suppress(OSError, UnicodeError):
            for e in entries(x):
                if e.get('type') == 'audit' and e.get('status') in DEVIATING:
                    found.append(e.get('deviation') or
                                 f'process deviation: red-checkpoint: {e.get("status")}: attempt {e.get("attempt_id") or "unbound"}')
            legacy = x / LEGACY_DEVIATIONS
            if legacy.is_file():
                found += [l for l in legacy.read_text(encoding='utf-8').splitlines() if l.startswith('process deviation:')]
        for l in found:
            if prefix + l not in seen:
                seen.add(prefix + l)
                out.append(prefix + l)
    return out


def cmd_deviations(target):
    for l in deviation_lines(target):
        print(l)
    return 0


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def selftest():
    misses = []
    os.environ.pop('SDLC_ATTEMPT_ID', None)

    def check(name, cond):
        if cond:
            print(f'ok: {name}')
        else:
            misses.append(name)

    def git(top, *a):
        subprocess.run(['git', '-C', str(top), *a], check=True, capture_output=True)

    def ticket(*crit):
        return '---\nid: T-9\n---\n\n## Goal\ng\n\n## Acceptance criteria\n' + ''.join(f'{c}\n' for c in crit)

    with tempfile.TemporaryDirectory() as tmp:
        repo = pathlib.Path(tmp).resolve() / 'repo'
        repo.mkdir()
        git(repo, 'init', '-q')
        git(repo, 'config', 'user.email', 't@t')
        git(repo, 'config', 'user.name', 't')
        (repo / 'README').write_text('r\n')
        (repo / '.gitignore').write_text('')
        git(repo, 'add', '-A')
        git(repo, 'commit', '-qm', 'base')
        count = [0]

        def task(*crit):
            count[0] += 1
            d = repo / '.sdlc' / 'runtime' / 'tasks' / f't{count[0]}' / 'step-1'  # a records-side step dir is its own records dir
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(ticket(*crit), encoding='utf-8')
            return d

        def lines(d):
            return run_main(['deviations', str(d)])[1].splitlines()

        def devs(d):
            return [l for l in lines(d) if l.startswith('process deviation: red-checkpoint: ')]

        red = '- (red) `test -f out.txt`'
        # records dir: a task folder holding only handoff.md records its checkpoint in order.records_dir, not beside it
        tf = repo / '.sdlc' / 'tf'
        tf.mkdir(parents=True)
        (tf / 'handoff.md').write_text(ticket(red), encoding='utf-8')
        rc, _, _ = run_main(['record', str(tf), '--attempt-id', 'A1'])
        check('(records dir) record writes red-checkpoint.jsonl in order.records_dir, not in the task folder',
              rc == 0 and len(entries(order.records_dir(tf))) == 1 and not (tf / CHECKPOINT).exists()
              and order.records_dir(tf) == repo / '.sdlc' / 'runtime' / 'tasks' / 'tf')
        # no tagged criteria
        d = task('- `test -d .sdlc`', '- (guard) `test -d .sdlc`')
        rc, out, _ = run_main(['record', str(d), '--attempt-id', 'A1'])
        rc2, out2, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('no tagged criteria: record and audit say so, write no checkpoint and no deviation',
              rc == 0 and 'no (red) criteria' in out and rc2 == 0 and 'audit: none' in out2
              and not (d / CHECKPOINT).exists() and lines(d) == [])

        # valid pre-edit control, then the edit
        d = task(red)
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        (repo / 'out.txt').write_text('x\n')
        rc2, out2, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('valid pre-edit control: recorded red, bound to attempt, hash, base, and exact criterion; audit ok, no deviation',
              rc == 0 and len(e) == 1 and e[0]['phase'] == 'pre-edit' and e[0]['result'] == 'red' and e[0]['exit'] != 0
              and e[0]['attempt_id'] == 'A1' and e[0]['handoff_sha256'] == sha256(d / 'handoff.md')
              and e[0]['base_sha'] == steps.base_sha(str(repo), d) and e[0]['criterion'] == red and e[0]['span'] == 'test -f out.txt'
              and rc2 == 0 and out2.rstrip().endswith('audit: ok') and devs(d) == [])
        # the same attempt id with the edit already made records nothing new for another attempt
        # missing evidence (control: out.txt exists now, the criterion is green; no record was made for t3)
        d3 = task(red)
        rc, out, err = run_main(['audit', str(d3), '--attempt-id', 'A1'])
        rc_b, out_b, _ = run_main(['audit', str(d3), '--attempt-id', 'A1'])
        check('missing evidence: audit records one process-deviation line (idempotent) and exits 0',
              rc == 0 and out.rstrip().endswith('audit: missing') and len(devs(d3)) == 1 and 'missing' in devs(d3)[0]
              and lines(d3) == devs(d3) and 'test -f out.txt' in devs(d3)[0] and rc_b == 0 and len(devs(d3)) == 1)
        (repo / 'out.txt').unlink()

        # green at baseline is surfaced, never a red control
        d = task('- (red) `test -f README`')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        rc2, out2, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('green on the baseline: record exits 1 naming it, audit green-baseline deviation',
              rc == 1 and 'is green now; it cannot detect the change' in err and entries(d)[0]['result'] == 'green'
              and out2.rstrip().endswith('audit: green-baseline') and len(devs(d)) == 1)

        # post-edit retrospective control
        d = task(red)
        (repo / 'src.txt').write_text('edit first\n')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        rc2, out2, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('post-edit control: phase retrospective with the dirty paths, record exits 0 saying so, audit retrospective deviation',
              rc == 0 and e[0]['phase'] == 'retrospective' and 'src.txt' in e[0]['dirty'] and 'retrospective' in err
              and out2.rstrip().endswith('audit: retrospective') and len(devs(d)) == 1 and 'retrospective' in devs(d)[0])

        # resumed work: original from attempt A1, base control from attempt A2
        (repo / 'src.txt').unlink()
        d = task(red)
        run_main(['record', str(d), '--attempt-id', 'A1'])
        (repo / 'src.txt').write_text('a1 work\n')
        rcr, _, errr = run_main(['record', str(d), '--attempt-id', 'A2'])
        rc2, out2, _ = run_main(['audit', str(d), '--attempt-id', 'A2'])
        rc3, out3, _ = run_main(['audit', str(d), '--attempt-id', 'A3'])
        check('resumed work: the earlier original is preserved, the later base control is retrospective, no deviation',
              rcr == 0 and [x['phase'] for x in entries(d) if x.get('type') == 'control'] == ['pre-edit', 'retrospective']
              and 'preserved (original from attempt A1)' in out2 and out2.rstrip().endswith('audit: preserved')
              and out3.rstrip().endswith('audit: preserved') and devs(d) == [])
        # controls: the evidence must bind to the handoff hash, the base, and an attempt id
        (d / 'handoff.md').write_text(ticket('- (red) `test -f other.txt`'), encoding='utf-8')
        _, out4, _ = run_main(['audit', str(d), '--attempt-id', 'A2'])
        check('a criterion changed after the original checkpoint no longer binds it or the later control (control)',
              out4.rstrip().endswith('audit: missing') and len(devs(d)) == 1)
        (d / 'handoff.md').write_text(ticket(red, '- extra line', '- (guard) `git diff --name-only | grep -vxF -e a`'), encoding='utf-8')
        _, out4b, _ = run_main(['audit', str(d), '--attempt-id', 'A2'])
        check('T-0425: other handoff lines changed (a widen), the criterion and span intact: the controls still bind',
              out4b.rstrip().endswith('audit: preserved') and len(devs(d)) == 1)
        (d / 'handoff.md').write_text(ticket(red), encoding='utf-8')
        subprocess.run(['git', '-C', str(repo), 'commit', '-q', '--allow-empty', '-m', 'move'], check=True, capture_output=True)
        head = subprocess.run(['git', '-C', str(repo), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
        (d / 'base-sha').write_text(head + '\n')
        _, out5, _ = run_main(['audit', str(d), '--attempt-id', 'A3'])
        check('T-0473: base moved to HEAD, no A3 control: the A1 original on an ancestor base is preserved',
              out5.rstrip().endswith('audit: preserved'))
        (repo / 'src.txt').unlink()
        d = task(red)
        run_main(['record', str(d), '--attempt-id', ''])
        _, out6, err6 = run_main(['audit', str(d), '--attempt-id', ''])
        check('an unbound control (no attempt id) is never accepted (control)', out6.rstrip().endswith('audit: missing') and 'unbound' in err6)

        # attempt id resolved from a running builder attempt record
        d = task(red)
        (d / 'builder-L1.attempt.json').write_text(json.dumps(dict(attempt_id='AX', role='builder', status='running', started_at='2026-01-01T00:00:00Z')))
        (d / 'builder-L1-2.attempt.json').write_text(json.dumps(dict(attempt_id='AY', role='builder', status='running', started_at='2026-01-02T00:00:00Z')))
        old = os.environ.pop('SDLC_ATTEMPT_ID', None)
        run_main(['record', str(d)])
        check('attempt id: the newest running builder attempt record names the control', entries(d)[0]['attempt_id'] == 'AY')
        if old is not None:
            os.environ['SDLC_ATTEMPT_ID'] = old

        # ordering is read from the records only: a fabricated report line or a later green run changes nothing
        d = task(red)
        (d / 'builder-L1.md').write_text('## Status\ndone\n## Notes\nran the (red) command first\n')
        (repo / 'out.txt').write_text('x\n')
        run_main(['record', str(d), '--attempt-id', 'A1'])
        _, out7, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('control: a report claiming red-first and a later baseline run do not make a pre-edit record',
              out7.rstrip().endswith('audit: retrospective'))
        (repo / 'out.txt').unlink()

        # declared test prelude (T-0395): a declared test, and only that, is a prelude and not an implementation edit
        impl = '- (red) `test -f impl.txt`'
        (repo / 'tests').mkdir(exist_ok=True)

        def clean():
            for n in ('impl.txt', 'src.txt', 'tests/a.sh', 'tests/b.sh'):
                (repo / n).unlink(missing_ok=True)
        clean()
        d = task(impl, '- tests: `tests/a.sh`')
        (repo / 'tests' / 'a.sh').write_text('test -f impl.txt\n')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        (repo / 'impl.txt').write_text('x\n')
        rc2, out2, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('declared new test, implementation untouched: records pre-edit with the test sha256, audit ok',
              rc == 0 and len(e) == 1 and e[0]['phase'] == 'pre-edit' and e[0]['result'] == 'red' and e[0]['dirty'] == []
              and e[0].get('prelude') == {'tests/a.sh': sha256(repo / 'tests' / 'a.sh')}
              and out2.rstrip().endswith('audit: ok') and devs(d) == [])
        (repo / 'tests' / 'a.sh').write_text('test -f impl.txt && true\n')
        rc3, out3, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('a declared test whose content changes after recording fails the later green binding (control)',
              out3.rstrip().endswith('audit: prelude-changed') and len(devs(d)) == 1 and 'tests/a.sh' in devs(d)[0])
        clean()
        d = task(impl, 'tests: tests/a.sh')
        (repo / 'tests' / 'a.sh').write_text('test -f impl.txt\n')
        (repo / 'src.txt').write_text('implementation\n')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        check('a declared test plus one source edit is retrospective, the source path is the dirty one',
              rc == 0 and e[0]['phase'] == 'retrospective' and e[0]['dirty'] == ['src.txt'] and 'tests/a.sh' in e[0].get('prelude', {}))
        clean()
        d = task(impl, 'tests: tests/a.sh')
        (repo / 'tests' / 'b.sh').write_text('test -f impl.txt\n')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        check('an undeclared new test is retrospective (control: tests/ is no blanket ignore)',
              rc == 0 and e[0]['phase'] == 'retrospective' and e[0]['dirty'] == ['tests/b.sh'] and not e[0].get('prelude'))
        clean()
        d = task(impl, 'tests: ../outside.sh, tests/*.sh, /abs/x.sh, tests/')
        (repo / 'tests' / 'a.sh').write_text('t\n')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        check('an unsafe tests: entry (.., glob, absolute, directory) declares nothing, so the new file is an edit',
              e[0]['phase'] == 'retrospective' and not e[0].get('prelude') and 'tests:' in err)
        clean()
        # T-0486: untracked stdout/stderr capture files at the repo root are launcher output, not edits
        d = task(impl)
        (repo / 'builder.out').write_text('o\n')
        (repo / 'builder.err').write_text('e\n')
        (repo / 'src.out').mkdir(exist_ok=True)
        (repo / 'src.out' / 'x.txt').write_text('x\n')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        check('root-level builder.out and builder.err captures do not make the control retrospective; a nested .out dir file still does',
              rc == 0 and e[0]['phase'] == 'retrospective' and e[0]['dirty'] == ['src.out/x.txt'])
        (repo / 'src.out' / 'x.txt').unlink(); (repo / 'src.out').rmdir()
        d = task(impl)
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        check('only builder.out and builder.err present: pre-edit, nothing dirty',
              rc == 0 and e[0]['phase'] == 'pre-edit' and e[0]['dirty'] == [])
        (repo / 'builder.out').unlink(); (repo / 'builder.err').unlink()
        clean()

        # T-0425: the control keys to its own criterion and span, not to the whole handoff hash
        (repo / 'out.txt').unlink(missing_ok=True)
        scope = '- (guard) `git diff --name-only | grep -vxF -e a.txt`'
        r1, r2 = '- (red) `test -f one.txt`', '- (red) `test -f two.txt`'
        d = task(r1, r2, scope)
        run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        (repo / 'one.txt').write_text('x\n')
        (repo / 'two.txt').write_text('x\n')
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('criterion hash: each control stores criterion_sha256 beside handoff_sha256, and audit is ok',
              len(e) == 2 and all(x['criterion_sha256'] == criterion_hash(x['criterion'], x['span']) and x['handoff_sha256'] for x in e)
              and e[0]['criterion_sha256'] != e[1]['criterion_sha256'] and o.rstrip().endswith('audit: ok'))
        (d / 'handoff.md').write_text(ticket(r1, r2, scope.replace('a.txt`', 'a.txt -e b.txt`')) + '\n## Scope widened\n- `b.txt`: allowed\n', encoding='utf-8')
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('T-0425: a widen that adds a path to the scope span leaves every control valid, no deviation',
              o.rstrip().endswith('audit: ok') and devs(d) == [] and sha256(d / 'handoff.md') != e[0]['handoff_sha256'])
        (d / 'handoff.md').write_text(ticket(r1, '- (red) `test -f two.txt || false`', scope), encoding='utf-8')
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('T-0425: editing one criterion invalidates only that control (control)',
              o.count('audit: ok') == 1 and o.count('audit: missing') == 2 and len(devs(d)) == 1 and 'two.txt || false' in devs(d)[0]
              and 'test -f one.txt' not in devs(d)[0])
        # an old-format entry (no criterion_sha256) still binds on the whole handoff hash
        for n in ('one.txt', 'two.txt'):
            (repo / n).unlink(missing_ok=True)
        d = task(r1)
        run_main(['record', str(d), '--attempt-id', 'A1'])
        old_e = [{k: v for k, v in x.items() if k != 'criterion_sha256'} for x in entries(d)]
        (d / CHECKPOINT).write_text(''.join(json.dumps(x) + '\n' for x in old_e), encoding='utf-8')
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('T-0425: an old-format entry (handoff hash only) still verifies as before', o.rstrip().endswith('audit: ok') and devs(d) == [])
        (d / 'handoff.md').write_text(ticket(r1, '- extra line'), encoding='utf-8')
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('T-0425: an old-format entry still goes stale when the handoff changes (control)', o.rstrip().endswith('audit: missing'))

        rc, out, err = run_main(['record', str(repo / '.sdlc' / 'nope')])
        check('a missing handoff exits 1 with a message', rc == 1 and 'no handoff' in err)

        # shared handoff in the primary checkout, builder in an owned lane worktree (T-0420)
        lane = repo.parent / 'lane'
        git(repo, 'worktree', 'add', '-q', '-b', 'lane', str(lane))
        (repo / 'primary-dirty.txt').write_text('p\n')
        d = task(red)
        here = os.getcwd()
        try:
            os.chdir(lane)
            rc, out, err = run_main(['record', str(d), '--attempt-id', 'A1'])
        finally:
            os.chdir(here)
        e = entries(d)
        check('shared handoff, cwd in the lane: controls are pre-edit (clean lane) and the entry names the lane tree',
              rc == 0 and len(e) == 1 and e[0]['phase'] == 'pre-edit' and e[0]['tree'] == str(lane.resolve()))
        rc, out, err = run_main(['record', str(task(red)), '--attempt-id', 'A1'])
        check('same handoff from the primary alone: unchanged, retrospective on the primary tree',
              rc == 0 and 'retrospective' in err)
        (repo / 'primary-dirty.txt').unlink()

        # T-0473: the phase is read against HEAD and a control binds on an ancestor base; these cases commit, so they
        # run in their own repo and leave the shared one untouched
        r2 = pathlib.Path(tmp).resolve() / 'repo2'
        r2.mkdir()
        git(r2, 'init', '-q')
        git(r2, 'config', 'user.email', 't@t')
        git(r2, 'config', 'user.name', 't')
        (r2 / 'README').write_text('r\n')
        git(r2, 'add', '-A')
        git(r2, 'commit', '-qm', 'base')

        def head2():
            return subprocess.run(['git', '-C', str(r2), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()

        def task2(*crit):
            count[0] += 1
            d = r2 / '.sdlc' / 'runtime' / 'tasks' / f't{count[0]}' / 'step-1'
            d.mkdir(parents=True)
            (d / 'handoff.md').write_text(ticket(*crit), encoding='utf-8')
            return d

        # T1: A1 records at the base, its work is committed, A3 records at a clean tree on the new HEAD
        d = task2(red)
        (d / 'base-sha').write_text(head2() + '\n')
        run_main(['record', str(d), '--attempt-id', 'A1'])
        (r2 / 'src.txt').write_text('a1 work\n')
        git(r2, 'add', 'src.txt')
        git(r2, 'commit', '-qm', 'a1 work')
        rc, out, err = run_main(['record', str(d), '--attempt-id', 'A3'])
        e = [x for x in entries(d) if x.get('type') == 'control']
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A3'])
        check('T-0473: base kept, A1 work committed: the A3 record is pre-edit at a clean tree and stores at_sha',
              rc == 0 and len(e) == 2 and e[-1]['phase'] == 'pre-edit' and e[-1].get('at_sha') == head2()
              and o.rstrip().endswith('audit: ok'))

        # T3: a control whose base is a parentless commit (not an ancestor of HEAD) does not bind
        d = task2(red)
        run_main(['record', str(d), '--attempt-id', 'A1'])
        tree = subprocess.run(['git', '-C', str(r2), 'rev-parse', 'HEAD^{tree}'], capture_output=True, text=True).stdout.strip()
        orphan = subprocess.run(['git', '-C', str(r2), 'commit-tree', tree, '-m', 'orphan'], capture_output=True, text=True).stdout.strip()
        moved = [dict(x, base_sha=orphan) for x in entries(d)]
        (d / CHECKPOINT).write_text(''.join(json.dumps(x) + '\n' for x in moved), encoding='utf-8')
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A3'])
        check('T-0473: a control whose base is not an ancestor of HEAD is not bound (control)',
              bool(orphan) and o.rstrip().endswith('audit: missing'))

        # T4: A1 red at B0, out.txt committed, base moved to the new HEAD, A3 records green
        d = task2(red)
        run_main(['record', str(d), '--attempt-id', 'A1'])
        (r2 / 'out.txt').write_text('x\n')
        git(r2, 'add', 'out.txt')
        git(r2, 'commit', '-qm', 'out')
        (d / 'base-sha').write_text(head2() + '\n')
        rc, _, _ = run_main(['record', str(d), '--attempt-id', 'A3'])
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A3'])
        check('T-0473: an own pre-edit green defers to an earlier same-lineage pre-edit red: preserved',
              rc == 1 and o.rstrip().endswith('audit: preserved'))
        git(r2, 'rm', '-q', 'out.txt')
        git(r2, 'commit', '-qm', 'rm out')

        # T5: out.txt committed after the base before any record: a green pre-edit control, no earlier red
        d = task2(red)
        (d / 'base-sha').write_text(head2() + '\n')
        (r2 / 'out.txt').write_text('x\n')
        git(r2, 'add', 'out.txt')
        git(r2, 'commit', '-qm', 'out again')
        run_main(['record', str(d), '--attempt-id', 'A1'])
        e = entries(d)
        _, o, _ = run_main(['audit', str(d), '--attempt-id', 'A1'])
        check('T-0473: work committed after the base with no earlier red is green-baseline (control)',
              len(e) == 1 and e[0]['phase'] == 'pre-edit' and e[0]['result'] == 'green' and o.rstrip().endswith('audit: green-baseline'))

        # T-0543: the audit writes no side file; deviations reads the audit rows (and a legacy file) back
        check('(T-0543) audit writes no process-deviations.md',
              not any(repo.rglob(LEGACY_DEVIATIONS)) and not any(r2.rglob(LEGACY_DEVIATIONS)))
        td = repo / '.sdlc' / 'runtime' / 'tasks' / 'dv'
        for n in (2, 1):
            sd = td / f'step-{n}'
            sd.mkdir(parents=True)
            (sd / 'handoff.md').write_text(ticket(red), encoding='utf-8')
            run_main(['audit', str(sd), '--attempt-id', f'S{n}'])
            run_main(['audit', str(sd), '--attempt-id', f'S{n}'])
        (td / 'step-1' / 'handoff.md').write_text(ticket(red, '- (red) `test -f two.txt`'), encoding='utf-8')
        run_main(['audit', str(td / 'step-1'), '--attempt-id', 'S1'])
        (td / 'step-1.superseded-1').mkdir()
        (td / 'step-1.superseded-1' / CHECKPOINT).write_text(json.dumps(dict(type='audit', status='missing', attempt_id='OLD')) + '\n')
        (td / CHECKPOINT).write_text(json.dumps(dict(type='audit', status='missing', attempt_id='')) + '\n'
                                     + json.dumps(dict(type='audit', status='ok', attempt_id='Z')) + '\n')
        (td / 'step-2' / LEGACY_DEVIATIONS).write_text('# Process deviations\nprocess deviation: red-checkpoint: missing: attempt L\n')
        rc, out, err = run_main(['deviations', str(td)])
        got = out.splitlines()
        rows = [e for e in entries(td / 'step-1') + entries(td / 'step-2') if e.get('type') == 'audit']
        check('(T-0543) deviations prints one line per deviating audit row',
              rc == 0 and len(got) == 5 and got[0] == 'process deviation: red-checkpoint: missing: attempt unbound'
              and got[1].startswith('step-1: process deviation: red-checkpoint: missing: attempt S1, handoff sha256 ')
              and got[2].startswith('step-1: ') and '2 of 2' in got[2] and got[1] != got[2]
              and got[3].startswith('step-2: process deviation: red-checkpoint: missing: attempt S2, ')
              and got[4] == 'step-2: process deviation: red-checkpoint: missing: attempt L'
              and all(r.get('deviation') for r in rows) and 'OLD' not in out and deviation_lines(td) == got
              and not (td / LEGACY_DEVIATIONS).exists() and run_main(['deviations', str(td / 'nope')])[:2] == (0, ''))

    if misses:
        print('redck selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('redck selftest: PASS')
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog='redck.py', description=__doc__.split('\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('record', help='run the handoff (red) spans before the first edit and append the controls')
    p.add_argument('target', help='a handoff.md or its dir')
    p.add_argument('--attempt-id', default='', help='the attempt (default SDLC_ATTEMPT_ID, else the newest running builder attempt record)')
    p.add_argument('--timeout', type=float, default=steps.DEFAULT_GUARD_TIMEOUT, help='seconds per span (default 300)')
    p = sub.add_parser('audit', help='judge a completed build against its recorded controls; record a process deviation when it lacks them')
    p.add_argument('target', help='a handoff.md or its dir')
    p.add_argument('--attempt-id', default='', help='the completed attempt (default as record)')
    p = sub.add_parser('deviations', help='print the process deviation lines recorded for a task, records or step dir')
    p.add_argument('dir', help='a task, records or step dir')
    sub.add_parser('selftest', help='prove every status and the binding controls')
    a = ap.parse_args(argv)
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'deviations':
        return cmd_deviations(a.dir)
    if a.cmd == 'record':
        return cmd_record(a.target, a.attempt_id, a.timeout)
    return cmd_audit(a.target, a.attempt_id)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
