---
id: T-0725
title: "lanes.py open takes the merge lock before committing to integration"
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
`lanes.py open --into <integration>` waits for the same merge lock `fanout.py land` holds, so it never commits to integration while a land's gates or auto-reset run.

## Intent
- Do: Take `merge.lock` (as `fanout.py land` and `fanout.py queue` use it) around the integration commit in `lanes.py open`.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #65 (quoted):

> **Repro**: start `fanout.py land` (gates running on integration); concurrently run `lanes.py open` which commits the lane record to integration.
>
> **Expected**: lane open takes the same merge lock as land.
>
> **Actual**: the land's gate went red and its auto-reset failed: `error: git reset -q --hard 61db973... failed: fatal: Unable to create '.../.git/worktrees/integration/index.lock'`; a second land had stacked on top and integration had to be reset by hand.
>
> **Evidence**: `fanout/logs/land.jsonl` (T-0060); trace detector `integration-reset` (22 findings).
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `lanes.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `plugins/sdlc-lite/scripts/lanes.py`: new `integration_lock(top, tree)` returns `fanout.MergeLock` on `<tree parent>/merge.lock` for a fanout integration tree, else the default lanes dir's (`fanout.resolve_lanes_dir`), a null context where land refuses that dir. `open` writes and commits the lane record in an integration tree under it; a record in main takes no lock. Module docstring updated.
- New selftest case `open into mergelock`: holds `<worktree root>/fanout/merge.lock` as land does, runs `lanes.py open --into wave/1`, wants it still waiting after 6 s with `wave/1` unmoved, then the record commit once released.
- Negative control (fix reverted, case kept): `FAIL: open into mergelock: open finished while merge.lock was held: 0: ...` and `FAIL: open into mergelock: wave/1 moved while merge.lock was held`.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check c491e6f8` exit 0.

## Outcome

2026-10-22 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: c491e6f8e22d
- Changed: see commits
- Commits: b2e21fc T-0725: lanes.py open takes the merge lock before committing to integration
- Check: 1 A lanes.py selftest case reproduces the repro and fails with the change reverted: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py sel...: pass
- Check: 3 `check.py` exits 0, `check-packaging.py` passes, `git diff --check <base>` exits 0: pass
- Follow-up: decide: Deadlock trace, no self-wait: the setup of fanout.py prep and run... -> notes.md
- Follow-up: decide: Lock ordering: lanes.lock is released end of its with at... -> notes.md
- Follow-up: decide: Stale lock: flock is released by the kernel on process death -> notes.md
- Follow-up: decide: lanes.py:62-64 module docstring: the added line runs past the... -> notes.md
- Follow-up: decide: integration_lock waits without a timeout or a message, so an open... -> notes.md
