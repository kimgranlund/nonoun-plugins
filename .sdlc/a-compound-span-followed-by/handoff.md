---
id: T-0147
title: "a compound span followed by &&, ;, or || after its closing keyword..."
type: idea            # feature | bug | chore | spike | idea
status: dropped       # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-27
from: T-0138
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0138 (the-steps-py-lint-does/filer-L1.md):

a compound span followed by `&&`, `;`, or `||` after its closing keyword (for example `done || echo x`) stays unlinted by design in this change; the planner's Risks section flags this as a likely follow-up scope if such forms show up in practice.

## Constraints
What must not change. "None" if none.

## Decision
Dropped 2026-09-27: speculative hardening with no observed failure; reopen if the form shows up in a real run.
