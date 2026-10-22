---
id: T-0723
title: "land drops a lane's stale open folder of a ticket closed on integration"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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

## Outcome
- Root cause: a lane tree holding the open `NNNN-*` copy beside the target's closed `.NNNN-*` (re-added by merging main into the lane) merged cleanly with both folders, and `tickets.py roadmap` inside `merge_generated` refused the duplicate id.
- Fix: `fanout.py` `drop_stale_open` runs in `merge_generated` after the merge and before the roadmap, `git rm`s each open folder the index holds beside a closed folder of the same number, and `merge_gate_close` reports `dropped stale open folder <path>: its ticket is closed on <integration>`. Every `merge_generated` caller (land, run, settle, sync, lanes forward) gets it.
- Repro first in a throwaway repo: `merge failed: 0002-t2: duplicate id T-0002, also used by .0002-t2`; with the fix: `merged`, `.sdlc/0002-t2` dropped.
- Selftest case `case 23 stale open folder (T-0723)`. Negative control (the drop call replaced by `[]`): `fanout selftest: FAIL` with `- case 23 stale open folder (T-0723): a lane carrying the open copy of a ticket closed on the integration branch lands with it dropped and reported, got rc2=0 rc=1 ...`.
- Checks: `gate_lock.py run ... fanout.py selftest` exit 0 (PASS); `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 9c803b49` exit 0.

## Outcome

2026-10-22 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 9c803b4950e4
- Changed: see commits
- Commits: 57658b4 T-0723: land drops a lane's stale open folder of a ticket closed on integration
- Check: 1 fanout.py selftest case reproduces the repro and fails with the change reverted: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py se...: pass
- Check: 3 check.py, check-packaging.py, git diff --check: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1652 decide: data-loss probe -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1652 decide: the drop is... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1660 fix-now: the glob... -> notes.md
- Follow-up: decide: The same-work-root requirement holds -> notes.md
