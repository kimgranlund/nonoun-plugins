---
id: T-0301
title: "Conductor schedules the rerun after a 429 limit"
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When `run.sh` or `solo_run.py` writes a `.limit` marker with a reset time, the conductor schedules the rerun for after that time instead of a human noticing.

## Context
Idea only, no build in the 0.20.11 batch. Source: agent-ui root-cause 2026-10-06 section 3 (429 session limit, "resets 1:40pm"). Depends on T-0298. Open: schedule skill or a supervisor wake.
