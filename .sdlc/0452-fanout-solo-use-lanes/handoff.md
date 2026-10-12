---
id: T-0452
title: "fanout.py and solo_run.py use lanes.py (lane lifecycle B)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0451]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
fanout and solo_run open and close their lanes through `lanes.py`, so a merged lane's tree is gone after a run and a stopped lane stays with a report line.

## Intent
- Do: ticket B of section 13: `fanout.py` (open in setup, close merged lanes, sweep at start, `lane still open` report lines, `SDLC_LANE_PORT`, `prep` prints `lanes.py open` for a `full` lane and writes the host record, `roll` removes its scratch, docstring and selftest cases); `solo_run.py` (`ensure_worktree` through `lanes.open`, selftest); `skills/fanout/SKILL.md` (a lifecycle paragraph replaces "Lane worktrees stay after the run", step 5 runs `lanes.py sweep`; keep the `.claude/worktrees/` phrase `check.py` pins). Fold in the integration-branch settle: after a non-fast-forward merge of the integration branch, `fanout.py settle` removes the branch and worktree.
- Also fix the T-0451 flake: the `lanes.py selftest` isolation case (criterion 8 of T-0451, selftest leaves worktrees and refs unchanged) compares the branches and worktrees of the real repository, so another session or lane writing refs during the run makes it fail (observed once in T-0451 step 1, and a first `check.sh` run exited 1 and passed on rerun). Limit the comparison to the selftest's own temporary repository; keep an observed-red control that a leaked ref or worktree in that temp repo is still caught.
- Non-goals: tickets.py, dispatch.py (C); the hook (D).
- Done when: `(red)` a fanout selftest case that expects a merged lane's tree gone after `run` fails now; after, `fanout.py selftest` and `solo_run.py selftest` exit 0, a stopped lane stays with its report line; `check.sh` exits 0.

## Context
Design (approved by the maintainer 2026-10-11, build A to D as a chain): `docs/specs/sdlc-lite/lane-lifecycle.md`, especially section 13 (ticket table), section 7 (the landed test and truth table), section 8 (who calls close) and section 8.1 (every lane has a ticket, tracker-agnostic). Interim lane guidance now in `plugins/sdlc-lite/AGENTS.md` (Lanes). Maintainer tool `~/.claude/lane/sweep.py` is the logic to port. Shared hot files (`check.sh`, `check.py`, `fanout.py`): one writer at a time.

## Constraints
No model or effort change. Never delete unmerged work; archive ref `refs/archive/<date>/<branch>` before any removal. A locked worktree is a running lane. No push, tag or publish. Read-only against any repo it does not own.
