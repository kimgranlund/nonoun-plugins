---
id: T-0472
title: "tickets.py close accepts a stage-owned deferred criterion (T-0470 finding 2)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close` accepts a held criterion whose state is `deferred` and whose owner is a stage word, and records `deferred: <ref> -> <owner>` in the close note.

## Repro
1. In a throwaway ticket, write a verifier result whose only held line is `deferred integration` for a criterion declared `[owner: integration]`.
2. Run `python3 plugins/sdlc-lite/scripts/tickets.py --root <root> close <folder>`.

## Expected
The close succeeds and the note names the deferral.

## Actual
`criteria still held` (`tickets.py:1963-1966`); `Verdict` must read `fail` beside a held line (`results.py:254-257`).

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report section 'The 12 findings', item 2. Red check: the `tickets.py selftest` `(held)` case (`tickets.py:3122-3124`) run with `deferred integration`. `unmet-dependency` and a `T-NNNN` owner still refuse. The declaration wording in handoff-format and the planner is T-0461 scope, not this ticket.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.
