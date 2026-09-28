---
id: T-0148
title: "Conductor scope decisions update the acceptance criteria, not just prose"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A conductor decision that widens a step's scope edits the scope guard the criteria read, so the next builder does not block on the old guard.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 1 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
What must not change. "None" if none.
