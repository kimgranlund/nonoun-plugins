---
id: T-0139
title: "Pre-sync wip<id>: dirty before sync commit in fanout.py run_ticket..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0126
---

## Goal
A `wip(<id>): dirty before sync` commit that `fanout.py` `run_ticket` makes on a lane branch can never reach the integration branch, matching the documented contract that a `wip(<id>)` commit is never merged.

Conductor decision (unattended, derived from that contract, no user choice needed): guard. When the pre-sync `wip_commit` finds a dirty lane tree, `run_ticket` stops that ticket with an outcome other than `merged` (for example `dirty before sync: wip <sha>`), so no sync, driver, lane commit, or merge happens for it, and the lane stops as for any other non-merged outcome (remaining tickets `skipped`). The wip sha shows in the report. The planner may pick an equivalent guard if it finds a reason, but must not merge that commit.

## Context
Follow-up from T-0126 (chain-stop-leaves-dirty-tree/filer-L1.md):

Pre-sync `wip(<id>): dirty before sync` commit in `fanout.py` `run_ticket` would be merged into the integration branch if that ticket then merges. It is unreachable today, but a lane with a dirty tree before its first ticket would trigger it; decide whether to guard or drop that commit from the merge.

## Constraints
- A clean lane tree before sync behaves exactly as today (all existing fanout selftests stay green).
- Main is never touched; the wip commit stays on the lane branch only.
- `fanout.py selftest` gains a case that makes a lane tree dirty before its first ticket and proves: the outcome is not `merged`, the lane branch tip is `wip(<id>): dirty before sync`, and that commit is not an ancestor of the integration branch; plus a negative control.
- Docs that describe fanout's wip behavior stay accurate in the same change: the fanout.py docstring, `skills/fanout/SKILL.md`, repo-root `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` where they cover it.
- `plugins/sdlc-lite/scripts/check.sh` passes.

## Done when
The guard is in, the selftest case and negative control pass, docs match, and `scripts/check.sh` is green.
