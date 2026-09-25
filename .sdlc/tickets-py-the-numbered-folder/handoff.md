---
id: T-0033
title: "tickets.py: the numbered-folder warning in check gives a false..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
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
