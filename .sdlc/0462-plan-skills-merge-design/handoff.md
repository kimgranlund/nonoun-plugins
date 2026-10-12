---
id: T-0462
title: "Design: merge the plan-* skills into /plan with kinds, shared rules and one lint"
type: spike           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
budget_usd: 6
---

## Question
Can plan, plan-goal, plan-campaign, plan-doc and plan-fanout become one `/plan` skill with kinds (steps, doc, goal, campaign, fanout), a shared rules reference and one lint, what does each old skill add that the merge must keep, and what does the merge cost?

## Goal
A design, read by the maintainer before any build, for a single `/plan` entry with kinds, plus `plan-loop` and `run-plan` unchanged, and `plan-verification` as a shared reference.

## Intent
- Do: produce an architect design with: (1) a line-by-line overlap table of `plugins/sdlc-lite/skills/{plan,plan-goal,plan-campaign,plan-doc,plan-fanout,plan-verification}/SKILL.md` and their references (what each unique rule, template and check adds, and what is duplicated text); (2) the merged `/plan` contract: kinds `steps`, `doc`, `goal`, `campaign`, `fanout`, arguments, what runs first (read a `clarify` handoff and ask only missing slots), the shared reference `skills/plan/references/plan-rules.md` (outcome block, stop rules, Authorization, budget, `Goal line`), a dry-run output (lint result, cost against the cap, lane plan from `fanout.py --dry-run`), and the length target; (3) which values are derived by script instead of written by the model (lane grouping and overlap, cost from `budget` rows, the `Goal line`); (4) the `plan_check.py` change (one `plan` kind with `goal`, `campaign` and `fanout` as views) and the `check.py` item 31 change, with the negative controls each needs; (5) the migration: thin redirect stubs for the old skill names for one release, the routing check (`skills/*/evals` or the routing corpus) re-run, the consumer upgrade note, and the Codex adapter mapping; (6) the controlled-language rules for plan artifacts from T-0461; (7) rejected alternatives (keep seven skills and only share a reference; merge only plan-goal and plan-campaign into plan-doc; a plan-doc-only world with no `/plan goal`); (8) the build split into tickets with files and checks, in an order that avoids editing `plan_check.py`, `check.py` and `core.md` at the same time as T-0460 and T-0461; (9) a replay plan: five asks through old and new skills, measured by lint pass rate and the number of questions asked.
- Non-goals: building anything; editing any skill, script or check; a model or effort change.
- Done when: the architect result names the recommended merge, the rejected alternatives, the overlap table, the migration and the first build ticket with its files, checks and size, and states what is unverified.

## Context
Maintainer decision 2026-10-11: file this spike after the discussion of merging the plan skills (seven skills today, same ingredients: Outcome block, stop rules, Authorization, budget, `plan_check.py` lint). Existing: `docs/specs/sdlc-lite/plan-doc-executor.md` (the plan doc already ends in a fenced `Goal line`), `docs/specs/sdlc-lite/plan-verification.md`, `plugins/sdlc-lite/scripts/plan_check.py` (kinds goal, loop, fanout, campaign, plan, clarify), `check.py` item 31 (the phrase set of every block-returning plan skill), `skills/clarify/SKILL.md` (T-0448, plan-ready handoff), T-0461 (controlled language), T-0460 (report skill; edits `core.md`). Evidence is by reading; no routing data shows today's names misroute, so say so.

## Constraints
Read-only. No model or effort change. Mark any claim about misrouting or confusion `[U]` unless a record shows it. Budget cap $6; stop and report at it.
