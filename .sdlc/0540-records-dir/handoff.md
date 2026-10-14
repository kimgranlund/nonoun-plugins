---
id: T-0540
title: "Lean records A: Records dir (0.23.0)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
- Done when: `bash plugins/sdlc-lite/scripts/check.sh` exits 0. A new dispatch.py selftest case: prepare plus record in a git fixture leaves `git status --porcelain -- <task dir>` listing only `handoff.md`, with the records under `.sdlc/runtime/tasks/<name>/`. Negative control: a legacy fixture with `runs.jsonl` in the task dir keeps recording in place. Hook selftest: spawn allowed through the `Artifacts dir:` line, denied when neither location holds a dispatch file

## Context
Maintainer decisions: `.sdlc/notes.md` "Lean work records (maintainer decisions 2026-10-13)". Objective: complete the task, update the ticket, hand off a clean merge-ready worktree, minimal documentation. Full chain reason: cross-cutting run-record change across scripts, roles and skills (design T-0539).

## Constraints
Preserve independent verification, the recorded build base, reference-safe closure and restart recovery. Legacy task folders stay readable with no migration.
