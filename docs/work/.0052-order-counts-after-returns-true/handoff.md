---
id: T-0052
title: "order.counts_after returns true when either file has no runs.jsonl..."
type: idea            # feature | bug | chore | spike | idea
status: dropped
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0049
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0049 (newest-by-mtime/filer-L1.md):

order.counts_after returns true when either file has no runs.jsonl record, so a stale unrecorded verifier can still show pass over a newer recorded build on the board.

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: fallback design question; the T-0049 review showed correct verdicts.
