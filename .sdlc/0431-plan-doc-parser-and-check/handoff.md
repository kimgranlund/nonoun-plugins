---
id: T-0431
title: "Plan-doc parser and plan_check.py plan"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Ticket A of the design: a plan-doc parser and `plan_check.py plan` that lints the plan-doc contract (design section 3).

## Intent
- Do: build exactly row A of section 8 of docs/specs/sdlc-lite/plan-doc-executor.md: new `plugins/sdlc-lite/scripts/plan_doc.py`, the `plan` kind in `plan_check.py` (GOOD_PLAN, one mutant per rule of section 3.3, usage and docstring), the `check.sh` selftest line and the `check.py` item. Read sections 3 and 8 first.
- Non-goals: plan_done.py, the skills, any model or effort change.
- Done when:
  - `plan_check.py selftest` exits 0 and prints one case per rule of section 3.3, each mutant observed failing first; `steps.py lint` accepts the step blocks the parser extracts.
  - plan_check.py, plan_doc.py selftest, check.py, check.sh (shellcheck clean) and tickets.py check pass.

## Context
Maintainer approved building T-0410 on 2026-10-10 (the plan-doc workflow: plan with a session, then tell a smaller faster model `/goal complete build and verify <plan-doc.md>`). Design: docs/specs/sdlc-lite/plan-doc-executor.md (sections 3 to 8). Defaults taken from its section 10: the driver for the first run is Sonnet high, Haiku 5.5 is not added as a worker row, an L1 step has no independent verifier by default.

## Constraints
No em or en dashes. No push or publish. No model, effort, levels.json or models.json change. The design is the contract; if it is wrong or silent, stop and report a plan defect. One writer at a time on check.py and check.sh: this ticket runs in the same lane as its predecessors. Close-first: run the Done-when checks once, fix what fails, report.
