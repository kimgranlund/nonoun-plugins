---
id: T-0129
title: "Worktrees created from inside a script or program a role runs..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0107
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0107 (role-throwaway-worktrees-created-outside/filer-L1.md):

Worktrees created from inside a script or program a role runs (python, make) bypass the new block-stray-worktree hook, which only sees Bash tool text; add run-end detection or reporting for stray worktrees and branches.

## Constraints
What must not change. "None" if none.
