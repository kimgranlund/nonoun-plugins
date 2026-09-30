---
id: T-0154
title: "Builders inside a lane leave nested tmp worktrees behind"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected
Throwaway worktrees a builder makes inside a lane (e.g. .worktrees/i1/.worktrees/tmp/builder-78490) are removed at the end of the run; none are left nested inside a lane worktree.

## Actual
Paste the output or error verbatim.

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 13 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
The failing test lands before or with the fix, never after.
