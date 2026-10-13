<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/plugins/sdlc-lite/scripts/dispatch.py`: `prepare` writes `<role>-<level>.running` (epoch seconds plus newline) after the two records, under the directory lock. The module docstring `Records.` paragraph is updated. The selftest gains the six T-0505 cases, and the existing case `a dead-parent attempt is recovered first` now expects the retry's own marker.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/plugins/sdlc-lite/scripts/hook-selftest.sh`: prepared-attempt cases after the `warn-handoff-edit.sh` block (warn, deny, completed, failed, recovered, live attempt of another run), plus the header comment.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/docs/references/claude-hooks.md`: who writes and who clears the marker, citing T-0505.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/docs/references/sdlc-internals.md`: the same fact in the `dispatch.py prepare` and `dispatch.py record` paragraphs, including `run_lifecycle.py recover` as the operator override.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md`: new report with the baseline FAIL line, the results after the change, the negative control, and `Live fresh-Claude check: unverified` with reason and recipe.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/docs/README.md`: one index line for the report.

## Checks
`SDLC_BASE_SHA=fdd2254adf96a392673a176aef687fd4a688adef` was exported by hand for criteria 3 and the two base-sha guards.
- Criterion 1 (deny after a real prepare, silent after record): exit 0. Before any edit the same recipe gave prepare exit 0, no marker, hook exit 0.
- Criterion 2 (warn and log after a real prepare): exit 0.
- Criterion 3 (new hook suite over the base plugin): exit 0. The suite exited 1 with `hook selftest: FAIL: handoff-edit prepared attempt warn: stderr lacks the freeze warning (prepare left no running marker)`.
- Criterion 4: `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exited 0 with `dispatch selftest: PASS` and all six `ok: <label>` lines. The criterion's greps were applied to that run's saved output (exit 0), not by a second selftest run.
- Criterion 5 (`T-0505` in both reference docs): exit 0.
- Criterion 6 (report line and README entry): exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0, `hook selftest: PASS`.
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`: exit 0, `board selftest: PASS`.
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest`: exit 0, `fleet_status selftest: ok`.
- (guard) scope `test -z ...`: exit 0.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0.
- `python3 plugins/sdlc-lite/scripts/docs_check.py`: `0 errors, 30 warnings`.
- Negative control: with the marker write replaced by `pass`, the dispatch selftest exited 1 with six `FAIL:` lines. Five are T-0505 labels and the sixth is `a dead-parent attempt is recovered first`. The write was restored before the passing run.

## Notes
- The ticket's acceptance criterion 6 (a fresh-Claude live run) is not proven. The report says `unverified` as the handoff directs, and the conductor carries it to close-out.
- The existing case `a dead-parent attempt is recovered first` used to assert that no `builder-L1.running` existed after the recover-then-prepare. The retry `builder-L1-2` now writes that same marker name, so the case asserts the hand-written `1` is gone and an epoch start is there. It fails in the negative control, so it was not weakened.
- The label `prepare --dry-run writes no running marker (T-0505)` stays green in the negative control, because a dry run wrote nothing at the base either.
- For `recover keeps a live attempt of another run`, the selftest uses `os.getppid()` as the foreign owner. The selftest's own pid would not work: an attempt carrying the caller's pid does not block the next prepare (T-0371).
- Known limit, recorded in the report: the marker is keyed by role and level. Two running attempts of the same role and level in one folder share one marker, and the first to close removes it. That needs two attempts owned by the same session.
- `check.sh` and `check.py` were not run. The handoff leaves the full suite to the `fanout.py land` gates.
- Nothing was committed, and no throwaway worktree was created.
