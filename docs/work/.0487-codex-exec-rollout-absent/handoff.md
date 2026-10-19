---
id: T-0487
title: "loaded_context shows rollout absent on codex exec runs"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Run any role through `run.sh` with `SDLC_BACKEND=codex` (exec transport), then read the `loaded_context` field of its runs.jsonl row (`docs/reports/codex-live-evidence/chain-step-1-runs.jsonl`).

## Expected
`loaded_context` records which context the Codex agent loaded, or says clearly that exec runs cannot record it.

## Actual
Every run printed `run.sh: loaded context not recorded: rollout absent`; `loaded_context.status` is `rollout absent` in each row. The `profile:` first line of the report is the only trace of the loaded revision.

## Context
Found by T-0316. Guess: `codex exec` writes no rollout file at the path the recorder looks for, or writes it elsewhere.

## Constraints
The failing test lands before or with the fix, never after.

## Closed

2026-10-12: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full
