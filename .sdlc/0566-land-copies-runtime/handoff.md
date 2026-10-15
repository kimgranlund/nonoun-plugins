---
id: T-0566
title: "fanout.py land carries the lane's run records to main"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0564]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0566-t0566
worktree: ../sdlc-lite.worktrees/T-0566-t0566
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Closing a ticket that ran in a lane needs no manual copy: after `fanout.py land`, the lane's `.sdlc/runtime/tasks/<ticket>/` records are in main's runtime, and `tickets.py close` finds the verifier verdict there.

## Intent
- Do:
  1. `fanout.py land` (and `lanes.py close`, if it removes a lane before land ran) copies the lane's `.sdlc/runtime/tasks/<key>/` into the main checkout's runtime for each ticket it lands, without overwriting newer files there; it prints `records: <path>`.
  2. Remove the manual copy step from `.claude/agents/sdlc-lite-author.md` "Running waves" item 3 and any skill that tells the conductor to copy.
- Non-goals: tracking `runtime/` in git.
- Done when: the criteria pass.

## Context
`.sdlc/runtime/` is gitignored (live per-checkout state), so a merge carries none of a lane's attempts, dispatch files or verifier result, and `tickets.py close` refuses for lack of a verdict. The conductor copies by hand today ("Running waves" item 3). Records dir rule: `order.py records-dir`; `tickets.py` around line 1806.

## Constraints
Never delete or overwrite a newer record in main. A lane under the sibling root (T-0563) and a legacy in-repo lane both work.

## Acceptance criteria
1. A `fanout.py selftest` case lands a lane with a verifier result under its runtime and then runs `tickets.py close` in main without any copy; it failed before the change.
2. A main record newer than the lane's copy is kept.
3. `grep -n 'copy the lane' .claude/agents/sdlc-lite-author.md` prints nothing.
4. `bash plugins/sdlc-lite/scripts/run-selftest.sh` and `git diff --check` exit 0.
