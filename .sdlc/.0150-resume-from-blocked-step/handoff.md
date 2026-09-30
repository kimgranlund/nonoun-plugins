---
id: T-0150
title: "Resuming a chain restarts at the blocked step, not the newest step"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
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
After an earlier step blocks, a resumed /chain rebuilds from that blocked step; it never builds a later step first. Before choosing the step, use `run_lifecycle.py recover <handoff-directory>` for a stale attempt when explicit recovery is required (especially Codex native), and inspect its artifacts. Confirm first whether steps.py next already chooses the blocked step; gen-ui worked around it with a local stepn.sh.

## Actual
Paste the output or error verbatim.

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 4 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
The failing test lands before or with the fix, never after.
