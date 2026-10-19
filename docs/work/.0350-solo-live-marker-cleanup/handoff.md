---
id: T-0350
title: "A conductor-path solo run clears its live marker, so later solos in the checkout do not default to a worktree for 6 hours"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Verifier finding 5

## Intent
- Do: Verifier finding 5. mark_live runs on every non-worktree sub-agent dispatch and only solo_run.py complete (or a 6 hour TTL) removes the marker; complete is called by fanout.py land only and no agent or skill text tells a conductor to run it. Fix: dispatch.py record clears the live marker for the solo it records (the stem and agent id are known there), the solo agent and conductor texts state the closing step, and the TTL stays as a backstop. Selftest: two sequential solo runs on one checkout, the second must not be forced into a worktree after the first recorded.
- Non-goals: model or effort changes; anything outside the named scripts and skills.
- Done when:
  - after one recorded sub-agent solo the next solo in the same checkout does not default to a worktree (observed, failing on the current main first).
  - check.py, tickets.py check, fanout, dispatch and solo_run selftests and `codex_roles.py generate --check` pass.

## Context
Independent verifier verdict on T-0343 to T-0348 (.sdlc/verify-maisonfix/verdict.md, Fable, 2026-10-07), findings numbered there.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
