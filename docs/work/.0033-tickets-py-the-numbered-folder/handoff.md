---
id: T-0033
title: "tickets.py: the numbered-folder warning in check gives a false..."
type: idea            # feature | bug | chore | spike | idea
status: dropped
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0026
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0026 (tickets-py-check-should-warn/filer-L1.md):

tickets.py: the numbered-folder warning in `check` gives a false positive when every plain slug starts with 4 digits and a hyphen (e.g. `2024-plan`); consider requiring the prefix to match the ticket's front matter id

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: warning only, rare (every slug date-prefixed).
