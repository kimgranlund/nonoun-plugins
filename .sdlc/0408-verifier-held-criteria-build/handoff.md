---
id: T-0408
title: "Build verifier unmet-dependency and deferred-to-owner verdicts (design T-0400)"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The verifier can report a criterion as `unmet-dependency <subject>` or `deferred <owner>` apart from `fail`, and a ticket cannot close while any criterion is unmet or deferred.

## Intent
- Do: build exactly what docs/specs/sdlc-lite/verifier-held-criteria.md specifies across scripts/results.py, agents/verifier.md (and its generated copies), the handoff-format skill, scripts/steps.py next-action routing, and the migration note for existing results. Include the negative control for premature closure.
- Non-goals: other verdict values; model or effort changes.
- Done when:
  - Selftest cases, each observed failing first: an unmet-dependency criterion routes to wait or reorder, not a replan; a deferred criterion is closed by its owner; a ticket with an unmet or deferred criterion is refused at close; existing pass and fail results still parse.
  - results, steps, dispatch and tickets selftests, check.py, claude_roles.py and codex_roles.py generate --check pass.

## Context
Maison and Codex, 2026-10-09: 11 component lanes failed on template rows 7 to 12 that a lane build cannot meet (2 to 3 hours). Design approved 2026-10-09 (T-0400); build approved in the same session.

## Constraints
No em or en dashes. No push or publish. The design is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.
