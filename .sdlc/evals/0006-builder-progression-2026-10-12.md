---
role: builder
level: all
model: all
effort: all
host: claude
task_set: maintainer decision 2026-10-12, no replay run
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-12
evidence: docs/reports/2026-10-12-builder-overlay-retest-l5-arm-b.md
---
## Method

The maintainer set the Claude builder table: L1 Haiku 5.5 xhigh, L2 Sonnet high, L3 Opus medium, L4 Opus high, L5 Opus xhigh. Model and effort defaults are a user decision (AGENTS.md shared invariants). Only one fact was checked: claude -p --model claude-haiku-5-5 --effort xhigh answers, so the L1 row loads.

## Result

No replay or benchmark ran on the new rows. Their quality, cost and the builder blocked rate are unverified. The retest evidence cited covers the old L5 Opus pair only (both arms blocked on the same plan defect). Measure with solo_stats.py and the fleet collector over the next waves.
