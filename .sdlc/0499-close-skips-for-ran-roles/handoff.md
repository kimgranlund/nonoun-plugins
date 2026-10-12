---
id: T-0499
title: "tickets.py close: no skip entry required for a role with a run record (retro 12h row 6)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close` does not demand a `## Skipped` entry in `skips.md` for a role that has a run record in the ticket folder.

## Repro
1. A ticket on lane `full` whose folder holds `planner-L2.md` and `filer-L1.md` and a `skips.md` with only a `## Lane` entry.
2. Run `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc close <folder>`.

## Expected
The close proceeds: planner and filer ran, so nothing was skipped.

## Actual
`skips.md records lane full but has no ## Skipped entry for planner, filer` (seen in agent-ui on ui-product-card and ui-board-grid; the check lists roles as skipped even when they ran).

## Context
Evidence: `docs/reports/2026-10-12-fleet-retro-12.md` row 6, 4 extra commands per ticket. Find the check by grepping `no ## Skipped entry` in `plugins/sdlc-lite/scripts/tickets.py`. T-0443 (wave 46) also hit the message, but there the roles truly did not run and the refusal was right: keep that case refusing.

## Constraints
Red check: a `tickets.py selftest` case with run records and no skip line closes (red first), and a case with a role that neither ran nor has a skip entry still refuses.
