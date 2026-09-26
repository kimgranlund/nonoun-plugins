---
id: T-0127
title: "fanout: make the resync retry limit configurable"
type: feature        # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P3         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Busy repos can raise the lane resync limit.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
From peer setup-sdlc-lite-generative-ui, overnight lanes on 0.11.1 (ids in parentheses are gen-ui's).

With many lanes touching shared registries (AGENTS.md indexes, generated files), 2 resync tries is too low; the peer raised it to 8 locally. Add `--resync-tries N` (default 2) or a config key.

## Constraints
What must not change. "None" if none.
