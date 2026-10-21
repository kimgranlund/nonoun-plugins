---
id: T-0695
title: "lanes.py close leaves a lane record written in an integration tree"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0680]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py close` removes a ticket's `branch:` and `worktree:` lines from wherever `lanes.py open` wrote them, including an integration worktree (T-0680), so no stale lane record stays behind.

## Intent
- Do: first reproduce in a `lanes.py selftest` fixture: open a lane with `--into` an integration branch that has a worktree (no `--root`), close it, and check the integration tree's ticket still holds `branch:`. Then make close clear the record in the tree that holds it (reuse T-0680's `record_tree`), and commit there.
- Non-goals: changing where the claim is checked.
- Done when: the criteria pass, or Outcome shows the reproduction did not fail and close already handles it.

## Context
Found by the T-0680 builder, untested: "lanes.py close removes branch: lines only from main's root, so a record written in an integration tree is not cleared by close". T-0680 added `record_tree` in `plugins/sdlc-lite/scripts/lanes.py` and its `open into integration` selftest case.

## Constraints
Closing a lane recorded on main behaves as before.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with a new case: after open `--into` an integration branch and close, the integration tree's ticket has no `branch:` or `worktree:` line; the case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
3. `git diff --check <base sha>` exits 0.

## Outcome
Reproduced: after `open --into <integration branch>` and a close, the integration tree's ticket still held `branch:` and `worktree:`. Added `clear_integration_record` in `plugins/sdlc-lite/scripts/lanes.py`, called from `do_close`: it clears the lane's lines (only while `branch:` is the lane branch) in the worktree holding the lane's into branch when that is not main, and commits them there as `<ids>: clear lane record <leaf>`, leaving paths dirty before the close alone. Closes recorded on main are unchanged. New selftest case `close integration record`; it fails with the call removed and passes with it.
- `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
- `git diff --check 64b57c74` exit 0

## Outcome

2026-10-20 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 64b57c746ed4
- Changed: see commits
- Commits: 746727f T-0695: lanes close clears the lane record in the integration tree
- Check: 1 `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with a new case that fails with the...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass
- Check: 3 `git diff --check <base sha>` exits 0: pass
