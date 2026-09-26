---
id: T-0121
title: "Pattern-kill hook does not catch a kill word assigned through a..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0111
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0111 (pattern-kill-hook-misses-forms/filer-L1.md):

Pattern-kill hook does not catch a kill word assigned through a substitution (`p=$(command -v pkill); $p x`), so it still passes inside role runs.

## Constraints
What must not change. "None" if none.
