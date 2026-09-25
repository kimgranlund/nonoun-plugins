---
id: T-0054
title: "tickets.py load reads .NNNN-<slug> folders as tickets in plain mode..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0050
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0050 (dot-prefix-closed/filer-L1.md):

tickets.py `load()` reads `.NNNN-<slug>` folders as tickets in plain mode too, so a plain-mode repo that already has such a folder with front matter would start seeing it as a ticket; decide whether to gate this on numbered mode.

## Constraints
What must not change. "None" if none.

## Closed

2026-09-24: Decision: read .NNNN-slug folders as closed tickets in both modes; documented in skills/ticket and CLAUDE.md.
