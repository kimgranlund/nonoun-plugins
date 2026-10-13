---
id: T-0529
title: "Writing rules for work records, and a placeholder gate at close (maison T-0546)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0528]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Writing rules for work records, and a placeholder gate at close, closing maison T-0546 observations 17, 18, 29.

## Intent
- **Files:** a new `plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (link), the `ROUTER_TEMPLATE` link in `tickets.py`, and `cmd_close` reusing `placeholder_problems` (around line 1405).
- **Behavior:**
  - The new reference holds controlled language and the patterns maison listed: checklist, dependency, decision, criterion, status line, open question, lane.
  - It adds a rule that `notes.md` never states a ticket's status and cites the ticket instead.
  - `close` refuses a handoff that still holds template placeholder text, unless `--reason` is given.
- **Done-when:**
  - `test -f plugins/sdlc-lite/skills/handoff-format/references/writing-rules.md`
  - `grep -n writing-rules.md plugins/sdlc-lite/skills/handoff-format/SKILL.md` prints a line.
  - `tickets.py selftest` exits 0 with a new case: `close` on a fixture holding the bug template's Repro prompt line exits nonzero and names the line. The same fixture filled in closes (negative control).
  - `python3 scripts/check-packaging.py` passes.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group G; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.
