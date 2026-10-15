---
id: T-0586
title: "Under layout: topics, tidy, check and the router text disagree"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Under `layout: topics`, `tickets.py tidy`, `tickets.py check` and the generated router text agree on which top-level `.sdlc` entries are allowed and where tidy archives to.

## Context
Found by the T-0585 solo and verifier (2026-10-15).
- A loose root `notes.md` or `roadmap.md` is allowed by `tidy` (`TOP_ALLOWED`) but reported by `check` as a stray under topics.
- The router Procedures block (`tickets.py` around line 2233) says `tidy lists its move into archive/` for every layout; under topics it should say `work/archive/`.

## Intent
- Do: make tidy's allow list depend on the layout the same way `check` does, and render the router line from `layout_paths()`.
- Non-goals: flat-layout behavior.
- Done when: the criteria pass.

## Constraints
Flat output unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new topics case shows a loose root `notes.md` listed by `tidy` and the router naming `work/archive/`. The case failed before the change.
2. `git diff --check` exits 0.
