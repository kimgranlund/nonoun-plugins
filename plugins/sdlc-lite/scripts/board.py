#!/usr/bin/env python3
"""Render the sdlc status board from task dirs. Never compose the board by hand.

Usage: board.py [--root DIR] [--task SLUG] [--waiting LINE] [--summary] [--sort MODE] [--lanes] [selftest]
  --root     dir holding task dirs (default: .sdlc in the cwd; bench/results works too)
  --task     only this task
  --waiting  one line saying what the session waits on, printed above the table
  --summary  one compact line for the status line (newest task only; writes no state):
             "<task> <pct>% (<passed>/<steps>)", plus "🔴<n>" for blocked/failed steps and
             "⚠ L5" when a step is on the last builder level. Prints nothing if no tasks.
  --lanes    a per-worktree table instead of the task board (see Lanes below)
  selftest   render temp fixtures with and without ticket front matter; prove the column gate bites

Lanes: --lanes renders | Lane | Branch | Board |, one row per `git worktree list` entry of the
root's repo, in list order: Lane is the worktree's basename, Branch its branch (or
"(detached <sha>)"), and Board the --summary line of that worktree's same-relative root (or
"no tasks"). When the repo has lane worktrees besides the main one, five ledger columns follow
(a repo with only the main worktree keeps the three-column table): Base (the lane's recorded base
sha, from its base-sha file or solo dispatch file, 7 chars), Stale (`yes` when that base is not an
ancestor of the main worktree's HEAD), Verifier (the newest verifier verdict: pass, fail, inherited,
or none), Merge (the lane's merge class from steps.merge_class, `rolling` or `integration (<reason>)`,
with the hash-bound globs from the main worktree's config and the lane's committed, uncommitted and
untracked paths since its fork point; T-0374) and Owner (the backend of the lane's newest run record,
claude or codex). A lane's own task is a task dir whose run record the main
worktree lacks; a lane with none shows `-`, and the main row shows `-` throughout. It never renders the task board or touches the state file; --waiting still prints
above it and --summary, --task and --sort are ignored. Outside a git work tree (any git
failure) it prints "<root>: not inside a git work tree" on stderr and exits 1. The default board
is unchanged.

A task dir is .sdlc/<task>/ with planner-L*.md and step-<n>/ subdirs (see skills/handoff-format),
or also .sdlc/tickets/<task>/ when .sdlc/config has a `ticket_root: tickets` line, and also
.sdlc/work/<task>/ (tasks with no ticket) when it has `layout: topics` too (an unsupported
ticket_root or layout value is ignored: the board lists root tasks only and never fails on config).
A step dir replaced by a replan is renamed step-<n>.superseded-<k>/: it is ignored for step rows
and the --summary L5 check, but its cost and recorded work still count.
Status is derived from files only: <role>-<level>.md (done), <role>-<level>.running (live),
the builder's "## Status", the verifier's "## Verdict" (a verifier with no pass/fail verdict renders
as 🟡 no verdict, rerun verify; two or more in a row after the newest build render as 🟡 stop,
ask the user, matching steps.py next), and runs.jsonl (cost). A rerun at the same
level writes <role>-<level>-<k>.md (run.sh never overwrites); the newest is the last in
runs.jsonl record order (order.py), never file time.
A builder whose Status starts with "inherited red" (a gate main already made red) renders as
🔴 inherited red · builder <level>, ask the user, and --summary counts it in 🔴<n>.
A newest verifier after the build whose Verdict starts with "inherited red:" renders as
🔴 inherited red · builder <level> · verifier <level>, ask the user; it counts as a verdict, so it
breaks a no-verdict run.
A step whose newest build a task-dir verifier lists under ## Verified with Verdict pass
(steps.batch_verified, the same rule steps.py next uses) renders as
🟢 pass · builder <level> · batch verifier <level>.

Ticket columns: when at least one rendered task's handoff.md has ticket front matter (read with
tickets.py's parser, for display only), the table becomes | ID | Task | Ticket | Step | Status | % |,
where ID is the ticket id and Ticket its status, or `<status> · <area>` when the ticket has a non-empty
`area:` (area_of; ticket_of keeps its (id, status) tuple); a task without front matter (or with an unreadable
handoff.md) gets empty cells there. With no front matter anywhere the table stays
| Task | Step | Status | % |. --summary never shows ticket fields.

Budget column: when at least one rendered ticket has a valid `budget_usd` (budget.py report, the only
spend and ceiling logic), the table becomes | ID | Task | Ticket | Budget | Step | Status | % |, with
the cell `$<spend>/$<ceiling> <percent>%` and an empty cell for a task with no budget. With no budget
anywhere the output is unchanged, byte for byte.

% ladder: 0 queued, 10 building, 50 built, 70 verifying, 100 verifier pass.
A changed row ends with "· changed" (compared with a per-root state file in
$SDLC_BOARD_STATE_DIR, else ${XDG_CACHE_HOME:-~/.cache}/sdlc-lite/board-state;
never inside the repo). A legacy <root>/.board-state.json left by older versions gets a one-line
"safe to delete" hint in the full board (never in --summary); board.py never touches it.
"""
import argparse, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile

import tickets  # same scripts/ dir: the only front matter parser
import order  # same scripts/ dir: recorded run order for result files
import steps  # same scripts/ dir: the batch verification rule (steps.batch_verified)
import budget  # same scripts/ dir: per-ticket spend and ceiling (budget.report)

LADDER = {'queued': 0, 'building': 10, 'built': 50, 'verifying': 70, 'verified': 100}


def section(md: pathlib.Path, heading: str) -> str:
    """First non-empty line under '## <heading>', lowercased."""
    lines = md.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.strip() == f'## {heading}':
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip().lower()
    return ''


def by_level(d: pathlib.Path, role: str, ext: str):
    if ext == 'md':
        return [pathlib.Path(p) for p in order.ordered(d, role)]
    def key(p):
        m = re.match(r'[a-z]+-L(\d+)', p.name)
        return (int(m.group(1)) if m else 0, p.name)
    return sorted(d.glob(f'{role}-L*.{ext}'), key=key)


def live_step_dirs(task: pathlib.Path):
    """step-<n>/ dirs only; superseded dirs (step-<n>.superseded-<k>/) are left out."""
    return [d for d in task.glob('step-*') if d.is_dir() and re.fullmatch(r'step-\d+', d.name)]


def cost(d: pathlib.Path, est=None) -> float:
    """Total cost_usd under a task; when est is a list, the cost_estimated part is appended to it."""
    total = 0.0
    # step-* on purpose: superseded dirs still count toward cost.
    for f in [d / 'runs.jsonl', *d.glob('step-*/runs.jsonl')]:
        if f.exists():
            for line in f.read_text().splitlines():
                try:
                    rec = json.loads(line)
                    c = rec.get('cost_usd') or 0
                    total += c
                    if est is not None and rec.get('cost_estimated') is True:
                        est.append(c)
                except json.JSONDecodeError:
                    pass
    return total


def level_of(p: pathlib.Path) -> str:
    """The L<n> token of a result file: builder-L3.md and builder-L3-2.md (a rerun) give L3."""
    m = re.search(r'-(L\d)(?:-\d+)?$', p.stem)
    return m.group(1) if m else p.stem.split('-')[-1]


def step_row(step: pathlib.Path, title: str, planned_level: str):
    builds, verifies = by_level(step, 'builder', 'md'), by_level(step, 'verifier', 'md')
    attempts = len(json_lines(step / 'runs.jsonl', 'builder'))
    tries = f' · attempt {attempts}' if attempts > 1 else ''
    if by_level(step, 'builder', 'running'):
        lvl = level_of(by_level(step, 'builder', 'running')[-1])
        return '🟡', f'building · builder {lvl}{tries}', LADDER['building']
    if by_level(step, 'verifier', 'running'):
        lvl = level_of(by_level(step, 'verifier', 'running')[-1])
        return '🟡', f'verifying · verifier {lvl}{tries}', LADDER['verifying']
    if not builds:
        return '⏳', f'queued · planned {planned_level}', LADDER['queued']
    last_build = builds[-1]
    if section(last_build, 'Status').startswith('blocked'):
        return '🔴', f'blocked · builder {level_of(last_build)}{tries}', LADDER['building']
    if section(last_build, 'Status').startswith('inherited red'):
        return '🔴', f'inherited red · builder {level_of(last_build)}, ask the user{tries}', LADDER['building']
    if verifies and order.counts_after(verifies[-1], last_build):
        verdict = section(verifies[-1], 'Verdict')
        if verdict.startswith('pass'):
            return '🟢', f'pass · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}{tries}', LADDER['verified']
        if verdict.startswith('fail'):
            return '🔴', f'fail · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}{tries}', LADDER['built']
        if verdict.startswith('inherited red:'):
            return '🔴', f'inherited red · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}, ask the user{tries}', LADDER['built']
        n = 0
        for w in map(pathlib.Path, reversed(order.ordered(step, 'verifier'))):
            if not order.counts_after(w, last_build):
                continue
            if section(w, 'Verdict').startswith(('pass', 'fail', 'inherited red:')):
                break
            n += 1
        if n >= 2:
            return '🟡', f'stop · no verdict x{n} · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}, ask the user{tries}', LADDER['built']
        return '🟡', f'no verdict · builder {level_of(last_build)} · verifier {level_of(verifies[-1])}, rerun verify{tries}', LADDER['built']
    bv = steps.batch_verified(step)
    if bv:
        return '🟢', f'pass · builder {level_of(last_build)} · batch verifier {level_of(pathlib.Path(bv))}{tries}', LADDER['verified']
    return '🟡', f'built · builder {level_of(last_build)}, awaiting verify{tries}', LADDER['built']


def json_lines(f: pathlib.Path, role: str):
    if not f.exists():
        return []
    out = []
    for line in f.read_text().splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get('role') == role:
            out.append(j)
    return out


def plan_steps(task: pathlib.Path):
    """Steps from step-<n>/handoff.md (rewritten by /chain on a replan), else from the newest plan."""
    dirs = sorted((d for d in live_step_dirs(task) if (d / 'handoff.md').exists()),
                  key=lambda d: int(d.name[5:]))
    if dirs:
        steps = []
        for d in dirs:
            text = (d / 'handoff.md').read_text()
            m = re.search(r'^## Step (\d+): (.+)$', text, re.M)
            lvl = re.search(r'^level:\s*(L\d)', text, re.M)
            n = int(d.name.split('-')[1])
            steps.append((n, m.group(2).strip() if m else d.name, lvl.group(1) if lvl else '?'))
        return steps
    plans = by_level(task, 'planner', 'md')
    if not plans:
        return []
    text = plans[-1].read_text()
    steps = []
    for m in re.finditer(r'^## Step (\d+): (.+)$', text, re.M):
        body = text[m.end():]
        lvl = re.search(r'^level:\s*(L\d)', body, re.M)
        steps.append((int(m.group(1)), m.group(2).strip(), lvl.group(1) if lvl else '?'))
    return steps


def solo_lane(task: pathlib.Path) -> bool:
    """True when the last `- lane:` line in the task's skips.md is solo."""
    try:
        lanes = re.findall(r'^- lane:\s*(\S+)', (task / 'skips.md').read_text(encoding='utf-8'), re.M)
    except OSError:
        return False
    return bool(lanes) and lanes[-1] == 'solo'


def orphaned_attempts(task: pathlib.Path):
    """Attempts of a running dispatch whose parent died (dispatch.py status --orphans); display-only, never fails."""
    if not any(task.glob('*.attempt.json')):
        return []
    try:
        import dispatch
        return dispatch.status(task, True)
    except Exception:
        return []


def task_rows(task: pathlib.Path):
    rows = []
    running = [p for p in task.glob('*.running')]
    steps = plan_steps(task)
    front = ticket_of(task)
    if not running and front is not None and front[1] == 'done' and solo_lane(task):
        # A merged, closed solo lane keeps its step folder; its builder row is not the ticket's state.
        return [(task.name, 'task', '🟢', 'closed', 100)], []
    if running and orphaned_attempts(task):
        rows.append((task.name, 'task', '🟡', 'orphaned · resume', 0))
    elif running:
        role_lvl = running[-1].stem
        rows.append((task.name, 'task', '🟡', f'running · {role_lvl}', 0))
    elif not steps:
        front = ticket_of(task)
        if front is not None and front[1] == 'done':
            rows.append((task.name, 'task', '🟢', 'closed', 100))
        else:
            rows.append((task.name, 'task', '⏳', 'not planned', 0))
    for n, title, lvl in steps:
        glyph, status, pct = step_row(task / f'step-{n}', title, lvl)
        rows.append((task.name, f'{n}. {title}', glyph, status, pct))
    grade = task / 'grade.md'
    if grade.exists():
        hidden = re.search(r'hidden_check:\s*(\w+)', grade.read_text())
        if hidden:
            ok = hidden.group(1) == 'pass'
            rows.append((task.name, 'hidden check', '🟢' if ok else '🔴', hidden.group(1), 100 if ok else 0))
    return rows, steps


def task_dirs(root: pathlib.Path):
    """Dirs directly under root holding a handoff.md, plus those directly under the ticket dir
    when tickets.ticket_dir(root) is not root, plus those under the work dir when
    tickets.layout_paths(root) puts it elsewhere (`layout: topics`: ticket-less tasks live in
    <root>/work). An unsupported ticket_root or layout value (tickets.Fail) counts root only:
    the board is display-only and never fails on config."""
    def under(d):
        return [c for c in d.iterdir() if c.is_dir() and (c / 'handoff.md').exists()] if d.is_dir() else []
    found = under(root)
    try:
        td = tickets.ticket_dir(root)
    except tickets.Fail:
        return found
    if td != root:
        found += under(td)
    try:
        work = tickets.layout_paths(root).work
    except tickets.Fail:
        return found
    if work != root:
        found += under(work)
    return found


def summary(root: pathlib.Path) -> str:
    if not root.is_dir():
        return ''
    tasks = task_dirs(root)
    if not tasks:
        return ''
    t = max(tasks, key=lambda d: max((p.stat().st_mtime for p in d.rglob('*')), default=0))
    rows, steps = task_rows(t)
    step_rows = [r for r in rows if r[1] not in ('task', 'hidden check')]
    if not step_rows:
        if any(t.glob('*.running')):
            return f'{t.name} planning'
        front = ticket_of(t)
        return f'{t.name} closed' if front is not None and front[1] == 'done' else f'{t.name} not planned'
    pct = sum(r[4] for r in step_rows) // len(step_rows)
    passed = sum(1 for r in step_rows if r[2] == '🟢')
    parts = [f'{t.name} {pct}% ({passed}/{len(step_rows)})']
    bad = sum(1 for r in step_rows if r[2] == '🔴')
    if bad:
        parts.append(f'🔴{bad}')
    if any(any(d.glob('builder-L5.*')) for d in live_step_dirs(t)):
        parts.append('⚠ L5')
    return ' · '.join(parts)


def ticket_of(task: pathlib.Path):
    """(id, status) from the task's ticket front matter, or None when it has none.
    Any read or parse error counts as no front matter: a bad file must not break the board."""
    try:
        meta = tickets.parse((task / 'handoff.md').read_text(encoding='utf-8'))
    except Exception:
        return None
    if not isinstance(meta, dict):
        return None
    return tuple(v if isinstance(v, str) else '' for v in (meta.get('id'), meta.get('status')))


def area_of(task: pathlib.Path) -> str:
    """The ticket's non-empty string `area:` from its front matter, stripped, else ''. Any read or parse
    error counts as no area. Kept apart from ticket_of, whose (id, status) tuple other scripts use."""
    try:
        meta = tickets.parse((task / 'handoff.md').read_text(encoding='utf-8'))
    except Exception:
        return ''
    a = meta.get('area') if isinstance(meta, dict) else None
    return a.strip() if isinstance(a, str) else ''


def budget_cell(task: pathlib.Path) -> str:
    """'$<spend>/$<ceiling> <percent>%' from budget.report, or '' with no budget or on any error."""
    try:
        r = budget.report(task)
    except Exception:
        return ''
    if not r:
        return ''
    return f"${r['spend']:.2f}/${budget.fmt(r['budget'])} {r['percent']}%"


def has_step_work(task: pathlib.Path) -> bool:
    """True when the task has any recorded step work: a planner-L*.md, a step-*/handoff.md,
    or a *.running file. The step-* glob is on purpose: a superseded dir's handoff still counts."""
    return bool(list(task.glob('planner-L*.md')) or list(task.glob('step-*/handoff.md'))
                or list(task.glob('*.running')))


# Board visibility per ticket status. A new status in tickets.ENUMS['status'] must be
# classified in exactly one of these sets; selftest() fails until it is.
ALWAYS_HIDDEN = frozenset({'dropped'})
HIDDEN_WITHOUT_STEP_WORK = frozenset({'done'})
ALWAYS_SHOWN = frozenset({'proposed', 'ready', 'claimed', 'paused', 'blocked'})


def belongs_on_board(task: pathlib.Path) -> bool:
    """False only when the task has ticket front matter and is dropped, or done with no
    recorded step work. Everything else (no front matter, other statuses, or done with
    step work) stays visible."""
    front = ticket_of(task)
    if front is None:
        return True
    _, status = front
    if status in ALWAYS_HIDDEN:
        return False
    if status in HIDDEN_WITHOUT_STEP_WORK and not has_step_work(task):
        return False
    return True  # ALWAYS_SHOWN, and any unknown status, stays visible


def unclassified_statuses(known, sets=None):
    """Problems with the board visibility sets against `known` statuses: a known status in
    no set, a status in two sets, or a classified status not in `known`. Empty means OK."""
    if sets is None:
        sets = {'ALWAYS_HIDDEN': ALWAYS_HIDDEN,
                'HIDDEN_WITHOUT_STEP_WORK': HIDDEN_WITHOUT_STEP_WORK,
                'ALWAYS_SHOWN': ALWAYS_SHOWN}
    problems = []
    classified = frozenset().union(*sets.values())
    for s in sorted(set(known) - classified):
        problems.append(f'status {s!r} is not classified in any board visibility set')
    names = list(sets)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for s in sorted(sets[a] & sets[b]):
                problems.append(f'status {s!r} is in both {a} and {b}')
    for s in sorted(classified - set(known)):
        problems.append(f'status {s!r} is classified but not a known status')
    return problems


def sort_tasks(tasks, mode='recent'):
    """Order task dirs: 'recent' by mtime, 'name' by folder name, 'id' by the numeric part
    of the ticket id with tasks lacking an id after, by folder name. 'auto' (what main()
    uses with no --sort when any rendered task has a ticket) is 'id' except that tasks
    lacking an id follow by mtime."""
    if mode == 'name':
        return sorted(tasks, key=lambda t: t.name)
    if mode in ('id', 'auto'):
        def key(t):
            front = ticket_of(t)
            m = re.search(r'T-(\d+)', front[0]) if front else None
            if m:
                return (0, int(m.group(1)), 0, t.name)
            return (1, 0, t.stat().st_mtime if mode == 'auto' else 0, t.name)
        return sorted(tasks, key=key)
    return sorted(tasks, key=lambda d: d.stat().st_mtime)


def state_path(root: pathlib.Path) -> pathlib.Path:
    """Where render() keeps the last statuses for root: outside the working tree."""
    d = os.environ.get('SDLC_BOARD_STATE_DIR')
    if d:
        base = pathlib.Path(d)
    else:
        cache = os.environ.get('XDG_CACHE_HOME') or os.path.expanduser('~/.cache')
        base = pathlib.Path(cache) / 'sdlc-lite' / 'board-state'
    key = hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:16]
    return base / f'{key}.json'


def render(root: pathlib.Path, tasks, waiting=None) -> str:
    state_file = state_path(root)
    try:
        old = json.loads(state_file.read_text())
    except (OSError, json.JSONDecodeError):
        old = {}
    fronts = {t: ticket_of(t) for t in tasks}
    with_ticket = any(f is not None for f in fronts.values())
    budgets = {t: budget_cell(t) if fronts[t] is not None else '' for t in tasks}
    with_budget = any(budgets.values())
    new, out = {}, []
    if waiting:
        out.append(waiting)
        out.append('')
    if with_budget:
        out.append('| ID | Task | Ticket | Budget | Step | Status | % |')
        out.append('|---|---|---|---|---|---|---|')
    elif with_ticket:
        out.append('| ID | Task | Ticket | Step | Status | % |')
        out.append('|---|---|---|---|---|---|')
    else:
        out.append('| Task | Step | Status | % |')
        out.append('|---|---|---|---|')
    total_cost, est_cost, pcts = 0.0, [], []
    for t in tasks:
        rows, steps = task_rows(t)
        total_cost += cost(t, est_cost)
        tid, tstatus = fronts[t] or ('', '')
        area = area_of(t) if fronts[t] is not None else ''
        if area:
            tstatus = f'{tstatus} · {area}'
        for task, step, glyph, status, pct in rows:
            key = f'{task}/{step}'
            cell = f'{glyph} {status}'
            new[key] = cell
            changed = ' · changed' if old and old.get(key) != cell else ''
            if with_budget:
                out.append(f'| {tid} | {task} | {tstatus} | {budgets[t]} | {step} | {cell}{changed} | {pct} |')
            elif with_ticket:
                out.append(f'| {tid} | {task} | {tstatus} | {step} | {cell}{changed} | {pct} |')
            else:
                out.append(f'| {task} | {step} | {cell}{changed} | {pct} |')
            if step not in ('task', 'hidden check'):
                pcts.append(pct)
    if pcts:
        out.append('')
        out.append(f'{sum(pcts) // len(pcts)}% across {len(pcts)} steps · ${total_cost:.2f} spent' + (f' (~${sum(est_cost):.2f} estimated)' if est_cost else ''))
    legacy = root / '.board-state.json'
    if legacy.exists():  # read-only hint; never delete or modify it
        out.append('')
        out.append(f'Note: legacy {legacy} is no longer used '
                   '(the board cache moved to a per-user dir); safe to delete.')
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(new, indent=1))
    except OSError:
        pass
    return '\n'.join(out)


LEDGER_COLS = ['Base', 'Stale', 'Verifier', 'Merge', 'Owner']


def lane_ledger(root: pathlib.Path, main_root, main_head: str, git) -> list:
    """[Base, Stale, Verifier, Merge, Owner] cells for one lane worktree, read-only. The lane's own
    tasks are the task dirs holding a run record (base-sha, *.dispatch.json, runs.jsonl) that the
    main worktree's same task dir lacks; the last by name decides. Base is the recorded base sha
    (7 chars), Stale `yes` when it is not an ancestor of main's HEAD, Verifier the newest verifier
    verdict (pass, fail, inherited, or none), Merge the merge class (steps.merge_class over that
    verdict, a stale base, and the paths declared in main's config that the lane worktree changed
    since its fork point, untracked files included), Owner the backend of the newest run record. A
    lane with no record shows `-` for Base, Stale and Owner, and its base is its fork point."""
    def own(d, name):
        f = d / name
        return f.is_file() and not (main_root / d.relative_to(root) / name).is_file()

    mine = [d for d in sorted(task_dirs(root))
            if own(d, 'base-sha') or own(d, 'runs.jsonl') or any(own(d, f.name) for f in d.glob('*.dispatch.json'))]
    base = owner = '-'
    verdict, held = 'none', ''
    if mine:
        d = mine[-1]
        sha = ''
        f = d / 'base-sha'
        if f.is_file():
            lines = f.read_text(encoding='utf-8', errors='replace').split()
            sha = lines[0] if lines else ''
        for df in sorted(d.glob('*.dispatch.json')):
            if sha:
                break
            try:
                rec = json.loads(df.read_text(encoding='utf-8'))
                sha = str(rec.get('base_sha') or '').strip() if rec.get('role') == 'solo' else ''
            except (OSError, ValueError, AttributeError):
                sha = ''
        if sha:
            base = sha[:7]
        backend = ''
        f = d / 'runs.jsonl'
        if f.is_file():
            for line in f.read_text(encoding='utf-8', errors='replace').splitlines():
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if isinstance(rec, dict):
                    backend = str(rec.get('backend') or 'claude')
        owner = backend or 'claude'  # a record with no backend field is a Claude run
        for where in [d] + sorted(c for c in d.glob('step-*') if c.is_dir())[::-1]:
            v = order.newest(where, 'verifier')
            if v and steps.verdict_or_none(v):
                verdict = steps.verdict_or_none(v)
                held = steps.held_note(v) if verdict == 'fail' else ''
                break
    stale = '-'
    if base != '-':
        try:
            git('rev-parse', '-q', '--verify', sha + '^{commit}')
            git('merge-base', '--is-ancestor', sha, main_head)
            stale = 'no'
        except ValueError:
            stale = 'yes'
    try:
        tree = pathlib.Path(git('-C', str(root), 'rev-parse', '--show-toplevel').strip())
        fork = git('-C', str(tree), 'merge-base', main_head, 'HEAD').strip()
        hits = steps.declared_hits(tree, tickets.hash_bound_globs(main_root), fork, untracked=True)
        cls, why = steps.merge_class(verdict, sha if stale == 'yes' else '', hits, held)
        merge = f'{cls} ({why})' if why else cls
    except ValueError:  # an unreadable lane tree: no class rather than a guess
        merge = '?'
    return [base, stale, verdict, merge, owner]


def lanes(root: pathlib.Path) -> str:
    """One row per `git worktree list` entry of root's repo: Lane (worktree basename), Branch,
    and Board, that worktree's summary() of the same-relative root. Raises ValueError outside
    a git work tree or on any git failure."""
    here = root.resolve()
    anchor = here
    while not anchor.is_dir() and anchor != anchor.parent:
        anchor = anchor.parent
    env = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}

    def git(*args):
        try:
            p = subprocess.run(['git', '-C', str(anchor), *args], env=env, capture_output=True, text=True)
        except OSError as e:
            raise ValueError(str(e))
        if p.returncode:
            raise ValueError(p.stderr.strip())
        return p.stdout

    top = pathlib.Path(git('rev-parse', '--show-toplevel').strip()).resolve()
    try:
        rel = here.relative_to(top)
    except ValueError:
        raise ValueError(f'{here} is outside the git toplevel {top}')
    entries = []
    for line in git('worktree', 'list', '--porcelain').splitlines():
        if line.startswith('worktree '):
            entries.append({'path': line[len('worktree '):]})
        elif entries and line.startswith('HEAD '):
            entries[-1]['head'] = line[len('HEAD '):]
        elif entries and line.startswith('branch '):
            entries[-1]['branch'] = line[len('branch '):]
    ledger = len(entries) > 1  # a repo with no lane worktrees keeps the three-column table
    cols = ['Lane', 'Branch', 'Board'] + (LEDGER_COLS if ledger else [])
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    main_head = entries[0].get('head', '') if entries else ''
    main_root = (pathlib.Path(entries[0]['path']).resolve() / rel).resolve() if entries else None
    for i, e in enumerate(entries):
        path = pathlib.Path(e['path']).resolve()
        ref = e.get('branch', '')
        if ref.startswith('refs/heads/'):
            branch = ref[len('refs/heads/'):]
        elif ref:
            branch = ref
        else:
            branch = f"(detached {e.get('head', '')[:7]})"
        board = summary((path / rel).resolve()) or 'no tasks'
        cells = [path.name, branch, board]
        if ledger:
            cells += ['-'] * len(LEDGER_COLS) if i == 0 else lane_ledger(
                (path / rel).resolve(), main_root, main_head, git)
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)


def selftest() -> int:
    misses = []

    def expect(label, cond):
        if not cond:
            misses.append(label)

    front = ('---\nid: T-0042\ntitle: "Fixture"\ntype: chore\nstatus: ready\nsize: S\n'
             'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n')

    def task_dir(root, name, content):
        d = root / name
        d.mkdir(parents=True)
        h = d / 'handoff.md'
        h.write_bytes(content) if isinstance(content, bytes) else h.write_text(content, encoding='utf-8')
        return d

    saved_state_dir = os.environ.get('SDLC_BOARD_STATE_DIR')
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as state_tmp:
        tmp = pathlib.Path(tmp)
        state_dir = pathlib.Path(state_tmp)
        # Outside every fixture root; subprocess runs inherit it.
        os.environ['SDLC_BOARD_STATE_DIR'] = str(state_dir)

        def clear_state():
            for f in state_dir.glob('*.json'):
                f.unlink(missing_ok=True)

        # 1. No task has front matter: today's 4-column table, byte for byte.
        plain = tmp / 'plain'
        t = task_dir(plain, 'plain-task', '## Goal\nno front matter\n')
        got = render(plain, [t])
        want = '| Task | Step | Status | % |\n|---|---|---|---|\n| plain-task | task | ⏳ not planned | 0 |'
        expect(f'no front matter renders the 4-column table byte for byte, got {got!r}', got == want)

        # 1b. Budget column: absent with no budget_usd anywhere (6-column table byte for byte),
        # present once one ticket has budget_usd; a task without a budget gets an empty cell.
        nob = tmp / 'nob'
        t = task_dir(nob, 'ticketed', front)
        (t / 'runs.jsonl').write_text('{"role":"builder","cost_usd":4,"attempt_id":"a1"}\n')
        got = render(nob, [t])
        expect(f'budget column: absent when no ticket has budget_usd, got {got!r}',
               got == '| ID | Task | Ticket | Step | Status | % |\n|---|---|---|---|---|---|\n'
                      '| T-0042 | ticketed | ready | task | ⏳ not planned | 0 |')
        wb = tmp / 'wb'
        tb = task_dir(wb, 'budgeted', front.replace('created: 2026-01-01\n', 'created: 2026-01-01\nbudget_usd: 10\n'))
        (tb / 'runs.jsonl').write_text('{"role":"builder","cost_usd":8.5,"attempt_id":"a1"}\n')
        tn = task_dir(wb, 'unbudgeted', front)
        tp = task_dir(wb, 'bare', '## Goal\nno front matter\n')
        lines = render(wb, [tb, tn, tp]).splitlines()
        expect(f'budget column: present when a ticket has budget_usd, got {lines!r}',
               lines[:2] == ['| ID | Task | Ticket | Budget | Step | Status | % |', '|---|---|---|---|---|---|---|']
               and '| T-0042 | budgeted | ready | $8.50/$10 85% | task | ⏳ not planned | 0 |' in lines
               and '| T-0042 | unbudgeted | ready |  | task | ⏳ not planned | 0 |' in lines
               and '|  | bare |  |  | task | ⏳ not planned | 0 |' in lines)

        # 2. Front matter mixed with no front matter and an undecodable handoff.md.
        mixed = tmp / 'mixed'
        ts = [task_dir(mixed, 'ticketed', front),
              task_dir(mixed, 'bare', '## Goal\nno front matter\n'),
              task_dir(mixed, 'broken', b'---\nid: \xff\xfe\n---\n')]
        try:
            got = render(mixed, ts)
        except Exception as e:
            got = ''
            expect(f'mixed render crashed: {e!r}', False)
        lines = got.splitlines()
        expect(f'mixed render has the 6-column header, got {lines[:1]}',
               lines[:2] == ['| ID | Task | Ticket | Step | Status | % |', '|---|---|---|---|---|---|'])
        expect('ticketed row shows its id and status',
               '| T-0042 | ticketed | ready | task | ⏳ not planned | 0 |' in lines)
        expect('bare row has empty ID and Ticket cells', '|  | bare |  | task | ⏳ not planned | 0 |' in lines)
        expect('undecodable handoff.md row has empty ID and Ticket cells',
               '|  | broken |  | task | ⏳ not planned | 0 |' in lines)

        # 3. tickets.parse raising counts as no front matter and does not crash.
        raising = tmp / 'raising'
        t = task_dir(raising, 'raises', front)
        real = tickets.parse

        def boom(text):
            raise ValueError('fixture parse failure')
        tickets.parse = boom
        try:
            got = render(raising, [t])
        except Exception as e:
            got = ''
            expect(f'render crashed when tickets.parse raised: {e!r}', False)
        finally:
            tickets.parse = real
        expect(f'tickets.parse raising falls back to the 4-column table, got {got!r}',
               got == '| Task | Step | Status | % |\n|---|---|---|---|\n| raises | task | ⏳ not planned | 0 |')

        # 4. --summary ignores front matter.
        solo = tmp / 'solo'
        task_dir(solo, 'ticketed', front)
        got = summary(solo)
        expect(f'summary unchanged by front matter, got {got!r}', got == 'ticketed not planned')

        # 5. Dropped/done filter: dropped is hidden regardless of steps; done is hidden only
        # without step work; other statuses (e.g. proposed) stay visible without over-filtering.
        gate = tmp / 'gate'

        def front_with(status):
            return ('---\nid: T-0099\ntitle: "Fixture"\ntype: chore\nstatus: %s\nsize: S\n'
                    'priority: P2\ndepends: []\ncreated: 2026-01-01\n---\n\n## Goal\nx\n') % status

        dropped_no_steps = task_dir(gate, 'dropped-no-steps', front_with('dropped'))
        dropped_with_plan = task_dir(gate, 'dropped-with-plan', front_with('dropped'))
        (dropped_with_plan / 'planner-L1.md').write_text('## Plan\n')
        done_no_steps = task_dir(gate, 'done-no-steps', front_with('done'))
        done_with_plan = task_dir(gate, 'done-with-plan', front_with('done'))
        (done_with_plan / 'planner-L1.md').write_text('## Plan\n')
        done_with_step = task_dir(gate, 'done-with-step', front_with('done'))
        (done_with_step / 'step-1').mkdir()
        (done_with_step / 'step-1' / 'handoff.md').write_text('## Step 1: x\nlevel: L1\n')
        proposed_no_steps = task_dir(gate, 'proposed-no-steps', front_with('proposed'))

        expect('dropped ticket with no steps is hidden', not belongs_on_board(dropped_no_steps))
        expect('dropped ticket with a planner file is still hidden',
               not belongs_on_board(dropped_with_plan))
        expect('done ticket with no steps is hidden', not belongs_on_board(done_no_steps))
        expect('done ticket with a planner file is shown', belongs_on_board(done_with_plan))
        expect('done ticket with a step handoff is shown', belongs_on_board(done_with_step))
        expect('proposed ticket with no steps is still shown', belongs_on_board(proposed_no_steps))

        # 5b. Same gate fixture through main()'s actual task selection (subprocess), not just
        # belongs_on_board() in isolation: proves the filter is wired into main(), not just defined.
        proc = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), '--root', str(gate)],
                               capture_output=True, text=True)
        out = proc.stdout
        expect(f'main() subprocess exited 0, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 0)
        expect('main() output hides dropped-no-steps', 'dropped-no-steps' not in out)
        expect('main() output hides dropped-with-plan', 'dropped-with-plan' not in out)
        expect('main() output hides done-no-steps', 'done-no-steps' not in out)
        expect('main() output shows done-with-plan', 'done-with-plan' in out)
        expect('main() output shows done-with-step', 'done-with-step' in out)
        expect('main() output shows proposed-no-steps', 'proposed-no-steps' in out)

        # 5c. A done ticket with step work but no plan renders as closed, not 'not planned';
        # the same fixture at status ready is the control that still reads 'not planned'.
        for status, word in (('done', 'closed'), ('ready', 'not planned')):
            croot = tmp / f'closed-{status}'
            ct = task_dir(croot, 'shipped', front.replace('status: ready', f'status: {status}'))
            (ct / 'step-1').mkdir()
            (ct / 'step-1' / 'builder-L1.md').write_text('## Status\ndone\n')
            crows, _ = task_rows(ct)
            task_status = [r[3] for r in crows if r[1] == 'task']
            expect(f'{status} ticket with no plan renders {word!r}, got {task_status!r}',
                   task_status == [word])
            if status == 'done':
                expect('done ticket with no plan has no not planned row',
                       not any(r[3] == 'not planned' for r in crows))
                expect('closed row is green at 100',
                       ('shipped', 'task', '🟢', 'closed', 100) in crows)
            got = summary(croot)
            expect(f'{status} ticket summary reads shipped {word}, got {got!r}',
                   got == f'shipped {word}')

        # 5d. A done ticket whose last skips.md lane is solo reads closed even with a step folder
        # (T-0300); the same fixture at status ready is the control that still reads built.
        for status, want in (('done', ['closed']), ('ready', ['built · builder L2, awaiting verify'])):
            sroot = tmp / f'solo-lane-{status}'
            st = task_dir(sroot, 'soloed', front.replace('status: ready', f'status: {status}'))
            (st / 'skips.md').write_text('## Lane\n- lane: solo\n')
            (st / 'runs.jsonl').write_text('{"role": "solo"}\n')
            (st / 'step-1').mkdir()
            (st / 'step-1' / 'handoff.md').write_text('## Step 1: do it\nlevel: L2\n')
            (st / 'step-1' / 'builder-L2.md').write_text('## Status\ndone\n')
            srows, _ = task_rows(st)
            got = [r[3] for r in srows]
            expect(f'solo lane {status} ticket reads {want!r}, got {got!r}', got == want)

        # 6. --sort through main(): id ignores mtime, unticketed tasks follow by name,
        # name is alphabetical. With no flag, a root with tickets sorts by id with
        # unticketed tasks after by mtime; a root without tickets equals --sort recent.
        def ticket_front(tid):
            return front.replace('T-0042', tid)

        def run_main(root, *extra):
            proc = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                                   '--root', str(root), *extra], capture_output=True, text=True)
            expect(f'main() {extra} exited 0, got {proc.returncode} stderr={proc.stderr!r}',
                   proc.returncode == 0)
            return proc.stdout

        def order(out, names):
            return sorted((n for n in names if f'| {n} |' in out), key=lambda n: out.index(f'| {n} |'))

        srt = tmp / 'sort'
        made = [task_dir(srt, 'zulu-three', ticket_front('T-0003')),
                task_dir(srt, 'yankee-two', ticket_front('T-0002')),
                task_dir(srt, 'bravo', '## Goal\nno front matter\n'),
                task_dir(srt, 'alpha', '## Goal\nno front matter\n')]
        for i, d in enumerate(made):
            os.utime(d, (1_000_000 + i * 100, 1_000_000 + i * 100))
        names = [d.name for d in made]
        got = order(run_main(srt, '--sort', 'id'), names)
        expect(f'--sort id puts T-0002 before T-0003, then unticketed by name, got {got}',
               got == ['yankee-two', 'zulu-three', 'alpha', 'bravo'])
        got = order(run_main(srt, '--sort', 'name'), names)
        expect(f'--sort name is alphabetical, got {got}', got == sorted(names))
        got = order(run_main(srt, '--sort', 'recent'), names)
        expect(f'--sort recent is mtime order, got {got}', got == names)
        # Unticketed tasks follow by mtime: derive the expected order from the utime values.
        unticketed = sorted((d for d in made if d.name in ('alpha', 'bravo')),
                            key=lambda d: d.stat().st_mtime)
        want = ['yankee-two', 'zulu-three'] + [d.name for d in unticketed]
        got = order(run_main(srt), names)
        expect(f'no --sort with tickets is id then unticketed by mtime, want {want}, got {got}',
               got == want and want != ['yankee-two', 'zulu-three', 'alpha', 'bravo'])

        plain = tmp / 'sort-plain'
        pmade = [task_dir(plain, 'charlie', '## Goal\nno front matter\n'),
                 task_dir(plain, 'alpha', '## Goal\nno front matter\n'),
                 task_dir(plain, 'bravo', '## Goal\nno front matter\n')]
        for i, d in enumerate(pmade):
            os.utime(d, (1_000_000 + i * 100, 1_000_000 + i * 100))
        pnames = [d.name for d in pmade]
        got = order(run_main(plain), pnames)
        expect(f'no --sort without tickets is mtime order, got {got}', got == pnames)
        # The state file adds ' · changed' markers between runs; compare with it removed.
        clear_state()
        default = run_main(plain)
        clear_state()
        expect('no --sort without tickets equals --sort recent',
               default == run_main(plain, '--sort', 'recent'))

        # 5b. Renders write nothing under the root, and "· changed" still works.
        clean = tmp / 'clean'
        ct = task_dir(clean, 'clean-task', '## Goal\nx\n')
        before = sorted(p for p in clean.rglob('*'))
        first = render(clean, [ct])
        (ct / 'planner-L1.running').touch()
        second = render(clean, [ct])
        after = sorted(p for p in clean.rglob('*') if p.name != 'planner-L1.running')
        expect('render writes no .board-state.json under the root',
               not list(clean.rglob('.board-state.json')))
        expect(f'render creates no file under the root, got {set(after) - set(before)}',
               after == before)
        expect(f'first render has no changed marker, got {first!r}', '· changed' not in first)
        expect(f'a status change between renders shows "· changed", got {second!r}',
               '· changed' in second)
        expect('two roots get different state paths',
               state_path(clean) != state_path(plain) and state_path(clean).parent == state_dir)

        # 5c. A legacy <root>/.board-state.json gets a hint, is never touched, and --summary ignores it.
        (ct / 'planner-L1.running').unlink()
        ot = task_dir(clean, 'orph', '# o\n')
        dead = subprocess.Popen([sys.executable, '-c', 'pass'])
        dead.wait()
        (ot / 'builder-L1.running').write_text('1\n')
        attempt = ot / 'builder-L1.attempt.json'
        for pid, want in ((dead.pid, 'orphaned · resume'), (os.getpid(), 'running · builder-L1')):
            attempt.write_text(json.dumps({'status': 'running', 'backend': 'claude', 'role': 'builder', 'level': 'L1', 'parent_pid': pid}))
            got = task_rows(ot)[0][0]
            expect(f'a running dispatch with parent {pid} renders {want}, got {got}', got and got[2:4] == ('🟡', want))
        no_hint = render(clean, [ct])
        sum_without = summary(clean)
        expect(f'no legacy file means no hint, got {no_hint!r}', 'safe to delete' not in no_hint)
        legacy = clean / '.board-state.json'
        legacy.write_bytes(b'{"old": 1}')
        with_hint = render(clean, [ct])
        expect(f'legacy file gets the hint, got {with_hint!r}',
               '.board-state.json' in with_hint and 'safe to delete' in with_hint)
        expect('render leaves the legacy file bytes unchanged', legacy.read_bytes() == b'{"old": 1}')
        expect('summary is unchanged by the legacy file', summary(clean) == sum_without)
        legacy.unlink()

        # 5d. Numbered reruns (run.sh writes <role>-<level>-<k>.md): level_of keeps the L<n>
        # token, and the newest file wins for plans and builds.
        expect(f"level_of(builder-L3-2.md) is L3, got {level_of(pathlib.Path('builder-L3-2.md'))!r}",
               level_of(pathlib.Path('builder-L3-2.md')) == 'L3')
        expect(f"level_of(planner-L3.md) is L3, got {level_of(pathlib.Path('planner-L3.md'))!r}",
               level_of(pathlib.Path('planner-L3.md')) == 'L3')
        rerun = tmp / 'rerun'
        rp = task_dir(rerun, 'replanned', '## Goal\nx\n')
        (rp / 'planner-L3.md').write_text('## Step 1: a\nlevel: L1\n## Step 2: b\nlevel: L2\n')
        (rp / 'planner-L3-2.md').write_text('## Step 1: only\nlevel: L2\n')
        os.utime(rp / 'planner-L3.md', (1_000_000, 1_000_000))
        os.utime(rp / 'planner-L3-2.md', (1_000_100, 1_000_100))
        got = plan_steps(rp)
        expect(f'plan_steps takes the newer planner-L3-2.md, got {got}', got == [(1, 'only', 'L2')])
        rb = task_dir(rerun, 'rebuilt', '## Goal\nx\n')
        st = rb / 'step-1'
        st.mkdir()
        (st / 'builder-L3.md').write_text('## Status\nblocked\n')
        (st / 'builder-L3-2.md').write_text('## Status\ndone\n')
        os.utime(st / 'builder-L3.md', (1_000_000, 1_000_000))
        os.utime(st / 'builder-L3-2.md', (1_000_100, 1_000_100))
        glyph, status, _ = step_row(st, 'x', 'L3')
        expect(f'newer builder-L3-2.md (done) renders built · builder L3, got {status!r}',
               status.startswith('built · builder L3') and 'blocked' not in status)

        # 5e. Superseded step dirs (step-<n>.superseded-<k>/) are not steps, but their cost
        # and recorded work still count.
        sup_root = tmp / 'superseded'
        sp = task_dir(sup_root, 'replanned-steps', '## Goal\nx\n')
        for name, title in (('step-1', 'one'), ('step-2', 'two'), ('step-2.superseded-1', 'old two')):
            (sp / name).mkdir()
            (sp / name / 'handoff.md').write_text(f'## Step {name[5]}: {title}\nlevel: L1\n')
        old = sp / 'step-2.superseded-1'
        (old / 'builder-L5.md').write_text('## Status\ndone\n')
        (old / 'runs.jsonl').write_text('{"role": "builder", "cost_usd": 1.25}\n')
        got = plan_steps(sp)
        expect(f'plan_steps skips superseded dirs, got {got}',
               got == [(1, 'one', 'L1'), (2, 'two', 'L1')])
        got = render(sup_root, [sp])
        step_lines = [ln for ln in got.splitlines() if re.search(r'\| \d+\. ', ln)]
        expect(f'board has exactly two step rows, got {step_lines}', len(step_lines) == 2)
        got = summary(sup_root)
        expect(f'summary ignores builder-L5 in a superseded dir, got {got!r}', '⚠ L5' not in got)
        expect(f'cost includes the superseded dir, got {cost(sp)}', abs(cost(sp) - 1.25) < 1e-9)
        only_old = task_dir(sup_root, 'only-superseded', '## Goal\nx\n')
        (only_old / 'step-1.superseded-1').mkdir()
        (only_old / 'step-1.superseded-1' / 'handoff.md').write_text('## Step 1: x\nlevel: L1\n')
        expect('has_step_work counts a handoff in a superseded dir', has_step_work(only_old))

        # 5f. Dot-prefixed closed ticket folders (.NNNN-slug) are ordinary tasks to the board.
        dot = tmp / 'dot'
        closed = task_dir(dot, '.0003-closed-work', front_with('done').replace('T-0099', 'T-0003'))
        (closed / 'planner-L1.md').write_text('## Plan\n')
        task_dir(dot, '.0004-closed-bare', front_with('done').replace('T-0099', 'T-0004'))
        task_dir(dot, '.0005-gone', front_with('dropped').replace('T-0099', 'T-0005'))
        task_dir(dot, '0002-open', front_with('ready').replace('T-0099', 'T-0002'))
        task_dir(dot, '0006-later', front_with('ready').replace('T-0099', 'T-0006'))
        (dot / '_templates').mkdir()
        (dot / '_templates' / 'feature.md').write_text(front)
        (dot / '.board-state.json').write_text('{}')
        out = run_main(dot)
        expect(f'dot folder with step work renders with ID T-0003, got {out!r}',
               '| T-0003 | .0003-closed-work |' in out)
        expect('done dot folder with no step work is hidden', '.0004-closed-bare' not in out)
        expect('dropped dot folder is hidden', '.0005-gone' not in out)
        expect('_templates produces no row', '_templates' not in out and 'feature' not in out)
        rows = [ln for ln in out.splitlines() if ln.startswith('| T-')]
        expect(f'.board-state.json produces no row, got {rows}',
               not any('board-state' in ln for ln in rows))
        got = order(out, ['0002-open', '.0003-closed-work', '0006-later'])
        expect(f'default sort puts the dot folder by its id, got {got}',
               got == ['0002-open', '.0003-closed-work', '0006-later'])
        one = run_main(dot, '--task', '.0003-closed-work')
        expect(f'--task .0003-closed-work renders that task alone, got {one!r}',
               '| T-0003 | .0003-closed-work |' in one and '0002-open' not in one
               and '0006-later' not in one)

    if saved_state_dir is None:
        os.environ.pop('SDLC_BOARD_STATE_DIR', None)
    else:
        os.environ['SDLC_BOARD_STATE_DIR'] = saved_state_dir

    # 6a. A ticket with an area shows `<status> · <area>` in the Ticket cell; one without stays `<status>`.
    with tempfile.TemporaryDirectory() as atmp:
        atmp = pathlib.Path(atmp)
        ar = atmp / 'areas'
        with_area = task_dir(ar, '0001-a', front.replace('T-0042', 'T-0001').replace(
            'status: ready\n', 'status: claimed\nclaimed_by: claude 2026-10-11\narea: ui-kit\n'))
        no_area = task_dir(ar, '0002-b', front.replace('T-0042', 'T-0002'))
        os.environ['SDLC_BOARD_STATE_DIR'] = str(atmp / 'state')  # keep the state file out of the user cache
        out = render(ar, [with_area, no_area])
        if saved_state_dir is None:
            os.environ.pop('SDLC_BOARD_STATE_DIR', None)
        else:
            os.environ['SDLC_BOARD_STATE_DIR'] = saved_state_dir
        expect(f'a ticket with an area shows status · area, got {out!r}',
               '| T-0001 | 0001-a | claimed · ui-kit |' in out)
        expect(f'a ticket without an area shows its bare status, got {out!r}',
               '| T-0002 | 0002-b | ready |' in out and 'ready ·' not in out)

    # 6. Every ticket status is classified for board visibility, and the guard bites.
    known = set(tickets.ENUMS['status'])
    probs = unclassified_statuses(known)
    expect(f'every ticket status has a board visibility class, got {probs}', probs == [])
    probs = unclassified_statuses(known | {'zz-new-status'})
    expect('an unclassified status is reported',
           any('zz-new-status' in p for p in probs))
    probs = unclassified_statuses(known, {'ALWAYS_HIDDEN': ALWAYS_HIDDEN,
                                          'HIDDEN_WITHOUT_STEP_WORK': HIDDEN_WITHOUT_STEP_WORK,
                                          'ALWAYS_SHOWN': ALWAYS_SHOWN,
                                          'EXTRA': frozenset({'dropped'})})
    expect('a status in two visibility sets is reported',
           any("'dropped'" in p and 'both' in p for p in probs))

    # 7. Verdicts follow runs.jsonl record order, never file times.
    with tempfile.TemporaryDirectory() as otmp:
        otmp = pathlib.Path(otmp)

        def step_fixture(name, runs, times=None):
            """runs: (role, level, file, body) in record order; times: {file: epoch}, else equal."""
            d = otmp / name / 'step-1'
            d.mkdir(parents=True)
            for role, level, f, body in runs:
                (d / f).write_text(body)
            (d / 'runs.jsonl').write_text(''.join(
                json.dumps({'role': r, 'level': lv, 'file': f}) + '\n' for r, lv, f, _ in runs))
            for p in d.iterdir():
                t = (times or {}).get(p.name, 1_700_000_000)
                os.utime(p, (t, t))
            return d

        built = '## Status\ndone\n'
        runs = [('builder', 'L1', 'builder-L1.md', built),
                ('verifier', 'L1', 'verifier-L1.md', '## Verdict\nfail\n'),
                ('builder', 'L2', 'builder-L2.md', built),
                ('verifier', 'L2', 'verifier-L2.md', '## Verdict\npass\n')]
        got = step_row(step_fixture('equal', runs), 'x', 'L1')[:2]
        expect(f'equal mtimes: record order gives the pass row, got {got}',
               got == ('🟢', 'pass · builder L2 · verifier L2 · attempt 2'))
        after = runs + [('builder', 'L2', 'builder-L2-2.md', built)]
        got = step_row(step_fixture('rebuild', after), 'x', 'L1')[:2]
        expect(f'equal mtimes: a build after the pass awaits verify, got {got}',
               got == ('🟡', 'built · builder L2, awaiting verify · attempt 3'))
        inverse = {f: 1_700_000_900 - 100 * i for i, (_, _, f, _) in enumerate(runs)}
        got = step_row(step_fixture('inverse', runs, inverse), 'x', 'L1')[:2]
        expect(f'inverse mtimes: record order still gives the pass row, got {got}',
               got == ('🟢', 'pass · builder L2 · verifier L2 · attempt 2'))
        novd = [('builder', 'L1', 'builder-L1.md', built),
                ('verifier', 'L1', 'verifier-L1.md', 'Nothing to do until the test gate reports.\n')]
        got = step_row(step_fixture('noverdict', novd), 'x', 'L1')[:2]
        ok = got[0] == '🟡' and got[1].startswith('no verdict') and 'rerun verify' in got[1]
        expect(f'a verifier with no verdict renders as 🟡 no verdict, rerun verify, got {got}', ok)
        if ok:
            print(f'ok: one no-verdict verifier: {got[1]}')
        nv = 'Nothing to do until the test gate reports.\n'
        novd2 = novd + [('verifier', 'L1', 'verifier-L1-2.md', nv)]
        got = step_row(step_fixture('noverdict2', novd2), 'x', 'L1')[:2]
        ok = got[0] == '🟡' and got[1].startswith('stop') and 'ask the user' in got[1]
        expect(f'two consecutive no-verdict verifiers render as stop, ask the user, got {got}', ok)
        if ok:
            print(f'ok: two no-verdict verifiers: {got[1]}')
        mixed = [('builder', 'L1', 'builder-L1.md', built),
                 ('verifier', 'L1', 'verifier-L1.md', nv),
                 ('verifier', 'L1', 'verifier-L1-2.md', '## Verdict\nfail\n'),
                 ('builder', 'L1', 'builder-L1-2.md', built),
                 ('verifier', 'L1', 'verifier-L1-3.md', nv)]
        got = step_row(step_fixture('noverdict-rebuild', mixed), 'x', 'L1')[:2]
        ok = got[1].startswith('no verdict') and 'rerun verify' in got[1]
        expect(f'no-verdict results before the newest build do not count, got {got}', ok)
        mixed2 = mixed + [('verifier', 'L1', 'verifier-L1-4.md', nv)]
        got = step_row(step_fixture('noverdict-rebuild2', mixed2), 'x', 'L1')[:2]
        ok = ok and got[1].startswith('stop · no verdict x2')
        expect(f'two no-verdict results after the newest build stop at x2, got {got}', ok)
        if ok:
            print(f'ok: fail then rebuild counts only later no-verdicts: {got[1]}')
        inh = [('builder', 'L2', 'builder-L2.md', '## Status\ninherited red: test_a\n')]
        got = step_row(step_fixture('inherited-red', inh), 'x', 'L2')[:2]
        expect(f'an inherited red builder renders as 🔴 inherited red, got {got}',
               got[0] == '🔴' and got[1].startswith('inherited red'))
        vinh = [('builder', 'L2', 'builder-L2.md', built),
                ('verifier', 'L1', 'verifier-L1.md', '## Verdict\ninherited red: test_a\n')]
        got = step_row(step_fixture('verifier-inherited-red', vinh), 'x', 'L2')[:2]
        expect(f'an inherited red verifier renders as 🔴 inherited red · builder · verifier, got {got}',
               got == ('🔴', 'inherited red · builder L2 · verifier L1, ask the user'))
        def batch_fixture(name, rebuilt):
            t = otmp / name
            for n in (1, 2):
                d = t / f'step-{n}'
                d.mkdir(parents=True)
                (d / 'handoff.md').write_text(f'## Step {n}: s{n}\nlevel: L2\n')
                (d / 'builder-L2.md').write_text('<!-- role=builder level=L2 model=opus effort=low -->\n' + built)
            if rebuilt:
                (t / 'step-1' / 'builder-L2-2.md').write_text('<!-- role=builder level=L2 model=opus effort=low -->\n' + built)
            (t / 'handoff.md').write_text('## Goal\ng\n')
            (t / 'verifier-L3.md').write_text('<!-- role=verifier level=L3 model=fable effort=xhigh -->\n'
                                              '## Verdict\npass\n\n## Verified\n- step-1/builder-L2.md\n')
            return t / 'step-1'
        got = step_row(batch_fixture('batch-pass', False), 'x', 'L2')[:2]
        expect(f'a batch-verified step renders as 🟢 pass · batch verifier, got {got}',
               got == ('🟢', 'pass · builder L2 · batch verifier L3'))
        print(f'ok: batch: listed newest build renders {got[1]}')
        got = step_row(batch_fixture('batch-rebuilt', True), 'x', 'L2')[:2]
        expect(f'a step rebuilt after the batch renders awaiting verify, got {got}',
               got[0] == '🟡' and got[1].startswith('built · builder L2, awaiting verify'))
        print(f'ok: batch: rebuilt after the batch renders {got[1]}')

    # 8. --lanes: one row per git worktree, each Board cell read from that worktree's own root.
    with tempfile.TemporaryDirectory() as ltmp:
        ltmp = pathlib.Path(ltmp).resolve()
        env = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}
        repo = ltmp / 'repo'
        (repo / '.sdlc' / 't').mkdir(parents=True)
        (repo / '.sdlc' / 't' / 'handoff.md').write_text('## Goal\nx\n')

        def git(*args):
            p = subprocess.run(['git', '-C', str(repo), *args], env=env, capture_output=True, text=True)
            expect(f'git {args} exited 0, got {p.returncode} stderr={p.stderr!r}', p.returncode == 0)

        git('init', '-q')
        git('config', 'user.name', 'board selftest')
        git('config', 'user.email', 'selftest@example.invalid')
        git('config', 'commit.gpgsign', 'false')
        git('add', '.sdlc/t/handoff.md')
        git('commit', '-q', '-m', 'fixture')
        lanes_dir = ltmp / 'lanes'
        git('worktree', 'add', '-q', '-b', 'alpha', str(lanes_dir / 'alpha'))
        git('worktree', 'add', '-q', '-b', 'beta', str(lanes_dir / 'beta'))
        (lanes_dir / 'alpha' / '.sdlc' / 't' / 'planner-L1.running').touch()
        head = subprocess.run(['git', '-C', str(repo), 'branch', '--show-current'], env=env,
                              capture_output=True, text=True).stdout.strip()

        def run_lanes(root):
            return subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                                   '--lanes', '--root', str(root)], env=env, capture_output=True, text=True)

        proc = run_lanes(repo / '.sdlc')
        expect(f'--lanes exited 0, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 0)
        lines = proc.stdout.splitlines()
        expect(f'--lanes header, got {lines[:2]}', lines[0].startswith('| Lane | Branch | Board | Base |') and lines[1].startswith('|---|'))
        data = [[c.strip() for c in ln.strip('|').split('|')] for ln in lines[2:] if ln.startswith('| ')]
        expect(f'--lanes has exactly three data rows, got {data}', len(data) == 3)
        cells = {r[0]: r for r in data if len(r) == 8}
        expect(f'--lanes rows are the main worktree first, then alpha and beta, got {[r[0] for r in data]}',
               sorted(r[0] for r in data) == ['alpha', 'beta', 'repo'] and data[0][0] == 'repo')
        expect(f'--lanes Branch cells are the branch names, got {[r[1] for r in data]}',
               {r[0]: r[1] for r in data} == {'repo': head, 'alpha': 'alpha', 'beta': 'beta'} and head)
        expect(f"alpha's Board reads its own running marker, got {cells.get('alpha')}",
               cells.get('alpha', [''] * 8)[2] == 't planning')
        expect(f"beta's Board is unchanged by alpha's marker, got {cells.get('beta')}",
               cells.get('beta', [''] * 8)[2] == 't not planned')
        expect(f"main's Board is unchanged by alpha's marker, got {cells.get('repo')}",
               cells.get('repo', [''] * 8)[2] == 't not planned')

        plain = ltmp / 'plain'
        plain.mkdir()
        proc = run_lanes(plain)
        expect(f'--lanes outside git exits 1 naming git, got {proc.returncode} stderr={proc.stderr!r}',
               proc.returncode == 1 and 'git' in proc.stderr and not proc.stdout)

    # 8b. --lanes ledger columns: base sha, stale-base flag, verifier verdict, merge class, owner.
    with tempfile.TemporaryDirectory() as ltmp:
        ltmp = pathlib.Path(ltmp).resolve()
        env = {k: v for k, v in os.environ.items() if k not in tickets.GIT_ENV_DROP}
        repo = ltmp / 'repo'
        (repo / '.sdlc' / 't').mkdir(parents=True)
        (repo / '.sdlc' / 't' / 'handoff.md').write_text('## Goal\nx\n')

        def git(*args, cwd=repo):
            p = subprocess.run(['git', '-C', str(cwd), *args], env=env, capture_output=True, text=True)
            expect(f'git {args} exited 0, got {p.returncode} stderr={p.stderr!r}', p.returncode == 0)
            return p.stdout.strip()

        git('init', '-q')
        git('config', 'user.name', 'board selftest')
        git('config', 'user.email', 'selftest@example.invalid')
        git('config', 'commit.gpgsign', 'false')
        git('add', '.sdlc/t/handoff.md')
        git('commit', '-q', '-m', 'fixture')
        base = git('rev-parse', 'HEAD')

        def run_lanes(root):
            return subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()),
                                   '--lanes', '--root', str(root)], env=env, capture_output=True, text=True)

        plain_out = run_lanes(repo / '.sdlc').stdout.splitlines()
        expect(f'--lanes with no lanes keeps the three-column table, got {plain_out}',
               plain_out[:2] == ['| Lane | Branch | Board |', '|---|---|---|'] and len(plain_out) == 3)

        git('checkout', '-q', '-b', 'side')
        (repo / 'side.txt').write_text('x')
        git('add', 'side.txt')
        git('commit', '-q', '-m', 'unmerged side work')
        orphan = git('rev-parse', 'HEAD')
        git('checkout', '-q', '-')
        lanes_dir = ltmp / 'lanes'
        for name in ('stale', 'verified', 'codex', 'genlane'):
            git('worktree', 'add', '-q', '-b', name, str(lanes_dir / name))
        # T-0374: the declared hash-bound list lives in the main worktree's config
        (repo / '.sdlc' / 'config').write_text('hash_bound: gen/*.json  # generated\n')
        # stale: its dispatch file recorded a base that main does not contain
        (lanes_dir / 'stale' / '.sdlc' / 't' / 'solo-L2-t.dispatch.json').write_text(
            json.dumps({'role': 'solo', 'base_sha': orphan}))
        # verified: a base-sha file at main's head and a passing task-dir verifier result
        (lanes_dir / 'verified' / '.sdlc' / 't' / 'base-sha').write_text(base + '\n')
        (lanes_dir / 'verified' / '.sdlc' / 't' / 'verifier-L2.md').write_text(
            '<!-- role=verifier level=L2 model=opus effort=high -->\n## Verdict\npass\n')
        # codex: its run record names the codex backend
        (lanes_dir / 'codex' / '.sdlc' / 't' / 'runs.jsonl').write_text(
            json.dumps({'role': 'solo', 'backend': 'codex', 'file': ''}) + '\n')
        # genlane: verified on main's head, but it writes a declared generated path (untracked so far)
        (lanes_dir / 'genlane' / '.sdlc' / 't' / 'base-sha').write_text(base + '\n')
        (lanes_dir / 'genlane' / '.sdlc' / 't' / 'verifier-L2.md').write_text(
            '<!-- role=verifier level=L2 model=opus effort=high -->\n## Verdict\npass\n')
        (lanes_dir / 'genlane' / 'gen').mkdir()
        (lanes_dir / 'genlane' / 'gen' / 'x.json').write_text('{}\n')

        proc = run_lanes(repo / '.sdlc')
        expect(f'--lanes ledger exited 0, got {proc.returncode} stderr={proc.stderr!r}', proc.returncode == 0)
        lines = proc.stdout.splitlines()
        head = ['Lane', 'Branch', 'Board', 'Base', 'Stale', 'Verifier', 'Merge', 'Owner']
        expect(f'--lanes ledger header, got {lines[:2]}',
               lines[:2] == ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)])
        rows = {}
        for ln in lines[2:]:
            cells = [c.strip() for c in ln.strip('|').split('|')]
            if len(cells) == len(head):
                rows[cells[0]] = dict(zip(head, cells))
        expect(f'--lanes ledger rows are repo, stale, verified, codex, genlane, got {list(rows)}',
               sorted(rows) == ['codex', 'genlane', 'repo', 'stale', 'verified'] and list(rows)[0] == 'repo')
        got = rows.get('stale', {})
        expect(f"stale lane shows its recorded base and Stale yes, got {got}",
               got.get('Base') == orphan[:7] and got.get('Stale') == 'yes' and got.get('Verifier') == 'none'
               and got.get('Merge') == f'integration (stale base {orphan[:7]})' and got.get('Owner') == 'claude')
        got = rows.get('verified', {})
        expect(f"verified lane shows base, Stale no, Verifier pass and Merge rolling, got {got}",
               got.get('Base') == base[:7] and got.get('Stale') == 'no' and got.get('Verifier') == 'pass'
               and got.get('Merge') == 'rolling')
        got = rows.get('codex', {})
        expect(f"codex lane shows Owner codex and, unverified, Merge integration, got {got}",
               got.get('Owner') == 'codex' and got.get('Merge') == 'integration (unverified)')
        got = rows.get('genlane', {})
        expect(f"a verified lane writing a declared path is Merge integration (hash-bound), got {got}",
               got.get('Verifier') == 'pass' and got.get('Stale') == 'no'
               and got.get('Merge') == 'integration (hash-bound gen/x.json)')
        got = rows.get('repo', {})
        expect(f"the main row carries no ledger values, got {got}",
               all(got.get(k) == '-' for k in ('Base', 'Stale', 'Verifier', 'Merge', 'Owner')))

    # 9. ticket_root: tickets: tasks under <root>/tickets/ join the root's tasks.
    with tempfile.TemporaryDirectory() as ttmp:
        ttmp = pathlib.Path(ttmp)
        me = str(pathlib.Path(__file__).resolve())

        def board(root, *args):
            env = dict(os.environ, SDLC_BOARD_STATE_DIR=str(ttmp / 'state'))
            return subprocess.run([sys.executable, me, '--root', str(root), *args],
                                  env=env, capture_output=True, text=True)

        tr = ttmp / 'tr' / '.sdlc'
        tk = task_dir(tr / 'tickets', '0001-a', front.replace('T-0042', 'T-0001'))
        (tk / 'planner-L1.md').write_text('## Step 1: x\nlevel: L1\n')
        side = task_dir(tr, 'side', '## Goal\ny\n')
        (side / 'planner-L1.md').write_text('## Step 1: y\nlevel: L1\n')
        (tr / 'config').write_text('ticket_root: tickets\n')
        out = board(tr).stdout
        expect(f'ticket_root: tickets renders the ticket and the root task, got {out!r}',
               '| T-0001 | 0001-a |' in out and '| side |' in out)
        proc = board(tr, '--task', '0001-a')
        expect(f'--task finds a ticket under tickets/, got {proc.returncode} {proc.stdout!r}',
               proc.returncode == 0 and '0001-a' in proc.stdout)
        (side / 'planner-L1.md').unlink()
        (side / 'handoff.md').unlink()
        out = board(tr, '--summary').stdout.strip()
        expect(f'--summary names the ticket under tickets/, got {out!r}', out.startswith('0001-a '))
        # Negative controls: no config line, and an unsupported value.
        (tr / 'config').write_text('# nothing\n')
        out = board(tr).stdout
        expect(f'with no ticket_root line tickets/<dir> is not a task, got {out!r}', '0001-a' not in out)
        bad = ttmp / 'bad' / '.sdlc'
        rt = task_dir(bad, '0002-b', front.replace('T-0042', 'T-0002'))
        (rt / 'planner-L1.md').write_text('## Step 1: x\nlevel: L1\n')
        (bad / 'config').write_text('ticket_root: work\n')
        proc = board(bad)
        expect(f'an unsupported ticket_root still lists root tasks, got {proc.returncode} {proc.stdout!r}',
               proc.returncode == 0 and '| T-0002 | 0002-b |' in proc.stdout)

    # 10. layout: topics: tasks under <root>/work/ join the board, --summary, and the status line.
    with tempfile.TemporaryDirectory() as ptmp:
        ptmp = pathlib.Path(ptmp)
        me = str(pathlib.Path(__file__).resolve())
        env = dict(os.environ, SDLC_BOARD_STATE_DIR=str(ptmp / 'state'))

        def board_p(root, *args):
            return subprocess.run([sys.executable, me, '--root', str(root), *args],
                                  env=env, capture_output=True, text=True)

        proj = ptmp / 'proj'
        pr = proj / '.sdlc'
        tk = task_dir(pr / 'tickets', '0001-a', front.replace('T-0042', 'T-0001'))
        (tk / 'planner-L1.md').write_text('## Step 1: x\nlevel: L1\n')
        wk = task_dir(pr / 'work', 'w1', '## Goal\ny\n')
        (wk / 'planner-L1.md').write_text('## Step 1: y\nlevel: L1\n')
        (pr / 'config').write_text('ticket_root: tickets\nlayout: topics\n')
        os.utime(tk / 'handoff.md', (1_000_000_000, 1_000_000_000))
        os.utime(wk / 'handoff.md', (2_000_000_000, 2_000_000_000))
        os.utime(wk / 'planner-L1.md', (2_000_000_000, 2_000_000_000))
        out = board_p(pr).stdout
        expect(f'layout: topics renders the ticket and the work/ task, got {out!r}',
               '| T-0001 | 0001-a |' in out and '| w1 |' in out)
        proc = board_p(pr, '--task', 'w1')
        expect(f'--task finds a task under work/, got {proc.returncode} {proc.stdout!r}',
               proc.returncode == 0 and '| w1 |' in proc.stdout and '0001-a' not in proc.stdout)
        out = board_p(pr, '--summary').stdout.strip()
        expect(f'--summary names the newest task under work/, got {out!r}', out.startswith('w1 '))
        if shutil.which('jq'):
            status = json.dumps({'model': {'display_name': 'm'}, 'workspace': {'current_dir': str(proj)}})
            sl = subprocess.run(['bash', str(pathlib.Path(me).with_name('statusline.sh'))], input=status,
                                env=env, capture_output=True, text=True)
            line2 = sl.stdout.split('\n')[1:2]
            expect(f'statusline line 2 names the work/ task, got rc={sl.returncode} {sl.stdout!r}',
                   sl.returncode == 0 and bool(line2) and line2[0].startswith('w1 '))
        # Negative controls: ticket_root without layout (work/ is not a task dir), and an unsupported layout.
        (pr / 'config').write_text('ticket_root: tickets\n')
        out = board_p(pr).stdout
        expect(f'without layout: topics work/<dir> is not a task, got {out!r}',
               '| w1 |' not in out and '0001-a' in out)
        (pr / 'config').write_text('ticket_root: tickets\nlayout: nested\n')
        proc = board_p(pr)
        expect(f'an unsupported layout still lists the tickets and never fails, got {proc.returncode} {proc.stdout!r}',
               proc.returncode == 0 and '0001-a' in proc.stdout and '| w1 |' not in proc.stdout)

    if misses:
        print('board selftest: FAIL, these did not hold:', file=sys.stderr)
        for m in misses:
            print(f'  - {m}', file=sys.stderr)
        return 1
    print('board selftest: PASS')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', nargs='?', choices=['selftest'])
    ap.add_argument('--root', default='.sdlc')
    ap.add_argument('--task')
    ap.add_argument('--waiting')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--sort', choices=['recent', 'id', 'name'], default=None)
    ap.add_argument('--lanes', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'selftest':
        sys.exit(selftest())
    root = pathlib.Path(a.root)
    if a.lanes:
        try:
            table = lanes(root)
        except ValueError:
            print(f'{root}: not inside a git work tree', file=sys.stderr)
            sys.exit(1)
        if a.waiting:
            print(a.waiting)
            print()
        print(table)
        return
    if a.summary:
        print(summary(root))
        return
    if not root.is_dir():
        print(f'no task dirs: {root} does not exist', file=sys.stderr)
        sys.exit(1)
    candidates = task_dirs(root)
    tasks = [t for t in candidates if belongs_on_board(t)]
    mode = a.sort or ('auto' if any(ticket_of(t) for t in tasks) else 'recent')
    tasks = sort_tasks(tasks, mode)
    if a.task:
        tasks = [t for t in tasks if t.name == a.task]
        if not tasks:
            print(f'no task named {a.task} in {root}', file=sys.stderr)
            sys.exit(1)
    print(render(root, tasks, a.waiting))


if __name__ == '__main__':
    main()
