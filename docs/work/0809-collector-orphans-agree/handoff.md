---
id: T-0809
title: "fleet_collect counts orphaned attempts differently from dispatch.py status"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fleet_collect.py` counts an attempt as orphaned exactly when `dispatch.py status` does, including a running attempt whose ticket is done or dropped (T-0796).

## Repro
1. Leave a verifier attempt `running` with its parent pid alive, then close its ticket.
2. Run `dispatch.py status` and `fleet_collect.py collect`.

## Expected
Both report the attempt as orphaned.

## Actual
Status shows T-0266 verifier-L2 orphaned; the fingerprint has `runs.orphaned.count` 0 (`docs/reports/2026-10-29-sdlc-retro-macbook-pro/ultimate-tokens-color-science.json`, `docs/reports/2026-10-29-sdlc-retro-macbook-pro/ultimate-tokens-color-science-status.txt`). `fleet_collect.py` counts an orphan only when `not pid_alive(pid)`.

## Context
- `docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 6.
- `plugins/sdlc-lite/scripts/fleet_collect.py` running-attempt branch; `dispatch.attempt_state_at`.

## Constraints
- Red check: a `fleet_collect.py selftest` case with a live-pid running attempt on a closed ticket; it counts 0 before and 1 after.
- outcome metric: collector orphan count vs status orphan count, before: 0 vs 1.
