---
id: T-0718
title: "dispatch.py advance reverifies at the failing verifier level"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After a verifier fail and a solo rebuild, `dispatch.py advance <solo dispatch>` prepares the reverify at the level of the verifier that failed (for example L3), not the solo's default.

## Intent
- Do: In `dispatch.py` `advance`, take the reverify level from the latest failing verifier attempt for the ticket when one exists.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #52 (quoted):

> **Repro**: ticket verified by verifier L3 → fail; solo rebuilds; `dispatch.py advance <solo dispatch>`.
>
> **Expected**: the reverify keeps the failing verifier's level (L3) unless the conductor changes it; identity-sensitive work was routed to L3 on purpose.
>
> **Actual**: advance prepared `verifier-L2` automatically; the conductor had to `record --no-result` it and prepare L3 by hand.
>
> **Evidence**: `.sdlc/runtime/tasks/0070-progress-track-and-dark-scrim-contrast/verifier-L2.dispatch.json` (closed no-result) next to `verifier-L3*.dispatch.json`.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
