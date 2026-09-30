---
id: T-0153
title: "Ticket depends can name a capability or file, not only a whole ticket"
type: feature        # feature | bug | chore | spike | idea
status: ready        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
A ticket can depend on the specific fix it needs (a capability or file) instead of a serial integration ticket, so parallel work is not blocked until a human overrides the dependency.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 11 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
What must not change. "None" if none.
