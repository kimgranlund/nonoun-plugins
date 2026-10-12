---
id: G-003
title: Solo tickets pass their independent verifier on the first round
status: proposed
owner: maintainer
created: 2026-10-11
horizon: 2026-Q4
kpis: [K-005]
---
## Outcome
Most solo tickets that get an independent verifier pass it on the first round, so the second round and the closed-without-a-pass cases become the exception and the lane's cost per closed ticket stays near one run.

## Why
The [solo campaign baseline of 2026-10-11](../reports/2026-10-11-solo-campaign-baseline.md) counted 89 of 123 verified solo tickets passing the first round (72 percent), 32 needing more than one verifier file, and 12 closed with no final pass. Each extra round is a verifier run and a solo rerun on top of the ticket's cost.

## Scope
In: the solo lane's agent files, ticket criteria and checks as they change first-round results, measured by `solo_stats.py`. Out: judging whether a pass met the ticket's intent, a solo against chain comparison, and model or effort rows.

## Done when
- [K-005](../kpi/005-solo-first-pass-rate.md) reads 85 or above in a retro window of the same four repositories after the findings of the solo failure review land.

## History
- 2026-10-11: proposed with K-005 from the solo campaign baseline (T-0449).
