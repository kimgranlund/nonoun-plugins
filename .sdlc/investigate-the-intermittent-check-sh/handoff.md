---
id: T-0133
title: "Investigate the intermittent check.sh failure hook selftest: FAIL..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0123
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0123 (replan-light-criterion-swap/filer-L1.md):

Investigate the intermittent `check.sh` failure `hook selftest: FAIL: block-pattern-kill without role: exit 141, want 0` (SIGPIPE, likely a timing race). It appeared on the built tree in the step 1 verification, and `hook-selftest.sh` alone passed 20 of 20.

## Constraints
What must not change. "None" if none.
