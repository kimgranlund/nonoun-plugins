---
id: T-0437
title: "Link the live-run record from the design doc"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
claimed_by: claude 2026-10-11
verify: auto
budget_usd: 3
---

## Goal
The design doc for the plan-doc executor links the record of its first live run and rehearsal.

## Intent
- Do: In docs/specs/sdlc-lite/plan-doc-executor.md section 8.1 add one line: the first live run and rehearsal are recorded in docs/reports/2026-10-11-plan-doc-live-run.md.
- Non-goals: any other file; any other edit to the design doc.
- Done when: the acceptance criteria below pass.

## Context
Read first: docs/specs/sdlc-lite/plan-doc-executor.md. Upserts: only docs/specs/sdlc-lite/plan-doc-executor.md. Plan doc: .sdlc/plan-doc-hardening/plan-doc.md step 2, cap $3.

## Acceptance criteria
- (red) `git grep -q '2026-10-11-plan-doc-live-run' -- docs/specs/sdlc-lite/plan-doc-executor.md`
- (guard) `python3 plugins/sdlc-lite/scripts/docs_check.py --root . >/dev/null`
- (guard) `git grep -q 'git grep' -- .sdlc/plan-doc-hardening/plan-doc.md`

## Constraints
None.
