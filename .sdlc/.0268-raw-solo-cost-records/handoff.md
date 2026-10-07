---
id: T-0268
title: "Raw claude -p solos have no solo_run cost records"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Teaching text points raw `claude -p` solo runs at `solo_run.py` so they get cost records.

## Context
Raw `claude -p` solos have no `solo_run` cost records. Check that the conductor and solo agent text already name `scripts/solo_run.py`; add a line where missing. Docs and agent text only, then `codex_roles.py generate` if shared bodies change.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
