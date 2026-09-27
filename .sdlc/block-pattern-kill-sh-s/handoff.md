---
id: T-0145
title: "block-pattern-kill.sh's new substitution matcher reads a..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0121
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0121 (pattern-kill-hook-does-not/filer-L1.md):

`block-pattern-kill.sh`'s new substitution matcher reads a substitution body only up to its first `)` or backtick, so a kill word placed after a nested inner substitution's closing paren (e.g. `k=$(basename $(x) kill)`) still passes undetected inside a role run; worth a dedicated ticket if that pattern is judged realistic.

## Constraints
What must not change. "None" if none.
