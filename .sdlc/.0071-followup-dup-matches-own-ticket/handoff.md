---
id: T-0071
title: "tickets.py close marks follow-ups as duplicates of the ticket being closed when their slug base equals its slug"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0064
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Close a ticket whose slug is `merge-step-conflict-marker-guard` with a filer follow-up whose title starts "Merge-step conflict-marker guard ...".
2. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc close <slug> --dry-run`

## Expected
A follow-up is only a duplicate of some other ticket; the ticket being closed is excluded from the duplicate set, so new follow-ups are filed.

## Actual
```
1. Merge-step conflict-marker guard still flags a line on the lane... [merge-step-conflict-marker-guard] duplicate of T-0064 (merge-step-conflict-marker-guard)
2. Merge-step conflict-marker guard's xargs empty-input branch was... [merge-step-conflict-marker-guard] duplicate of T-0064 (merge-step-conflict-marker-guard)
```
The real close then filed 0 follow-ups; T-0069 and T-0070 were stamped by hand.

## Context
Found closing T-0064 (2026-09-25). Guess: the follow-up slug is derived from the first title words, which here equal the parent slug, and the duplicate check (`tickets.py` around line 530) compares against every ticket including the one being closed. A slug collision between two distinct follow-ups may also need a suffix.

## Constraints
The failing test lands before or with the fix, never after.
