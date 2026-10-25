---
id: T-0787
title: "steps.py lane writes skips.md in the tree that owns the ticket"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lane` run from the main checkout on a lane's ticket appends to the `skips.md` of the tree that owns the ticket, so main stays clean and the next land does not refuse (GitHub #80, the part 0.36.0 left open).

## Repro
1. Open a lane for a ticket (`lanes.py open`), then from the main checkout run `python3 plugins/sdlc-lite/scripts/steps.py lane <main's copy of the ticket folder>`.
2. `git status --short` in main.

## Expected
Main shows no change: the `- lane:` line is in the lane tree's `skips.md`, the owner tree by `wtroot.owner_tree` (the Owner trees table in `docs/references/sdlc-internals.md`).

## Actual
Release report `docs/reports/2026-10-25-release-0-36-0.md`: "`steps.py lane` run in the main checkout still leaves `skips.md` there (one helper for its location is future work)."

## Context
Writers of `skips.md`: `steps.py` lane (about line 288 doc, 336 append), `dispatch.py` lines 705, 1437, 1442. Guess: add one helper, for example `order.skips_path(task_dir)`, that resolves the owner tree, and route those writers through it; readers that already check the owner tree stay as they are.

## Acceptance criteria
1. A `steps.py` selftest case: with a lane open for the ticket, `steps.py lane <main ticket folder>` leaves main's `skips.md` absent or unchanged and appends the line in the lane's; with the fix reverted it fails (state the FAIL line).
2. The `dispatch.py` writers use the same helper; `grep -n "'skips.md'" plugins/sdlc-lite/scripts/dispatch.py plugins/sdlc-lite/scripts/steps.py` shows no path built outside the helper except selftest fixtures.
3. The steps and dispatch selftests through gate_lock exit 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Constraints
The failing test lands before or with the fix, never after.
