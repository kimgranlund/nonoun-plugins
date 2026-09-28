---
id: T-0081
title: "Add a steps.py selftest case for a done L3 build → verify L2: a..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0061
---

## Goal
`python3 plugins/sdlc-lite/scripts/steps.py selftest` fails when the build-level to verifier-level mapping is wrong: a done L3 build must map to `verify L2`, so a mutant mapping L3 to verifier L3 turns the selftest red.

## Context
Follow-up from T-0061 (add-a-steps-py-next/filer-L1.md):

Add a `steps.py selftest` case for a done L3 build → `verify L2`: a mutant mapping L3 to verifier L3 left the selftest green (step 1 verifier observation).

## Constraints
No behavior change to `steps.py next`; only selftest coverage. `scripts/check.sh` stays green.

## Plan review
- step 1 verifier-L1 fail, replan:
  > plan defect: the mutant criterion says to copy `plugins/sdlc-lite/scripts/steps.py` alone to a temp dir, but steps.py does `import order` (line 76), so the copy dies with `ModuleNotFoundError` before the selftest runs. The criterion should say to copy the whole `plugins/sdlc-lite/scripts/` dir.
  > plan defect: the (guard) says `git diff --name-only` lists no other file, but the task handoff `.sdlc/0081-add-a-steps-py-selftest/handoff.md` was modified before the plan (mtime 18:19:46, before planner-L1.md at 18:20:36). The guard was red before any build. Scope it to paths outside `.sdlc/`, or compare it against the tree as it was when the step was split.
  > The build needs no change. The 2-line steps.py addition is correct: the selftest passes, check.sh has no new findings, and the added case catches the L3 to L3 mutant (exit 1 naming the case, while HEAD stays green on the same mutant).
