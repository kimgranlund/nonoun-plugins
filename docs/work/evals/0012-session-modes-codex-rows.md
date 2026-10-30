---
role: session-modes
level: L1
model: gpt-6-astra
effort: medium
host: codex
task_set: T-0815 new session agent rows, no experiment
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-30
evidence: [docs/work/.0815-session-modes-agents/handoff.md, docs/reports/2026-10-28-speed-experiment.md]
---
## Method

No experiment. T-0815 Do 3 registers the new direct and hybrid session agents in the Codex mapping, which needs a models.json row each. The ticket names no model, so both rows copy the conductor row (gpt-6-astra at effort medium) because they fill the same session slot; the user may override them.

## Result

The Codex table gains direct L1 and hybrid L1, both gpt-6-astra medium. No other row changed, and the Claude table is unchanged (both agents pin opus medium in their own front matter, as the conductor does). No pass rate or cost was measured; live behavior is not proven by this record.
