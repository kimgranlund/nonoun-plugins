---
id: T-0151
title: "fanout.py never discards uncommitted edits when it resets the integration tree"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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
The red-gate `git reset --hard <pre-merge HEAD>` in fanout.py refuses, or stashes first, when the integration worktree has uncommitted changes, so a train revert never wipes a human's edits.

## Actual
Paste the output or error verbatim.

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 7 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
The failing test lands before or with the fix, never after.
