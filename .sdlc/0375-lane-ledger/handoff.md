---
id: T-0375
title: "board.py --lanes shows base sha, stale-base flag, verifier verdict, merge class and owner"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`board.py --lanes` shows each lane's base sha, stale-base flag, verifier verdict, merge class and owner.

## Intent
- Do: Extend board.py --lanes with columns: base sha, stale-base (base is not an ancestor of main), verifier verdict (from the lane's verifier result), merge class (from T-0374 once it exists, else `n/a`) and owner (claude or codex, from the run record backend). Read-only. Maison is prototyping a repo-local scripts/lane-ledger.mjs (their T-0286); lift its columns and format rather than inventing new ones if it is available when this starts.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A selftest with fixture lanes (one stale, one verified, one codex-owned) prints each column correctly (observed failing first).
  - `board.py --lanes` output without lanes is unchanged.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
`board.py --lanes` exists but shows none of the fields a conductor needs to decide what to merge. Source: feedback from the maison conductor, 2026-10-08 (about 30 lanes across Claude and Codex, 3 bases, 2 peer repos); its specifics are in the maison repo's .sdlc/notes.md and handoffs. Maison ran plugin 0.21.2; check each claim against 0.21.3 and main before building.

## Constraints
No em or en dashes. No push or publish.
