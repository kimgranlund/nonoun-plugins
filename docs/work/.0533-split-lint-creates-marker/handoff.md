---
id: T-0533
title: "steps.py split lints each step alone: a path an earlier step creates ([creates: ...]) reads as a plan defect (maison T-0546 item 32)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py split` and `steps.py lint` accept a step that cites a file an earlier step in the same plan creates, so a sound plan is not refused as a plan defect.

## Intent
- Do: when linting step N, treat a path as existing if an earlier step's handoff or the plan marks it `[creates: <path>]` (or the plan's equivalent create marker; find the one the planner contract and `plan_check.py` already use). Apply the same rule in `split --only N`.
- Do: keep the existing refusal for a path no step creates and the tree lacks.
- Non-goals: changing the planner's marker syntax.
- Done when: `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with a case where step 2 cites a path step 1 marks as created (lint ok) and a negative control where the same path has no create marker (refused as before).

## Context
- maison T-0546 item 32 (2026-10-13, on 0.22.7): ui-kit-maison T-0528 steps 2 and 5 cite `probe-statements.md` created by step 1; split printed "plan defect: replan this step"; both lint ok once step 1 ran.
- Same class seen here: T-0520 step 2 was refused at split for cited paths (`.sdlc/review/handoff.md`, `.sdlc/generate/handoff.md`) inside a throwaway project, which cost one replan (`.sdlc/.0520-ui-designer-agent/refusals.jsonl`). Check whether that case (a path outside the repo tree, described in prose) needs the same or a separate rule, and say which in the result.

## Constraints
The lint must still be able to fail: keep the negative control observed red.

## Closed

2026-10-13: solo L2 built, verifier L2 pass, merged from fanout/wave67-s. The T-0520 case (paths outside the repo tree) is a separate rule, already covered by the foreign-path exemption when declared
