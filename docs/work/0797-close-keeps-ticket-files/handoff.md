---
id: T-0797
title: "tickets.py close deletes skips.md and other ticket-folder files (#83)"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py close` keeps every file in the ticket folder when it renames it to `.NNNN-<slug>` (GitHub #83).

## Repro
1. A ticket folder holds `handoff.md` and `skips.md`.
2. `tickets.py --root .sdlc close T-NNNN ...`.

## Expected
The closed folder `.NNNN-<slug>/` holds both files.

## Actual
Here: `git show --stat 5bc34f77` (close T-0790) and `git show --stat 23368535` (close T-0791) each delete a `skips.md`. ultimate-tokens-color-science restored it by hand in 6 commits (`git log --grep '#83'`, MacBook report row U1). Issue #83 is OPEN.

## Context
`plugins/sdlc-lite/scripts/tickets.py` close. Fleet retro 2026-10-28 row 13 (scored below 7 for an unmeasured cost; filed on the user's request).
outcome metric: `git log --grep '#83'` restore commits in ultimate-tokens-color-science after the release, before: 6.

## Acceptance criteria
1. A `tickets.py` selftest case: closing a ticket whose folder holds `skips.md` keeps it in the closed folder; with the fix reverted it fails (state the FAIL line).
2. tickets selftest through gate_lock exits 0, `check.py` exits 0.

## Constraints
The failing test lands before or with the fix, never after.
