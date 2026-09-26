---
id: T-0110
title: "Decide how the pinned-sha lint should handle a deliberate commit..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0100
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0100 (planner-parallel-safe-criteria/filer-L1.md):

Decide how the pinned-sha lint should handle a deliberate commit reference such as `git merge-base --is-ancestor <real sha> HEAD`, which is now refused with no escape hatch.

## Decision (user, 2026-09-26)
Exempt only the ancestry form: `git merge-base --is-ancestor <sha> HEAD` passes the `pins_sha` lint (scripts/steps.py). Every other pinned sha (`diff`, `<sha>..HEAD`, `<sha>^`, and so on) is still refused. Add selftest cases for both, and update planner rule 6 and CLAUDE.md to match.

## Constraints
What must not change. "None" if none.
