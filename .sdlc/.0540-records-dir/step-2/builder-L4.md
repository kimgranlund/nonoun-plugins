<!-- role=builder level=L4 model=opus effort=high -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/dispatch.py: `prepare` writes all records in `order.records_dir`: lock, settle, stem, result, attempt, dispatch, `.running`, base-sha, Artifacts dir and `row_before`. The handoff gates keep `handoff.parent`. `build_base(directory, records, tree)` reads base-sha and dispatch records from the records dir, and reads the `base:` line from the handoff first, then from the task handoff. The lane gate and the override line use `order.task_dir`. `step_build`, `slug_of` and `attempt_dirs(open_only)` map runtime dirs. New `handoff_records` maps the `status` and `recover` CLI argument. Docstring updated. Selftest: two new records-dir cases, and the record pins now read through `R = records_dir(create=True)`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/run_lifecycle.py: `run` locks and writes in `order.records_dir(handoff dir, create=True)`. The `recover` and `status` CLI map a task or step dir.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/run.sh: sources `records.sh`. `hdir` is used for the gates and the exec tree; `dir` is the records dir, made just before the lifecycle exec. The lane check uses `order.py task-dir`. Codex `resolve` falls back to `hdir` when the records dir does not exist yet.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/solo_run.py: dispatch record, runs.jsonl (`append` and `complete`), solo.limit, request file, solo result file, solo.stream.log and `artifacts_dir` all go to the records dir. Selftest pins updated.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/budget.py: `ticket_of` maps runtime paths through `order.task_dir`. `spend` reads the records dir and the ticket folder, each file once. `ack` writes to the records dir, and the reader looks there first.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/codex_exec.py: `native-*.request.json` files now go to `.sdlc/runtime/` (created with parents, plus a `.gitignore`).
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/hooks/block-role-spawn.sh: parses an `Artifacts dir:` line the same way as `Handoff:`. Looks for the record there first, then beside the handoff. The deny message names both places.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/hooks/warn-handoff-edit.sh: sources `records.sh`. Collects `.running` markers from the records dir and the handoff dir (once when they are the same dir). `stale-edits.log` goes to the first dir that holds a marker.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/lifecycle-selftest.py: pins and the direct `recover` and `lock` calls use `order.records_dir`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/run-selftest.sh: new `rd` and `rdm` helpers, and all pins moved to the records dir. Added a records-dir check and a legacy in-place case. The lane gate case now asserts a refused planner makes no records dir.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/hook-selftest.sh: the T-0505 record, attempt and stale-edits pins point at `.sdlc/runtime/tasks/task`. Added Artifacts-dir allow cases (absolute and relative) and one deny case where neither place holds a record.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/codex-selftest.py: pins go through `order.records_dir`, and the native conductor request is read from `.sdlc/runtime/`.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/order.py and records.sh: step 1's uncommitted work. I did not edit them.

## Checks
- `redck.py record <handoff>`, before any edit: exit 0, recorded 6 controls red, stamped retrospective (see Notes).
- All 12 acceptance criteria, each run verbatim as extracted from the handoff with `SDLC_TMP_WORKTREES` set to the tmp prefix and `SDLC_BASE_SHA=27a0cc9c...`: every one exited 0. That covers the 6 red criteria, the 4 guards (including the scope guard), the dispatch selftest grep and the six-selftest chain.
- The selftests inside criterion 11 (hook, lifecycle, run, solo_run, budget, codex) each passed. The dispatch.py selftest printed `dispatch selftest: PASS`, including both new `ok: records dir: ...` lines.
- `shellcheck --severity=warning` on run.sh, run-selftest.sh, hook-selftest.sh, block-role-spawn.sh and warn-handoff-edit.sh: exit 0.
- `git diff --check -- plugins`: clean.

## Notes
- The redck record is marked retrospective because step 1's uncommitted `order.py` and `records.sh` already differed from HEAD when I ran it. It ran before any edit of mine.
- The brief's Artifacts dir line now goes through `handoff_locator` in `dispatch.py prepare` and `solo_run.dispatch_json`, so a path with a space is double-quoted. The handoff did not ask for this. The T-0504 spaced-path case in the dispatch selftest needed it, because the hook now has to find the record in `runtime/tasks/a task`. `run.sh` still prints the line bare; Codex has no spawn hook.
- When the records dir is made: `prepare` and `run.sh` compute the path up front but create the dir only after every gate passes (in prepare just before the lock, in run.sh just before the lifecycle exec). The path is the same as `create=not dry_run`, but a refused gate leaves no empty runtime dir, which the run-selftest lane gate case now asserts.
- The Python functions `status()` and `recover_orphans()` take a records dir; only the CLI maps its argument. Selftest calls now pass `R(w)`. Nothing else in `scripts/` calls them.
- The dispatch selftest pin rewrite was mechanical: 83 path pins and 10 globs now go through `R`, so seeds land in the runtime dir and add no legacy markers. Two things stay task-side on purpose: the `lk/step-3.superseded-1/builder-L3.md` fixture (the path `steps.py lint` checks) and the `skips.md` fixtures. In run-selftest, the `sw` step-1 seeds moved into the records dir, because task `t` already records in runtime (order.py rule 2).
- The deny message names the Artifacts dir only when that dir exists. That keeps the existing `Artifacts dir: x` fixtures and the T-0504 wording assertion green; the new hook-selftest case checks the both-places wording.
- Not run: `fanout.py selftest`, which the handoff says turns red in this step and step 3 fixes. `check.py` and `check.sh` are not in the criteria.
- `.worktrees/tmp/d.json` and `.worktrees/tmp/last.py` were already there and are not mine. My scratch dir under `.worktrees/tmp/0540-s2-builder-L4` is removed.
