---
id: T-0574
title: "Silence the flat-layout warning and drop the stale board.md"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: [T-0567]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py check` in this repo prints no layout warning, and no stale `board.md` sits in `.sdlc/`.

## Intent
- Do:
  1. Add `layout: flat` to `.sdlc/config` (maintainer choice 2026-10-15: keep the flat layout).
  2. `git rm .sdlc/board.md` if `/board` and `ragboard.py` regenerate it on demand. Otherwise leave it and say why in the Outcome.
- Non-goals: topic-layout migration.
- Done when: the criteria pass.

## Context
Gaps G5 and G6 (2026-10-15). `board.md` is an empty table last changed 2026-10-06.

## Constraints
None.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check 2>&1 | grep -c 'flat layout'` prints 0.
2. `git diff --check` exits 0.
