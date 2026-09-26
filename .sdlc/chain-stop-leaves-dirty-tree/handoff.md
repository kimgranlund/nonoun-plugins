---
id: T-0126
title: "A chain that stops mid-step leaves the tree dirty and blocks the next sync merge"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
A stopped chain never blocks the next sync.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

Uncommitted builder output blocked the next sync merge twice ("commit your changes before you merge"). Proposal: when /chain or fanout stops mid-step, it leaves a WIP commit on the lane branch (never on main), or a tagged stash. It must match the builder no-commit rule, since the chain commits, not the builder.

## Constraints
The failing test lands before or with the fix, never after.
