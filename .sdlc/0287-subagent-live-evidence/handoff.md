---
id: T-0287
title: "Live evidence for sub-agent mode, including an account switch"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0283, T-0284, T-0285, T-0286]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Prove sub-agent mode end to end on a throwaway project and record what it did across an account switch.

## Intent
- Do: Live evidence for sub-agent mode, including an account switch.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `docs/reports/subagent-mode-live-<date>.md` records, with raw run records: one solo S ticket, one chain ticket (planner, builder, verifier), and one two-lane fanout, each `transport: subagent`; `test "$(grep -c "^| L[1-3] |" docs/reports/subagent-mode-live-*.md)" -eq 3`.
  - The verifier in each run ran on a different model family than the builder, shown from the dispatch record and, when probe P5 allows, from the transcript model field.
  - One run spans a `/login` switch: the record states what survived and what needed `dispatch.py resume`, with the resume rung used.
  - Estimated cost per run is within the 35 percent calibration band against the session cost shown by the host, or the report states the gap.

## Context
Design section 9 lists what is unverified; this ticket closes each item it can and marks the rest.

## Constraints
Throwaway project only; no push or publish. No em dashes. No push, tag, or publish.
