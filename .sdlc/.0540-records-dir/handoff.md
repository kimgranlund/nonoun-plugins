---
id: T-0540
title: "Lean records A: Records dir (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L4             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Records dir: part A of SDLC Lite 0.23.0 lean work records (wave 1).

## Intent
- Do: build part A of the design in `.sdlc/.0539-lean-work-records/architect-L1.md` (read its Approach, the row for A, Interfaces and Risks). Files: `scripts/order.py` (`records_dir`; a `records-dir <task dir>` CLI that prints the path for the conductor, skills and Codex; `records`/`ordered`/`_results` resolve it), `dispatch.py` (prepare `artifacts_dir`, `build_base`, `next_stem`, `attempt_dirs`/`recover`/`resume`/`status` walk `runtime/tasks/*` plus legacy dirs, `lane_gate`, `solo_model`), `run.sh`, `run_lifecycle.py`, `solo_run.py`, `steps.py` (split/swap/widen write step dirs in the records dir; `record_lane`, `write_solo_skips`, `base_sha`, `result_ts`), `redck.py` (path only), `budget.py` (ack and `spend`), `verify_scope.py`, `codex_exec.py` (top-level `native-*` request files into `runtime/`), new `scripts/records.sh`, `hooks/block-role-spawn.sh` (read the prompt's `Artifacts dir:` line, else beside the handoff), `hooks/warn-handoff-edit.sh`, `lifecycle-selftest.py`, `run-selftest.sh`, `hook-selftest.sh`, `skills/handoff-format/SKILL.md` layout block :9-78, `adapters/codex/instructions.md` resume packet
- Non-goals: the other parts (A to F) of the same design.
- Decided (user, 2026-10-13, after plan review blocked): `skips.md` stays in the task folder in A, and C or D moves it. `tickets.py skip_missing` and fanout selftest case 16 are left unchanged, so `check.sh` stays green between waves.
- Done when: `bash plugins/sdlc-lite/scripts/check.sh` exits 0. A new dispatch.py selftest case: prepare plus record in a git fixture leaves `git status --porcelain -- <task dir>` listing only `handoff.md`, with the records under `.sdlc/runtime/tasks/<name>/`. Negative control: a legacy fixture with `runs.jsonl` in the task dir keeps recording in place. Hook selftest: spawn allowed through the `Artifacts dir:` line, denied when neither location holds a dispatch file

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.

## Plan review
plan review: blocked: .sdlc/0540-records-dir/plan-reviewer-L1.md
plan review: decision: maintainer picked (c): skips.md stays in the task folder in A (see Intent "Decided"); tickets.py skip_missing and fanout selftest case 16 stay unchanged.
plan review: replan: step 3: drop the skips.md move; step 3 keeps skips.md writers (record_lane, write_solo_skips) on the task folder so fanout case 16 stays green.
plan review: replan: step 2: run_lifecycle.run derives its dir from the handoff and its only caller is run.sh (step 4); order the run.sh/run_lifecycle/lifecycle-selftest change in one step so every step's criteria are green on their own.
plan review: replan: step 2: hook-selftest.sh prepared cases record .sdlc/task/scout-L1.dispatch.json and read $pt/scout-L1.attempt.json (hook-selftest.sh:667-677, :691); update those with stale-edits.log.
plan review: replan: plan: drop the claim that step 3 does not need step 2's code.
plan defect: dispatch.py prepare builder L3 step-1 refused: steps.py lint link check: "cited path does not exist" for fixture paths written as "$d/.sdlc/<name>" in criteria and Do text (step 1: 30, step 2: 19, step 3: 10 findings; e.g. .sdlc/0001-a, .sdlc/.0002-b/step-2, .sdlc/runtime/tasks/0001-a, .sdlc/task). The lint treats a "$d/" prefixed .sdlc path as a repo-relative citation unless it sits in a (red) criterion code span or a [creates: ...] marker (steps.py declared_future_paths, cited_sdlc_paths). Fix: keep the plan from planner-L3-2.md (it passed review plan-reviewer-L1-2.md) and declare every fixture path in each step with one [creates: <path>, ...] marker (or another form the lint accepts); run `steps.py lint` on each step handoff text before returning. Carry the plan-reviewer-L1-2 notes-fix lines into step 2 Notes.

## Closed

2026-10-14: warnings acknowledged: process deviations only: every red control was run by the step verifiers on base copies; decide item is owned by T-0541 and T-0543, notes by T-0545

> - Step 3's first verifier (verifier-L3) failed. `steps.py` could not read a task-side step handoff once its records twin existed and was empty, which broke `dispatch.py selftest`. The retry (builder-L4-2, then verifier-L3-2) passed. The first attempt's second finding, `fanout.py` `planned_scope` ignoring records-dir step folders, is shown by the artifacts as handled in the retry. I did not read builder-L4-2's text for that.
> - process deviation: red-checkpoint, step 2: retrospective, attempt 2669785dc90a4be2a582e2c5bd66760c. All 6 of 6 (red) criteria had no pre-edit red control. Step 1's uncommitted `order.py` and `records.sh` already differed from HEAD when `redck.py record` ran. The verifier ran each red control itself on a base copy and saw red.
> - process deviation: red-checkpoint, step 3: retrospective, attempts 73db2d8f0bfc4e51bc59daa02023a918 and 54ed83b3c2ed475fb02b8dd12cc9ac17. Both (red) criteria in each attempt had no pre-edit red control, because the 14 step-1/2 paths were already dirty. The verifier ran the controls itself and saw red at base and green on the built tree.
> - process deviation: red-checkpoint, step 4: retrospective, attempt f9158105536b4335b1256a615ed4d778. 2 of 2 recorded (red) criteria had no pre-edit red control. The step has 3 (red) criteria and `redck.py` recorded only 2 controls, and nobody traced why. The verifier ran the base-sha controls for all three.
> - process deviation: red-checkpoint, step 5 (Loose ends): retrospective, attempt 7c67b11d67344d09a2509bd915e33915. Both (red) criteria had no pre-edit red control, because 49 paths already differed from HEAD. The verifier ran the red controls itself on mutated scratch copies.
> - Passing verdicts do not clear the deviations above.
> - Unverified: `fanout.py selftest` was not usable in steps 2 and 3, because step 2's handoff declared it red until step 3. Step 1's verifier saw no output from `fanout.py selftest` or `tickets.py selftest`. Step 4's verifier ran `check.sh`, which exited 0 after 18m17s.
> - Step 5's second (red) criterion does not fail through the new case's own assertion. With `step_dirs` mutated to read only the records side, an earlier selftest case crashes first. The criterion goes red, but the new case is never reached under that mutation.
