---
id: T-0229
title: "Solo start has no budget gate, and /agent solo without a ticket is unmetered"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Starting a solo session (conductor Bash start, fanout solo lane, `/agent solo`) checks the ticket's budget first and stops at 80 percent as `run.sh` does for roles, and `/agent solo` without a named ticket still records its cost.

## Intent
- Do: (1) in `solo_run.py` (and fanout's solo start, which goes through it) call the same budget check `run.sh` uses (`budget.py status`, exit 4 at 80 percent, `budget.py ack` to continue) before launching the session, with the same messages and an `--ack` path; a ticket with no budget field is not blocked. (2) `/agent solo` with instructions that name no ticket: have the skill create a small task folder with a `handoff.md` from the instructions (as it already does for the read-only roles) so the wrapper can write a record, or record cost in a documented fallback location that `budget.py` and the board read; pick the smaller. (3) Selftests with negative controls: a ticket seeded past 80 percent refuses to start a solo session and an acked one starts; `/agent solo` leaves a `role solo` record. (4) Update agents/solo.md and docs/maintenance/sdlc-internals.md only where they claim the budget gate counts or stops the default lane. check.py guard with the next free item number.
- Non-goals: model or effort defaults; a version bump, tag, push, or publish.
- Done when: both behaviors are tested with negative controls, a real headless solo start on a throwaway over-budget ticket is refused and an acked one runs (about $3), and an independent verifier passed with an overall pass.

## Context
Found by the post-publish fact-check of release 0.20.7 (findings 7 and 8): metering happens only after a solo session ends, and no stop applies before it starts, so a ticket already over budget still starts solo; the release notes read as if the 80 percent stop applies to the default lane. Size M, solo lane, P1. Goes in 0.20.8. Philosophy: "Done is better than perfect."

## Constraints
Reuse the existing budget code, do not fork it. No em dashes.
