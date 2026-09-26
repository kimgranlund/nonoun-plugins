---
id: T-0119
title: "fanout.py still reports only driver failed rc=<n> when a lane's..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0115
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0115 (fanout-py-treats-a-lane/filer-L1.md):

fanout.py still reports only `driver failed rc=<n>` when a lane's conductor exits non-zero after an inherited-red stop, so the inherited-red cause stays hidden in that case; detect it there too.

## Constraints
What must not change. "None" if none.
