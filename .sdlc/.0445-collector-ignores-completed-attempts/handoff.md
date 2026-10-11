---
id: T-0445
title: "Collector and recover: a completed attempt is never counted or marked interrupted"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
K-002 lost minutes count only attempts that were really interrupted: an attempt whose result file already holds a verdict is never counted by the collector and never marked `interrupted` by `dispatch.py recover`.

## Intent
- Do: (1) `fleet_collect.py`: skip an attempt for `runs.interrupted` when a result file for that attempt holds a verdict (`## Verdict` with a first value from `results.py`); (2) `dispatch.py recover`: leave such an attempt alone (its status is repaired to `completed` or left as is, never `interrupted`); (3) a selftest case for each with a negative control (a truly orphaned attempt with no result still counts and is still marked interrupted).
- Non-goals: rewriting history in the committed attempt files of T-0431 and T-0432 beyond one repair commit if the collector fix alone does not zero them; the `--open` scope already shipped in 0.22.4.
- Done when: both selftests pass with an observed red before the fix; `check.sh` exits 0; `fleet_collect.py collect . --since 2026-10-11` reports `runs.interrupted.lost_min_total` of 0 for this repo (the two phantom attempts).
- outcome metric: fleet_collect.py collect . --since 2026-10-11 (runs.interrupted.lost_min_total), before: 1364.7

## Context
Evidence: `docs/reports/2026-10-11-fleet-retro-12.md` row 1; the files `.sdlc/.0431-plan-doc-parser-and-check/verifier-L3.attempt.json` and `.sdlc/.0432-plan-done-script/verifier-L3.attempt.json` hold `status: interrupted` beside a passing `verifier-L3.md`; commit d7bea393 committed them. Code: `plugins/sdlc-lite/scripts/fleet_collect.py` (interrupted and lost_min), `dispatch.py recover`.

## Constraints
No model or effort change. Preserve the K-002 definition in `docs/kpi/002-*.md`; update it only if the definition text is now wrong.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest` exits 0 and prints `ok: interrupted: an attempt whose result file holds a verdict is not counted` and `ok: negative control: an interrupted attempt whose result holds no verdict is still counted`.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and prints `ok: recover leaves a dead-parent attempt whose result holds a verdict alone (T-0445)` and `ok: recover marks it interrupted with run_lifecycle.py text` (the negative control).
3. `python3 plugins/sdlc-lite/scripts/results.py selftest` exits 0.
4. `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 2026-10-11` reports `runs.interrupted.lost_min_total` 0.
5. `bash plugins/sdlc-lite/scripts/check.sh` exits 0.

## Closed

2026-10-11: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
