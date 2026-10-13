---
id: T-0525
title: "Triage maison T-0546: 30 work-record gaps, one reply line each"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Question
For each of maison T-0546's 30 observations: is it already fixed, worth a new SDLC Lite ticket, or out of scope?

## Goal
A decision for each of the 30 observations in maison's T-0546: accepted as a new SDLC Lite ticket, already fixed in a released version, or declined with a reason.

## Intent
- Do: read `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/handoff.md` and `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md`, and the audit `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/ticket-completion-audit/claude/reconciliation.md` behind items 21 to 30. Check each observation against this repository's current main (released as 0.22.7; maison runs 0.22.6). Use `git log --oneline v0.22.6..v0.22.7` and the closed `.sdlc/.NNNN-*` handoffs to find existing fixes, and `.sdlc/roadmap.md` for open tickets that already cover one.
- Do: maison's own hand-written rules are the working reference for what they want: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md` (Writing, Lane worktrees, Operating hazards), `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/AGENTS.md`, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/writing-rules.md`.
- Do: group accepted items into the smallest set of new tickets that each fit one solo or lean lane (aim for 4 to 8), with a size L1 to L3 and the observation numbers each one covers. Decline an item that belongs to the project, the host, or is already a project rule that needs no plugin change; say which.
- Do: write two outputs in the artifacts dir: `author-reply.draft.md` with exactly one line per observation, `<n>. accepted as sdlc-lite <group-letter> | already fixed in <version> (<T-NNNN>) | declined: <reason>`, and the architect result listing each proposed ticket (letter, title, size, observations, the files it changes, and a runnable done-when).
- Non-goals: editing anything in ui-kit-maison; filing tickets (the conductor files them from your list); changing plugin code.
- Done when: the draft has 30 lines numbered 1 to 30, every `already fixed` cites a ticket id present in this repo, and every accepted item maps to exactly one proposed ticket.

## Context
Maison's request arrived 2026-10-13 by cross-session message; the user approved triage after 0.22.7. Maison stays on 0.22.6 until its T-0439 closes, so "already fixed in 0.22.7" still means they cannot use it yet; say so where it matters.

## Constraints
Read-only outside the artifacts dir. Writing rules for the reply: short lines, no em dashes.

## Closed

2026-10-13: triage done: 7 tickets filed (T-0526 to T-0532), reply written to maison T-0546 author-reply.md
