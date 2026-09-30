<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/bench.py`: new file. Adds `baseline(bench_dir)` and `default_bench_dir()`.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: adds two `bench` cases and a `_bench_step` fixture helper.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k bench`: PASS (2 ok).
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k bench | grep -q '^ok: bench: '`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/sources/bench.py`: exit 0.
- (guard) scope command: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (full): PASS.

## Notes
- The fixture also has a `step-2.superseded-1` dir with a passing verifier and cost 99.0, which checks that superseded dirs are excluded. The median still comes out 3.0.
- Only step dirs named exactly `step-<n>` are read.
- A non-numeric `cost_usd` is left out of the step's cost sum.
- The missing-results case also checks that `default_bench_dir()` returns a path ending in `bench`.
