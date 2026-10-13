---
id: T-0524
title: "Find and fix the 1 error /reload-plugins reported after 0.22.6"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/reload-plugins` loads SDLC Lite and Progressive Context with zero errors.

## Intent
- Do: reproduce the 1 error the maintainer saw from `/reload-plugins` after installing 0.22.6 (`claude plugin validate` on both plugins and the marketplace, `claude --debug` load output), name the file and cause, and fix it.
- Non-goals: unrelated packaging cleanup.
- Done when: the cause is named with the exact error text; `scripts/check-packaging.py` passes and gains a case that would have caught it, with a negative control; if the error is not ours (another installed plugin), close with that evidence instead.

## Context
Seen in the maintainer session on 2026-10-12; never examined. Other user-scope plugins are installed (harness, figma), so the error may not be ours.

## Constraints
None beyond the repository guidance.
