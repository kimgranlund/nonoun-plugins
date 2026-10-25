---
id: T-0776
title: "steps.py next works on a solo ticket task folder"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py next <task dir>` on a solo ticket (no planner, no builder step) reads the level from the ticket handoff and reports the solo/verifier state, from main and from the lane, instead of failing.

## Intent
- Do: reproduce first (a selftest case built from the observation), then the smallest fix in `plugins/sdlc-lite/scripts/steps.py` and its docs.
- Non-goals: other rehearsal findings.
- Done when: the criteria pass.

## Context
Observed: `steps next: no builder result and no .../runtime/tasks/add-div/handoff.md to read a level from` (rc=1), both from main and on the lane-redirected path; the handoff is `.sdlc/add-div/handoff.md`, not under runtime/tasks. T-0763 noted the same as out of scope.

Evidence: the second 0.36 release rehearsal 2026-10-25 (sdlc-lite b7c64749) in /Users/kimgranlund/Projects/nonoun/live036b (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036b-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036b-run/log.md.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`steps.py next` on a solo ticket's task dir (ticket handoff with front matter `size:`, no `level:` line, no planner or builder result) now routes by the solo result: no report -> `solo L<size>`, solo-L1 report -> `close`, solo-L2/L3 report -> `verify L<ticket verifier level>`, verifier pass -> `close`, fail -> `stop`, blocked report -> `stop`. The handoff is read through `step_handoff` from the dir given or its lane twin, the results through `records_of` (T-0755 owner tree). `handoff_level` and the step routes of T-0766 and T-0781 are unchanged. Docs: the `next` usage text in `steps.py` and `skills/chain/references/step-rules.md`.

Checks: `steps.py selftest` (through gate_lock) exit 0; `check.py` exit 0; `scripts/check-packaging.py` exit 0; `git diff --check f7d88cd3` exit 0.
Negative control (the two `next_action` lines reverted in a scratch copy): selftest FAIL, 10 cases, first `next solo (T-0776): a solo ticket of size L2 with no result -> solo L2`, last `next solo lane (T-0776): a verifier pass in the lane twin -> close`.
Not covered: a ticket handoff present only in the lane tree (no ticket id above the path in main, so no twin lookup).
