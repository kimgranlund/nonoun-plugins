---
id: T-0136
title: "Decide whether path-scoped git status --porcelain -- <path>..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0125
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0125 (criteria-no-porcelain-clean/filer-L1.md):

Decide whether path-scoped `git status --porcelain -- <path>` emptiness criteria should be flagged when the path is one the step itself changes. Today they pass the lint and could still never pass.

## Constraints
What must not change. "None" if none.
