---
id: T-0124
title: "Gate guards on every step block on inherited red; a final gates-green step instead"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Inherited red never blocks a step whose own work is green.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

The four-gates guard on every step blocks on red that earlier steps or the merged main introduced (T-0238 step 4, T-0235 step 4). The verifier now reports inherited red (T-0114, which is in the current batch). The remaining proposal: the planner puts the full gates guard on one final "gates green" step instead of on every step.

## Constraints
The failing test lands before or with the fix, never after.
