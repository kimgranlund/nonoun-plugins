---
id: T-0315
title: "Re-measure planner and replan cost after T-0297 and the L4/L5 plan-review rule"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
The exact question this spike answers.

## Goal
Recompute what planning and replanning cost now, after T-0297 and the L4 and L5 plan-review rule, to decide whether delta replans (dropped T-0200) are worth building.

## Intent
- Do: Using runs.jsonl from agent-ui, maison and this repo (read-only, deduped by attempt_id), report planner and plan-reviewer cost, runs per ticket, replan counts, and wall minutes before and after 2026-10-06 (T-0297 and the plan-review rule shipped in 0.20.11). Write docs/reports/replan-cost-remeasure.md with a recommendation: build delta replans (reopen T-0200 as a new ticket with the numbers) or leave dropped.
- Non-goals: Building anything; changing the replan cap.
- Done when:
  - The report has per-repo and combined cost tables with the dedupe method stated and a count that matches each repo's own report within 2 percent for the earlier period (agent-ui: 193 runs, $787).
  - It states a clear recommendation with the number that decides it.
  - `git diff --check` and the link check pass.

## Context
Agent-ui measured planners at 37 runs, $250, about 20 minutes each, and no-barrels at 12 planner results; later fixes may have changed this. Do not use the fleet collector if T-0305 is not built yet; a short script in the report appendix is fine. Dropped T-0200 and T-0213 are the reference for what a delta replan would do.

## Constraints
No change to any model or effort value. No em dashes. No push, tag or publish. Independent verifier per ticket; checks need a positive case and an observed negative control.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
