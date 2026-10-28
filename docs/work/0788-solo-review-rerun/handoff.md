---
id: T-0788
title: "advance on a solo reruns the pre-verify review after a verifier fail"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After a ticket verifier fails and the solo reports its fix, `dispatch.py advance` on the solo runs the `pre_verify_role` review again only when the fix touches `pre_verify_paths` since the last passing review.

## Repro
1. A project with `pre_verify_role:` and `pre_verify_paths:` in `.sdlc/config`; an L2 solo whose diff touches those paths.
2. advance: review passes, verifier fails; the solo fixes a file outside `pre_verify_paths`; advance the solo's dispatch again.

## Expected
The ticket verifier is prepared directly; the earlier passing review still covers the reviewed paths.

## Actual
T-0732 Outcome, Limitation: "advancing a solo always runs the review again, including after a verifier fail. That's because a solo's report has no position in the record order (`order.py`)".

## Context
T-0732 (`advance_solo` in plugins/sdlc-lite/scripts/dispatch.py); verifier note in its records dir, verifier-L2.md `## Notes`. The step path already decides from recorded results. Cost: one extra review run per solo retry.

## Acceptance criteria
1. A `dispatch.py` selftest case: review pass, verifier fail, a fix outside `pre_verify_paths`, then advance prepares the verifier, not the review; a fix inside the paths still prepares the review. With the change reverted the first case fails (state the FAIL line).
2. The dispatch selftest through gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Constraints
The failing test lands before or with the fix, never after.
