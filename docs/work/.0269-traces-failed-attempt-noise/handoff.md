---
id: T-0269
title: "traces detector reports failed attempts as missing a runs.jsonl row"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The traces detector stops reporting failed and interrupted attempts as missing a `runs.jsonl` row.

## Context
Source: maison `.sdlc/tickets/.0130-sdlc-lite-run-waste/review/report.md`, draft 1. `attempt <id>: attempt failed has no runs.jsonl row` is reported 21 times, but `run.sh:526` appends a row only after a successful result.
Fix (settled in the draft): in `traces/detectors/escalation.py` `attempt_without_run_row`, skip `failed` and `interrupted` attempts; keep `completed` and status-less. Update dependents: `traces/selftest.py` fixture at about 1166-1173 (completed, severity 2), the corpus expectation at about 1930, `thresholds.py` key `attempt-without-run-row-failed`, and the docstring at `escalation.py:43`.
Acceptance: the three `_esc_repo` commands in draft 1 plus `traces.py selftest`.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
