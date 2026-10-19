---
id: T-0294
title: "Plan review only for L4 and L5 steps"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Plan review (`plan-reviewer`) runs only for plans that hold an L4 or L5 step. A plan whose steps are all L1 to L3 skips it, and the reviewer's readiness concerns become builder notes. USER DECISION (agent-ui root-cause: 25 plan reviews cost $186, many repeated builder-readiness findings). Independent review stays for L4 and L5.

## Context
`review_required()` in plugins/sdlc-lite/scripts/steps.py (used by `steps.py review` and `lane`) currently also requires review for a planner L3 plan, two or more planner results (a replan), a Merge step, or a `## Plan review` line in handoff.md. Callers and text: skills/chain, agents/conductor.md, agents/planner.md if it mentions review, docs/lean-sdlc/design.md, skills/level-rubric/SKILL.md (all under plugins/sdlc-lite except docs/). Do not change any model or effort value in run.sh, adapters/codex/models.json, or the rubric tables. If agent bodies change run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. An `unresolved:` assumption keeps routing to `stop`.

Rule: review iff some step is `level: L4` or `L5` (a Merge step is L4 or higher by its template). Planner level, replans, and a `## Plan review` line no longer trigger review on their own. Keep `steps.py lane` consistent (it uses `review_required`).

## Requirements
- `steps.py review` prints `split` for an L1 to L3 plan including a planner-L3 plan, a replan, and a `## Plan review` handoff line, and keeps the existing review flow for L4 or L5.
- chain skill and conductor text: dispatch plan-reviewer only for a plan with an L4 or L5 step; otherwise turn the planner's open readiness concerns into `## Notes` for the builder.
- docs/lean-sdlc/design.md and the level-rubric text state the rule.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a new case: an all-L1-to-L3 plan (including planner L3) prints `split`; a plan with an L4 step and a plan with an L5 step each still print `review L1`.
- [ ] Negative control shown once: with the old rule restored, the new L1-L3 case fails.
- [ ] Each of skills/chain/SKILL.md, agents/conductor.md (both under plugins/sdlc-lite), docs/lean-sdlc/design.md, and skills/level-rubric/SKILL.md states plan review is for L4 and L5 steps only (grep output in the report).
- [ ] No diff to the run.sh role:level model/effort rows, adapters/codex/models.json, or the level rubric's model table; `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
