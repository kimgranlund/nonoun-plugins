#!/usr/bin/env python3
"""Read-only baseline probe for K-002, K-003 and K-004 (planner-L3, 2026-10-09).

Usage: python3 kpi-baseline-probe.py SINCE REPO [REPO ...]   (SINCE as 2026-10-09)

Reads <repo>/.sdlc, <repo>/.worktrees/*/.sdlc and <repo>/.claude/worktrees/*/.sdlc, hidden ticket folders included,
and writes nothing. Per repo it prints:
  interrupted   attempts with status interrupted started on or after SINCE, deduped by attempt_id
  lost_min      minutes from each one's started_at to the started_at of the next attempt of the same role in the
                same handoff dir (its finished_at when there is none): the work a restart threw away plus the gap
  orphaned      attempts still status running, claude backend, whose parent pid is dead now (never recovered)
  builders      builder runs.jsonl rows with ts on or after SINCE (deduped), and how many of their result files
                hold a ## Status whose first word is blocked (a result rewritten later counts as rewritten)
  late_defects  builder and verifier rows whose result holds a line starting `plan defect:`
  verifier_min  completed verifier attempts: median and max of finished_at minus started_at
Stand-in until fleet_collect.py carries these fields (plan step 1 of .sdlc/plan-reliability-docs/plan.md).
"""
import glob
import json
import os
import re
import statistics
import sys
from datetime import datetime


def ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def walk(root):
    for s in [root + '/.sdlc'] + glob.glob(root + '/.worktrees/*/.sdlc') + glob.glob(root + '/.claude/worktrees/*/.sdlc'):
        for dp, dns, fns in os.walk(s):
            dns[:] = [d for d in dns if d not in ('.git', 'node_modules')]
            yield s, dp, fns


def probe(root, since):
    atts, seen, orphans = {}, set(), set()
    rows, rows_seen = [], set()
    for s, dp, fns in walk(root):
        rel = os.path.relpath(dp, s)
        for f in fns:
            p = os.path.join(dp, f)
            if f.endswith('.attempt.json'):
                try:
                    d = json.load(open(p))
                except (OSError, ValueError):
                    continue
                if not isinstance(d, dict) or not d.get('started_at'):
                    continue
                aid = d.get('attempt_id') or p
                if aid in seen:
                    continue
                seen.add(aid)
                atts.setdefault((rel, d.get('role')), []).append(d)
                pid = d.get('parent_pid') or d.get('owner_pid')
                if (d.get('status') == 'running' and d['started_at'] >= since and d.get('backend', 'claude') == 'claude'
                        and isinstance(pid, int) and not alive(pid)):
                    orphans.add(aid)
            elif f == 'runs.jsonl':
                for line in open(p, errors='replace'):
                    try:
                        r = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(r, dict) or r.get('ts', '') < since or r.get('role') not in ('builder', 'verifier'):
                        continue
                    key = r.get('attempt_id') or (rel, r.get('file'))
                    if key in rows_seen:
                        continue
                    rows_seen.add(key)
                    rows.append((r['role'], os.path.join(dp, r.get('file') or '')))
    lost, vmin = [], []
    for (_, role), group in atts.items():
        group.sort(key=lambda d: d['started_at'])
        for i, d in enumerate(group):
            if d['started_at'] < since:
                continue
            if d.get('status') == 'interrupted':
                nxt = group[i + 1] if i + 1 < len(group) else None
                end = nxt['started_at'] if nxt else d.get('finished_at')
                if end:
                    lost.append(round((ts(end) - ts(d['started_at'])).total_seconds() / 60, 1))
            if role == 'verifier' and d.get('status') == 'completed' and d.get('finished_at'):
                vmin.append(round((ts(d['finished_at']) - ts(d['started_at'])).total_seconds() / 60, 1))
    builders = blocked = late = 0
    for role, path in rows:
        text = open(path, errors='replace').read() if os.path.isfile(path) else ''
        if role == 'builder':
            builders += 1
            m = re.search(r'^## Status\s*\n\s*(\S+)', text, re.M)
            blocked += bool(m and m.group(1).lower().startswith('blocked'))
        late += bool(re.search(r'^\s*[-*]?\s*plan defect:', text, re.M))
    return dict(interrupted=len(lost), lost_min=sorted(lost), lost_min_median=statistics.median(lost) if lost else None,
                orphaned=len(orphans), builder_rows=builders, blocked=blocked, builder_and_verifier_rows=len(rows),
                late_defects=late, verifier_completed=len(vmin),
                verifier_min_median=statistics.median(vmin) if vmin else None, verifier_min_max=max(vmin) if vmin else None)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    since, total_lost = argv[0], []
    for root in argv[1:]:
        r = probe(root.rstrip('/'), since)
        total_lost += r['lost_min']
        print(json.dumps(dict(repo=os.path.basename(root.rstrip('/')), **r)))
    print(json.dumps(dict(fleet_lost_min_median=statistics.median(total_lost) if total_lost else None,
                          fleet_interrupted=len(total_lost))))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
