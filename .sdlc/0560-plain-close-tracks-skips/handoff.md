---
id: T-0560
title: "A plain tickets.py close leaves skips.md tracked in the closed folder"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
branch: lane/T-0560-w76-0560
worktree: .claude/worktrees/T-0560-w76-0560
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

## Acceptance criteria
1. A plain or `--reason` close of a ticket whose committed task-folder `skips.md` has a runtime records dir moves it there; after `git add -A` the closed folder tracks only `handoff.md`, and the Outcome still reads the lane: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0, including its `(T-0560 plain)` and `(T-0560 reason)` cases (red before the fix).
2. A legacy in-place ticket keeps its `skips.md`: the `(T-0560) a legacy in-place fixture keeps its skips.md in the folder` case passes in the same selftest.
3. fanout land still closes and untracks as before: `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
