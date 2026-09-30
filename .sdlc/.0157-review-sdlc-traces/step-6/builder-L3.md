<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/fanout.py`: new. `read(lanes_dir)` returns `report`, `fanout_log`, `driver_logs`, `gate_logs` and `problems` for both lanes-dir layouts.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added the `fanout` family with two cases, legacy and prefixed, each with a negative control.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k fanout`: exit 0, two `ok: fanout:` lines, then `traces selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k fanout | grep -q '^ok: fanout: '`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/sources/fanout.py`: exit 0.
- Scope guard (the exact `test -z "$( ... )"` command from the handoff): exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (whole suite): PASS.
- Negative control: I patched `fanout.RED_RE` in-process so it never matches, then ran `selftest.run('fanout')`. Both cases failed on the missing rc and the run exited 1, so the cases catch a broken rc placement.
- Ran `fanout.read` on the real legacy dir `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout-night`:
  - Report: run_id None, 11 rows, gate 1 is `bash plugins/sdlc-lite/scripts/check.sh`.
  - Logs: no fanout.log entries, 9 driver logs, 14 gate logs, no problems.
  - `gate-fanout-T-0151-1.log` reads as attempt None, run_ids `[None]`, rc None (that ticket merged, so no line records an rc).
- `git diff --check`: clean.

## Notes
- Placing an rc:
  - A gate log gets an rc only when a fanout.log line or a report row records `red: <gate> rc=<n>` for that lane and ticket. Green gates keep rc None; the handoff's "rc when a ... line records rc=<n>" asks for nothing more.
  - The gate k comes from matching the command against the report's `- Gate <k>:` lines, with whitespace normalized. If no command matches, k is the highest one logged in that run.
  - The rc goes on the newest attempt that carries the recording run's id. A legacy record with no id goes on the legacy log.
- Fields added beyond the handoff:
  - Each log has `run_id_lines`: pairs of run id and the 1-based line where that id first appears. Step 14's `stale-log-lines` detector needs "the first line of the second id" as evidence.
  - `problems` lists files that could not be read, matching the other readers.
  - `run_ids` includes None when a log has unprefixed lines.
- Report row cells are un-escaped (`\|` becomes `|`) so they compare against gate commands.
- A pure-whitespace line in fanout.log is skipped. A non-empty line that does not parse is kept, with lane and ticket None and its text as `event`.
