---
id: T-0727
title: "steps.py split reports missing dependencies as an environment error"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When a guard or red span fails because dependencies are missing in the tree (`ERR_MODULE_NOT_FOUND`, `Cannot find module`, `command not found`, no `node_modules`), `steps.py split` reports an environment error with an install hint and exit 2, not a `plan defect`.

## Intent
- Do: In `steps.py` split, classify those failure texts before emitting `plan defect`.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #51 (quoted):

> **Repro**: open a fresh lane worktree (no `node_modules`), run `steps.py split <task> --only 1 --only 2 --tree <lane>` on a plan whose guards run `npx vitest`/`node packages/...`.
>
> **Expected**: an environment error (dependencies missing in the tree) with a hint to install, not a plan verdict.
>
> **Actual**: `ERR_MODULE_NOT_FOUND ... plan defect: step 1 red guard: nice -n 10 npx vitest run ...; replan this step (/chain 3)`. Following the rule would burn a replan on a missing `npm ci`.
>
> **Evidence**: T-0068 split, 2026-10-22; the same split passed after `npm ci` in the lane.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
