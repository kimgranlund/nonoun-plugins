<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Stop run.sh from overwriting results: a rerun of the same role and level (a replan, or a rebuild at the same level) writes a new numbered file, the first file stays as it was, and /board, /chain, and the docs read the newest file.

## Step 1: run.sh keeps earlier results, with a failing test first
level: L3
### Do
- New test `plugins/sdlc-lite/scripts/run-selftest.sh` (bash, `set -euo pipefail`, shellcheck-clean). Write it first and confirm it fails against the current run.sh before changing run.sh. It must:
  - make a temp dir holding a git repo with one commit and `.sdlc/t/handoff.md`;
  - put a stub `claude` at the front of `PATH`. The stub ignores its args and prints `{"is_error":false,"result":"## Goal\nrun N","total_cost_usd":0,"duration_ms":1,"num_turns":1}`, where N is a counter kept in a file in the temp dir;
  - from inside the temp repo, run `plugins/sdlc-lite/scripts/run.sh planner L3 .sdlc/t/handoff.md` three times;
  - assert that `planner-L3.md` still contains `run 1`, that `planner-L3-2.md` contains `run 2`, that `planner-L3-3.md` contains `run 3`, that the matching `.log` files exist (`planner-L3.log`, `planner-L3-2.log`, `planner-L3-3.log`), that `runs.jsonl` has 3 lines, that run.sh's stdout each time is the path it wrote, and that no `.running` file is left over;
  - print `run selftest: PASS` or `FAIL` with the reason, exit non-zero on failure, and clean up with a trap.
- `plugins/sdlc-lite/scripts/run.sh` around lines 44-46:
  - Keep `result="$dir/$role-$level.md"` when that file does not exist yet.
  - Otherwise pick the lowest k >= 2 for which `$dir/$role-$level-$k.md` does not exist, and set `result`/`log` to `$role-$level-$k.md`/`.log`.
  - Keep the `.running` marker named `$role-$level.running`.
  - Update the header comment (lines 4-6) to describe the numbering.
  - The verifier swap at line 51 (`ls -t builder-L*.md`) already picks the newest file and needs no change.
- `plugins/sdlc-lite/scripts/check.sh`: run `bash "$root/scripts/run-selftest.sh" || fail=1` next to the other selftests, and update its header comment.
- `plugins/sdlc-lite/scripts/board.py`:
  - `level_of` must return the `L<n>` token, for example by matching the regex `-(L\d)` on the stem, so that `builder-L3-2` gives `L3` and not `2`.
  - Add selftest cases:
    - `level_of` on `builder-L3-2.md` and on `planner-L3.md` returns `L3`;
    - in a task dir with no step dirs, holding `planner-L3.md` (2 steps) and a newer `planner-L3-2.md` (1 step), `plan_steps` returns the 1-step plan;
    - a step dir holding `builder-L3.md` (Status blocked) and a newer `builder-L3-2.md` (Status done) renders as `built · builder L3`, not `blocked`.
### Acceptance criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0 and prints `run selftest: PASS`.
- Red-then-green: with only run.sh reverted (`git stash push -m t0038-red plugins/sdlc-lite/scripts/run.sh`, then run the selftest, then `git stash apply` by SHA and drop the entry), the selftest exits non-zero and names the overwritten `planner-L3.md`.
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS`. Reverting only `level_of` makes one of the new cases fail.
- `SDLC_DRY_RUN=1 plugins/sdlc-lite/scripts/run.sh planner L3 .sdlc/0038-replan-overwrites-plan/handoff.md` still prints a command, and its prompt names `planner-L3-2.md` because `planner-L3.md`... is not present in this dir (only `planner-L2` exists). Running the same thing with level L2 after `planner-L2.md` exists names `planner-L2-2.md`.
- `plugins/sdlc-lite/scripts/check.sh` exits 0 and its output includes the run selftest PASS line and `ok: shellcheck`.

## Step 2: Docs and skills describe numbered reruns
level: L1
### Do
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md` line 25: replace "Rerunning the same role and level overwrites them" with: a rerun writes `<role>-<level>-<k>.md`/`.log` (k = 2, 3, ...), the first result is never overwritten, and the newest file by mtime is the current one. Add `planner-L3-2.md` (a replan) to the layout example.
- `plugins/sdlc-lite/skills/chain/SKILL.md` §4.2: the replan writes a new `planner-L3[-k].md`, and /chain rewrites the remaining step handoffs from the newest planner file, leaving earlier plans in place. §4.4: a same-level rebuild writes `builder-L<n>-<k>.md`, so earlier attempts stay for the rubric's "earlier builder-*.md with Status blocked" count.
- Repo-root `CLAUDE.md`:
  - The "Run one role directly" line should note that a rerun writes `<role>-<level>-<k>.md` and never overwrites.
  - The Commands "Check everything" list should mention the run selftest.
- `.claude/agents/sdlc-lite-author.md` line 19: add the run selftest to the list of things check.sh runs.
### Acceptance criteria
- `grep -rn "overwrites" plugins/sdlc-lite/skills plugins/sdlc-lite/scripts CLAUDE.md` finds no line saying a rerun overwrites a result.
- `grep -n "<role>-<level>-<k>" plugins/sdlc-lite/skills/handoff-format/SKILL.md CLAUDE.md` matches in both files.
- `grep -n "newest" plugins/sdlc-lite/skills/chain/SKILL.md` matches the replan instruction.
- `grep -n "run selftest\|run-selftest" CLAUDE.md .claude/agents/sdlc-lite-author.md` matches in both.
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The CLAUDE.md validate warning is expected.

## Risks
- The fix applies to every role, not only the planner. It also stops rebuilds at the same level from overwriting `builder-L<n>.md`. Every current reader picks the newest file by mtime or `ls -t` (board.py `by_level`, the run.sh verifier swap, bench-summary.sh), so nothing should break. A consumer that hardcodes `<role>-<level>.md` would still read the first run's file; none was found in the plugin.
- Ordering depends on mtime. Hand-editing an older result file makes it look newest. This was already true before the fix.
- A replan plan that covers only the failed step does not change what the board shows, because the board prefers the step handoffs. The only difference is that the full original plan now survives.
- The run selftest needs `jq` and `git` on the host. `jq` is already required by run.sh.
- This task's own role runs use a different checkout's run.sh (per the handoff), so this task's artifacts will not show the fix.
