---
id: T-0280
title: "Estimated cost for sub-agent runs from tokens and a price table"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0278]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A sub-agent run records an estimated `cost_usd` (tokens times a per-model blended rate, marked estimated) so `budget.py` and the board stay live instead of counting every run unmetered.

## Intent
- Do: Estimated cost for sub-agent runs from tokens and a price table.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `adapters/claude/prices.json` holds a blended USD per million tokens per model, and `cost_estimate.py selftest` calibrates it against recorded `runs.jsonl` lines that hold both `usage` and a real `cost_usd`: the estimate is within 35 percent of actual in aggregate per model (the selftest fails when the table is off by more).
  - `record` writes `cost_usd`, `cost_estimated: true`, and `cost_basis` (`tokens x blended`, or `transcript usage x price` when probe P5 allows it); a run with no usage block writes null with `cost_reason`, never zero.
  - `budget.py status` counts estimated cost, prints an `estimated` share, and a ticket whose runs are all estimated still exits 3 at 80 percent (positive), while the same ticket with null costs exits 0 (the control that shows the gap this closes).
  - `board.py` shows an estimated total with a `~` prefix; `traces` cost detector reads `cost_estimated` without a crash.

## Context
Design section 3. Lost with sub-agents: `total_cost_usd`, the input/output/cache split, `num_turns`, and a per-model split. Existing `runs.jsonl` history holds usage and cost together, which is the calibration set.

## Constraints
No change to the budget tiers or the 80 percent rule. No em dashes. No push, tag, or publish.
