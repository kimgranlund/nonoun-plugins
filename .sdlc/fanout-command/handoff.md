---
id: T-0058
title: "/fanout command for parallel lanes, with per-lane board view"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0055, T-0056, T-0059]          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Running ticket lanes in parallel needs no hand-written driver.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

Today each conductor rebuilds: one worktree per lane, sync from main before each ticket, /chain, /file, merge into main under a lock, gates on main, revert on red, close on main. Suggested: `/fanout <lane>=<ids>...` in the plugin, plus board.py showing each lane.

## Constraints
What must not change. "None" if none.
