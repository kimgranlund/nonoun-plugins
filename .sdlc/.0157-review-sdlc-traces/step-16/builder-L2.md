<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/cli.py`: added the `ingest`, `detect` and `clusters` subcommands through argparse. `selftest` still works. The module docstring now describes all four subcommands.
- `plugins/sdlc-lite/scripts/traces.py`: the module docstring now gives usage for all four subcommands.
- `.gitignore`: added `.sdlc/runtime/`.

## Checks
- Criterion 1 (ingest, detect and clusters on `.` with `--out` a tmp dir, then the file-existence tests): exit 0.
- Criterion 2 (`claude` and `codex` that exit 99 put first on PATH, then ingest and detect): exit 0.
- `grep -qxF '.sdlc/runtime/' .gitignore`: exit 0.
- `grep -q 'clusters' plugins/sdlc-lite/scripts/traces.py`: exit 0.
- Guard scope check against `$SDLC_BASE_SHA`: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (extra regression check): exit 0.

## Notes
- `detect` passes `datetime.now(UTC)` as the `now` argument to `findings.write`.
- The detectors run with default thresholds, since the step gives no CLI flag to override them.
- `detect` fails with a traceback if `events.jsonl` or `aux.json` is missing, because the step specifies no error handling for that case.
