---
id: T-0188
title: "Tighten the idle-host limit note: wait does not address the limit"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-01
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The idle-host limit note states correctly that `wait` does not address the limit and the unbuilt watcher is what would.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Decisions made, paths, links. Everything a clean-context agent needs; it sees nothing else.

## Constraints
What must not change. "None" if none.

## Closed

2026-10-01: fixed in session by /fix: the note no longer says wait addresses the idle-host limit
