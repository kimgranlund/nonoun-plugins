---
id: T-0138
title: "The steps.py lint does not check compound criteria with a trailing..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0093
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0093 (check-the-steps-py-lint/filer-L1.md):

The steps.py lint does not check compound criteria with a trailing redirect, such as `while read x; do ...; done < f`, because they do not end in `done`. Such a criterion can hold an unlinted `||` fallback.

## Constraints
What must not change. "None" if none.
