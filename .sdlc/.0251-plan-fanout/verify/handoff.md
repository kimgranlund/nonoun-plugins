# Verify plan skills (T-0249, T-0250, T-0251), commit 64da232

Independently check, running the commands yourself. Never edit code.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` passes and its assertions are real (read plan_check.py selftest for vacuous ones).
2. Each of plugins/sdlc-lite/skills/plan-goal, plan-loop, plan-fanout has a SKILL.md and references file; no `harness:` text (grep); each has a Codex-host line, argument-hint, and a read-only tool list plus AskUserQuestion.
3. Feed the example block in plan-goal/references/goal-rules.md and plan-loop/references/loop-rules.md to plan_check.py: pass. Mutate each (remove Done when; use `20mins:` as the interval; remove the dry-run line in a fanout block): each is rejected with a FAIL.
4. `python3 plugins/sdlc-lite/scripts/check.py`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `git diff --check` pass; guard 30 negative controls fire (temporarily break a copy, not the repo).
5. docs/reports/plan-skills-live-run.md claims are supported by its committed files in plan-skills-live-run.d/ and by running plan_check.py on them; flag anything overstated.
6. Skill statements match fanout.py facts (caps 4 and 16, stagger 20, tiers $5/$30/$60 in budget.py).
## Verdict contract
Return ## Verdict pass or fail with evidence per criterion.
