---
id: T-0348
title: "tickets.py close offers a quiet --keep-refs so a doc citing the folder does not force --force"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0342]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
tickets.py close offers a quiet --keep-refs so a doc citing the folder does not force --force

## Intent
- Do: `tickets.py close` needs --force when any doc cites the folder (maison); we already have --rewrite-refs. Add --keep-refs (leave citing text as is, record the stale citations in the close note) or make the refusal message name both options and the exact command; do not weaken the reference-safety invariant in plugins/sdlc-lite/AGENTS.md. First reproduce the reported behavior (the report is a conductor's account, marked [U]); if it cannot be reproduced on the current main, close with a note saying so instead of changing code.
- Non-goals: model or effort changes; anything outside the named script or hook.
- Done when:
  - a selftest closes a ticket cited by a doc with --keep-refs and the close note lists the citing files; without a flag the refusal still happens. (observed, failing on the old behavior).
  - check.py, tickets.py check and the touched selftests pass.

## Context
From the maison conductor's upstream friction list of 2026-10-07 (about 40 sub-agent runs, no verification by me yet). Start after T-0342, which edits the same scripts and hook.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
