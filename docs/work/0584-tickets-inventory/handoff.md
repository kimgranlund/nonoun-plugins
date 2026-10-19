---
id: T-0584
title: "tickets.py inventory: landed state by content and patch identity"
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py inventory` reports each open or recently closed ticket's real state: its branch, whether that branch's content is on main or a named integration branch (by ancestry, patch identity or equal files), and its newest verdict in correct order.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 6. maison hand-built `collect.py` and `classify.py`, and their architect found four defects: verifier sort order (lexical `verifier-L3-2` before `verifier-L3`), stale sibling branches, pointer branches, and records under unusual paths. This repo already owns the pieces: `order.py` (newest-result ordering), `lanes.py` landed tests, `order.py records-dir`. Idea ticket: shape before building.

## Intent
- Do: propose the command's output and which existing functions it composes. Note whether `order.py` already sorts `verifier-L3-2` after `verifier-L3` (it should; maison's bug was in their own script).
- Non-goals: building it in this ticket.
- Done when: the Outcome holds the design and the ordering check result.

## Constraints
None.

## Acceptance criteria
1. The Outcome holds the output format, the functions reused, and the `order.py` ordering result with the command that showed it.
