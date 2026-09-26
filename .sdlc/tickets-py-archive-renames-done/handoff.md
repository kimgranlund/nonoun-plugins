---
id: T-0116
title: "tickets.py archive renames done/dropped numbered folders to the..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0113
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0113 (close-rename-breaks-refs/filer-L1.md):

`tickets.py archive` renames done/dropped numbered folders to the dot-prefixed form with no reference scan, so it can break committed references the same way `close` did.

## Constraints
What must not change. "None" if none.
