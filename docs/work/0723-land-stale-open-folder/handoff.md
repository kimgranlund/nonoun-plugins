---
id: T-0723
title: "land drops a lane's stale open folder of a ticket closed on integration"
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
Landing a lane that still carries the open folder of a ticket already closed on the target (renamed to `.NNNN-*`) does not fail with `duplicate id`: land drops the stale open copy.

## Intent
- Do: In `fanout.py land` (and the merge into the lane, if main is merged there), remove a lane's open `NNNN-*` folder when the target holds the closed `.NNNN-*` folder of the same id, and report it.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #59 (quoted):

> **Repro**: open lane A; land and close ticket T on integration (folder renamed to `.NNNN-...`); land lane A (or merge main into it, which re-adds the open folder from main).
>
> **Expected**: land treats the lane's open copy of a closed ticket as stale and drops it, or the close propagates.
>
> **Actual**: `merge failed: 0062-ui-context-typography-density: duplicate id T-0062, also used by .0062-ui-context-typography-density`. Every older lane needed a manual `git rm -r docs/tickets/<NNNN>-*` before landing.
>
> **Evidence**: `fanout/logs/land.jsonl` (T-0071 x2); same cleanup done by hand for T-0039/T-0073 in four more lanes.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
