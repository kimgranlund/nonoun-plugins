---
id: T-0381
title: "Native runner accepts a valid ancestor that is the wrong lane base"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A native runner request carries the lane's real merge-base even when a valid but wrong ancestor is stored or supplied, in the shape maison uses: handoff in MAIN, owned lane worktree as the execution cwd.

## Intent
- Do: scripts/run.sh (about lines 410 to 456) unsets a supplied SDLC_BASE_SHA, accepts a stored ancestor as valid, and runs `git -C <handoff dir>`. Make the base the merge-base of the execution tree (the lane worktree) with the recorded integration or named base, refuse a stored value that is an ancestor but not that merge-base unless the handoff names it explicitly, and print the chosen base and why. T-0376 (0.22.0) wrote the base from the lane merge-base for dispatch and steps; this ticket covers the run.sh and Codex native request path that still resolves in the handoff's tree. Do not call it fixed until the discriminating rerun below passes.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - Discriminating rerun (observed failing first): handoff in a MAIN checkout, lane worktree on a different commit, a supplied base; the request base equals the lane merge-base. Cases from the ledger row 6: T-0152 step 3 rework chose fe2b6bc90 instead of the explicit 2b2abee2c; T-0295 amendment request carried da6e1f2 though the handoff names 4022eee64 and the delta starts at 36588cdb.
  - A shared handoff in MAIN with the lane as cwd keeps the right base for steps.py, dispatch.py and run.sh alike.
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Maison recurrences of its T-0289 (T-0152 step 3 and the T-0295 amendment), and Codex's read-only 0.22.0 audit: run.sh lines 430 to 456 still unset the supplied SDLC_BASE_SHA and run git in the handoff dir. Related: T-0376 (shipped), T-0366. Source: the maison conductor's delivery check of 2026-10-08 (13 unread messages in the maison repo, .sdlc/messages/new/sdlc-lite-author/; RCA ledger /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/rca-ledger-2026-10-08.md). The user's RCA directive there: fix at the origin; workarounds retire only after an installed proof and a live discriminating rerun.

## Constraints
No em or en dashes. No push or publish. Codex host behavior cannot be run live here; mark it unverified.

## Acceptance criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh 2>&1 | tail -1 | grep -qx 'run selftest: PASS'`
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1 | grep -c '^ok: a main-checkout handoff run from the lane' | grep -qx 2`
- `grep -q 'base shared handoff, lane prerequisite' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'SDLC_BASE_SHA refused' plugins/sdlc-lite/scripts/run.sh`
- `python3 plugins/sdlc-lite/scripts/check.py && python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- Codex host behavior is unverified live; the Codex native request path reaches the same run.sh base block.
