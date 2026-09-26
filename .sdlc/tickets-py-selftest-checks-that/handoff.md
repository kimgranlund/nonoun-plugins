---
id: T-0096
title: "tickets.py selftest checks that the close --dry-run expect digest..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0079
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0079 (close-dry-run-lists-open/filer-L1.md):

tickets.py selftest checks that the `close --dry-run` expect digest ignores other-worktree open lines only when there are no follow-ups (fixed `e3b0c44298fc`); add a case with follow-ups present so the digest guarantee is actually tested.

## Constraints
What must not change. "None" if none.
