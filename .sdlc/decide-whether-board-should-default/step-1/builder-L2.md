<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: `--sort` now defaults to None. `main()` filters with `belongs_on_board` before it sorts. With no flag it picks `auto` when any rendered task has a ticket and `recent` when none does. `sort_tasks` gains an `auto` mode: ticketed tasks by id, then unticketed tasks by mtime. Explicit `id` still puts unticketed tasks by name. Docstring updated. Selftest section 6 is rewritten and has a new no-ticket fixture.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: `board selftest: PASS`.
- Temp root with T-0003 (older), T-0002 (newer) and one unticketed task, no flag: order is new2 (T-0002), old3 (T-0003), then plain. Passed.
- Same root with `--sort id`: new2, old3, plain. Passed.
- Temp root with no tickets: output with no flag equals `--sort recent` output, with `.board-state.json` removed between runs. Passed.
- `--summary` on a fixture root: output of HEAD's board.py and the new board.py diff clean. Passed.
- `--task plain`: renders only that task (1 matching row). Passed.
- `plugins/sdlc-lite/scripts/check.sh`: selftest, tickets selftest and board selftest PASS; shellcheck ok; plugin validate ok.

## Notes
- The selftest's expected no-flag order comes from the fixture mtimes: bravo +200 and alpha +300, so bravo comes before alpha. That order is not what the handoff states (`...,'bravo','alpha'` does match, but the handoff says alpha is the later one, which puts it last, as the test expects). The test also asserts that this order differs from the `--sort id` order, so it would fail if both modes put unticketed tasks by name.
- `summary()` does not call `sort_tasks`, so `statusline.sh` is not affected.
- Two docs still describe the old default and need updating (outside this step's scope): the `/board` skill (`plugins/sdlc-lite/skills/board/SKILL.md:10`, "`recent` by mtime is the default") and CLAUDE.md line 23 ("the default recency"). No doc or script found that relies on newest-last order.
- `git diff` also shows a change to the task-level `.sdlc/decide-whether-board-should-default/handoff.md` that I did not make.
