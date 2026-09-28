---
id: T-0152
title: "External agents (Codex) get lane integration and reserved ticket ids"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-28
---

## Goal
Branches owned by an outside agent can join fanout without hand-made lane/<x> refs, and ticket ids created on such a branch cannot collide with tickets.py ids (register the owner or branch, or reserve id ranges).

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From the gen-ui-system-svelte-lite overnight run 2026-09-28, feedback batch 3 item 9 (peer setup-sdlc-lite-generative-ui). Evidence is in that repo's lane logs.
## Constraints
What must not change. "None" if none.
