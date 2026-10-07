---
id: T-0316
title: "Live headless chain run on Codex, recorded"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A real headless chain run on Codex is recorded, so Codex execution has live evidence like Claude does.

## Intent
- Do: In a throwaway repo under /tmp, run one small ticket through the full chain on Codex (planner, builder, verifier through run.sh with SDLC_BACKEND=codex or the documented Codex transport) and a solo run via sdlc-solo-l1; record exact commands, models, durations and results in docs/reports/codex-live-evidence.md. Say what worked, what did not, and what remains unverified (the native subagent transport vs exec).
- Non-goals: Changing the Codex adapter or model table; the Claude sub-agent flip (T-0287).
- Done when:
  - The report shows a run.sh chain and a solo run that finished on Codex with validated result files (results.py validate output included).
  - Any failure is recorded with its log path and filed as a ticket.
  - No model or effort value changed; `codex_roles.py generate --check` passes.

## Context
From dropped T-0208: a headless chain run on Codex stayed unproven (docs/reports/parked-tickets-review-2026-10-06.md). T-0287 covers Claude sub-agent evidence only. Read docs/references/codex-role-execution.md first. Costs Codex runs; keep the task tiny.

## Constraints
No change to any model or effort value. No em dashes. No push, tag or publish. Independent verifier per ticket; checks need a positive case and an observed negative control.
