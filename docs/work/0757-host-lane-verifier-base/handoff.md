---
id: T-0757
title: "The verifier of a host lane diffs against the commit the host cut the worktree from"
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

## Outcome
- `plugins/sdlc-lite/scripts/dispatch.py`: new `host_fork(tree)`; in a host worktree (`<main checkout>/.claude/worktrees/<leaf>`) it returns the merge base of HEAD with the remote default branch (`fanout.remote_default`, the branch the host cuts from). `build_base` gives a verifier with nothing named that cut point before the recorded solo base or the lane start, so `dispatch.py advance` on a prep solo diffs only the lane's change, whether the host cut is older or newer than prep's base.
- Selftest: two `T-0757 advance on a host lane ...` cases (cut from an older commit than prep's base, the rehearsal shape; cut from origin ahead of prep's base, the T-0756 shape). Before the fix both failed: `FAIL: T-0757 advance on a host lane cut from an older commit than prep's base: ... (got 709af474c314, diff '')` (the lane HEAD, an empty diff) and `FAIL: T-0757 advance on a host lane cut from origin ahead of prep's base: ... (got d47eaae608f2, diff 'ahead.txt\nlane.txt')` (prep's base, origin's commit included).
- Docs: `skills/handoff-format/references/step-handoff-rules.md` names the host-worktree verifier base.
- Checks: `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0 (PASS); `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check 1c6715a9` exit 0.
- Open: the solo brief's `Base sha:` line still names prep's base (prep cannot know the host cut point before the spawn); land's `--base` pins the integration start, which is unaffected.
