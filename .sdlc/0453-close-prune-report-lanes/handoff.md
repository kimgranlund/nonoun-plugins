---
id: T-0453
title: "tickets.py close and dispatch.py prune report open lanes (lane lifecycle C)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0451]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Closing a ticket or pruning a finished agent prints the open lane it leaves behind.

## Intent
- Do: ticket C of section 13: `tickets.py close` prints one `lane still open: <path> (branch <b>, <reason>)` line per plugin lane whose record lists the ticket or whose host name is `<id>-solo` (exit code unchanged); `dispatch.py prune --done <name>` closes the host lane through `lanes.close` and prints `closed lane <path> (<reason>)` or `lane still open: <path> (<reason>)`, and the listing names an open lane; both selftests.
- Non-goals: any other lane behavior.
- Done when: `(red)` closing a ticket with an open lane prints no `lane still open` line now; after, `tickets.py selftest` and `dispatch.py selftest` exit 0; `check.sh` exits 0.

## Context
Design (approved by the maintainer 2026-10-11, build A to D as a chain): `docs/specs/sdlc-lite/lane-lifecycle.md`, especially section 13 (ticket table), section 7 (the landed test and truth table), section 8 (who calls close) and section 8.1 (every lane has a ticket, tracker-agnostic). Interim lane guidance now in `plugins/sdlc-lite/AGENTS.md` (Lanes). Maintainer tool `~/.claude/lane/sweep.py` is the logic to port. Shared hot files (`check.sh`, `check.py`, `fanout.py`): one writer at a time.

## Constraints
No model or effort change. Never delete unmerged work; archive ref `refs/archive/<date>/<branch>` before any removal. A locked worktree is a running lane. No push, tag or publish. Read-only against any repo it does not own.
