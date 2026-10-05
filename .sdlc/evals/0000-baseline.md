---
role: all
level: all
model: all
effort: all
host: all
task_set: pre-eval-baseline
pass_rate: 0/0
cost_usd: unknown
date: 2026-09-30
evidence: [docs/reports/haiku-alias-2026-09-30.md, docs/reports/planner-l3-opus-2026-09-30.md, docs/reports/codex-account-models-2026-09-30.md]
---
## Method

No experiment was run. This record marks the model table, as it stood when evals.py landed, as the pre-eval baseline, decided by the three dated records cited as evidence.

## Result

- haiku-alias: the Claude scout runs the pinned `claude-haiku-4-5`, because the `haiku` alias ran Sonnet 5.5.
- planner-l3-opus: Claude planner L3 moved from Fable xhigh to Opus xhigh.
- codex-account-models: these are the Codex defaults in `models.json`, with `gpt-6.1-sol` as the verifier alternate.

No pass rate or cost was measured, and every later table change cites a newer eval.
