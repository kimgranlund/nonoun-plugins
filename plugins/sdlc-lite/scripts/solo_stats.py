#!/usr/bin/env python3
"""Count how the solo lane performed in one or more repos. No model call, read-only.

Usage: solo_stats.py stats <repo> [<repo> ...] [--since DATE] [--until DATE] [--json]
       solo_stats.py selftest

Prints one table (or with --json one object) for the repos together plus a line per repo. Only each repo's own
main checkout `.sdlc` is read: a ticket folder copied into a linked worktree is not counted. Closed `.NNNN-*`
folders (a leading dot) are read like any other. The ticket-folder layout is the repo's (`ticket_root: tickets` in
its `.sdlc/config`), as fleet_collect.py reads it. A runs.jsonl under `.sdlc/runtime/tasks/<key>/` (the records dir)
counts for its task folder (fleet_collect.ticket_of). Rows are deduplicated by attempt_id (a row with none, on its whole line).

A solo ticket is a ticket folder whose `runs.jsonl` files hold at least one `solo` role row inside the window:
at or after --since and up to --until (a bare YYYY-MM-DD is that UTC midnight, and a bare --until date includes the
whole day; an ISO instant is exact; no bound counts every row). Closed state and verifier files are read as they are now. Keys:
  tickets         solo tickets; runs: their solo rows in the window
  closed, open    closed = a hidden folder (the name starts with a dot: `tickets.py close` renames a closed ticket to
                  `.NNNN-slug`); every other folder is open. A repo that keeps closed tickets visible (no `ticket_folders:
                  numbered`) reports them as open: open_done counts those whose handoff.md front matter has status done or dropped
  verified        tickets holding at least one verifier result file `verifier-L<n>[-<round>].md` (no round suffix is
                  round 1); the rest are docs-only skips and the L1 default (no verifier)
  first_pass      verified tickets whose lowest-numbered round has Verdict pass
  ended_pass      verified tickets whose highest-numbered round has Verdict pass
  multi_round     verified tickets with two or more rounds
  closed_no_pass  closed verified tickets whose highest round is not a pass (inherited, deferred, superseded)
  gate_tests_only tickets whose skips.md holds `reason: tests-gate diff against`, the skip line `tickets.py close`
                  writes for a ticket closed on the tests-gate class with no verifier (T-0496)
  gate_verifier   tickets with at least one verifier round (the verified condition)
  cost            runs, priced (a numeric cost_usd and no `unpriced` flag), unmetered (the rest), cost_usd and minutes of the
                  priced runs. Unpriced runs are counted and never estimated.
Rounds are ordered by round number, never by file name (`verifier-L2-10.md` follows `-9`). Two files in one round
(an escalated level) count as one round: it passes when any file passes.

Exit codes: 0 ok, 2 usage or a missing repo.
"""
import json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fleet_collect as fc  # noqa: E402
import order  # noqa: E402

VERIFIER_RE = re.compile(r'verifier-L([1-5])(?:-(\d+))?\.md')
CLOSED_STATUS = ('done', 'dropped')
USAGE = ('usage: solo_stats.py stats <repo> [<repo> ...] [--since DATE] [--until DATE] [--json]\n'
         '       solo_stats.py selftest')
COUNTS = ('tickets', 'closed', 'open', 'open_done', 'verified', 'first_pass', 'ended_pass', 'multi_round', 'closed_no_pass',
          'gate_tests_only', 'gate_verifier')
TESTS_GATE_SKIP = 'reason: tests-gate diff against'


def verdict_of(text):
    """The first non-blank line under `## Verdict`, lowercased and cut to its first word, else ''."""
    inside = False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.rstrip() == '## Verdict'
            continue
        if inside and line.strip():
            words = line.strip().lower().split()
            return words[0] if words else ''
    return ''


def round_verdicts(folder, round_key=None):
    """[(round number, verdict)] of the verifier result files in one ticket folder, one per file, ordered by
    round number then verifier level (`verifier-L2.md`, `verifier-L3.md`, `verifier-L3-2.md`). round_key is the
    negative control: when given, the files are ordered by it applied to the file name instead. The files are read
    from the folder's records dir (order.records_dir: `runtime/tasks/<key>/`, or the folder itself for a legacy one)."""
    folder = str(order.records_dir(folder))
    files = []
    try:
        names = os.listdir(folder)
    except OSError:
        return []
    for n in names:
        m = VERIFIER_RE.fullmatch(n)
        if m:
            files.append((int(m.group(2)) if m.group(2) else 1, int(m.group(1)), n))
    if round_key is not None:
        files.sort(key=lambda f: round_key(f[2]))
    else:
        files.sort()
    return [(rnd, verdict_of(fc.read_text(os.path.join(folder, n)))) for rnd, _lvl, n in files]


def is_closed(sdlc, key):
    """Closed = a hidden `.NNNN-*` folder (the T-0449 baseline's rule)."""
    return os.path.basename(key).startswith('.')


def handoff_done(sdlc, key):
    """True when the folder's handoff.md front matter has status done or dropped."""
    lines = fc.read_text(os.path.join(sdlc, key, 'handoff.md')).splitlines()
    if lines and lines[0].strip() == '---':
        for line in lines[1:]:
            if line.strip() == '---':
                break
            m = re.match(r'^status:\s*"?([a-z]+)', line)
            if m:
                return m.group(1) in CLOSED_STATUS
    return False


def new_counts():
    d = dict.fromkeys(COUNTS, 0)
    d['cost'] = {'runs': 0, 'priced': 0, 'unmetered': 0, 'cost_usd': 0.0, 'minutes': 0.0}
    return d


def repo_stats(repo, window, round_key=None, dedupe=True, main_only=True, closed_fn=None):
    """The counts of one repo, from its main checkout `.sdlc` alone. The keyword arguments are the negative controls
    the selftest flips: main_only=False reads linked worktrees too, dedupe=False counts every row, round_key orders
    rounds by file name, closed_fn replaces the hidden-folder rule."""
    closed_fn = closed_fn or is_closed
    repo = os.path.realpath(repo)
    roots = [repo]
    if not main_only:
        roots = fc.worktree_roots(repo)[0]
    out = new_counts()
    nested = fc.nested_tickets(os.path.join(repo, '.sdlc'))
    seen, tickets = set(), {}
    for root in roots:
        sdlc = os.path.join(root, '.sdlc')
        for cur, dirs, files in os.walk(sdlc):
            dirs[:] = sorted(d for d in dirs if d not in fc.SKIP_DIRS)
            if 'runs.jsonl' not in files:
                continue
            p = os.path.join(cur, 'runs.jsonl')
            key = fc.ticket_of(sdlc, p, nested)
            for line in fc.read_text(p).splitlines():
                line = line.strip()
                try:
                    rec = json.loads(line) if line else None
                except ValueError:
                    continue
                if not isinstance(rec, dict) or rec.get('role') != 'solo' or not window.has(rec.get('ts')):
                    continue
                aid = rec.get('attempt_id')
                if dedupe:
                    k = ('id', aid) if isinstance(aid, str) and aid else ('raw', line)
                    if k in seen:
                        continue
                    seen.add(k)
                tickets.setdefault(key, (sdlc, []))[1].append(rec)
    cost = out['cost']
    for key in sorted(tickets):
        sdlc, rows = tickets[key]
        folder = os.path.join(sdlc, key)
        out['tickets'] += 1
        closed = closed_fn(sdlc, key)
        out['closed' if closed else 'open'] += 1
        out['open_done'] += not closed and handoff_done(sdlc, key)
        for rec in rows:
            c, d = fc.num(rec.get('cost_usd')), fc.num(rec.get('duration_ms'))
            cost['runs'] += 1
            if c is None or rec.get('unpriced') is True:
                cost['unmetered'] += 1
                continue
            cost['priced'] += 1
            cost['cost_usd'] += c
            cost['minutes'] += (d or 0.0) / 60000.0
        out['gate_tests_only'] += TESTS_GATE_SKIP in fc.read_text(os.path.join(folder, 'skips.md'))
        rounds = round_verdicts(folder, round_key)
        if not rounds:
            continue
        out['verified'] += 1
        out['gate_verifier'] += 1
        out['first_pass'] += rounds[0][1] == 'pass'
        ended = rounds[-1][1] == 'pass'
        out['ended_pass'] += ended
        out['multi_round'] += len(rounds) > 1
        out['closed_no_pass'] += closed and not ended
    cost['cost_usd'] = round(cost['cost_usd'], 2)
    cost['minutes'] = round(cost['minutes'], 1)
    return out


def add_counts(total, one):
    for k in COUNTS:
        total[k] += one[k]
    for k in total['cost']:
        total['cost'][k] += one['cost'][k]


def pct(n, d):
    return '%d percent' % round(100.0 * n / d) if d else 'n/a'


def render(total, per_repo, since, until=None):
    c = total['cost']
    v = total['verified']
    lines = ['solo stats since %s%s' % (since or 'the start', ' until ' + until if until else ''),
             'solo tickets      %d (%d solo runs)' % (total['tickets'], c['runs']),
             'closed / open     %d / %d (%d of the open have a handoff status done or dropped)'
             % (total['closed'], total['open'], total['open_done']),
             'verified          %d (%d without a verifier)' % (v, total['tickets'] - v),
             'first round pass  %d of %d (%s)' % (total['first_pass'], v, pct(total['first_pass'], v)),
             'ended in a pass   %d of %d (%s)' % (total['ended_pass'], v, pct(total['ended_pass'], v)),
             'multi-round       %d' % total['multi_round'],
             'closed, no pass   %d' % total['closed_no_pass'],
             'gate: tests-only  %d' % total['gate_tests_only'],
             'gate: verifier    %d' % total['gate_verifier'],
             'priced runs       %d of %d, %d unmetered; $%.2f, %.0f minutes of the priced runs'
             % (c['priced'], c['runs'], c['unmetered'], c['cost_usd'], c['minutes'])]
    if c['priced']:
        lines.append('per priced run    $%.2f, %.1f minutes' % (c['cost_usd'] / c['priced'], c['minutes'] / c['priced']))
    for name, r in per_repo:
        lines.append('  %s: %d tickets, %d verified, first pass %d, ended in pass %d, priced %d of %d'
                     % (name, r['tickets'], r['verified'], r['first_pass'], r['ended_pass'],
                        r['cost']['priced'], r['cost']['runs']))
    return '\n'.join(lines)


def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == 'selftest':
        return selftest()
    if argv[0] != 'stats':
        print(USAGE, file=sys.stderr)
        return 2
    repos, since, until, as_json, rest, i = [], None, None, False, argv[1:], 0
    while i < len(rest):
        a = rest[i]
        if a == '--since' and i + 1 < len(rest):
            i += 1
            since = rest[i]
        elif a == '--until' and i + 1 < len(rest):
            i += 1
            until = rest[i]
        elif a == '--json':
            as_json = True
        elif not a.startswith('--'):
            repos.append(a)
        else:
            print(USAGE, file=sys.stderr)
            return 2
        i += 1
    if not repos:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        window = fc.Window(since, until)
    except ValueError as e:
        print('solo_stats: %s' % e, file=sys.stderr)
        return 2
    total, per_repo = new_counts(), []
    for repo in repos:
        if not os.path.isdir(repo):
            print('solo_stats: no such repo directory: %s' % repo, file=sys.stderr)
            return 2
        r = repo_stats(repo, window)
        per_repo.append((os.path.basename(os.path.realpath(repo)), r))
        add_counts(total, r)
    if as_json:
        json.dump({'since': since, 'until': until, 'total': total, 'repos': dict(per_repo)}, sys.stdout, indent=2)
        sys.stdout.write('\n')
    else:
        print(render(total, per_repo, since, until))
    return 0


# --- selftest ----------------------------------------------------------------

def selftest():
    misses = []

    def case(name, got, want):
        if got != want:
            misses.append('%s: got %r, want %r' % (name, got, want))

    def write(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    def row(aid, ts, cost=None, dur=60000, role='solo', **extra):
        d = {'ts': ts, 'role': role, 'attempt_id': aid, 'duration_ms': dur}
        if cost is not None:
            d['cost_usd'] = cost
        d.update(extra)
        return json.dumps(d) + '\n'

    def verdict(v):
        return '<!-- role=verifier level=L2 model=opus effort=high -->\n## Verdict\n%s\n\n## Criteria\n- 1. ok\n' % v

    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, 'repo')
        sd = os.path.join(repo, '.sdlc')
        # a: open; rounds fail, fail, fail, pass by number (-1, -2, -9, -10); by file name -10 sorts first and L2.md last.
        write(os.path.join(sd, '0001-a', 'runs.jsonl'),
              row('a1', '2026-10-09T10:00:00Z', 1.5, 120000) + row('a2', '2026-10-09T11:00:00Z', 0.5, 60000))
        for n, v in (('verifier-L2.md', 'fail'), ('verifier-L2-2.md', 'fail'), ('verifier-L2-9.md', 'fail'),
                     ('verifier-L2-10.md', 'pass')):
            write(os.path.join(sd, '0001-a', n), verdict(v))
        # b: hidden closed folder, first-pass; the row before --since is not counted.
        write(os.path.join(sd, '.0002-b', 'runs.jsonl'),
              row('b1', '2026-10-09T10:00:00Z') + row('b0', '2026-10-01T10:00:00Z', 9.0))
        write(os.path.join(sd, '.0002-b', 'verifier-L3.md'), verdict('pass'))
        # c: visible folder, handoff status done (open by the hidden rule), no verifier, a duplicated row, an unpriced flag.
        write(os.path.join(sd, '0003-c', 'handoff.md'), '---\nid: T-0003\nstatus: done\n---\n')
        write(os.path.join(sd, '0003-c', 'skips.md'), '# Skips\n\n## Lane\n- lane: solo; point: before planning\n\n## Skipped\n'
              '- skip: verifier; step: all; reason: tests-gate diff against abc1234 needs no verifier\n')
        # a's skips.md has a docs-only skip line and no tests-gate one: the control for gate_tests_only.
        write(os.path.join(sd, '0001-a', 'skips.md'), '# Skips\n\n## Skipped\n'
              '- skip: verifier; step: all; reason: docs-only diff against abc1234 needs no verifier\n')
        write(os.path.join(sd, '0003-c', 'runs.jsonl'),
              row('c1', '2026-10-10T10:00:00Z', 2.0, 30000, unpriced=True) + row('c1', '2026-10-10T10:00:00Z', 2.0, 30000))
        # d: hidden closed; fail, then inherited: ended without a pass.
        write(os.path.join(sd, '.0004-d', 'runs.jsonl'), row('d1', '2026-10-10T10:00:00Z', 1.0, 60000))
        write(os.path.join(sd, '.0004-d', 'verifier-L2.md'), verdict('fail'))
        write(os.path.join(sd, '.0004-d', 'verifier-L2-2.md'), verdict('inherited red: t1'))
        # e: a builder-only folder, no solo row: not a solo ticket.
        write(os.path.join(sd, '0005-e', 'runs.jsonl'), row('e1', '2026-10-10T10:00:00Z', 1.0, role='builder'))
        # g: open; an L2 pass then an L3 file that fails: two verifier files are two rounds.
        write(os.path.join(sd, '0007-g', 'runs.jsonl'), row('g1', '2026-10-10T10:00:00Z', 1.0, 60000))
        write(os.path.join(sd, '0007-g', 'verifier-L2.md'), verdict('pass'))
        write(os.path.join(sd, '0007-g', 'verifier-L3.md'), verdict('fail'))
        # a linked worktree holding ticket f and a copy of a: neither is counted.
        wt = os.path.join(repo, '.worktrees', 'lane')
        write(os.path.join(wt, '.sdlc', '0006-f', 'runs.jsonl'), row('f1', '2026-10-10T10:00:00Z', 1.0))
        write(os.path.join(wt, '.sdlc', '0001-a', 'runs.jsonl'), row('a3', '2026-10-10T12:00:00Z', 1.0))
        window = fc.Window('2026-10-08')

        def counts(got):
            return {k: got[k] for k in COUNTS}

        got = repo_stats(repo, window)
        case('counts', counts(got), {
            'tickets': 5, 'closed': 2, 'open': 3, 'open_done': 1, 'verified': 4, 'first_pass': 2, 'ended_pass': 2,
            'multi_round': 3, 'closed_no_pass': 1, 'gate_tests_only': 1, 'gate_verifier': 4})
        os.remove(os.path.join(sd, '0003-c', 'skips.md'))
        gone = repo_stats(repo, window)
        case('control skip line absent', (gone['gate_tests_only'], gone['gate_verifier']), (0, 4))
        text = render(got, [], None)
        case('render gate lines', [ln for ln in text.splitlines() if ln.startswith('gate: ')],
             ['gate: tests-only  1', 'gate: verifier    4'])
        case('cost', got['cost'], {'runs': 6, 'priced': 4, 'unmetered': 2, 'cost_usd': 4.0, 'minutes': 5.0})
        # Observed-red controls: each wrong method moves a count pinned above.
        by_name = repo_stats(repo, window, round_key=lambda n: n)
        case('control name-ordered rounds', (by_name['first_pass'], by_name['ended_pass']), (3, 1))
        with_wt = repo_stats(repo, window, main_only=False)
        case('control worktree copy', (with_wt['tickets'], with_wt['cost']['runs']), (6, 8))
        status_only = repo_stats(repo, window, closed_fn=lambda sdlc, k: handoff_done(sdlc, k))
        case('control hidden closed folder', (status_only['closed'], status_only['closed_no_pass']), (1, 0))
        case('control duplicate rows', repo_stats(repo, window, dedupe=False)['cost']['runs'], 7)
        case('verdict first word', verdict_of(verdict('inherited red: t1')), 'inherited')
        case('cli no arguments', main([]), 2)
        case('cli missing repo', main(['stats', os.path.join(tmp, 'nope')]), 2)
        case('cli bad date', main(['stats', repo, '--since', 'soon']), 2)
        # records dir: a solo row under runtime/tasks/<key>/ counts for its closed folder; legacy reads in place.
        for name, rt in (('records dir: runtime-only fixture', True), ('records dir: legacy fixture', False)):
            r2 = os.path.join(tmp, 'rr-' + str(rt))
            s2 = os.path.join(r2, '.sdlc')
            write(os.path.join(s2, '.0001-a', 'handoff.md'), '---\nid: T-0001\nstatus: done\n---\n')
            rec_dir = os.path.join(s2, 'runtime', 'tasks', '0001-a') if rt else os.path.join(s2, '.0001-a')
            write(os.path.join(rec_dir, 'runs.jsonl'), row('r1', '2026-10-10T10:00:00Z', 2.5, 60000))
            write(os.path.join(rec_dir, 'verifier-L2.md'), verdict('pass'))
            got2 = repo_stats(r2, window)
            want2 = (1, 1, 0, 1, 1, 2.5)
            have2 = (got2['tickets'], got2['closed'], got2['open'], got2['verified'], got2['first_pass'],
                     got2['cost']['cost_usd'])
            case(name, have2, want2)
            if have2 == want2:
                print('ok: ' + name)
    if misses:
        print('solo_stats selftest: %d failed: %s' % (len(misses), '; '.join(misses)), file=sys.stderr)
        return 1
    print('solo_stats selftest: ok')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
