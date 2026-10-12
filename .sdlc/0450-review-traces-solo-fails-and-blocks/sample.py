#!/usr/bin/env python3
"""Draw the T-0450 sample: solo first-round verifier non-passes and builder blocked notes. Read-only, no model call.

Usage (from the sdlc-lite repo root):
  python3 .sdlc/0450-review-traces-solo-fails-and-blocks/sample.py [--since DATE] [--until INSTANT] [--k N] [repo ...]

Defaults: the four repos of the solo campaign baseline, --since 2026-10-08, --until 2026-10-11T20:00:00Z (the instant
that reproduces the baseline counts in docs/reports/2026-10-11-solo-campaign-baseline.md), --k 2.

Method (the baseline's, through solo_stats.py and fleet_collect.py):
- A solo ticket has a `solo` row in a runs.jsonl inside the window. Only each repo's main checkout `.sdlc` is read
  (worktree copies excluded); hidden closed `.NNNN-*` folders are read; `ticket_root: tickets` is honoured.
- Verifier rounds are ordered by round number then level (`verifier-L2.md`, `-2`, `-3`), never by name.
- First-round non-pass: the first verifier file's verdict is not `pass`. "Later passed or closed": a later round
  passes, or the folder is hidden (closed), or its handoff status is done or dropped.
- Builder blocked note: a `builder-L<n>[-<k>].md` anywhere under a ticket folder (step dirs and superseded step dirs
  included) whose `## Status` first line starts with `blocked`, in a ticket folder whose runs.jsonl holds a
  `builder` row inside the window. Tagged by its lines: `plan defect:`, `stale lane:`, `inherited red`, else other.
- Read sample: per repo, the blocked notes in sorted path order, every k-th one (index 0, k, 2k, ...).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'plugins', 'sdlc-lite', 'scripts'))
import fleet_collect as fc  # noqa: E402
import solo_stats as ss  # noqa: E402

REPOS = ['~/Projects/maison/ui-kit-maison', '~/Projects/nonoun/agent-ui', '~/Projects/nonoun/ultimate-tokens',
         '~/Projects/nonoun/sdlc-lite']
BUILDER_RE = re.compile(r'builder-L([1-5])(?:-(\d+))?\.md')
HOME = os.path.expanduser('~')


def tilde(p):
    return '~' + p[len(HOME):] if p.startswith(HOME + os.sep) else p


def section_first(text, head):
    inside = False
    for line in text.splitlines():
        if line.startswith('## '):
            inside = line.rstrip() == head
            continue
        if inside and line.strip():
            return line.strip()
    return ''


def ticket_rows(repo, window):
    """{ticket key: (sdlc, set of roles, [minutes, priced usd])} from the main checkout only, deduped. Minutes sum
    duration_ms of every row in the window; usd sums cost_usd of priced rows only (no `unpriced` flag)."""
    sdlc = os.path.join(repo, '.sdlc')
    nested = fc.nested_tickets(sdlc)
    out, seen = {}, set()
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
            if not isinstance(rec, dict) or not window.has(rec.get('ts')):
                continue
            aid = rec.get('attempt_id')
            k = ('id', aid) if isinstance(aid, str) and aid else ('raw', line)
            if k in seen:
                continue
            seen.add(k)
            ent = out.setdefault(key, (sdlc, set(), [0.0, 0.0]))
            ent[1].add(rec.get('role'))
            ent[2][0] += (fc.num(rec.get('duration_ms')) or 0.0) / 60000.0
            c = fc.num(rec.get('cost_usd'))
            if c is not None and rec.get('unpriced') is not True:
                ent[2][1] += c
    return out


def first_round_file(folder):
    files = []
    for n in os.listdir(folder):
        m = ss.VERIFIER_RE.fullmatch(n)
        if m:
            files.append((int(m.group(2)) if m.group(2) else 1, int(m.group(1)), n))
    files.sort()
    return files


def blocked_tag(text):
    low = text.lower()
    if re.search(r'^\s*(?:[-*]\s*)?plan defect:', low, re.M):
        return 'plan defect'
    if re.search(r'^\s*(?:[-*]\s*)?stale lane:', low, re.M):
        return 'stale lane'
    if 'inherited red' in low:
        return 'inherited red'
    return 'other'


def main(argv):
    since, until, k, repos, i = '2026-10-08', '2026-10-11T20:00:00Z', 2, [], 0
    while i < len(argv):
        a = argv[i]
        if a in ('--since', '--until', '--k') and i + 1 < len(argv):
            i += 1
            if a == '--since':
                since = argv[i]
            elif a == '--until':
                until = argv[i] if argv[i] != 'none' else None
            else:
                k = int(argv[i])
        else:
            repos.append(a)
        i += 1
    repos = repos or REPOS
    window = fc.Window(since, until)
    tot = {'solo': 0, 'verified': 0, 'first_nonpass': 0, 'nonpass_later_ok': 0, 'blocked': 0, 'read': 0}
    tags_all = {}
    nonpass, blocked, read = [], [], []
    for r in repos:
        repo = os.path.realpath(os.path.expanduser(r))
        name = os.path.basename(repo)
        rows = ticket_rows(repo, window)
        rb = []
        for key in sorted(rows):
            sdlc, roles, spend = rows[key]
            folder = os.path.join(sdlc, key)
            if not os.path.isdir(folder):
                continue
            if 'solo' in roles:
                tot['solo'] += 1
                files = first_round_file(folder)
                if files:
                    tot['verified'] += 1
                    verdicts = [ss.verdict_of(fc.read_text(os.path.join(folder, f[2]))) for f in files]
                    if verdicts[0] != 'pass':
                        tot['first_nonpass'] += 1
                        closed = ss.is_closed(sdlc, key) or ss.handoff_done(sdlc, key)
                        later = any(v == 'pass' for v in verdicts[1:])
                        ok = closed or later
                        tot['nonpass_later_ok'] += ok
                        nonpass.append((name, tilde(os.path.join(folder, files[0][2])), verdicts[0],
                                        'later-pass' if later else ('closed' if closed else 'open-no-pass'),
                                        '%.0f' % spend[0], '%.2f' % spend[1]))
            if 'builder' in roles:
                for cur, dirs, fs in os.walk(folder):
                    dirs[:] = sorted(dirs)
                    for n in sorted(fs):
                        if not BUILDER_RE.fullmatch(n):
                            continue
                        p = os.path.join(cur, n)
                        text = fc.read_text(p)
                        if section_first(text, '## Status').lower().startswith('blocked'):
                            rb.append((p, blocked_tag(text)))
        rb.sort()
        for idx, (p, tag) in enumerate(rb):
            tot['blocked'] += 1
            tags_all[tag] = tags_all.get(tag, 0) + 1
            blocked.append((name, tilde(p), tag))
            if idx % k == 0:
                read.append((name, tilde(p), tag))
        print('repo %s: blocked notes %d, read %d' % (name, len(rb), len([x for x in read if x[0] == name])))
    tot['read'] = len(read)
    print('window since %s until %s, k=%d' % (since, until, k))
    print('solo tickets %(solo)d, verified %(verified)d, first-round non-pass %(first_nonpass)d, '
          'of which later passed or closed %(nonpass_later_ok)d' % tot)
    print('builder blocked notes %d by tag %s; read sample %d' % (tot['blocked'], json.dumps(tags_all, sort_keys=True),
                                                                    tot['read']))
    print('\n# first-round non-passes (repo, file, verdict, outcome, ticket minutes, ticket priced usd; all roles)')
    for row in nonpass:
        print('\t'.join(row))
    print('\n# blocked read sample (repo, file, tag)')
    for row in read:
        print('\t'.join(row))
    print('\n# all blocked notes (repo, file, tag)')
    for row in blocked:
        print('\t'.join(row))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
