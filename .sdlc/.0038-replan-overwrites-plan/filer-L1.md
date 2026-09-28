<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0038: Keep earlier role results on rerun so a replan no longer overwrites the plan

## PR body
### Summary
When a role ran again at the same level, `run.sh` saved over the earlier result. A replan (planner L3 on the task handoff) replaced the full `planner-L3.md` with a plan for one step. After this change the first run still writes `<role>-<level>.md`. Each rerun writes the lowest free `<role>-<level>-<k>.md` and `.log` with k >= 2, so the first result is never overwritten. The newest file by mtime is the current one. The fix covers every role, so a rebuild at the same level also keeps earlier `builder-L<n>.md` attempts.

### Changes
- `plugins/sdlc-lite/scripts/run-selftest.sh` (new): runs `planner L3` three times with a stub `claude` in a temp git repo. It checks the contents of `planner-L3.md`, `-2.md` and `-3.md`, the matching `.log` files, the stdout paths, that `runs.jsonl` has 3 lines, and that no `.running` file is left.
- `plugins/sdlc-lite/scripts/run.sh`: numbers rerun files as above. The `.running` marker name is unchanged, and the header comment describes the numbering.
- `plugins/sdlc-lite/scripts/check.sh`: runs the new selftest.
- `plugins/sdlc-lite/scripts/board.py`: `level_of` now reads the `L<n>` token, so `builder-L3-2` gives `L3` instead of `2`. New selftest cases cover `level_of`, `plan_steps` picking the newer `planner-L3-2.md`, and a newer done `builder-L3-2.md` rendering over an older blocked `builder-L3.md`.
- Docs: `skills/handoff-format/SKILL.md`, `skills/chain/SKILL.md` (§4.2 replan reads the newest planner file, §4.4 same-level rebuild), repo `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` now describe numbered reruns and the run selftest.

### Verification
- Step 1 (verifier L2: pass):
  - The run selftest failed first against the unchanged `run.sh` (`planner-L3.md ... overwritten`). The verifier reproduced that red in a throwaway worktree at HEAD, and the selftest passes after the fix.
  - `board.py selftest` passes. With the old `level_of` restored, it fails the two cases that use `level_of`.
  - `check.sh` exits 0 with `run selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
  - Dry runs: L2 names `planner-L2-2.md` because `planner-L2.md` exists. L3 names `planner-L3.md` because no L3 file exists. That is correct under the Do rule; the criterion's text asking for `-2` contradicted itself.
- Step 2 (verifier L1: pass):
  - Each doc grep failed at HEAD and passes now. No line says a rerun overwrites.
  - `check.sh` exits 0 on the final tree.
- This task's own role runs used a different checkout's `run.sh`, so the artifacts in this task folder do not show the fix.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: rerunning a role at the same level (a replan or a rebuild) no longer overwrites the earlier result. Reruns write `<role>-<level>-<k>.md`, and `/board` and `/chain` read the newest file. (T-0038)

## Follow-ups
- `board.py summary` counts L5 runs with the glob `step-*/builder-L5.*`, which assumes the first L5 run is always named `builder-L5.md`; it should also match numbered `builder-L5-<k>.md` reruns.
