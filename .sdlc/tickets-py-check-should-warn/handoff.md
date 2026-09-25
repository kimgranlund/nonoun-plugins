---
id: T-0026
title: "tickets.py: check should warn when every ticket folder has an NNNN..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0024
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0024 (numbered-mode-not-persisted/filer-L1.md):

tickets.py: `check` should warn when every ticket folder has an NNNN- prefix but `<root>/config` lacks `ticket_folders: numbered` (e.g. gen-ui-system-svelte-lite, whose numbered folders predate T-0024)

## Constraints
What must not change. "None" if none.
