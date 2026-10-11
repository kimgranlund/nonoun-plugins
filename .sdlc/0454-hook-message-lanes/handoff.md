---
id: T-0454
title: "Stray-worktree hook message points to lanes.py (lane lifecycle D)"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0453]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The stray-worktree hook message tells the person which command opens and closes a lane.

## Intent
- Do: ticket D of section 13: `hooks/block-stray-worktree.sh` (message text only, naming `lanes.py open` and `lanes.py close`), `scripts/hook-selftest.sh` (the C7 cases) and one sentence in `docs/references/claude-hooks.md`.
- Non-goals: any hook logic change.
- Done when: `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 with both C7 cases; `git diff --check` is clean.

## Context
Design (approved by the maintainer 2026-10-11, build A to D as a chain): `docs/specs/sdlc-lite/lane-lifecycle.md`, especially section 13 (ticket table), section 7 (the landed test and truth table), section 8 (who calls close) and section 8.1 (every lane has a ticket, tracker-agnostic). Interim lane guidance now in `plugins/sdlc-lite/AGENTS.md` (Lanes). Maintainer tool `~/.claude/lane/sweep.py` is the logic to port. Shared hot files (`check.sh`, `check.py`, `fanout.py`): one writer at a time.

## Constraints
No model or effort change. Never delete unmerged work; archive ref `refs/archive/<date>/<branch>` before any removal. A locked worktree is a running lane. No push, tag or publish. Read-only against any repo it does not own.
