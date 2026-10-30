---
role: solo
level: all
model: all
effort: all
host: claude
task_set: maintainer decision 2026-10-12, no replay run
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-13
evidence: docs/specs/sdlc/solo-lane-contract.md
---
## Method

The maintainer decided the Claude solo table is the builder table shifted down one level: solo L1 Sonnet high (builder L2), solo L2 Opus medium (builder L3), solo L3 Opus high (builder L4); was L1 Sonnet low, L2 Sonnet high, L3 Opus xhigh. Codex solo rows and builder rows are unchanged. Model and effort defaults are a user decision (AGENTS.md shared invariants).

## Result

No replay or benchmark ran on the new rows. Their quality, cost and blocked rate are unverified. prices.json was not recalibrated and keeps its old price basis. Measure with solo_stats.py over the next waves.
