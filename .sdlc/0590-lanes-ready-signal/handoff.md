---
id: T-0590
title: "lanes.py ready pins the review sha and tells the conductor"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0589]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0590-t0590
worktree: ../sdlc-lite.worktrees/T-0590-t0590
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A worker on any host tells the conductor exactly what to review. `lanes.py ready <lane>` pins `refs/sdlc/ready/T-NNNN` at the lane state, snapshots uncommitted work as a commit when needed, unlocks the lane, and sends a `ready` mailbox message to the repo's conductor. `lanes.py list --ready` lists the queue. Verify and land use that sha, and a lane that moved after ready is flagged stale.

## Context
Maintainer decision 2026-10-15: Claude Code, Codex and Pi work tickets in one repo at once. The design is in the conversation summary: claims and ids are atomic through git refs, which every worktree and host shares; lanes are locked with their owner; workers signal ready with a pinned sha; one conductor per repo writes main. Workers commit nothing (Codex workspace-write cannot write .git); the conductor commits. Today the conductor learns a ticket is done from the sub-agent's final message, which works only for Claude sub-agents. Codex and Pi sessions have no such channel. `messages.py send` exists. The base drift bugs T-0578 and T-0587 are both cases of reviewing the wrong state.

## Intent
- Do:
  1. `ready` refuses when the lane has no changes, or when the ticket has no acceptance criteria. Snapshot uncommitted work with `git stash create`-style plumbing (no stash stack use) into a commit on the ready ref.
  2. Send `messages.py send --receiver <conductor> --kind handoff --topic "ready T-NNNN" <sha and lane path>`. The receiver comes from `.sdlc/config` `conductor:`, else `conductor`.
  3. `list --ready` prints ticket, lane, sha, and `stale` when the lane HEAD or tree differs from the pinned state.
  4. `dispatch.py prepare verifier` takes `Base sha:` and the review tree from the ready ref when it exists.
- Non-goals: an event-driven wake (T-0583).
- Done when: the criteria pass.

## Constraints
No use of the shared stash stack. Works with uncommitted lanes (Codex workers).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0. Its new cases cover: `ready` on a lane with uncommitted changes, which creates the ref with those changes and a mailbox message; `list --ready` showing it; an edit after ready, which shows `stale`; and `ready` on an unchanged lane, which refuses. The cases failed before the change.
2. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0. Its new case shows a verifier prepared for a ticket with a ready ref taking that sha as `Base sha:`.
3. `git diff --check` exits 0.

## Plan review
- amend: criterion 2, the verifier keeps `Base sha:` as the lane start (the base_sha recorded in the ready commit) and gets a new `Review sha: <ready sha>` line; prepare warns when the tree differs from the ready sha. Using the ready sha as Base sha would empty the scope diff. Proposed by the solo; decided: maintainer conductor, 2026-10-15.
