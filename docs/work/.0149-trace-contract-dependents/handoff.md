---
id: T-0149
title: "A step that changes a shared contract pulls its dependents into scope"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
When a step edits a shared contract (a catalog entry, a type, an exported API), the planner or verifier finds its dependents (tests, fixtures, lint fixtures) and puts them in scope before a later step trips on them.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 2 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
What must not change. "None" if none.
