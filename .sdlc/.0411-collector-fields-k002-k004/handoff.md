---
id: T-0411
title: "Collector fields for K-002, K-003, K-004 and verifier minutes"
type: feature        # feature | bug | chore | spike | idea
status: done
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []
created: 2026-10-09
claimed_by: claude 2026-10-09
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Collector fields for K-002, K-003, K-004 and verifier minutes. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 1 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: feature, size L2, serves G-002. Spec: section "Measures" of `docs/specs/sdlc-lite/restart-and-blocked-run-plan.md`. Depends on: none.

In `plugins/sdlc-lite/scripts/fleet_collect.py` (`collect_runs`, `fleet_collect.py:320-414`, and `collect`, `704-720`), add these keys; none of today's keys changes:
- `runs.interrupted.attempts[].lost_min`: minutes from the attempt's `started_at` to the `started_at` of the next attempt record of the same role in the same handoff dir, else to its own `finished_at`; plus `runs.interrupted.lost_min_median` and `lost_min_total` (null and 0 with no interrupted attempt).
- `runs.orphaned`: `{count, attempts: [{attempt_id, role, level, started_at, path}]}` for attempt records with status `running`, backend claude (default), started in the window, whose `parent_pid` (else `owner_pid`) is dead now, using the same `kill(pid, 0)` test as `dispatch.pid_alive` (`dispatch.py:216-225`). Deduplicate by `attempt_id` across worktree copies, as `interrupted` does.
- `results.builder`: `{total, blocked}`: builder rows of `runs.jsonl` in the window, deduplicated as `runs` is; `blocked` counts those whose result file (the row's `file` beside its `runs.jsonl`) holds `## Status` whose next non-blank line's first word is `blocked`.
- `plan_defects`: `{late, early}`: `late` counts builder and verifier rows in the window whose result file holds a line starting `plan defect:` (after an optional list marker); `early` counts lines of `refusals.jsonl` files in any scanned `.sdlc` dir whose `ts` is in the window, deduplicated by `(plan, text)`. The line format `{ts, tool, plan, step, text}` is settled in the spec section 4; step 5 writes it, so `early` reads 0 until then.
- `attempts.by_role`: `{role: {count, median_min, max_min}}` over completed attempt records in the window, minutes from `started_at` to `finished_at`.
Add selftest cases with exactly these labels: `interrupted: lost_min runs to the next attempt start in the same dir and role`, `orphaned: a running attempt whose parent pid is dead is counted`, `negative control: a running attempt whose parent pid is alive is not counted orphaned` (use the selftest's own pid), `results: a builder result whose Status is blocked is counted`, `plan_defects: a plan defect line in a builder or verifier result is counted late`, `plan_defects: a refusals.jsonl line in the window is counted early`, `attempts: completed verifier minutes run from started_at to finished_at`. Update the module docstring's field list.

Then remove the "absent until plan step 1" notes from the `read:` lines of `docs/kpi/002-restart-recovery-minutes.md`, `003-blocked-builders-per-wave.md` and `004-unsatisfiable-criteria-caught.md`, and the matching "cannot be read today" sentence in each Reading it, so the KPI files describe the fields as they now exist (K-004 keeps its note that early reads 0 until step 5).

Contract dependents (`git grep -l fleet_collect -- plugins scripts`): `fleet_detect.py`, `fleet_status.py`, `plan_check.py`, `check.py`, `check.sh`, `skills/fleet-retro/SKILL.md`, `skills/plan-goal/references/goal-rules.md`, `skills/plan-verification/references/outcome-block.md`. All read existing keys only; the new keys are additive, so none is edited. Validation scope: `fleet_collect.py selftest`, plus `fleet_detect.py selftest` and `fleet_status.py selftest` as the two dependents that parse the collector's JSON. A read-only stand-in that computes the same numbers today is `.sdlc/plan-reliability-docs/kpi-baseline-probe.py`; compare one window by hand if a number looks off.

## Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/kpi/AGENTS.md`

## Done when
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && for l in 'interrupted: lost_min runs to the next attempt start in the same dir and role' 'orphaned: a running attempt whose parent pid is dead is counted' 'negative control: a running attempt whose parent pid is alive is not counted orphaned'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && for l in 'results: a builder result whose Status is blocked is counted' 'plan_defects: a plan defect line in a builder or verifier result is counted late' 'plan_defects: a refusals.jsonl line in the window is counted early'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `out=$(python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: attempts: completed verifier minutes run from started_at to finished_at'`
- (red) `test -f docs/kpi/002-restart-recovery-minutes.md && ! grep -qF 'absent until plan step 1' docs/kpi/002-restart-recovery-minutes.md docs/kpi/003-blocked-builders-per-wave.md docs/kpi/004-unsatisfiable-criteria-caught.md`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_detect.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/fleet_collect.py -e docs/kpi/002-restart-recovery-minutes.md -e docs/kpi/003-blocked-builders-per-wave.md -e docs/kpi/004-unsatisfiable-criteria-caught.md)"`

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Acceptance criteria
- `fleet_collect.py selftest` prints `ok:` for each of the seven labels in Done when and exits 0.
- `runs.interrupted.attempts[].lost_min`, `lost_min_median` and `lost_min_total`, `runs.orphaned`, `results.builder`, `plan_defects` and `attempts.by_role` appear in `fleet_collect.py collect` output with the shapes in Intent; every key present before is unchanged.
- `fleet_detect.py selftest` and `fleet_status.py selftest` pass.
- None of `docs/kpi/002`, `003`, `004` contains `absent until plan step 1` or a "cannot be read today" sentence; 004 still says early reads 0 until plan step 5.
- Only `fleet_collect.py` and the three KPI files changed outside `.sdlc`.

## Closed

2026-10-09: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
