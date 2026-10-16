---
id: T-0589
title: "lanes.py open locks the worktree with its owner; ready and close unlock it"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0588]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0589-t0589
worktree: ../sdlc-lite.worktrees/T-0589-t0589
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane in use is visibly owned on every host. `lanes.py open` runs `git worktree lock --reason "<host>:<session> T-NNNN"`; `lanes.py ready` (T-0590) and `close` unlock it. `lanes.py list` and every sweep show the owner and never call a locked lane closable.

## Context
Maintainer decision 2026-10-15: Claude Code, Codex and Pi work tickets in one repo at once. The design is in the conversation summary: claims and ids are atomic through git refs, which every worktree and host shares; lanes are locked with their owner; workers signal ready with a pinned sha; one conductor per repo writes main. Workers commit nothing (Codex workspace-write cannot write .git); the conductor commits. On 2026-10-15, `lanes.py list` showed two running lanes as `closable` because their branches had no commits yet and nothing locked them. The Lanes rule already says a locked worktree is a running lane.

## Intent
- Do: lock on open, with the reason; unlock on close; `list` prints `running (<reason>)` for a locked lane; sweep skips it.
- Non-goals: ready (T-0590).
- Done when: the criteria pass.

## Constraints
`--discard` close still works on a locked lane after an explicit unlock.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0. Its new case shows an opened lane with no commits listed as running with its owner, not closable, and sweep `--apply` keeping it. The case failed before the change.
2. `git diff --check` exits 0.
