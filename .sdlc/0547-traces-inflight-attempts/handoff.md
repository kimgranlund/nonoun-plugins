---
id: T-0547
title: "traces selftest corpus case counts in-flight runtime attempts, so check.sh is red inside a role run"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`bash plugins/sdlc-lite/scripts/check.sh` passes when run inside a role run on a ticket, with that role's own in-flight attempt records present under `.sdlc/runtime/tasks/`.

## Repro
1. Start any role on a ticket (its `<role>.attempt.json` exists in `.sdlc/runtime/tasks/<task>/`, no `runs.jsonl` row yet).
2. From the same tree run `python3 plugins/sdlc-lite/scripts/traces/selftest.py`.

## Expected
The corpus case passes; an attempt that is still running (a live `.running` marker, or no recorded result yet) is not an "attempt in no row".

## Actual
The case `corpus: this repo's .sdlc traces ingest whole` fails, listing the in-flight `.attempt.json` files as "attempts in no row", so `check.sh` is red from inside a role run (T-0542 step 2 blocked on it; T-0540 notes).

## Context
`plugins/sdlc-lite/scripts/traces/selftest.py` lines 2024-2054 (the corpus case). Became visible once T-0540 moved run records to `.sdlc/runtime/tasks/`. Guess: the case should skip attempts whose run is still open, or the corpus should be read from tracked records only. Notes: `.sdlc/notes.md` line 469.

## Constraints
The failing test lands before or with the fix, never after. Do not weaken the check for finished attempts that truly have no row.
