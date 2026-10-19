---
id: T-0595
title: "lanes.py finish leaves the lane-close edit staged and can stick on rerun"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py finish` leaves main clean, and a rerun after main moved still completes.

## Repro
1. First live use, 2026-10-15, on T-0565: `lanes.py finish T-0565-t0565 --transcript ... --verifier-transcript ...` printed `close: skipped (T-0565 is done in main)` and `finish: ... done`, rc 0, but left staged in main the ticket's removed `branch:` and `worktree:` lines and the regenerated `messages/**/AGENTS.md`. The maintainer committed them by hand (`1653f5ab`).
2. The T-0594 solo found the second case: land merges into `finish/<lane>`, settle stops, main moves, and every rerun fails the same way without a `land_gate` (settle cannot `--forward`).

## Expected
Finish commits the lane-close edit whenever it changes main (`<id>: lane <lane> closed`), including when close was skipped because fanout already closed the ticket. A rerun whose `finish/<lane>` is behind main merges main into it (generated files resolved as in T-0565) and settles.

## Context
`lanes.py finish` (T-0594). The record step's `dispatch.py record` path worked live: the solo was priced at $2.67.

## Constraints
No push without `--backup`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0. Its new cases cover:
   - a finish whose close is skipped, which leaves `git status --porcelain` empty in main;
   - a rerun after main moved between land and settle, which completes.

   Both cases failed before the fix.
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: 7873caf51047
- Changed: finish commits through ignored tracked paths, stops if the lane-close commit fails, and forwards a stale finish branch
- Commits: ee4dca1 T-0595: finish commits through ignored tracked paths and forwards a stale finish branch
- Check: 1 `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, with new cases for a skipped-close...: pass
- Check: 2 `git diff --check` exits 0: pass
- Follow-up: note: redck.py deviations printed no process deviation: lines, and... -> notes.md
