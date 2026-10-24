---
id: T-0756
title: "A host-worktree solo brief asks for no git sync"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The solo brief `fanout.py prep` writes for a host worktree asks for no git command at all (the host sandbox refuses every git command and compound or quoted shell lines in that worktree), and the ticket stays reachable: either prep refuses when the base sha is not on the remote default branch the host cuts worktrees from, or land merges the base itself, so a solo never needs `git merge --ff-only <base>`.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: the brief line `before anything else run git merge --ff-only <base sha> in your worktree so the ticket folder is visible` (fanout.py SOLO_SYNC); all three solos reported it refused ("The host worktree guard refused every git command and any compound shell line", "refused any command containing a quoted string"). The host cut every worktree from origin/main 1e7dd6d while prep's base was the unpushed local main 304126d, then 26b7276.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case: prep for a host lane whose base is not reachable from the remote default branch refuses (exit 2) naming the push to make, or the brief carries no git command and land merges the base; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
