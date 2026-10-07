---
id: T-0328
title: "Sub-agent cost estimate is 7 to 12 percent of host and null for solo rows (T-0287 finding 4)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The sub-agent cost estimate is within the 35 percent band of the host figure for verifier and solo rows, and solo rows are no longer null.

## Intent
- Do: Finding 4 in docs/reports/2026-10-07-subagent-mode-live.md: the estimate was 7 to 12 percent of host because `subagent_tokens` excludes cache reads, and solo rows record null. Price from the transcript usage (input, output, cache read and write tokens) when the transcript is readable, else refit against host totals in docs/reports/2026-10-07-subagent-mode-live/host-cost.txt; record usage at solo completion. Done when the estimate for the L2 and L3 verifier rows in that folder is within 35 percent of host (computed from the stored records), solo rows carry a priced value, and the price table change is covered by a selftest.
- Non-goals: any model or effort change; the account-switch criterion of T-0287.
- Done when:
  - The observed result above holds; `check.py`, `tickets.py check` and the touched script selftests pass.

## Context
Found by the T-0287 live run on branch subagent-w5. Files: plugins/sdlc-lite/scripts/dispatch.py, cost code from T-0280.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
