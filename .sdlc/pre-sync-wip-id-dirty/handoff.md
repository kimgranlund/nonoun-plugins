---
id: T-0139
title: "Pre-sync wip<id>: dirty before sync commit in fanout.py run_ticket..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0126
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0126 (chain-stop-leaves-dirty-tree/filer-L1.md):

Pre-sync `wip(<id>): dirty before sync` commit in `fanout.py` `run_ticket` would be merged into the integration branch if that ticket then merges. It is unreachable today, but a lane with a dirty tree before its first ticket would trigger it; decide whether to guard or drop that commit from the merge.

## Constraints
What must not change. "None" if none.
