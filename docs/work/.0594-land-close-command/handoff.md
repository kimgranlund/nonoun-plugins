---
id: T-0594
title: "One plugin command records, lands, closes and backs up a lane"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Finishing a lane is one plugin command, so no conductor state lives in scratch or context. `lanes.py finish <lane>` records the verifier dispatch, records and prices the solo, commits the lane, lands it into the default branch (with the generated-file resolution), carries run records, runs the configured gate, closes the ticket and removes the lane. It prints one line per step and stops at the first failure with a rerun-safe message.

## Context
Maintainer decision 2026-10-15 (risk 2 of the multi-host review). A host crash on 2026-10-15 wiped the maintainer's scratch `land.sh`, which was rebuilt from the transcript. The same sequence runs by hand for every ticket: `dispatch.py record` for the verifier, `solo_run.py complete`, `git commit`, `git merge` (or `fanout.py land`), resolve `.sdlc/AGENTS.md` and `roadmap.md`, copy runtime records (now automatic, T-0566), `check.sh`, `tickets.py close --rewrite-refs`, `lanes.py close`, and an optional backup push. The pieces exist; the order and recovery do not.

## Intent
- Do: compose the existing commands. Each step is idempotent, and a rerun skips completed steps (detected from the attempt records, merge ancestry and ticket status). Read the gate command from `.sdlc/config` `land_gate:`, defaulting to none. A `--backup <remote ref>` option pushes only when given.
- Non-goals: new merge logic; publishing beyond the explicit backup ref.
- Done when: the criteria pass.

## Constraints
Never pushes without `--backup`. Never closes without a pass verdict. Stops on any merge conflict outside generated files.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0. Its new cases cover:
   - a solo lane with a pass verdict, where `finish` leaves the ticket done, the lane removed and main containing the work;
   - a rerun after a simulated stop between merge and close, which completes without a second merge;
   - a fail verdict, which stops before merging.

   The cases failed before (no command).
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L3 · verdict: pass · verifier: verifier-L2 (sonnet) · base: 2c4bae57eee5
- Changed: lanes.py finish records, lands, settles, closes and removes a lane in one rerunnable command
- Commits: 6fd473e T-0594: lanes.py finish records, lands, settles, closes and removes a lane in one rerunnable command; b54808c T-0594: record planner skip for solo L3
- Check: 1 `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with new cases for a pass lane, a r...: pass
- Check: 2 `git diff --check` exits 0: pass
- Follow-up: note: /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/T-0594-t0594... -> notes.md
- Follow-up: note: /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/T-0594-t0594... -> notes.md
