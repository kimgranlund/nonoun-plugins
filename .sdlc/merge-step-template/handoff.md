---
id: T-0059
title: "Standard merge-branch step template for builders"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
Merging two lanes is a standard builder step with criteria it can meet.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

A merge conflict between lanes needed a hand-written handoff, and the builder correctly blocked on an unmeetable criterion. Suggested: a `merge <branch>` step template with criteria: no conflict markers, gates green, two-parent commit.

## Constraints
What must not change. "None" if none.
