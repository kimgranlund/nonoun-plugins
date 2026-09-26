---
id: T-0108
title: "A dry run of a role whose agent declares skills planner, architect..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0095
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0095 (role-worktrees-left-behind/filer-L1.md):

A dry run of a role whose agent declares skills (planner, architect, verifier) leaves its `mktemp` skill file behind in `run.sh`; remove it on dry-run exit.

## Constraints
What must not change. "None" if none.
