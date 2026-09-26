---
id: T-0114
title: "Verifier fail on a gate that is already red at the pre-build HEAD..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0101
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0101 (builder-inherited-red/filer-L1.md):

Verifier fail on a gate that is already red at the pre-build HEAD still routes as an ordinary fail; T-0101 left the verifier unchanged, so decide whether it should route to `inherited` too.

## Constraints
What must not change. "None" if none.
