---
id: T-0579
title: "close --reason accepts a 'landed on main' claim that is false"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close --reason TEXT` refuses a reason that claims the work is on main or landed unless it names a commit that is an ancestor of the default branch.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 7. maison closed T-0573 as "landed on main", but its fix `fa6de2b8f` was not on main (their `.0573-*/handoff.md` `## Correction`). `--reason` skips the verdict gate, so nothing checked the claim.

## Intent
- Do: when the reason matches `on main` or `landed` (case-insensitive), require a sha in the text and `git merge-base --is-ancestor <sha> <default branch>`; otherwise refuse with exit 1 and say what is missing. `default_branch()` in `tickets.py` gives the branch.
- Non-goals: other reason wording.
- Done when: the criteria pass.

## Constraints
A reason with no landing claim behaves as today.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new cases show `--reason "landed on main"` with no sha refused; a sha that is not an ancestor refused; an ancestor sha accepted. The refusals failed before the change.
2. `git diff --check` exits 0.
