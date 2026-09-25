---
id: T-0032
title: "Confirm with one real scripts/bench.sh --bench-dir DIR run that the..."
type: idea            # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0025
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0025 (bench-project-dirs/filer-L1.md):

Confirm with one real `scripts/bench.sh --bench-dir DIR` run that the headless /bench session receives SDLC_BENCH_DIR, since without it the skill ignores an explicit --bench-dir.

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: keep, P2; prove the --bench-dir wiring end to end (bench.sh to the headless /bench session) with one real run, and fix it if it breaks.
