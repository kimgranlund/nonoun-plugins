---
id: T-0680
title: "lanes.py open --into an integration branch writes the claim and lane record there, not on main"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`lanes.py open --into <branch>`, when that branch is checked out in an integration worktree, writes the ticket's `branch:` and `worktree:` lines and the `<ids>: record lane <leaf>` commit in that integration tree, not in the main checkout. Main gains no lane-record commit unless `--root` explicitly points there.

## Intent
- Do: in `open_lane` (`plugins/sdlc-lite/scripts/lanes.py`, near line 1348), when `--root` was not given (make its argparse default `None` near line 1889 and treat `None` as `.sdlc`), resolve the worktree holding `into_` with `worktrees(top)` (line 359); when it is not the main checkout, set `rootp` to that tree plus the same root, and run the `pre`/`porcelain`/`commit_new` block (near lines 1446 to 1478) against that tree instead of `top`. Print `recorded in <tree relative to the main checkout>` so the conductor sees where the commit went.
- Do: update the T-0599 paragraph of the `lanes.py` docstring (near line 55) and the `Open:` bullet of `plugins/sdlc-lite/AGENTS.md` (Lanes section, line 42) to say the record goes to the integration tree when `--into` names one.
- Do: add a `lanes.py selftest` case: open an integration tree, open a lane with `--into <integration>` and a local ticket, then assert main's HEAD did not move and the integration branch gained the `record lane` commit.
- Non-goals: changing the T-0609 upstream rule; changing `fanout.py prep`, which opens its own lanes.
- Done when: the criteria pass.

## Context
Source: GitHub issue #34, ui-kit 0.27 vs 0.28 measurement 2026-10-21.
- 16 lane-record commits on main had to be reverted by hand in three rounds (one, `b0325ff`, reverted nine). The workaround that worked: `--root <integration tree>/.sdlc`, after which main moved 0 commits.
- The issue marks 0.28.1 unverified; main still has the behavior. `open_lane` sets `rootp = Path(cwd, root)` (lanes.py:1361), relative to the cwd, and the commit runs `commit_new(top, ...)` (lanes.py:1465) where `top` is the main checkout. Nothing reads `into_` to pick the tree.
- With `--root <integration tree>/.sdlc` today, `record_branch` writes into the integration tree but `commit_new(top, ...)` sees no change in main, so nothing is committed there either; the new path must commit in the integration tree.
- `lanes.py open` has no skill `## Arguments` table; its flags are documented in the module docstring (lines 4 and 5).

## Constraints
- A ticket folder missing from the integration tree (filed on main after the branch forked) falls back to the main checkout and prints why, never fails the open.
- An explicit `--root` keeps today's behavior exactly.
- A dirty-before-open path in the integration tree is never committed, as in main today.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with the new case, and the case fails with the `open_lane` change reverted.
2. `git grep -n "integration tree" plugins/sdlc-lite/AGENTS.md` shows the updated `Open:` bullet.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
4. `git diff --check <base sha>` exits 0.
