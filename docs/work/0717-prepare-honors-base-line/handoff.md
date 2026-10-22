---
id: T-0717
title: "dispatch.py prepare uses the handoff base: line for Base sha"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `base: <sha>` line in the ticket or step handoff (and a written `<artifacts>/base-sha`) sets the brief's Base sha, as prepare's own hint promises, including in a lane whose HEAD moved past its start after a main merge.

## Intent
- Do: Find why `dispatch.py` (the base resolution about line 499 and 3146, the "nothing recorded for this step" hint about line 560) ignores the line in the reported case (`prepare --tree <lane> verifier L3 <handoff>` after a main merge); fix it so the named base wins.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #49 (quoted):

> **Repro**
> 1. Open a fanout lane, then merge main into it (lane HEAD moves past the lane start).
> 2. A worker builds on the new HEAD. Add `base: <new HEAD>` to the ticket handoff (as prepare's own hint says) and/or write `<artifacts>/base-sha`.
> 3. `dispatch.py prepare --tree <lane> verifier L3 <handoff>`.
>
> **Expected**: the brief's Base sha is the named base (the commit the build started from).
>
> **Actual**: prepare prints `nothing recorded for this step: Base sha is the lane start d767131f273d, not its HEAD 7a68a2e6422e; name another with a line 'base: <sha>'` and still emits `Base sha: d767131f...` after the `base:` line and the base-sha file were added. All five verifier dispatches of the ticket carried d767131f, so verifiers diffed the main merge as if it were build scope.
>
> **Evidence**: `.sdlc/runtime/tasks/0039-ts-semantic-systems/verifier-L3{,-2,-3,-4,-5}.dispatch.json` → `base_sha` d767131f on every try.
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
