---
id: T-0101
title: "Builder reports inherited red when a gate is already red at the merge base"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A gate that main already made red is reported as inherited, not as a build failure or a plan defect.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer setup-sdlc-lite-generative-ui, 2026-09-25: about 20 builder stops across 12 gen-ui-system-svelte-lite lanes in one day. Each class cost a stop plus a conductor decision. Ticket ids in parentheses are gen-ui's.

A gate criterion ("npm test exits 0") can go red because of a main sync. Proposal: before claiming a failure, the builder runs the gate at the merge base. If it is already red there, Status is `inherited red: <tests>`, which routes to the conductor (not a replan, rebuild or bump). Needs a new status value in builder.md, steps.py next, board.py and chain (T-0133, T-0009, T-0044).

## Constraints
What must not change. "None" if none.
