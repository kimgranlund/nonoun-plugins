---
role: verifier
level: L2
model: sonnet
effort: high
host: claude
task_set: T-0333 replay: 12 sub-agent tickets in 6 batches, 43 criteria, 3 recorded true fails
pass_rate: 41/43
cost_usd: 6.19
date: 2026-10-07
evidence: docs/reports/2026-10-07-verifier-l2-replay.md
---
## Method

Replayed the six T-0333 verifier batches with verifier L2 (Sonnet high) on a git archive of f0ba4f94 and compared each criterion with the recorded verifier L3 (Fable xhigh) verdict.

## Result

L2 matched L3 on 41 of 43 criteria for 6.19 USD against 36.56 USD, caught 3 of the 4 true failing criteria, missed the literal label match T0280-2, and added one false fail (T0275-3). Routing: verifier L2 for L1 and L2 tickets, L3 for L4, L5, merge, security and exact label or string tickets. No levels.json or models.json row changed.
