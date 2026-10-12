---
id: T-0490
title: "solo_run.py defaults to a worktree when an integration lane is open in the repo (T-0488)"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`solo_run.py` runs a solo in its own worktree by default when `lanes.py list` shows an open integration lane in the repo, so a solo in the primary checkout cannot dirty a tree that a wave merge needs clean.

## Intent
- Do: in `scripts/solo_run.py` (`:33-35`, T-0345 adds a worktree only when another solo is live) add the open-integration-lane condition; `--no-worktree` still forces the checkout.
- Non-goals: any change for chain roles or the builder; fanout lanes.
- Done when: a `solo_run.py selftest` case with an open integration lane starts in a worktree (red first: today it uses the checkout), a case without one is unchanged, and `--no-worktree` wins; `check.py` exits 0.

## Context
Design: `docs/planning/merge-ops-and-queue.md` (Approach 1, later build B). Lower priority than T-0489.

## Constraints
Never delete unmerged work; reuse the lane open/close rules in `lanes.py`.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0, and its `integration lane:` cases show an open integration lane (unlanded work) defaults the solo to a worktree, a closable lane and a repo with no lane keep the checkout, `--no-worktree` wins, and a solo already inside a lane tree does not nest a worktree.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
- (red) with the new `open_integration_lane` condition removed from `auto_worktree`, the `integration lane: an open lane defaults the solo to a worktree` case fails.

## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
