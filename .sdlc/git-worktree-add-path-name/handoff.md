---
id: T-0130
title: "git worktree add <path> <name> where <name> exists only as a remote..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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

`git worktree add <path> <name>` where `<name>` exists only as a remote branch can make git create a local tracking branch, but block-stray-worktree treats `<name>` as a commit-ish and allows it; close this gap, or require `--detach`.

## Constraints
What must not change. "None" if none.
