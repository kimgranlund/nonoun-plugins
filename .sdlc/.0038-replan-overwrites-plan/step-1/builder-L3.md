<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run-selftest.sh` (new): three `planner L3` runs with a stub `claude` in a temporary git repo. It checks the file contents, the `.log` files, the stdout paths, that `runs.jsonl` has 3 lines, and that no `.running` file is left. It prints PASS or FAIL with the reason and cleans up with a trap.
- `plugins/sdlc-lite/scripts/run.sh`: keeps `<role>-<level>.md` for the first run. After that it uses the lowest free `<role>-<level>-<k>.md`/`.log` with k >= 2. The `.running` marker name is unchanged, and the header comment now describes the numbering.
- `plugins/sdlc-lite/scripts/check.sh`: runs `bash "$root/scripts/run-selftest.sh" || fail=1` after the board selftest, and the header comment mentions it.
- `plugins/sdlc-lite/scripts/board.py`: `level_of` matches `-(L\d)(?:-\d+)?$` on the stem, with the old split kept as a fallback. The module docstring notes the numbered reruns. New selftest case 5d covers `level_of` on `builder-L3-2.md` and `planner-L3.md`, `plan_steps` picking the newer `planner-L3-2.md`, and a newer `builder-L3-2.md` (done) rendering over `builder-L3.md` (blocked).

## Checks
- 🟢 Red first: `bash plugins/sdlc-lite/scripts/run-selftest.sh` against the unchanged run.sh exited 1 with `run selftest: FAIL: planner-L3.md does not hold 'run 1', it was overwritten: ... run 3`.
- 🟢 After the run.sh change the same command exited 0 with `run selftest: PASS`.
- 🟢 Red-then-green by stash: `git stash push -m t0038-red plugins/sdlc-lite/scripts/run.sh`, then the selftest exited 1 with the same "planner-L3.md ... overwritten" message. I restored it with `git stash apply 5c9458ec...` and dropped that entry by SHA. The selftest then exited 0 with PASS.
- 🟢 `python3 plugins/sdlc-lite/scripts/board.py selftest`: `board selftest: PASS`, exit 0.
- 🟢 With the old `level_of` restored in a temp copy of board.py, the board selftest exited 1, failing `level_of(builder-L3-2.md) is L3, got '2'` and `renders built · builder L3, got 'built · builder 2, awaiting verify'`.
- 🟡 `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh planner L3 .sdlc/0038-replan-overwrites-plan/handoff.md` printed a command whose prompt names `planner-L3.md`, not the `planner-L3-2.md` the criterion asks for. With L2, where `planner-L2.md` exists, it named `planner-L2-2.md`. See Notes.
- 🟢 `plugins/sdlc-lite/scripts/check.sh` exited 0. Its output includes `run selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- 🟢 `shellcheck plugins/sdlc-lite/scripts/run-selftest.sh` is clean at every severity. Full `shellcheck` on run.sh shows only two info-level notes (SC2012, SC2016) on lines this step did not change, and check.sh uses `--severity=warning`.

## Notes
- The L3 dry-run criterion contradicts itself. It says the prompt should name `planner-L3-2.md` because `planner-L3.md` is not present. By the Do section's rule, a missing `planner-L3.md` means the first run writes `planner-L3.md`, which is what happens. The L2 half of the criterion (`planner-L2-2.md`) shows the numbering works.
- My `level_of` regex is a bit stricter than the one suggested (`-(L\d)` anchored to the end, with an optional `-k`), and falls back to the old split when nothing matches. `.running` stems (`builder-L3`) still give `L3`.
- The docs updates (handoff-format, chain, CLAUDE.md, sdlc-lite-author.md) are left for step-2 as planned. Until then, CLAUDE.md and handoff-format still say a rerun overwrites.
- `board.summary`'s `step-*/builder-L5.*` glob is unchanged. It still works because the first L5 run always writes `builder-L5.md`.
- The runner for this build is the main repo's run.sh (`sdlc-agents/plugins/sdlc-lite/scripts/run.sh`, pid 25984), not the file I edited. Changing this worktree's run.sh during the run cannot affect how it saves this result.
