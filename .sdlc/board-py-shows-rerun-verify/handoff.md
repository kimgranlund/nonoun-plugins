---
id: T-0088
title: "board.py shows 'rerun verify' for a second no-verdict result in a..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0073
---

## Goal
The /board step row for a step whose newest two or more verifier results after the build have no pass/fail verdict says the step is stopped and the user must be asked (matching `steps.py next`, which returns `stop`), instead of "rerun verify". A single no-verdict result still says "rerun verify". Done when board.py's selftest covers both cases and `scripts/check.sh` passes.

## Context
Follow-up from T-0073 (verifier-no-verdict/filer-L1.md):

board.py shows "rerun verify" for a second no-verdict result in a row, but `steps.py next` returns `stop` for that case; make the board row say stop/ask the user so the two stay in sync.

## Constraints
- Code lives in plugins/sdlc-lite/scripts/board.py (`step_row`); `steps.py next` is the spec (consecutive no-verdict verifiers counted with `order.counts_after` against the newest build, stopping at the first verifier with a verdict). Do not change steps.py behavior.
- Keep the existing single no-verdict rendering (🟡 no verdict ... rerun verify) unchanged.
- Update any doc that describes the board's no-verdict rendering (board.py docstring, CLAUDE.md Layout feed line, skills/board if it mentions it) in the same change.
