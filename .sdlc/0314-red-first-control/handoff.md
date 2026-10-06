---
id: T-0314
title: "Red-first control: a (red) criterion must fail at base and pass after, for solo and chain"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A criterion tagged `(red)` must fail before its step and pass after, checked mechanically for solo and chain tickets, so a vacuous criterion is caught without a plan reviewer.

## Intent
- Do: Add the `(red)` tag beside `(guard)` in criteria and a script `specgate.py red <task dir> [--step N] [--timeout S]` (or the solo equivalent in solo_run.py brief check) that runs each `(red)` span in the current tree and refuses a zero exit (`red-first: <criterion>` is green at base). For solo, accept `(red)` criteria in the ticket handoff `Done when` and have the solo agent body say to run `specgate.py red` before building and the criterion check after. For chains keep the original T-0211 behavior at split time. `steps.py swap` keeps tag parity for `(red)`.
- Non-goals: Judgment-only criteria; a mandatory red tag (it stays opt-in); any model or effort change.
- Done when:
  - A `(red)` criterion that is green at base is refused with its name (observed negative control); one that is red passes.
  - A span that changes the tree is refused (the snapshot restores it).
  - A swap that drops a `(red)` tag is refused.
  - A solo ticket fixture with a `(red)` criterion shows red before the build and green after (observed).
  - `check.py`, `tickets.py check` and the selftests pass.

## Context
Reconsidered 2026-10-06 from dropped T-0211 (see docs/reports/parked-tickets-review-2026-10-06.md and the old handoff .sdlc/0211-spec-gate-red). Evidence: agent-ui's report lists plan review catches such as vacuous loader scenarios; plan review now runs only for L4 and L5 steps, so L1 to L3 steps need a mechanical replacement. 2026-10-04 measurement: 4 of 7 plans returned for replan, about $190 over 78 role runs. The repo rule that a new check needs a positive and an observed negative control is the same idea applied to criteria. Owning files: scripts/specgate.py, scripts/steps.py, agents/solo.md and the generated per-level agents if bodies change, docs/sdlc-lite/cost-control.md.

## Constraints
No change to any model or effort value. No em dashes. No push, tag or publish. Independent verifier per ticket; checks need a positive case and an observed negative control.
