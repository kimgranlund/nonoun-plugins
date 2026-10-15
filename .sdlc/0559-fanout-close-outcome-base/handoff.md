---
id: T-0559
title: "Fanout closes write base: none and Commits: none in the Outcome"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
branch: lane/T-0559-w77-0559
worktree: .claude/worktrees/T-0559-w77-0559
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket closed by fanout gets the real base sha and commit list in its `## Outcome`.

## Repro
1. Close a ticket through `fanout.py run` or `land`, as T-0553 and T-0555 were.
2. Read the closed handoff's `## Outcome`.

## Expected
`base: <sha>` and `Commits: <sha> <subject>` lines.

## Actual
`base: none` and `Commits: none` (T-0545 builder report, 2026-10-14).

## Context
T-0543 writes the Outcome at close; the fanout close runs in the integration worktree, where the lane's base-sha record may not be copied (T-0542). Guess: the copy misses `base-sha`, or close reads the wrong records dir.

## Constraints
The failing test lands before or with the fix. Target 0.23.1.
