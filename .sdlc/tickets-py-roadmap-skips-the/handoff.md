---
id: T-0022
title: "tickets.py roadmap skips the numbered prefix/id check, so with..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0016
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0016 (ticket-numbered-folders/filer-L1.md):

tickets.py `roadmap` skips the numbered prefix/id check, so with `ticket_folders: numbered` set it can rebuild the roadmap while `check` fails

## Constraints
What must not change. "None" if none.
