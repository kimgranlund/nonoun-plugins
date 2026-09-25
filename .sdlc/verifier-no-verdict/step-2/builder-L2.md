<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/board.py: in `step_row`, a verdict whose first line starts `pass` still gives 🟢 pass and one starting `fail` still gives 🔴 fail. Anything else, including a missing Verdict section, now gives 🟡 `no verdict · builder <L> · verifier <L>, rerun verify`. The module docstring now says this, and selftest section 7 has a new `noverdict` case.

## Checks
- Criterion 1, the fixture pipeline (no-verdict board row, no 🔴 in the task board or in `--summary`): exit 0.
- `grep -q "no verdict" plugins/sdlc-lite/scripts/board.py`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`: printed `board selftest: PASS`.

## Notes
- The `git diff --stat` output also lists `steps.py` and the task `handoff.md`. Those changes were already in the tree from earlier work, and I did not touch them.
- I ran the guard piped through `tail`, so the exit code I captured was `tail`'s, not the selftest's. The `PASS` line is what shows the selftest passed.
