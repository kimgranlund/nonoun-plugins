---
id: T-0122
title: "fanout.py inherited_red reads the tests from the newest builder's..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0114
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0114 (verifier-fail-on-a-gate/filer-L1.md):

fanout.py `inherited_red()` reads the tests from the newest builder's `## Status`, so a verifier-inherited step reports `inherited red: step-<n>: done` and names the wrong tests; read them from the verifier Verdict when that is newer.

## Constraints
What must not change. "None" if none.
