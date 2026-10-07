<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: each gate attempt now gets its own log, `gate-<lane>-<id>-<k>-a<n>.log`. `n` is 1 plus the highest `a<n>` already in `logs/`, found by regex (mtime is never used). Updated the module and `run_logged` docstrings. In case 9, renamed the `gate-alpha-T-0001-1.log` references to the attempt-1 name. Added case 10 (gate retry case) and a line about it in the docstring's selftest paragraph.
- `docs/references/sdlc-internals.md`: the fanout entry now gives the per-attempt gate log name and says earlier attempts survive.

## Checks
- Two-run probe (the command from the acceptance criteria): exit 0 (pass)
- `grep -qF "gate retry case" plugins/sdlc-lite/scripts/fanout.py`: pass
- `! grep -qF "gate-<lane>-<id>-<k>.log" ...`: pass
- `! grep -qF "Driver and gate log files keep their names and are overwritten" ...`: pass
- Scope check (`git diff --name-only "$SDLC_BASE_SHA"` plus untracked files, with the allowed files excluded): empty (pass)
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. It printed "skip: shellcheck not installed", so the shellcheck part did not run.
- `python3 scripts/check-packaging.py`: PASS, exit 0
- `git diff --check`: exit 0

## Notes
- I did not run the two-run probe at base, so I have no run showing it red on the current tree.
- Driver logs (`<lane>-<id>.log`) still overwrite on a rerun. They were out of scope for this step.
