---
id: T-0719
title: "dispatch.py record --no-result closes a stalled solo as failed"
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
`dispatch.py record --no-result <solo dispatch>` closes the solo attempt as failed (exit 1) and clears its live marker, as for other roles (T-0412).

## Intent
- Do: In `dispatch.py` (`solo_report_file` path, about line 2085), honour `no_result` before requiring a report or transcript.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #54 (quoted):

> ## What happened
> `dispatch.py record --no-result <solo dispatch.json>` does not close a stalled solo's attempt. The solo path goes through `solo_report_file` (scripts/dispatch.py, around line 2085). With no report and no transcript final message, it returns 2 and prints:
>
> ```
> dispatch.py: no solo report at <path> and no transcript final message to take; the row and live marker are unchanged: record again once the solo writes it, or pass --transcript
> ```
>
> So `--no-result` is never honoured for solos. A solo that stalled for good, silent for 90 minutes, could not be closed as failed; its live marker stayed, and I re-dispatched over it.
>
> ## Expected
> `--no-result` closes a solo attempt as failed (exit 1, `failed`), as it does for the other roles (T-0412), and clears the live marker.
>
> ## Repro
> 1. Start a solo with `solo_run.py run ...` and stop the agent before it writes a report.
> 2. Run `dispatch.py record --no-result <dispatch.json>`; the attempt stays as it was.
>
> Seen on 0.30.0, and the code path is unchanged in 0.33.0.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`dispatch.py record --no-result <solo dispatch>` with no report file and no transcript final message now exits 1, prints `solo failed; live marker cleared`, and clears the live marker. Without `--no-result` it still exits 2 and changes nothing; its message now also names `--no-result`. `solo_report_file` takes `no_result` and returns 1; the `rec()` caller runs `solo_run.complete` then returns 1.

- New selftest case `T-0719 record --no-result on a solo dispatch with no report exits 1, says failed, and clears the live marker` (the `solo_rec` helper gained a `git=True` option so the marker lives in a repo's git dir).
- Negative control (call site reverted to `solo_report_file(sd, args.transcript)`): `FAIL: T-0719 record --no-result on a solo dispatch with no report exits 1, says failed, and clears the live marker`, `dispatch selftest: FAIL`; restored: `dispatch selftest: PASS`.
- `gate_lock.py run ... dispatch.py selftest` exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check a41157c6` exit 0.
