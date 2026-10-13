# T-0469 solo report

Files changed: scripts/plan_check.py (`--summary`, `cost_line`, `language_goal`, `language_plan`, `lang_warn`, selftest controls, GOOD_GOAL, GOOD_CAMPAIGN and GOOD_PLAN reworded to pass), skills/plan/SKILL.md (cost sentence), references/plan-rules.md, goal.md (example), campaign.md, doc.md, the handoff (Acceptance criteria, replay notes).

Controls observed red: with `lang_warn` and `cost_line` stubbed in place, the selftest failed 24 `language:` and `cost:` cases; restored, it passes (282 checks).

Spans:
`python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exit 0
`python3 plugins/sdlc-lite/scripts/plan_check.py goal --summary --root /nonexistent --text x | grep -q '^cost: unknown of unknown (0 tickets)'` exit 0
`grep -q -- '--summary' plugins/sdlc-lite/skills/plan/SKILL.md && grep -q -- '--summary' plugins/sdlc-lite/skills/plan/references/plan-rules.md` exit 0
`test -z "$(git diff --name-only -- plugins/sdlc-lite/scripts/check.py)"` exit 0
`python3 plugins/sdlc-lite/scripts/prompt_lint.py` exit 0
`python3 plugins/sdlc-lite/scripts/check.py` exit 0
`bash plugins/sdlc-lite/scripts/check.sh` exit 0
