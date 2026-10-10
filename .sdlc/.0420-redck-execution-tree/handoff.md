---
id: T-0420
title: "redck record and verify resolve the shared handoff's checkout, not the lane worktree"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`redck.py` binds pre-edit red controls to the builder's execution tree (the lane worktree), not the checkout that holds a shared handoff, so a clean lane is labeled pre-edit.

## Intent
- Do: in scripts/redck.py (`record` near line 164 and the verify path near line 231) replace `steps.git_toplevel(d)` with the execution tree that `steps.exec_toplevel(d)` already returns for a task dir in the main checkout read from inside an owned lane worktree (T-0381). Keep the recorded `base_sha` from `steps.base_sha(top, d)`. Record the tree path in the control entry so a verifier can see which tree was judged.
- Non-goals: changing the red-first rules; model or effort changes.
- Done when:
  - A redck selftest case, observed failing first: handoff in a primary checkout whose HEAD differs from the lane worktree, cwd in the lane; `redck record` labels the controls pre-edit (clean lane) and the entry names the lane tree; run from the primary alone it behaves as before.
  - redck.py selftest, steps.py selftest, check.py and tickets.py check pass.

## Context
Maison and Codex, 2026-10-09 (0.22.2): maison .sdlc/tickets/0356-redck-shared-handoff-execution-tree caused "retrospective" labels on T-0348 steps 2/3 and T-0355; verifiers had to judge red controls by hand. Related: T-0381, T-0395.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-10: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
