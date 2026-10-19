---
id: T-0355
title: "dispatch.py record refuses a solo_run.py dispatch file as not a dispatch file, so solo lanes get no cost rows"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
dispatch.py record accepts the dispatch file that solo_run.py writes, so a solo lane gets a runs.jsonl row with cost.

## Intent
- Do: gen-ui-kit's conductor reported dispatch.py record refusing a solo_run.py dispatch file ('not a dispatch file', raised by the RECORD_KEYS check in dispatch.py record), so 17 solo lanes have no cost rows. Reproduce with the plugin version gen-ui-kit runs and with current main, find which keys the solo dispatch file lacks, and fix the writer or the reader. Coordinate with T-0352, which also touches solo rows.
- Non-goals: Model or effort changes.
- Done when:
  - A selftest records a solo dispatch file end to end and the runs.jsonl row carries cost, agent_id and duration (observed failing first).
  - check.py, dispatch, solo_run, fanout selftests pass.

## Context
Fleet cost analysis of 2026-10-07 (all-time deduped run records, five repos): verifier L3 Fable $1,291 over 198 runs (about $6.5 each) versus verifier L2 Sonnet about $0.50 each; solo L2 Sonnet xhigh about $406 ($3.31 to $5.53 per run). The user approved these four proposals on 2026-10-07. Reported by the gen-ui-kit conductor; its earlier waves used headless claude -p lanes and are invisible to the collector.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-07: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
