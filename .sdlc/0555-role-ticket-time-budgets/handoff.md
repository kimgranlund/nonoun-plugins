---
id: T-0555
title: "Wall-clock budgets per role and per ticket, enforced by dispatch.py"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No role or ticket runs far past its expected time unnoticed: a role over its wall-clock budget, and a ticket over its total budget, stop and ask the person.

## Intent
- Do: per-level wall-clock budgets for each role (defaults from the median of recorded `duration_ms` in run records, times 3, with a floor), and a per-ticket budget by `size:` level. `dispatch.py prepare` prints the role's budget in the brief; `dispatch.py status` and `recover` flag an attempt past its budget; a ticket past its total budget makes `prepare` refuse the next role until `--approved "<who: why>"`.
- Do: the conductor contract and the maintainer agent: on a budget flag, check the role (stdin wait, stall) and ask the person; headless lanes stop as `blocked`.
- Non-goals: killing a role automatically; token or dollar budgets (budget.py keeps those).
- Done when: selftests show a role past budget flagged and one within budget not, and a ticket past budget refused then allowed with `--approved` (negative controls observed red); `check.sh` passes.

## Context
2026-10-14: a builder hung 39 min on stdin (T-0548) unnoticed; maison T-0541 ran 7.7 agent-hours over 97 runs. "Stop and report when a ticket passes its budget" exists only as prose in the maintainer agent file.

## Constraints
Ships in 0.23.0 (maintainer, 2026-10-14). The failing selftest lands before or with the change.
