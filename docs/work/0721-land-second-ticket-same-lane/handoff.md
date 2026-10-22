---
id: T-0721
title: "fanout.py land closes a second lane ticket whose commits an earlier land merged"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
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

## Outcome
- Fix: `fanout.py land_ticket` no longer stops at `no changes` when the lane branch adds nothing but `carrying_merge` finds the integration merge that brought its tip in (tip under the merge's second parent, not its first) and the ticket is still open on the integration branch. It falls through to `merge_gate_close` (merge up to date, gates skipped), closes the ticket, and the Commit cell shows that merge. `close_reason` appends `; commits carried by merge <sha>` with no `landed` wording, so `tickets.py close`'s ancestry check does not apply. A stub that never committed stays `no changes` (case 24).
- Test: selftest case 32b reproduces issue #56 (two-ticket lane from prep's `lanes.py open` line, one commit per ticket, land A then land B) and expects B closed naming the merge and the lane closed.
- Negative control: with the carried branch disabled the selftest fails with `case 32b carried: after land A, land B closes B naming merge c5b1455 and closes the lane, got ... land B rc=1 ... T-0002 | no changes ...`.
- Checks: `fanout.py selftest` through gate_lock exit 0 (PASS), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check 9fd99a3c` exit 0.
- Docs: fanout.py land docstring and case list, `docs/references/sdlc-internals.md`, `skills/fanout/references/land.md`.
- Open: a filer-closed ticket (`--filer`) names the merge only in the report's Commit cell, not the close reason. `roll_ticket` has the same `no changes` short-circuit (out of scope). A lane ticket that committed nothing itself, sharing a lane with a landed sibling, now closes too: land cannot tell its commits apart.
