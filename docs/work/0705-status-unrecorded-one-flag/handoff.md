---
id: T-0705
title: "dispatch.py status prints one unrecorded-report flag"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py status` names an unrecorded report with one token, not two.

## Intent
- Do: merge `report-written-unrecorded` (T-0383) and `report-unrecorded` (T-0703) in `plugins/sdlc-lite/scripts/dispatch.py` into one token that fires for every state the two cover today; update every reader and doc that names either token.
- Non-goals: changing which states are flagged.
- Done when: the criteria pass.

## Context
T-0703 verifier: "Running or orphaned with a newer report prints both tokens. Running or orphaned with an older report ... prints only the old one. Only the new token covers interrupted and limit-stopped."

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, and its cases show a running attempt with a newer report prints exactly one flag token.
2. `git grep -n "report-written-unrecorded\|report-unrecorded" plugins docs/references` shows only the kept token.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.
