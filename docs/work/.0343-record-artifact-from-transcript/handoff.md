---
id: T-0343
title: "dispatch.py record writes the role artifact from the sub-agent transcript so no model Write is needed"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0342]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
dispatch.py record writes the role artifact from the sub-agent transcript so no model Write is needed

## Intent
- Do: Maison saw sub-agent final messages not reaching disk as <role>-<level>.md for planner, plan-reviewer, builder, architect (verifier sometimes) and had to message each to Write the file; notices truncate. Make `dispatch.py record` accept the agent transcript (it already takes --transcript for cost) and write the result file from the final assistant message when stdin is empty or truncated; the conductor path becomes first class (item 2 of the maison list: sub-agents that cannot Write findings or solo-result files, record writes the artifact). First reproduce the reported behavior (the report is a conductor's account, marked [U]); if it cannot be reproduced on the current main, close with a note saying so instead of changing code.
- Non-goals: model or effort changes; anything outside the named script or hook.
- Done when:
  - dispatch.py record writes <role>-<level>.md from the transcript's last assistant message; a selftest shows an empty stdin plus a transcript produces a valid result and a truncated message is rejected with a clear error. (observed, failing on the old behavior).
  - check.py, tickets.py check and the touched selftests pass.

## Context
From the maison conductor's upstream friction list of 2026-10-07 (about 40 sub-agent runs, no verification by me yet). Start after T-0342, which edits the same scripts and hook.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
