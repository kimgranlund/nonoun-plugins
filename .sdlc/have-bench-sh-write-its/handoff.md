---
id: T-0036
title: "Have bench.sh write its exit code and wall-clock duration to the..."
type: idea            # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0032
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0032 (confirm-with-one-real-scripts/filer-L1.md):

Have bench.sh write its exit code and wall-clock duration to the bench log: the T-0032 verifier could not check `exit=0` or the run time because both go only to stdout.

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: keep, P3; exit code and duration per bench task.
