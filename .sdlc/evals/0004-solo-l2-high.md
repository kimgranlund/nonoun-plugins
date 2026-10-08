---
role: solo
level: L2
model: sonnet
effort: high
host: claude
task_set: T-0343 to T-0350 (8) and T-0271, T-0274, T-0304, T-0314, T-0323 (5), high vs xhigh
pass_rate: 13/13
cost_usd: 10.84
date: 2026-10-08
evidence: [docs/reports/2026-10-07-solo-l2-effort-sweep.md, docs/reports/2026-10-07-solo-l2-effort-sweep-2.md]
---
## Method

Ran 13 past tickets through solo L2 (Sonnet) at effort high and at effort xhigh in throwaway trees, one run per arm, and compared each arm's own checks and verdict. Sweep 1 covered T-0343 to T-0350 (8 tickets); sweep 2 covered the L2 tickets T-0271, T-0274, T-0304, T-0314, T-0323 (5) and added a blind reviewer over both arms. The sweeps ran 2026-10-07 (local time); this record is dated by UTC, which is already 2026-10-08, so it is later than the 2026-10-07 eval the lock cites. cost_usd is the high arm only: 4.69 (sweep 1) plus 6.15 (sweep 2, session cost).

## Result

High matched xhigh on every verdict (zero disagreements) at 29 to 39 percent of the cost: sweep 1 high 4.69 against xhigh 15.32 USD, sweep 2 high 6.15 against xhigh 21.48 USD. Own checks passed 13 of 13 at high; sweep 2 own checks were 5 of 5 on both arms. The blind reviewer scored 4 of 5 on both arms, and the one fail was identical on both and a ticket-text artifact. Limits: one run per arm per ticket. The lock hash excludes the solo rows (T-0342), so this eval records the decision and does not move table_sha256. Row changed: solo L2 sonnet xhigh to sonnet high, nothing else.
