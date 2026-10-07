---
id: T-0330
title: "Verifier report is not on disk when dispatch.py record runs for a sub-agent"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
dispatch.py record finds the verifier report for a sub-agent dispatch, by an explicit path in the prompt that the sub-agent writes to before it ends; a selftest shows record rejecting a missing report with a clear message and accepting a present one.

## Intent
- Do: dispatch.py record finds the verifier report for a sub-agent dispatch, by an explicit path in the prompt that the sub-agent writes to before it ends; a selftest shows record rejecting a missing report with a clear message and accepting a present one.
- Non-goals: model or effort changes; the account-switch criterion.
- Done when:
  - The goal holds (observed); check.py, tickets.py check and the touched selftests pass.

## Context
Found by the live rerun appended to docs/reports/subagent-mode-live-2026-10-07.md (section `Rerun after T-0326 to T-0328`).

## Constraints
No em or en dashes. No push or publish.
