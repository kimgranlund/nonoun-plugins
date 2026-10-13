---
id: T-0521
title: "Recalibrate prices.json for the model rows changed in T-0516, T-0517, T-0519 and T-0520"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0520]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`prices.json` matches every model and effort row now in `adapters/claude/levels.json` and `adapters/codex/models.json`, so cost reports are right.

## Intent
- Do: find `prices.json` under `plugins/sdlc-lite`, list rows used by the two tables that have no price or a stale one, and fix them from the provider's published prices. Cite the source and date in the file's own note field or the nearest reference.
- Non-goals: changing any model or effort row.
- Done when: every (model) named in both tables resolves to a price; the script that reads prices (`report.py` or `solo_stats.py` cost path) selftest passes; a negative control shows a missing price is reported.

## Context
T-0516, T-0517, T-0519 changed rows and left prices alone (their handoffs made it a non-goal). T-0520 adds ui-designer rows.

## Constraints
None beyond the repository guidance.

## Closed

2026-10-13: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full
