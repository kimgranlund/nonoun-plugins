---
id: T-0541
title: "Lean records B: Cost, board and fleet readers (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0540]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Cost, board and fleet readers: part B of SDLC Lite 0.23.0 lean work records (wave 2).

## Intent
- Do: build part B of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for B, Interfaces and Risks). Files: `report.py`, `solo_stats.py`, `board.py`, `fleet_collect.py` (`scan_sdlc`, `ticket_of` maps `runtime/tasks/<name>` to `<name>`, lane from Outcome for closed rows, plan defects from `## Plan review` lines), `fleet_status.py`, `traces/ingest.py` (`SKIP_TASK`), `traces/sources/*.py`, `traces/rerun.py`, `proposals.py` (`SKIP_TOP`), `footprint.py`, `plan_done.py` (`runs.jsonl`; `plan-state.json` into the plan folder's records dir), `reorg.py` (`held_locks` :386-400 looks for `.run.lock` in records dirs), `statusline.sh`, `bench-summary.sh`
- Non-goals: the other parts (A to F) of the same design.
- Done when: Selftests of report, solo_stats, board, fleet_collect, fleet_status, plan_done and traces exit 0 with a runtime-only fixture that reports nonzero cost under the right ticket key. Negative control: the same fixture with the runtime dir removed reads the legacy in-folder records

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.

## Closed

2026-10-14: warnings acknowledged: process deviations only: verifiers ran every red control against the base archive; all steps pass

> - process deviation: red-checkpoint: retrospective: attempt 4c2fc64fdc814fa4b9ee1d7743ee6f78, handoff sha256 41f9ce21a7e0, 7 of 7 (red) criteria in step 2 had no pre-edit red control recorded before the edit. The tree already held step 1's uncommitted edits, so the builder recorded it as retrospective. The step 2 verifier later ran each of the 7 criteria against a `git archive` of the base sha. All 7 failed there (red) and passed on the built tree. A passing verdict does not clear this deviation.
> - All three steps passed their verifiers (step 1, step 2, step 3: pass). No step failed or lacks a verdict.

2026-10-14: kept stale refs to .sdlc/0541-records-readers in: .sdlc/.0540-records-dir/step-3/verifier-L3.md, .sdlc/runtime/tasks/0541-records-readers/planner-L3.md, .sdlc/runtime/tasks/0541-records-readers/step-1/builder-L3.md, .sdlc/runtime/tasks/0541-records-readers/step-1/handoff.md, .sdlc/runtime/tasks/0541-records-readers/step-1/verifier-L2.md, .sdlc/runtime/tasks/0541-records-readers/step-2/verifier-L2.md, .sdlc/runtime/tasks/0541-records-readers/step-3/verifier-L2.md
