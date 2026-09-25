---
id: T-0078
title: "skills/file/SKILL.md line 18 still says block-publish 'only fires..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0065
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0065 (fanout-py-s-default-lane/filer-L1.md):

skills/file/SKILL.md line 18 still says block-publish "only fires when `SDLC_ROLE` is set by `scripts/run.sh`", which is stale now that fanout.py sets `SDLC_ROLE=conductor` for lane drivers (T-0065).

## Constraints
What must not change. "None" if none.
