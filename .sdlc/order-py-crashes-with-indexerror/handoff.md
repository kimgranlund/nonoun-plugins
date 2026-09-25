---
id: T-0051
title: "order.py crashes with IndexError when run with no arguments while..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0049
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0049 (newest-by-mtime/filer-L1.md):

order.py crashes with IndexError when run with no arguments (while printing its usage from `__doc__`) instead of printing usage and exiting cleanly.

## Constraints
What must not change. "None" if none.
