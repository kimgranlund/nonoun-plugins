---
id: T-0079
title: "close --dry-run lists open tickets from the local --root only, so..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0066
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0066 (file-semantic-duplicates/filer-L1.md):

`close --dry-run` lists open tickets from the local `--root` only, so `/file` cannot catch a follow-up that duplicates an open ticket in another worktree or on an unmerged branch (T-0066 plan risk).

## Constraints
What must not change. "None" if none.
