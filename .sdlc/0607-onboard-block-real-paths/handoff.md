---
id: T-0607
title: "Onboard root block states lane root, ticket root and gitignore rules that are false for the repo"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The root `AGENTS.md` managed block that `onboard.py setup` writes states only facts true for the repo: the lane root from `wtroot.py root`, the ticket root from `.sdlc/config` (`ticket_root:`, layout), and the mailbox `.gitignore` line as advice, not as a rule.

## Context
Reported by the gen-ui-kit conductor 2026-10-15 after `onboard.py setup` on 0.24.0 (reverted). gen-ui-kit is a bare clone with lanes at `<bare parent>/lanes/`, tickets in `docs/tickets` (`ticket_root:`), its own doc routing and AGENTS.md size gates, and an owner ruling that `.gitignore` stays as is. The block said "lanes live in ../<repo>.worktrees/" (false for a bare clone), ".sdlc/ holds SDLC Lite tickets" (false with `ticket_root: docs/tickets`), and ".sdlc/messages/ keep it in .gitignore". T-0576 already made the block read the topics layout. Extend the same approach.

## Intent
- Do: render the lane-root, ticket-root and mailbox lines from `wtroot.root()` and the `.sdlc/config` values, the same functions the scripts use.
- Non-goals: when setup runs (the sibling ticket).
- Done when: the criteria pass.

## Constraints
Default-layout repos get byte-identical output.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exits 0. Its new cases cover:
   - a bare-clone fixture, whose block names `<bare parent>/lanes`;
   - a `ticket_root: docs/tickets` fixture, whose block names `docs/tickets`.

   Both cases failed before the change.
2. `git diff --check` exits 0.
