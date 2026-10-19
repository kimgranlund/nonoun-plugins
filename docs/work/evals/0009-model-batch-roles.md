---
role: all
level: all
model: all
effort: all
host: all
task_set: maintainer decision 2026-10-12, no replay run
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-14
evidence: docs/work/NOTES.md
---
## Method

Maintainer decision dated 2026-10-12, recorded in docs/work/NOTES.md; no experiment was run for it. Rows changed in adapters/claude/levels.json and the run.sh mirror (old value to new value): planner L1 sonnet medium to sonnet high; planner L2 opus medium, unchanged; planner L3 opus xhigh to opus high; architect L1 fable high to opus xhigh; plan-reviewer L1 opus high to fable high; verifier L1 sonnet medium to opus low (L2 sonnet high and L3 fable xhigh unchanged); scout L1 claude-haiku-5-5 low to sonnet low; researcher L1 sonnet medium to sonnet high (L2 and L3 unchanged); filer L1 sonnet medium to sonnet low. Row changed in adapters/codex/models.json: scout L1 gpt-5.6-terra low to gpt-6.1-sol low. Front matter pins outside the table: messenger claude-haiku-5-5 to sonnet with effort low; conductor gains model opus and effort medium. Family rule widened with the rows: an Opus build moves an Opus verifier to Sonnet, and a Fable planner moves the Fable plan-reviewer to Opus, each at the same effort.

## Result

No replay or benchmark ran. The Pareto read behind the decision comes from third-party summaries of Artificial Analysis; it is secondary and unverified, and has no copy in docs/reports/. adapters/claude/prices.json was not recalibrated for the new rows. Live behavior of the new rows is not proven by this record.
