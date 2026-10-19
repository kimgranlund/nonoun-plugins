---
role: builder
level: all
model: all
effort: all
host: all
task_set: maintainer decision 2026-10-12, no replay run
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-12
evidence: docs/reports/2026-10-12-builder-overlay-retest-l5-arm-b.md
---
## Method

The maintainer set the builder tables. Claude: L1 Opus low, L2 Sonnet high, L3 Opus medium, L4 Opus high, L5 Opus xhigh. Codex: all five levels on gpt-6.1-sol, L1 low, L2 medium, L3 high, L4 xhigh, L5 max (was L1 gpt-6-luna low, L2 sol low to L5 sol xhigh). Model and effort defaults are a user decision (AGENTS.md shared invariants). The maintainer first named L1 as Haiku 5.5 xhigh and then changed it to Opus low the same day; no row was run.

## Result

No replay or benchmark ran on the new rows. Their quality, cost and the builder blocked rate are unverified. The retest evidence cited covers the old L5 Opus pair only (both arms blocked on the same plan defect). Measure with solo_stats.py and the fleet collector over the next waves.
