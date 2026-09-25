---
id: T-0061
title: "Add a steps.py next <step dir> helper that reads the newest builder..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0060
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0060 (unpassable-plan-criteria/filer-L1.md):

Add a `steps.py next <step dir>` helper that reads the newest builder and verifier results through `order.py` and prints the next action. Today the plan-defect route is followed only by instruction in `/chain` and the conductor. That same channel was ignored in the second T-0060 report.

## Constraints
What must not change. "None" if none.
