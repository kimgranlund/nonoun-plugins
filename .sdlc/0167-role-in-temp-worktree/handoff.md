---
id: T-0167
title: "Document running a role from a temporary worktree"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
A conductor in a repository whose checkout must not be touched, such as a bare-clone layout with a dirty primary worktree, knows how to run a role from a clean temporary worktree and where `.sdlc/` state lives while it does.

## Intent
- Do: a documented recipe in the handoff-format run operations or in `/chain`: create a temporary worktree, run `run.sh` there, carry results back, remove the worktree.
- Non-goals: changing `fanout.py`, which already manages lane worktrees.
- Done when: the recipe runs end to end in a throwaway bare-clone repository with a dirty primary worktree, and the role's result and `.sdlc/` state are where the recipe says.

## Context
Source: the second report in T-0165, from the gen-ui-kit conductor session on 2026-09-29. The session reported that `run.sh` runs a role in the current directory and that there was no obvious clean place to run it.

`SDLC_TMP_WORKTREES` and the stray-worktree reporting already exist for runner-created worktrees. Check whether the recipe can reuse them.

## Constraints
Preserve user worktrees, branches, and stashes. Remove only worktrees the recipe created.
