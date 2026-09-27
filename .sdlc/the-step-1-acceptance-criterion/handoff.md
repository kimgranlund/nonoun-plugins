---
id: T-0146
title: "The step-1 acceptance criterion pattern git diff --stat HEAD | awk..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-27
from: T-0134
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0134 (mirror-the-extended-planner-rules/filer-L1.md):

The step-1 acceptance criterion pattern `git diff --stat HEAD | awk '{print $1}'` (unscoped file-change check) can never pass inside a `/chain` run because the pipeline's own uncommitted `.sdlc/<task>/` artifacts are always present in the tree; the planner should default to a `.sdlc/`-excluding scoped check (as used in this task's swap) whenever a step's acceptance criteria assert "only this file changed."

## Constraints
What must not change. "None" if none.
