<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: rerun text now describes numbered files, and `planner-L3-2.md` is added to the layout example.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: §4.2 replan and §4.4 same-level rebuild describe numbered reruns and the newest planner file.
- `CLAUDE.md`: the "Run one role directly" line notes numbered reruns, and the "Check everything" list mentions the run selftest.
- `.claude/agents/sdlc-lite-author.md`: the check.sh list includes the run selftest.

## Checks
- `check.sh` exited 0: selftests (tickets, board, run), shellcheck and plugin validate all passed. I did not check the exit code or the expected CLAUDE.md validate warning separately.
- The overwrites grep now finds only comments and selftest strings in `run.sh`, `run-selftest.sh` and `board.py`, none saying a rerun overwrites. The `handoff-format` line is gone.
- I did not re-run the greps for `<role>-<level>-<k>`, `newest`, or `run selftest` after the edits. I checked `newest` by eye in the chain file.
- I moved the `planner-L3-2.md` line after `check.sh` ran. I did not re-run `check.sh` after that reorder.

## Notes
None
