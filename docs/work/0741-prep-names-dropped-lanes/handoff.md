---
id: T-0741
title: "fanout.py prep names every ticket it leaves out"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py prep` never drops a requested lane silently: each ticket it does not plan is named with the reason (lane cap, load cap, overlap, or other), and a cap that drops a lane is visible in the exit output.

## Intent
- Do: Find why `prep d=T-0298 e=T-0299` planned one lane (`lane cap: 1 lane(s) of at most 4`) with no line for T-0299 (`fanout.py` about lines 1209 and 2241, and the T-0700 load cap). Print `not planned: <ticket> (<reason>)` for each dropped ticket.
- Non-goals: the other parts of the same issue.
- Done when: the criteria pass.

## Context
GitHub issue #69 (quoted):

> **Version:** sdlc-lite 0.33.0. Seen in ui-kit-neue 2026-10-22.
>
> **What happened**
> `fanout.py prep d=T-0298 e=T-0299 --base main --integration fanout/2026-10-22d --lanes-dir <root>/fanout-d --gate ... --light-gate ...` exited 0. It planned and wrote a dispatch record only for T-0298 and printed `lane cap: 1 lane(s) of at most 4`. T-0299 got no lane, no dispatch record, and no warning or refusal. The same happened with different lane names (`webkit=T-0298 fxtabs=T-0299`). Run on its own, `prep fxtabs=T-0299` with the same arguments planned it normally.
>
> Both tickets were size L2, status ready, committed on main, with no `depends:`. Prep reported overlap as `none`, plus `not planned, checked at merge time: T-0298`.
>
> **Expected**
> Both lanes are planned, or prep refuses (exit 2) and names why the second ticket was left out.
>
> **Workaround used**
> Ran prep once per ticket.
>
> **Ask**
> Find why the second lane is dropped. A silent drop must at least print a line naming the ticket and the reason.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Cause: `fanout.py prep` `load_cap` (T-0700) trims `ctx['lanes']` to the first regular lane when the load is over `max_load`; it printed only `prep: load <x> over <max>: opening 1 of <n> lanes`, and `print_prep` then showed `lane cap: 1 lane(s)` with no line for the other tickets.
Change: `load_cap` records `ctx['dropped']` (each ticket of the lanes it removes, reason `load cap: load <x> over <max>; --force opens all <n> lanes`); `print_prep` ends with `not planned: <ticket> (<reason>)` per dropped ticket. The `--max-lanes` overflow already refuses with exit 2.
Selftest: new case 22 expectation (T-0741) on the busy-load prep. Red before the change and with the change reverted: `FAIL: case 22 prep load cap names each dropped ticket (T-0741): busy prep ends with a `not planned:` line per dropped ticket ...`. Green with it.
Checks: fanout selftest via gate_lock exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 8f08aaab` exit 0.
