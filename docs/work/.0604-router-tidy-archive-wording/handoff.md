---
id: T-0604
title: "Router Procedures block names archive/ for tidy under every layout"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The router Procedures block says where `tickets.py tidy` moves a loose top-level entry for the layout the repo uses (`archive/` for flat, `work/archive/` for topics).

## Context
`plugins/sdlc-lite/scripts/tickets.py` (about line 2302) renders "`<CMD> tidy` lists its move into `archive/`" for every layout, while `tidy` under `layout: topics` archives into `work/archive/` (T-0585; see the docstring near line 877 and the topics selftest case near line 6060). Found by the T-0585 verifier (2026-10-15); still true on main at T-0573. Source note: `.sdlc/notes.md` T-0585.

## Constraints
Regenerate the router (`.sdlc/AGENTS.md`) and keep `onboard.py` text consistent. Run `python3 plugins/sdlc-lite/scripts/tickets.py selftest`.

## Acceptance criteria
1. A topics-layout router renders `work/archive/` in the tidy line and a flat router renders `archive/`; the tickets selftest covers both.
2. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.

## Outcome

2026-10-15 · lane: full L2 · verdict: closed by reason (duplicate of T-0586, which covers the router tidy text under topics) · verifier: none · base: none
- Changed: see commits
- Commits: none
