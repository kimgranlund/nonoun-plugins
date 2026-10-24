---
id: T-0762
title: "settle does not count a removed host lane as open"
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
After a host-owned lane landed and its worktree was removed (by the `git worktree remove` line settle printed), its host lane record no longer holds the integration tree open, and settle prints a remove line for every landed host worktree.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/lanes.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: round 2 `settle --forward` fast-forwarded main but exited 1: `lane still open: .../live036.worktrees/fanout/integration (lanes still open into fanout/rehearsal: agent-a82fa7f9f67d4ffd8)`; that worktree was already removed, but `live036.worktrees/host/agent-a82fa7f9f67d4ffd8.lane.json` was left behind. No remove line was printed for the landed T-0002 host worktree.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `lanes.py` or `fanout.py` selftest case: a host lane record whose worktree no longer exists does not block the integration close, and settle prints a remove line for each landed host worktree still present; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Cause: the integration close (row 4) counted a host record whose `.claude/worktrees/<leaf>` tree was removed but whose branch still existed, so round 2 settle refused; the refusal returned before the T-0743 remove lines were printed, which is why T-0002's line was missing.
- Fix: `plugins/sdlc-lite/scripts/lanes.py` `evaluate` skips a host record with no tree whose branch is an ancestor of the integration branch; the truth table row 4 note says so. The record stays for sweep or `dispatch.py prune --done`. T-0743 behavior unchanged.
- Test: selftest case `host removed` (`case_host_removed_integration`): landed agent-x tree present plus landed agent-z whose tree was removed; close exits 0, removes the integration tree, prints agent-x's remove line and no agent-z line.
- Negative control (fix lines reverted, test kept): selftest rc 1, `FAIL: host removed: host removed: want the integration tree closed, 'host-owned .../hostgone-56/repo/.claude/worktrees/agent-x landed in wave/1; remove it yourself: git worktree remove .../agent-x' and no agent-z line, got 1: lanes still open into wave/1: agent-z`.
- Checks: `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 12f046a9` exit 0.
