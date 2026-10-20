---
id: T-0657
title: "steps.py review reports red criteria already green at base"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan whose `(red)` criterion already passes at the base commit is caught at `steps.py review`, before any builder starts, and reported as a plan defect.

## Intent
- Do: (1) `cmd_review` in `plugins/sdlc-lite/scripts/steps.py`, when the newest plan's action is `split` or `review`, runs every step's runnable `(red)` span (`red_spans`, skipping `guard_skipped`) once in a throwaway detached worktree at the base sha (`base_sha`), through `red_first`, and removes the worktree after. (2) Each span green at base is printed as `plan defect: red-at-base: step <n>: <span>`, appended under the handoff's `## Plan review` with `record_plan_review`, and turns the action into `replan` with that reason. (3) A `steps.py selftest` case: one plan with a span already green at base (review prints `replan` and the defect line) and one with a red span (review prints `split` as before).
- Non-goals: changing red-first at `split --only` (`run_red`) or `redck.py record`; running guard spans at review.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #17, ui-kit-neue audit 2026-10-20.
- Evidence: 8 role results reported a plan defect; T-0065 step 6's `reopen` grep was already green at base and passed two plan reviews, costing a blocked builder-L4 and a re-dispatch. Plan review cost $83.5 (16% of $520.6 role cost).
- Partly present: `run_red` (`plugins/sdlc-lite/scripts/steps.py:1162`) runs `(red)` spans through `red_first` (`:1134`) and records refusals with `record_plan_review` (`:1902`), but only at `split --only` (called at `:2287`); its docstring says a full split and lint never execute a span. So a full split, and review, accept an already-green red criterion.
- `review_action` (`plugins/sdlc-lite/scripts/steps.py:3323`) is documented as read-only; keep it so, and do the red run in `cmd_review` (`:3401`) after it returns. Output goes through `print_action` (`:3031`).
- Base: `base_sha(top)` (`:957`). Put the throwaway worktree under the worktree root tmp prefix (`wtroot.tmp_root`), as `dispatch.py` does.

## Constraints
A plan with no `(red)` spans reviews exactly as before, and review never changes the main or lane tree. Existing `split --only` red-first behavior is unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0. Its new case shows `steps.py review` on a plan whose `(red)` span is `test -f README.md` (present at base) printing `replan` and `plan defect: red-at-base: step 1`, and the same plan with `test -f absent.txt` printing `split`. The first case fails with the change reverted.
2. After that selftest, `git worktree list` lists no worktree it created (the case asserts this too).
3. `git diff --check` exits 0.
