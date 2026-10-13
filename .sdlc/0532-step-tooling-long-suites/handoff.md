---
id: T-0532
title: "Step tooling and long suites (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Step tooling and long suites, closing maison T-0546 observations 10, 11, 20.

## Intent
- **Files:** `plugins/sdlc-lite/scripts/steps.py` (`split` around lines 1823-1864, `swap` around line 3277), `plugins/sdlc-lite/agents/verifier.md` (rule 5), and the generated agent definitions (regenerated, never edited by hand).
- **Behavior:**
  - `split --supersede` renames a step dir that holds role output to the next free `step-<n>.superseded-<k>`, then splits.
  - `swap` accepts a solo task folder, using the solo result in place of the builder result.
  - The verifier rule says to shard a suite that cannot finish within the 600000 ms foreground cap.
- **Done-when:** `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with these new cases:
  - `split --supersede` on a `step-2` holding `builder-L2.md` moves it to `step-2.superseded-1` and writes a new `step-2`. Without the flag it still refuses and writes nothing (negative control).
  - `swap` on a solo dir with `solo-L2.md` and a plan-defect verifier fail applies the swap.

  Also, `grep -n shard plugins/sdlc-lite/agents/verifier.md` prints a line and `bash plugins/sdlc-lite/scripts/check.sh` passes, which includes generated-agent parity.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group F; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.
