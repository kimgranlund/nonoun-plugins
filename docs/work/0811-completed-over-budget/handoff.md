---
id: T-0811
title: "Completed attempts that overran their time budget are never reported"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py status` and `fleet_collect.py` report completed attempts whose wall time exceeded their role's time budget, not only running ones.

## Repro
1. Complete an attempt whose wall time exceeds its `time_budget_min`.
2. Run `dispatch.py status` and `fleet_collect.py collect`.

## Expected
Each names the overrun once (role, wall, budget).

## Actual
T-0270 verifier ran 42.3 min against 25 and T-0275 step-2 builder ran 50.1 against 45; neither was reported after completion (`docs/reports/2026-10-29-sdlc-retro-macbook-pro/ultimate-tokens-color-science-attempts.jsonl`). `over_budget_lines` checks only running attempts.

## Context
- `docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 13.
- `plugins/sdlc-lite/scripts/dispatch.py` `over_budget`, `over_budget_lines`; `fleet_collect.py` completed-attempt branch.

## Constraints
- Red check: selftest cases with a completed over-budget attempt; nothing is reported before and one line after.
- outcome metric: completed over-budget attempts reported, before: 0 of 2.
