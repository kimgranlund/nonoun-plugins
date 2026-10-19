---
id: T-0318
title: "fleet_status.py render: ticket_root layout shows 60 done tickets as 'board still claims work' and prints a -0.1 load trend arrow"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The status render does not report closed tickets as open work and its load trend arrow is correct.

## Intent
- Do: Found by the 0.20.12 sanity run (docs/reports/release-0.20.12.md): on a repo using `ticket_root: tickets` (ui-kit-maison), fleet_status.py render lists 60 tickets as 'done, board still claims work', and the load trend prints an odd `→ -0.1`. Find the cause (the board source for that layout versus the ticket status files; the arrow thresholds) and fix both with selftest cases.
- Non-goals: new features; any model or effort change.
- Done when:
  - A fixture repo with `ticket_root: tickets`, closed tickets and a board file shows no stale `board still claims work` rows (red before, green after).
  - Load samples that differ by less than the flat threshold print a flat arrow, not a number; a clear rise or fall prints up or down (observed).
  - `fleet_status.py selftest`, `check.py` and `tickets.py check` pass.

## Context
Files: plugins/sdlc-lite/scripts/fleet_status.py and fleet_collect.py. Released in 0.20.12.

## Constraints
No em dashes. No push, tag or publish. Positive case and an observed negative control for any new check.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
