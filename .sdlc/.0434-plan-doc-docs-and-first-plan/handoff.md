---
id: T-0434
title: "Docs and the first customer plan doc (goal 002 wrapped)"
type: chore           # feature | bug | chore | spike | idea
status: done
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0433]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Ticket D of the design: the docs state the built contract and the goal 002 plan is wrapped as the first customer plan doc.

## Intent
- Do: row D of section 8: set docs/specs/sdlc-lite/plan-doc-executor.md to built; update docs/specs/sdlc-lite/README.md, the docs/README.md row and the managed block of docs/specs/sdlc-lite/AGENTS.md through `onboard.py` in this repo (allowed under the T-0419 rule: managed blocks only, after check and a dry run); write `.sdlc/plan-reliability-docs/plan-doc.md` wrapping the goal 002 plan in the contract.
- Non-goals: running the goal 002 plan (the maintainer picks the driver and is present); any code change.
- Done when:
  - `docs_check.py --root .` exits 0 and `plan_check.py plan .sdlc/plan-reliability-docs/plan-doc.md --run` exits 0; `plan_done.py` on it exits 1 and lists the open steps; onboard.py check shows no stale managed block for the files touched; no dashes.

## Context
Maintainer approved building T-0410 on 2026-10-10 (the plan-doc workflow: plan with a session, then tell a smaller faster model `/goal complete build and verify <plan-doc.md>`). Design: docs/specs/sdlc-lite/plan-doc-executor.md (sections 3 to 8). Defaults taken from its section 10: the driver for the first run is Sonnet high, Haiku 5.5 is not added as a worker row, an L1 step has no independent verifier by default.

## Constraints
No em or en dashes. No push or publish. No model, effort, levels.json or models.json change. The design is the contract; if it is wrong or silent, stop and report a plan defect. One writer at a time on check.py and check.sh: this ticket runs in the same lane as its predecessors. Close-first: run the Done-when checks once, fix what fails, report.

## Closed

2026-10-10: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
