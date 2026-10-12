---
id: T-0482
title: "board.py --lanes shows light merges not yet covered by the full gate (T-0480)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0481]       # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`board.py --lanes` lists light merges on an integration branch that no ledger entry covers yet, so an uncovered merge is visible before settle.

## Intent
- Do: read `gate-ledger.jsonl` and the first-parent `Merge <branch>: <id>` commits since the newest entry's `to`; print them in the lanes view.
- Non-goals: the ledger format and `cover` (T-0481).
- Done when: a `board.py selftest` case: two light merges after a ledger entry shows both as uncovered, and a `cover` entry clears them; observed red first.

## Context
Design: `docs/planning/light-merge-lane.md` (Approach, last paragraph). Follow-up the architect named, not in the first build.

## Constraints
Read-only view; no change to gate behavior.
