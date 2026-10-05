---
id: T-0001
title: "Add median to mathkit"
type: feature
status: ready
size: M
priority: P2
depends: []
created: 2026-10-05
---

## Goal
`mathkit.median(values)` returns the median of a sequence of numbers.

## Intent
- Do: add `median(values)` to `mathkit/stats.py` and export it from `mathkit/__init__.py`. Odd count returns the middle value after sorting. Even count returns the mean of the two middle values (a float). An empty sequence raises ValueError. It must not mutate its input and must accept any iterable. Add tests to `tests/test_stats.py` and one line to the README.
- Non-goals: other statistics; packaging.
- Done when: the behavior holds and `python3 -m unittest discover -s tests` passes.

## Context
Files: mathkit/__init__.py, mathkit/stats.py, tests/test_stats.py, README.md.

## Constraints
Standard library only.
