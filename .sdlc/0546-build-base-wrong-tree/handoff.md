---
id: T-0546
title: "Build base taken from the wrong tree: solo_run --cwd and resumed lanes record a base that is not the build's start"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0540]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every prepared role records the base sha and Tree of the tree it actually builds or verifies in.

## Intent
- Do: `solo_run.py run --cwd <tree>` without `--exec` prints a dispatch prompt with no `Tree:` line and takes `base_sha` from the session checkout instead of `<tree>`'s HEAD. Make it use `<tree>` for both.
- Do: a lane resumed after its driver died (no `base-sha` recorded) gets `HEAD` of the lane, which is the driver's own WIP commit, so a verifier sees an empty diff. Take the base from the lane's recorded start (the integration branch point, or the fanout record) instead, or refuse with a message naming the right sha.
- Non-goals: other prompt fields.
- Done when: `solo_run.py selftest` and `dispatch.py selftest` pass with a case for each (base and Tree from `--cwd`; base for a resumed lane equals its start, not its WIP commit) and a negative control each.

## Context
- maison report 2026-10-13: `solo_run.py run --cwd <tree>` printed base_sha 29822d8e0 (session checkout) instead of 0ed758a3e (the tree's HEAD) and no Tree line; corrected by message.
- Seen here 2026-10-14: after the weekly-limit stop, `dispatch.py prepare verifier` in `.worktrees/fanout67/s` and `/b` printed the WIP commit (3fdfbfe6, d382acb9) as Base sha; the maintainer passed the start commit 3509ed11 by hand.
- Depends on T-0540 because the records dir moves `base-sha`.

## Constraints
Preserve the recorded build baseline (`SDLC_BASE_SHA`). A check must be able to fail.
