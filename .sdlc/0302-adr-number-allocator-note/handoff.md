---
id: T-0302
title: "ADR number allocator note (repo-owned, docs only)"
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A short repo-owned note (docs only) on allocating ADR numbers so two sibling worktrees never take the same one.

## Context
Idea only, no build. Source: agent-ui root-cause 2026-10-06 section 2: T-0012 and T-0014 both took ADR-0235 in sibling worktrees, found by a plan reviewer by luck. The allocator is the consumer repo's to own; sdlc-lite adds only a docs note (for example in handoff-format or onboard), not code.
