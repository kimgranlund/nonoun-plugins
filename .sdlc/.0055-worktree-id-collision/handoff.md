---
id: T-0055
title: "Ticket ids collide across parallel worktrees"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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

## Clarified (unattended, by the conductor)
- Root goal: `tickets.py new` and `close` (follow-up filing) never hand out an id already used by a ticket in any worktree of the same repo, and a merge that still carries duplicate ids is caught.
- Scope: (1) id allocation takes the max id across the current root and the same-relative `.sdlc` root of every tree in `git worktree list` (falls back to the local root outside git or when git fails); (2) `tickets.py check` fails on two tickets sharing one id, naming both folders (`problems()` already reports `duplicate id`; confirm a selftest case covers it, add one if not); (3) `selftest` proves both. Keep CLAUDE.md, the sdlc-lite-author agent, and the ticket skill docs in sync with the new behavior.
- Done when: a test with two worktrees (or two roots simulating them) shows the second `new` gets a fresh id, `check` fails on a duplicate id, and `scripts/check.sh` passes.
- Gap named, not blocking: the Repro/Expected/Actual sections were left as template text; the Context paragraph above is the repro. Branches not checked out in any worktree cannot be seen at allocation time; the `check` duplicate gate covers them after merge.
