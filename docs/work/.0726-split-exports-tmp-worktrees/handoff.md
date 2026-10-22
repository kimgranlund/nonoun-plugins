---
id: T-0726
title: "steps.py split sets SDLC_TMP_WORKTREES for guard and red spans"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py split --only N` runs guard and red spans with `SDLC_TMP_WORKTREES` set to a fresh throwaway dir that it removes afterwards, so a guard using it is not misread as a plan defect.

## Intent
- Do: In `steps.py`, export a temp `SDLC_TMP_WORKTREES` (under the repo scratch root) for the spans it runs, and remove it after.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #50 (quoted):

> **Repro**: a plan whose guard criterion uses `mktemp -d "$SDLC_TMP_WORKTREES/x.XXXXXX"`; run `steps.py split <task> --only 1 --tree <lane>`.
>
> **Expected**: split exports SDLC_TMP_WORKTREES (as briefs do) before running guard/red spans.
>
> **Actual**: `mktemp: mkdtemp failed on /uikn.t7SGDH: Read-only file system` and split prints `plan defect: step 1 red guard: ... replan this step (/chain 3)`, i.e. an environment gap is routed to a replan. Workaround: `SDLC_TMP_WORKTREES=<dir> steps.py split ...`.
>
> **Evidence**: `grep -n SDLC_TMP_WORKTREES scripts/steps.py` has no match; T-0073 split on 2026-10-22.
>
> ---
> Found by a trace review (sdlc-lite `review-traces`) of a 2026-10-21/22 fanout run, sdlc-lite 0.30.0 to 0.33.0.
>

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `steps.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`steps.py split --only N` now runs guard and (red) spans with `SDLC_TMP_WORKTREES` set to a fresh `split-spans-*` dir under the worktree root tmp prefix (`span_tmp`, `span_env(base, tmp)`, `run_guard(..., tmp)`, `red_first(..., tmp=)`), removed after the spans ran. `swap`, `amend`, `widen`, `redck.py` and `specgate.py` are unchanged.
- Criterion 1: two selftest cases `(T-0726) --only exports SDLC_TMP_WORKTREES to a guard ...` and `... to a (red) span ...` pass. With the export line replaced by `pass`, `steps.py selftest` exits 1 and lists both: `  - (T-0726) --only exports SDLC_TMP_WORKTREES to a guard, a fresh dir removed afterwards` and `  - (T-0726) --only exports SDLC_TMP_WORKTREES to a (red) span, a fresh dir removed afterwards`.
- Criterion 2: `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exit 0.
- Criterion 3: `python3 plugins/sdlc-lite/scripts/check.py` exit 0, `python3 scripts/check-packaging.py` exit 0, `git diff --check 83a3a4e6` exit 0.
- Also updated the `steps.py` split docstring and `docs/references/sdlc-internals.md`.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 83a3a4e63e21
- Changed: see commits
- Commits: b0df23d T-0726: steps.py split exports SDLC_TMP_WORKTREES to guard and red spans
- Check: 1 A `steps.py` selftest case reproduces the issue's repro and passes; with the change reverted it f...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plug...: pass
- Check: 3 `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0: pass
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:1042-1053 Conductor check: the... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:1031-1039 Conductor check: a... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:4251,4397,4653,3697 and... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:5367 The selftest runs from a... -> notes.md
