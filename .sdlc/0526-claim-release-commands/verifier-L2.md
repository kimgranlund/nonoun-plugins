<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 selftest exits 0 and holds the Done-when cases: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed "tickets selftest: PASS", exit 0. The selftest block in the diff (tickets.py, "claim and release" section) has cases for: claimed_by directly after `created:` plus roadmap regenerated; a trailing comment warns naming `alpha` while the same claim without it does not (`'alpha' not in out`); a 10-day-old claim with no running attempt is listed while the same claim beside `step-1/builder-L2.running` is not; `new` succeeds beside a ticket with status claimed and claimed_by.
- #2 each new case bites: pass. Evidence: ran the unmutated copy of the plugin scripts in a temp dir outside git (selftest rc=0), then seven single-edit mutants, each making selftest exit 1 on a named claim case: lint-off (`out += claim_warnings` removed) failed "a trailing comment ... warns" and "a claim line out of place warns"; running-exempt-off (`and True`) failed "the same claim beside a running attempt is not listed"; placement (extra line before claimed_by) failed "claimed_by goes directly after created:"; roadmap-skip (write_roadmap removed from write_claim) failed the claim and release roadmap cases; handover-line (body line text changed) and handover-replace (`if False:`) failed "claim --handover replaces the value and appends one dated body line"; comment-off failed the trailing-comment case. A git worktree could not be created (the hook reports SDLC_TMP_WORKTREES unset), so the control was a temp-dir copy; the mutants were applied to that copy only.
- #3 `tickets.py --root .sdlc check` exits 0: pass. Evidence: ran it, exit 0, "ok: 525 tickets, roadmap current" (only the existing closed-ticket placeholder and flat-layout warnings follow). The `.sdlc/AGENTS.md` block diff matches the new `ROUTER_PROCEDURES` text.
- #4 router "Claim a ticket" and SKILL.md describe claim, `--handover --reason`, release, `claim_days:`; a refused `new` names the ticket and a one-line fix: pass. Evidence: diff of `ROUTER_PROCEDURES` (steps 2 and 4) and `.sdlc/AGENTS.md`; SKILL.md argument hint, table rows (`<id>`, `--by`, `--handover`, `--reason`) and the router rule line naming `claim_days:` (default 7). The `new` refusal line now reads "beta: status claimed needs a non-empty claimed_by ...; fix: run tickets.py claim T-0002 --by <agent>, or set status: ready"; the selftest case "new refusing on a ticket problem names the ticket and the one-line fix" passed in the run above.
- #5 `git diff --check` exits 0: pass. Evidence: ran it, no output, exit 0.

## Out of scope changes
None. The diff touches only `plugins/sdlc-lite/scripts/tickets.py`, `plugins/sdlc-lite/skills/ticket/SKILL.md`, the regenerated `.sdlc/AGENTS.md` router, and this ticket's `handoff.md` (acceptance criteria added) and run artifacts. Contract dependents: the router text is regenerated and checked by `check` (exit 0); new subcommands add to the CLI without changing existing outputs.

## For the next attempt
None.

## Notes
- Steelman on a possible fail ("`claim` leaves a body-line change in the handover only when the roadmap is current"): dropped, since the handover case asserts the exact line count (+2) and the exact line text, and the mutants against it went red.
