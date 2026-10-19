---
id: T-0011
title: "Bring this repo's backlog under /ticket"
type: idea            # feature | bug | chore | spike | idea
status: dropped      # resolved in the T-0001..T-0006 merge review
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0002
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0002 (ticket-intake-roadmap/filer-L1.md):

Bring this repo's backlog under `/ticket`. It lives in flat files (`.sdlc/tickets/T-*.md`), and `tickets.py` does not scan them. Their ids also collide with task dirs (T-0002 is used by both). This is from the plan's Risks.

## Constraints
What must not change. "None" if none.
