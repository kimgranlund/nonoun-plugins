# Agent prompt lint baseline, 2026-10-11

Recorded: 2026-10-11, tree at the T-0441 merge. Tool: `potency_lint.py` from the upstream `prompt-wording-rules` skill (commit 5f9819b86b4dc77934fd36226025cec2e2a88d81), run read-only from `/tmp/pwr`, never installed here. The lint is triage: it counts smells and cannot judge whether a line instantiates behavior. Budgets are the tool's defaults (prohibitions 5, NEVER 3, vague quantifiers 3, hedges 0, hard emphasis 3).

| File | Prohibitions | NEVER | Vague quantifiers | Hedges | Hard emphasis |
|---|---|---|---|---|---|
| `plugins/sdlc-lite/agents/builder.md` | 14 | 11 | 6 | 0 | 0 |
| `plugins/sdlc-lite/agents/solo.md` | 17 | 11 | 14 | 0 | 0 |
| `plugins/sdlc-lite/agents/verifier.md` | 15 | 12 | 6 | 0 | 0 |
| `plugins/sdlc-lite/agents/planner.md` | 36 | 33 | 6 | 0 | 0 |
| `plugins/sdlc-lite/agents/conductor.md` | 29 | 26 | 3 | 0 | 0 |
| `plugins/sdlc-lite/agents/plan-reviewer.md` | 8 | 8 | 4 | 0 | 0 |
| `plugins/sdlc-lite/overlays/builder.md` | 0 | 0 | 0 | 0 | 0 |

Reading: every role file is over budget on prohibitions and on NEVER; only the conductor is within the vague-quantifier budget; no file uses hard emphasis or hedges. The two new overlay sections are within every budget. Unverified: whether the counts predict behavior (T-0442 measures the overlays only); the budgets may be too tight for rule-heavy agents. Reproduce with `python3 -I /tmp/pwr/potency_lint.py <file>` after fetching the upstream script at the commit above.
