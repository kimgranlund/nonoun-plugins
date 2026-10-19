---
id: T-0249
title: "plan-goal skill and the plan_check.py validator"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The /sdlc-lite:plan-goal skill returns one `/goal <text>` block that passes plan_check.py goal, and plugins/sdlc-lite/scripts/plan_check.py (shared validator for goal, loop and fanout) exists with a selftest.

## Intent
- Do: skills/plan-goal/SKILL.md (gather inputs from thread and repo, apply the goal rules, return one fenced /goal block plus a 5 line why-this-plan and an explicit authorization list, run plan_check.py goal before returning); scripts/plan_check.py with goal, loop and fanout subcommands (exit 0 pass, 1 named findings); selftest with a mutant per rule wired into check.sh; check.py guard; routes. Goal rules: checkable done-when, numbered scope verified with tickets.py check, how to work (lane first, solo default S and M, scope freeze, lane cap, one writer per file, replan cap one, claims from commands), stop rules with numbers (total and per-ticket money cap, rate or weekly limit, three 529s) writing state to .sdlc/notes.md, explicit authorization (publish, push, tag and external writes are never implied), done-when covering the stopped-on-limit case; note a goal pasted as text is not registered until run as /goal.
- Non-goals: running /goal or /loop (they cannot run headlessly); model or effort defaults; a version bump, tag, push, or publish.
- Done when: the skill, validator (shared in T-0249), guard and routes exist, the plan_check selftest passes with a negative control per rule, and the batched L3 verifier passed.

## Context
User request: 'plan and create skills for planning fanout, goal, and loop sessions: /plan-fanout, /plan-goal, /plan-loop ... return a compliant copy/paste format for user to input and execute'. Built together on branch plan-skills with one batched verifier. Philosophy: "Done is better than perfect."

## Constraints
No harness: references; Codex adapter line; one authoritative place per fact. No em dashes.

## Closed

2026-10-05: built on branch plan-skills; verified by one L3 Fable verifier; see docs/reports/plan-skills-live-run.md
