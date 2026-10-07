---
id: T-0331
title: "Sub-agent cost estimate still 8.5 percent of host after T-0328"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor and chain skills pass --transcript to dispatch.py record, the fanout path writes a priced solo row, and the estimate for the L2 and L3 verifier rows in docs/reports/2026-10-07-subagent-mode-live (host-cost.txt) is within 35 percent of host; where the transcript undercounts input and output tokens, apply and document a calibration factor fitted on those rows and state the fitted band in the report. Pillar: cost gates must not undercount spend.

## Intent
- Do: The conductor and chain skills pass --transcript to dispatch.py record, the fanout path writes a priced solo row, and the estimate for the L2 and L3 verifier rows in docs/reports/2026-10-07-subagent-mode-live (host-cost.txt) is within 35 percent of host; where the transcript undercounts input and output tokens, apply and document a calibration factor fitted on those rows and state the fitted band in the report. Pillar: cost gates must not undercount spend.
- Non-goals: model or effort changes; the account-switch criterion.
- Done when:
  - The goal holds (observed); check.py, tickets.py check and the touched selftests pass.

## Context
Found by the live rerun appended to docs/reports/2026-10-07-subagent-mode-live.md (section `Rerun after T-0326 to T-0328`).

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
