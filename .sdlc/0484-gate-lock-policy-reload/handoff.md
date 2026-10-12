---
id: T-0484
title: "gate_lock.py: a queued waiter rereads policy.json each poll, so a capacity change reaches it"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A gate_lock waiter already in the queue admits under a capacity set by `gate_lock.py policy set` after it queued, without a restart.

## Repro
1. Fill both slots (capacity compute_units 6, two grants of 3) and queue a third gate that needs 1 unit.
2. Run `gate_lock.py policy set compute_units=20`.
3. Watch `gate_lock.py status` for 30 seconds.

## Expected
The queued gate is admitted within a few polls (usage 6 of 20 fits).

## Actual
It stays queued. `run_top` (`gate_lock.py:622-640`) receives `pol` once at start and passes the same object to every `schedule(L, pol, legacy_n)` poll. Seen 2026-10-12 with maison and sdlc-lite waiters queued 15 minutes after the capacity went from 6 to 20.

## Context
Origin: maintainer raised the capacity to 20 (a 20-core machine) while wave 42 lane b and three maison gates were queued. Fix: load the policy inside the polling transaction (`load_policy(root)`), at the cost of one small file read per 0.2 s poll, or reread when the file mtime changes. Red check: a `gate_lock.py selftest` case that queues a waiter, runs `policy set`, and expects admission; red today.

## Constraints
Do not change the built-in capacity or default need. No behavior change for a waiter when the policy file is unchanged.
