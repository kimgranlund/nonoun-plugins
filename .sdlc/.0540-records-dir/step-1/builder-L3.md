<!-- role=builder level=L3 model=opus effort=medium -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/order.py: added `records_dir(task_dir, create=False)` and `task_dir(path)`. `records`, `_results`, `_ranks` and `ordered` now resolve their dir through `records_dir` without creating it. Added the `records-dir` and `task-dir` CLI commands, updated the docstring's Usage and rule lines, fixed the usage path that crashed on unknown arguments, and added nine `(g)` selftest cases.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/plugins/sdlc-lite/scripts/records.sh (new): a sourced bash library with `records_dir` and `records_dir_make` that follow the same five rules and have no top-level side effects.

## Checks
- `redck.py record <handoff>` before any edit: exit 0, all 10 `(red)` controls recorded red in `step-1/red-checkpoint.jsonl`.
- `python3 plugins/sdlc-lite/scripts/order.py selftest`: PASS. Cases (a) to (f) still hold, and all nine new cases print `ok: (g) records_dir: ...` or `ok: (g) task_dir: ...`.
- `order.py bogus`: prints the Usage block and exits 2. Before the fix it raised IndexError.
- All 11 acceptance criteria (10 red plus the guard), each extracted verbatim from the handoff and run with `SDLC_TMP_WORKTREES` set to the tmp prefix and `SDLC_BASE_SHA=27a0cc9c`: exit 0 under both zsh and bash.
- Criterion 4 (sources `records.sh`) also exits 0 under `sh` (bash 3.2 in POSIX mode).
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/records.sh`: exit 0.
- Bash, sh and zsh `records_dir` output matched `order.py records-dir` on seven extra fixtures: a legacy step marker, a step dir under a legacy task, a dotted folder, its step dir, runtime precedence, `*.attempt.json`, and a nested runtime step.
- `git diff --check -- plugins`: clean.

## Notes
- The handoff's rule 4 lists "or a `step-<n>` dir" as a legacy marker, but criterion 1 contradicts that literal reading. Criterion 1 builds `.0002-b/step-2` (empty) and expects `.0002-b` to map to runtime. I implemented the step-dir marker as a `step-<n>` dir that itself holds a record (`runs.jsonl`, a `*.attempt.json` or a role result). This matches the planner's own note (planner-L3-3.md:85) that a hand-written task-side `step-<n>/handoff.md` resolves to `runtime/tasks/<key>/step-<n>`. The `order.py` docstring and the `records.sh` header both state this reading.
- `create=True` and `records_dir_make` create only runtime results. A legacy result, including a step dir under a legacy task folder, is never created.
- `records.sh` lists directories with `find` fed through a here-doc, not a glob or `<(...)`. A glob with no match aborted under zsh (this host's Bash tool shell), and `sh` rejects `<(...)`, so the file now works when sourced from bash, sh or zsh.
- The `rm` of scratch fixtures under `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout68b/r/.worktrees/tmp/0540-s1-builder-L3` was denied by the permission layer, so the dirs `rd.*` and `p.*` and the files `c*.sh` remain there. They sit under the gitignored `.worktrees/` and are not in any diff.
