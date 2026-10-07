---
id: T-0085
title: "Recurring-finding rule: question the plan or rule, not the last attempt (planner replan, conductor escalation)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
When the same finding recurs, the chain asks whether the plan or rule is wrong before retrying.

## Intent
- Do: add a recurring-finding test to sdlc-lite's escalation doctrine. When a verifier fail (or a builder block) repeats the same class of finding as an earlier attempt on the same step (same criterion, same root cause) despite a rebuild that addressed it, the chain treats that as evidence the plan or a rule is wrong, not the last attempt: it goes to a planner L3 replan (like `plan defect:`) instead of a level bump, and the replan must first ask whether the criterion, step, or rule is wrong and land the answer as a concrete change (a rewritten criterion or step, or a stated reason the rule holds). Fold it into `plugins/sdlc-lite/skills/level-rubric/SKILL.md` (bump rule), `plugins/sdlc-lite/skills/chain/SKILL.md` step 4, `plugins/sdlc-lite/agents/planner.md` replan rules, and the conductor's escalation line in `plugins/sdlc-lite/agents/conductor.md`, keeping the four consistent. Include the lowest-order guard: most fails are ordinary; the test fires only on a recurrence, and the replan's answer must pay rent as a changed criterion, step, or rule (no commentary-only replan).
- Non-goals: porting the whole thinking-depth-rules skill (the n-order spectrum, 3rd/4th order triggers, anti-pattern table); any runtime code enforcing it beyond an optional `check.py` doc-presence guard; changing any level, model, or effort table; changing the `plan defect:` tag semantics.
- Done when: the four files state the recurring-finding rule consistently (recurrence → planner L3 replan that questions the plan or rule, not a bump; does not count toward a bump); `plugins/sdlc-lite/scripts/check.sh` passes; no new level/model/effort changes.

## Context
From peer projects-workspace-optimizer (user's workspace-optimizer session), 2026-09-25: port from harness@nonoun-plugins 3.19.6, which the user keeps disabled at user scope, so sdlc-lite must carry what it needs.

Source: ~/.claude/plugins/cache/nonoun-plugins/harness/3.19.6/skills/thinking-depth-rules/SKILL.md (87 lines). level-rubric escalates only by bumping a level after repeated fails. Fold the recurring-finding test into level-rubric / chain step 4 and the planner replan rules; do not port the whole skill.

## Constraints
What must not change. "None" if none.
