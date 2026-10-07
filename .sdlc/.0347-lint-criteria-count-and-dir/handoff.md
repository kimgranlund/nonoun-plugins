---
id: T-0347
title: "steps.py lint flags criteria that cite a count or `node --test <dir>` without a named source"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0342]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
steps.py lint flags criteria that cite a count or `node --test <dir>` without a named source

## Intent
- Do: Two false verifier fails came from steps.py criteria that cite a numeric count or the directory form `node --test dir` (maison). Add lint warnings (errors for the dir form) for numeric criteria without a named source file or command, and for `node --test <dir>`; keep existing lint behavior for everything else. First reproduce the reported behavior (the report is a conductor's account, marked [U]); if it cannot be reproduced on the current main, close with a note saying so instead of changing code.
- Non-goals: model or effort changes; anything outside the named script or hook.
- Done when:
  - steps.py lint selftest cases: the dir form fails, a bare count warns, a count with a named command passes. (observed, failing on the old behavior).
  - check.py, tickets.py check and the touched selftests pass.

## Context
From the maison conductor's upstream friction list of 2026-10-07 (about 40 sub-agent runs, no verification by me yet). Start after T-0342, which edits the same scripts and hook.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
