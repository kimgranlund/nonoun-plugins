---
id: T-0530
title: "Lane record on the ticket (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0541, T-0542]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Lane record on the ticket, closing maison T-0546 observations 15, 30, and 31.

## Intent
- **Files:**
  - `plugins/sdlc-lite/scripts/lanes.py` (`open_lane`, `close_lane`, `list_lanes` around line 978)
  - `plugins/sdlc-lite/scripts/tickets.py` (a `branch:` field, shown on the roadmap and router active line; an "Open a lane" procedure)
  - `plugins/sdlc-lite/scripts/board.py`
  - `plugins/sdlc-lite/skills/handoff-format/run-operations.md`
- **Behavior:**
  - `lanes.py open --ticket` writes `branch:` and `close` removes it.
  - `list --all` matches a manual worktree to its ticket by `branch:` and shows the ticket's newest verifier verdict, so verified, unmerged work is visible.
  - `lanes.py open` already applies the claim rule, which covers "dispatch on an unclaimed ticket" once lanes open through it.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/lanes.py selftest` and `tickets.py selftest` exit 0 with these new cases:
  - A manual worktree on `fix-0520`, plus a ticket with `branch: fix-0520` and a passing `verifier-L2.md`, gives a `list --all --json` row with ticket `T-0520` and verdict `pass`. Without the `branch:` line the row has no ticket (negative control).
  - `open --kind solo --ticket T-0001` writes `branch: lane/...` and `close` removes it.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group D; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.
