---
id: T-0006
title: "add title_case"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`textkit.title_case(s)` capitalizes the first letter of each whitespace-separated word and lowercases the rest: `title_case("hELLO wORLD")` gives `Hello World`.

## Actual
There is no `title_case` helper.

## Context
`textkit.py`; tests run with `python3 -m unittest discover -s tests -t .`.

## Acceptance criteria
1. `grep -q "def title_case" textkit.py` exits 0.

## Constraints
Change only what the goal needs.
