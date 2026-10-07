---
id: T-0220
title: "Re-verify T-0212's check-packaging fix"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
T-0212's fixed check-packaging defect is independently re-verified.

## Intent
- Do: No code change. The T-0212 L3 verifier returned fail on `scripts/check-packaging.py` pinning the PreToolUse route count at 3; the fix landed afterwards with no re-verification committed. Re-verified with a narrow L2 verifier. The Codex note in docs/references/claude-hooks.md already exists, so nothing was added there.
- Non-goals: model or effort defaults; a version bump, tag, push, or publish.
- Done when: the change is merged into local main with checks green and an independent verifier passed.

## Context
Closes a known limit listed in docs/reports/release-0.20.5.md. Built under the burn-down rules (one handwritten step, one L2 verifier).

## Evidence
Independent L2 verifier: pass (`.sdlc/verify-0220/step-1/verifier-L2.md`). check-packaging no longer pins 3 (it asserts 4 routes and the Edit|Write|NotebookEdit matcher). With the hook unregistered in a throwaway worktree, check-packaging.py and check.py each go red, and the registered tree is green.

## Constraints
None beyond the repository guidance.

## Closed

2026-10-04: Built and verified on branch limits (L2 verifier pass, evidence in the ticket); merged into local main in the limits merge.
