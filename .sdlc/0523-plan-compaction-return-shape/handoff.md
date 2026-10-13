---
id: T-0523
title: "/plan compaction output does not match the kind's declared return shape"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/plan compaction` prints exactly the return shape its kind declares.

## Intent
- Do: reconcile the live output with the kind's return shape in the `plan` skill. Observed: one sentence before the fence, three attention lines plus a next-action line after `Run:`, and the lint's `lines:` and `pin:` lines merged into one. Fix the skill text or the shape, whichever is wrong, and keep one authoritative statement.
- Non-goals: `--write-handoff`, the CLAUDE.local.md reload check.
- Done when: `plan_check.py` selftest covers the shape with a positive case and a negative control, and a replay of the kind matches it.

## Context
Filed as fix-now in the T-0465 close notes in `.sdlc/notes.md`.

## Constraints
None beyond the repository guidance.
