---
id: T-0731
title: "gate_lock status explains a load-cap stall"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When the queue waits on the load cap, `gate_lock.py status` shows how long it has waited and the top non-gate CPU consumers, so a stall caused by outside load is visible and actionable.

## Intent
- Do: In `gate_lock.py status` (and the waiting line `run` prints), add the queue wait time and the top 3 non-gate processes by CPU when the reason is the load cap. Admission rules stay as T-0697 set them.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #67 (quoted):

> **Observed**: with `max_load=10`, four non-test processes (hung browser tabs, about 4 cores) kept the 1-minute load near 10.5; `gate_lock status` showed 9 queued jobs and `waiting: load 10.8 over cap 10`, with nothing admitted for a long stretch.
>
> **Expected**: admission considers load from admitted gate jobs (or subtracts a baseline), or escalates a stall (print the top non-gate CPU consumers and how long the queue has waited).
>
> **Evidence**: `gate_lock.py status` on 2026-10-22 ~07:38 PDT.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `gate_lock.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
