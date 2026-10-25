---
id: T-0785
title: "steps.py next from main sees a solo report that is still only in the lane"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py next <task dir>` run from the main checkout before land reads a solo ticket's report and verifier result from its lane twin (the host worktree), as `dispatch.py status` already does, instead of printing `solo L<n>`.

## Intent
- Do: reproduce first with a selftest case built from the observation, then the smallest fix in `plugins/sdlc-lite/scripts/steps.py` and its docs.
- Non-goals: other findings.
- Done when: the criteria pass.

## Context
Observed: from main before land, `dispatch.py status .sdlc/add-div` printed `verifier-L2 completed`, but `steps.py next .sdlc/add-div` printed `solo L2` / `reason: solo ticket L2 (no builder, planner or solo report); run the solo at L2`; after land it printed `close`. T-0776 noted the cause: a lane records dir holding only a solo report and its dispatch record (and here a verifier result) is not picked up as the records owner by `records_of`/`order._legacy`. Make `next` find the owner twin through the same owner-tree path `dispatch.py status` uses (T-0755, T-0763) when the twin holds a solo report or dispatch record.

Evidence: the fourth 0.36 rehearsal 2026-10-25 (sdlc-lite 7d8acebe) in /Users/kimgranlund/Projects/nonoun/live036d (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036d-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036d-run/log.md, lanes dir /Users/kimgranlund/Projects/nonoun/live036d.worktrees.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Cause: before land `records_of` reads the host lane twin (its `verifier-L2.md` counts as records), but `dispatch.py record` wrote `T-0003-solo.dispatch.json` in main's records dir (rehearsal log.md:333, 335), so `solo_report` found no solo dispatch record and no `solo-L<n>.md` and `next` printed `solo L2`. The fixture follows that evidence; a twin that also holds the dispatch record already routed to `close` (the T-0776 lane case).
- Fix: `solo_report` in `plugins/sdlc-lite/scripts/steps.py` reads the solo dispatch record from the same place in the ticket's other checkouts (`tree_twins`, `wtroot.owner_trees`) when the twin holds none, and the report from the twin first. The `next` usage text names it (T-0785).
- Selftest: `next solo host lane (T-0785): ...` (a host lane, record `agent-t0785.lane.json` under `wtroot.lanes_root`, twin with report, verifier pass, attempt and verifier runs row; main with the dispatch record, report copy and solo row) passes.
- Negative control (the twin lookup reverted): steps selftest exit 1, `steps selftest: FAIL, these did not hold:` / `- next solo host lane (T-0785): from main before land, the host twin holds the solo report and verifier pass and main holds the solo dispatch record -> close`, the only failure.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exit 0; dispatch.py selftest (gate_lock) exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0 (PASS); `git diff --check 327b2bd0` exit 0.
