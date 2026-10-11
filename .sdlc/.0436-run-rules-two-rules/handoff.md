---
id: T-0436
title: "Two preflight and stop rules in run-rules.md"
type: chore           # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
claimed_by: claude 2026-10-11
verify: required
budget_usd: 3
---

## Goal
Two gaps the live run found in the run-plan run rules get a rule each: a driver started outside the plan's repository, and a step whose work already exists.

## Intent
- Do: In plugins/sdlc-lite/skills/run-plan/references/run-rules.md, Preflight: add one numbered item: run `git rev-parse --show-toplevel`; if it is not the repository that holds the plan doc, stop with state written (the host makes sub-agent worktrees from the session's repository). In The loop, after step 4: add one sentence: a solo that reports no diff possible because the step's (red) criterion already passes is a plan defect stop that names the commit that built it; the driver never closes that ticket itself.
- Non-goals: any other file; any other rule change.
- Done when: the acceptance criteria below pass.

## Context
Read first: plugins/sdlc-lite/skills/run-plan/references/run-rules.md and docs/reports/2026-10-11-plan-doc-live-run.md. Upserts: only run-rules.md. Plan doc: .sdlc/plan-doc-hardening/plan-doc.md step 1, cap $3.

## Acceptance criteria
- (red) `git grep -q 'show-toplevel' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`
- (red) `git grep -qi 'already passes' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py >/dev/null`
- (guard) `git grep -q 'plan_done.py' -- plugins/sdlc-lite/skills/run-plan/references/run-rules.md`

## Constraints
Edit only the file named in Upserts. Add the two rules and nothing else.

## Closed

2026-10-11: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
