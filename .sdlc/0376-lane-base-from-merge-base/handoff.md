---
id: T-0376
title: "The lane base sha is the lane's merge-base at dispatch, not the main checkout HEAD"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The base sha recorded for a lane is the lane worktree's merge-base at dispatch, not the main checkout HEAD, so a scope-guard `git diff $SDLC_BASE_SHA` lists only the lane's changes.

## Intent
- Do: Find where the runner and step-N/base-sha write the base (scripts/steps.py, scripts/dispatch.py build_base, scripts/fanout.py lane creation) and make it the lane worktree's `git merge-base HEAD <integration or main>` at dispatch time. T-0366 (merged, unreleased) already makes `prepare verifier` read the pre-build sha recorded in a solo dispatch file; reuse it and check that the step-N/base-sha path agrees. Maison saw three stale bases (29822d8e0 and 4c6531dc9 where the lane forked from 44bb3fb63 or 0d7edbecf), so a guard listed 971 files until corrected by hand.
- Maison's three observed cases (2026-10-08): step-1/base-sha for T-0138 held 29822d8e0 while the lane forked from 44bb3fb63 (r3a-integration), so `git diff --name-only "$SDLC_BASE_SHA"` listed 971 files and the allow-list guard could not pass; a Codex native request emitted SDLC_BASE_SHA=4c6531dc9 (a mid-integration commit) for the same lane; the T-0152 step 1 verifier saw 29822d8e0 for a lane built on 4022eee64. Common cause per maison: base-sha is written from the main checkout HEAD at split time, not from the lane tree. Wanted: `dispatch.py prepare` writes `<step>/base-sha` from `git merge-base HEAD <main or the named base>` in the lane worktree it is given (the Tree: line), and refuses when the recorded one is not an ancestor of the lane tip. The Codex native request path (SDLC_BASE_SHA in its request) needs the same source.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A selftest: a lane forked from a commit older than main HEAD records its fork point as the base; the scope-guard diff lists only the lane's files (observed failing first).
  - Interaction with T-0366 checked: prepare verifier and step-N/base-sha print the same sha for the same lane.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Evidence in the maison repo's notes; maison corrected the base by hand three times in one session. Source: feedback from the maison conductor, 2026-10-08 (about 30 lanes across Claude and Codex, 3 bases, 2 peer repos); its specifics are in the maison repo's .sdlc/notes.md and handoffs. Maison ran plugin 0.21.2; check each claim against 0.21.3 and main before building.

## Constraints
No em or en dashes. No push or publish.
