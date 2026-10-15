---
id: T-0573
title: "notes.md keeps only live notes"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`.sdlc/notes.md` holds only notes that still matter: open decisions, live caveats and standing maintainer rulings. Resolved items are gone, and still-open work becomes tickets.

## Intent
- Do:
  1. For each of the 82 `## ` sections, decide: delete it if resolved or stale (the fix landed, or the path no longer exists); keep it if it is a standing ruling or a live caveat; or file it as a proposed ticket with `tickets.py new` if it is open work, then delete the note.
  2. Keep maintainer rulings (lines starting with a date and `maintainer:`) unless a later ruling replaces them.
- Non-goals: rewriting kept notes.
- Done when: the criteria pass.

## Context
Gap G4 (2026-10-15): `notes.md` is 567 lines and 79 KB, starting 2026-09-26. Many entries cite fixed bugs or old `.worktrees/fanout*` paths. `tickets.py close` appends verifier notes here, so the file only grows.

## Constraints
Do not delete a note that an open ticket cites. Check with `grep -rn 'notes.md' .sdlc/0*/handoff.md`.

## Acceptance criteria
1. `wc -l < .sdlc/notes.md` is under 150.
2. The Outcome lists each new ticket id filed from a note, or says `none`.
3. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 and `git diff --check` exits 0.
