---
id: T-0254
title: "Handoff and evidence lints with citation resolver"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Add warning-level lints: no template placeholder text in a closed ticket, and a citation resolver that opens every path:line in a document.

## Intent
- Do: Extend tickets.py check for placeholder text in closed tickets, and add a short script that resolves every backticked path:line in a named doc and that each cited evidence path is tracked in git. Start as warnings.
- Done when: positive and negative controls exist for both lints and the gap analysis doc itself resolves clean.

## Context
Gap analysis R6. Both failures happened: placeholder text in .sdlc/verify-0224/verifier-L3.md:15 and an unbacked record in .sdlc/verify-0229/verifier-L3.md:11. The architect review found three wrong citations a resolver would catch (docs/validation/progressive-context-gap-analysis-review.md). Lane: solo. Philosophy: Done is better than perfect.

## Constraints
No push, tag, version bump, or publish. No em dashes. Preserve other agents' worktrees.
