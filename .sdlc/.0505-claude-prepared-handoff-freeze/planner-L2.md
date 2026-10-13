<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make `dispatch.py prepare` own the `<role>-<level>.running` marker so a live prepared attempt activates the handoff edit guard (warn and deny), and completion, failure, or recovery releases it.
guard timeout: 600

## Step 1: Prepare writes the running marker; prove the freeze lifecycle end to end
level: L3
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
### Do
Depends on: none.

Settled design: `prepare` owns the marker. The hook `plugins/sdlc-lite/hooks/warn-handoff-edit.sh` stays untouched and gets no second definition of "live".
- `record`'s `close()` (`plugins/sdlc-lite/scripts/dispatch.py:1128`), `recover_orphans` (`dispatch.py:497`), and `run_lifecycle.recover_unlocked` (`run_lifecycle.py:45-51`) already unlink `<role>-<level>.running`. Only `prepare` never writes it.
- Marker readers already pair a marker with a Claude attempt record: `board.py` `task_rows` and its selftest (lines 909-912), and `fleet_status.py` `inspect_markers`.

Implementation, in `plugins/sdlc-lite/scripts/dispatch.py`:
- In `prepare`, right after the two `run_lifecycle.write(...)` calls for the attempt and dispatch records (about line 848), still under the directory lock, write `directory / ('%s-%s.running' % (role, level))`.
- Name it by role and level, not by stem, because `close()` and both recover paths unlink by role and level.
- Content is the epoch start in whole seconds plus a newline, the same as `run.sh:639` (`date +%s`). `statusline.sh:49` does arithmetic on it and `fleet_status.py` `inspect_markers` parses 9 to 11 digits.
- `--dry-run` writes no marker. A refused prepare writes none, which the placement after the records already gives.
- Do not change `close()`, `recover_orphans`, `run_lifecycle.py`, or `run.sh`. A no-result record (T-0412, attempt stays running, exit 2) never calls `close()`, so its marker stays.
- Update the module docstring's Records paragraph to say prepare writes the marker and record and recover clear it.

Regression cases in the `dispatch.py` selftest. Use these exact labels, because criterion 4 greps them:
- `prepare writes the running marker with an epoch start (T-0505)`
- `prepare --dry-run writes no running marker (T-0505)`
- `a no-result record keeps the running marker (T-0505)`
- `record removes the running marker on completed and on failed (T-0505)`
- `recover removes the running marker of a dead-parent attempt (T-0505)`
- `recover keeps a live attempt of another run and its running marker (T-0505)`

The last label is acceptance criterion 3. It covers `recover_orphans` and prepare's `settle`: the attempt stays `running` with its `parent_pid` unchanged and the marker stays. The hand-written marker at `dispatch.py:2055` becomes redundant; remove it or leave it. Fix any existing selftest assertion that lists the files prepare writes (see the `iterdir` and `rglob` cases near lines 1640-1693 and 1995-1999).

Integration cases in `plugins/sdlc-lite/scripts/hook-selftest.sh`, next to the existing `warn-handoff-edit.sh` block (about line 589):
- Build a throwaway git repo with `.sdlc/task/handoff.md` and run the real `dispatch.py prepare scout L1`. The recipe is in `docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` lines 13-28. Strip `SDLC_*` from the environment as the suite already does. Never create a marker by hand in these cases.
- Pipe the Edit payload for that handoff through the hook and assert: warn mode exits 0 with the warning and one `stale-edits.log` line; deny mode exits 2.
- After `dispatch.py record` with a valid scout result on stdin, the hook is silent and exits 0. Repeat for a failed record.
- After `dispatch.py recover <dir>` on an attempt whose `parent_pid` was rewritten to a dead pid, the hook is silent. With a live `parent_pid` that is not the caller, recover leaves the guard active.
- The first deny assertion's `fail` text must start with `handoff-edit prepared attempt`, because criterion 3 greps `hook selftest: FAIL: handoff-edit prepared attempt` when the new suite runs against the base plugin.

Docs:
- `docs/references/claude-hooks.md`, section `hooks/warn-handoff-edit.sh`: say who writes the marker (`run.sh` for the legacy runner, `dispatch.py prepare` for sub-agent dispatch) and who clears it (record, `dispatch.py recover`, `run_lifecycle.py recover`). Cite T-0505.
- `docs/references/sdlc-internals.md`, the `dispatch.py prepare` and `record` paragraphs (lines 25-27): same fact, cite T-0505.
- Create `docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md` [creates: docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md]. It holds the baseline FAIL line from criterion 3's command, the passing runs, and one line that reads exactly `Live fresh-Claude check: observed` or `Live fresh-Claude check: unverified`, followed by the reason.
- Add one index line for the report to `docs/README.md` beside the other report entries.
- Do not edit `docs/reports/2026-10-12-sdlc-lite-astra-review.md` or its folder.

Acceptance criterion 6 (a fresh-Claude run) is not proven by this step. The installed plugin in a live session is not this tree, so the builder writes `unverified` unless it actually ran a fresh Claude session against this tree's plugin and saw the guard fire and release.

Contract dependents of the marker, found with `git grep -l '\.running' -- plugins docs/references docs/specs scripts`:
- `board.py` and `fleet_status.py` now see a marker for sub-agent dispatches. Their selftests are guards below.
- Left untouched on purpose, because they read any marker the same way: `statusline.sh`, `traces/detectors/escalation.py`, `traces/sources/attempts.py`.
- Left untouched on purpose, because they already exclude `*.running`: `fanout.py` `LANE_ADD`, `docs_check.py` `GENERATED_NAME`, and `.gitignore:6`.
- `check.py:865-876` reads the hook file, which does not change.

Validation scope: the criteria below. The whole `check.sh` suite belongs to the `fanout.py land` gates for lane `fanout/wave54-a`. At the reviewed baseline it was interrupted at the fanout selftest and carried an unrelated Progressive Context link failure the handoff says not to fix.

### Acceptance criteria
- `r=$(mktemp -d) && p="$PWD/plugins/sdlc-lite" && h="$r/.sdlc/task/handoff.md" && git -C "$r" init -q && git -C "$r" -c user.name=t -c user.email=t@example.invalid commit --allow-empty -qm seed && mkdir -p "$r/.sdlc/task" && printf "## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n" >"$h" && (cd "$r" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/scripts/dispatch.py" prepare scout L1 .sdlc/task/handoff.md >/dev/null) && printf "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"%s\"}}" "$h" | env -i PATH="$PATH" SDLC_HANDOFF_EDIT_MODE=deny bash "$p/hooks/warn-handoff-edit.sh" 2>&1 | grep -qF "handoff freeze: handoff" && (cd "$r" && printf "## Map\nNone\n\n## Entry points\nNone\n\n## Not found\nNone\n\n## Carry forward\nNone\n" | env -i PATH="$PATH" HOME="$HOME" python3 "$p/scripts/dispatch.py" record .sdlc/task/scout-L1.dispatch.json >/dev/null 2>&1) && test -z "$(printf "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"%s\"}}" "$h" | env -i PATH="$PATH" SDLC_HANDOFF_EDIT_MODE=deny bash "$p/hooks/warn-handoff-edit.sh" 2>&1)"` exits 0: a real prepared attempt denies the edit with no hand-made marker, and recording releases it.
- `r=$(mktemp -d) && p="$PWD/plugins/sdlc-lite" && h="$r/.sdlc/task/handoff.md" && git -C "$r" init -q && git -C "$r" -c user.name=t -c user.email=t@example.invalid commit --allow-empty -qm seed && mkdir -p "$r/.sdlc/task" && printf "## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n" >"$h" && (cd "$r" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/scripts/dispatch.py" prepare scout L1 .sdlc/task/handoff.md >/dev/null) && printf "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"%s\"}}" "$h" | env -i PATH="$PATH" bash "$p/hooks/warn-handoff-edit.sh" 2>&1 | grep -qF "handoff freeze (warning)" && grep -q "edited while scout-L1 ran" "$r/.sdlc/task/stale-edits.log"` exits 0: warn mode warns and logs for a real prepared attempt.
- `t=$(mktemp -d) && git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C "$t" && cp plugins/sdlc-lite/scripts/hook-selftest.sh "$t/plugins/sdlc-lite/scripts/hook-selftest.sh" && bash "$t/plugins/sdlc-lite/scripts/hook-selftest.sh" 2>&1 | grep -qF "hook selftest: FAIL: handoff-edit prepared attempt"` exits 0: the new hook suite fails on the base plugin at the prepared-attempt case.
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1); for l in "prepare writes the running marker with an epoch start (T-0505)" "prepare --dry-run writes no running marker (T-0505)" "a no-result record keeps the running marker (T-0505)" "record removes the running marker on completed and on failed (T-0505)" "recover removes the running marker of a dead-parent attempt (T-0505)" "recover keeps a live attempt of another run and its running marker (T-0505)"; do grep -qF "ok: $l" <<<"$out" || exit 1; done; grep -qF "dispatch selftest: PASS" <<<"$out"` exits 0.
- `for f in docs/references/claude-hooks.md docs/references/sdlc-internals.md; do grep -qF "T-0505" "$f" || exit 1; done` exits 0.
- `grep -qE "^Live fresh-Claude check: (observed|unverified)" docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md && grep -qF "2026-10-12-handoff-freeze-prepared-attempts.md" docs/README.md` exits 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fleet_status.py selftest`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/(dispatch\.py|hook-selftest\.sh)|docs/references/(claude-hooks|sdlc-internals)\.md|docs/README\.md|docs/reports/2026-10-12-handoff-freeze-prepared-attempts\.md")"`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`

## Assumptions
- The marker, not the attempt record, is what the hook should keep reading: verified by `dispatch.py:497` and `dispatch.py:1128` (recover and record already unlink it) and by `board.py:909-912` (its selftest pairs a marker with a Claude `parent_pid` attempt).
- Marker content is epoch seconds: verified by `run.sh:639`, `statusline.sh:49`, and `fleet_status.py` `inspect_markers` (lines 378-392).
- The defect reproduces at this HEAD: verified by running criterion 1's prepare-then-hook pipeline, which exited 1 with only `scout-L1.attempt.json` and `scout-L1.dispatch.json` beside the handoff; the same pipeline exited 0 once a marker was added by hand.
- `dispatch.py record` with a scout result on stdin completes in a throwaway repo and leaves the hook silent: verified by a run (exit 0, attempt `completed`, hook exit 0 with empty output).
- Criterion 3's command shape runs outside the repo: verified by a run at HEAD, where the copied suite printed `hook selftest: PASS`, so the grep is red now.
- Guards are green at base: verified by runs of the hook selftest (41 s), lifecycle selftest (18 s), board selftest (7 s), fleet_status selftest (30 s), the scope guard, and `git diff --check`. The dispatch selftest took 181 s, hence `guard timeout: 600`.
- Acceptance criterion 3 means `dispatch.py recover` and prepare's `settle`. `run_lifecycle.py recover <dir>` stays the explicit operator override that interrupts any running attempt once the lock is free: verified by the refusal text at `dispatch.py:560`, which recommends it for a spawn that never started.
- `*.running` never reaches a commit or a scope check: verified by `git check-ignore -v` (`.gitignore:6`).

## Risks
- The marker is keyed by role and level, while attempts are keyed by stem. Recording one of two same-role, same-level attempts in a directory drops the marker while the other still runs. `settle` refuses overlapping attempts from other sessions, so this needs two own-session attempts (the T-0371 skip).
- An own-session attempt that is never recorded leaves a standing marker until `dispatch.py recover` or `run_lifecycle.py recover` runs. The legacy runner behaves the same after a kill.
- Board, statusline, and fleet status now show sub-agent dispatches as running. That is intended but visible.
- Selftests of other prepare callers (`fanout.py`, `solo_run.py`, `plan_done.py`, `run-selftest.sh`) were not run for this plan. The `fanout.py land` gates own them; a red there comes back to this step.
- Acceptance criterion 6 (a fresh-Claude run) is likely to land as `unverified` in the new report; it needs this tree's plugin loaded in a live session.
- Criteria 1 and 2 are long single spans with embedded JSON. `steps.py split` was not run on them; if it refuses a span, the fix is cosmetic (move the recipe into the Do and point the criterion at the hook selftest).
- The plan was not run through `results.py validate`, because the final message is saved by the dispatcher.
