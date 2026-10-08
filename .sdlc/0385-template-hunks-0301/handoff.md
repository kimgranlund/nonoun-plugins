---
id: T-0385
title: "Rebase the Codex lean-template hunks onto 0.22.x and answer per hunk"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The four template and rule edits proposed by Codex's RCA review are assessed against 0.22.x and each hunk is accepted, adapted or declined with a reason.

## Intent
- Do: Read .sdlc/tickets/0301-lean-template-bootstrap-design/proposed-diff.md and review-notes.md in the maison repo (text against 0.21.x; four source edits: the handoff-format template, planner rules 1 and 14 with whole-suite timing, and fanout.py's rerun-all solo briefs, plus a standing-orders note that stays maison's). Rebase each hunk onto current main, apply the accepted ones, and reply to the maison conductor per hunk with accept, adapt or decline and why. The review's eight review cases become selftest or check cases where they test plugin behavior; the install-receipt integrity check and T-0299 preflight are proposals, not built, so do not claim them. Check that the edits do not conflict with the new parser and lint rules.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A per-hunk disposition list committed in docs/reports/ and sent to the maison conductor.
  - Accepted hunks have selftest or check coverage (observed failing first where behavior changes); declined hunks name the reason.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Codex RCA review for maison T-0301, 2026-10-08. Observed cause: one-line amendments repeated npm ci, generated fanout briefs ask for all named checks after any fix, and the planner treats every one-step plan as gates green. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.
