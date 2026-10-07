---
id: T-0267
title: "A hook denies git worktree add with variable paths"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Find which hook denies `git worktree add` with variable paths and make it accept them or explain the denial.

## Context
A hook denies `git worktree add` with variable paths (`$d/x`); literal paths work. Reproduced in this session by a harness refusal of a loop with `git` and variables. Identify the owning hook (plugin hooks or host sandbox) before fixing.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
