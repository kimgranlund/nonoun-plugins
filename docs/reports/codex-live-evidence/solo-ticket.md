---
id: T-0001
title: "Add shout()"
type: feature
status: ready
size: L1
priority: P2
depends: []
created: 2026-10-12
---

## Goal
Add `shout(text)` to a new `kit/shout.py`: it returns `text.upper() + "!"`.

## Intent
- Do: create `kit/shout.py` and a test `tests/test_shout.py` with `shout("hi") == "HI!"` and `shout("") == "!"`.
- Non-goals: touching `kit/greet.py`.
- Done when: `python3 -m unittest discover -s tests` exits 0 with at least 3 tests run.

## Context
Tiny throwaway project for a live Codex solo run. Stdlib only.

## Constraints
No dependencies. Change nothing outside `kit/shout.py`, `tests/test_shout.py` and this ticket folder.
