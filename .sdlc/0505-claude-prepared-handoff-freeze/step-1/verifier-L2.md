<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 Real prepare denies the edit with no hand-made marker, record releases it: pass. Evidence: ran the criterion's command verbatim in the tree with SDLC_BASE_SHA exported, exit 0. The check bites: the builder's baseline probe and the criterion 3 run over the base plugin show no marker after the base `prepare`, so the `grep -qF "handoff freeze: handoff"` leg goes red there.
- #2 Warn mode warns and logs for a real prepared attempt: pass. Evidence: ran the command verbatim, exit 0 (stderr held `handoff freeze (warning)` and `stale-edits.log` held `edited while scout-L1 ran`).
- #3 New hook suite fails on the base plugin at the prepared-attempt case: pass. Evidence: git-archive of `fdd2254a` plus the new `hook-selftest.sh`; output `hook selftest: FAIL: handoff-edit prepared attempt warn: stderr lacks the freeze warning (prepare left no running marker)`; the grep leg exits 0.
- #4 dispatch selftest labels and PASS: pass. Evidence: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` printed `dispatch selftest: PASS` and all six `ok: <label>` lines (checked one by one with `grep -qF`; 439 `ok` lines). Negative controls I ran on a copy of the plugin under the tmp prefix: (a) making `recover_orphans` keep the marker gave 438 `ok` lines and `FAIL: recover removes the running marker of a dead-parent attempt (T-0505)`, and the hook suite failed with `handoff-edit prepared attempt recovered: the handoff stayed frozen after recover (rc=2)`; (b) moving the marker write above the dry-run return crashed the dispatch selftest (`FileNotFoundError` at line 1791), so the dry-run placement is exercised.
- #5 T-0505 in both reference docs: pass. Evidence: `grep -qF T-0505` on `docs/references/claude-hooks.md` and `docs/references/sdlc-internals.md`, both found; the diff shows the writer/clearer text and the `run_lifecycle.py recover` operator override sentence in sdlc-internals.md (grep count 1 for "operator override").
- #6 Report line and README index: pass. Evidence: the `^Live fresh-Claude check: unverified` line exists in `docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md`; the baseline FAIL line, post-change results, and the recipe are present; `docs/README.md` has the index line; the command exits 0.
- #7 (guard) hook-selftest.sh: pass. Evidence: exit 0, `hook selftest: PASS`. Bites per the #3 base run and the recover mutation above.
- #8 (guard) lifecycle-selftest.py: pass. Evidence: exit 0.
- #9 (guard) board.py selftest: pass. Evidence: exit 0, `board selftest: PASS`.
- #10 (guard) fleet_status.py selftest: pass. Evidence: exit 0, `fleet_status selftest: ok`.
- #11 (guard) scope check against SDLC_BASE_SHA: pass. Evidence: exit 0; changed non-.sdlc files are only dispatch.py, hook-selftest.sh, the two reference docs, docs/README.md, and the new report.
- #12 (guard) `git diff --check`: pass. Evidence: exit 0.
- docs_check.py: `0 errors, 30 warnings`, as the handoff requires.

## Out of scope changes
None. `warn-handoff-edit.sh`, `close()`, `recover_orphans`, `run_lifecycle.py`, and `run.sh` are untouched (git status shows only the listed files).

## For the next attempt
None

## Notes
- plugins/sdlc-lite/scripts/dispatch.py (the selftest line `case('attempt record: running, subagent transport, parent pid',(att[...`): the builder removed the space after the comma on an unrelated line; cosmetic.
- plugins/sdlc-lite/scripts/dispatch.py selftest label `prepare --dry-run writes no running marker (T-0505)` is green at the base too (a dry run wrote nothing before), so it only guards the placement; the builder disclosed this.
- Steelman: I considered failing for the weak dry-run label; the handoff prescribes the label and my placement mutation (moving the marker write above the dry-run return) broke the selftest, so the finding was dropped.
- The tmp worktrees/copies were removed; criterion 6 of the ticket (a fresh-Claude run) stays `unverified` in the report, as the handoff directs, for the conductor to carry to close-out.
