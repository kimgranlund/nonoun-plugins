---
id: T-0585
title: "tickets.py tidy archives into .sdlc/archive under layout: topics"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Under `layout: topics`, `tickets.py tidy` moves loose entries into `<root>/work/archive/`, the layout's work folder, matching the onboarding block (T-0576) and agent-ui's migrated tree.

## Repro
1. A `.sdlc` with `layout: topics` and `ticket_root: tickets`, plus a loose top-level file.
2. `tickets.py --root .sdlc tidy --apply`.

## Expected
The file lands in `.sdlc/work/archive/`.

## Actual
It lands in `.sdlc/archive/`, which `check` under topics then reports as a stray root entry. Found by the T-0576 solo (2026-10-15).

## Context
`layout_paths()` in `tickets.py` (around line 747) gives `work`. `tidy` is around line 865 and `top_level_strays` around 836.

## Constraints
Flat layout keeps `.sdlc/archive/`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new case shows a topics fixture: `tidy --apply` moves a loose file to `work/archive/`, and `check` reports no stray. The case failed before the fix.
2. `git diff --check` exits 0.
