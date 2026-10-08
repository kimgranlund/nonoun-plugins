---
id: T-0387
title: "The architect skips decompose and the coverage check for a Markdown-only design handoff"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The architect skips decompose and the coverage checker when the handoff is a Markdown-only design with no code to locate.

## Intent
- Do: Add a one-line rule to agents/architect.md and the architect skill: for a handoff whose deliverable is a Markdown design document only, produce the design and skip the two-plane decomposition and scripts/coverage_check.py unless the handoff asks for a breakdown. Regenerate agents.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A check.py phrase guard with its removal control (observed failing first); generate --check passes.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
The maison conductor noted its architect ran decomposition and a coverage checker on a Markdown-only design handoff (T-0300): ceremony with no value. Not an eval item; the model row is unchanged. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.
