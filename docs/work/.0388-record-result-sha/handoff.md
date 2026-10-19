---
id: T-0388
title: "dispatch.py record stores result_sha256 in the attempt and the runs row"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0383]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A recorded result has an identity that survives later edits: `dispatch.py record` stores the sha256 of the result file in the attempt record and in the runs row.

## Intent
- Do: in scripts/dispatch.py record (about lines 592 to 630, where only handoff_sha256 is stored today), compute sha256 of the result bytes at the moment it is accepted, after any header record writes, and store it as `result_sha256` in `<role>-L<n>.attempt.json` and in the runs.jsonl row. Document the field in the run-operations reference. Keep old attempt files readable (field absent). A later structural change (binding acceptances to a small canonical verdict record written once at record time) is out of scope and noted as a follow-up design.
- Non-goals: model or effort changes; binding anything repo-side (maison's renderer-adoption.mjs binds the review file bytes and needs its own repo-side guard: refuse a review whose attempt record is not status completed).
- Done when:
  - A selftest: record on a fixture stores result_sha256 equal to the sha256 of the result file; editing the file afterwards no longer matches, so the mismatch is detectable (observed failing first).
  - check.py, tickets.py check, dispatch and solo_run selftests, both generate --check pass.

## Context
Independent fable-high review of the maison delivery loop (maison .sdlc/tickets/0302-process-review-fable/architect-L1-2.md, section Interfaces), forwarded 2026-10-08. Maison's integration solo copied a verifier report while the verifier was still writing it, and its acceptance had to be rebound in a later commit that regenerated 543 files. The repo-side guard is maison's; this is the plugin-side identity. Starts after T-0383, which edits dispatch.py record.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-08: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
