---
id: T-0143
title: "step 2's fix picking the correct result event from a stream-json..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0105
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0105 (find-out-why-the-t/filer-L1-3.md):

step 2's fix (picking the correct result event from a `stream-json` log) rests on the assumption that `claude -p --output-format stream-json --verbose` emits one `result` event per turn, including task-notification turns; this is proven only against stubs, never against a real run that ends in a task notification (both the planner's Risks and step 2's builder Notes flag it, and a live repro was explicitly out of scope for this task) — worth deciding whether to schedule that live confirmation.

## Constraints
What must not change. "None" if none.

## Closed

2026-09-27: Confirmed live 2026-09-27: claude -p stream-json emits one result event per turn incl. the task-notification turn; last one carries the final answer
