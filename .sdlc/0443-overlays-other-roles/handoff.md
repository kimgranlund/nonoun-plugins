---
id: T-0443
title: "Extend overlays to the other roles and levels, gated on the A/B"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0458]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Overlays exist for the other roles and levels where the A/B result supports them.

## Intent
- Do: only if T-0442's verdict is keep or extend: extend `overlays/builder.md` to L2 and L4 as the data supports, and add `overlays/verifier.md` (L3), `overlays/planner.md` (L3), `overlays/solo.md` (L1 and L3, additive to the per-level Stop rules and Verification text that `check.py` items 18, 21 and 25 pin in `agents/solo.md`), and the single-row roles, per the architect's build-split paragraph.
- Non-goals: a model or effort change; any role the A/B did not support.
- Done when: each added overlay passes the generator refusals and `check.sh`; generated files for rows without an overlay stay byte-identical.

## Context
Design: `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md` (build split). Gated on T-0458's retest verdict (T-0442's first A/B said drop on a rule that could not bite; the maintainer chose to keep the overlays and retest). If T-0458 says drop, close this ticket as dropped.

## Constraints
Hard invariants never vary by tier. No hand edits to generated files.

## Gate check
gate: not met: T-0458 `Verdict: drop` (docs/reports/2026-10-12-builder-overlay-retest.md); close as dropped per Context. No roles run (2026-10-12, unattended /chain).
