---
id: T-0560
title: "A plain tickets.py close leaves skips.md tracked in the closed folder"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After any `tickets.py close`, the closed folder tracks only `handoff.md`, as lean records intends.

## Repro
1. Run a ticket whose lane writes `skips.md` in the task folder, then `tickets.py close <slug>` outside fanout.
2. `git ls-files .sdlc/.<slug>/`.

## Expected
Only `handoff.md`.

## Actual
`skips.md` is tracked too (T-0545 builder report, 2026-10-14; seen on this repo's wave 71 to 74 closes).

## Context
T-0540 kept `skips.md` in the task folder by maintainer decision; C or D were to move it, which did not happen. Guess: move `skips.md` to the records dir, or untrack it at close.

## Constraints
The failing test lands before or with the fix. Target 0.23.1.
