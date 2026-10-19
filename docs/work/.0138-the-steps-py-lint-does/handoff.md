---
id: T-0138
title: "The steps.py lint does not check compound criteria with a trailing..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0093
---

## Goal
The `steps.py` `||` lint (split and lint) also checks compound criteria (`for`/`while`/`until`/`if`/`{`) that end in a trailing redirect or pipe after their closing keyword, such as `while read x; do ...; done < f`, so an unlinted `||` fallback inside them is refused like any other; its selftest proves the new case fires and that allowed forms still pass.

## Context
Follow-up from T-0093 (check-the-steps-py-lint/filer-L1.md):

The steps.py lint does not check compound criteria with a trailing redirect, such as `while read x; do ...; done < f`, because they do not end in `done`. Such a criterion can hold an unlinted `||` fallback.

## Constraints
Existing lint behavior for other criteria must not change: allowed `||` forms (after `test $# -eq 0`, a nonzero `exit` right operand) still pass, and every existing selftest case keeps its result. Any doc that describes the lint's compound-criterion coverage (CLAUDE.md, sdlc-lite-author.md, planner or handoff-format docs) is updated in the same change. `scripts/check.sh` stays green.
