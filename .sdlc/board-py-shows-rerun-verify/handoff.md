---
id: T-0088
title: "board.py shows 'rerun verify' for a second no-verdict result in a..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0073
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0073 (verifier-no-verdict/filer-L1.md):

board.py shows "rerun verify" for a second no-verdict result in a row, but `steps.py next` returns `stop` for that case; make the board row say stop/ask the user so the two stay in sync.

## Constraints
What must not change. "None" if none.
