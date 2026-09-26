---
id: T-0107
title: "Role throwaway worktrees created outside $SDLC_TMP_WORKTREES for..."
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

Role throwaway worktrees created outside `$SDLC_TMP_WORKTREES` (for example in `/tmp`) or with `-b` are never cleaned, and `-b` leaves its branch behind; add a guard or a check that detects them.

## Constraints
What must not change. "None" if none.
