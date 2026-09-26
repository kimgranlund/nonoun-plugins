---
id: T-0111
title: "Pattern-kill hook misses forms it does not match: ps aux | grep x |..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0102
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0102 (builder-scope-hygiene/filer-L1.md):

Pattern-kill hook misses forms it does not match: `ps aux | grep x | awk ... | xargs kill` and a kill word held in a variable (`p=pkill; $p x`) pass inside role runs.

## Constraints
What must not change. "None" if none.
