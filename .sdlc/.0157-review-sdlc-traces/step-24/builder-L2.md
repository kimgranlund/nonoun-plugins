<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/ingest.py`: added `other_dirs(task)`, which returns the non-step subdirectories of a task dir that hold a `runs.jsonl`. `run()` now reads those after the step dirs. Their rows keep step None, because `table.STEP_DIR` does not match those directory names. I also updated the module docstring.
- `plugins/sdlc-lite/scripts/traces/cli.py`: `detect` now checks for `events.jsonl` and `aux.json` in the out dir before reading. If either is missing, it prints one line to stderr naming the file and saying to run `traces.py ingest` first, then exits 2.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added the `nested-runs` case. It builds a task dir with `verify/runs.jsonl`, ingests it, and asserts that exactly one row comes from that file and that its step is None.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k nested-runs | grep -q '^ok: nested-runs'`: passed (printed `ok: nested-runs`).
- `d=$(mktemp -d); python3 plugins/sdlc-lite/scripts/traces.py detect --out "$d" > "$d/o" 2>&1; ...`: passed. It exited 2 with no traceback, and the output named `events.jsonl` and `traces.py ingest`.
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`: passed (`traces selftest: PASS`). The `corpus: overwritten-gate-log` case skipped because `.worktrees/fanout-night/logs` does not exist.
- `git diff --check`: clean.

## Notes
None
