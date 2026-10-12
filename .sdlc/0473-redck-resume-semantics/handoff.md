---
id: T-0473
title: "redck: phase against the working tree, bind to an ancestor base (T-0470 finding 6)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A second builder on a branch that already holds the first builder's commits gets `pre-edit` or `preserved`, not `retrospective` or `missing`, while a different lineage is still refused.

## Repro
1. In `redck.py selftest`, keep the base at the first dispatch, commit the attempt A1 work, then `redck record --attempt-id A3`.
2. Separately, move the base to HEAD with no A3 control and run `redck audit --attempt-id A3`.

## Expected
(a) phase `pre-edit`; (b) `preserved`.

## Actual
(a) `retrospective`; (b) `missing` (`redck.py:390-394`).

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 6. Three rules: `record` reads the phase against the working tree (`git status --porcelain` on the source paths) and stores the commit; `audit` binds a control whose `base_sha` is the current base or an ancestor of HEAD; an own pre-edit control that is green defers to an earlier same-lineage pre-edit red before it reads `green-baseline`. Code: `redck.py:176`, `:213-214`, `:222-226`. The existing `missing` control at `redck.py:394` flips to a lineage check.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.
