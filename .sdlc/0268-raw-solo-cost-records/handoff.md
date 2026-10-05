---
id: T-0268
title: "Raw claude -p solos have no solo_run cost records"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
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
