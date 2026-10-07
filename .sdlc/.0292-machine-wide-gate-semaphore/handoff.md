---
id: T-0292
title: "Machine-wide gate semaphore so a load stop line counts gates, not lanes"
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Heavy gates (npm test, browser shards, tsc) across sessions take a shared machine-wide lock, so a load stop line can count running gates instead of lanes.

## Context
Reported by the agent-ui conductor: lanes use about 2 percent CPU each, and the gates they run cause the load spikes. A lane count therefore says little about load; a gate count would. Not built; triage decides the shape (lock directory, slot count, wrapper vs hook) and whether it belongs in fanout.py or a standalone script.

## Constraints
Idea only, no build in T-0291. Never kill processes it does not own.

## Closed

2026-10-07: built in 0.20.11 as scripts/gate_lock.py (check.py guard 35); ticket left open by mistake
