---
id: T-0339
title: "A fanout or solo lane commit never stages run artifacts that fail repo gates (*.log, .run.lock, *.running)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fanout lane commit never stages verifier-L3.log or .run.lock, which failed the consumer repo's em-dash gate on two ultimate-tokens lanes and cost a manual strip, amend and rerun. Make the lane commit path in fanout.py and solo_run.py exclude *.log, .run.lock and *.running (keep *.md, runs.jsonl and *.attempt.json that the closure needs); add a selftest with a planted log and lock file in the lane tree.

## Intent
- Do: 
- Non-goals: model or effort changes; anything outside the named files.
- Done when:
  - The goal holds, shown by a selftest case that fails on the old behavior (observed) and passes now.
  - check.py, tickets.py check and the touched selftests pass.

## Context
Found by the 2026-10-07 fleet retro (ultimate-tokens conductor, .sdlc/fleet-retro-2026-10-07.md in that repo, rows marked [V]; read-only).

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
