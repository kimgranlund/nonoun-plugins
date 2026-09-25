---
id: T-0030
title: "Board '· changed' markers silently stop working when the per-user..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0019
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0019 (move-the-board-cache-sdlc/filer-L1.md):

Board "· changed" markers silently stop working when the per-user cache dir is unwritable, because write failures are ignored; consider a visible hint.

## Constraints
What must not change. "None" if none.
