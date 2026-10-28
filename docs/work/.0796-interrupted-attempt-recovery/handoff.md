---
id: T-0796
title: "interrupted and stale-running attempts go unnoticed until a person looks"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
claimed_by: sdlc-lite-author 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
An interrupted or stale-running attempt is flagged without a person looking: the fleet stall rule fires on minutes lost, and `dispatch.py status` marks a running attempt whose ticket is closed as orphaned.

## Repro
1. In a repo, leave a verifier attempt interrupted (its process gone, no record) for over 2 hours, with fewer than 3 interrupted attempts.
2. `fleet_collect.py collect <repo>` then `fleet_detect.py detect`: no finding.
3. Close the attempt's ticket, then `dispatch.py status <task dir>`: the attempt still reads `running ... over-budget`.

## Expected
Step 2 prints a stall finding on `runs.interrupted.lost_min_total`; step 3 reports the attempt orphaned.

## Actual
Fleet retro 2026-10-28 (`docs/reports/2026-10-28-fleet-retro.md` rows 2 and 3, verified 10 of 10 against the rubric): ultimate-tokens-color-science lost 1345.1 min to 2 interrupted attempts (0062 verifier-L3-2 lost 1335.0 min) with no detect finding, because 2 is under the stall threshold of 3; ui-kit-neue lost 674.7 min to 4. MacBook report row E2: `verifier-L2 running verifier-L2 parent_pid=1836 over-budget 3d (budget 25m)` on 0118 while T-0118 is done.

## Context
`plugins/sdlc-lite/scripts/fleet_detect.py` (rule `stall_attempts`), `dispatch.py` status and recover. Evidence: `docs/reports/2026-10-28-sdlc-retro-kims-macbook-pro.md` rows 1, E1, E2; verify result `.sdlc/runtime/tasks/fleet-retro-2026-10-28/verify/verifier-L1-2.md`.
outcome metric: `runs.interrupted.lost_min_total` per repo, before: 1345.1 (ultimate-tokens-color-science), 674.7 (ui-kit-neue).

## Acceptance criteria
1. A `fleet_detect.py` selftest case: a fingerprint with 2 interrupted attempts and lost_min_total over 120 fires `stall_attempts`; with the change reverted it does not (state the FAIL line).
2. A `dispatch.py` selftest case: a running attempt whose ticket is done reads orphaned in `status`; reverted, it reads running.
3. Both selftests through gate_lock exit 0, `check.py` exits 0.

## Constraints
The failing tests land before or with the fix, never after. If both parts need more than 3 steps, split into two tickets.

## Outcome
- `fleet_detect.py`: new threshold `stall_lost_min` (120); `stall_attempts` also fires on `runs.interrupted.lost_min_total` over it, as its own finding. The healthy fixture sits at 120.0.
- `dispatch.py`: `attempt_state_at` reads a running attempt orphaned when its task folder's ticket is done or dropped; `status`, `recover` and the over-budget lines use it, so recover marks such an attempt interrupted and it no longer reads `over-budget`.
- Red before the fix (cases added first):
  - `FAIL: positive: stall_attempts (runs.interrupted.lost_min_total) fires once and nothing else does` (plus its evidence and resolve lines)
  - `FAIL: closed ticket: status reads a running attempt orphaned once its ticket is done, with no over-budget token`
  - `FAIL: closed ticket: recover would mark it interrupted`
- Negative controls green before and after: `negative: stall_attempts: 120 minutes lost yields no finding`, `negative control: raising stall_lost_min in the table silences stall_attempts`, `negative control: the same attempt reads running while its ticket is open`.
- Checks after the fix: `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest` exit 0; the same for `dispatch.py selftest` exit 0 (PASS); `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `git diff --check` clean.

## Outcome

2026-10-28 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: f11d3f72cf7c
- Changed: see commits
- Commits: d7c4598 T-0796: flag interrupted and stale-running attempts
- Check: 1 fleet_detect selftest: 2 interrupted attempts with lost_min_total over 120 fires stall_attempts, ...: pass
- Check: 2 dispatch selftest: a running attempt whose ticket is done reads orphaned in status, and running w...: pass
- Check: 3 both selftests through gate_lock exit 0, check.py exits 0: pass
- Follow-up: decide: Conductor check: attempt_state_at dispatch.py:829-836 only adds... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:1099 and :1167: wait and the... -> notes.md
