---
id: T-0322
title: "Make the flaky fleet_status selftest deterministic"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The flaky fleet_status selftest is deterministic.

## Intent
- Do: The 0.20.12 and subagent-mode merge agents saw `fleet_status.py selftest` fail once under heavy load on the negative control 'a third run with nothing changed lists no close and no state change', then pass on rerun. Find the time dependence and make it deterministic (injected clock or snapshot compare).
- Non-goals: the two verifier findings (T-0320 nameless entry line number, T-0321 interview read-through), which were filed separately by the T-0319 lane; any model or effort change.
- Done when:
  - fleet_status selftest passes 20 times in a loop under `nice` with a parallel CPU burner (observed).
  - The cause is stated in one line in the ticket notes.
  - `check.py` and `tickets.py check` pass.

## Context
Scope reduced on 2026-10-06 after the followups lane filed T-0320 and T-0321 for the verifier findings (A4, B3). File: plugins/sdlc-lite/scripts/fleet_status.py.

## Constraints
No em dashes. No push, tag or publish.
