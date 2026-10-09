---
id: T-0407
title: "Build the plan-verification skill and the two plan_check.py goal rules (design T-0405)"
type: feature        # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0406]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `plan-verification` skill exists as designed, `plan-goal` calls it, and `plan_check.py goal` rejects a goal with no Outcome and no Measured-by section.

## Intent
- Do: build exactly what docs/specs/sdlc-lite/plan-verification.md specifies: skills/plan-verification/SKILL.md and its references, the plan-goal change, the two new `plan_check.py goal` fail rules with a negative control each, the Codex mapping and generated files, and the migration note for existing goals. Change only the files the design names.
- Non-goals: other plan-* skills (the design says whether they follow later); model or effort changes.
- Done when:
  - plan_check.py selftest holds a positive goal block with the new sections and an observed-failing negative case per new rule.
  - plan_check.py selftest, check.py, claude_roles.py and codex_roles.py generate --check, scripts/check-packaging.py and tickets.py check pass.

## Context
Maintainer decision 2026-10-09: build the plan-verification skill (design T-0405). Needs T-0406 (plan-campaign, its check lives in plan_check.py too) merged first.

## Constraints
No em or en dashes. No push or publish. The design is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0; its goal block carries Outcome, Measured by, Rubric and Negative control, and each of the ten outcome-block mutants and the two done-measured mutants (tickets-only Done when, a different K id) is flagged as its rule.
2. A goal block without the outcome block, and one whose Done when only closes tickets, pass `check_goal` at the previous commit and are flagged `outcome-block` and `done-measured` now.
3. `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`, `claude_roles.py generate --check`, `codex_roles.py generate --check`, `python3 scripts/check-packaging.py` and `tickets.py --root .sdlc check` exit 0.
4. `skills/plan-verification/SKILL.md` and `references/outcome-block.md` exist; plan-goal reads the skill as step 2 and renumbers; the entry skill routes to plan-verification; the example in goal-rules.md passes `plan_check.py goal`.
5. Unverified: the design's live criterion (a `/plan-goal` run in a throwaway project) was not run.

## Closed

2026-10-09: delivered by the solo agent (level L2); verified pass by an independent L2 verifier
