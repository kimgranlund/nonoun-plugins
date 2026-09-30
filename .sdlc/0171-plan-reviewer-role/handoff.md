---
id: T-0171
title: "Independent plan-reviewer role before implementation"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
A cross-cutting or risky plan, or any replan, gets an independent semantic review before a builder starts, and a defective plan is rejected before it costs a build.

## Intent
- Do: a `plan-reviewer` role that reads the goal, the proposed plan, the relevant code, and supporting evidence in a fresh context, and reports `pass`, `replan`, or `blocked` with findings tied to steps and evidence. It checks goal coverage, assumptions, interfaces, dependency ordering, scope, acceptance criteria, and whether the assigned builder can execute each step with no unresolved design decision. It never rewrites the plan or edits code. It runs on a different model from the planner.
- Do: strengthen the planner's handoff where the reviewer needs it: implementation targets, settled interface decisions, dependencies, focused checks, unresolved assumptions. Missing design decisions return to planning and never become the builder's job.
- Non-goals: reviewing routine plans, which keep structural validation alone; changing any existing Claude or Codex model row.
- Done when: the role exists on both hosts through `scripts/run.sh` with its output contract, generated Codex profiles pass parity, alternate selection has a negative control, and a live planning, review, build, verify run in a throwaway project shows the reviewer rejecting an intentionally defective plan. Completion time, replans, rebuilds, and correctness are measured against the same tasks without the reviewer before any claim that it helps.

## Context
Proposed by the Codex session on 2026-09-30 after inspecting the contracts at 47eb722, and judged a real gap: `steps.py split` checks only structure, and the build verifier finds design defects after a builder run.

Decisions needed before building:

1. Claude model and effort for the new role. `scripts/run.sh` has no row for it, so a run exits 2 until one exists. A different family from the planner is the natural rule: Opus reviewing Fable plans, Fable reviewing Opus plans, mirroring the verifier rule.
2. Codex models: Astra high reviewing Sol plans and Sol 6.1 high reviewing Astra plans, as the Codex session proposed.
3. When a review is required: cross-cutting or risky plans and every replan, as proposed. The rubric needs a definition of "risky".
4. How `steps.py next` and `/chain` route `pass`, `replan`, and `blocked`, and how a `replan` from the reviewer interacts with the existing plan-defect and recurring-finding replan rules.
5. The output section name `run.sh` requires for the role, and the level-rubric and handoff-format entries.

Touches: `agents/plan-reviewer.md`, `scripts/run.sh` role and section tables, `scripts/check.py`, `skills/level-rubric`, `skills/handoff-format`, `skills/chain`, `agents/planner.md`, `adapters/codex/models.json`, generated Codex agents, `docs/codex-role-execution.md`.

## Constraints
Pipeline roles stay routed through `scripts/run.sh`. Existing Claude model rows do not change. The failing check lands before or with the role.
