---
id: T-0090
title: "fanout default lanes dir becomes <toplevel>/.worktrees/fanout/<lane>"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A repo's fanout lane worktrees live inside it, under a gitignored `.worktrees/fanout/<lane>`, not in a sibling `<toplevel>-fanout` dir.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
User request relayed 2026-09-25, following the ultimate-tokens convention. Requirements:
- fanout.py's default `--lanes-dir` becomes `<toplevel>/.worktrees/fanout`, and `--lanes-dir` stays as the override.
- Preflight refuses, naming the fix, when `.worktrees/` is not ignored (`git check-ignore -q .worktrees/x`).
- The docs (skills/fanout, CLAUDE.md) say that .gitignore does not exclude `.worktrees/` from vitest, tsc or file watchers, and that Node module resolution walks up into the main tree's node_modules.
- Update anything left stale by the sibling convention: CLAUDE.md, the sdlc-lite-author agent, and the fanout selftest's default-dir expectations. The user-level git-bare-repo-setup skill lives outside this repo, so note any stale line for the user instead of editing it.

## Constraints
What must not change. "None" if none.
