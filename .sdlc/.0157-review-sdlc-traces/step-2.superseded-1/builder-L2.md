<!-- role=builder level=L2 model=opus effort=low -->
I built the attempt reader and its selftests pass. The scope guard fails, though, only on files step 1 left behind, so I'm reporting this step as blocked.

## Status
blocked

## Changes
- plugins/sdlc-lite/scripts/traces/sources/__init__.py (new): package docstring for the readers.
- plugins/sdlc-lite/scripts/traces/sources/attempts.py (new): `read(dir)` returns `(records, problems)`. There is one record per `*.attempt.json`, sorted by name, holding the parsed dict plus `path` and `marker` (True when `<role>-<level>.running` exists). A file that is not a JSON object is skipped and its path goes into `problems`.
- plugins/sdlc-lite/scripts/traces/selftest.py: added 3 `attempts:` cases:
  - the completed, failed, interrupted and running records each come back with their status and exit code (None for running), and the bad files are listed in `problems`
  - `table.join` with an empty run list still gives one row per record
  - only the running record with its marker reports `marker` True

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts`: 3 ok lines, PASS, exit 0.
- `... selftest -k attempts | grep -q '^ok: attempts: '`: matched.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (every case): PASS.
- `test -f plugins/sdlc-lite/scripts/traces/sources/attempts.py`: passes.
- (guard) scope with `SDLC_BASE_SHA=7334f49`: FAILS. The files outside the allowed pattern are `.gitignore` (modified, adds `__pycache__/`) and `plugins/sdlc-lite/scripts/traces.py` (untracked). This step touched neither; both come from step 1, and nothing is committed since the base.

## Notes
plan defect: (guard) scope. Its regex `^(plugins/sdlc-lite/scripts/traces/.*)$` does not allow `plugins/sdlc-lite/scripts/traces.py` (the entry script, with no slash after `traces`) or step 1's `.gitignore` change. The guard compares against the chain base SHA, so both show up as out of scope even though this step never touched them. The pre-build check does not apply: this is a plan defect, not an inherited failure.

To fix it, the allowed pattern should also accept `plugins/sdlc-lite/scripts/traces\.py` and `\.gitignore` (or the guard should diff from the step's own start state). The work is left in the tree, uncommitted.
