<!-- role=filer level=L1 model=sonnet effort=low -->
## Warnings
- Step 3 verifier-L3 failed on the first attempt. `steps.py` could not read a task-side step handoff once its records twin existed and was empty, which broke `dispatch.py selftest`. A second builder attempt (builder-L4-2) and verifier-L3-2 passed. The first attempt's second finding, `fanout.py` `planned_scope` ignoring records-dir step folders, is shown by the artifacts as handled in the retry. I did not read builder-L4-2's text for that.
- process deviation: red-checkpoint, step 2: retrospective, attempt 2669785dc90a4be2a582e2c5bd66760c. All 6 of 6 (red) criteria had no pre-edit red control. Step 1's uncommitted `order.py` and `records.sh` already differed from HEAD when `redck.py record` ran. The verifier ran each red control itself on a base copy and saw red.
- process deviation: red-checkpoint, step 3: retrospective, attempts 73db2d8f0bfc4e51bc59daa02023a918 and 54ed83b3c2ed475fb02b8dd12cc9ac17. Both (red) criteria in each attempt had no pre-edit red control, because the 14 step-1/2 paths were already dirty. The verifier ran the controls itself and saw red at base and green on the built tree.
- process deviation: red-checkpoint, step 4: retrospective, attempt f9158105536b4335b1256a615ed4d778. 2 of 2 recorded (red) criteria had no pre-edit red control. The step has 3 (red) criteria and `redck.py` recorded only 2 controls, and nobody traced why. The verifier ran the base-sha controls for all three.
- Passing verdicts do not clear the deviations above.
- Unverified, step 2 and step 3 (second attempt): `fanout.py selftest` was not usable. Step 2's handoff declared it red until step 3. Step 1's verifier saw no output from `fanout.py selftest` or `tickets.py selftest`. Step 4's verifier ran `check.sh`, which exited 0 after 18m17s.

## PR title
T-0540: Lean records A: Records dir (0.23.0)

## PR body
## Summary
Part A of the SDLC Lite 0.23.0 lean work records. Run records (dispatch, attempt, result and red-checkpoint files, `runs.jsonl`, step dirs) for a new task now go to the git-ignored `.sdlc/runtime/tasks/<name>/`. The task folder in git keeps `handoff.md` and `skips.md`. Legacy task folders stay readable and keep recording in place, with no migration.

## Changes
- Step 1: `scripts/order.py` gains `records_dir`, a `records-dir <task dir>` CLI and a `task-dir` reverse map. New `scripts/records.sh` exposes `records_dir` and `records_dir_make`, which writes a `.gitignore` containing `*`. Legacy markers (`runs.jsonl`, an attempt file, a role result, a `step-<n>` dir) and runtime precedence are covered. `skips.md` is not a legacy marker.
- Step 2: `dispatch.py`, `run.sh`, `run_lifecycle.py`, `solo_run.py`, `budget.py`, `codex_exec.py`, `hooks/block-role-spawn.sh` and `hooks/warn-handoff-edit.sh` write to and read the records dir. The spawn hook reads the prompt's `Artifacts dir:` line first, then looks beside the handoff. The lifecycle, run and hook selftests are updated.
- Step 3: `steps.py` (split, swap, widen, `record_lane`, `write_solo_skips`, `base_sha`, `result_ts`), `fanout.py`, `redck.py` and `verify_scope.py` use the records dir. `skips.md` stays in the task folder, per the maintainer's decision, so `tickets.py skip_missing` and fanout selftest case 16 are unchanged. The retry fixed the case where a task-side step handoff has an existing empty records twin.
- Step 4: the `skills/handoff-format/SKILL.md` layout block and the Codex resume packet in `adapters/codex/instructions.md` name the records dir. The 29 Codex agent TOMLs are regenerated from that edit.

## Verification
- Step 1 (verifier L2, pass): all 11 criteria ran verbatim and the red ones fail at base. The Bash and Python `records_dir` agree on six fixtures. `shellcheck` is clean.
- Step 2 (verifier L3, pass): `dispatch.py prepare` on a fresh git task leaves only `handoff.md` task-side. A legacy fixture with `runs.jsonl` keeps recording in place. `dispatch.py selftest` prints both new cases. The hook allows a spawn through the `Artifacts dir:` line and denies it when neither location holds a dispatch file.
- Step 3 (first verifier fail, second verifier L3 pass): `steps.py`, `redck.py` and `verify_scope.py` selftests print the `(records dir)` ok lines. Legacy split-in-place and the `skips.md` guards hold.
- Step 4 (verifier L2, pass): `check.sh` exits 0, `check-packaging.py` passes, `codex_roles.py generate --check` is clean and `git diff --check` is clean.

Process deviations: the red-checkpoint of steps 2, 3 and 4 was recorded retrospectively, so the builders' red controls were not recorded before the edit. The verifiers re-ran the red controls themselves. See Warnings.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- SDLC Lite 0.23.0: run records for new tasks live in the git-ignored `.sdlc/runtime/tasks/<name>/` (`order.py records-dir <task dir>` prints the path). The task folder keeps `handoff.md` and `skips.md`. Legacy task folders keep recording in place.

## Follow-ups
- fix-now: `specgate.py:149` `red --step N` still reads `task_dir / step-N` and misses records-side step dirs and their `base-sha`. `specgate.py selftest` passes, and no criterion names it.
- fix-now: `steps.py:505` has no selftest for the task-side half of `step_dirs`' union. Changing it to records-only still passes the 451 ok lines.
- decide: `tickets.py:1583`, `board.py:104` and `report.py:640` still read `step-*` under the task folder, and `board.py:226` passes the task dir to `dispatch.status`, so orphaned attempts of a runtime-recorded task will not show on the board. T-0541 and T-0543 own these readers; confirm that coverage.
- note: `dispatch.py` selftest (around :2456) and `specgate.py` selftest fail when `TMPDIR` sits inside a git worktree, because their "outside git" fixtures break there. They pass with the system `TMPDIR`.
- note: `handoff-format/SKILL.md` still says "Add `.sdlc/` to `.gitignore` unless the user wants the trail committed", which sits loosely against "records are local and ignored". T-0545 owns the docs specs.
- note: `redck.py` recorded 2 controls for 3 (red) criteria in step 4, and nobody investigated why.
