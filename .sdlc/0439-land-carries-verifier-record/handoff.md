---
id: T-0439
title: "Fanout land carries the verifier result for every verified step, then one more rehearsal plan runs to plan done"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan run closes a verified step with no hand step to carry the verifier record onto the lane branch.

## Intent
- Do: make the verifier result reach the landed checkout for solo L1 `verify: required` and L2/L3 steps: either the run rules tell the driver to `git -C <sub-agent worktree> add -f -- <ticket folder>` and commit the record before `fanout.py land`, or `land` / `plan_done.py` reads it from the lane. Back it with a `fanout.py` or `plan_done.py` selftest that fails before and passes after (observed red).
- Non-goals: the other T-0438 items (verified).
- Done when: the selftest case; `check.sh` exits 0. A separate rehearsal plan run is the maintainer's live check, not a verifier criterion.

## Context
Verifier result with the finding: `.sdlc/.0438-executor-live-run-fixes/verifier-L2.md` (criterion 3). `land_ticket` is fanout.py:1825-1842; `SOLO_VERIFIED` is fanout.py:350; run-rules line 37.

## Constraints
No push, tag or publish. Smallest change.
