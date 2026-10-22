---
id: T-0748
title: "A re-verify after a lane merges main keeps the ticket's build base"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
When a lane has merged main after its first verifier attempt and its handoff names no `base:`, a second `dispatch.py prepare verifier` gives a Base sha whose diff to HEAD holds the whole ticket's own changes and nothing from main: never HEAD itself (an empty diff) and never the merge commit (which drops the first pass).

## Intent
- Do: in `plugins/sdlc-lite/scripts/dispatch.py` (`build_base`, the base-sha write in prepare about line 1300, and the T-0717 lane-copy base-sha read), find why the base moves to HEAD and then to the lane's merge commit, and resolve the default to the lane's merge point with the target (`git merge-base HEAD <target>`) when the lane start is no longer below the fork floor. Keep T-0717 (a named `base:` wins) and T-0745 (a recorded lane start is quiet).
- Non-goals: other base sources.
- Done when: the criteria pass.

## Context
Observed 2026-10-22 on lane T-0745-t0745 (lanes.py open, `.lane.json` base_sha aebe6d47): verifier attempt 1 got Base sha aebe6d47. The solo then merged main (merge commit a9d0ac33) and fixed. `prepare` for attempt 2 printed `Base sha: 5c8b07b3...` = the review sha (HEAD) and wrote it to `<records>/base-sha`; with base-sha set by hand to the main merge point 34a12178, attempt 3 printed `Base sha: a9d0ac33` (the merge commit), whose diff omits the first pass cb92e235. A verifier diffing against either base would review the wrong scope.

## Acceptance criteria
1. A `dispatch.py` selftest case: lane with a recorded start, a verifier attempt, then a main merge and a fix commit; the next verifier prepare's Base sha diff to HEAD contains both lane commits and no main-only change; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
