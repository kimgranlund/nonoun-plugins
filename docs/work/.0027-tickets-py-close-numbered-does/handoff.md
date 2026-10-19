---
id: T-0027
title: "tickets.py: close --numbered does not persist ticket_folders..."
type: idea            # feature | bug | chore | spike | idea
status: dropped
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0024
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0024 (numbered-mode-not-persisted/filer-L1.md):

tickets.py: `close --numbered` does not persist `ticket_folders: numbered`, so a repo that only ever ran `close --numbered` stays in plain check mode

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: merged into T-0026 (numbered mode persists its config from every entry point).
