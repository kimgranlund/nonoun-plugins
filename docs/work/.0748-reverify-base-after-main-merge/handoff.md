---
id: T-0748
title: "A re-verify after a lane merges main keeps the ticket's build base"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
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

## Outcome
Reproduced in a throwaway repo (lane with `.lane.json`, first pass, verifier, main merge, fix): attempt 2 and 3 got HEAD (empty diff). Two causes in `build_base` (`plugins/sdlc-lite/scripts/dispatch.py`):
- Attempt 1 writes the lane start to `base-sha`. After the main merge the fork floor moves past it, so the stored base is rejected, and the lane-start fallback was gated on `not stored`, so the verifier fell to HEAD.
- With the merge point stored (the incident's hand-set 34a12178), the resync-merge rule moved the base to the merge commit, dropping the first pass.

Fix: a verifier whose stored base is below the floor falls to the lane start too; a lane start below the floor is clamped to the floor (`git merge-base HEAD <main>`, with a one-line note); the resync-merge move is skipped when the stored base is the floor itself. A named `base:` still wins (T-0717 cases green). Builders are unchanged.

T-0745 landed on main during this ticket; the lane merged main (70772dfc). The clamp sits after `lane_start` (which now calls T-0745's `lane_record_base`), so a fanout or host record stays quiet, and its base is clamped to the merge point when the lane has merged main since. Two T-0745 cases and the T-0376 verifier/builder case asserted the old base (start3, or HEAD for a verifier); they now expect the merge point and the fork point.

Checks:
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0
- `git diff --check 2de1b84a` exit 0 (and against the merge point 6885c68b)
- Negative control (fix reverted in a scratch copy): `FAIL: a verifier after the lane merged main (attempt 2): the base diff holds both lane commits and no main-only file` and the same for attempt 3; reverting only the resync guard fails attempt 3 alone.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (sonnet) · base: 6885c68b458a
- Changed: see commits
- Commits: 89c45bf T-0748: a re-verify after a lane merges main keeps the ticket's build base
- Check: 1 selftest case: lane with recorded start, verifier attempt, main merge, fix commit; next prepare's...: pass
- Check: 2 selftest exit 0, check.py exit 0, check-packaging passes, `git diff --check` exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:3251: the changed T-0376 case... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:3396 and :3404: the two... -> notes.md
- Follow-up: decide: T-0717: no named-base: case was touched, and all of them are green... -> notes.md
