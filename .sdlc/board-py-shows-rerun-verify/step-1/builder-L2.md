<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: the no-verdict branch of `step_row` now counts consecutive no-verdict verifier results after the newest build. Two or more give a 🟡 `stop · no verdict xN ..., ask the user` row. One still gives the `rerun verify` row. The docstring is updated to match, and the selftest has three new no-verdict cases (a, b, c), each printing an `ok:` line when it passes.

## Checks
- `grep -q "ask the user" plugins/sdlc-lite/scripts/board.py`: passed.
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: PASS. It printed an `ok:` line for one no-verdict result ("rerun verify"), two in a row ("stop ... ask the user") and fail-then-rebuild (only no-verdicts after the newest build counted, x2).
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0.
- `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/steps.py` (guard): passed, `steps.py` is untouched.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0.

## Notes
- CLAUDE.md's feed line and `skills/board/SKILL.md` don't mention no-verdict rendering, so neither was changed. The CLAUDE.md "no verdict" text is in the `steps.py` line and already says two in a row stop.
- Case (c) has two parts. With one no-verdict after a fail and a rebuild, the row stays "rerun verify": an earlier no-verdict before the build is not counted. Adding a second no-verdict after the build gives "stop x2".
- `order.ordered` returns string paths, so the loop turns them into `pathlib.Path` before calling `section`.
