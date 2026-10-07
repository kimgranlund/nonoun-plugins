---
id: T-0300
title: "Board row for a merged solo lane reads done"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A ticket merged from a solo lane shows done on the board once merged and closed, not "built, awaiting verify".

## Context
Maison T-0039, T-0043, T-0036: the board row for a merged solo lane read "built, awaiting verify", because it read the step folder, which a solo lane never has. File: plugins/sdlc-lite/scripts/board.py (it already renders a `done` ticket with no plan as a `closed` task row; find why a solo-merged ticket still reads built). Reproduce first in a temp .sdlc: a ticket with a `skips.md` lane `solo` record and a `role solo` runs.jsonl line, before and after the ticket is `done`.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0 with a new case reproducing the stale row (red before the fix, shown once) and asserting the row reads done or closed after.
- [ ] A solo ticket that is built but not closed still reads as before (control case in the selftest).
- [ ] docs/references/sdlc-internals.md Feed entry states the rule in one sentence.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
