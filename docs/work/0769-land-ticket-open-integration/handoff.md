---
id: T-0769
title: "land reads the ticket status where it closed it"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #77 reports no longer happens (title: land reads the ticket status where it closed it).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/lanes.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #77 (quoted):

> **Observed:** every land into an integration branch that auto-closed its ticket (integration commit `close T-NNNN`) still ended with `ticket still open: T-NNNN`.
>
> **Root cause:** `scripts/lanes.py:972-975` reads ticket status through `local_tickets(top)` (`lanes.py:908`), i.e. the main checkout; the close is committed on the integration branch, so main still reads open. Not #56.
>
> **Proposed fix:** read status from the worktree of the branch the lane landed into, or skip ids already in `done` from `clear_integration_record`.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `lanes.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Reproduced on main (ff181d81): the new `lanes.py` selftest case `close done in integration` failed with `FAIL: close done in integration: close done in integration: T-0001 is done in wave/1 but close reported it open: 0: closed T-0001-one (ancestor) ... ticket still open: T-0001` before the fix (that run is the reverted state: the case was added first, the code unchanged). `do_close` now resolves `wtroot.owner_tree('ticket-close', None, <lane path>)` before the lane tree is removed and reads status through `close_tree` (the integration tree holding `into`, else main; main for a ticket that tree lacks). Docs: the lanes.py header, the `ticket-close` row of `docs/references/sdlc-internals.md` and `wtroot.OWNERS`. Checks: lanes.py selftest exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `wtroot.py owner-selftest` ok.
