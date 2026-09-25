---
id: T-0055
title: "Ticket ids collide across parallel worktrees"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
No two tickets ever get the same id when worktrees file tickets in parallel.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

Each worktree allocates the next id from its own .sdlc/ (tickets.py new and close). Closing T-0033 in one worktree and T-0004 in another both file follow-ups from T-0050, and the merge carries two T-0050s. Suggested: allocate against the main tree or all `git worktree list` trees, or have `check` flag duplicate ids after a merge.

## Constraints
The failing test lands before or with the fix, never after.
