<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k bench`: pass. Evidence: I ran it and it printed 2 `ok: bench:` lines and `traces selftest: PASS`, rc=0.
- `... selftest -k bench | grep -q '^ok: bench: '`: pass. Evidence: rc=0. The check can go red. I mutated `STEP_RE` in a throwaway copy to drop the `$` anchor, so `step-2.superseded-1` was counted. The bench case then failed with median 5.5 and 4 steps, and rc=1.
- `test -f plugins/sdlc-lite/scripts/traces/sources/bench.py`: pass. Evidence: rc=0.
- (guard) scope: pass. Evidence: I ran the exact command with `SDLC_BASE_SHA` from `step-9/base-sha`, and it returned guard=0. The changed and untracked files are all `.gitignore`, `traces.py`, or under `scripts/traces/`.
- Task behavior, checked against the Do. Read `bench.py` and the selftest cases:
  - The fixture has passed steps costing 1.0, 3.0, and 8.0, one failed step at 50.0, and a superseded step at 99.0. The selftest asserts a median of 3.0 and 3 counted steps. The case ran green.
  - Result dirs that are missing give a None median.
  - `default_bench_dir()` follows the order in `scripts/bench-dir.sh`: `$SDLC_BENCH_DIR`, then `<git toplevel>/bench` if it exists, then the plugin's own `bench/`.

## Out of scope changes
None. The `.gitignore` change is allowed by the guard. I did not inspect its content. The other listed files sit under `scripts/traces/`, which the step allows.

## For the next attempt
None
