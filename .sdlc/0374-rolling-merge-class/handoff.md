---
id: T-0374
title: "Lanes get a computed merge class (rolling or integration) and a land command for rolling lanes"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0375]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane has a computed merge class, and a rolling lane that is independently verified can land on main at once.

## Intent
- Do: Compute a merge class per lane in the plugin: `rolling` (independently verified, touches no hash-bound or generated path, base is an ancestor of main) can fast-forward to main immediately; `integration` (touches hash-bound or generated files) waits for the next regeneration. Add a `fanout.py land`-style path for rolling lanes with the verifier verdict as the gate. The set of hash-bound paths must come from the repo (a declared list in .sdlc/config or the lane's handoff), not be guessed. Design first: write the rule and the config shape in docs/references/sdlc-internals.md before code; stop and ask if the hash-bound declaration needs a decision from the user.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - Selftests: a verified lane touching no declared path and based on an ancestor of main is classed rolling and lands; one touching a declared path is integration and does not; an unverified one never lands; a stale base is not rolling (observed failing first).
  - The class and the land gate are documented in one place.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Lanes accumulate faster than integrations land because the only merge path is the per-round integration solo (maison R2: 15 verified lanes waited on one combined integration). Source: feedback from the maison conductor, 2026-10-08 (about 30 lanes across Claude and Codex, 3 bases, 2 peer repos); its specifics are in the maison repo's .sdlc/notes.md and handoffs. Maison ran plugin 0.21.2; check each claim against 0.21.3 and main before building.

## Constraints
No em or en dashes. No push or publish.
