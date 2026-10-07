---
id: T-0340
title: "dispatch.py prepare recovers or names a stale attempt left by a failed spawn instead of blocking the next prepare"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After a spawn the hook denied (the scout model mismatch), a stale scout-L1.attempt.json blocked the next prepare until run_lifecycle.py recover was run by hand. Make prepare detect an attempt whose dispatch never reached record and has no live owner, and either recover it itself (same rule as run_lifecycle recover) or print the exact recover command; add a selftest with a planted dead attempt.

## Intent
- Do: 
- Non-goals: model or effort changes; anything outside the named files.
- Done when:
  - The goal holds, shown by a selftest case that fails on the old behavior (observed) and passes now.
  - check.py, tickets.py check and the touched selftests pass.

## Context
Found by the 2026-10-07 fleet retro (ultimate-tokens conductor, .sdlc/fleet-retro-2026-10-07.md in that repo, rows marked [V]; read-only).

## Constraints
No em or en dashes. No push or publish.
