---
id: T-0407
title: "Build the plan-verification skill and the two plan_check.py goal rules (design T-0405)"
type: feature        # feature | bug | chore | spike | idea
status: ready
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
