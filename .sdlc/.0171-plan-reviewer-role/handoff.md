---
id: T-0171
title: "Independent plan-reviewer role before implementation"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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

## Decisions
Made 2026-09-30, after the Codex session's review of the Codex allocation. Decision 1 is the user's; the rest are defaults the user accepted by asking for the build, recorded so the planner does not reopen them.

1. Claude row: `plan-reviewer` runs on Opus high (user choice). It never shares the planner's family: after an Opus planner (L2) `run.sh` moves the review to Fable high; after a Fable or Sonnet planner it stays Opus high.
2. Codex: Astra high reviewing Sol plans, and `gpt-6.1-sol` high reviewing Astra plans, using the existing `verifier_alternates` map keyed by the newest planner result's recorded model. A `plan-reviewer` entry in `models.json` at level L1.
3. Required for: any plan by planner L3, any plan with a step at builder L4 or L5, any plan with a merge step, and every replan. Routine plans keep structural validation alone.
4. Output: `## Verdict` with `pass`, `replan`, or `blocked`, plus `## Findings` tied to steps. `pass` proceeds to `steps.py split`. `replan` takes the existing plan-defect route in `/chain` 3 with the findings appended under `## Plan review`, and after the second review that says `replan` the conductor stops and asks the user. `blocked` means a design decision is missing and always stops for the user.
5. `run.sh` required section for the role is `Verdict`, allowed values `pass|replan|blocked`.

## Constraints
Pipeline roles stay routed through `scripts/run.sh`. Existing Claude model rows do not change. The failing check lands before or with the role.
