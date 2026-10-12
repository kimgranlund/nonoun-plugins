---
id: T-0486
title: "red-checkpoint marked retrospective though controls were recorded first"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Rerun the T-0316 builder step (`docs/reports/codex-live-evidence.md`) in a throwaway repo; read `docs/reports/codex-live-evidence/process-deviations.md`.

## Expected
Controls the builder records with `redck.py record` before its first edit are classed as a red-first checkpoint, not retrospective.

## Actual
`redck: process deviation: red-checkpoint: retrospective`: both `(red)` controls were recorded at 15:00:32 as phase `retrospective` with exit 1, though the builder says it recorded before editing.

## Context
Found by T-0316. Cause not traced; guess: the checkpoint compares record time to the first edit or to the launcher's own timestamp and the builder's order differs from what redck assumes.

## Constraints
The failing test lands before or with the fix, never after.
