---
id: T-0781
title: "steps.py next lets a later verifier verdict win over an inherited-red build"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py next` routes a step by its newest verifier verdict when one comes after a builder's `inherited red`, the same order `board.py step_row` uses since T-0771, so a step whose verifier passed after an inherited-red build reads done.

## Intent
- Do: in `plugins/sdlc-lite/scripts/steps.py` next (about line 3337; GitHub #79 part (a) names line 3233), check the builder's inherited red only when no verifier verdict is newer, keeping T-0766's `lane red` route for the case where it is the newest result.
- Non-goals: board.py (T-0771 fixed it).
- Done when: the criteria pass.

## Context
T-0771 builder (2026-10-25): board.py is fixed; `steps.py next` has the same ordering bug and was left because T-0766 was editing that route. GitHub #79.

## Acceptance criteria
1. A `steps.py` selftest case: an inherited-red builder result followed by a verifier pass reads done; with no verifier verdict it still routes inherited (or lane red per T-0766); with the change reverted the first case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
