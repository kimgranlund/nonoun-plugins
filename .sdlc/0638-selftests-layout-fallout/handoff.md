---
id: T-0638
title: "results and plan_check selftests break under the work_root migration"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `results.py` and `plan_check.py` selftests pass both on today's layout and in a repository migrated to `work_root: docs/work`, proven by running them in the migrated T-0636 lane tree.

## Repro
1. On main: `python3 plugins/sdlc-lite/scripts/results.py selftest` exits 1: `MISS: negative control: an accept-all results.py lets steps.py next print verify` with `ModuleNotFoundError: No module named 'roots'` from the copied `order.py`.
2. In the migrated lane `/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/T-0636-t0636`: `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` fails `goal: the good block passes`, `goal: the topics-layout notes path passes` and three done-measured goal cases.

## Expected
Both selftests are independent of the live repository layout.

## Actual
`results.py` selftest copies only `steps.py`, `order.py` and `results.py` into its accept-all dir (`results.py` near line 359), but `order.py` imports `roots` since T-0622. `plan_check.py` goal selftest cases resolve the notes path against the real repository's `.sdlc/config`, so once that config sets `work_root` (T-0631 rule) the legacy-path fixtures fail.

## Context
Found by the full check.sh in the T-0636 lane (2 of 57 jobs failed) on 2026-10-19. T-0636 (this repo's migration) waits on this ticket.

## Constraints
- The failing check lands before or with the fix.
- Fix the selftests, not the rules: the T-0631 work_root notes rule stays.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/results.py selftest` exits 0 on this tree.
- `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0 on this tree.
- Both selftests exit 0 when run with the lane's fixed scripts inside a `work_root: docs/work` repository: copy the two fixed files into `/Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/T-0636-t0636/plugins/sdlc-lite/scripts/` is NOT allowed; instead run them from a throwaway worktree of this lane whose `.sdlc/config` has `work_root: docs/work` added.
