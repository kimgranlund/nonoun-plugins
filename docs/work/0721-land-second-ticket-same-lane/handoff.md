---
id: T-0721
title: "fanout.py land closes a second lane ticket whose commits an earlier land merged"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
With two tickets in one lane (`lanes.py open --tickets A,B`), landing A then B closes B too, naming the merge that carried its commits, instead of `no changes` with B left open.

## Intent
- Do: In `fanout.py land`, when the lane has no new commits but the ticket is open and its commits are already in the target, close it with a reason naming that merge (and make the close reason pass `tickets.py close`'s ancestry check).
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #56 (quoted):

> ## What happened
> I ran two tickets in one lane: `lanes.py open rules --tickets T-0292,T-0297`, then one commit per ticket.
>
> 1. `fanout.py land fanout/<int>-rules --ticket T-0292` merges the lane branch, which carries both commits, and closes T-0292.
> 2. `fanout.py land ... --ticket T-0297` then reports `T-0297 | no changes` and leaves the ticket open, with `lane still open: ... (no changes)`.
> 3. A manual `tickets.py close 0297-... --reason "landed ... in 605a610"` refuses with "it claims the work is on main or landed but 605a610 is not an ancestor of main". The reason has to be reworded to avoid "landed".
>
> ## Expected
> When a later ticket's commits already arrived with an earlier merge from the same lane, `land` closes that ticket too, naming the merge that carried it. Or the first land closes every lane ticket whose commits it merged.
>
> ## Repro
> Open a lane with `--tickets A,B`, make one commit per ticket, land A, then land B.
>
> Seen on 0.30.0.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
