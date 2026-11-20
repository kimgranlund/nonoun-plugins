---
id: T-0871
title: "When a landed host agent worktree is still locked by the harness, the close output says so and gives a removal"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0870]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When a landed host agent worktree is still locked by the harness, the close output says so and gives a removal command that works, and the docs say who releases that lock.

## Intent
- Do: make the host-owned removal hint lock-aware and document the lock owner.
- Non-goals: removing locked trees automatically; changing sweep, which already keeps host-owned trees.
- Done when: the criteria below hold.

## Context
- #97: 19 agent worktrees were clean and merged but `cannot remove a locked working tree, lock reason: claude agent ...`; only `remove -f -f` overrode it. Ask: skip locked worktrees with a clear note, and "the docs say who releases the lock (the harness, when the agent ends)".
- `plugins/sdlc/scripts/lanes.py:1065` prints `host-owned <p> landed in <b>; remove it yourself: git worktree remove <p>`, which fails on a locked tree. The row-4 doc at line 116 repeats it. Selftest lines 3846 and 3872 assert the exact text. `discover` reads `locked` from `git worktree list --porcelain` (line 430).
- Design: when the host tree is locked, print `host-owned <p> landed in <b>; locked by the harness (<reason>), which releases it when its agent ends; once that agent has ended: git worktree unlock <p> && git worktree remove <p>`. Unlocked trees keep today's text.
- Doc homes: the `lanes.py` docstring row 4, the Lanes section of `plugins/sdlc/AGENTS.md` (host-owned bullet), and the `lanes.py` entry of `docs/references/sdlc-internals.md`.
- Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`.

## Do
1. Make the hint lock-aware as above.
2. Add a selftest case beside lines 3846-3872 with the agent tree locked (`git worktree lock --reason "claude agent x"`), asserting the new text; keep the unlocked case.
3. Update the three doc homes and the CHANGELOG `[Unreleased]`.

## Acceptance criteria
- The lanes selftest (or the shard holding the host-owned cases) exits 0; with the lock check removed, the locked case fails (state the observed red).
- `bash plugins/sdlc/scripts/check.sh --fast` exits 0 and `git diff --check` is clean.

## Constraints
- No lanes.py command removes a tree with a foreign lock.
