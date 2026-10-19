---
id: T-0357
title: "Test solo L2 Sonnet at high versus xhigh on past tickets"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A recorded comparison of solo L2 (sonnet) at high versus xhigh on past tickets decides whether the effort drops.

## Intent
- Do: Pick 6 to 8 past L2 solo tickets with known outcomes, run solo L2 at high and xhigh in throwaway trees, compare pass, cost and duration; budget about $30 to $60. Report in docs/reports/. Change levels.json only if high passes everything xhigh passes at lower cost, with an eval lock.
- Non-goals: Changing builder, planner or verifier rows.
- Done when:
  - A dated report with per-ticket results at both efforts.
  - If effort changes: eval locked, generated agents current, check.sh passes.

## Context
Fleet cost analysis of 2026-10-07 (all-time deduped run records, five repos): verifier L3 Fable $1,291 over 198 runs (about $6.5 each) versus verifier L2 Sonnet about $0.50 each; solo L2 Sonnet xhigh about $406 ($3.31 to $5.53 per run). The user approved these four proposals on 2026-10-07. Sonnet 5.5 docs say effort levels were recalibrated and suggest starting at medium for agentic coding.

## Constraints
Report before changing levels.json. No em or en dashes.

## Closed

2026-10-08: Two sweeps recorded (docs/reports/2026-10-07-solo-l2-effort-sweep.md and -2.md); user approved high; shipped as T-0360, eval 0004
