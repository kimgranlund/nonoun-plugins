---
id: T-0433
title: "The plan-doc and run-plan skills, with the live rehearsal"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0432]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Ticket C of the design: the `plan-doc` and `run-plan` skills, so a smaller model can run a plan document unattended, with the rehearsal and guardrail probes of section 8.1.

## Intent
- Do: build exactly row C of section 8 and sections 5 to 7: `skills/plan-doc/` and `skills/run-plan/` (SKILL.md plus references), the two routing rows in skills/sdlc-lite/SKILL.md with the Codex translations, one routing line in agents/conductor.md, `codex_roles.py generate`, and the check.py items. Skills are self-contained (check.py item 42). Then run items 1 to 4 of section 8.1 in a scratch project and write docs/reports/<date>-plan-doc-live-run.md: dry state, the throwaway two-step rehearsal driven by the cheapest candidate driver (Haiku 5.5 high), the crash drill, the guardrail probes. A step that cannot run is reported unverified, never substituted. Item 5 (the goal 002 run) is not part of this ticket.
- Non-goals: item 5; a levels.json or models.json row; hooks.
- Done when:
  - Both skills exist and route; claude_roles.py and codex_roles.py generate --check, check.py, check-packaging.py and tickets.py check pass; the live-run report exists with every probe's result or `unverified: <reason>`; no dashes.

## Context
Maintainer approved building T-0410 on 2026-10-10 (the plan-doc workflow: plan with a session, then tell a smaller faster model `/goal complete build and verify <plan-doc.md>`). Design: docs/specs/sdlc-lite/plan-doc-executor.md (sections 3 to 8). Defaults taken from its section 10: the driver for the first run is Sonnet high, Haiku 5.5 is not added as a worker row, an L1 step has no independent verifier by default.

## Constraints
No em or en dashes. No push or publish. No model, effort, levels.json or models.json change. The design is the contract; if it is wrong or silent, stop and report a plan defect. One writer at a time on check.py and check.sh: this ticket runs in the same lane as its predecessors. Close-first: run the Done-when checks once, fix what fails, report.
