---
id: T-0720
title: "fanout.py land finds a verifier result recorded by prepare --tree"
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
`fanout.py land` finds the passing verifier result that `dispatch.py prepare --tree <lane>` recorded, wherever prepare wrote it, or prepare writes it where land reads.

## Intent
- Do: Make `prepare --tree` and `land` agree on the records dir for a lane ticket (pick one location and use it in both, in `dispatch.py` and `fanout.py`).
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #55 (quoted):

> **Repro**: `dispatch.py prepare --tree <lane worktree> verifier L3 <primary handoff>` → result lands in `<primary>/.sdlc/runtime/tasks/<t>/verifier-L3.md`; then `fanout.py land <lane branch> --lane solo ...`.
>
> **Expected**: land finds the passing verifier result the dispatch recorded (or prepare writes it where land reads).
>
> **Actual**: `no verifier result (the lane worktree's records dir holds none; a branch with no worktree commits it into the ticket folder with git add -f, then lands again)`. Workaround: copy the result into the lane's records dir.
>
> **Evidence**: `fanout/logs/land.jsonl`: 2 refusals (T-0036).
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
- Fix: `fanout.py land` now reads, as the last fallback in `branch_verdict` (after the integration copy of the lane records and the results committed on the branch), the main checkout's records dir (`order.records_dir` of the ticket folder there), which is where `dispatch.py prepare --tree <lane>` records a verifier of a primary-checkout handoff. `prepare` is unchanged. The `SDLC_SELFTEST_NO_RECORDS_COPY` knob now also skips land's carry into main, so the existing records-copy negative control still bites.
- New selftest case `case 23 land prepare --tree (T-0720)`: a pass verifier in the primary checkout's records dir for a lane ticket whose worktree holds none; land merges it.
- Negative control (case in place, fix absent): `- case 23 land prepare --tree (T-0720): a verifier result in the primary checkout records dir is read, got rc=1 out="... | agent-w2 | T-0002 | no verifier result (the lane worktree's records dir holds none; ...) | f25930f |"`.
- Checks: `gate_lock.py run ... fanout.py selftest` exit 0; `check.py` exit 0; `scripts/check-packaging.py` PASS; `git diff --check 83a3a4e6` exit 0.
