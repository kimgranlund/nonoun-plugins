<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- Ticket acceptance criterion 6 is unverified. No fresh-Claude run observed the handoff guard during a prepared role and its release after recording. The report at `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/a/docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md` says `Live fresh-Claude check: unverified` and gives the recipe for a later live run.
- The full suite (`check.sh` and `check.py`) was not run. The `fanout.py land` gates for lane `fanout/wave54-a` own it.
- Step 1 passed: the verifier verdict is pass on all 12 criteria, and `docs_check.py` printed `0 errors, 30 warnings`.
- No `process-deviations.md` exists in the artifacts dir or its step folders.

## PR title
T-0505: bug: Claude hooks: freeze handoffs during prepared attempts

## PR body
### Summary
Handoff edit protection now covers sub-agent attempts started with `dispatch.py prepare`. Before this change, `prepare` created a running attempt but no `<role>-<level>.running` marker. `warn-handoff-edit.sh` reads only that marker, so a deny-mode edit exited 0 during a live prepared attempt. Now `prepare` writes the marker. The existing clear paths (`record` on completed or failed, `dispatch.py recover`, `run_lifecycle.py recover`) remove it. Fixes review finding F3 from the Astra review.

### Changes
- `plugins/sdlc-lite/scripts/dispatch.py`: `prepare` writes `<role>-<level>.running` (epoch seconds plus newline) under the directory lock, after the attempt and dispatch records.
  - `--dry-run` and refused prepares write no marker.
  - The module docstring is updated.
  - The selftest gains six T-0505 cases.
  - The case `a dead-parent attempt is recovered first` now expects the retry's own marker.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: prepared-attempt cases using real `dispatch.py prepare`, with no hand-made markers. They cover warn, deny, completed, failed, recovered, and a live attempt owned by another run.
- `docs/references/claude-hooks.md` and `docs/references/sdlc-internals.md`: who writes and who clears the marker. `run_lifecycle.py recover` stays the operator override. Both cite T-0505.
- `docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md` (new) and one index line in `docs/README.md`.
- `warn-handoff-edit.sh`, `close()`, `recover_orphans`, `run_lifecycle.py`, and `run.sh` are unchanged. The immutable Astra report is untouched.

### Verification
- Deny after a real prepare and silent after record: the criterion command exits 0. The verifier reran it verbatim. Before the change the same recipe left no marker and the hook exited 0.
- Warn mode warns and logs `edited while scout-L1 ran`: exit 0.
- The new hook suite run over the base plugin (`git archive` of `fdd2254a`) fails with `hook selftest: FAIL: handoff-edit prepared attempt warn: stderr lacks the freeze warning (prepare left no running marker)`. On this tree it passes.
- `dispatch.py selftest` prints `dispatch selftest: PASS` and all six T-0505 `ok:` labels.
- Builder negative control: with the marker write replaced by `pass`, the selftest fails six cases.
- Verifier mutations:
  - Keeping the marker in `recover_orphans` failed the recover selftest case and the hook suite's recovered case.
  - Moving the marker write above the dry-run return crashed the selftest.
- Guards pass: `hook-selftest.sh`, `lifecycle-selftest.py`, `board.py selftest`, `fleet_status.py selftest`, the scope check, and `git diff --check`.
- Not run: `check.sh` and `check.py`. The `fanout.py land` gates own them.
- Not verified: a fresh-Claude run (ticket criterion 6).

### Known limit
The marker is keyed by role and level. Two running attempts of the same role and level in one folder share one marker, and the first to close removes it. That needs two attempts owned by the same session.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Claude hooks: `dispatch.py prepare` now writes the `<role>-<level>.running` marker, so handoff warn and deny modes apply during prepared sub-agent attempts. Completion, failure, and recovery release it (T-0505).

## Follow-ups
- decide: Run a live fresh-Claude check on this tree's plugin and record it as `observed` in a new dated report. Ticket criterion 6 is open, and the builder's headless sub-agent loaded the main checkout's plugin, not this tree's.
- note: The marker is keyed by role and level, not by attempt stem. Recording one of two same-role, same-level attempts of one session drops the marker while the other still runs (the T-0371 skip). A standing marker from an unrecorded attempt stays until `dispatch.py recover` or `run_lifecycle.py recover` runs.
- note: The selftest label `prepare --dry-run writes no running marker (T-0505)` also passes on the base. It guards only the placement of the marker write.
