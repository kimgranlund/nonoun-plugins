---
id: T-0358
title: "A solo lane stops early when the ticket is already fixed or stale"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo lane checks first whether the ticket is already fixed or stale and stops with a one-line report instead of building.

## Intent
- Do: Add a short first step to the solo role brief and solo skill: confirm the Goal still reproduces or is still unmet, and if not, report 'already fixed' with the evidence and change nothing. Measure on gen-ui-kit's lane list (6 of 17 solo lanes on 2026-10-07 found the ticket already fixed or stale and changed nothing).
- Non-goals: Model or effort changes; skipping the independent verifier on tickets that did change code.
- Done when:
  - Brief and skill updated, generated agents current.
  - A focused throwaway run on an already-fixed ticket stops early and reports it; a still-open ticket proceeds (positive and negative control).
  - check.py and relevant selftests pass.

## Context
Fleet cost analysis of 2026-10-07 (all-time deduped run records, five repos): verifier L3 Fable $1,291 over 198 runs (about $6.5 each) versus verifier L2 Sonnet about $0.50 each; solo L2 Sonnet xhigh about $406 ($3.31 to $5.53 per run). The user approved these four proposals on 2026-10-07.

## Constraints
No em or en dashes. No push or publish.
