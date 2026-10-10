---
id: T-0425
title: "redck keys the red checkpoint to the criterion text, so steps.py widen does not invalidate it"
type: bug             # feature | bug | chore | spike | idea
status: ready
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `steps.py widen` that only adds scope paths no longer invalidates the red checkpoint, because the checkpoint is keyed to the criterion text and span it recorded, not to the whole handoff hash.

## Intent
- Do: in scripts/redck.py the `control` entries carry `handoff_sha256` and `verify` matches on it (about lines 173 and 202). Key each control to a hash of its own criterion line and span (`sha256(criterion + span)`), keep `handoff_sha256` in the entry for provenance, and match on the criterion hash. A widen that rewrites other lines of the handoff then leaves earlier controls valid; a changed criterion or span still invalidates only that control. `dispatch.py record` must stop printing the stale-input red-checkpoint deviation for a widen-only change.
- Non-goals: changing what a red criterion is; model or effort changes.
- Done when:
  - Selftest cases, each observed failing first: record, then `widen` adds a path to the scope span, then `redck verify` still finds every control; editing one criterion invalidates only that control; an old-format entry (handoff hash only) still verifies as before.
  - redck.py selftest, steps.py selftest, dispatch.py selftest, check.py and tickets.py check pass.

## Context
Maison, 2026-10-10: every step verifier reported a red-checkpoint process deviation after a widen (8 of 8 in the T-0378 wave), and rebuilt a pre-edit worktree to supply its own control. Evidence: maison .sdlc/tickets/0378-integration-wave-3/step-1/process-deviations.md. Also agent-ui (2026-10-09 12h retro, row 5) and ultimate-tokens. Related: T-0395, T-0420.

## Constraints
No em or en dashes. No push or publish. Do not remove any worktree or branch outside the role's own tmp prefix.
