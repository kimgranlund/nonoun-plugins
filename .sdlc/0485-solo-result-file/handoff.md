---
id: T-0485
title: "solo has no validatable result file"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Run `python3 plugins/sdlc-lite/scripts/solo_run.py run --backend codex --task-dir <ticket> --tier L1 --no-worktree --brief ...` as in `docs/reports/codex-live-evidence.md`, then `python3 plugins/sdlc-lite/scripts/results.py validate <file> --role solo`.

## Expected
A finished solo run leaves a result file in the task folder that `results.py validate` can check, so a solo run has the same evidence as a chain role.

## Actual
The runs.jsonl row has `"file": ""` and `results.py validate --role` has no solo role (see `docs/reports/codex-live-evidence/solo-runs.jsonl`). A solo run is evidenced only by its report, the diff and a rerun of its done check.

## Context
Found by T-0316 (`docs/reports/codex-live-evidence.md`, section What did not work). The solo report format has `solo-report` in `results.py` (spans per criterion); a validate role could reuse it.

## Constraints
The failing test lands before or with the fix, never after.
