---
id: T-0384
title: "steps.py lint rejects grep -P, which is vacuous on macOS"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A generated acceptance guard using `grep -P` is rejected by lint, because BSD grep on macOS has no -P and a negated pipeline then passes vacuously.

## Intent
- Do: scripts/steps.py lint rejects `grep -P` (and any `grep` option that BSD grep lacks and a negated pipeline would swallow) in a criterion or guard span with a message naming a portable alternative (python3 -c, or grep -E with a literal byte sequence); add one line to the planner rules and handoff-format template so planners stop writing it. Keep the existing guard-vacuity checks.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A lint selftest: a handoff with `! ... | grep -P '...\x{2014}'` is refused; the portable form passes (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Seen twice in maison: T-0286 verifier and T-0271 builder (guards passed vacuously on macOS). RCA ledger row 8. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.

## Closed

2026-10-08: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
