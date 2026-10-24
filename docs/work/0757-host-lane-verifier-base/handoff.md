---
id: T-0757
title: "The verifier of a host lane diffs against the commit the host cut the worktree from"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
For a host-worktree lane, `dispatch.py advance` gives the ticket verifier a Base sha equal to the commit the host worktree actually started from (the fork point of the host branch), and land/the brief agree, so the verifier diff holds only the ticket's change.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/dispatch.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: the T-0003 verifier got `Base sha: 1e7dd6d...` (origin/main, the host cut point) while prep's base was 26b7276, so its diff included T-0001's already-landed change; the T-0735 base-sha line was present but named the wrong commit. Coordinate with the host-solo-no-git-sync ticket (whichever lands second merges the first).

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `dispatch.py` selftest case: advance on a host lane cut from an older commit than prep's base gives a Base sha whose diff to the lane HEAD holds only the lane's commit; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
