---
id: T-0810
title: "dispatch.py advance prepares a verifier for an already-fixed solo"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
branch: lane/T-0810-t0810
worktree: ../sdlc-lite.worktrees/T-0810-t0810
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py advance` on a solo whose report says `already fixed: <evidence>` prints the close line and prepares no verifier.

## Repro
1. Record an L2 solo whose report is `already fixed: <evidence>`.
2. Run `dispatch.py advance` on its dispatch file.

## Expected
No verifier is prepared; the conductor closes the ticket with a reason.

## Actual
`advance_solo` prepares the ticket verifier for any non-blocked L2 solo, so T-0266's verifier was prepared, never ran, and was left `running` (`docs/reports/2026-10-29-sdlc-retro-macbook-pro/ultimate-tokens-color-science-status.txt`).

## Context
- `docs/reports/2026-10-29-sdlc-retro-macbook-pro.md` Finding 7.
- `plugins/sdlc-lite/scripts/dispatch.py` `advance_solo`; the solo contract in `plugins/sdlc-lite/agents/solo.md` step 1 (`already fixed:` with no `verify: needed`).

## Constraints
- Red check: a `dispatch.py selftest` case advancing an `already fixed` L2 solo; it prepares a verifier before and prints the close line after.
- outcome metric: verifier attempts prepared for already-fixed solos, before: 1.

## Outcome

2026-10-29 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: c98cfdc53dfc
- Changed: see commits
- Commits: 5cce280 T-0810: advance prints the close line with a reason for an already-fixed solo; 60e0514 T-0810: record lane T-0810-t0810
- Check: 1 Goal and red check: `dispatch.py advance` on an `already fixed` L2 solo prints the close line and...: pass
