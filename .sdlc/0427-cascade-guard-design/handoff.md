---
id: T-0427
title: "Design a cascade guard: a per-ticket agent-run counter that stops and asks, and a template-instance plan review"
type: idea            # feature | bug | chore | spike | idea
status: proposed
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A design for stopping a "verify the verifier" cascade: a per-ticket count of agent runs that stops and asks after N, and a reviewed route for a plan that is a mechanical copy of a passed plan.

## Intent
- Do: design only, Markdown, docs/specs/sdlc-lite/cascade-guard.md with a status line. Read the maison report in this ticket's Context and the maison evidence files named there, scripts/steps.py (replan cap, plan review routing), scripts/dispatch.py, scripts/fleet_collect.py (runs.by_ticket), agents/plan-reviewer.md and docs/specs/sdlc-lite (T-0421 bounded plan correction, T-0400 held criteria). Decide and write down: (1) a cascade counter: agent runs per ticket step from runs.jsonl, the threshold N, where it is checked (prepare), what it prints, and that it stops and asks the maintainer, never silently continues; the override is explicit and recorded; (2) a template-instance plan review: how a plan is shown to be a mechanical copy of a passed plan (a diff that touches only shas, counts and ids, proven by a command), one reviewer on the diff only, and that it does not count against the replan cap; what forces the normal route; (3) the rule that a verifier never spawns a second verifier on its own report (check what block-role-spawn already enforces); (4) how this relates to T-0421 and to the replan cap of one; (5) K-004-style measures from the collector; (6) the build split into tickets with sizes, a negative control each.
- Non-goals: building it; model or effort changes.
- Done when:
  - The design names the files a build changes, the counter threshold with the evidence for N, the template-instance proof as a command, and the rejected alternatives; docs_check.py and check.py pass; no dashes.

## Context
Maison conductor bug report, 2026-10-10 (user asked it to send): the pipeline rewards more checking of checks. T-0378 and T-0379 plans were the T-0362 plan with shas and counts swapped, yet each got two plan-review runs and a replan (maison .sdlc/tickets/.0378-integration-wave-3/plan-reviewer-L1.md and plan-reviewer-L1-2.md; .sdlc/tickets/0379-integration-wave-4/plan-reviewer-L1.md and plan-reviewer-L1-2.md; about 40 to 60 minutes and 2 runs each); the second-replan stop then forced an override question to the user. T-0339 verifier-L3 failed a ticket on a Done-when that contradicted its Non-goals, which spawned an L2 reverify and a second verifier (.sdlc/tickets/.0339-examples-axe-inherited-nodes/verifier-L3.md). Maison counted 11 agent runs on T-0378 steps 1 and 2. Maison suggested: a template-instance lane, red-checkpoint keyed to criterion text (T-0425), record removing the tmp prefix (T-0426), a verifier never spawning a verifier, a cascade counter. Maison applies a self-cap on T-0379: one plan review, one verifier per step, no reverify of a pass.

## Constraints
No em or en dashes. No push or publish. Do not remove any worktree or branch outside the role's own tmp prefix.
