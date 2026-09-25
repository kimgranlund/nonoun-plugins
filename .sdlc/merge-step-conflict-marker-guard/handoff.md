---
id: T-0064
title: "Merge-step conflict-marker guard scans the whole tree when git diff..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0059
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0059 (merge-step-template/filer-L1.md):

Merge-step conflict-marker guard scans the whole tree when `git diff --name-only HEAD^1 HEAD` is empty and can flag legitimate lines starting with seven `<` or `>`; make it fail safe or skip on an empty path list.

## Constraints
What must not change. "None" if none.
