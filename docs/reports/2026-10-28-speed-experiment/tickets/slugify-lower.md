---
id: T-0001
title: "slugify does not lowercase"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`slugify` lowercases its result, keeping its other rules.

## Actual
`slugify` returns mixed case: `slugify("Hello World")` gives `Hello-World`.

## Context
`textkit.py`; tests run with `python3 -m unittest discover -s tests -t .`.

## Acceptance criteria
1. `python3 -m unittest tests.test_slugify` exits 0.

## Constraints
Change only what the goal needs.
