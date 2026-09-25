---
id: T-0046
title: "tickets.py selftest case m, empty --reason, passes without the new..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0037
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0037 (close-without-filer/filer-L1.md):

tickets.py selftest case (m), empty `--reason`, passes without the new code because it checks only rc 1 and an unchanged tree; also assert the "empty --reason" error text so the case proves the new refusal path.

## Constraints
What must not change. "None" if none.
