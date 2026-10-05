---
id: T-0263
title: "A builder blocked by a stale lane routes to replan, not rebase-and-resplit"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A blocked builder whose cause is a stale lane (missing merged prerequisites, not a plan defect) has a named route: rebase and resplit the step.

## Context
`steps.py next` prints `replan` for a block whose cause is a stale lane. The right route is rebase the lane onto its merged prerequisites, move the step dir to `.superseded-N`, then `steps.py split --only N`.
Fix: route or message in steps.py naming that, documented in `docs/maintenance/sdlc-internals.md`, with a regression test.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-05: steps.py next prints resplit for a stale lane block (8ed117d); verifier L3 pass, verify-defect-fixes-0209
