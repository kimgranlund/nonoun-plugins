---
id: T-0250
title: "plan-loop skill"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The /sdlc-lite:plan-loop skill returns one `/loop <interval> <prompt>` (or dynamic form) block that passes plan_check.py loop.

## Intent
- Do: skills/plan-loop/SKILL.md plus a references file for cron and cost rules; interval token must be a leading ^\d+[smhd]$ or a trailing 'every N unit' clause ('20mins:' falls into dynamic mode: mistake made in the thread); seconds round up to minutes, non-dividing intervals round to a clean one, avoid :00 and :30 when approximate; recurring jobs expire after 7 days and run only while the REPL is idle; prompt self-contained, idempotent, reads state from files or commands, reports progress since the last run, has a stop condition; prefer Monitor for event waits; dynamic mode with a 1200 to 1800 s heartbeat when cadence depends on the work; cost note.
- Non-goals: running /goal or /loop (they cannot run headlessly); model or effort defaults; a version bump, tag, push, or publish.
- Done when: the skill, validator (shared in T-0249), guard and routes exist, the plan_check selftest passes with a negative control per rule, and the batched L3 verifier passed.

## Context
User request: 'plan and create skills for planning fanout, goal, and loop sessions: /plan-fanout, /plan-goal, /plan-loop ... return a compliant copy/paste format for user to input and execute'. Built together on branch plan-skills with one batched verifier. Philosophy: "Done is better than perfect."

## Constraints
No harness: references; Codex adapter line; one authoritative place per fact. No em dashes.

## Closed

2026-10-05: built on branch plan-skills; verified by one L3 Fable verifier; see docs/reports/plan-skills-live-run.md
