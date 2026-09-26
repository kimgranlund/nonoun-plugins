---
id: T-0131
title: "The reference scan still treats another tree's .sdlc/0003-x as a..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0118
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0118 (the-reference-scan-matches-only/filer-L1.md):

The reference scan still treats another tree's `.sdlc/0003-x` as a reference, and `.sdlc/0003-xy` as a match for `0003-x`. The literal-substring rule was kept per the T-0118 Constraints, which contradicts the Deltas rule that a path resolving elsewhere is not a reference.

## Constraints
What must not change. "None" if none.
