---
id: T-0857
title: "Keep tickets in docs/tickets instead of .sdlc folders"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Tickets live under `docs/tickets/` instead of `.sdlc/` folders.

## Intent
- Do: to be scoped with the user before work starts.
- Non-goals: none stated yet.
- Done when: to be scoped.

## Context
- User feedback, 2026-11-19, verbatim: "use /docs/tickets/ for tickets instead of .sdlc/ folders".
- Today the ticket root comes from `.sdlc/config` (`work_root`, `ticket_root`, `layout`); this repo uses `work_root: docs/work`. Open questions for scoping: whether `docs/tickets` becomes the default for new `onboard.py` installs, whether this repo migrates from `docs/work`, and where run records (`.sdlc/runtime/`) stay.

## Constraints
None stated.
