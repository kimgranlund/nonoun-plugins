---
role: session-modes
level: L1
model: gpt-6-astra
effort: medium
host: codex
task_set: T-0819 session agent rename, no experiment
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-30
evidence: [plugins/sdlc/adapters/codex/models.json, CHANGELOG.md]
---
## Method

No experiment. T-0819 renames the session agents conductor to factory and direct to live, so the Codex models.json rows are renamed with them; no model or effort value changes.

## Result

The Codex table keeps the same three session rows under the new keys: factory L1, live L1 and hybrid L1, each gpt-6-astra medium. The Claude table is unchanged. No pass rate or cost was measured.
