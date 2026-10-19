---
id: T-0578
title: "dispatch.py prepare --tree records a stale base for lane trees"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare` for a role working in a lane tree records the lane's real base: the lane HEAD, or the merge-base with the default branch for a verifier. A conductor never has to hand-write `<step>/base-sha`.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 4. maison wrote `<step>/base-sha` by hand all session (their `notes.md` 2026-10-14 16:08) because `prepare --tree` picked a stale base. `Base sha:` in a verifier brief is the diff-scope anchor, and T-0559 already takes the Outcome base from the solo dispatch's `base_sha`.

## Intent
- Do: find where `prepare` derives the base for `--tree` (or the brief's `Tree:`) and take it from that tree's HEAD for build roles, and from the build's recorded base (else the merge-base with the default branch) for a verifier.
- Non-goals: changing the main-checkout case.
- Done when: the criteria pass.

## Constraints
A recorded `base-sha` still wins when present.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0. Its new case covers a lane tree whose HEAD is ahead of the main checkout's HEAD: `prepare --tree <lane>` records the lane's base, not main's. The case failed before the change.
2. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: 5b5f37a91fc3
- Changed: prepare ignores a solo base recorded in another tree; lane trees get the lane head or start
- Commits: 04a9201 T-0578: prepare ignores a solo base recorded in another tree; lane base from the lane
- Check: 1 `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 with a new lane-ahead-of-main ca...: pass
- Check: 2 `git diff --check` exits 0: pass
