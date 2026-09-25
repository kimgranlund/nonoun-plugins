---
id: T-0065
title: "fanout.py's default lane driver does not set SDLC_ROLE, so..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0058
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0058 (fanout-command/filer-L1.md):

fanout.py's default lane driver does not set `SDLC_ROLE`, so `hooks/block-publish.sh` does not guard lane conductors against `git push` or `gh` writes. Only the prompt forbids them. Set `SDLC_ROLE` for lane drivers.

## Constraints
What must not change. "None" if none.
