---
id: T-0265
title: "Headless planner stalled on a denied rm permission prompt"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Find why a headless planner hit a permission prompt for `rm`, and make unattended roles fail fast instead of stalling.

## Context
A headless planner stalled once on a denied `rm` permission prompt (`tool_use_result` user-rejected). One occurrence. Check what the planner was removing (a scratch file?) and whether the planner prompt or tool allowlist should avoid it.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
