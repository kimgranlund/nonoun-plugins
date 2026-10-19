---
id: T-0381
title: "Native runner accepts a valid ancestor that is the wrong lane base"
type: bug             # feature | bug | chore | spike | idea
status: dropped      # dropped by the maintainer 2026-10-12: Claude path covered by T-0376 and T-0413; Codex run.sh path not rechecked
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
- Replan (the one allowed, 2026-10-08), from the lane verifier of the first attempt (branch wave6-runbase, wip commit 25a9c569; start by merging that branch into your tree, it holds the run-selftest cases and the refusal message). Decision on the open design question (T-0376's build-start rule versus the merge-base rule): the base of a step is, in this order, (1) a base the handoff names explicitly, else (2) the sha recorded at the step's first dispatch (the execution tree's HEAD at build start, as T-0376 records it), and never the MAIN checkout's HEAD. A supplied or stored value that is a valid ancestor but differs from the one the order selects is refused with `SDLC_BASE_SHA refused: ...` (use that exact literal prefix in both run.sh and dispatch.py), unless the handoff names it. A rework of a step keeps the original recorded base, so prerequisites are not counted as new work (the T-0152 step 3 case: explicit 2b2abee2c, not fe2b6bc90). Implement the order in run.sh (about lines 466 to 485), dispatch.py build_base and steps.py (base_sha and git_toplevel near line 686, which resolve from the step dir in MAIN and fall back to MAIN's HEAD: run git in the execution tree or check the recorded base). Required selftests (red before): handoff in MAIN, lane with commits after the fork, wrong but valid supplied base -> refused, correct base kept; a handoff-named base wins; a rework keeps its original base; the same shape for steps.py. The first attempt's criterion 3 grep needs the literal `SDLC_BASE_SHA refused`.
- Two more required cases from the maison conductor (2026-10-08), added after the second attempt started: (a) a legitimate re-base: a base the handoff names explicitly with a scope-decision line wins over the base stored at an earlier dispatch of the same ticket (maison T-0152 steps 5 to 8 were dispatched from an explicit combined base f9f95d476, then the step 5 tip 0c7ef5500 for step 8), and the `SDLC_BASE_SHA refused` message says why when it does not win; (b) a verifier dispatch for a lane reads the builder's recorded base, not the verifier's own tree HEAD, and a verifier in a throwaway worktree is not refused. The independent L3 rerun checks these; if the second attempt misses either, file a follow-up ticket rather than a second replan.
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
verifier: L3

Design reading: the Replan paragraph of the Intent settled the open question for the build-start rule, so the base of a step is the order named base, then recorded base, then HEAD of the execution tree (never the main checkout's HEAD). The Goal and Done-when wording "equals the lane merge-base" predates it; the two ledger cases (T-0152 step 3, T-0295) are met through the handoff-named base. A step handoff names its base with a line `base: <sha>`.

- `bash plugins/sdlc-lite/scripts/run-selftest.sh 2>&1 | tail -1 | grep -qx 'run selftest: PASS'`
- `python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1 | grep -c '^ok: a main-checkout handoff run from the lane' | grep -qx 8`
- `python3 plugins/sdlc-lite/scripts/steps.py selftest 2>&1 | grep -c '^ok: shared step dir (T-0381)' | grep -qx 5`
- `grep -q 'base shared handoff, wrong supplied base' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'SDLC_BASE_SHA refused' plugins/sdlc-lite/scripts/run.sh && grep -q 'SDLC_BASE_SHA refused' plugins/sdlc-lite/scripts/dispatch.py && grep -q 'SDLC_BASE_SHA refused' plugins/sdlc-lite/scripts/steps.py`
- `python3 plugins/sdlc-lite/scripts/check.py && python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`
- Codex host behavior is unverified live; the Codex native request path reaches the same run.sh base block.
