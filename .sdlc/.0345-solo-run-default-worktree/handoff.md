---
id: T-0345
title: "solo_run.py run defaults to --worktree when another solo is live, so parallel solos never share the main checkout"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0342]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
solo_run.py run defaults to --worktree when another solo is live, so parallel solos never share the main checkout

## Intent
- Do: Parallel solo lanes spawned without --worktree share and switch the main checkout's branch and sweep each other's commits (maison). solo_run.py run should detect another live solo (lock or process) in the same checkout and default to a worktree for the new run, printing the choice; the existing --worktree and --no-worktree flags win. Related: T-0313 (conductor creates the lane worktree). First reproduce the reported behavior (the report is a conductor's account, marked [U]); if it cannot be reproduced on the current main, close with a note saying so instead of changing code.
- Non-goals: model or effort changes; anything outside the named script or hook.
- Done when:
  - a selftest starts two solo runs on one checkout and shows the second uses a worktree; a single run keeps today's behavior. (observed, failing on the old behavior).
  - check.py, tickets.py check and the touched selftests pass.

## Context
From the maison conductor's upstream friction list of 2026-10-07 (about 40 sub-agent runs, no verification by me yet). Start after T-0342, which edits the same scripts and hook.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
