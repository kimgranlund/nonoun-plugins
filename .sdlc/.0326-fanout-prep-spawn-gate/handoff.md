---
id: T-0326
title: "fanout prep lane dispatch is refused by the spawn gate (T-0287 finding 2)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py prep` lane prompts pass the spawn gate and each lane writes a dispatch record, so a fanout lane runs as a sub-agent.

## Intent
- Do: Finding 2 in docs/reports/2026-10-07-subagent-mode-live.md: the prep prompt has no `Handoff:` line and prep writes no record, so the spawn gate denied both lane spawns. Make prep emit the Handoff line and write the dispatch record (the solo-S|M|L form the gate now allows, commit 08bf3599). Done when a selftest spawns two lanes through the gate and both are allowed, and a lane prompt without the line is still refused (observed).
- Non-goals: any model or effort change; the account-switch criterion of T-0287.
- Done when:
  - The observed result above holds; `check.py`, `tickets.py check` and the touched script selftests pass.

## Context
Found by the T-0287 live run on branch subagent-w5. Files: plugins/sdlc-lite/scripts/fanout.py, dispatch.py, hooks.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
