---
id: T-0096
title: "tickets.py selftest checks that the close --dry-run expect digest..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0079
---

## Goal
`tickets.py selftest` proves that the `close --dry-run` `expect <digest>` line is unchanged by other-worktree `open ... (worktree <name>)` lines when follow-ups are present, so the digest guarantee (it covers only the ordered follow-ups) is tested beyond the empty-follow-ups case. Done when the new selftest case passes and fails against a mutant that folds open lines into the digest.

## Context
Follow-up from T-0079 (close-dry-run-lists-open/filer-L1.md):

tickets.py selftest checks that the `close --dry-run` expect digest ignores other-worktree open lines only when there are no follow-ups (fixed `e3b0c44298fc`); add a case with follow-ups present so the digest guarantee is actually tested.

## Constraints
Test-only change to `plugins/sdlc-lite/scripts/tickets.py` selftest; no change to close/dry-run behavior or output. `plugins/sdlc-lite/scripts/check.sh` stays green.
