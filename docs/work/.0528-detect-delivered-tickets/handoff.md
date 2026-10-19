---
id: T-0528
title: "Detect delivered and superseded open tickets (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0527]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Detect delivered and superseded open tickets, closing maison T-0546 observations 21, 23, 24, 25, 26.

## Intent
- **Files:** `plugins/sdlc-lite/scripts/tickets.py` (field validation, `cmd_check`, roadmap row), `plugins/sdlc-lite/skills/ticket/SKILL.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (field list).
- **Behavior:**
  - `check` lists every open ticket whose id starts a commit subject (`T-NNNN:`) on the default branch.
  - A new optional field `successor: <T-NNNN | <repo>:T-NNNN>` covers four cases with one record: superseded, delivered under another ticket, verified by an integration ticket, and fixed in another repository.
  - When a local successor is done, `check` prints the ready-to-run `close <folder> --reason "..."` line. A cross-repository successor is shown but not resolved.
- **Done-when:** `tickets.py selftest` exits 0 with these new cases:
  - In a git fixture, a commit `T-0002: x` on main makes `check` list T-0002. The same commit on an unmerged branch lists nothing (negative control).
  - `successor: T-0003` with T-0003 done prints the close line. With T-0003 open it prints nothing.
  - `successor: maison:T-0158` is accepted and `successor: banana` is rejected.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group B; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.

## Closed

2026-10-13: solo L2 built, verifier L2 pass with observed negative controls, merged from fanout/wave67-b
