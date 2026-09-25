---
id: T-0056
title: "filer-L1.md stays uncommitted in a lane worktree, so close on main finds no filer file"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
close on main finds the filer record of work done in a lane worktree.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

/chain commits only on a step pass and the filer runs after the last step, so filer-L1.md stays uncommitted in the lane worktree, the merge to main misses it, and close on main says "no filer-L*.md". Suggested: /file commits its record, or close names the worktree holding it.

## Constraints
The failing test lands before or with the fix, never after.
