---
id: T-0775
title: "land merges a lane runs.jsonl into the primary one instead of overwriting it"
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
Landing a lane never loses a `runs.jsonl` row: rows from the lane copy are merged into the primary copy (dedup by attempt id), never overwrite it.

## Intent
- Do: reproduce first (a selftest case built from the observation), then the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: other rehearsal findings.
- Done when: the criteria pass.

## Context
Observed: landing T-0003 overwrote main's `.sdlc/runtime/tasks/add-div/runs.jsonl` with the lane's copy; the solo L2 row (`"ts":"2026-10-25T00:47:08Z","role":"solo","level":"L2"`) was lost and only the verifier row remained. The verifier's records were in the lane worktree (owner tree, T-0750), the solo row in main.

Evidence: the second 0.36 release rehearsal 2026-10-25 (sdlc-lite b7c64749) in /Users/kimgranlund/Projects/nonoun/live036b (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036b-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036b-run/log.md.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Fix: `lanes.merge_runs` appends a source runs.jsonl's missing rows to the destination (dedup by `attempt_id`, the destination row wins; else by whole line). `lanes.copy_newer` (used by `carry_records`, the land carry into main, the close mirror in fanout.py, and `lanes.py close`) merges runs.jsonl instead of newest-wins; `fanout.copy_lane_records` (lane into integration) merges through `lanes.copy_record`. Other record files keep newest-wins.
- Selftest: fanout.py case 23 `land runs.jsonl merge (T-0775)` builds the rehearsal shape (solo row only in main and older, verifier row in the lane's newer copy, plus the same solo attempt_id in the lane). The T-0566 assertions in fanout.py case 23 and lanes.py `case_carry` now expect the merge.
- Negative control (fix reverted, tests kept): `fanout selftest: FAIL` with `case 23 land runs.jsonl merge (T-0775): main keeps its solo row once and gains the lane verifier row, got rc=0 rows=[{'role': 'verifier', ...}, {... 'attempt_id': 'solo-1', 'cost_usd': 1.0}]`; lanes.py `FAIL: carry: carry: a main runs.jsonl newer than the lane copy was overwritten or missed the lane row (T-0775)`.
- Checks: fanout.py selftest through gate_lock exit 0, lanes.py selftest exit 0, check.py exit 0, check-packaging.py PASS, `git diff --check 73aefc97` exit 0.
