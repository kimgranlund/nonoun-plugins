---
id: T-0378
title: "Record required red checks before a builder implements, and record a deviation when a run lacks them"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A builder run records its tagged `(red)` criteria before it edits source, and a completed run without that checkpoint records a process deviation instead of passing silently.

## Intent
- Do: inspect agents/builder.md, scripts/specgate.py, scripts/run.sh and the Codex native exchange, and reuse the existing red-control facility where it applies. Record the exact handoff criterion, base sha, command, exit and timestamp before new implementation changes, bound to the current attempt and the handoff content hash. A criterion already green on the baseline is surfaced, not called a successful red control. A resumed build distinguishes a preserved original red checkpoint from a retrospective base control. A completed run missing the checkpoint records a process deviation; do not infer ordering from a final report or a later baseline run. Keep three things distinct in the record: runner format acceptance, builder test success, and independent verification. State per host whether enforcement is procedural or mechanically guaranteed: on Claude a hook could enforce it, on Codex no hook exists, so say procedural and do not invent a Codex hook.
- Non-goals: model or effort changes; resetting other agents' work; changing any repo's implementation; claiming red-before-edit for the observed run.
- Done when:
  - Tests cover: no tagged criteria, valid pre-edit controls, missing evidence, post-edit retrospective controls, and resumed work with evidence from an earlier attempt (observed failing first).
  - A run that completes without the checkpoint writes a process-deviation line that the verifier handoff and the filer read.
  - check.py, tickets.py check, the affected selftests, codex-selftest and both generate --check pass.

## Context
Idea forwarded by the maison conductor from Codex, 2026-10-08 (maison's T-0287; copy at the maison repo .sdlc/tickets/0287-codex-builder-red-checkpoint/handoff.md, reporter priority P2, budget 30 USD). Evidence: T-0152 step 9 fix pass in maison: a native sdlc-builder-l4 implemented items 9 to 11 and ran green checks before running either `(red)` command on the base; it disclosed this; both commands then failed on a clean base snapshot and passed on the changed tree, which shows the tests discriminate but cannot show red-before-edit ordering. Files there: .sdlc/tickets/0152-manifest-driven-renderers/step-9/{builder-L4.md,native-base-controls.md,builder-L4.attempt.json}, branch codex/0152-s9, base 5a096cc72, fix 512e3ec7. Independent Claude L3 verification of that step was running; its finding is not in this ticket. Related: T-0366 and T-0376 (base sha), which the checkpoint depends on for the recorded base.

## Constraints
No em or en dashes. No push or publish. The Codex host cannot be run live here; mark live Codex behavior unverified.
