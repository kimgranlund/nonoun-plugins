---
id: T-0135
title: "Extend the clean-status lint in steps.py to catch a whole-tree..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0125
---

## Goal
`steps.py lint` and `split` also refuse, as a plan defect, a criterion that requires a clean whole work tree through `git diff` (for example `git diff --quiet` or `git diff --exit-code` with no `-- <pathspec>` and no two-commit range), not only through an empty `git status --porcelain`/`-s`, while scoped and commit-to-commit diffs still pass. A clean check hidden inside a script the span calls stays out of reach, since the detector only reads span text; the docs say so.

## Context
Follow-up from T-0125 (criteria-no-porcelain-clean/filer-L1.md):

Extend the clean-status lint in steps.py to catch a whole-tree clean check not written as a `git status --porcelain` emptiness test (for example `git diff --quiet && ...` over the whole tree, or a script that hides it). The detector only matches span text.

## Constraints
Existing porcelain rule, its selftest fixtures, and the recommended `git diff` plus untracked files replacement keep working. Docs that describe the rule (CLAUDE.md, planner.md, steps.py docstring, sdlc-lite-author.md) stay in sync; `scripts/check.sh` stays green.

## Plan review
- step 1 builder-L3 blocked: plan defect: criterion 5 writes a fixture handoff.md with no `## Goal`, so split exits 1 on the goal before linting; fix the fixture to `printf '## Goal\nh\n'` (see step-1.superseded-1/builder-L3.md). The step-1 build is left in the tree.
- step 2: an extra pre-build `steps.py split --only 2` run (not required by /chain 3) reported the whole-suite `check.sh` guard red before step 2 synced the docs; nothing was written, the step-2 handoff from the full split was built unchanged, and check.sh is green after the build.
