# Planner and replan cost, re-measured (T-0315)

Measured 2026-10-06 from the live `runs.jsonl` ledgers of agent-ui, maison and this repository, read-only. The split date is 2026-10-06, the day T-0297 and the L4 and L5 plan-review rule shipped (0.20.11). Counts move a run or two while lanes keep running.

## Method

- Sources: every `runs.jsonl` under each repo's `.sdlc` folder (closed `.NNNN-*` folders included) plus its worktree folders (agent-ui `.claude/worktrees`, this repo `.worktrees`). maison: `ui-kit-maison` and `ui-kit-maison-testing`.
- Dedupe: one row per `attempt_id`, first seen wins, across all files and worktrees. A worktree copy of a ticket's ledger therefore counts once.
- Period: `ts` before 2026-10-06 is "before", on or after is "after".
- A replan is any planner run after the first planner run of the same repo and ticket folder. Cost is `cost_usd`; rows with no cost count as zero and are listed as `null_cost`.
- Calibration against agent-ui's own report (`.sdlc/root-cause-2026-10-06.md`, 193 runs, $787, planner 37 runs $250, plan-reviewer 25 runs $186): this method, cut at `ts` 2026-10-06T14:04:49Z (the 193rd row), gives 193 runs, $787, planner 37 runs $250, plan-reviewer 25 runs $186. That is 0 percent difference, inside the 2 percent limit.

## Per-repo results

| Repo | Period | All runs | All cost | Planner runs / cost / avg min | Plan-reviewer runs / cost / avg min | Planner runs per ticket | Replans / cost |
|---|---|---|---|---|---|---|---|
| agent-ui | before | 140 | $568 | 30 / $188 / 17.7 | 19 / $126 / 8.8 | 1.76 (17 tickets) | 13 / $68 |
| agent-ui | after | 85 | $363 | 7 / $62 / 29.8 | 6 / $60 / 13.5 | 2.33 (3 tickets) | 4 / $30 |
| maison | before | 1084 | $264 (944 rows have no cost) | 86 / $46 / 6.6 | 61 / $44 / 3.3 | 1.51 (57 tickets) | 29 / $18 |
| maison | after | 20 | $72 | 0 | 0 | none | 0 |
| this repo | before | 580 | $1066 (9 null) | 56 / $230 / 18.7 | 25 / $89 / 5.9 | 1.37 (41 tickets) | 15 / $90 |
| this repo | after | 70 | $284 | 2 / $19 / 31.3 | 0 | 1.00 (2 tickets) | 0 |

## Combined

| Period | All runs | All cost | Planner runs / cost / avg min | Plan-reviewer runs / cost / avg min | Planner runs per ticket | Replans | Replan cost | Replan share of all cost |
|---|---|---|---|---|---|---|---|---|
| before | 1804 | $1898 | 172 / $464 / 12.5 | 105 / $259 / 4.9 | 1.50 (115 tickets) | 57 | $175 | 9.2% |
| after | 175 | $720 | 9 / $81 / 30.1 | 6 / $60 / 13.5 | 1.80 (5 tickets) | 4 | $30 | 4.2% |

## Reading

- Per-run planner cost and wall time rose after 0.20.11 (about 30 minutes against 12.5 combined, 17.7 for agent-ui alone), and plan-reviewers now run on L4 and L5 plans, so each is larger. The after sample is small: 9 planner runs on 5 tickets, 4 of them replans, all in agent-ui.
- maison's before figures understate cost: 944 of its 1084 rows carry no `cost_usd`, so its planner cost is a floor. Its replan count (29 of 86 planner runs) is real.
- Replans are about 1 in 3 planner runs before (57 of 172) and 4 of 9 after. Their cost is $175 before and $30 after, 9.2 and 4.2 percent of all spend.

## Recommendation

Leave T-0200 dropped; do not reopen it as a new ticket. The deciding number is the replan cost ceiling: all replans together cost $222 of $2617 total (8.5 percent) across three repos, and $30 (4.2 percent) since 0.20.11. A delta replan that saved half of each replan would return about $15 over the after period and about $111 over the full history, for a feature that would add a second planner path to keep correct. The replan cap stays unchanged.

Reopen if a later measure shows replan cost above 10 percent of all spend on at least 20 post-0.20.11 planner tickets. The after sample here (5 tickets) is too small to settle that; rerun the appendix script then.

## Appendix: measurement script

Run with `python3 -I`. It prints the rows in the tables above.

```python
import json, os, collections
HOME = '/Users/kimgranlund/Projects'
REPOS = {
    'agent-ui': [f'{HOME}/nonoun/agent-ui/.sdlc', f'{HOME}/nonoun/agent-ui/.claude/worktrees'],
    'maison': [f'{HOME}/maison/ui-kit-maison/.sdlc', f'{HOME}/maison/ui-kit-maison-testing/.sdlc'],
    'sdlc-lite': [f'{HOME}/nonoun/sdlc-lite/.sdlc', f'{HOME}/nonoun/sdlc-lite/.worktrees'],
}
CUT = '2026-10-06'

def load(roots, repo):
    rows = {}
    for r in roots:
        for dp, _, fn in os.walk(r):          # os.walk, not glob: closed folders are dot-named
            if 'runs.jsonl' not in fn or 'node_modules' in dp:
                continue
            for line in open(os.path.join(dp, 'runs.jsonl')):
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get('attempt_id'):
                    d['_t'], d['_r'] = os.path.basename(dp), repo
                    rows.setdefault(d['attempt_id'], d)   # dedupe by attempt_id
    return rows

data = {k: load(v, k) for k, v in REPOS.items()}
data['combined'] = {a: d for r in data.values() for a, d in r.items()}
cost = lambda rs: sum(d.get('cost_usd') or 0 for d in rs)
for repo, rows in data.items():
    for per, f in (('before', lambda t: t < CUT), ('after', lambda t: t >= CUT)):
        rs = sorted((d for d in rows.values() if f(d['ts'])), key=lambda d: d['ts'])
        print(f'{repo} {per}: runs={len(rs)} cost=${cost(rs):.0f} null_cost={sum(d.get("cost_usd") is None for d in rs)}')
        for role in ('planner', 'plan-reviewer'):
            rr = [d for d in rs if d['role'] == role]
            tk = collections.Counter((d['_r'], d['_t']) for d in rr)
            if rr:
                print(f'  {role}: runs={len(rr)} cost=${cost(rr):.0f} '
                      f'avg_min={sum(d.get("duration_ms") or 0 for d in rr)/60000/len(rr):.1f} '
                      f'tickets={len(tk)} runs_per_ticket={len(rr)/len(tk):.2f}')
        seen, replans = set(), []
        for d in (d for d in rs if d['role'] == 'planner'):
            k = (d['_r'], d['_t'])
            if k in seen:
                replans.append(d)        # a replan = any planner run after the ticket's first
            seen.add(k)
        print(f'  replans={len(replans)} cost=${cost(replans):.0f} share_of_all_cost={cost(replans)/max(1,cost(rs))*100:.1f}%')
```
