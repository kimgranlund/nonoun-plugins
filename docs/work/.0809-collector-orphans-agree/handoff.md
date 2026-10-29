---
id: T-0809
title: "fleet_collect counts orphaned attempts differently from dispatch.py status"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
branch: lane/T-0809-t0809
worktree: ../sdlc-lite.worktrees/T-0809-t0809
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

## Outcome

2026-10-29 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: c229bc6b59ff
- Changed: see commits
- Commits: 1861ee5 T-0809: fleet_collect counts orphaned attempts as dispatch.py status does; 11be945 T-0809: record lane T-0809-t0809
- Check: 1 Red check: a `fleet_collect.py selftest` case with a live-pid running attempt on a closed ticket ...: pass
- Check: 2 Goal: fleet_collect counts orphaned exactly when dispatch.py status does: pass
