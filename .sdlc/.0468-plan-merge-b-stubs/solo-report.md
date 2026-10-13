# T-0468 solo report

Files changed: 4 stub SKILL.md (plan-goal, plan-campaign, plan-doc, plan-fanout), 4 old references/ files deleted, scripts/check.py (items 31, 48, 51 retargeted, item 58 added), agents/conductor.md, skills/sdlc-lite/SKILL.md, skills/clarify/SKILL.md (dependent link), sdlc-conductor-l1.toml (regenerated), docs/README.md, docs/specs/sdlc-lite/plan-doc-executor.md and plan-verification.md (link targets), docs/references/plugin-compatibility.md (changelog and compatibility note), the handoff's Acceptance criteria.

Negative controls observed red on the real files: stub kind token replaced, regrown `## 1. Gather`, references/ folder regained, missing stub, plan skill without `references/plan-rules.md`, goal.md without `outcome-block.md`, doc.md without `Goal line`, conductor without `/sdlc-lite:plan doc`.

Spans:
`python3 plugins/sdlc-lite/scripts/check.py` exit 0
`python3 scripts/check-packaging.py` exit 0
`python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0
`test -z "$(git grep -l 'plan-goal/references\|plan-doc/references\|plan-campaign/references\|plan-fanout/references' -- plugins)"` exit 0
`test -z "$(ls plugins/sdlc-lite/skills/plan-goal/references plugins/sdlc-lite/skills/plan-campaign/references plugins/sdlc-lite/skills/plan-doc/references plugins/sdlc-lite/skills/plan-fanout/references 2>/dev/null)"` exit 0
`grep -c 'Redirect: run' plugins/sdlc-lite/skills/plan-goal/SKILL.md plugins/sdlc-lite/skills/plan-campaign/SKILL.md plugins/sdlc-lite/skills/plan-doc/SKILL.md plugins/sdlc-lite/skills/plan-fanout/SKILL.md` exit 0
`grep -c '/sdlc-lite:plan doc' plugins/sdlc-lite/agents/conductor.md` exit 0
`python3 plugins/sdlc-lite/scripts/rename_refs.py links` exit 0
`bash plugins/sdlc-lite/scripts/check.sh` exit 0
`codex_roles.py generate --check` exit 0
`rename_refs.py links` exit 0

verify: needed

verifier-L3 (first run): fail on criterion 7 only, a plan defect: the old span was green at the base. Span swapped as the verifier proposed; it ran green on the built tree and red at the base in the verifier copy. Criteria 1 to 6 and 8 passed. The verifier did not rerun check.sh (load); the solo log shows exit 0.
