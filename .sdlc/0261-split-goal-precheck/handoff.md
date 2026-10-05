---
id: T-0261
title: "steps.py split needs ## Goal; fail fast before any planner runs"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py split` fails fast, before any planner or reviewer runs, when the task handoff lacks `## Goal`.

## Context
`steps.py split` requires `## Goal` in the task handoff (`read_goal`). Four planner runs and four plan reviews were spent (about 2 hours, maison T-0105) before a handoff using `## Task goal` was caught at split.
Fix: a precheck with a clear message that names the missing heading, run where a planner would be launched (steps.py lint/plan entry), and a regression test showing it fails before and passes after.

## Constraints
No push, tag, version bump, or publish. No em dashes.
