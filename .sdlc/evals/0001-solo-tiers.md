---
role: solo
level: all
model: gpt-6.1-sol
effort: all
host: codex
task_set: T-0215 user decision, no experiment run
pass_rate: 0/0
cost_usd: unknown
date: 2026-10-04
evidence: [.sdlc/0215-solo-operator-tiers/handoff.md, docs/other/orchestration-optimization-question.md]
---
## Method

No experiment ran. The user decided the solo tiers on 2026-10-04 (T-0215, recorded in .sdlc/0215-solo-operator-tiers/handoff.md) after the orchestration question in docs/other/orchestration-optimization-question.md, and asked to build before the solo-vs-lean benchmark finishes.

## Result

Adds the Codex solo entry to adapters/codex/models.json: L1 gpt-6.1-sol low (tier S), L2 gpt-6.1-sol high (tier M), L3 gpt-6.1-sol xhigh (tier L). No existing row changed. The Claude tiers (S Sonnet low, M Sonnet xhigh, L Opus xhigh) live in agents/solo.md, not run.sh.
