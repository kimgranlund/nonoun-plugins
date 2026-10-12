---
id: T-0491
title: "fanout land gates run at --priority 1; gate_lock status shows ahead and blocking (T-0488, T-0470 finding 7)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A land gate runs at `--priority 1`, and `gate_lock.py status` shows `ahead` and `blocking` per queued row, so a merge gate is not queued behind a builder's checks and a waiter can see what holds it.

## Repro
1. `grep -n -- '--priority' plugins/sdlc-lite/scripts/fanout.py`.
2. Queue a land gate while another repo holds the slots; run `gate_lock.py status`.

## Expected
`gate_argv` passes `--priority 1` for a land gate; each queued row prints `ahead` (compute units held plus queued before it) and `blocking` (the holder names).

## Actual
No `--priority` anywhere in `fanout.py`, so a land gate queues at priority 0; `status` prints `age_s` and `waited_s` only (`gate_lock.py:712-726`).

## Context
Design: `docs/planning/merge-ops-and-queue.md` (Approach 3, later build C). Closes the remaining piece of T-0470 finding 7 (`docs/reports/2026-10-12-maison-wave-7b-mechanics.md`).

## Constraints
A `fanout.py selftest` case asserts the priority argument (red first) and a `gate_lock.py selftest` case asserts the two keys (absent today). No change to the capacity or default need.
