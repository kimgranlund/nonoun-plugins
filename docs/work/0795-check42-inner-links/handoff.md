---
id: T-0795
title: "check.py item 42 rejects ../ links that stay inside the skill folder"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`check.py` item 42 accepts a relative link in a context skill that starts with `../` but resolves inside the same skill folder, and still rejects one that leaves it.

## Repro
1. In `plugins/context/skills/context-fog-of-war/references/learnings/<file>.md`, add `[x](../viewer.md)` (it resolves to `references/viewer.md`, inside the skill).
2. `python3 plugins/sdlc-lite/scripts/check.py`.

## Expected
Exit 0: the link stays inside `context-fog-of-war/`.

## Actual
T-0790 verifier, 2026-10-25, with `../SKILL.md` from `references/viewer.md`: `FAIL context/skills/context-fog-of-war/references/viewer.md: link leaves the skill folder: ../SKILL.md`, exit 1. T-0790 turned 17 such inner links into code spans to pass.

## Context
Item 42 in `plugins/sdlc-lite/scripts/check.py` (guess: it tests the `../` prefix instead of resolving the path against the skill root). Found by `solo-0790` and confirmed by `0790-verifier-L3` (T-0790 Outcome).

## Acceptance criteria
1. A check.py case: an inner `../` link passes and a link leaving the skill still fails; with the fix reverted the first case fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `python3 scripts/check-packaging.py` exits 0.

## Constraints
The failing test lands before or with the fix, never after. Restoring the 17 T-0790 code spans to links is out of scope.
