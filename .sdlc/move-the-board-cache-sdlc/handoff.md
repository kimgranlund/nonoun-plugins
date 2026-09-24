---
id: T-0019
title: "Move the board cache .sdlc/.board-state.json out of the working..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0018
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0018 (gitignore-board-state/filer-L1.md):

Move the board cache `.sdlc/.board-state.json` out of the working tree so `/board` never dirties a repo, even one that doesn't use the recommended ignore lines (needs changes to board.py and statusline.sh).

## Constraints
What must not change. "None" if none.
