---
id: T-0120
title: "block-publish.sh: an option that takes a separate value word before..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0097
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0097 (block-publish-sh-no-longer/filer-L1.md):

block-publish.sh: an option that takes a separate value word before the inline-code flag (for example `python3 -X dev -c '...git push...'`) stops the interpreter match, so that command keeps the masked scan and a publish call can slip through

## Constraints
What must not change. "None" if none.
