---
id: T-0048
title: "Guard close --skip against index drift: if the filer file changes..."
type: idea            # feature | bug | chore | spike | idea
status: ready
size: M              # S | M | L | XL
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0041
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0041 (confirm-follow-ups/filer-L1.md):

Guard `close --skip` against index drift: if the filer file changes between `--dry-run` and `--skip`, the indices shift and the wrong follow-ups get skipped (no lock or content check today).

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: keep, P3; guard --skip against filer-file drift between dry run and close.
