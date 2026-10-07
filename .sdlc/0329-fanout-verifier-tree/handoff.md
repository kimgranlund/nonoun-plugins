---
id: T-0329
title: "Fanout verifier prompt Tree: points at the main tree, not the lane worktree"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The verifier prompt written for a fanout lane names the lane worktree as its Tree, and a selftest shows the prompt for a worktree lane carries the worktree path.

## Intent
- Do: The verifier prompt written for a fanout lane names the lane worktree as its Tree, and a selftest shows the prompt for a worktree lane carries the worktree path.
- Non-goals: model or effort changes; the account-switch criterion.
- Done when:
  - The goal holds (observed); check.py, tickets.py check and the touched selftests pass.

## Context
Found by the live rerun appended to docs/reports/subagent-mode-live-2026-10-07.md (section `Rerun after T-0326 to T-0328`).

## Constraints
No em or en dashes. No push or publish.
