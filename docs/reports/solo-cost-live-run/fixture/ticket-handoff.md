---
id: T-0001
title: "Add shout() to util.py"
type: feature
status: ready
size: S
priority: P2
depends: []
created: 2026-10-05
budget_usd: 5
---

## Goal
Add `shout(s)` to `util.py`: uppercase the text and end it with `!`. Add one test for it in `tests/test_util.py`.

## Intent
- Do: edit only `util.py` and `tests/test_util.py`.
- Done when: `python3 -m unittest discover -s tests` passes and `shout("hi")` returns `HI!`.
