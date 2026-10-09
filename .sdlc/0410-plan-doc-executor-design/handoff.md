---
id: T-0410
title: "Plan-doc contract, plan_done.py and a run-plan executor any builder tier can drive with /goal"
type: feature        # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-09
claimed_by: claude 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A written design so the maintainer can plan work, goals, KPIs and rubrics in one session and then tell a smaller, faster model `/goal complete build and verify <plan-doc.md>` and have it finish unattended, with the verifier still independent.

## Intent
- Do: design only, Markdown, in docs/specs/sdlc-lite/plan-doc-executor.md with a status line. Read skills/plan-goal, skills/plan-verification, skills/plan-campaign, docs/specs/repo-onboarding/goals-and-kpi.md, scripts/plan_check.py, scripts/fanout.py, scripts/dispatch.py, scripts/run_lifecycle.py, agents/conductor.md and docs/specs/sdlc-lite/restart-and-blocked-run-plan.md (written by the planner in .sdlc/plan-reliability-docs; the first customer). Decide and write down: (1) the plan-doc contract: one file holding goal, KPIs, rubric, ordered steps with builder levels and criteria, authorization, stop rules and per-step dollar caps, in a fixed shape plan_check.py can lint (name the new `plan_check.py plan` rules and a negative control each); (2) `plan_done.py <plan-doc>`: exits 0 only when every step ticket is closed with an independent verifier pass, no held or deferred criterion remains, and each KPI measure reads on the right side of its target, else prints what is open; this is the condition the stop hook evaluates; (3) the `run-plan` skill: what a smaller model reads, files, dispatches and records, how it upserts corpus docs (goals, kpi, specs, skills, entry files) and repairs stale records in the same change, and how it resumes after a crash with run_lifecycle recover; (4) model-agnostic: the plan names the executor tier per step or per run (Haiku 5.5 high, Sonnet low or high, or any builder agent), and the design says what minimum the executor must be able to do and what stays with a stronger seat (verifier, plan review at L4 and L5); (5) the guardrails: executor never grades itself, publish/push/tag/onboard setup only when the plan names them, replan cap one then stop and write state; (6) the build split into tickets with sizes, and a live-run plan using the goal 002 plan as the first customer; (7) rejected alternatives (extend plan-goal only; a new long-lived orchestrator agent).
- Non-goals: writing the skill, plan_done.py or any plan_check.py rule in this ticket; model or effort changes (the executor tier is chosen per plan, not changed globally).
- Done when:
  - The design names every file the build changes, the new plan_check.py plan rules with a negative control each, the plan_done.py exit conditions as a truth table, and the live-run steps.
  - docs_check.py and check.py pass.

## Context
Maintainer direction, 2026-10-09: work at a higher level of abstraction. Plan with a session (intent, goals, KPIs, rubrics), then tell a smaller faster model `/goal complete build and verify {plan-doc.md}, upsert corpus docs, skills, etc.`. Executor candidates named by the maintainer: Haiku 5.5 High, Sonnet Low, Sonnet High, any builder agent. First plan doc: the goal 002 reliability plan. Pieces that exist: goals and kpi homes (T-0392), plan-verification (T-0407), plan-campaign (T-0406), fanout and solo lanes, plan-goal. Crash recovery (goal 002) is a prerequisite for unattended runs.

## Constraints
Design only. No em or en dashes. No push or publish. Build waits for its own ticket and the maintainer's approval.
