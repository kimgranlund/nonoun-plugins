---
id: T-0112
title: "Formatter rule is prompt-only: check.py proves only that the phrase..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0102
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0102 (builder-scope-hygiene/filer-L1.md):

Formatter rule is prompt-only: check.py proves only that the phrase is in builder.md, so a builder can still run a repo-wide formatter through a project script such as `npm run format`.

## Constraints
What must not change. "None" if none.
