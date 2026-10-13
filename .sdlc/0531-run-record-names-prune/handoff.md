---
id: T-0531
title: "Run records: retry names, filer prune, empty solo (maison T-0546)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Run records: retry names, filer prune, empty solo, closing maison T-0546 observations 8, 9, 28.

## Intent
- **Files:** `plugins/sdlc-lite/scripts/dispatch.py` (`next_stem` and `agent_name` around lines 287 and 803; `queue_prune` around line 1054; prune docs at lines 109-113), `plugins/sdlc-lite/scripts/solo_run.py` (around lines 609-630).
- **Behavior:**
  - The attempt counter also counts attempt records with no result, so a retry is named `-2` the same way the host names it.
  - A filer is queued for prune even when it has follow-ups, because its follow-ups are its output and `close` consumes them.
  - A solo whose result text is empty, or that leaves no result file, is a failed run.
  - A solo refuses a handoff that is still the unfilled template.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` and `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exit 0 with these new cases:
  - Two prepares on a dir whose first attempt left no result file print `...-L4` and then `...-L4-2`. HEAD's script prints the same name twice (negative control).
  - A filer record whose result has a non-empty `## Follow-ups` prints `prune: <name>`.
  - A result event with empty text exits 1 and prints `FAILED`.
  - A solo on a template-equal handoff refuses.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group E; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.
