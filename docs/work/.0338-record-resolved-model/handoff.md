---
id: T-0338
title: "dispatch.py record writes the transcript's resolved model into the run record"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py record --transcript` writes the model the sub-agent actually ran on (the transcript's assistant `message.model`) into the runs.jsonl row, beside the alias in `model`.

## Intent
- Do: read the transcript model field in `cost_estimate.transcript_usage` or a sibling, pass it through `record()` into the run row as `resolved_model`, with a selftest case and a negative control (no transcript, no field).
- Non-goals: any change to the scout model or effort default (a user decision).
- Done when: a record with a transcript shows `resolved_model` in runs.jsonl; dispatch selftest and check.py pass.

## Context
Live scout spawn 2026-10-07 (docs/reports/2026-10-07-subagent-mode-live.md, section Live scout spawn): the alias haiku resolved to claude-haiku-4-5-20251001, visible only in the transcript. On a Max login the alias has resolved to Sonnet 5.5 before (bench-scout-pin), so the run row should say which model ran. Files: plugins/sdlc-lite/scripts/dispatch.py (record), plugins/sdlc-lite/scripts/cost_estimate.py.

## Constraints
No em or en dashes. No push or publish. Model and effort defaults unchanged.

## Closed

2026-10-07: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
