---
id: T-0319
title: "Independent verification of T-0307 and T-0310, which closed on the solo lane with no verifier verdict"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
T-0307 and T-0310 each get the independent verifier the repo rule requires.

## Intent
- Do: The 0.20.12 release agent found no verifier verdict for T-0307 (interview template) and T-0310 (fleet_config.py and fleet.json); both closed on the solo lane. Run one batched independent L3 verifier (different model family than the builder) against their acceptance criteria on the released tree, write the verdict under .sdlc/verify-fleet-0307-0310, and file any failure as a ticket.
- Non-goals: new features; any model or effort change.
- Done when:
  - A verifier result with `pass` or a list of failed criteria exists for both tickets.
  - Any failed criterion has a ticket and a one-line note in docs/reports/release-0.20.12.md follow-up section.

## Context
Both shipped in 0.20.12 with this limitation stated in the release record.

## Constraints
No em dashes. No push, tag or publish. Positive case and an observed negative control for any new check.

## Closed

2026-10-07: verification done: findings became T-0320 to T-0322, all closed
