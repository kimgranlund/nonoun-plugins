---
id: T-0264
title: "steps.py split has no override after a replan verdict"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Decide an override for `steps.py split` after a replan verdict.

## Context
split refuses with "a rejected plan is never split". In the field specgate refused a plan over 13 duplicate-criterion findings, and there was no way to proceed short of rewriting the plan. Needs a decision: an explicit flag, or specgate not counting duplicates as a rejection.

## Constraints
No push, tag, version bump, or publish. No em dashes.
