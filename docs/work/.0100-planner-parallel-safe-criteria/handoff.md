---
id: T-0100
title: "Planner criteria that break under parallel lanes: stale shas, fixed set counts, global aggregates"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
Plan criteria stay valid while other lanes change main.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui, 2026-09-25: about 20 builder stops across 12 gen-ui-system-svelte-lite lanes in one day. Each class cost a stop plus a conductor decision. Ticket ids in parentheses are gen-ui's.

Planner rules, each lintable in `steps.py split`:
1. Guards compare against HEAD at build start, never a sha fixed at plan time. `git diff --quiet <sha> -- ...` goes stale on the first main sync (T-0111, steps 1 and 2).
2. No hard-coded counts over a ticket set that other lanes change ("26 port handoffs"). Derive the set at run time (T-0164 step 4).
3. A criterion over a generated or aggregate budget (catalog token size, exact deviation lists) belongs only to the ticket that owns that budget. Other tickets check only their own delta ("adds no new deviation") (T-0164 step 5, T-0044, T-0146).

## Constraints
The failing test lands before or with the fix, never after.
