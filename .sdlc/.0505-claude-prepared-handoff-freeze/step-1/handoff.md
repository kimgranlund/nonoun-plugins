## Task goal
Activate handoff warning and deny modes throughout prepared attempts. Release protection after completion or recovery.

## Step 1: Prepare writes the running marker; prove the freeze lifecycle end to end
level: L3
guard timeout: 600
### Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/AGENTS.md`
- `docs/references/AGENTS.md`
- `docs/reports/AGENTS.md`
### Do
Depends on: none.

Settled design: `prepare` owns the marker. The hook `plugins/sdlc-lite/hooks/warn-handoff-edit.sh` stays untouched and gets no second definition of "live" (review finding F3 asks for one lifecycle source).
- `record`'s `close()` (`plugins/sdlc-lite/scripts/dispatch.py`, about line 1124), `recover_orphans` (about line 485), and `run_lifecycle.recover_unlocked` (`plugins/sdlc-lite/scripts/run_lifecycle.py`, about line 44) already unlink `<role>-<level>.running`. Only `prepare` never writes it.
- Marker readers already pair a marker with a Claude attempt record: `board.py` (its `*.running` globs) and `fleet_status.py` (its marker inspection, which reads the pid from the attempt record).

Implementation, in `plugins/sdlc-lite/scripts/dispatch.py`:
- In `prepare`, right after the two `run_lifecycle.write(...)` calls for the attempt and dispatch records (about line 849), still under the directory lock, write `directory / ('%s-%s.running' % (role, level))`.
- Name it by role and level, not by stem, because `close()` and both recover paths unlink by role and level.
- Content is the epoch start in whole seconds plus a newline, the same as `run.sh` writes with `date +%s`. `statusline.sh` does arithmetic on it and `fleet_status.py` parses it.
- `--dry-run` writes no marker and a refused prepare writes none. The placement gives both: a dry run returns before the records, and a refusal raises before them.
- Do not change `close()`, `recover_orphans`, `run_lifecycle.py`, or `run.sh`. A no-result record (T-0412: the attempt stays running, exit 2) never calls `close()`, so its marker stays.
- Update the module docstring's `Records.` paragraph to say prepare writes the marker and record and recover clear it.

Regression cases in the `dispatch.py` selftest. Use these exact labels, because criterion 4 greps each as `ok: <label>`:
- `prepare writes the running marker with an epoch start (T-0505)`
- `prepare --dry-run writes no running marker (T-0505)`
- `a no-result record keeps the running marker (T-0505)`
- `record removes the running marker on completed and on failed (T-0505)`
- `recover removes the running marker of a dead-parent attempt (T-0505)`
- `recover keeps a live attempt of another run and its running marker (T-0505)`

The last label is the ticket's acceptance criterion 3. It covers `recover_orphans` and prepare's `settle`: the attempt stays `running` with its `parent_pid` unchanged and the marker stays. Leave the two hand-written `builder-L1.running` markers in the existing status and recover cases as they are. An existing case that lists a directory after a successful prepare is updated to expect the marker. Never weaken a refusal, dry-run, or "wrote nothing" case.

Integration cases in `plugins/sdlc-lite/scripts/hook-selftest.sh`, after the existing `warn-handoff-edit.sh` block:
- Resolve the scripts folder once as an absolute path, the way the suite resolves `hooks` (a `cd` to `dirname "$0"` and `pwd`), and run `dispatch.py` from there. Never use a repo-relative path or a path from `git rev-parse`. Criterion 3 copies the new suite over the base plugin, and the suite must then run the base `prepare`.
- For each case, build a fresh throwaway git repo with one empty commit and one task folder inside its `.sdlc` folder, holding a `handoff.md` with `## Goal`, `## Context`, and `## Question` sections. Run the real `dispatch.py prepare scout L1` from inside that repo. The recipe is criterion 1 below and `docs/reports/2026-10-12-sdlc-lite-astra-review/probes.py` lines 13-28. Use one task folder per case, because a live attempt refuses a second prepare in its folder.
- Run every `dispatch.py` call under `env -i PATH="$PATH" HOME="$HOME"`, so the caller's `SDLC_ROLE` and `SDLC_HEADLESS` never leak in. Add `SDLC_DISPATCH_PARENT_PID=<pid>` only where a case sets the owner; `parent_pid()` in `dispatch.py` reads it, and the `dispatch.py` selftest uses the same seam.
- Never create a marker by hand in these cases.
- Warn mode: the hook exits 0, stderr holds `handoff freeze (warning)` and names `scout-L1`, and `stale-edits.log` beside the handoff holds exactly one `edited while scout-L1 ran` line.
- Deny mode (`SDLC_HANDOFF_EDIT_MODE=deny`): the hook exits 2.
- Completed: after `dispatch.py record` with a valid scout result on stdin, the hook is silent and exits 0 in deny mode.
- Failed: after `dispatch.py record` with error text on stdin (text with no `## ` heading line; record exits 1 and the attempt is `failed`), the hook is silent and exits 0 in deny mode.
- Recovered: prepare with `SDLC_DISPATCH_PARENT_PID` set to the pid of a child the suite already reaped, check that deny mode exits 2, run `dispatch.py recover <task folder>`, check that it prints `marked interrupted`, then check that the hook is silent and exits 0.
- Live attempt of another run: prepare with `SDLC_DISPATCH_PARENT_PID=$$` (the suite's own pid, which is alive and older than the attempt, as `pid_reused` requires). Run `dispatch.py recover <task folder>` and check that it prints `no orphaned attempts`, the attempt record still says `running` with the same `parent_pid`, and deny mode still exits 2.
- Every new assertion's `fail` text starts with `handoff-edit prepared attempt`. The suite stops at its first `fail`, and criterion 3 greps `hook selftest: FAIL: handoff-edit prepared attempt` when the new suite runs against the base plugin.
- Add the prepared-attempt cases to the suite's header comment.

Docs:
- `docs/references/claude-hooks.md`, section `hooks/warn-handoff-edit.sh`: say who writes the marker (`run.sh` for the legacy runner, `dispatch.py prepare` for sub-agent dispatch) and who clears it (`dispatch.py record`, `dispatch.py recover`, `run_lifecycle.py recover`). Cite T-0505.
- `docs/references/sdlc-internals.md`, the `dispatch.py prepare` and `dispatch.py record` paragraphs: same fact, cite T-0505. Say that `run_lifecycle.py recover` stays the operator override that interrupts any running attempt once the directory lock is free.
- Create `docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md` [creates: docs/reports/2026-10-12-handoff-freeze-prepared-attempts.md]. Follow the Report row of `docs/specs/doc-standards/README.md`. It holds the baseline FAIL line printed by criterion 3's command, the commands run after the change with their results, and one line that reads exactly `Live fresh-Claude check: unverified`, followed by the reason and by the recipe a later live run follows (the T-0212 record `docs/reports/handoff-freeze-live-run.md`). Keep the evidence inline; add no sibling folder.
- Add one index line for the report to `docs/README.md`, beside the other report entries.
- Do not edit `docs/reports/2026-10-12-sdlc-lite-astra-review.md` or its folder.

The ticket's acceptance criterion 6 (a fresh-Claude run) is not proven by this step, and the step launches no Claude session. The builder is a headless sub-agent whose loaded plugin is the main checkout, not this tree, and a live probe makes model calls the user opts into. The report says `unverified` and the conductor carries the item to close-out. Criterion 6 also accepts `observed`, for a live run on this tree's plugin that the conductor or the user ran and handed over with its evidence; the builder never writes `observed` on its own.

Contract dependents of the marker, found with `git grep -n '\.running' -- plugins docs/references docs/specs scripts .gitignore`:
- `board.py` and `fleet_status.py` now see a marker for sub-agent dispatches. Their selftests are guards below.
- Left untouched on purpose, because they read any marker the same way: `statusline.sh`, `traces/detectors/escalation.py`, `traces/sources/attempts.py`.
- Left untouched on purpose, because they already exclude `*.running`: `fanout.py` (`LANE_ADD`), `docs_check.py` (`GENERATED_NAME`), `agents/solo.md` and `skills/handoff-format/run-operations.md` (the staging pathspec), and the `.gitignore` line `*.running`.
- Left untouched on purpose, because they drive `run.sh` and never call `dispatch.py prepare`: `run-selftest.sh`, `codex-selftest.py`, and `lifecycle-selftest.py` (a guard below).

Validation scope: the criteria below, plus `python3 plugins/sdlc-lite/scripts/docs_check.py` after the docs edits (it prints `0 errors` at the base and must still). The whole `check.sh` suite belongs to the `fanout.py land` gates for lane `fanout/wave54-a`.

### Acceptance criteria
- `r=$(mktemp -d) && n=task && d="$r/.sdlc/$n" && h="$d/handoff.md" && p="$PWD/plugins/sdlc-lite" && j=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$h") && git -C "$r" init -q && git -C "$r" -c user.name=t -c user.email=t@example.invalid commit --allow-empty -qm seed && mkdir -p "$d" && printf "## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n" >"$h" && (cd "$r" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/scripts/dispatch.py" prepare scout L1 ".sdlc/$n/handoff.md" >/dev/null) && printf "%s" "$j" | env -i PATH="$PATH" SDLC_HANDOFF_EDIT_MODE=deny bash "$p/hooks/warn-handoff-edit.sh" 2>&1 | grep -qF "handoff freeze: handoff" && (cd "$r" && printf "## Map\nNone\n\n## Entry points\nNone\n\n## Not found\nNone\n\n## Carry forward\nNone\n" | env -i PATH="$PATH" HOME="$HOME" python3 "$p/scripts/dispatch.py" record ".sdlc/$n/scout-L1.dispatch.json" >/dev/null 2>&1) && out=$(printf "%s" "$j" | env -i PATH="$PATH" SDLC_HANDOFF_EDIT_MODE=deny bash "$p/hooks/warn-handoff-edit.sh" 2>&1) && test -z "$out"` exits 0: a real prepared attempt denies the edit with no hand-made marker, and recording releases it.
- `r=$(mktemp -d) && n=task && d="$r/.sdlc/$n" && h="$d/handoff.md" && p="$PWD/plugins/sdlc-lite" && j=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$h") && git -C "$r" init -q && git -C "$r" -c user.name=t -c user.email=t@example.invalid commit --allow-empty -qm seed && mkdir -p "$d" && printf "## Goal\nMap seed.\n\n## Context\nseed\n\n## Question\nWhere is seed?\n" >"$h" && (cd "$r" && env -i PATH="$PATH" HOME="$HOME" python3 "$p/scripts/dispatch.py" prepare scout L1 ".sdlc/$n/handoff.md" >/dev/null) && printf "%s" "$j" | env -i PATH="$PATH" bash "$p/hooks/warn-handoff-edit.sh" 2>&1 | grep -qF "handoff freeze (warning)" && grep -q "edited while scout-L1 ran" "$d/stale-edits.log"` exits 0: warn mode warns and logs for a real prepared attempt.
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
